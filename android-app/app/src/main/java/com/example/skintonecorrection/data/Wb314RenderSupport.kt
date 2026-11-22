package com.example.skintonecorrection.data

import kotlin.math.floor

/** Frozen mapping from original frame coordinates to the WB314 analysis support. */
internal class Wb314RenderSupport(
    width: Int,
    height: Int,
    private val alpha: DoubleArray,
    private val protected: BooleanArray,
    private val researchPrecision: Boolean = false
) {
    private data class Sample(val nearest: Int, val low: Int, val high: Int,
                              val weight: Double, val complement: Double)

    private val xAxis = axis(width)
    private val yAxis = axis(height)

    fun measurementIndex(x: Int, y: Int): Int = yAxis[y].nearest * SIDE + xAxis[x].nearest

    fun alphaAt(x: Int, y: Int): Double {
        val index = measurementIndex(x, y)
        if (protected[index] || alpha[index] == 0.0) return 0.0
        return interpolate(alpha, x, y).coerceIn(0.0, 1.0)
    }

    fun interpolate(values: DoubleArray, x: Int, y: Int): Double {
        val xx = xAxis[x]
        val yy = yAxis[y]
        val low = blend(values[yy.low * SIDE + xx.low], values[yy.low * SIDE + xx.high], xx)
        val high = blend(values[yy.high * SIDE + xx.low], values[yy.high * SIDE + xx.high], xx)
        return blend(low, high, yy)
    }

    private fun axis(size: Int) = Array(size) { i ->
        val coordinate = (i + 0.5) * SIDE / size - 0.5
        val position = if (researchPrecision) coordinate else coordinate.toFloat().toDouble()
        val low = floor(position).toInt()
        val weight = if (researchPrecision) position - low else (position.toFloat() - low).toDouble()
        val complement = if (researchPrecision) 1.0 - weight else (1.0 - weight).toFloat().toDouble()
        Sample((i.toLong() * SIDE / size).toInt(), low.coerceIn(0, SIDE - 1),
            (low + 1).coerceIn(0, SIDE - 1), weight, complement)
    }

    private fun blend(a: Double, b: Double, sample: Sample): Double =
        a * sample.complement + b * sample.weight

    companion object {
        private const val SIDE = 256
    }
}
