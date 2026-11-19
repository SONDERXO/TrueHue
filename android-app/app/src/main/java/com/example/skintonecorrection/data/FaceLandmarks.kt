package com.example.skintonecorrection.data

import android.content.Context
import android.graphics.Bitmap
import com.google.mediapipe.framework.image.BitmapImageBuilder
import com.google.mediapipe.tasks.core.BaseOptions
import com.google.mediapipe.tasks.core.Delegate
import com.google.mediapipe.tasks.vision.core.RunningMode
import com.google.mediapipe.tasks.vision.facelandmarker.FaceLandmarker
import org.opencv.android.Utils
import org.opencv.core.Mat
import org.opencv.core.Point
import org.opencv.core.Rect
import org.opencv.imgproc.Imgproc
import java.nio.ByteBuffer

internal object FaceLandmarks {
    data class Detection(val points: List<Point>, val marginFraction: Double)

    /** Return landmarks in whole-frame pixel coordinates using the research crop order. */
    fun detect(context: Context, bgr: Mat, face: Rect, verifiedModel: ByteArray): Detection? {
        val width = bgr.cols()
        val height = bgr.rows()
        require(face.x >= 0 && face.y >= 0 && face.width > 0 && face.height > 0 &&
            face.x + face.width <= width && face.y + face.height <= height)
        val modelBuffer = ByteBuffer.allocateDirect(verifiedModel.size)
        modelBuffer.put(verifiedModel).rewind()
        val options = FaceLandmarker.FaceLandmarkerOptions.builder()
            .setBaseOptions(BaseOptions.builder().setModelAssetBuffer(modelBuffer).setDelegate(Delegate.CPU).build())
            .setRunningMode(RunningMode.IMAGE).setNumFaces(1).setMinFaceDetectionConfidence(.5f).build()
        var result: Detection? = null
        FaceLandmarker.createFromOptions(context, options).use { landmarker ->
            for (fraction in listOf(0.0, .5, 1.5, -1.0)) {
                val pad = (fraction * maxOf(face.width, face.height)).toInt()
                val left = if (fraction < 0) 0 else maxOf(0, face.x - pad)
                val top = if (fraction < 0) 0 else maxOf(0, face.y - pad)
                val right = if (fraction < 0) width else minOf(width, face.x + face.width + pad)
                val bottom = if (fraction < 0) height else minOf(height, face.y + face.height + pad)
                val crop = bgr.submat(Rect(left, top, right - left, bottom - top))
                val rgba = Mat()
                val bitmap = Bitmap.createBitmap(crop.cols(), crop.rows(), Bitmap.Config.ARGB_8888)
                try {
                    Imgproc.cvtColor(crop, rgba, Imgproc.COLOR_BGR2RGBA)
                    Utils.matToBitmap(rgba, bitmap)
                    val image = BitmapImageBuilder(bitmap).build()
                    val detected = try { landmarker.detect(image).faceLandmarks() } finally { image.close() }
                    if (detected.isNotEmpty()) {
                        val points = detected[0].map {
                            Point(it.x().toDouble() * crop.cols() + left, it.y().toDouble() * crop.rows() + top)
                        }
                        result = Detection(points, fraction)
                        break
                    }
                } finally {
                    bitmap.recycle()
                    rgba.release()
                    crop.release()
                }
            }
        }
        // Keep the verified direct buffer reachable until the native graph closes.
        check(modelBuffer.capacity() == verifiedModel.size)
        return result
    }
}
