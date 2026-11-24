package com.example.skintonecorrection.data

import org.junit.Assert.assertFalse
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class Wb314LowLightTest {
    private fun qualifies(faceCode: Int, brightScene: Int, highlightsInMask: Boolean = false): Boolean {
        val levels = IntArray(40) { i -> if (i < 8) faceCode else if (i < 8 + brightScene) 238 else 45 }
        val rgb = ByteArray(3 * levels.size) { levels[it / 3].toByte() }
        val measurement = ByteArray(levels.size) { if (it < 8) -1 else 0 }
        val alpha = DoubleArray(levels.size) { if (it < 8 || highlightsInMask && it < 8 + brightScene) 1.0 else 0.0 }
        val gain = Wb314LowLight.proposedGain(rgb, measurement, alpha)
        if (gain != null) assertEquals(Wb314LowLight.gain, gain, 0.0)
        return gain != null
    }

    @Test fun requiresStrongBacklightAndDeepFacialShadow() {
        assertTrue(qualifies(58, 3))
        assertFalse(qualifies(118, 3))
        assertFalse(qualifies(58, 1))
        assertFalse(qualifies(58, 0))
        assertFalse(qualifies(0, 3))
    }

    @Test fun highlightsInsideApplicationAreaDoNotCountAsSceneEvidence() {
        assertFalse(qualifies(58, 3, highlightsInMask = true))
    }

    private fun diffuseBacklight(faceLower: Int, faceUpper: Int, litScene: Int, enabled: Boolean = true): Boolean {
        val levels = IntArray(40) { i -> when {
            i < 4 -> faceLower
            i < 8 -> faceUpper
            i < 8 + litScene -> 210
            else -> 100
        } }
        val rgb = ByteArray(3 * levels.size) { levels[it / 3].toByte() }
        val measurement = ByteArray(levels.size) { if (it < 8) -1 else 0 }
        val alpha = DoubleArray(levels.size) { if (it < 8) 1.0 else 0.0 }
        val gain = Wb314LowLight.proposedGain(rgb, measurement, alpha, enabled)
        if (gain != null) assertEquals(Math.pow(2.0, 5.0 / 8.0), gain, 0.0)
        return gain != null
    }

    @Test fun diffuseBacklightRequiresBroadLightingAndFaceShadows() {
        assertTrue(diffuseBacklight(47, 78, 8))
        assertFalse(diffuseBacklight(47, 78, 8, enabled = false))
        assertFalse(diffuseBacklight(47, 78, 7))
        assertFalse(diffuseBacklight(78, 78, 8))
        assertFalse(diffuseBacklight(47, 92, 8))
    }
}
