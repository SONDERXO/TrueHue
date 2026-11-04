package com.example.skintonecorrection

import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.example.skintonecorrection.data.ImageRepository
import com.example.skintonecorrection.data.OnDevicePipeline
import kotlinx.coroutines.runBlocking
import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith
import java.io.File

/** Must run on an emulator/phone. Compilation alone is not a pass. */
@RunWith(AndroidJUnit4::class)
class OnDevicePipelineTest {
    @Test fun noFaceFailsWithReportAndWithoutCorrectedImage()=runBlocking {
        val context=InstrumentationRegistry.getInstrumentation().targetContext
        val source=File(context.cacheDir,"no_face_test.png")
        val bitmap=Bitmap.createBitmap(256,256,Bitmap.Config.ARGB_8888)
        source.outputStream().use{bitmap.compress(Bitmap.CompressFormat.PNG,100,it)};bitmap.recycle()
        val result=ImageRepository(context).runCorrection(Uri.fromFile(source))
        assertFalse(result.success);assertNull(result.corrected)
        val report=JSONObject(File(result.report.path!!).readText())
        assertEquals("face_detection",report.getString("failed_stage"));assertEquals(0,report.getInt("face_count"))
        assertFalse(report.getBoolean("platform_pixel_parity_verified"))
    }
    @Test fun fixedKnownDevelopmentExampleMatchesPythonPixels(){
        val instrumentation=InstrumentationRegistry.getInstrumentation()
        val input=instrumentation.context.assets.open("pipeline_fixture/photo_used.png").use{BitmapFactory.decodeStream(it)}!!
        val report=JSONObject()
        val evidence=File(instrumentation.targetContext.noBackupFilesDir,"parity_"+System.currentTimeMillis()).apply{check(mkdirs())}
        val output=try {OnDevicePipeline(instrumentation.targetContext).run(input,report)}
            finally {File(evidence,"report.json").writeText(report.toString(2))}
        for((name,bitmap) in listOf("photo_used.png" to output.input,"skin_mask.png" to output.mask,"experimental_correction.png" to output.corrected)){
            File(evidence,name).outputStream().use{check(bitmap.compress(Bitmap.CompressFormat.PNG,100,it))}
        }
        assertEquals("experimental_success",report.getString("status"))
        fun pixels(bitmap:Bitmap)=IntArray(bitmap.width*bitmap.height).also{bitmap.getPixels(it,0,bitmap.width,0,0,bitmap.width,bitmap.height)}
        try {
            for((name,actual) in listOf("photo_used.png" to output.input,"skin_mask.png" to output.mask,"experimental_correction.png" to output.corrected)){
                val expected=instrumentation.context.assets.open("pipeline_fixture/$name").use{BitmapFactory.decodeStream(it)}!!
                try{assertArrayEquals(name,pixels(expected),pixels(actual))}finally{expected.recycle()}
            }
        }finally{input.recycle();output.input.recycle();output.mask.recycle();output.corrected.recycle()}
    }
}
