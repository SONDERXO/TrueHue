package com.example.skintonecorrection.data

import android.content.Context
import android.graphics.Bitmap
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

    private data class Models(val predictor: Wb314ResearchPipeline, val generator: Wb314ResearchMasks)

    private val models by lazy {
        val folder = File(context.filesDir, "wb314_models")
        val required = listOf("manifest.json", "model.json", "mapping.json", "wb_srgb.bin",
            "yunet.onnx", "parser.onnx", "faceocc.onnx", "template.bin")
        require(required.all { File(folder, it).isFile }) { "WB314 research assets are missing on this device." }
        check(OpenCVLoader.initLocal()) { "The local image engine could not start." }
        val landmarker = context.assets.open(OnDevicePipeline.ASSETS + "face_landmarker.task").use { it.readBytes() }
        Models(Wb314ResearchPipeline.load(folder, MANIFEST_SHA), Wb314ResearchMasks(context, folder, FACEOCC_SHA, landmarker))
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
        val auto = available.predictor.correct(upright, available.generator, glasses,
            previewWidespreadExposure = pickerFixes, previewMaskBoundaryProtection = pickerFixes,
            verifyLuminanceRgb = pickerFixes, repairSkinEdges = BuildConfig.WB314_EDGE_REPAIR,
            softenEdge = BuildConfig.WB314_SOFT_EDGE, repairJaw = BuildConfig.WB314_JAW_REPAIR,
            tonePositiveExposure = tonePositiveExposure, guardPhonePortraits = tonePositiveExposure,
            guardLocalHighlights = BuildConfig.WB314_HIGHLIGHT_TEST, faceAttempts = faceAttempts,
            allowDiffuseBacklight = BuildConfig.WB314_DIFFUSE_BACKLIGHT_TEST,
            allowWarmCast = BuildConfig.WB314_WARM_CAST_TEST,
            allowCombined = BuildConfig.WB314_COMBINED_TEST, decisionTrace = decisionTrace)
        val corrected = auto.correction.bitmap
        var mask: Bitmap? = null
        try {
            val side = FaceOccGeometry.SIDE
            val preview = IntArray(side * side) { if (auto.masks.alpha[it] > 0.0) -1 else 0xff000000.toInt() }
            mask = Bitmap.createBitmap(preview, side, side, Bitmap.Config.ARGB_8888)
            val controls = auto.correction.controls
            report.put("leaf", auto.correction.leaf).put("controls", JSONArray(controls.toList()))
                .put("picker_fixes", pickerFixes)
                .put("edge_repair", BuildConfig.WB314_EDGE_REPAIR)
                .put("soft_edge", BuildConfig.WB314_SOFT_EDGE)
                .put("positive_exposure_toned", tonePositiveExposure)
                .put("low_light_lift", auto.correction.lowLightLift)
                .put("jaw_repair", BuildConfig.WB314_JAW_REPAIR)
                .put("edge_repair_added_pixels", auto.masks.repairedApplication?.addedPixels ?: 0)
                .put("identity_controls", auto.correction.appliedControls.all { it == 1.0 })
                .put("analysis_dimensions", JSONArray(listOf(side, side)))
                .put("face_analysis_side", auto.visionSide)
                .put("output_dimensions", JSONArray(listOf(corrected.width, corrected.height)))
                .put("protected_pixels_analysis", auto.masks.protected.count { it })
                .put("status", "experimental_success").remove("failed_stage")
            auto.correction.highlightCheck?.let { report.put("highlight_check", it) }
            if (BuildConfig.WB314_WARM_CAST_TEST) {
                report.put("warm_cast_applied", auto.correction.warmCastApplied)
                    .put("warm_cast_protected_highlight_pixels", auto.correction.warmCastProtectedHighlights)
                auto.correction.warmCastScore?.let { report.put("warm_cast_score", it) }
            }
            auto.correction.exposurePreview?.let { decision ->
                report.put("effective_controls", JSONArray(auto.correction.appliedControls.toList()))
                    .put("highlight_limited_gain", decision.effectiveControls[1])
                    .put("exposure_limit_method", decision.method)
                    .put("eligible_face_pixels", decision.eligiblePixels)
                    .put("raw_exposure_clipped_face_pixels", decision.exposureClippedPixels)
            }
            return PipelineImages(upright, mask, corrected)
        } catch (error: Throwable) {
            mask?.recycle()
            corrected.recycle()
            throw error
        }
    }
}
