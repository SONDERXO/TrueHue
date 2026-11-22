package com.example.skintonecorrection.data

import android.graphics.Bitmap
import com.example.skintonecorrection.ml.PortableRegressionTree
import com.example.skintonecorrection.ml.PortableTreeAsset
import com.example.skintonecorrection.ml.Wb314Features
import com.example.skintonecorrection.ml.Wb314PixelRenderer
import com.example.skintonecorrection.ml.Wb314WhiteBalance
import org.json.JSONObject
import org.opencv.android.Utils
import org.opencv.core.Mat
import org.opencv.core.Size
import org.opencv.imgproc.Imgproc
import java.io.DataInputStream
import java.io.File
import java.security.DigestInputStream
import java.security.MessageDigest

/** WB314 feature extraction and rendering with masks from the same normalized input. */
internal class Wb314ResearchPipeline private constructor(
    private val tree: PortableRegressionTree,
    private val whiteBalance: Wb314WhiteBalance,
    private val itaKnots: DoubleArray,
    private val mstKnots: DoubleArray
) {
    data class Result(val bitmap: Bitmap, val features: DoubleArray, val controls: DoubleArray, val leaf: Int,
                      val exposurePreview: Wb314ExposureDecision? = null,
                      val appliedControls: DoubleArray = exposurePreview?.effectiveControls ?: controls)
    data class AutoResult(val correction: Result, val masks: ResearchMaskRules.Result)

    companion object {
        private const val SIDE = 256
        private const val PIXELS = SIDE * SIDE

        /** The manifest digest must come from the trusted local release, outside this folder. */
        fun load(folder: File, manifestSha: String): Wb314ResearchPipeline {
            val manifest = JSONObject(checkedBytes(File(folder, "manifest.json"), manifestSha, 4096).toString(Charsets.UTF_8))
            require(manifest.getString("schema") == "truehue_wb314_android_research_v1")
            val modelSha = manifest.getString("tree_sha256")
            val tree = PortableTreeAsset.parseWb314(checkedBytes(File(folder, "model.json"), modelSha, 65536), modelSha)
            val mapping = JSONObject(checkedBytes(File(folder, "mapping.json"), manifest.getString("mapping_sha256"),
                65536).toString(Charsets.UTF_8))
            require(mapping.getString("schema_version") == "truehue_shared_core_development_mst_v1")
            require(mapping.getString("status") == "development_unvalidated_transfer")
            fun knots(name: String) = mapping.getJSONArray(name).let { a -> DoubleArray(a.length()) { a.getDouble(it) } }
            val bank = File(folder, "wb_srgb.bin")
            val digest = MessageDigest.getInstance("SHA-256")
            val wb = DataInputStream(DigestInputStream(bank.inputStream().buffered(), digest)).use { input ->
                val rows = input.readInt()
                require(rows == 62_535) { "Unexpected WB_sRGB bank dimensions" }
                fun floats(count: Int) = FloatArray(count) { input.readFloat() }
                val offset = floats(10_800)
                val projection = floats(10_800 * 55)
                val encoded = floats(rows * 55)
                val coefficients = floats(rows * 33)
                val norms = floats(rows)
                require(input.read() == -1 && hex(digest.digest()) == manifest.getString("bank_sha256")) {
                    "WB_sRGB bank checksum mismatch"
                }
                Wb314WhiteBalance(offset, projection, encoded, coefficients, norms)
            }
            return Wb314ResearchPipeline(tree, wb, knots("ita_knots"), knots("mst_score_knots"))
        }

        private fun checkedBytes(file: File, expected: String, maxBytes: Long): ByteArray {
            require(file.length() in 1..maxBytes) { "Unexpected research asset size" }
            val bytes = file.readBytes()
            require(hex(MessageDigest.getInstance("SHA-256").digest(bytes)) == expected) { "Research asset checksum mismatch" }
            return bytes
        }

        private fun hex(bytes: ByteArray) = bytes.joinToString("") { "%02x".format(it) }
    }

    fun correct(
        original: Bitmap, measurement: ByteArray, alpha: DoubleArray, protected: BooleanArray,
        normalizedRgbSha: String, previewWidespreadExposure: Boolean = false
    ): Result = withNormalizedRgb(original) { rgb ->
        val bytes = rgbBytes(rgb)
        val actual = hex(MessageDigest.getInstance("SHA-256").digest(bytes))
        require(actual == normalizedRgbSha) { "Masks belong to a different analysis image" }
        correctNormalized(original, rgb, bytes, measurement, alpha, protected, previewWidespreadExposure)
    }

    fun correct(original: Bitmap, generator: Wb314ResearchMasks, glasses: GlassesChoice,
                previewWidespreadExposure: Boolean = false,
                previewMaskBoundaryProtection: Boolean = false,
                verifyLuminanceRgb: Boolean = false, repairSkinEdges: Boolean = false,
                softenEdge: Boolean = false, repairJaw: Boolean = false,
                tonePositiveExposure: Boolean = false): AutoResult =
        withNormalizedRgb(original) { rgb ->
            val bgr = Mat()
            val masks = try {
                Imgproc.cvtColor(rgb, bgr, Imgproc.COLOR_RGB2BGR)
                generator.generate(bgr, glasses, previewMaskBoundaryProtection, repairSkinEdges, softenEdge, repairJaw).masks
            } finally {
                bgr.release()
            }
            val correction = correctNormalized(original, rgb, rgbBytes(rgb), masks.measurement,
                masks.alpha, masks.protected, previewWidespreadExposure, verifyLuminanceRgb,
                masks.repairedApplication, masks.softEdge, tonePositiveExposure)
            val repair = masks.repairedApplication
            val applied = if (repair == null) masks else masks.copy(alpha = repair.alpha, protected = repair.protected)
            AutoResult(correction, applied)
        }

    private fun correctNormalized(original: Bitmap, rgb: Mat, bytes: ByteArray, measurement: ByteArray,
                                  alpha: DoubleArray, protected: BooleanArray,
                                  previewWidespreadExposure: Boolean, verifyLuminanceRgb: Boolean = false,
                                  repair: ResearchMaskRules.ApplicationRepair? = null,
                                  softEdge: Wb314SoftEdge? = null, tonePositiveExposure: Boolean = false): Result {
        require(measurement.size == PIXELS && alpha.size == PIXELS && protected.size == PIXELS)
        require(alpha.indices.all { alpha[it] in 0.0..1.0 && (!protected[it] || alpha[it] == 0.0) })
        require(alpha.any { it > 0.0 })
        val features = Wb314Features.extract(rgb, measurement, itaKnots, mstKnots, whiteBalance.extract(bytes))
        val controls = tree.predict(features)
        val support = Wb314RenderSupport(original.width, original.height, alpha, protected,
            researchPrecision = previewWidespreadExposure)
        val preview = if (previewWidespreadExposure) {
            Wb314WidespreadExposure.select(original, support, bytes, measurement, alpha, protected, controls, verifyLuminanceRgb)
        } else null
        // Evaluate exposure on the existing mask so a coverage repair cannot change the controls.
        val renderSupport = if (repair == null) support else Wb314RenderSupport(
            original.width, original.height, repair.alpha, repair.protected, researchPrecision = previewWidespreadExposure)
        val limited = preview?.effectiveControls ?: controls
        val applied = if (tonePositiveExposure) limited.copyOf().apply {
            this[1] = Wb314ExposureToning.limit(controls[1], this[1])
        } else limited
        val output = render(original, renderSupport, applied,
            repair?.softEdge ?: softEdge, if (repair?.softEdge == null) null else support, softEdge)
        return Result(output, features, controls, tree.leafId(features), preview, applied)
    }

    private fun rgbBytes(rgb: Mat) = ByteArray(PIXELS * 3).also { check(rgb.get(0, 0, it) == it.size) }

    private fun <T> withNormalizedRgb(original: Bitmap, action: (Mat) -> T): T {
        val rgba = Mat()
        val resized = Mat()
        val rgb = Mat()
        try {
            Utils.bitmapToMat(original, rgba)
            Imgproc.resize(rgba, resized, Size(SIDE.toDouble(), SIDE.toDouble()), 0.0, 0.0, Imgproc.INTER_AREA)
            rgba.release()
            Imgproc.cvtColor(resized, rgb, Imgproc.COLOR_RGBA2RGB)
            return action(rgb)
        } finally {
            rgb.release()
            resized.release()
            rgba.release()
        }
    }

    private fun render(original: Bitmap, support: Wb314RenderSupport, controls: DoubleArray,
                       softEdge: Wb314SoftEdge?, referenceSupport: Wb314RenderSupport?,
                       referenceFade: Wb314SoftEdge?): Bitmap {
        val width = original.width
        val height = original.height
        val renderer = Wb314PixelRenderer(controls[0], controls[1], controls[2], controls[3], controls[4])
        val result = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
        try {
            val row = IntArray(width)
            for (y in 0 until height) {
                original.getPixels(row, 0, width, 0, y, width, 1)
                for (x in row.indices) {
                    val coverage = support.alphaAt(x, y)
                    if (coverage > 0) {
                        val input = row[x]
                        val corrected = renderer.render(input, coverage, false)
                        val blended = if (softEdge != null && corrected != input) {
                            softEdge.blend(input, corrected, support.interpolate(softEdge.distance, x, y))
                        } else corrected
                        row[x] = blended
                        // The repair may brighten additional skin. Preserve the prior result if this clips it.
                        if (referenceSupport != null && referenceFade != null && blended != input &&
                            newlyClips(input, blended)) {
                            val priorAlpha = referenceSupport.alphaAt(x, y)
                            val prior = renderer.render(input, priorAlpha, false)
                            val base = referenceFade.blend(input, prior,
                                referenceSupport.interpolate(referenceFade.distance, x, y))
                            if (newlyClips(base, blended)) row[x] = base
                        }
                    }
                }
                result.setPixels(row, 0, width, 0, y, width, 1)
            }
            return result
        } catch (error: Throwable) {
            result.recycle()
            throw error
        }
    }

    private fun newlyClips(before: Int, after: Int): Boolean =
        ((before ushr 16) and 255) < 255 && ((after ushr 16) and 255) == 255 ||
            ((before ushr 8) and 255) < 255 && ((after ushr 8) and 255) == 255 ||
            (before and 255) < 255 && (after and 255) == 255
}
