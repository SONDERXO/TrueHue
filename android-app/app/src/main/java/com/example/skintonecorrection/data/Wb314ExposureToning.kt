package com.example.skintonecorrection.data

import kotlin.math.pow

/** Retain three quarters of the predicted positive exposure in stops, subject to the RGB limit. */
internal object Wb314ExposureToning {
    fun limit(rawGain: Double, limitedGain: Double): Double =
        if (rawGain > 1.0) minOf(limitedGain, rawGain.pow(0.75)) else limitedGain

    /** A positive gain is unsuitable when at least a quarter of the measured face is near white. */
    fun hasWidespreadNearWhite(rgb: ByteArray, measurement: ByteArray): Boolean {
        require(rgb.size == measurement.size * 3)
        var measured = 0
        var nearWhite = 0
        for (i in measurement.indices) {
            if (measurement[i] == 0.toByte()) continue
            measured++
            val j = i * 3
            val luma = 2126 * (rgb[j].toInt() and 255) + 7152 * (rgb[j + 1].toInt() and 255) +
                722 * (rgb[j + 2].toInt() and 255)
            if (luma >= 240 * 10_000) nearWhite++
        }
        return measured > 0 && 4L * nearWhite >= measured
    }
}
