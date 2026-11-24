package com.example.skintonecorrection.data

import org.junit.Assert.assertEquals
import org.junit.Test

class ResearchMaskMeasurementTest {
    @Test
    fun ordinaryAnalysisKeepsTheExistingMinimum() {
        assertEquals(1_000, ResearchMaskRules.minimumMeasurementPixels(null))
    }

    @Test
    fun retryMinimumRoundsUpAndRemainsBounded() {
        assertEquals(750, ResearchMaskRules.minimumMeasurementPixels(1_000))
        assertEquals(751, ResearchMaskRules.minimumMeasurementPixels(2_501))
        assertEquals(900, ResearchMaskRules.minimumMeasurementPixels(3_000))
        assertEquals(1_000, ResearchMaskRules.minimumMeasurementPixels(4_000))
    }
}
