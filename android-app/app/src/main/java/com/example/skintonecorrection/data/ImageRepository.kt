package com.example.skintonecorrection.data

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Matrix
import android.net.Uri
import androidx.annotation.StringRes
import androidx.exifinterface.media.ExifInterface
import com.example.skintonecorrection.R
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.coroutines.ensureActive
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import kotlin.coroutines.coroutineContext
import org.json.JSONObject
import java.io.ByteArrayOutputStream
import java.io.File
import java.io.FileNotFoundException
import java.security.MessageDigest
import java.util.UUID

data class CorrectionResult(val input:Uri?,val mask:Uri?,val corrected:Uri?,val report:Uri,val success:Boolean,val message:String,
                            val needsGlassesChoice: Boolean = false, val identityControls: Boolean = false)

enum class CorrectionStage { PREPARING, CORRECTING, SAVING }

internal class PhotoProcessingException(@StringRes val userMessage: Int, diagnostic: String,
                                        val retryFaceAnalysis: Boolean = false) :
    IllegalArgumentException(diagnostic)

/** Local processing. Failure never returns the original as a corrected result. */
class ImageRepository internal constructor(
    private val context: Context,
    private val pipeline: (Bitmap, GlassesChoice, JSONObject) -> PipelineImages
) {
    constructor(context: Context) : this(context, Wb314PhotoPipeline(context)::run)

    companion object { private val processingMutex=Mutex() }
    suspend fun runCorrection(
        inputUri: Uri,
        glasses: GlassesChoice = GlassesChoice.UNCERTAIN,
        onStage: (CorrectionStage) -> Unit = {}
    ): CorrectionResult = withContext(Dispatchers.IO) {
        processingMutex.withLock { coroutineContext.ensureActive();runLocked(inputUri, glasses, onStage) }
    }
    private fun runLocked(inputUri: Uri, glasses: GlassesChoice, onStage: (CorrectionStage) -> Unit): CorrectionResult {
        val folder=File(context.noBackupFilesDir,"runs/"+UUID.randomUUID());check(folder.mkdirs())
        val report=JSONObject().put("schema_version","truehue_android_run_v1").put("status","failed")
            .put("experimental",true).put("quality_gate_passed",false).put("platform_pixel_parity_verified",false)
            .put("run_id",folder.name).put("started_epoch_ms",System.currentTimeMillis())
            .put("original_file_modified",false).put("network_calls",false)
            .put("notice","Experimental research correction. Skin tone estimates and correction quality are unvalidated.")
        val started=System.nanoTime();var images:PipelineImages?=null;var message:String
        var needsGlassesChoice = false
        try {
            report.put("failed_stage","decode")
            val bytes=context.contentResolver.openInputStream(inputUri)?.use { stream ->
                val out=ByteArrayOutputStream();val buffer=ByteArray(8192);var n=stream.read(buffer)
                while (n != -1) {
                    if (out.size() + n > 32 * 1024 * 1024) {
                        throw PhotoProcessingException(R.string.error_photo_too_large, "Input exceeds the file size limit")
                    }
                    out.write(buffer, 0, n)
                    n = stream.read(buffer)
                }
                out.toByteArray()
            } ?: throw PhotoProcessingException(R.string.error_photo_unavailable, "Photo stream is unavailable")
            report.put("source_sha256",hash(bytes))
            val bounds=BitmapFactory.Options().apply{inJustDecodeBounds=true};BitmapFactory.decodeByteArray(bytes,0,bytes.size,bounds)
            if (bounds.outWidth <= 0 || bounds.outHeight <= 0) {
                throw PhotoProcessingException(R.string.error_photo_unreadable, "Could not decode photo dimensions")
            }
            report.put("source_width", bounds.outWidth).put("source_height", bounds.outHeight)
            val runtime = Runtime.getRuntime()
            val headroom = runtime.maxMemory() - (runtime.totalMemory() - runtime.freeMemory())
            val pixels = bounds.outWidth.toLong() * bounds.outHeight
            if (!fitsOriginalPhoto(pixels, headroom)) {
                throw PhotoProcessingException(R.string.error_photo_too_large, "Insufficient memory for original dimensions")
            }
            report.put("decoded_sampling",1)
                .put("decode_policy","Original dimensions, EXIF orientation, square256 analysis")
            val decoded=BitmapFactory.decodeByteArray(bytes,0,bytes.size,BitmapFactory.Options().apply{inPreferredConfig=Bitmap.Config.ARGB_8888})
                ?: throw PhotoProcessingException(R.string.error_photo_unreadable, "Photo decoder returned no bitmap")
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
            try {
                onStage(CorrectionStage.CORRECTING)
                images = pipeline(upright, glasses, report)
            }
            finally { if (images == null) upright.recycle() }
            message=if (report.optBoolean("identity_controls")) "WB314 left this photo unchanged."
                else "Experimental correction finished. Inspect the result."
        } catch (request: GlassesChoiceRequired) {
            needsGlassesChoice = true
            message = requireNotNull(request.message)
            report.put("status", "needs_glasses_choice").put("reason", message).remove("failed_stage")
        } catch (cancelled: CancellationException) {
            throw cancelled
        } catch (error: OutOfMemoryError) {
            report.put("status","failed")
            message = context.getString(R.string.error_photo_too_large)
            report.put("reason", "Insufficient memory for original dimensions")
        } catch(error:LinkageError){
            message = context.getString(R.string.error_correction_unavailable)
            report.put("status", "failed").put("reason", error.message ?: error.javaClass.simpleName)
                .put("native_error", error.javaClass.simpleName)
        } catch(error:Exception){
            val stage = report.optString("failed_stage")
            val messageRes = when {
                error is PhotoProcessingException -> error.userMessage
                stage == "wb314_assets" -> R.string.error_correction_unavailable
                stage == "decode" && (error is FileNotFoundException || error is SecurityException) -> R.string.error_photo_unavailable
                stage == "decode" -> R.string.error_photo_unreadable
                else -> R.string.error_processing_failed
            }
            message = context.getString(messageRes)
            report.put("status", "failed").put("reason", error.message ?: error.javaClass.simpleName)
        }
        var input:Uri?=null;var mask:Uri?=null;var corrected:Uri?=null
        images?.let { result ->
            fun save(name:String,image:Bitmap):Uri {
                val file=File(folder,name);file.outputStream().use { check(image.compress(Bitmap.CompressFormat.PNG,100,it)) }
                return Uri.fromFile(file)
            }
            try {
                onStage(CorrectionStage.SAVING)
                val beforeFile = save("photo_used.png",result.input)
                val maskFile = save("skin_mask.png",result.mask)
                val correctedFile = save("experimental_correction.png",result.corrected)
                input = beforeFile
                mask = maskFile
                corrected = correctedFile
            } catch (error: Exception) {
                message = context.getString(R.string.error_result_storage)
                report.put("status", "failed").put("failed_stage", "save")
                    .put("reason", error.message ?: error.javaClass.simpleName)
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
        return CorrectionResult(input,mask,corrected,Uri.fromFile(reportFile),corrected!=null,message,needsGlassesChoice,
            corrected != null && report.optBoolean("identity_controls"))
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

internal fun fitsOriginalPhoto(pixels: Long, headroom: Long): Boolean {
    val workingReserve = 48L * 1024 * 1024
    // Rotation, OpenCV normalization and rendering run separately. Each peaks with two RGBA frames.
    val bytesPerPixelAtPeak = 2L * Int.SIZE_BYTES
    return headroom >= workingReserve && pixels in 1..(headroom - workingReserve) / bytesPerPixelAtPeak
}
