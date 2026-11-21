package com.example.skintonecorrection.data

import android.graphics.Bitmap
import com.example.skintonecorrection.ml.Wb314PixelRenderer
import kotlin.math.pow

internal data class Wb314ExposureDecision(
    val effectiveControls: DoubleArray,
    val eligiblePixels: Int,
    val exposureClippedPixels: Int,
    val method: String
)

/** Research port of the fixed one-quarter exposure rule. */
internal object Wb314WidespreadExposure {
    fun select(
        original: Bitmap,
        support: Wb314RenderSupport,
        analysisRgb: ByteArray,
        measurement: ByteArray,
        alpha: DoubleArray,
        protected: BooleanArray,
        raw: DoubleArray,
        verifyLuminanceRgb: Boolean
    ): Wb314ExposureDecision {
        var eligible = 0
        var clipped = 0
        val neutral = raw.copyOf().apply { this[1] = 1.0 }
        val originalRenderer = renderer(raw)
        val neutralRenderer = renderer(neutral)
        fun clipsWithExposure(pixel: Int, coverage: Double): Boolean =
            hasFullChannel(originalRenderer.render(pixel, coverage, false)) &&
                !hasFullChannel(neutralRenderer.render(pixel, coverage, false))

        forEachEligible(original, support, measurement) { pixel, coverage ->
            eligible++
            if (raw[1] > 1 && clipsWithExposure(pixel, coverage)) clipped++
        }
        if (clipped == 0 || 4L * clipped < eligible) {
            return Wb314ExposureDecision(raw.copyOf(), eligible, clipped, "original")
        }

        val luminanceGain = facialLuminanceBound(analysisRgb, measurement, alpha, protected, raw)
        val hasLuminanceLimit = luminanceGain >= 1 && luminanceGain < raw[1]
        if (hasLuminanceLimit && !verifyLuminanceRgb) {
            return Wb314ExposureDecision(raw.copyOf().apply { this[1] = luminanceGain },
                eligible, clipped, "facial_luminance")
        }

        val affectedPixels = IntArray(clipped)
        val affectedAlpha = DoubleArray(clipped)
        var count = 0
        forEachEligible(original, support, measurement) { pixel, coverage ->
            if (clipsWithExposure(pixel, coverage)) {
                affectedPixels[count] = pixel
                affectedAlpha[count] = coverage
                count++
            }
        }
        check(count == clipped)
        val effective = raw.copyOf()
        fun clipsAt(gain: Double): Boolean {
            effective[1] = gain
            val trial = renderer(effective)
            return affectedPixels.indices.any { hasFullChannel(trial.render(affectedPixels[it], affectedAlpha[it], false)) }
        }
        if (hasLuminanceLimit && !clipsAt(luminanceGain)) {
            return Wb314ExposureDecision(effective, eligible, clipped, "facial_luminance")
        }
        var safe = 1.0
        var unsafe = if (hasLuminanceLimit) luminanceGain else raw[1]
        repeat(24) {
            val gain = (safe + unsafe) / 2
            if (clipsAt(gain)) {
                unsafe = gain
            } else {
                safe = gain
            }
        }
        effective[1] = safe
        return Wb314ExposureDecision(effective, eligible, clipped, "facial_rgb")
    }

    private inline fun forEachEligible(
        bitmap: Bitmap,
        support: Wb314RenderSupport,
        measurement: ByteArray,
        visit: (Int, Double) -> Unit
    ) {
        val row = IntArray(bitmap.width)
        for (y in 0 until bitmap.height) {
            bitmap.getPixels(row, 0, row.size, 0, y, row.size, 1)
            for (x in row.indices) {
                val pixel = row[x]
                if (measurement[support.measurementIndex(x, y)] == 0.toByte() || hasFullChannel(pixel)) continue
                val coverage = support.alphaAt(x, y)
                if (coverage > 0) visit(pixel, coverage)
            }
        }
    }

    private fun facialLuminanceBound(
        rgb: ByteArray,
        measurement: ByteArray,
        alpha: DoubleArray,
        protected: BooleanArray,
        raw: DoubleArray
    ): Double {
        var maximum = 0.0
        for (i in measurement.indices) {
            if (measurement[i] == 0.toByte() || alpha[i] == 0.0 || protected[i]) continue
            val r = lowerLinear(rgb[i * 3]) * raw[2]
            val g = lowerLinear(rgb[i * 3 + 1])
            val b = lowerLinear(rgb[i * 3 + 2]) * raw[3]
            maximum = maxOf(maximum, (0.2126 * r + 0.7152 * g + 0.0722 * b).pow(raw[0]))
        }
        return if (maximum == 0.0 || maximum * raw[1] <= 1) raw[1]
        else Math.nextAfter(1.0 / maximum, 0.0)
    }

    private fun lowerLinear(code: Byte): Double {
        val value = ((code.toInt() and 255) - 0.5).coerceAtLeast(0.0) / 255
        return if (value <= 0.04045) value / 12.92 else ((value + 0.055) / 1.055).pow(2.4)
    }

    private fun hasFullChannel(pixel: Int): Boolean =
        ((pixel shr 16) and 255) == 255 || ((pixel shr 8) and 255) == 255 || (pixel and 255) == 255

    private fun renderer(p: DoubleArray) = Wb314PixelRenderer(p[0], p[1], p[2], p[3], p[4])
}
