package com.example.skintonecorrection.data

import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class Wb314WarmCastTest {
    @Test fun selectsCoolingForAnEligibleWarmSignal() {
        val rgb = ByteArray(256 * 3)
        repeat(256) { pixel ->
            val levels = if (pixel < 128) intArrayOf(120, 102, 95) else intArrayOf(202, 154, 92)
            levels.forEachIndexed { channel, level -> rgb[pixel * 3 + channel] = level.toByte() }
        }
        val estimate = checkNotNull(Wb314WarmCast.estimate(rgb, DoubleArray(256) { 1.0 }))
        val controls = checkNotNull(estimate.controls)
        assertTrue(estimate.score > 0.0 && controls[2] < 0.95 && controls[3] > 1.10)
    }

    @Test fun preservesNeutralSamplesAndAbstainsWithoutEnoughSupport() {
        val rgb = ByteArray(256 * 3) { if (it / 3 < 128) 90.toByte() else 160.toByte() }
        val estimate = checkNotNull(Wb314WarmCast.estimate(rgb, DoubleArray(256) { 1.0 }))
        assertTrue(estimate.score < 0.0)
        assertNull(estimate.controls)
        assertNull(Wb314WarmCast.estimate(rgb, DoubleArray(256)))
    }
}
