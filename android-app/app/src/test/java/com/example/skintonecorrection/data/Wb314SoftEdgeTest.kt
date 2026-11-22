package com.example.skintonecorrection.data

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class Wb314SoftEdgeTest {
    private val edge = Wb314SoftEdge(DoubleArray(256 * 256), 4)

    @Test fun boundaryAndCoreKeepTheirExpectedPixels() {
        val input = 0xff3850f0.toInt()
        val corrected = 0xff9850c0.toInt()
        assertEquals(input, edge.blend(input, corrected, 0.0))
        assertEquals(corrected, edge.blend(input, corrected, 8.0))
        assertEquals(0xff6850d8.toInt(), edge.blend(input, corrected, 4.0))
    }

    @Test fun fadeMovesEachChannelTowardInputWithoutNewClipping() {
        val input = 0xff30fe87.toInt()
        val corrected = 0xfff02bf0.toInt()
        for (step in 0..64) {
            val distance = step / 8.0
            val blended = edge.blend(input, corrected, distance)
            assertTrue(((blended ushr 16) and 255) in 48..240)
            assertTrue(((blended ushr 8) and 255) in 43..254)
            assertTrue((blended and 255) in 135..240)
            assertEquals(input, edge.blend(input, input, distance))
        }
    }
}
