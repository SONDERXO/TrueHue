package com.example.skintonecorrection.data

/** Attenuate the saved correction inside the mask without adding application pixels. */
internal class Wb314SoftEdge(val distance: DoubleArray, private val width: Int) {
    fun blend(input: Int, corrected: Int, boundaryDistance: Double): Int {
        if (boundaryDistance <= 0) return input
        if (boundaryDistance >= 2 * width) return corrected
        val weight = smooth(boundaryDistance / (2 * width)) / smooth(boundaryDistance / width)
        fun channel(shift: Int): Int {
            val from = (input ushr shift) and 255
            val to = (corrected ushr shift) and 255
            return Math.rint(from + (to - from) * weight).toInt() shl shift
        }
        return (corrected and 0xff000000.toInt()) or channel(16) or channel(8) or channel(0)
    }

    private fun smooth(value: Double): Double {
        val t = value.coerceIn(0.0, 1.0)
        return t * t * (3 - 2 * t)
    }
}
