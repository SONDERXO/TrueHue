package com.example.skintonecorrection.data

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class Wb314JawSeamTest {
    @Test fun keepsTheOrdinaryCorrectionBeyondTheSeam() {
        assertEquals(.45, Wb314JawSeam.retainedWeight(0.0), 0.0)
        assertEquals(.45, Wb314JawSeam.retainedWeight(2.0), 0.0)
        assertEquals(.725, Wb314JawSeam.retainedWeight(6.0), 1e-10)
        assertEquals(1.0, Wb314JawSeam.retainedWeight(10.0), 0.0)
    }

    @Test fun movesEachChannelTowardTheOriginal() {
        val original = 0xff354658.toInt()
        val candidate = 0xff5d324e.toInt()
        val tapered = Wb314JawSeam.blend(original, candidate, .45)
        assertEquals(0xff473d54.toInt(), tapered)
        assertEquals(original, Wb314JawSeam.blend(original, original, .45))
        assertTrue((tapered ushr 24) == 255)
    }
}
