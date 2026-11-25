package com.example.skintonecorrection.data

import kotlin.math.ln
import kotlin.math.pow

/** Optional development model fitted to confirmed colour decisions on three usable originals. */
internal object Wb314WarmCast {
    private val linearCodes = DoubleArray(256) { code ->
        val value = code / 255.0
        if (value <= 0.04045) value / 12.92 else ((value + 0.055) / 1.055).pow(2.4)
    }
    private val redGain = 0.95.pow(0.8048)
    private val blueGain = 1.10.pow(0.8048)

    data class Estimate(val score: Double, val controls: DoubleArray?)
    private data class Sample(val luma: Double, val red: Double, val green: Double, val blue: Double)

    fun estimate(rgb: ByteArray, alpha: DoubleArray): Estimate? {
        require(rgb.size == alpha.size * 3)
        val samples = ArrayList<Sample>()
        for (i in alpha.indices) {
            if (alpha[i] <= 0.0) continue
            val r = rgb[3 * i].toInt() and 255
            val g = rgb[3 * i + 1].toInt() and 255
            val b = rgb[3 * i + 2].toInt() and 255
            if (r !in 17..244 || g !in 17..244 || b !in 17..244) continue
            val red = linearCodes[r]
            val green = linearCodes[g]
            val blue = linearCodes[b]
            samples.add(Sample(luma(red, green, blue), red, green, blue))
        }
        if (samples.size < 256) return null
        samples.sortBy { it.luma }
        val split = medianSorted(samples.size) { samples[it].luma }
        val boundary = samples.indexOfFirst { it.luma >= split }
        if (boundary < 128 || samples.size - boundary < 128) return null
        val dark = samples.subList(0, boundary)
        val bright = samples.subList(boundary, samples.size)
        val red = median(bright) { ln(it.red / it.green) }
        val blue = median(bright) { ln(it.blue / it.green) }
        val contrast = median(bright) { ln(it.red / it.blue) } - median(dark) { ln(it.red / it.blue) }
        val score = -1.285272430430584 + 0.23283101242219392 * (red / .20) -
            0.2022077898678121 * (blue / .20) + 0.426005203584889 * (contrast / .20)
        if (score <= 0.0) return Estimate(score, null)
        val exposure = median(bright) { it.luma / luma(it.red * redGain, it.green, it.blue * blueGain) }
        return Estimate(score, doubleArrayOf(1.0, exposure, redGain, blueGain, 1.0))
    }

    private fun luma(red: Double, green: Double, blue: Double) =
        0.2126 * red + 0.7152 * green + 0.0722 * blue

    private inline fun median(samples: List<Sample>, value: (Sample) -> Double): Double {
        val sorted = DoubleArray(samples.size) { value(samples[it]) }
        sorted.sort()
        return medianSorted(sorted.size) { sorted[it] }
    }

    private inline fun medianSorted(count: Int, value: (Int) -> Double): Double =
        (value((count - 1) / 2) + value(count / 2)) / 2.0
}
