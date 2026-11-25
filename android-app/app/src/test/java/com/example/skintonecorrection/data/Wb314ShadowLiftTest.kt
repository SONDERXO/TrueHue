package com.example.skintonecorrection.data

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class Wb314ShadowLiftTest {
    @Test fun selectsDeepShadowsWithoutChangingEvenLighting() {
        assertNull(Wb314ShadowLift.select(116, 152, false))
        val lift = checkNotNull(Wb314ShadowLift.select(64, 131, false))
        val dark = gray(55)
        assertTrue((lift.keepSafe(dark, dark, lift.propose(dark, dark, 1.0)) and 255) > 55)
        val bright = gray(131)
        assertEquals(bright, lift.propose(bright, bright, 1.0))
        assertEquals(dark, lift.propose(dark, dark, 0.0))
    }

    @Test fun blockedBacklightUsesLocalLiftAndKeepsAcceptedPixelsAtRisk() {
        assertNull(Wb314ShadowLift.select(75, 95, false))
        val lift = checkNotNull(Wb314ShadowLift.select(75, 95, true))
        val base = 0xfffc2929.toInt()
        assertEquals(base, lift.keepSafe(base, base, 0xffff3333.toInt()))
        assertEquals(base, lift.keepSafe(base, base, gray(30)))
    }

    private fun gray(value: Int) = 0xff000000.toInt() or (value shl 16) or (value shl 8) or value
}
