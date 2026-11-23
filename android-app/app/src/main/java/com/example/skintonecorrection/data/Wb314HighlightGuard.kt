package com.example.skintonecorrection.data

import kotlin.math.sqrt

/** Check the actual blended RGB output against the original before delivering an edit. */
internal object Wb314HighlightGuard {
    fun backedOff(controls: DoubleArray): DoubleArray = DoubleArray(controls.size) { sqrt(controls[it]) }

    fun losesHighlight(before: Int, after: Int): Boolean {
        if (before == after) return false
        if (newlyClips(before, after)) return true
        val originalLuma = luma(before)
        val resultLuma = luma(after)
        return resultLuma >= 240 * 10_000 && resultLuma - originalLuma >= 16 * 10_000
    }

    fun newlyClips(before: Int, after: Int): Boolean =
        ((before ushr 16) and 255) < 255 && ((after ushr 16) and 255) == 255 ||
            ((before ushr 8) and 255) < 255 && ((after ushr 8) and 255) == 255 ||
            (before and 255) < 255 && (after and 255) == 255

    private fun luma(pixel: Int): Int =
        2126 * ((pixel ushr 16) and 255) + 7152 * ((pixel ushr 8) and 255) + 722 * (pixel and 255)
}
