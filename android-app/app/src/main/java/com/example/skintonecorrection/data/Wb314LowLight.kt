package com.example.skintonecorrection.data

import kotlin.math.pow

/** A bounded exposure-only proposal for severe backlight when WB314 selected identity. */
internal object Wb314LowLight {
    val gain = 2.0.pow(3.0 / 8.0)

    fun hasSevereBacklight(rgb: ByteArray, measurement: ByteArray, alpha: DoubleArray): Boolean {
        require(rgb.size == measurement.size * 3 && alpha.size == measurement.size)
        val face = IntArray(256)
        val scene = IntArray(256)
        var faceCount = 0
        var sceneCount = 0
        var brightCount = 0
        for (i in measurement.indices) {
            val measured = measurement[i] != 0.toByte()
            if (!measured && alpha[i] > 0.0) continue
            val j = i * 3
            val level = (2126 * (rgb[j].toInt() and 255) + 7152 * (rgb[j + 1].toInt() and 255) +
                722 * (rgb[j + 2].toInt() and 255) + 5000) / 10_000
            if (measured) {
                face[level]++
                faceCount++
            } else {
                scene[level]++
                sceneCount++
                if (level >= 224) brightCount++
            }
        }
        if (faceCount == 0 || sceneCount == 0 || 16L * brightCount < sceneCount) return false
        val faceUpper = linear(percentile(face, faceCount, 75))
        val sceneHighlight = linear(percentile(scene, sceneCount, 95))
        return faceUpper > 0 && 8.0 * faceUpper <= sceneHighlight
    }

    private fun percentile(histogram: IntArray, count: Int, percent: Int): Int {
        val rank = (count * percent + 99) / 100
        var seen = 0
        return histogram.indices.first { index ->
            seen += histogram[index]
            seen >= rank
        }
    }

    private fun linear(code: Int): Double {
        val x = code / 255.0
        return if (x <= 0.04045) x / 12.92 else ((x + 0.055) / 1.055).pow(2.4)
    }
}
