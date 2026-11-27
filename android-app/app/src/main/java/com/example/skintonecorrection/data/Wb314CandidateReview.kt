package com.example.skintonecorrection.data

import android.graphics.Bitmap
import kotlin.math.abs

/** Reviews the combined correction on the saved support before it can be exported. */
internal object Wb314CandidateReview {
    const val defaultStops = .30

    data class Samples(
        val face: Int,
        val changed: Int,
        val brightInput: Int,
        val brightenedHighlights: Int,
        val newClipping: Int,
        val strongEdits: Int,
        val absoluteChange: Long
    ) {
        fun rejection(defaultExposure: Boolean): String? = when {
            face == 0 || changed == 0 -> "no_visible_edit"
            200L * newClipping > face -> "new_clipping"
            50L * brightenedHighlights > face -> "brightened_highlights"
            20L * strongEdits > face || absoluteChange > 18L * 3 * face -> "heavy_edit"
            defaultExposure && 5L * brightInput >= face -> "already_bright"
            else -> null
        }
    }

    fun sample(original: Bitmap, candidate: Bitmap, alpha: DoubleArray): Samples {
        val side = FaceOccGeometry.SIDE
        val width = original.width
        val height = original.height
        val before = IntArray(width)
        val after = IntArray(width)
        val columns = IntArray(width) { it * side / width }
        var face = 0
        var changed = 0
        var brightInput = 0
        var brightenedHighlights = 0
        var newClipping = 0
        var strongEdits = 0
        var absoluteChange = 0L
        for (y in 0 until height step 4) {
            val offset = y * side / height * side
            original.getPixels(before, 0, width, 0, y, width, 1)
            candidate.getPixels(after, 0, width, 0, y, width, 1)
            for (x in 0 until width step 4) {
                if (alpha[offset + columns[x]] <= 0.0) continue
                val a = before[x]
                val b = after[x]
                val initial = luma(a)
                val final = luma(b)
                val red = abs(((b ushr 16) and 255) - ((a ushr 16) and 255))
                val green = abs(((b ushr 8) and 255) - ((a ushr 8) and 255))
                val blue = abs((b and 255) - (a and 255))
                val peak = maxOf(red, green, blue)
                face++
                if (peak > 1) changed++
                if (peak > 48) strongEdits++
                if (initial >= 160) brightInput++
                if (final >= 224 && final - initial >= 6) brightenedHighlights++
                if (Wb314HighlightGuard.newlyClips(a, b)) newClipping++
                absoluteChange += red + green + blue
            }
        }
        return Samples(face, changed, brightInput, brightenedHighlights, newClipping, strongEdits, absoluteChange)
    }

    private fun luma(pixel: Int): Int = (2126 * ((pixel ushr 16) and 255) +
        7152 * ((pixel ushr 8) and 255) + 722 * (pixel and 255) + 5000) / 10_000
}
