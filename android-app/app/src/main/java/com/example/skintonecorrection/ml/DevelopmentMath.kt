package com.example.skintonecorrection.ml

import kotlin.math.*

/** Deterministic numerical helpers; experimental lookup, not validated skin truth. */
object DevelopmentMath {
    fun rounded(value: Double, digits: Int = 4): Double {
        val scale = 10.0.pow(digits)
        return Math.rint(value * scale) / scale
    }
    fun ita(l: Double, b: Double): Double {
        require(l.isFinite() && b.isFinite() && abs(b) >= 1e-6) { "ITA is undefined for this skin region." }
        return rounded(atan((l - 50.0) / b) * 180.0 / PI)
    }
    fun mst(ita: Double, x: DoubleArray, y: DoubleArray): Int {
        require(ita.isFinite() && x.isNotEmpty() && x.size == y.size)
        require(x.all { it.isFinite() } && y.all { it.isFinite() && it in 1.0..10.0 })
        require((1 until x.size).all { x[it] > x[it-1] && y[it] <= y[it-1] })
        val value = when {
            ita <= x.first() -> y.first()
            ita >= x.last() -> y.last()
            else -> { val i = (0 until x.lastIndex).first { ita < x[it+1] }
                y[i] + (ita-x[i]) * (y[i+1]-y[i]) / (x[i+1]-x[i]) }
        }
        return floor(value + .5).toInt()
    }
    /** Current desktop baseline uses reciprocal gamma. Never pass direct targets here. */
    fun correct(argb: Int, p: DoubleArray): Int {
        require(p.size == 3 && p.all { it.isFinite() && it > 0 })
        fun channel(v: Int, gain: Double): Int = Math.rint(((v/255.0).pow(1.0/p[0])*gain).coerceIn(0.0,1.0)*255).toInt()
        return (argb and -0x1000000) or (channel((argb ushr 16) and 255,p[1]) shl 16) or
            (channel((argb ushr 8) and 255,1.0) shl 8) or channel(argb and 255,p[2])
    }
}
