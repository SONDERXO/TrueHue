package com.example.skintonecorrection

import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.example.skintonecorrection.data.OnDevicePipeline
import com.example.skintonecorrection.data.ResearchMaskRules
import com.example.skintonecorrection.data.Wb314ResearchMasks
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Assume.assumeTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.opencv.android.OpenCVLoader
import org.opencv.core.CvType
import org.opencv.core.Mat
import org.opencv.core.Rect
import java.io.DataInputStream
import java.io.File
import kotlin.math.abs

@RunWith(AndroidJUnit4::class)
class Wb314ResearchMaskParityTest {
    @Test fun generatesMasksFromSavedAnalysisImages() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val sha = InstrumentationRegistry.getArguments().getString("faceOccGraphSha")
        assumeTrue("Requires the private WB314 mask fixture", sha != null)
        assertTrue(OpenCVLoader.initLocal())
        val folder = File(context.filesDir, "wb314_masks")
        val landmarker = context.assets.open(OnDevicePipeline.ASSETS + "face_landmarker.task").use { it.readBytes() }
        val generator = Wb314ResearchMasks(context, folder, requireNotNull(sha), landmarker)
        val report = File(folder, "result.txt").apply { writeText("") }
        var allExact = true
        val pixels = 256 * 256
        for (name in listOf("test1", "test2")) {
            val frame = Mat(256, 256, CvType.CV_8UC3)
            try {
                DataInputStream(File(folder, "$name.bin").inputStream().buffered()).use { data ->
                    val box = Rect(data.readInt(), data.readInt(), data.readInt(), data.readInt())
                    val glasses = ResearchMaskRules.Glasses.entries[data.readUnsignedByte()]
                    fun bytes(size: Int) = ByteArray(size).also { data.readFully(it) }
                    assertEquals(pixels * 3, frame.put(0, 0, bytes(pixels * 3)))
                    val categories = bytes(pixels)
                    val visibility = bytes(pixels)
                    val baseline = bytes(pixels)
                    val measurement = bytes(pixels)
                    val protected = bytes(pixels)
                    val alpha = DoubleArray(pixels) { data.readDouble() }
                    assertEquals(-1, data.read())

                    val actual = generator.generate(frame, glasses)
                    val masks = actual.masks
                    val differences = linkedMapOf(
                        "box" to if (actual.faceBox == box) 0 else 1,
                        "categories" to differences(categories, actual.categories),
                        "visibility" to differences(visibility, actual.visibility),
                        "baseline" to differences(baseline, masks.baseline),
                        "measurement" to differences(measurement, masks.measurement),
                        "protected" to protected.indices.count { (protected[it] != 0.toByte()) != masks.protected[it] },
                        "support" to alpha.indices.count { (alpha[it] > 0.0) != (masks.alpha[it] > 0.0) },
                        "alpha" to alpha.indices.count { alpha[it] != masks.alpha[it] }
                    )
                    val maxAlphaError = alpha.indices.maxOf { abs(alpha[it] - masks.alpha[it]) }
                    report.appendText("$name $differences max_alpha_error=$maxAlphaError\n")
                    assertTrue("Protected pixels must have zero alpha", masks.alpha.indices.none {
                        masks.protected[it] && masks.alpha[it] != 0.0
                    })
                    allExact = allExact && differences.values.all { it == 0 }
                }
            } finally {
                frame.release()
            }
        }
        assertTrue("WB314 masks or upstream inputs differed from Python. See result.txt.", allExact)
    }

    private fun differences(expected: ByteArray, actual: ByteArray): Int {
        assertEquals(expected.size, actual.size)
        return expected.indices.count { expected[it] != actual[it] }
    }
}
