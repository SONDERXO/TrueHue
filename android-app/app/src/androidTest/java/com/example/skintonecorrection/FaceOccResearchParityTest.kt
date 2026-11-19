package com.example.skintonecorrection

import android.graphics.BitmapFactory
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.example.skintonecorrection.data.FaceOccResearchModel
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Assume.assumeTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.opencv.android.OpenCVLoader
import java.io.DataInputStream
import java.io.File
import kotlin.math.abs

@RunWith(AndroidJUnit4::class)
class FaceOccResearchParityTest {
    @Test fun matchesSavedPythonVisibility() {
        val instrumentation = InstrumentationRegistry.getInstrumentation()
        val graphSha = InstrumentationRegistry.getArguments().getString("faceOccGraphSha")
        assumeTrue("Requires the private FaceOcc fixture", graphSha != null)
        assertTrue(OpenCVLoader.initLocal())
        val folder = File(instrumentation.targetContext.filesDir, "faceocc_parity")
        val model = FaceOccResearchModel.load(File(folder, "faceocc.onnx"), requireNotNull(graphSha))
        val report = StringBuilder()
        for (name in listOf("test1", "test2")) {
            val image = requireNotNull(BitmapFactory.decodeFile(File(folder, "$name.png").path))
            val pixels = try {
                assertEquals(256, image.width)
                assertEquals(256, image.height)
                IntArray(65_536).also { image.getPixels(it, 0, 256, 0, 0, 256, 256) }
            } finally {
                image.recycle()
            }
            val rgb = ByteArray(pixels.size * 3)
            for (i in pixels.indices) {
                rgb[i * 3] = (pixels[i] ushr 16).toByte()
                rgb[i * 3 + 1] = (pixels[i] ushr 8).toByte()
                rgb[i * 3 + 2] = pixels[i].toByte()
            }
            val actual = model.logits(rgb)
            var maxError = 0f
            var different = 0
            DataInputStream(File(folder, "$name.bin").inputStream().buffered()).use { reference ->
                for (logit in actual) {
                    val expected = reference.readFloat()
                    maxError = maxOf(maxError, abs(expected - logit))
                    if ((expected > 0f) != (logit > 0f)) different++
                }
                assertEquals(-1, reference.read())
            }
            report.appendLine("$name max_abs_error=$maxError visibility_mismatches=$different")
            File(folder, "result.txt").writeText(report.toString())
            assertTrue("$name maximum logit error was $maxError", maxError <= 0.001f)
            assertEquals("$name visibility mismatches", 0, different)
        }
    }
}
