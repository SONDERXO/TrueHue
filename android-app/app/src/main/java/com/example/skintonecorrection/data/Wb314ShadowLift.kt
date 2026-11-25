package com.example.skintonecorrection.data

import com.example.skintonecorrection.ml.Wb314PixelRenderer
import kotlin.math.pow

internal class Wb314ShadowLift private constructor(private val lower: Int, private val upper: Int) {
    private val renderer = Wb314PixelRenderer(1.0, Wb314LowLight.gain, 1.0, 1.0, 1.0)
    private val floor = lower * 10_000
    private val ceiling = upper * 10_000

    fun propose(original: Int, base: Int, coverage: Double): Int {
        val level = luma(original)
        if (level >= ceiling || coverage <= 0.0) return base
        val blend = ((ceiling - level).toDouble() / (ceiling - floor)).coerceIn(0.0, 1.0)
        val opacity = coverage * blend * blend * (3 - 2 * blend)
        return renderer.render(base, opacity, false)
    }

    fun keepSafe(original: Int, base: Int, proposed: Int): Int =
        if (luma(proposed) <= luma(base) || Wb314HighlightGuard.losesHighlight(original, proposed) ||
            Wb314HighlightGuard.losesHighlight(base, proposed)) base else proposed

    companion object {
        fun select(faceLuma25: Int?, faceLuma75: Int?, backlightBlockedByHeadroom: Boolean): Wb314ShadowLift? {
            val lower = faceLuma25 ?: return null
            val upper = faceLuma75 ?: return null
            if (lower <= 0 || upper <= lower) return null
            val deepShadows = linear(upper) >= 2.0.pow(1.5) * linear(lower)
            return if (deepShadows || backlightBlockedByHeadroom) Wb314ShadowLift(lower, upper) else null
        }

        private fun linear(code: Int): Double {
            val x = code / 255.0
            return if (x <= .04045) x / 12.92 else ((x + .055) / 1.055).pow(2.4)
        }

        private fun luma(pixel: Int): Int =
            2126 * ((pixel ushr 16) and 255) + 7152 * ((pixel ushr 8) and 255) + 722 * (pixel and 255)
    }
}
