package com.example.skintonecorrection

import android.graphics.Bitmap
import android.graphics.BitmapFactory
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.example.skintonecorrection.data.GlassesChoice
import com.example.skintonecorrection.data.OnDevicePipeline
import com.example.skintonecorrection.data.Wb314RenderSupport
import com.example.skintonecorrection.data.Wb314ResearchMasks
import com.example.skintonecorrection.data.Wb314ResearchPipeline
import com.example.skintonecorrection.ml.Wb314PixelRenderer
import org.json.JSONArray
import org.json.JSONObject
import org.junit.Assume.assumeTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.opencv.android.OpenCVLoader
import java.io.DataInputStream
import java.io.File

@RunWith(AndroidJUnit4::class)
class Wb314LiveExposurePreviewTest {
    @Test fun checksOriginalSizeBrightnessWithLiveMasks() {
        val args = InstrumentationRegistry.getArguments()
        assumeTrue(args.getString("wb314LiveExposureFixture") == "true")
        val fixture = File(InstrumentationRegistry.getInstrumentation().targetContext.filesDir, "wb314_live_exposure")
        val result = checkPhoto(fixture, args.getString("glassesChoice"), widespreadExposure = true)
        check(result.getInt("live_outside_changes") == 0)
        check(result.getInt("baseline_newly_full") > result.getInt("preview_newly_full"))
    }

    @Test fun protectsTheUncertainBoundaryInTheLivePipeline() {
        val args = InstrumentationRegistry.getArguments()
        assumeTrue(args.getString("wb314MaskBoundaryFixture") == "true")
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val folder = File(context.filesDir, "wb314_boundary_check")
        val results = JSONObject()
        for (name in listOf("adjusted", "identity", "portrait")) {
            val fixture = File(folder, name)
            val expected = JSONObject(File(fixture, "expected.json").readText())
            val result = checkPhoto(fixture, expected.getString("glasses"),
                widespreadExposure = name == "portrait", protectBoundary = true)
            results.put(name, result)
            File(folder, "result.json").writeText(results.toString(2))
            val controls = result.getJSONArray("raw")
            val raw = expected.getJSONArray("raw")
            check((0 until raw.length()).all { controls.getDouble(it) == raw.getDouble(it) })
            check(result.getInt("width") == expected.getInt("width"))
            check(result.getInt("height") == expected.getInt("height"))
            check(result.getInt("live_outside_changes") == 0)
            check(result.getInt("reference_outside_changes") == 0)
            check((result.getInt("changed") == 0) == (name == "identity"))
            if (name == "portrait") {
                check(result.getString("method") == "facial_rgb")
                check(result.getInt("baseline_newly_full") > result.getInt("preview_newly_full"))
            }
        }
    }

    private fun checkPhoto(fixture: File, glassesChoice: String?, widespreadExposure: Boolean,
                           protectBoundary: Boolean = false): JSONObject {
        val args = InstrumentationRegistry.getArguments()
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val assets = File(context.filesDir, "wb314_models")
        check(OpenCVLoader.initLocal())
        val landmark = context.assets.open(OnDevicePipeline.ASSETS + "face_landmarker.task")
            .use { it.readBytes() }
        val generator = Wb314ResearchMasks(context, assets, requireNotNull(args.getString("faceOccGraphSha")), landmark)
        val pipeline = Wb314ResearchPipeline.load(assets, requireNotNull(args.getString("wb314ManifestSha")))
        val glasses = GlassesChoice.valueOf(requireNotNull(glassesChoice))
        val input = checkNotNull(BitmapFactory.decodeFile(File(fixture, "input.png").path))
        try {
            val result = pipeline.correct(input, generator, glasses,
                previewWidespreadExposure = widespreadExposure, previewMaskBoundaryProtection = protectBoundary)
            val bitmap = result.correction.bitmap
            try {
                check(bitmap.width == input.width && bitmap.height == input.height)
                val report = compare(input, result, File(fixture, "reference-mask.bin"))
                File(fixture, "result.json").writeText(report.toString(2))
                if (widespreadExposure) {
                    File(fixture, "output.png").outputStream().buffered().use {
                        check(bitmap.compress(Bitmap.CompressFormat.PNG, 100, it))
                    }
                }
                return report
            } finally {
                bitmap.recycle()
            }
        } finally {
            input.recycle()
        }
    }

    private fun compare(input: Bitmap, auto: Wb314ResearchPipeline.AutoResult, reference: File): JSONObject {
        val width = input.width
        val height = input.height
        val masks = auto.masks
        val decision = auto.correction.exposurePreview
        val baselineSupport = Wb314RenderSupport(width, height, masks.alpha, masks.protected)
        val raw = auto.correction.controls
        val baseline = Wb314PixelRenderer(raw[0], raw[1], raw[2], raw[3], raw[4])
        val measurement = ByteArray(masks.measurement.size)
        val alpha = DoubleArray(masks.alpha.size)
        val protected = BooleanArray(masks.protected.size)
        DataInputStream(reference.inputStream().buffered()).use { data ->
            data.readFully(measurement)
            for (i in alpha.indices) alpha[i] = data.readDouble()
            for (i in protected.indices) protected[i] = data.readBoolean()
            check(data.read() == -1)
        }
        val before = IntArray(width)
        val after = IntArray(width)
        var baselineClipped = 0
        var previewClipped = 0
        var liveOutside = 0
        var referenceOutside = 0
        var changed = 0
        for (y in 0 until height) {
            input.getPixels(before, 0, width, 0, y, width, 1)
            auto.correction.bitmap.getPixels(after, 0, width, 0, y, width, 1)
            for (x in before.indices) {
                val index = (y * 256 / height) * 256 + x * 256 / width
                if (before[x] != after[x]) {
                    changed++
                    if (masks.protected[index] || masks.alpha[index] == 0.0) liveOutside++
                    if (protected[index] || alpha[index] == 0.0) referenceOutside++
                }
                if (hasFullChannel(before[x])) continue
                if (hasFullChannel(after[x])) previewClipped++
                val coverage = baselineSupport.alphaAt(x, y)
                if (coverage > 0 && hasFullChannel(baseline.render(before[x], coverage, false))) baselineClipped++
            }
        }
        return JSONObject()
            .put("width", width).put("height", height).put("leaf", auto.correction.leaf)
            .put("method", decision?.method ?: "original")
            .put("raw", JSONArray(raw.toList()))
            .put("effective", JSONArray((decision?.effectiveControls ?: raw).toList()))
            .put("eligible", decision?.eligiblePixels).put("exposure_clipped", decision?.exposureClippedPixels)
            .put("changed", changed)
            .put("baseline_newly_full", baselineClipped).put("preview_newly_full", previewClipped)
            .put("live_outside_changes", liveOutside).put("reference_outside_changes", referenceOutside)
            .put("measurement_differences", measurement.indices.count { measurement[it] != masks.measurement[it] })
            .put("protected_differences", protected.indices.count { protected[it] != masks.protected[it] })
            .put("support_differences", alpha.indices.count { (alpha[it] > 0.0) != (masks.alpha[it] > 0.0) })
            .put("alpha_differences", alpha.indices.count { alpha[it] != masks.alpha[it] })
    }

    private fun hasFullChannel(pixel: Int) =
        ((pixel shr 16) and 255) == 255 || ((pixel shr 8) and 255) == 255 || (pixel and 255) == 255
}
