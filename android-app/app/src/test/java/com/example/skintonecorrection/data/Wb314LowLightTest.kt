package com.example.skintonecorrection.data

import org.junit.Assert.assertFalse
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
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

    private fun diffuseBacklight(faceLower: Int, faceUpper: Int, litScene: Int, enabled: Boolean = true): Double? {
        val levels = IntArray(40) { i -> when {
            i < 4 -> faceLower
            i < 8 -> faceUpper
            i < 8 + litScene -> 210
            else -> 100
        } }
        val rgb = ByteArray(3 * levels.size) { levels[it / 3].toByte() }
        val measurement = ByteArray(levels.size) { if (it < 8) -1 else 0 }
        val alpha = DoubleArray(levels.size) { if (it < 8) 1.0 else 0.0 }
        return Wb314LowLight.proposedGain(rgb, measurement, alpha, enabled)
    }

    @Test fun diffuseBacklightRequiresBroadLightingAndFaceShadows() {
        assertEquals(Math.pow(2.0, 5.0 / 8.0), diffuseBacklight(47, 78, 8)!!, 0.0)
        assertNull(diffuseBacklight(47, 78, 8, enabled = false))
        assertNull(diffuseBacklight(47, 78, 7))
        assertNull(diffuseBacklight(78, 78, 8))
        assertNull(diffuseBacklight(47, 92, 8))
    }

    @Test fun diffuseLiftIncreasesWithShadowDepthAndStopsAtOneStop() {
        val ordinary = diffuseBacklight(47, 78, 8)!!
        val deeper = diffuseBacklight(32, 78, 8)!!
        val deepest = diffuseBacklight(18, 78, 8)!!
        assertTrue(ordinary < deeper && deeper < deepest)
        assertEquals(2.0, deepest, 0.0)
    }
}
