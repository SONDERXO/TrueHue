package com.example.skintonecorrection.data

import android.graphics.Bitmap
import org.json.JSONObject
import java.io.File
import java.security.MessageDigest
import kotlin.math.exp
import kotlin.math.pow
import kotlin.math.roundToInt

/** Local brightness fit applied only inside the already approved correction support. */
internal class Wb314LearnedExposure private constructor(
    private val points: List<DoubleArray>, private val coefficients: DoubleArray
) {
    fun estimate(original: Bitmap, accepted: Bitmap, alpha: DoubleArray): Double {
        val before = areaLuma(original)
        val after = areaLuma(accepted)
        val inner = DoubleArray(PIXELS)
        val surround = DoubleArray(PIXELS)
        val integral = IntArray((SIDE + 1) * (SIDE + 1))
        val stride = SIDE + 1
        for (y in 0 until SIDE) {
            var rowCount = 0
            for (x in 0 until SIDE) {
                if (alpha[y * SIDE + x] > 0.0) rowCount++
                integral[(y + 1) * stride + x + 1] = integral[y * stride + x + 1] + rowCount
            }
        }
        fun nearby(x: Int, y: Int, radius: Int): Int {
            val left = (x - radius).coerceAtLeast(0)
            val top = (y - radius).coerceAtLeast(0)
            val right = (x + radius + 1).coerceAtMost(SIDE)
            val bottom = (y + radius + 1).coerceAtMost(SIDE)
            return integral[bottom * stride + right] - integral[bottom * stride + left] -
                integral[top * stride + right] + integral[top * stride + left]
        }
        var faceCount = 0
        var ringCount = 0
        var supportCount = 0
        var priorGain = 0.0
        for (i in alpha.indices) {
            val x = i % SIDE
            val y = i / SIDE
            if (alpha[i] > 0.0) {
                priorGain += after[i] - before[i]
                supportCount++
                if (nearby(x, y, 1) == 9) inner[faceCount++] = before[i]
            } else if (nearby(x, y, 10) > 0) {
                surround[ringCount++] = before[i]
            }
        }
        if (faceCount == 0 || ringCount == 0 || supportCount == 0) return 0.0
        inner.sort(0, faceCount)
        surround.sort(0, ringCount)
        val middle = quantile(inner, faceCount, .5)
        val values = doubleArrayOf(middle, quantile(surround, ringCount, .75) - middle,
            quantile(inner, faceCount, .75) - quantile(inner, faceCount, .25), priorGain / supportCount)
        val predicted = points.indices.sumOf { i ->
            val squaredDistance = values.indices.sumOf { j ->
                val delta = (values[j] - points[i][j]) / scales[j]
                delta * delta
            }
            exp(-.5 * squaredDistance) * coefficients[i]
        }.coerceIn(0.0, .55)
        return if (predicted < .10) 0.0 else predicted
    }

    fun apply(original: Bitmap, accepted: Bitmap, support: Wb314RenderSupport,
              edge: Wb314SoftEdge, stops: Double): Int {
        val source = IntArray(original.width)
        val output = IntArray(original.width)
        val channels = Array(257) { step ->
            val gain = 2.0.pow(stops * step / 256)
            IntArray(256) { code ->
                val exposed = (linearCodes[code] * gain).coerceAtMost(1.0)
                val srgb = if (exposed <= .0031308) 12.92 * exposed
                    else 1.055 * exposed.pow(1 / 2.4) - .055
                (255 * srgb).roundToInt().coerceIn(0, 255)
            }
        }
        var count = 0
        for (y in 0 until original.height) {
            original.getPixels(source, 0, source.size, 0, y, source.size, 1)
            accepted.getPixels(output, 0, output.size, 0, y, output.size, 1)
            for (x in source.indices) {
                if (support.alphaAt(x, y) == 0.0) continue
                val ramp = ((192.0 - luma(source[x])) / 64).coerceIn(0.0, 1.0)
                val boundary = (support.interpolate(edge.distance, x, y) / 6).coerceIn(0.0, 1.0)
                val t = ramp * boundary
                val index = (256 * t * t * (3 - 2 * t)).roundToInt()
                if (index == 0) continue
                val rgb = channels[index]
                val base = output[x]
                val corrected = (base and 0xff000000.toInt()) or (rgb[(base ushr 16) and 255] shl 16) or
                    (rgb[(base ushr 8) and 255] shl 8) or rgb[base and 255]
                if (corrected == base || Wb314HighlightGuard.losesHighlight(source[x], corrected) ||
                    Wb314HighlightGuard.losesHighlight(base, corrected) || luma(corrected) < luma(base)) continue
                output[x] = corrected
                count++
            }
            accepted.setPixels(output, 0, output.size, 0, y, output.size, 1)
        }
        return count
    }

    private fun areaLuma(bitmap: Bitmap): DoubleArray {
        val sums = DoubleArray(PIXELS)
        val counts = IntArray(PIXELS)
        val row = IntArray(bitmap.width)
        val bins = IntArray(bitmap.width) { it * SIDE / bitmap.width }
        for (y in 0 until bitmap.height) {
            bitmap.getPixels(row, 0, row.size, 0, y, row.size, 1)
            val offset = y * SIDE / bitmap.height * SIDE
            for (x in row.indices) {
                val i = offset + bins[x]
                sums[i] += luma(row[x])
                counts[i]++
            }
        }
        return DoubleArray(PIXELS) { i -> if (counts[i] > 0) sums[i] / counts[i] else 0.0 }
    }

    companion object {
        private const val SIDE = 256
        private const val PIXELS = SIDE * SIDE
        private val scales = doubleArrayOf(32.0, 40.0, 30.0, 5.0)
        private val linearCodes = DoubleArray(256) { code ->
            val value = code / 255.0
            if (value <= .04045) value / 12.92 else ((value + .055) / 1.055).pow(2.4)
        }

        fun load(file: File, digest: String): Wb314LearnedExposure {
            require(file.length() in 1..8192) { "Missing local brightness fit" }
            val bytes = file.readBytes()
            val hash = MessageDigest.getInstance("SHA-256").digest(bytes).joinToString("") { "%02x".format(it) }
            require(hash == digest) { "Brightness fit checksum mismatch" }
            val data = JSONObject(bytes.toString(Charsets.UTF_8))
            val saved = data.getJSONArray("points")
            val weights = data.getJSONArray("coefficients")
            require(saved.length() in 1..64 && weights.length() == saved.length())
            val points = List(saved.length()) { i ->
                val row = saved.getJSONArray(i)
                require(row.length() == scales.size)
                DoubleArray(scales.size) { row.getDouble(it).also { value -> require(value.isFinite()) } }
            }
            val coefficients = DoubleArray(weights.length()) {
                weights.getDouble(it).also { value -> require(value.isFinite()) }
            }
            return Wb314LearnedExposure(points, coefficients)
        }

        private fun quantile(values: DoubleArray, count: Int, fraction: Double): Double {
            val position = (count - 1) * fraction
            val low = position.toInt()
            return values[low] * (1 - (position - low)) +
                values[(low + 1).coerceAtMost(count - 1)] * (position - low)
        }

        private fun luma(rgb: Int): Double =
            (2126 * ((rgb ushr 16) and 255) + 7152 * ((rgb ushr 8) and 255) + 722 * (rgb and 255)) / 10000.0
    }
}
