package com.example.skintonecorrection

import android.graphics.BitmapFactory
import android.net.Uri
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.example.skintonecorrection.data.GlassesChoice
import com.example.skintonecorrection.data.ImageRepository
import com.example.skintonecorrection.data.OnDevicePipeline
import com.example.skintonecorrection.data.Wb314ResearchMasks
import kotlinx.coroutines.runBlocking
import org.json.JSONObject
import org.junit.Assume.assumeTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.opencv.android.OpenCVLoader
import org.opencv.android.Utils
import org.opencv.core.Mat
import org.opencv.core.Size
import org.opencv.imgproc.Imgproc
import java.io.File
import java.util.Locale

@RunWith(AndroidJUnit4::class)
class Wb314JawlineDiagnosticTest {
    @Test fun processEdgeRepairFixtures() = runBlocking {
        val instrumentation = InstrumentationRegistry.getInstrumentation()
        assumeTrue(InstrumentationRegistry.getArguments().getString("wb314EdgeFixtures") == "true")
        check(BuildConfig.WB314_EDGE_REPAIR || BuildConfig.WB314_SOFT_EDGE)
        val context = instrumentation.targetContext
        val folder = File(context.filesDir, "wb314_edge_fixtures")
        val inputs = checkNotNull(folder.listFiles()).filter { it.extension == "png" }.sortedBy { it.name }
        check(inputs.isNotEmpty())
        val repo = ImageRepository(context)
        for (input in inputs) {
            val prefix = input.nameWithoutExtension
            val glasses = GlassesChoice.valueOf(File(folder, "$prefix.glasses").readText().trim())
            val result = repo.runCorrection(Uri.fromFile(input), glasses)
            val report = File(checkNotNull(result.report.path))
            report.copyTo(File(folder, "$prefix.json"))
            check(result.success) { report.readText() }
            repo.export(checkNotNull(result.corrected), Uri.fromFile(File(folder, "$prefix.result")))
            File(checkNotNull(result.mask?.path)).copyTo(File(folder, "$prefix.mask"))
        }
    }

    @Test fun traceSavedJawlineCases() {
        val arguments = InstrumentationRegistry.getArguments()
        val ids = arguments.getString("wb314JawlineRuns")?.split(",").orEmpty()
        assumeTrue(ids.isNotEmpty())
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        check(OpenCVLoader.initLocal())
        val landmarker = context.assets.open(OnDevicePipeline.ASSETS + "face_landmarker.task").use { it.readBytes() }
        val generator = Wb314ResearchMasks(context, File(context.filesDir, "wb314_models"),
            "706b236065be76c0d68a67d5497a53e153debc43894aae0ce16f0fb22eebc936", landmarker)
        for (id in ids) {
            check(id.matches(Regex("[a-f0-9-]{36}")))
            val run = File(context.noBackupFilesDir, "runs/$id")
            val report = JSONObject(File(run, "report.json").readText())
            val glasses = GlassesChoice.valueOf(report.getString("glasses_choice").uppercase(Locale.ROOT))
            val input = checkNotNull(BitmapFactory.decodeFile(File(run, "photo_used.png").path))
            val rgba = Mat()
            val small = Mat()
            val bgr = Mat()
            try {
                Utils.bitmapToMat(input, rgba)
                Imgproc.resize(rgba, small, Size(256.0, 256.0), 0.0, 0.0, Imgproc.INTER_AREA)
                Imgproc.cvtColor(small, bgr, Imgproc.COLOR_RGBA2BGR)
                val current = generator.generate(bgr, glasses, protectUncertainBoundary = true)
                val earlier = generator.generate(bgr, glasses)
                val saved = checkNotNull(BitmapFactory.decodeFile(File(run, "skin_mask.png").path))
                try {
                    check(saved.width == 256 && saved.height == 256)
                    val pixels = IntArray(256 * 256)
                    saved.getPixels(pixels, 0, 256, 0, 0, 256, 256)
                    check(pixels.indices.all { (pixels[it] == -1) == (current.masks.alpha[it] > 0) })
                } finally {
                    saved.recycle()
                }
                File(context.filesDir, "jawline-$id.bin").outputStream().buffered().use { out ->
                    out.write(current.categories)
                    out.write(current.visibility)
                    out.write(ByteArray(256 * 256) { if (earlier.masks.alpha[it] > 0) 1 else 0 })
                    out.write(ByteArray(256 * 256) { if (current.masks.protected[it]) 1 else 0 })
                    out.write(ByteArray(256 * 256) { (current.masks.alpha[it] * 255).toInt().toByte() })
                }
            } finally {
                input.recycle()
                rgba.release()
                small.release()
                bgr.release()
            }
        }
    }
}
