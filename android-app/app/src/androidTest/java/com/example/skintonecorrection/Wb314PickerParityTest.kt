package com.example.skintonecorrection

import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.example.skintonecorrection.data.GlassesChoice
import com.example.skintonecorrection.data.ImageRepository
import com.example.skintonecorrection.data.Wb314PhotoPipeline
import kotlinx.coroutines.runBlocking
import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Test
import org.junit.runner.RunWith
import java.io.DataInputStream
import java.io.File

/** Uses the same URI processing and export entry points as SharedViewModel. */
@RunWith(AndroidJUnit4::class)
class Wb314PickerParityTest {
    @Test fun defaultsToWb314AndExportsOriginalSize() = runBlocking {
        val instrumentation = InstrumentationRegistry.getInstrumentation()
        assumeTrue("Requires the private picker fixture", InstrumentationRegistry.getArguments().getString("wb314PickerFixture") == "true")
        val context = instrumentation.targetContext
        val fixture = File(context.filesDir, "wb314_picker_test")
        val receipt = File(fixture, "result.txt").apply { writeText("") }
        val repository = ImageRepository(context)
        for (name in listOf("adjusted", "preserved")) {
            val input = File(fixture, "${name}_input.png")
            val result = repository.runCorrection(Uri.fromFile(input), GlassesChoice.OPAQUE)
            assertTrue(result.message, result.success)
            val report = JSONObject(File(requireNotNull(result.report.path)).readText())
            assertEquals(Wb314PhotoPipeline.MODEL_SHA, report.getString("model_sha256"))
            assertEquals("opaque", report.getString("glasses_choice"))
            assertEquals(name == "preserved", report.getBoolean("identity_controls"))
            val exported = File(fixture, "${name}_export.png")
            repository.export(requireNotNull(result.corrected), Uri.fromFile(exported))
            val before = bitmap(input)
            val expected = bitmap(File(fixture, "${name}_output.png"))
            val output = bitmap(exported)
            val mask = bitmap(File(requireNotNull(result.mask?.path)))
            try {
                val width = before.width
                val height = before.height
                assertEquals(512, width)
                assertEquals(768, height)
                assertEquals(width, output.width)
                assertEquals(height, output.height)
                assertEquals(256, mask.width)
                assertEquals(256, mask.height)
                DataInputStream(File(fixture, "$name.bin").inputStream().buffered()).use { data ->
                    data.skipBytes(64 + 65_536)
                    val alpha = DoubleArray(65_536) { data.readDouble() }
                    val protected = BooleanArray(65_536) { data.readBoolean() }
                    data.skipBytes(314 * Double.SIZE_BYTES)
                    val controls = DoubleArray(5) { data.readDouble() }
                    val leaf = data.readInt()
                    assertEquals(-1, data.read())
                    val maskPixels = pixels(mask)
                    val inputPixels = pixels(before)
                    val actualPixels = pixels(output)
                    val expectedPixels = pixels(expected)
                    val maskMismatches = maskPixels.indices.count { (maskPixels[it] == -1) != (alpha[it] > 0.0) }
                    val outputMismatches = expectedPixels.indices.count { expectedPixels[it] != actualPixels[it] }
                    var changed = 0
                    var changedOutside = 0
                    for (i in inputPixels.indices) {
                        if (actualPixels[i] != inputPixels[i]) {
                            changed++
                            val analysis = (i / width * 256 / height) * 256 + (i % width * 256 / width)
                            if (protected[analysis] || alpha[analysis] == 0.0) changedOutside++
                        }
                    }
                    receipt.appendText("$name width=$width height=$height mask_mismatches=$maskMismatches " +
                        "python_pixel_mismatches=$outputMismatches changed_pixels=$changed outside_changes=$changedOutside\n")
                    val actualControls = report.getJSONArray("controls")
                    assertArrayEquals(controls, DoubleArray(5) { actualControls.getDouble(it) }, 0.0)
                    assertEquals(leaf, report.getInt("leaf"))
                    assertEquals("Correction support", 0, maskMismatches)
                    assertEquals("Export pixels", 0, outputMismatches)
                    assertEquals("Protected and outside pixels", 0, changedOutside)
                    assertEquals(name == "preserved", changed == 0)
                }
            } finally {
                mask.recycle()
                output.recycle()
                expected.recycle()
                before.recycle()
                exported.delete()
                File(requireNotNull(result.report.path)).parentFile?.let { folder ->
                    listOf(result.input, result.corrected, result.mask, result.report).forEach { uri ->
                        uri?.path?.let { File(it).delete() }
                    }
                    folder.delete()
                }
            }
        }
    }

    private fun bitmap(file: File): Bitmap = requireNotNull(BitmapFactory.decodeFile(file.path))
    private fun pixels(bitmap: Bitmap) = IntArray(bitmap.width * bitmap.height).also {
        bitmap.getPixels(it, 0, bitmap.width, 0, 0, bitmap.width, bitmap.height)
    }
}
