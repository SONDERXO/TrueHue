package com.example.skintonecorrection

import android.graphics.BitmapFactory
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.example.skintonecorrection.data.Wb314ResearchPipeline
import org.json.JSONArray
import org.json.JSONObject
import org.junit.Assert.assertTrue
import org.junit.Assume.assumeTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.opencv.android.OpenCVLoader
import java.io.DataInputStream
import java.io.File
import kotlin.math.abs

@RunWith(AndroidJUnit4::class)
class Wb314ExposurePreviewTest {
    @Test fun comparesTheOptInPreviewWithSavedResearchOutputs() {
        val instrumentation = InstrumentationRegistry.getInstrumentation()
        val args = InstrumentationRegistry.getArguments()
        assumeTrue(args.getString("wb314ExposureFixture") == "true")
        val root = instrumentation.targetContext.filesDir
        val manifest = requireNotNull(args.getString("wb314ManifestSha"))
        assertTrue(OpenCVLoader.initLocal())
        val pipeline = Wb314ResearchPipeline.load(File(root, "wb314_models"), manifest)
        val folder = File(root, "wb314_exposure_preview")
        val fixtures = JSONArray(File(folder, "cases.json").readText())
        val report = JSONArray()
        for (i in 0 until fixtures.length()) {
            val spec = fixtures.getJSONObject(i)
            val name = spec.getString("name")
            val row = JSONObject().put("case", name)
            try {
                verify(pipeline, folder, spec, row)
            } catch (error: Exception) {
                row.put("passed", false).put("failure", error.message ?: error.javaClass.simpleName)
            } finally {
                report.put(row)
                File(folder, "results.json").writeText(report.toString(2))
            }
        }
        assertTrue("See exposure preview results.json.",
            (0 until report.length()).all { report.getJSONObject(it).optBoolean("passed") })
    }

    private fun verify(pipeline: Wb314ResearchPipeline, folder: File, spec: JSONObject, row: JSONObject) {
        val name = spec.getString("name")
        val size = 256 * 256
        val measurement = ByteArray(size)
        val alpha = DoubleArray(size)
        val protected = BooleanArray(size)
        DataInputStream(File(folder, "$name.bin").inputStream().buffered()).use { data ->
            data.readFully(measurement)
            for (i in alpha.indices) alpha[i] = data.readDouble()
            for (i in protected.indices) protected[i] = data.readBoolean()
            check(data.read() == -1)
        }
        val original = checkNotNull(BitmapFactory.decodeFile(File(folder, "$name-input.png").path))
        try {
            val result = pipeline.correct(original, measurement, alpha, protected,
                spec.getString("normalized_rgb_sha256"), previewWidespreadExposure = true)
            try {
                val preview = requireNotNull(result.exposurePreview)
                val expected = checkNotNull(BitmapFactory.decodeFile(File(folder, "$name-expected.png").path))
                try {
                    check(original.width == result.bitmap.width && original.height == result.bitmap.height)
                    check(original.width == expected.width && original.height == expected.height)
                    val width = original.width
                    val referenceRow = IntArray(width)
                    val resultRow = IntArray(width)
                    val originalRow = IntArray(width)
                    var pixelDifferences = 0
                    var outsideDifferences = 0
                    var maxChannelDifference = 0
                    for (y in 0 until original.height) {
                        expected.getPixels(referenceRow, 0, width, 0, y, width, 1)
                        result.bitmap.getPixels(resultRow, 0, width, 0, y, width, 1)
                        original.getPixels(originalRow, 0, width, 0, y, width, 1)
                        for (x in 0 until width) {
                            val maskIndex = (y * 256 / original.height) * 256 + x * 256 / width
                            if ((protected[maskIndex] || alpha[maskIndex] == 0.0) && originalRow[x] != resultRow[x]) {
                                outsideDifferences++
                            }
                            if (referenceRow[x] != resultRow[x]) {
                                pixelDifferences++
                                for (shift in 0..16 step 8) {
                                    val target = (referenceRow[x] shr shift) and 255
                                    val actual = (resultRow[x] shr shift) and 255
                                    maxChannelDifference = maxOf(maxChannelDifference, abs(target - actual))
                                }
                            }
                        }
                    }
                    val raw = spec.getJSONArray("raw")
                    val effective = spec.getJSONArray("effective")
                    val rawDifference = result.controls.indices.maxOf { abs(result.controls[it] - raw.getDouble(it)) }
                    val effectiveDifference = preview.effectiveControls.indices.maxOf {
                        abs(preview.effectiveControls[it] - effective.getDouble(it))
                    }
                    val decisionMatches = preview.method == spec.getString("method")
                        && preview.eligiblePixels == spec.getInt("eligible")
                        && preview.exposureClippedPixels == spec.getInt("clipped")
                    row.put("method", preview.method).put("eligible", preview.eligiblePixels)
                        .put("clipped", preview.exposureClippedPixels).put("decision_matches", decisionMatches)
                        .put("raw_control_max_difference", rawDifference)
                        .put("effective_control_max_difference", effectiveDifference)
                        .put("pixel_differences", pixelDifferences).put("outside_differences", outsideDifferences)
                        .put("max_channel_difference", maxChannelDifference)
                        .put("passed", decisionMatches && rawDifference <= 1e-12 && effectiveDifference <= 1e-12
                            && pixelDifferences == 0 && outsideDifferences == 0)
                } finally {
                    expected.recycle()
                }
            } finally {
                result.bitmap.recycle()
            }
        } finally {
            original.recycle()
        }
    }
}
