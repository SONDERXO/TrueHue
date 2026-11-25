package com.example.skintonecorrection.data

import android.graphics.Bitmap
import com.example.skintonecorrection.data.Wb314HighlightGuard.newlyClips
import com.example.skintonecorrection.ml.PortableRegressionTree
import com.example.skintonecorrection.ml.PortableTreeAsset
import com.example.skintonecorrection.ml.Wb314Features
import com.example.skintonecorrection.ml.Wb314ImageFeatures.DEFAULT_MINIMUM_MEASUREMENT_PIXELS
import com.example.skintonecorrection.ml.Wb314PixelRenderer
import com.example.skintonecorrection.ml.Wb314WhiteBalance
import org.json.JSONObject
import org.json.JSONArray
import org.opencv.android.Utils
import org.opencv.core.Mat
import org.opencv.core.Size
import org.opencv.imgproc.Imgproc
import java.io.DataInputStream
import java.io.File
import java.security.DigestInputStream
import java.security.MessageDigest
import kotlin.math.pow

/** WB314 feature extraction and rendering with masks from the same normalized input. */
internal class Wb314ResearchPipeline private constructor(
    private val tree: PortableRegressionTree,
    private val whiteBalance: Wb314WhiteBalance,
    private val itaKnots: DoubleArray,
    private val mstKnots: DoubleArray
) {
    data class Result(val bitmap: Bitmap, val features: DoubleArray, val controls: DoubleArray, val leaf: Int,
                      val exposurePreview: Wb314ExposureDecision? = null,
                      val appliedControls: DoubleArray = exposurePreview?.effectiveControls ?: controls,
                      val lowLightLift: Boolean = false, val highlightCheck: String? = null,
                      val warmCastScore: Double? = null, val warmCastApplied: Boolean = false,
                      val warmCastProtectedHighlights: Int = 0, val shadowLiftPixels: Int = 0)
    data class AutoResult(val correction: Result, val masks: ResearchMaskRules.Result, val visionSide: Int)

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
                tonePositiveExposure: Boolean = false, guardPhonePortraits: Boolean = false,
                guardLocalHighlights: Boolean = false, faceAttempts: JSONArray? = null,
                allowDiffuseBacklight: Boolean = false, allowWarmCast: Boolean = false,
                allowCombined: Boolean = false, decisionTrace: JSONObject? = null,
                allowShadowLift: Boolean = false): AutoResult =
        withNormalizedRgb(original) { rgb ->
            val bgr = Mat()
            val analysis = try {
                Imgproc.cvtColor(rgb, bgr, Imgproc.COLOR_RGB2BGR)
                generator.generate(bgr, glasses, previewMaskBoundaryProtection, repairSkinEdges, softenEdge,
                    repairJaw, originalForRetry = original.takeIf { guardPhonePortraits }, attempts = faceAttempts)
            } finally {
                bgr.release()
            }
            val masks = analysis.masks
            val correction = correctNormalized(original, rgb, rgbBytes(rgb), masks.measurement,
                masks.alpha, masks.protected, previewWidespreadExposure, verifyLuminanceRgb,
                masks.repairedApplication, masks.softEdge, tonePositiveExposure, guardPhonePortraits,
                guardLocalHighlights, minimumMeasurement = analysis.minimumMeasurement,
                allowDiffuseBacklight = allowDiffuseBacklight, allowWarmCast = allowWarmCast,
                allowCombined = allowCombined, decisionTrace = decisionTrace, allowShadowLift = allowShadowLift)
            val repair = masks.repairedApplication
            val applied = if (repair == null) masks else masks.copy(alpha = repair.alpha, protected = repair.protected)
            AutoResult(correction, applied, analysis.visionSide)
        }

    private fun correctNormalized(original: Bitmap, rgb: Mat, bytes: ByteArray, measurement: ByteArray,
                                  alpha: DoubleArray, protected: BooleanArray,
                                  previewWidespreadExposure: Boolean, verifyLuminanceRgb: Boolean = false,
                                  repair: ResearchMaskRules.ApplicationRepair? = null,
                                  softEdge: Wb314SoftEdge? = null, tonePositiveExposure: Boolean = false,
                                  guardPhonePortraits: Boolean = false, guardLocalHighlights: Boolean = false,
                                  minimumMeasurement: Int = DEFAULT_MINIMUM_MEASUREMENT_PIXELS,
                                  allowDiffuseBacklight: Boolean = false, allowWarmCast: Boolean = false,
                                  allowCombined: Boolean = false, decisionTrace: JSONObject? = null,
                                  allowShadowLift: Boolean = false): Result {
        require(measurement.size == PIXELS && alpha.size == PIXELS && protected.size == PIXELS)
        require(alpha.indices.all { alpha[it] in 0.0..1.0 && (!protected[it] || alpha[it] == 0.0) })
        require(alpha.any { it > 0.0 })
        val features = Wb314Features.extract(rgb, measurement, itaKnots, mstKnots, whiteBalance.extract(bytes),
            minimumMeasurement)
        val controls = tree.predict(features)
        val support = Wb314RenderSupport(original.width, original.height, alpha, protected,
            researchPrecision = previewWidespreadExposure)
        val preview = if (previewWidespreadExposure) {
            Wb314WidespreadExposure.select(original, support, bytes, measurement, alpha, protected, controls,
                verifyLuminanceRgb, guardPhonePortraits)
        } else null
        // Evaluate exposure on the existing mask so a coverage repair cannot change the controls.
        val renderSupport = if (repair == null) support else Wb314RenderSupport(
            original.width, original.height, repair.alpha, repair.protected, researchPrecision = previewWidespreadExposure)
        val limited = preview?.effectiveControls ?: controls
        val applied = if (tonePositiveExposure) limited.copyOf().apply {
            this[1] = Wb314ExposureToning.limit(controls[1], this[1])
        } else limited
        var exposureEvidence: Wb314LowLight.Evidence? = null
        val recordExposure: ((Wb314LowLight.Evidence) -> Unit)? = if (allowShadowLift || decisionTrace != null) {
            { evidence ->
                exposureEvidence = evidence
                decisionTrace?.put("backlight_check", evidence.reason)
                    ?.put("face_pixels", evidence.facePixels)?.put("scene_pixels", evidence.scenePixels)
                    ?.put("scene_at_least_224", evidence.nearWhitePixels)
                    ?.put("scene_at_least_192", evidence.diffuseBrightPixels)
                    ?.put("face_luma_25", evidence.faceLuma25)?.put("face_luma_75", evidence.faceLuma75)
                    ?.put("scene_luma_95", evidence.sceneLuma95)
            }
        } else null
        val proposedGain = if (guardPhonePortraits && controls.all { it == 1.0 }) {
            Wb314LowLight.proposedGain(bytes, measurement, alpha, allowDiffuseBacklight, recordExposure)
        } else {
            decisionTrace?.put("backlight_check", "tree_proposed_edit")
            null
        }
        val lowLightGain = when {
            proposedGain == null -> null
            hasLowLightHeadroom(original, renderSupport, proposedGain) -> proposedGain
            proposedGain > Wb314LowLight.diffuseBaseGain &&
                hasLowLightHeadroom(original, renderSupport, Wb314LowLight.diffuseBaseGain) ->
                Wb314LowLight.diffuseBaseGain
            proposedGain > Wb314LowLight.gain && hasLowLightHeadroom(original, renderSupport, Wb314LowLight.gain) ->
                Wb314LowLight.gain
            else -> null
        }
        decisionTrace?.put("backlight_proposed_gain", proposedGain)
            ?.put("backlight_headroom_gain", lowLightGain)
        var finalControls = if (lowLightGain == null) applied else applied.copyOf().apply { this[1] = lowLightGain }
        // Preserve existing edits and let the same highlight guard check the new proposal.
        var warmCast = if (allowWarmCast && guardLocalHighlights && finalControls.all { it == 1.0 }) {
            Wb314WarmCast.estimate(bytes, alpha)
        } else null
        warmCast?.controls?.let { finalControls = it }
        var protectedWarmHighlights = 0
        val preserveWarmHighlights: (() -> Unit)? = if (warmCast?.controls != null) {
            { protectedWarmHighlights++ }
        } else null
        fun renderProposal(checkHighlights: Boolean) = render(original, renderSupport, finalControls,
            repair?.softEdge ?: softEdge, if (repair?.softEdge == null) null else support, softEdge,
            checkHighlights, preserveWarmHighlights)
        val checkHighlights = guardLocalHighlights && finalControls.any { it != 1.0 }
        var highlightCheck = if (checkHighlights) "passed" else null
        var output = renderProposal(checkHighlights)
        if (output == null) {
            finalControls = Wb314HighlightGuard.backedOff(finalControls)
            highlightCheck = "reduced_edit"
            output = renderProposal(true)
        }
        if (output == null) {
            finalControls = DoubleArray(controls.size) { 1.0 }
            highlightCheck = "kept_original"
            output = checkNotNull(renderProposal(false))
        }
        var warmCastApplied = warmCast?.controls != null && highlightCheck != "kept_original"
        if (allowCombined && checkHighlights && warmCast == null && finalControls[1] != 1.0 &&
            finalControls[2] == 1.0 && finalControls[3] == 1.0 && finalControls[4] == 1.0) {
            // The base edit is already guarded. Reuse its bitmap and retain it at unsafe pixels.
            warmCast = Wb314WarmCast.estimate(bytes, alpha)
            warmCast?.controls?.let { cooling ->
                val combined = finalControls.copyOf().apply {
                    this[1] *= cooling[1].pow(this[0])
                    this[2] = cooling[2]
                    this[3] = cooling[3]
                }
                output = checkNotNull(render(original, renderSupport, combined, softEdge, null, null,
                    checkHighlights = true, onHighlightPreserved = { protectedWarmHighlights++ },
                    acceptedOutput = checkNotNull(output)))
                finalControls = combined
                warmCastApplied = true
            }
        }
        val corrected = checkNotNull(output)
        val shadow = if (allowShadowLift && lowLightGain == null) {
            Wb314ShadowLift.select(exposureEvidence?.faceLuma25, exposureEvidence?.faceLuma75,
                backlightBlockedByHeadroom = proposedGain != null)
        } else null
        val shadowPixels = if (shadow == null) 0 else applyShadowLift(original, corrected, renderSupport, softEdge, shadow)
        return Result(corrected, features, controls, tree.leafId(features), preview, finalControls,
            lowLightGain != null && highlightCheck != "kept_original", highlightCheck,
            warmCast?.score, warmCastApplied, protectedWarmHighlights, shadowPixels)
    }

    private fun applyShadowLift(original: Bitmap, output: Bitmap, support: Wb314RenderSupport,
                                softEdge: Wb314SoftEdge?, lift: Wb314ShadowLift): Int {
        val before = IntArray(original.width)
        val corrected = IntArray(original.width)
        var changed = 0
        try {
            for (y in 0 until original.height) {
                original.getPixels(before, 0, before.size, 0, y, before.size, 1)
                output.getPixels(corrected, 0, corrected.size, 0, y, corrected.size, 1)
                for (x in before.indices) {
                    val coverage = support.alphaAt(x, y)
                    if (coverage <= 0.0) continue
                    val base = corrected[x]
                    val proposed = lift.propose(before[x], base, coverage)
                    if (base == proposed) continue
                    val blended = if (softEdge == null) proposed
                        else softEdge.blend(base, proposed, support.interpolate(softEdge.distance, x, y))
                    corrected[x] = lift.keepSafe(before[x], base, blended)
                    if (corrected[x] != base) changed++
                }
                output.setPixels(corrected, 0, corrected.size, 0, y, corrected.size, 1)
            }
        } catch (error: Throwable) {
            output.recycle()
            throw error
        }
        return changed
    }
    private fun hasLowLightHeadroom(original: Bitmap, support: Wb314RenderSupport, gain: Double): Boolean {
        val renderer = Wb314PixelRenderer(1.0, gain, 1.0, 1.0, 1.0)
        // For the stronger proposal, check highlights before the soft edge can attenuate the edit.
        val stronger = gain > Wb314LowLight.gain
        val row = IntArray(original.width)
        for (y in 0 until original.height) {
            original.getPixels(row, 0, row.size, 0, y, row.size, 1)
            for (x in row.indices) {
                val coverage = support.alphaAt(x, y)
                if (coverage == 0.0) continue
                val corrected = renderer.render(row[x], coverage, false)
                val losesDetail = if (stronger) Wb314HighlightGuard.losesHighlight(row[x], corrected)
                    else newlyClips(row[x], corrected)
                if (losesDetail) return false
            }
        }
        return true
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
                       referenceFade: Wb314SoftEdge?, checkHighlights: Boolean,
                       onHighlightPreserved: (() -> Unit)? = null, acceptedOutput: Bitmap? = null): Bitmap? {
        val width = original.width
        val height = original.height
        val renderer = Wb314PixelRenderer(controls[0], controls[1], controls[2], controls[3], controls[4])
        val result = acceptedOutput ?: Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
        try {
            val row = IntArray(width)
            val accepted = acceptedOutput?.let { IntArray(width) }
            for (y in 0 until height) {
                original.getPixels(row, 0, width, 0, y, width, 1)
                if (accepted != null) result.getPixels(accepted, 0, width, 0, y, width, 1)
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
                        if (checkHighlights && (Wb314HighlightGuard.losesHighlight(input, row[x]) ||
                                (accepted != null && Wb314HighlightGuard.losesHighlight(accepted[x], row[x])))) {
                            if (onHighlightPreserved == null) {
                                result.recycle()
                                return null
                            }
                            row[x] = accepted?.get(x) ?: input
                            onHighlightPreserved()
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

}
