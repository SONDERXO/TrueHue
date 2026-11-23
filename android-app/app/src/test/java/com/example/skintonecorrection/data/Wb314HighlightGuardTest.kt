package com.example.skintonecorrection.data

import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class Wb314HighlightGuardTest {
    @Test fun rejectsLocalClippingFromCombinedControls() {
        assertTrue(Wb314HighlightGuard.losesHighlight(0xff80f090.toInt(), 0xfffffa90.toInt()))
        assertTrue(Wb314HighlightGuard.losesHighlight(0xfffff090.toInt(), 0xffffff90.toInt()))
        assertFalse(Wb314HighlightGuard.losesHighlight(0xffff9090.toInt(), 0xffffa090.toInt()))
    }

    @Test fun rejectsAJumpIntoNearWhiteAndPreservesModestLifts() {
        assertTrue(Wb314HighlightGuard.losesHighlight(0xffe0e0e0.toInt(), 0xfff0f0f0.toInt()))
        assertFalse(Wb314HighlightGuard.losesHighlight(0xffe0e0e0.toInt(), 0xffefefef.toInt()))
        assertFalse(Wb314HighlightGuard.losesHighlight(0xff404040.toInt(), 0xff505050.toInt()))
    }

    @Test fun halvesTheFullProposalInLogSpace() {
        assertArrayEquals(doubleArrayOf(1.0, 2.0, 0.5, 1.0, 1.0),
            Wb314HighlightGuard.backedOff(doubleArrayOf(1.0, 4.0, 0.25, 1.0, 1.0)), 0.0)
    }
}
