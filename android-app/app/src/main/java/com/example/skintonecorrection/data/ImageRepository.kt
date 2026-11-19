package com.example.skintonecorrection.data

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Matrix
import android.net.Uri
import androidx.exifinterface.media.ExifInterface
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.coroutines.ensureActive
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlin.coroutines.coroutineContext
import org.json.JSONObject
import java.io.ByteArrayOutputStream
import java.io.File
import java.security.MessageDigest
import java.util.UUID

data class CorrectionResult(val input:Uri?,val mask:Uri?,val corrected:Uri?,val report:Uri,val success:Boolean,val message:String)

/** Local processing. Failure never returns the original as a corrected result. */
class ImageRepository internal constructor(
    private val context: Context,
    private val pipeline: (Bitmap, GlassesChoice, JSONObject) -> PipelineImages
) {
    constructor(context: Context) : this(context, Wb314PhotoPipeline(context)::run)

    companion object { private val processingMutex=Mutex() }
    suspend fun runCorrection(inputUri:Uri, glasses: GlassesChoice = GlassesChoice.UNCERTAIN):CorrectionResult=withContext(Dispatchers.IO) {
        processingMutex.withLock { coroutineContext.ensureActive();runLocked(inputUri, glasses) }
    }
    private fun runLocked(inputUri:Uri, glasses: GlassesChoice):CorrectionResult {
        val folder=File(context.noBackupFilesDir,"runs/"+UUID.randomUUID());check(folder.mkdirs())
        val report=JSONObject().put("schema_version","truehue_android_run_v1").put("status","failed")
            .put("experimental",true).put("quality_gate_passed",false).put("platform_pixel_parity_verified",false)
            .put("run_id",folder.name).put("started_epoch_ms",System.currentTimeMillis())
            .put("original_file_modified",false).put("network_calls",false)
            .put("notice","Experimental research correction. Skin tone estimates and correction quality are unvalidated.")
        val started=System.nanoTime();var images:PipelineImages?=null;var message:String
        try {
            report.put("failed_stage","decode")
            val bytes=context.contentResolver.openInputStream(inputUri)?.use { stream ->
                val out=ByteArrayOutputStream();val buffer=ByteArray(8192);var n=stream.read(buffer)
                while(n!=-1){require(out.size()+n<=32*1024*1024){"This file is too large. Choose a smaller photo."};out.write(buffer,0,n);n=stream.read(buffer)}
                out.toByteArray()
            } ?: error("The selected photo could not be opened. Select it again.")
            report.put("source_sha256",hash(bytes))
            val bounds=BitmapFactory.Options().apply{inJustDecodeBounds=true};BitmapFactory.decodeByteArray(bytes,0,bytes.size,bounds)
            require(bounds.outWidth>0 && bounds.outHeight>0){"This file could not be decoded as a photo."}
            val runtime = Runtime.getRuntime()
            val headroom = runtime.maxMemory() - (runtime.totalMemory() - runtime.freeMemory())
            val pixels = bounds.outWidth.toLong() * bounds.outHeight
            require(pixels <= (headroom - 16L * 1024 * 1024) / 16) {
                "This photo is too large to process at its original size on this phone."
            }
            report.put("decoded_sampling",1).put("source_width",bounds.outWidth).put("source_height",bounds.outHeight)
                .put("decode_policy","Original dimensions, EXIF orientation, square256 analysis")
            val decoded=BitmapFactory.decodeByteArray(bytes,0,bytes.size,BitmapFactory.Options().apply{inPreferredConfig=Bitmap.Config.ARGB_8888})
                ?: error("The selected photo could not be decoded.")
            val orientation=bytes.inputStream().use { ExifInterface(it).getAttributeInt(ExifInterface.TAG_ORIENTATION,ExifInterface.ORIENTATION_NORMAL) }
            report.put("exif_orientation",orientation)
            val matrix=Matrix()
            when(orientation){
                2->matrix.setScale(-1f,1f);3->matrix.setRotate(180f);4->matrix.setScale(1f,-1f)
                5->{matrix.setRotate(90f);matrix.postScale(-1f,1f)}
                6->matrix.setRotate(90f)
                7->{matrix.setRotate(-90f);matrix.postScale(-1f,1f)}
                8->matrix.setRotate(-90f)
            }
            val upright = try {
                Bitmap.createBitmap(decoded,0,0,decoded.width,decoded.height,matrix,false)
            } catch (error: Throwable) {
                decoded.recycle()
                throw error
            }
            if (upright !== decoded) decoded.recycle()
            try { images=pipeline(upright, glasses, report) }
            finally { if (images == null) upright.recycle() }
            message=if (report.optBoolean("identity_controls")) "WB314 left this photo unchanged."
                else "Experimental correction finished. Inspect the result."
        } catch (error: OutOfMemoryError) {
            report.put("status","failed")
            message="This photo could not be processed at its original size with the available memory."
            report.put("reason",message)
        } catch(error:LinkageError){
            report.put("status","failed");message="The local image engine is unavailable on this device. Save the report for diagnosis."
            report.put("reason",message).put("native_error",error.javaClass.simpleName);images=null
        } catch(error:Exception){
            report.put("status","failed");message=error.message ?: "The photo could not be processed. Try another photo."
            report.put("reason",message);images=null
        }
        var input:Uri?=null;var mask:Uri?=null;var corrected:Uri?=null
        images?.let { result ->
            fun save(name:String,image:Bitmap):Uri {
                val file=File(folder,name);file.outputStream().use { check(image.compress(Bitmap.CompressFormat.PNG,100,it)) }
                return Uri.fromFile(file)
            }
            try {
                val beforeFile = save("photo_used.png",result.input)
                val maskFile = save("skin_mask.png",result.mask)
                val correctedFile = save("experimental_correction.png",result.corrected)
                input = beforeFile
                mask = maskFile
                corrected = correctedFile
            } catch (error: Exception) {
                message = "The result could not be stored. Check available storage and try again."
                report.put("status","failed").put("failed_stage","save").put("reason",message)
            }
            finally{result.input.recycle();result.mask.recycle();result.corrected.recycle()}
        }
        report.put("elapsed_ms",(System.nanoTime()-started)/1e6).put("timing_scope","Includes asset initialization; not a benchmark")
        val files=JSONObject();folder.listFiles()?.forEach { file ->
            val digest = MessageDigest.getInstance("SHA-256")
            file.inputStream().use { stream ->
                val buffer = ByteArray(8192)
                var count = stream.read(buffer)
                while (count != -1) {
                    digest.update(buffer, 0, count)
                    count = stream.read(buffer)
                }
            }
            files.put(file.name,digest.digest().joinToString(""){"%02x".format(it)})
        };report.put("output_sha256",files)
        val reportFile=File(folder,"report.json");reportFile.writeText(report.toString(2))
        return CorrectionResult(input,mask,corrected,Uri.fromFile(reportFile),corrected!=null,message)
    }
    suspend fun export(source:Uri,destination:Uri)=withContext(Dispatchers.IO) {
        context.contentResolver.openInputStream(source).use { input ->
            requireNotNull(input){"Saved result is unavailable."}
            context.contentResolver.openOutputStream(destination,"w").use { output ->
                requireNotNull(output){"This location could not be written."};input.copyTo(output)
            }
        };Unit
    }
    private fun hash(bytes:ByteArray)=MessageDigest.getInstance("SHA-256").digest(bytes).joinToString(""){"%02x".format(it)}
}
