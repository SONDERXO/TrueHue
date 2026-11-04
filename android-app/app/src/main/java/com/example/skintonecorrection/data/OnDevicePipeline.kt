package com.example.skintonecorrection.data

import android.content.Context
import android.graphics.Bitmap
import com.google.mediapipe.framework.image.BitmapImageBuilder
import com.google.mediapipe.tasks.core.BaseOptions
import com.google.mediapipe.tasks.core.Delegate
import com.google.mediapipe.tasks.vision.core.RunningMode
import com.google.mediapipe.tasks.vision.facelandmarker.FaceLandmarker
import com.example.skintonecorrection.ml.DevelopmentMath
import com.example.skintonecorrection.ml.PortableTreeAsset
import org.json.JSONObject
import org.opencv.android.OpenCVLoader
import org.opencv.android.Utils
import org.opencv.core.*
import org.opencv.imgproc.Imgproc
import org.opencv.geometry.Geometry
import org.opencv.objdetect.FaceDetectorYN
import java.io.File
import java.security.MessageDigest

data class PipelineImages(val input: Bitmap, val mask: Bitmap, val corrected: Bitmap)

/** Original rule mask only. This is an experimental port; cross-platform parity is pending. */
class OnDevicePipeline(private val context: Context) {
    companion object { const val ASSETS = "development_pipeline/" }
    fun run(bitmap: Bitmap, report: JSONObject): PipelineImages {
        report.put("failed_stage","initialization")
        check(OpenCVLoader.initLocal()) { "The local image engine could not start." }
        val owned = mutableListOf<Mat>()
        fun mat(): Mat = Mat().also { owned.add(it) }
        fun tracked(value: Mat): Mat = value.also { owned.add(it) }
        fun bytes(name: String) = context.assets.open(ASSETS+name).use { it.readBytes() }
        val manifest = JSONObject(bytes("manifest.json").toString(Charsets.UTF_8))
        val hashes = manifest.getJSONObject("assets_sha256")
        fun checked(name: String): ByteArray = bytes(name).also {
            val hash = MessageDigest.getInstance("SHA-256").digest(it).joinToString("") { b -> "%02x".format(b) }
            require(hash == hashes.getString(name)) { "A bundled model checksum does not match." }
        }
        report.put("model",manifest).put("opencv_version",Core.VERSION).put("failed_stage","assets")
        // Verify every asset before opening a native model. No network/download path exists.
        val assets = listOf("baseline5.json","mst_lookup.json","face_landmarker.task","face_detection_yunet.onnx").associateWith { checked(it) }
        val features = manifest.getJSONArray("features").let { a -> List(a.length()) { a.getString(it) } }
        require(features == listOf("input_mean_l_star","input_mean_a_star","input_mean_b_star","input_ita_degrees","input_mst_index"))
        val tree = PortableTreeAsset.parse(assets.getValue("baseline5.json"),hashes.getString("baseline5.json"),features)
        val lookup = JSONObject(assets.getValue("mst_lookup.json").toString(Charsets.UTF_8))
        require(lookup.getString("measurement_contract_sha256") == manifest.getString("python_measurement_contract_sha256"))
        require(lookup.getString("status") == "experimental_not_final_validated")
        fun extracted(name: String): File {
            val file = File(context.noBackupFilesDir,"pipeline_$name")
            val content = assets.getValue(name)
            if (!file.exists() || !file.readBytes().contentEquals(content)) file.writeBytes(content)
            return file
        }
        try {
            report.put("failed_stage","resize")
            val rgba = mat();Utils.bitmapToMat(bitmap,rgba)
            val full = mat();Imgproc.cvtColor(rgba,full,Imgproc.COLOR_RGBA2BGR)
            val square = mat();Imgproc.resize(full,square,Size(256.0,256.0),0.0,0.0,Imgproc.INTER_LINEAR)
            val inputRgba = mat();Imgproc.cvtColor(square,inputRgba,Imgproc.COLOR_BGR2RGBA)
            val input = Bitmap.createBitmap(256,256,Bitmap.Config.ARGB_8888);Utils.matToBitmap(inputRgba,input)
            report.put("failed_stage","face_detection")
            val detector = FaceDetectorYN.create(extracted("face_detection_yunet.onnx").absolutePath,"",Size(256.0,256.0),.85f,.3f,5000)
            val faces = mat();detector.detect(square,faces);report.put("face_count",faces.rows())
            require(faces.rows()==1) { if (faces.rows()==0) "No clear face was found. Choose a clear photo with one face." else "More than one face was found. Choose one person." }
            val x=faces.get(0,0)[0].toInt().coerceIn(0,255);val y=faces.get(0,1)[0].toInt().coerceIn(0,255)
            val w=faces.get(0,2)[0].toInt().coerceIn(1,256-x);val h=faces.get(0,3)[0].toInt().coerceIn(1,256-y)
            val rect=Rect(x,y,w,h);report.put("face_box",org.json.JSONArray(listOf(x,y,w,h)))
            val roi=tracked(square.submat(rect));val crop=tracked(roi.clone())
            report.put("failed_stage","landmarks")
            // Own a verified direct buffer for the entire native graph lifetime, independent
            // of Activity/AssetManager recreation and mapped APK resources.
            val modelBuffer=java.nio.ByteBuffer.allocateDirect(assets.getValue("face_landmarker.task").size)
            modelBuffer.put(assets.getValue("face_landmarker.task"));modelBuffer.rewind()
            val options=FaceLandmarker.FaceLandmarkerOptions.builder()
                .setBaseOptions(BaseOptions.builder().setModelAssetBuffer(modelBuffer).setDelegate(Delegate.CPU).build())
                .setRunningMode(RunningMode.IMAGE).setNumFaces(1).setMinFaceDetectionConfidence(.5f).build()
            val polygons=manifest.getJSONArray("landmark_regions")
            var points: List<Point>?=null
            FaceLandmarker.createFromOptions(context,options).use { landmarker ->
                for (fraction in listOf(0.0,.5,1.5,-1.0)) {
                    val pad=if(fraction<0) 256 else (fraction*maxOf(w,h)).toInt()
                    val left=if(fraction<0) 0 else maxOf(0,x-pad);val top=if(fraction<0) 0 else maxOf(0,y-pad)
                    val right=if(fraction<0) 256 else minOf(256,x+w+pad);val bottom=if(fraction<0) 256 else minOf(256,y+h+pad)
                    val sub=tracked(square.submat(Rect(left,top,right-left,bottom-top)))
                    val converted=mat();Imgproc.cvtColor(sub,converted,Imgproc.COLOR_BGR2RGBA)
                    val frame=Bitmap.createBitmap(sub.cols(),sub.rows(),Bitmap.Config.ARGB_8888);Utils.matToBitmap(converted,frame)
                    val mp=BitmapImageBuilder(frame).build()
                    val detected=try { landmarker.detect(mp).faceLandmarks() } finally { mp.close();frame.recycle() }
                    if (detected.isNotEmpty()) {
                        points=detected[0].map { Point(it.x().toDouble()*sub.cols()+left-x,it.y().toDouble()*sub.rows()+top-y) }
                        report.put("landmark_margin_fraction",fraction);break
                    }
                }
            }
            // Keep the backing buffer reachable until after close() drains the graph.
            check(modelBuffer.capacity()==assets.getValue("face_landmarker.task").size)
            val landmarks=points ?: error("Face details could not be measured. Try a sharper, front-facing photo.")
            report.put("failed_stage","skin_mask")
            val hsv=mat();val ycc=mat();Imgproc.cvtColor(crop,hsv,Imgproc.COLOR_BGR2HSV);Imgproc.cvtColor(crop,ycc,Imgproc.COLOR_BGR2YCrCb)
            val hm=mat();val ym=mat();Core.inRange(hsv,Scalar(0.0,48.0,0.0),Scalar(20.0,255.0,255.0),hm)
            Core.inRange(ycc,Scalar(0.0,133.0,77.0),Scalar(255.0,173.0,127.0),ym)
            val mask=mat();Core.bitwise_and(hm,ym,mask)
            val kernel=tracked(Imgproc.getStructuringElement(Imgproc.MORPH_ELLIPSE,Size(5.0,5.0)))
            for (op in listOf(Imgproc.MORPH_OPEN,Imgproc.MORPH_CLOSE,Imgproc.MORPH_CLOSE)) Imgproc.morphologyEx(mask,mask,op,kernel)
            val labels=mat();val stats=mat();val centroids=mat();val count=Imgproc.connectedComponentsWithStats(mask,labels,stats,centroids,8,CvType.CV_32S)
            var largest=0;var area=0.0
            for (label in 1 until count) { val a=stats.get(label,Imgproc.CC_STAT_AREA)[0];if(a>area){area=a;largest=label} }
            if(largest==0) mask.setTo(Scalar(0.0)) else Core.compare(labels,Scalar(largest.toDouble()),mask,Core.CMP_EQ)
            val exclusion=tracked(Mat.zeros(h,w,CvType.CV_8UC1))
            for (i in 0 until polygons.length()) {
                val indices=polygons.getJSONArray(i)
                val poly=tracked(MatOfPoint(*Array(indices.length()) { j ->
                    val p=landmarks[indices.getInt(j)]
                    require(p.x.isFinite() && p.y.isFinite())
                    Point(p.x.coerceIn(0.0,w-1.0).toInt().toDouble(),p.y.coerceIn(0.0,h-1.0).toInt().toDouble())
                })) as MatOfPoint
                if(i==polygons.length()-1) require(kotlin.math.abs(Geometry.contourArea(poly))>=1.0) { "Mouth geometry is unavailable." }
                Imgproc.fillPoly(exclusion,listOf(poly),Scalar(255.0))
            }
            Core.bitwise_not(exclusion,exclusion);Core.bitwise_and(mask,exclusion,mask)
            val pixels=Core.countNonZero(mask);report.put("selected_pixels",pixels)
            require(pixels>=1000) { "Too little usable facial skin was found. Try a clearer photo without heavy shadows." }
            report.put("failed_stage","measurement")
            val lab=mat();Imgproc.cvtColor(crop,lab,Imgproc.COLOR_BGR2Lab)
            val labBytes=ByteArray(w*h*3);lab.get(0,0,labBytes);val selected=ByteArray(w*h);mask.get(0,0,selected)
            val totals=DoubleArray(3)
            for(i in selected.indices) if(selected[i].toInt()!=0) {
                // Match Python's per-sample float32 Lab conversion, then explicitly report port parity pending.
                totals[0]+=((labBytes[i*3].toInt() and 255).toFloat()*(100f/255f)).toDouble()
                totals[1]+=((labBytes[i*3+1].toInt() and 255)-128).toDouble();totals[2]+=((labBytes[i*3+2].toInt() and 255)-128).toDouble()
            }
            val means=DoubleArray(3){DevelopmentMath.rounded(totals[it]/pixels)};val ita=DevelopmentMath.ita(means[0],means[2])
            fun knots(name:String)=lookup.getJSONArray(name).let{a->DoubleArray(a.length()){a.getDouble(it)}}
            val mst=DevelopmentMath.mst(ita,knots("ita_knots"),knots("mst_knots"))
            val vector=doubleArrayOf(means[0],means[1],means[2],ita,(mst-1).toDouble())
            report.put("features",org.json.JSONArray(vector.toList())).put("feature_names",org.json.JSONArray(features)).put("mst_estimate",mst)
            report.put("failed_stage","correction")
            val parameters=tree.predict(vector);report.put("parameters",org.json.JSONArray(parameters.toList()))
            val inputPixels=IntArray(256*256);input.getPixels(inputPixels,0,256,0,0,256,256)
            val correctedPixels=inputPixels.copyOf();val maskPixels=IntArray(256*256){0xff000000.toInt()};var changed=0
            for (yy in 0 until h) for(xx in 0 until w) if(selected[yy*w+xx].toInt()!=0) {
                val i=(y+yy)*256+x+xx;maskPixels[i]=-1;correctedPixels[i]=DevelopmentMath.correct(inputPixels[i],parameters)
                if(correctedPixels[i]!=inputPixels[i])changed++
            }
            report.put("changed_pixels",changed).put("status","experimental_success").remove("failed_stage")
            return PipelineImages(input,Bitmap.createBitmap(maskPixels,256,256,Bitmap.Config.ARGB_8888),Bitmap.createBitmap(correctedPixels,256,256,Bitmap.Config.ARGB_8888))
        } finally { owned.asReversed().forEach { it.release() } }
    }
}
