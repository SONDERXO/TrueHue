package com.example.skintonecorrection

import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.example.skintonecorrection.data.ImageRepository
import com.example.skintonecorrection.data.OnDevicePipeline
import com.example.skintonecorrection.ml.Wb314Features
import kotlinx.coroutines.runBlocking
import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Test
import org.junit.runner.RunWith
import org.opencv.android.OpenCVLoader
import org.opencv.core.CvType
import org.opencv.core.Mat
import org.opencv.core.Scalar
import java.io.File

/** Must run on an emulator/phone. Compilation alone is not a pass. */
@RunWith(AndroidJUnit4::class)
class OnDevicePipelineTest {
    @Test fun wb314FeatureAssemblyMatchesPythonForGeneratedRgb() {
        assertTrue(OpenCVLoader.initLocal())
        val rgb = Mat(256, 256, CvType.CV_8UC3, Scalar(180.0, 100.0, 0.0))
        try {
            val coefficients = FloatArray(33) { it * 0.125f }
            val actual = Wb314Features.extract(
                rgb, ByteArray(256 * 256) { -1 }, doubleArrayOf(-90.0, 90.0),
                doubleArrayOf(5.0, 5.0), coefficients
            )
            // Python features281 on this generated RGB image and constant test mapping.
            val image = floatArrayOf(
                50.5882f, 27f, 59f, 0.5712f, 5f, 0.5833765268325806f, -4.6151204109191895f,
                50.58823776245117f, 50.58823776245117f, 50.58823776245117f, 1f, 0f, 100f, 100f, 100f
            )
            val expected = DoubleArray(314) { index ->
                when {
                    index < image.size -> image[index].toDouble()
                    index >= 281 -> coefficients[index - 281].toDouble()
                    else -> 0.0
                }
            }
            assertArrayEquals(expected, actual, 0.0)
        } finally {
            rgb.release()
        }
    }

    @Test fun exportedCorrectionUsesOriginalPixelsAndDimensions() = runBlocking {
        val test = InstrumentationRegistry.getInstrumentation()
        val square = test.context.assets.open("pipeline_fixture/photo_used.png").use { BitmapFactory.decodeStream(it) }!!
        val width = 2304
        val height = 512
        val original = Bitmap.createScaledBitmap(square, width, height, false)
        square.recycle()
        val file = File(test.targetContext.cacheDir, "original_size_test.png")
        try {
            file.outputStream().use { check(original.compress(Bitmap.CompressFormat.PNG, 100, it)) }
            val repository = ImageRepository(test.targetContext)
            val result = repository.runCorrection(Uri.fromFile(file))
            assertTrue(result.message, result.success)
            val saved = File(test.targetContext.cacheDir, "original_size_export.png")
            repository.export(result.corrected!!, Uri.fromFile(saved))
            val output = BitmapFactory.decodeFile(saved.path)!!
            val mask = BitmapFactory.decodeFile(result.mask!!.path)!!
            try {
                assertEquals(width, output.width)
                assertEquals(height, output.height)
                var unchangedOutside = 0
                var changedInside = 0
                val before = IntArray(width)
                val after = IntArray(width)
                for (y in 0 until height) {
                    original.getPixels(before, 0, width, 0, y, width, 1)
                    output.getPixels(after, 0, width, 0, y, width, 1)
                    for (x in 0 until width) {
                        if (mask.getPixel(x / 9, y / 2) == -1) {
                            if (before[x] != after[x]) changedInside++
                        } else {
                            assertEquals(before[x], after[x])
                            unchangedOutside++
                        }
                    }
                }
                assertTrue(changedInside > 0)
                assertTrue(unchangedOutside > 0)
            } finally {
                output.recycle()
                mask.recycle()
            }
        } finally {
            original.recycle()
        }
    }

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
