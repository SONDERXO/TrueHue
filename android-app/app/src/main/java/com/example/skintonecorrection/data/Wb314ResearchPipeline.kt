package com.example.skintonecorrection.data

import android.graphics.Bitmap
import com.example.skintonecorrection.ml.PortableRegressionTree
import com.example.skintonecorrection.ml.PortableTreeAsset
import com.example.skintonecorrection.ml.Wb314Features
import com.example.skintonecorrection.ml.Wb314PixelRenderer
import com.example.skintonecorrection.ml.Wb314WhiteBalance
import org.json.JSONObject
import org.opencv.android.Utils
import org.opencv.core.Mat
import org.opencv.core.Size
import org.opencv.imgproc.Imgproc
import java.io.DataInputStream
import java.io.File
import java.security.DigestInputStream
import java.security.MessageDigest
import kotlin.math.floor

/** WB314 feature extraction and rendering with masks from the same normalized input. */
internal class Wb314ResearchPipeline private constructor(
    private val tree: PortableRegressionTree,
    private val whiteBalance: Wb314WhiteBalance,
    private val itaKnots: DoubleArray,
    private val mstKnots: DoubleArray
) {
    data class Result(val bitmap: Bitmap, val features: DoubleArray, val controls: DoubleArray, val leaf: Int)
    data class AutoResult(val correction: Result, val masks: ResearchMaskRules.Result)

    companion object {
        private const val SIDE = 256
        private const val PIXELS = SIDE * SIDE

        /** The manifest digest must come from the trusted local release, outside this folder. */
        fun load(folder: File, manifestSha: String): Wb314ResearchPipeline {
            val manifest = JSONObject(checkedBytes(File(folder, "manifest.json"), manifestSha, 4096).toString(Charsets.UTF_8))
            require(manifest.getString("schema") == "truehue_wb314_android_research_v1")
            val modelSha = manifest.getString("tree_sha256")
            val tree = PortableTreeAsset.parseWb314(checkedBytes(File(folder, "model.json"), modelSha, 65536), modelSha)
            val mapping = JSONObject(checkedBytes(File(folder, "mapping.json"), manifest.getString("mapping_sha256"),
                65536).toString(Charsets.UTF_8))
            require(mapping.getString("schema_version") == "truehue_shared_core_development_mst_v1")
            require(mapping.getString("status") == "development_unvalidated_transfer")
            fun knots(name: String) = mapping.getJSONArray(name).let { a -> DoubleArray(a.length()) { a.getDouble(it) } }
            val bank = File(folder, "wb_srgb.bin")
            val digest = MessageDigest.getInstance("SHA-256")
            val wb = DataInputStream(DigestInputStream(bank.inputStream().buffered(), digest)).use { input ->
                val rows = input.readInt()
                require(rows == 62_535) { "Unexpected WB_sRGB bank dimensions" }
                fun floats(count: Int) = FloatArray(count) { input.readFloat() }
                val offset = floats(10_800)
                val projection = floats(10_800 * 55)
                val encoded = floats(rows * 55)
                val coefficients = floats(rows * 33)
                val norms = floats(rows)
                require(input.read() == -1 && hex(digest.digest()) == manifest.getString("bank_sha256")) {
                    "WB_sRGB bank checksum mismatch"
                }
                Wb314WhiteBalance(offset, projection, encoded, coefficients, norms)
            }
            return Wb314ResearchPipeline(tree, wb, knots("ita_knots"), knots("mst_score_knots"))
        }

        private fun checkedBytes(file: File, expected: String, maxBytes: Long): ByteArray {
            require(file.length() in 1..maxBytes) { "Unexpected research asset size" }
            val bytes = file.readBytes()
            require(hex(MessageDigest.getInstance("SHA-256").digest(bytes)) == expected) { "Research asset checksum mismatch" }
            return bytes
        }

        private fun hex(bytes: ByteArray) = bytes.joinToString("") { "%02x".format(it) }
    }

    fun correct(
        original: Bitmap, measurement: ByteArray, alpha: DoubleArray, protected: BooleanArray,
        normalizedRgbSha: String
    ): Result = withNormalizedRgb(original) { rgb ->
        val bytes = rgbBytes(rgb)
        val actual = hex(MessageDigest.getInstance("SHA-256").digest(bytes))
        require(actual == normalizedRgbSha) { "Masks belong to a different analysis image" }
        correctNormalized(original, rgb, bytes, measurement, alpha, protected)
    }

    fun correct(original: Bitmap, generator: Wb314ResearchMasks, glasses: GlassesChoice): AutoResult =
        withNormalizedRgb(original) { rgb ->
            val bgr = Mat()
            val masks = try {
                Imgproc.cvtColor(rgb, bgr, Imgproc.COLOR_RGB2BGR)
                generator.generate(bgr, glasses).masks
            } finally {
                bgr.release()
            }
            val correction = correctNormalized(original, rgb, rgbBytes(rgb), masks.measurement,
                masks.alpha, masks.protected)
            AutoResult(correction, masks)
        }

    private fun correctNormalized(original: Bitmap, rgb: Mat, bytes: ByteArray, measurement: ByteArray,
                                  alpha: DoubleArray, protected: BooleanArray): Result {
        require(measurement.size == PIXELS && alpha.size == PIXELS && protected.size == PIXELS)
        require(alpha.indices.all { alpha[it] in 0.0..1.0 && (!protected[it] || alpha[it] == 0.0) })
        require(alpha.any { it > 0.0 })
        val features = Wb314Features.extract(rgb, measurement, itaKnots, mstKnots, whiteBalance.extract(bytes))
        val controls = tree.predict(features)
        return Result(render(original, alpha, protected, controls), features, controls, tree.leafId(features))
    }

    private fun rgbBytes(rgb: Mat) = ByteArray(PIXELS * 3).also { check(rgb.get(0, 0, it) == it.size) }

    private fun <T> withNormalizedRgb(original: Bitmap, action: (Mat) -> T): T {
        val rgba = Mat()
        val resized = Mat()
        val rgb = Mat()
        try {
            Utils.bitmapToMat(original, rgba)
            Imgproc.resize(rgba, resized, Size(SIDE.toDouble(), SIDE.toDouble()), 0.0, 0.0, Imgproc.INTER_AREA)
            rgba.release()
            Imgproc.cvtColor(resized, rgb, Imgproc.COLOR_RGBA2RGB)
            return action(rgb)
        } finally {
            rgb.release()
            resized.release()
            rgba.release()
        }
    }

    private fun render(original: Bitmap, alpha: DoubleArray, protected: BooleanArray, controls: DoubleArray): Bitmap {
        val width = original.width
        val height = original.height
        val xAxis = axis(width)
        val yAxis = axis(height)
        val renderer = Wb314PixelRenderer(controls[0], controls[1], controls[2], controls[3], controls[4])
        val result = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
        try {
            val row = IntArray(width)
            for (y in 0 until height) {
                val yy = yAxis[y]
                original.getPixels(row, 0, width, 0, y, width, 1)
                for (x in row.indices) {
                    val xx = xAxis[x]
                    val nearest = yy.nearest * SIDE + xx.nearest
                    if (protected[nearest] || alpha[nearest] == 0.0) continue
                    val a = blend(alpha[yy.low * SIDE + xx.low], alpha[yy.low * SIDE + xx.high], xx.weight)
                    val b = blend(alpha[yy.high * SIDE + xx.low], alpha[yy.high * SIDE + xx.high], xx.weight)
                    row[x] = renderer.render(row[x], blend(a, b, yy.weight).coerceIn(0.0, 1.0), false)
                }
                result.setPixels(row, 0, width, 0, y, width, 1)
            }
            return result
        } catch (error: Throwable) {
            result.recycle()
            throw error
        }
    }

    private data class Sample(val nearest: Int, val low: Int, val high: Int, val weight: Double)

    private fun axis(size: Int) = Array(size) { i ->
        val coordinate = ((i + 0.5) * SIDE / size - 0.5).toFloat()
        val lo = floor(coordinate).toInt()
        Sample((i.toLong() * SIDE / size).toInt(), lo.coerceIn(0, SIDE - 1),
            (lo + 1).coerceIn(0, SIDE - 1), (coordinate - lo).toDouble())
    }

    private fun blend(a: Double, b: Double, weight: Double): Double =
        a * (1.0 - weight).toFloat().toDouble() + b * weight
}
