package com.example.skintonecorrection.data

import org.junit.Assert.assertEquals
import org.junit.Test
import kotlin.math.sqrt

class Wb314ExposureToningTest {
    @Test fun reducesPositiveExposureInStops() {
        assertEquals(1.2968395546510096, Wb314ExposureToning.limit(sqrt(2.0), sqrt(2.0)), 1e-14)
    }

    @Test fun preservesExistingStricterLimitAndNonpositiveExposure() {
        assertEquals(1.005, Wb314ExposureToning.limit(sqrt(2.0), 1.005), 0.0)
        assertEquals(1.0, Wb314ExposureToning.limit(1.0, 1.0), 0.0)
        assertEquals(0.8, Wb314ExposureToning.limit(0.8, 0.8), 0.0)
    }
}
