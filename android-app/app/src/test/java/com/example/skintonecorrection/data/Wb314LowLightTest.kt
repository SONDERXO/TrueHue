package com.example.skintonecorrection.data

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class Wb314LowLightTest {
    private fun qualifies(faceCode: Int, brightScene: Int, highlightsInMask: Boolean = false): Boolean {
        val levels = IntArray(40) { i -> if (i < 8) faceCode else if (i < 8 + brightScene) 238 else 45 }
        val rgb = ByteArray(3 * levels.size) { levels[it / 3].toByte() }
        val measurement = ByteArray(levels.size) { if (it < 8) -1 else 0 }
        val alpha = DoubleArray(levels.size) { if (it < 8 || highlightsInMask && it < 8 + brightScene) 1.0 else 0.0 }
        return Wb314LowLight.hasSevereBacklight(rgb, measurement, alpha)
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
}
