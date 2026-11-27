package com.example.skintonecorrection.data

import android.graphics.Bitmap
import kotlin.math.roundToInt

/** Reduces correction contrast around a protected face-to-neck seam. */
internal class Wb314JawSeam(
    private val distance: DoubleArray, val seedCount: Int,
    private val left: Int, private val top: Int, private val right: Int, private val bottom: Int
) {
    fun apply(original: Bitmap, candidate: Bitmap, support: Wb314RenderSupport): Int {
        val side = FaceOccGeometry.SIDE
        val width = candidate.width
        val height = candidate.height
        val x0 = left * width / side
        val x1 = (right * width + side - 1) / side
        val y0 = top * height / side
        val y1 = (bottom * height + side - 1) / side
        val before = IntArray(x1 - x0)
        val proposed = IntArray(before.size)
        var changed = 0
        for (y in y0 until y1) {
            original.getPixels(before, 0, before.size, x0, y, before.size, 1)
            candidate.getPixels(proposed, 0, proposed.size, x0, y, proposed.size, 1)
            for (i in proposed.indices) {
                val x = x0 + i
                if (before[i] == proposed[i] || support.alphaAt(x, y) == 0.0) continue
                val weight = retainedWeight(support.interpolate(distance, x, y))
                if (weight == 1.0) continue
                val edited = blend(before[i], proposed[i], weight)
                if (edited != proposed[i]) {
                    proposed[i] = edited
                    changed++
                }
            }
            candidate.setPixels(proposed, 0, proposed.size, x0, y, proposed.size, 1)
        }
        return changed
    }

    companion object {
        const val radius = 10.0

        internal fun retainedWeight(distance: Double): Double {
            val t = ((distance - 2.0) / (radius - 2.0)).coerceIn(0.0, 1.0)
            return .45 + .55 * t * t * (3 - 2 * t)
        }

        internal fun blend(original: Int, proposed: Int, weight: Double): Int {
            fun channel(shift: Int): Int {
                val a = (original ushr shift) and 255
                val b = (proposed ushr shift) and 255
                return (a + (b - a) * weight).roundToInt() shl shift
            }
            return (original and 0xff000000.toInt()) or channel(16) or channel(8) or channel(0)
        }
    }
}
