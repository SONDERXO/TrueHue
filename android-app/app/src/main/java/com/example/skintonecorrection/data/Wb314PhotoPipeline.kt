package com.example.skintonecorrection.data

import android.content.Context
import android.graphics.Bitmap
import android.graphics.Matrix
import com.example.skintonecorrection.BuildConfig
import org.json.JSONArray
import org.json.JSONObject
import org.opencv.android.OpenCVLoader
import java.io.File

/** Picker path for the pinned, locally provisioned WB314 research release. */
internal class Wb314PhotoPipeline(private val context: Context) {
    companion object {
        const val MODEL_SHA = "7e451825f36242145015723ea0923e291bf1d4513d177a6f07258b56ceaf794f"
        private const val MANIFEST_SHA = "b1146aff3c5a190b9e495c62caef44e573d28674cb5050c479051314593b8de6"
        private const val FACEOCC_SHA = "706b236065be76c0d68a67d5497a53e153debc43894aae0ce16f0fb22eebc936"
    }

    private data class Models(val predictor: Wb314ResearchPipeline, val generator: Wb314ResearchMasks,
                              val brightness: Wb314LearnedExposure?)

    private val models by lazy {
        val folder = File(context.filesDir, "wb314_models")
        val required = listOf("manifest.json", "model.json", "mapping.json", "wb_srgb.bin",
            "yunet.onnx", "parser.onnx", "faceocc.onnx", "template.bin")
        require(required.all { File(folder, it).isFile }) { "WB314 research assets are missing on this device." }
        check(OpenCVLoader.initLocal()) { "The local image engine could not start." }
        val landmarker = context.assets.open(OnDevicePipeline.ASSETS + "face_landmarker.task").use { it.readBytes() }
        val brightness = BuildConfig.WB314_PHONE_BRIGHTNESS_FIT_SHA.takeIf { it.isNotEmpty() }?.let {
            Wb314LearnedExposure.load(File(context.filesDir, "wb314_phone_brightness.json"), it)
        }
        Models(Wb314ResearchPipeline.load(folder, MANIFEST_SHA),
            Wb314ResearchMasks(context, folder, FACEOCC_SHA, landmarker), brightness)
    }

    fun run(upright: Bitmap, glasses: GlassesChoice, report: JSONObject): PipelineImages {
        report.put("model_sha256", MODEL_SHA).put("glasses_choice", glasses.name.lowercase())
            .put("failed_stage", "wb314_assets")
        val available = models
        report.put("failed_stage", "wb314_mask_and_correction")
        val pickerFixes = BuildConfig.WB314_PICKER_FIXES
        val tonePositiveExposure = BuildConfig.WB314_SOFT_EDGE && !BuildConfig.WB314_JAW_REPAIR
        val faceAttempts = if (BuildConfig.WB314_HIGHLIGHT_TEST) JSONArray().also {
            report.put("face_analysis_attempts", it)
        } else null
        val decisionTrace = if (BuildConfig.WB314_DECISION_TRACE) JSONObject().also {
            report.put("decision_trace", it)
        } else null
        fun correct(bitmap: Bitmap, attempts: JSONArray?) = available.predictor.correct(bitmap, available.generator, glasses,
            previewWidespreadExposure = pickerFixes, previewMaskBoundaryProtection = pickerFixes,
            verifyLuminanceRgb = pickerFixes, repairSkinEdges = BuildConfig.WB314_EDGE_REPAIR,
            softenEdge = BuildConfig.WB314_SOFT_EDGE, repairJaw = BuildConfig.WB314_JAW_REPAIR,
            tonePositiveExposure = tonePositiveExposure, guardPhonePortraits = tonePositiveExposure,
            guardLocalHighlights = BuildConfig.WB314_HIGHLIGHT_TEST, faceAttempts = attempts,
            allowDiffuseBacklight = BuildConfig.WB314_DIFFUSE_BACKLIGHT_TEST,
            allowWarmCast = BuildConfig.WB314_WARM_CAST_TEST,
            allowCombined = BuildConfig.WB314_COMBINED_TEST, decisionTrace = decisionTrace,
            allowShadowLift = BuildConfig.WB314_SHADOW_LIFT_TEST,
            brightColourOnly = BuildConfig.WB314_BRIGHT_COLOUR_TEST)
        var analysisBitmap = upright
        var turn = 0
        val auto = try {
            correct(upright, faceAttempts)
        } catch (error: PhotoProcessingException) {
            val missingBoth = faceAttempts?.length() == 2 && (0..1).all { index ->
                faceAttempts.optJSONObject(index)?.optString("reason") == "Expected one face, found 0"
            }
            if (!BuildConfig.WB314_QUARTER_TURN_TEST || upright.width <= upright.height || !missingBoth) throw error
            turn = available.generator.recoveryQuarterTurn(upright) ?: throw error
            report.put("orientation_retry_degrees", turn)
            val rotatedAttempts = JSONArray()
            report.put("orientation_retry_attempts", rotatedAttempts)
            analysisBitmap = rotate(upright, turn)
            try {
                correct(analysisBitmap, rotatedAttempts)
            } catch (failure: Throwable) {
                analysisBitmap.recycle()
                throw failure
            }
        }
        var corrected = auto.correction.bitmap
        var mask: Bitmap? = null
        try {
            val side = FaceOccGeometry.SIDE
            val correction = auto.correction
            val brightness = available.brightness
            val edge = auto.masks.softEdge
            var addedPixels = 0
            val existingDarkLift = correction.lowLightLift || correction.shadowLiftPixels > 0
            val strongerDarkFaces = BuildConfig.WB314_DARK_FACE_STRENGTH_TEST
            if (brightness != null && edge != null && (!existingDarkLift || strongerDarkFaces) &&
                !correction.warmCastApplied &&
                correction.appliedControls[0] == 1.0 && correction.appliedControls[1] >= 1.0 &&
                correction.highlightCheck != "kept_original") {
                val stops = brightness.estimate(
                    analysisBitmap, corrected, auto.masks.alpha, existingDarkLift, strongerDarkFaces
                )
                report.put("learned_brightness_stops", stops)
                if (stops > 0.0) {
                    val support = Wb314RenderSupport(corrected.width, corrected.height, auto.masks.alpha,
                        auto.masks.protected, researchPrecision = pickerFixes)
                    addedPixels = brightness.apply(analysisBitmap, corrected, support, edge, stops)
                }
            }
            var identity = correction.appliedControls.all { it == 1.0 } &&
                correction.shadowLiftPixels == 0 && addedPixels == 0
            var restoreOriginal = false
            if (BuildConfig.WB314_DEFAULT_CORRECTION_TEST) {
                val proposedDefault = identity && brightness != null && edge != null
                if (proposedDefault) {
                    val support = Wb314RenderSupport(corrected.width, corrected.height, auto.masks.alpha,
                        auto.masks.protected, researchPrecision = pickerFixes)
                    checkNotNull(brightness).apply(analysisBitmap, corrected, support, checkNotNull(edge),
                        Wb314CandidateReview.defaultStops)
                }
                val seam = auto.masks.jawSeam
                val jawTaperPixels = if (seam != null && (!identity || proposedDefault)) {
                    val support = Wb314RenderSupport(corrected.width, corrected.height, auto.masks.alpha,
                        auto.masks.protected, researchPrecision = pickerFixes)
                    seam.apply(analysisBitmap, corrected, support)
                } else 0
                val review = Wb314CandidateReview.sample(analysisBitmap, corrected, auto.masks.alpha)
                val rejection = if (identity && !proposedDefault) "no_safe_proposal"
                    else review.rejection(proposedDefault)
                restoreOriginal = rejection != null
                identity = restoreOriginal
                report.put("candidate_mode", if (proposedDefault) "default_exposure" else "model")
                    .put("candidate_review", rejection ?: "accepted")
                    .put("candidate_review_face_samples", review.face)
                    .put("candidate_review_changed_samples", review.changed)
                    .put("candidate_review_new_clipping_samples", review.newClipping)
                if (BuildConfig.WB314_JAW_SEAM_TEST) {
                    report.put("jaw_seam_seed_pixels", seam?.seedCount ?: 0)
                        .put("jaw_seam_tapered_pixels", if (restoreOriginal) 0 else jawTaperPixels)
                }
                if (proposedDefault && !restoreOriginal) {
                    report.put("default_exposure_stops", Wb314CandidateReview.defaultStops)
                }
                if (restoreOriginal) {
                    corrected.recycle()
                    corrected = upright
                }
            }
            if (brightness != null) report.put("learned_brightness_pixels", if (restoreOriginal) 0 else addedPixels)
            val preview = IntArray(side * side) { if (auto.masks.alpha[it] > 0.0) -1 else 0xff000000.toInt() }
            mask = Bitmap.createBitmap(preview, side, side, Bitmap.Config.ARGB_8888)
            if (turn != 0) {
                val restoredMask = rotate(mask, -turn)
                mask.recycle()
                mask = restoredMask
                analysisBitmap.recycle()
                if (!restoreOriginal) {
                    val restored = rotate(corrected, -turn)
                    corrected.recycle()
                    corrected = restored
                    preserveOutsideRotatedMask(upright, corrected, mask)
                }
            }
            val controls = auto.correction.controls
            report.put("leaf", auto.correction.leaf).put("controls", JSONArray(controls.toList()))
                .put("picker_fixes", pickerFixes)
                .put("edge_repair", BuildConfig.WB314_EDGE_REPAIR)
                .put("soft_edge", BuildConfig.WB314_SOFT_EDGE)
                .put("positive_exposure_toned", tonePositiveExposure)
                .put("low_light_lift", auto.correction.lowLightLift && !restoreOriginal)
                .put("jaw_repair", BuildConfig.WB314_JAW_REPAIR)
                .put("edge_repair_added_pixels", auto.masks.repairedApplication?.addedPixels ?: 0)
                .put("identity_controls", identity)
                .put("analysis_dimensions", JSONArray(listOf(side, side)))
                .put("face_analysis_side", auto.visionSide)
                .put("output_dimensions", JSONArray(listOf(corrected.width, corrected.height)))
                .put("protected_pixels_analysis", auto.masks.protected.count { it })
                .put("status", "experimental_success").remove("failed_stage")
            auto.correction.highlightCheck?.let { report.put("highlight_check", it) }
            if (BuildConfig.WB314_SHADOW_LIFT_TEST) {
                report.put("shadow_lift_pixels", if (restoreOriginal) 0 else auto.correction.shadowLiftPixels)
            }
            if (BuildConfig.WB314_WARM_CAST_TEST) {
                report.put("warm_cast_applied", auto.correction.warmCastApplied && !restoreOriginal)
                    .put("warm_cast_protected_highlight_pixels", auto.correction.warmCastProtectedHighlights)
                auto.correction.warmCastScore?.let { report.put("warm_cast_score", it) }
            }
            auto.correction.exposurePreview?.let { decision ->
                val effective = if (restoreOriginal) List(controls.size) { 1.0 }
                    else auto.correction.appliedControls.toList()
                report.put("effective_controls", JSONArray(effective))
                    .put("highlight_limited_gain", decision.effectiveControls[1])
                    .put("exposure_limit_method", decision.method)
                    .put("eligible_face_pixels", decision.eligiblePixels)
                    .put("raw_exposure_clipped_face_pixels", decision.exposureClippedPixels)
            }
            return PipelineImages(upright, mask, corrected)
        } catch (error: Throwable) {
            mask?.recycle()
            if (corrected !== upright) corrected.recycle()
            throw error
        } finally {
            if (analysisBitmap !== upright && !analysisBitmap.isRecycled) analysisBitmap.recycle()
        }
    }

    private fun rotate(bitmap: Bitmap, degrees: Int): Bitmap =
        Bitmap.createBitmap(bitmap, 0, 0, bitmap.width, bitmap.height,
            Matrix().apply { postRotate(degrees.toFloat()) }, false)

    private fun preserveOutsideRotatedMask(original: Bitmap, corrected: Bitmap, mask: Bitmap) {
        // Native pixels at fractional analysis boundaries can map differently after a turn.
        // Reapply the displayed mask in the restored frame as an additional preservation check.
        val side = mask.width
        val support = IntArray(side * side)
        mask.getPixels(support, 0, side, 0, 0, side, side)
        val before = IntArray(original.width)
        val after = IntArray(original.width)
        val columns = IntArray(original.width) { x -> (x.toLong() * side / original.width).toInt() }
        for (y in 0 until original.height) {
            original.getPixels(before, 0, before.size, 0, y, before.size, 1)
            corrected.getPixels(after, 0, after.size, 0, y, after.size, 1)
            val row = (y.toLong() * side / original.height).toInt() * side
            for (x in after.indices) {
                if (support[row + columns[x]] != -1) after[x] = before[x]
            }
            corrected.setPixels(after, 0, after.size, 0, y, after.size, 1)
        }
    }
}
