package com.example.skintonecorrection

import android.content.pm.ActivityInfo
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Canvas
import android.graphics.Rect
import android.net.Uri
import androidx.lifecycle.ViewModelProvider
import androidx.test.core.app.ActivityScenario
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.example.skintonecorrection.data.ImageRepository
import com.example.skintonecorrection.ui.ProcessingState
import com.example.skintonecorrection.ui.SharedViewModel
import kotlinx.coroutines.runBlocking
import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith
import java.io.File
import java.util.UUID

@RunWith(AndroidJUnit4::class)
class ReliabilityTest {
    private val instrumentation get()=InstrumentationRegistry.getInstrumentation()
    private val context get()=instrumentation.targetContext
    private fun file(name:String)=File(context.cacheDir,UUID.randomUUID().toString()+name)
    private fun photo():File=file(".png").also{f->instrumentation.context.assets.open("pipeline_fixture/photo_used.png").use{input->f.outputStream().use{input.copyTo(it)}}}
    private fun waitFor(predicate:()->Boolean){
        val end=System.currentTimeMillis()+20000
        while(!predicate() && System.currentTimeMillis()<end)Thread.sleep(50)
        assertTrue("State did not finish within20seconds",predicate())
    }
    @Test fun multipleFacesFailWithoutCorrection()=runBlocking {
        val source=photo();val image=BitmapFactory.decodeFile(source.path)
        val combined=Bitmap.createBitmap(256,256,Bitmap.Config.ARGB_8888)
        val canvas=Canvas(combined);canvas.drawColor(android.graphics.Color.BLACK)
        canvas.drawBitmap(image,null,Rect(0,64,128,192),null);canvas.drawBitmap(image,null,Rect(128,64,256,192),null)
        val input=file(".png");input.outputStream().use{combined.compress(Bitmap.CompressFormat.PNG,100,it)}
        image.recycle();combined.recycle()
        val result=ImageRepository(context).runCorrection(Uri.fromFile(input))
        val report=JSONObject(File(result.report.path!!).readText())
        assertFalse(result.success);assertNull(result.corrected)
        assertEquals("face_detection",report.getString("failed_stage"));assertTrue(report.getInt("face_count")>1)
        assertTrue(result.message.contains("More than one"))
    }
    @Test fun failureReportSaveErrorCanBeRetried()=runBlocking {
        val corrupt=file(".png").apply{writeText("not an image")}
        val original=corrupt.readBytes();val repository=ImageRepository(context)
        val result=repository.runCorrection(Uri.fromFile(corrupt))
        assertFalse(result.success);assertNull(result.corrected)
        val blocker=file(".txt").apply{writeText("not a folder")}
        var failed=false
        try{repository.export(result.report,Uri.fromFile(File(blocker,"report.json")))}catch(expected:Exception){failed=true}
        assertTrue(failed)
        val destination=file(".json");repository.export(result.report,Uri.fromFile(destination))
        assertArrayEquals(File(result.report.path!!).readBytes(),destination.readBytes())
        assertArrayEquals(original,corrupt.readBytes())
        assertEquals("decode",JSONObject(destination.readText()).getString("failed_stage"))
    }
    @Test fun rotationDuringProcessingAndNewSelectionClearOldResults(){
        ActivityScenario.launch(MainActivity::class.java).use { scenario ->
            lateinit var first:SharedViewModel
            val input=photo()
            scenario.onActivity { activity ->
                first=ViewModelProvider(activity)[SharedViewModel::class.java]
                first.selectImage(Uri.fromFile(input));first.startProcessing()
                assertEquals(ProcessingState.PROCESSING,first.uiState.value.processingState)
                activity.requestedOrientation=ActivityInfo.SCREEN_ORIENTATION_LANDSCAPE
            }
            waitFor{first.uiState.value.processingState!=ProcessingState.PROCESSING}
            assertEquals(ProcessingState.SUCCESS,first.uiState.value.processingState)
            val report=first.uiState.value.reportUri;assertNotNull(report)
            scenario.recreate()
            scenario.onActivity { activity ->
                val retained=ViewModelProvider(activity)[SharedViewModel::class.java]
                assertSame(first,retained);assertEquals(report,retained.uiState.value.reportUri)
                val corrupt=file(".png").apply{writeText("invalid")}
                retained.selectImage(Uri.fromFile(corrupt))
                assertNull(retained.uiState.value.correctedImageUri);assertNull(retained.uiState.value.reportUri)
                assertNull(retained.uiState.value.maskUri);assertEquals(ProcessingState.IDLE,retained.uiState.value.processingState)
                retained.startProcessing()
            }
            waitFor{first.uiState.value.processingState!=ProcessingState.PROCESSING}
            assertEquals(ProcessingState.ERROR,first.uiState.value.processingState)
            assertNull(first.uiState.value.correctedImageUri)
        }
    }
    @Test fun supersededProcessingCannotPublishAnOldResult(){
        ActivityScenario.launch(MainActivity::class.java).use { scenario ->
            lateinit var model:SharedViewModel
            val good=photo();val bad=file(".png").apply{writeText("invalid")}
            scenario.onActivity { activity ->
                model=ViewModelProvider(activity)[SharedViewModel::class.java]
                model.selectImage(Uri.fromFile(good));model.startProcessing()
                model.selectImage(Uri.fromFile(bad));model.startProcessing()
            }
            waitFor{model.uiState.value.processingState!=ProcessingState.PROCESSING}
            instrumentation.waitForIdleSync()
            assertEquals(Uri.fromFile(bad),model.uiState.value.selectedImageUri)
            assertEquals(ProcessingState.ERROR,model.uiState.value.processingState)
            assertNull(model.uiState.value.correctedImageUri)
        }
    }
}
