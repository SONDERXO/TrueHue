package com.example.skintonecorrection

import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.example.skintonecorrection.data.ImageRepository
import com.example.skintonecorrection.data.Wb314ResearchPipeline
import kotlinx.coroutines.runBlocking
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.opencv.android.OpenCVLoader
import java.io.DataInputStream
import java.io.File

/** Run with the explicitly staged local WB314 fixture and its asset manifest digest. */
@RunWith(AndroidJUnit4::class)
class Wb314ResearchParityTest {
    @Test fun usesMatchingMasksAndExportsPythonPixelsAtOriginalSize() = runBlocking {
        val instrumentation = InstrumentationRegistry.getInstrumentation()
        val manifestSha = InstrumentationRegistry.getArguments().getString("wb314ManifestSha")
        assumeTrue("Requires a staged local research fixture", manifestSha != null)
        val context = instrumentation.targetContext
        val folder = File(context.filesDir, "wb314_parity")
        assertTrue(OpenCVLoader.initLocal())
        val pipeline = Wb314ResearchPipeline.load(folder, requireNotNull(manifestSha))
        val repository = ImageRepository(context)
        for (name in listOf("adjusted", "preserved")) {
            val original = requireNotNull(BitmapFactory.decodeFile(File(folder, "${name}_input.png").path))
            val expectedBitmap = requireNotNull(BitmapFactory.decodeFile(File(folder, "${name}_output.png").path))
            try {
                DataInputStream(File(folder, "$name.bin").inputStream().buffered()).use { fixture ->
                    val digest = ByteArray(64).also { fixture.readFully(it) }.toString(Charsets.US_ASCII)
                    val measurement = ByteArray(65_536).also { fixture.readFully(it) }
                    val alpha = DoubleArray(65_536) { fixture.readDouble() }
                    val protected = BooleanArray(65_536) { fixture.readBoolean() }
                    val features = DoubleArray(314) { fixture.readDouble() }
                    val controls = DoubleArray(5) { fixture.readDouble() }
                    val leaf = fixture.readInt()
                    assertEquals(-1, fixture.read())
                    val result = pipeline.correct(original, measurement, alpha, protected, digest)
                    try {
                        assertEquals(leaf, result.leaf)
                        assertArrayEquals(features, result.features, 0.0)
                        assertArrayEquals(controls, result.controls, 0.0)
                        val png = File(context.cacheDir, "wb314_$name.png")
                        png.outputStream().use { assertTrue(result.bitmap.compress(Bitmap.CompressFormat.PNG, 100, it)) }
                        val exported = File(context.cacheDir, "wb314_${name}_export.png")
                        repository.export(Uri.fromFile(png), Uri.fromFile(exported))
                        val decoded = requireNotNull(BitmapFactory.decodeFile(exported.path))
                        try {
                            assertEquals(original.width, decoded.width)
                            assertEquals(original.height, decoded.height)
                            assertArrayEquals(pixels(expectedBitmap), pixels(decoded))
                            assertEquals(name == "preserved", pixels(original).contentEquals(pixels(decoded)))
                        } finally {
                            decoded.recycle()
                            png.delete()
                            exported.delete()
                        }
                    } finally {
                        result.bitmap.recycle()
                    }
                }
            } finally {
                original.recycle()
                expectedBitmap.recycle()
            }
        }
    }

    private fun pixels(image: Bitmap) = IntArray(image.width * image.height).also {
        image.getPixels(it, 0, image.width, 0, 0, image.width, image.height)
    }
}
