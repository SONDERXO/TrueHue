package com.example.skintonecorrection.data

import kotlin.math.pow

/** Retain three quarters of the predicted positive exposure in stops, subject to the RGB limit. */
internal object Wb314ExposureToning {
    fun limit(rawGain: Double, limitedGain: Double): Double =
        if (rawGain > 1.0) minOf(limitedGain, rawGain.pow(0.75)) else limitedGain
}
