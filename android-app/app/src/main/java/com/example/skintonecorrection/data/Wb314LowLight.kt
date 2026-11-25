package com.example.skintonecorrection.data

import kotlin.math.pow
import kotlin.math.log2

/** A bounded exposure-only proposal for severe backlight when WB314 selected identity. */
internal object Wb314LowLight {
    val gain = 2.0.pow(3.0 / 8.0)
    private const val DIFFUSE_BASE_STOPS = 5.0 / 8.0
    val diffuseBaseGain = 2.0.pow(DIFFUSE_BASE_STOPS)

    data class Evidence(val reason: String, val facePixels: Int, val scenePixels: Int,
                        val nearWhitePixels: Int, val diffuseBrightPixels: Int,
                        val faceLuma25: Int?, val faceLuma75: Int?, val sceneLuma95: Int?)

    fun proposedGain(rgb: ByteArray, measurement: ByteArray, alpha: DoubleArray,
                     allowDiffuseBacklight: Boolean = false, record: ((Evidence) -> Unit)? = null): Double? {
        require(rgb.size == measurement.size * 3 && alpha.size == measurement.size)
        val face = IntArray(256)
        val scene = IntArray(256)
        var faceCount = 0
        var sceneCount = 0
        var brightCount = 0
        var diffuseBrightCount = 0
        for (i in measurement.indices) {
            val measured = measurement[i] != 0.toByte()
            if (!measured && alpha[i] > 0.0) continue
            val j = i * 3
            val level = (2126 * (rgb[j].toInt() and 255) + 7152 * (rgb[j + 1].toInt() and 255) +
                722 * (rgb[j + 2].toInt() and 255) + 5000) / 10_000
            if (measured) {
                face[level]++
                faceCount++
            } else {
                scene[level]++
                sceneCount++
                if (level >= 224) brightCount++
                if (level >= 192) diffuseBrightCount++
            }
        }
        fun decision(reason: String, proposal: Double? = null): Double? {
            if (record != null) {
                record(Evidence(reason, faceCount, sceneCount, brightCount, diffuseBrightCount,
                    if (faceCount == 0) null else percentile(face, faceCount, 25),
                    if (faceCount == 0) null else percentile(face, faceCount, 75),
                    if (sceneCount == 0) null else percentile(scene, sceneCount, 95)))
            }
            return proposal
        }
        if (faceCount == 0 || sceneCount == 0) return decision("missing_samples")
        val nearWhiteBackground = 16L * brightCount >= sceneCount
        if (!nearWhiteBackground && (!allowDiffuseBacklight || 4L * diffuseBrightCount < sceneCount)) {
            return decision("bright_background_coverage")
        }
        val faceUpper = linear(percentile(face, faceCount, 75))
        val sceneHighlight = linear(percentile(scene, sceneCount, 95))
        if (faceUpper <= 0 || 8.0 * faceUpper > sceneHighlight) return decision("face_to_scene_contrast")
        if (nearWhiteBackground) return decision("near_white_backlight", gain)
        val faceLower = linear(percentile(face, faceCount, 25))
        if (faceLower <= 0 || faceUpper < 2.0 * faceLower) return decision("facial_shadow_contrast")
        // Keep the verified lift for ordinary shadows. Give deeper shadows more lift, up to one stop.
        val extraStops = (log2(faceUpper / faceLower) - 2.0).coerceAtLeast(0.0) / 4.0
        return decision("diffuse_backlight", 2.0.pow((DIFFUSE_BASE_STOPS + extraStops).coerceAtMost(1.0)))
    }

    private fun percentile(histogram: IntArray, count: Int, percent: Int): Int {
        val rank = (count * percent + 99) / 100
        var seen = 0
        return histogram.indices.first { index ->
            seen += histogram[index]
            seen >= rank
        }
    }

    private fun linear(code: Int): Double {
        val x = code / 255.0
        return if (x <= 0.04045) x / 12.92 else ((x + 0.055) / 1.055).pow(2.4)
    }
}
