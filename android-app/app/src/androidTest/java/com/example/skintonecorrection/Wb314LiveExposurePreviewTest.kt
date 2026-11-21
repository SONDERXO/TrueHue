package com.example.skintonecorrection

import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.example.skintonecorrection.data.GlassesChoice
import com.example.skintonecorrection.data.ImageRepository
import com.example.skintonecorrection.data.OnDevicePipeline
import com.example.skintonecorrection.data.Wb314RenderSupport
import com.example.skintonecorrection.data.Wb314ResearchMasks
import com.example.skintonecorrection.data.Wb314ResearchPipeline
import com.example.skintonecorrection.ml.Wb314PixelRenderer
import kotlinx.coroutines.runBlocking
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
    @Test fun checksNormalPickerProcessingAndExport() = runBlocking {
        val instrumentation = InstrumentationRegistry.getInstrumentation()
        assumeTrue(InstrumentationRegistry.getArguments().getString("wb314PickerFixture") == "true")
        check(BuildConfig.WB314_PICKER_FIXES)
        val context = instrumentation.targetContext
        val repository = ImageRepository(context)
        val folder = File(context.filesDir, "wb314_boundary_check")
        for (name in listOf("adjusted", "identity", "portrait")) {
            val fixture = File(folder, name)
            val expected = JSONObject(File(fixture, "expected.json").readText())
            val input = File(fixture, "input.png")
            val result = repository.runCorrection(Uri.fromFile(input), GlassesChoice.valueOf(expected.getString("glasses")))
            val report = JSONObject(File(requireNotNull(result.report.path)).readText())
            check(result.success) { report.toString() }
            check(report.getBoolean("picker_fixes"))
            val raw = expected.getJSONArray("raw")
            val actual = report.getJSONArray("controls")
            check((0 until raw.length()).all { actual.getDouble(it) == raw.getDouble(it) })
            check(result.identityControls == (name == "identity"))
            val corrected = requireNotNull(result.corrected)
            val output = File(fixture, "export.png")
            val comparison = if (result.identityControls) {
                File(requireNotNull(corrected.path))
            } else {
                repository.export(corrected, Uri.fromFile(output))
                output
            }
            val area = readReferenceSupport(File(fixture, "reference-mask.bin"))
            val (changed, clipped) = comparePickerPixels(input, comparison, expected.getInt("width"),
                expected.getInt("height"), area)
            check((changed == 0) == result.identityControls)
            if (name == "portrait") {
                check(report.getString("exposure_limit_method") == "facial_rgb")
                check(clipped == 213)
            }
            File(fixture, "picker-result.json").writeText(report
                .put("changed_pixels", changed).put("newly_clipped_pixels", clipped).toString(2))
        }
    }

    @Test fun checksReportedOverbrightRun() = runBlocking {
        val runId = InstrumentationRegistry.getArguments().getString("wb314OverbrightRun")
        assumeTrue(runId != null)
        check(BuildConfig.WB314_PICKER_FIXES && requireNotNull(runId).matches(Regex("[a-f0-9-]{36}")))
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val baseline = File(context.noBackupFilesDir, "runs/$runId")
        val previous = JSONObject(File(baseline, "report.json").readText())
        check(previous.getString("exposure_limit_method") == "facial_luminance")
        val source = File(baseline, "photo_used.png")
        val glasses = GlassesChoice.valueOf(previous.getString("glasses_choice").uppercase(java.util.Locale.ROOT))
        val repository = ImageRepository(context)
        val result = repository.runCorrection(Uri.fromFile(source), glasses)
        val reportFile = File(requireNotNull(result.report.path))
        val report = JSONObject(reportFile.readText())
        check(result.success) { report.toString() }
        check(report.getJSONArray("controls").toString() == previous.getJSONArray("controls").toString())
        check(report.getString("exposure_limit_method") == "facial_rgb")
        check(report.getJSONArray("effective_controls").getDouble(1) <
            previous.getJSONArray("effective_controls").getDouble(1))
        val priorHashes = previous.getJSONObject("output_sha256")
        val currentHashes = report.getJSONObject("output_sha256")
        for (file in listOf("photo_used.png", "skin_mask.png")) {
            check(currentHashes.getString(file) == priorHashes.getString(file)) { "$file differs" }
        }
        val mask = checkNotNull(BitmapFactory.decodeFile(File(baseline, "skin_mask.png").path))
        val pixels = IntArray(256 * 256)
        try {
            check(mask.width == 256 && mask.height == 256)
            mask.getPixels(pixels, 0, 256, 0, 0, 256, 256)
        } finally {
            mask.recycle()
        }
        val area = BooleanArray(pixels.size) { pixels[it] == -1 }
        val width = previous.getInt("source_width")
        val height = previous.getInt("source_height")
        val (_, oldClipped) = comparePickerPixels(source, File(baseline, "experimental_correction.png"), width, height, area)
        val exported = File(reportFile.parentFile, "export.png")
        repository.export(requireNotNull(result.corrected), Uri.fromFile(exported))
        val (changed, clipped) = comparePickerPixels(source, exported, width, height, area)
        File(context.filesDir, "wb314_overbright_result.json").writeText(report
            .put("previous_newly_clipped_pixels", oldClipped)
            .put("newly_clipped_pixels", clipped).put("changed_pixels", changed).toString(2))
        check(clipped < oldClipped)
    }

    private fun comparePickerPixels(input: File, output: File, width: Int, height: Int,
                                    area: BooleanArray): Pair<Int, Int> {
        val before = checkNotNull(BitmapFactory.decodeFile(input.path))
        val after = checkNotNull(BitmapFactory.decodeFile(output.path))
        try {
            check(before.width == width && before.height == height)
            check(after.width == width && after.height == height)
            val original = IntArray(width)
            val exported = IntArray(width)
            var changed = 0
            var clipped = 0
            for (y in 0 until height) {
                before.getPixels(original, 0, width, 0, y, width, 1)
                after.getPixels(exported, 0, width, 0, y, width, 1)
                for (x in original.indices) {
                    if (original[x] == exported[x]) continue
                    val index = (y * 256 / height) * 256 + x * 256 / width
                    check(area[index]) { "Changed pixel outside saved support at ($x, $y)" }
                    changed++
                    if (!hasFullChannel(original[x]) && hasFullChannel(exported[x])) clipped++
                }
            }
            return changed to clipped
        } finally {
            before.recycle()
            after.recycle()
        }
    }

    private fun readReferenceSupport(reference: File): BooleanArray {
        val size = 256 * 256
        return DataInputStream(reference.inputStream().buffered()).use { data ->
            data.readFully(ByteArray(size))
            val area = BooleanArray(size) { data.readDouble() > 0.0 }
            for (i in area.indices) {
                if (data.readBoolean()) area[i] = false
            }
            check(data.read() == -1)
            area
        }
    }

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
