package com.example.skintonecorrection.ml

import org.junit.Assert.assertEquals
import org.junit.Assert.assertThrows
import org.junit.Test

class Wb314ImageMeasurementTest {
    private val rgb = ByteArray(256 * 256 * 3) { 135.toByte() }
    private val lab = ByteArray(rgb.size) { 145.toByte() }
    private val ita = doubleArrayOf(-30.0, 60.0)
    private val mst = doubleArrayOf(10.0, 1.0)

    @Test
    fun featureExtractionUsesTheProvidedRetryMinimum() {
        val visible = ByteArray(256 * 256) { if (it < 771) 255.toByte() else 0 }
        assertThrows(IllegalArgumentException::class.java) {
            Wb314ImageFeatures.extract(rgb, lab, visible, ita, mst)
        }
        assertEquals(281, Wb314ImageFeatures.extract(rgb, lab, visible, ita, mst, 750).size)
        assertThrows(IllegalArgumentException::class.java) {
            Wb314ImageFeatures.extract(rgb, lab, visible, ita, mst, 772)
        }
    }
}
