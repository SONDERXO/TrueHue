package com.example.skintonecorrection.data

import org.opencv.core.CvType
import org.opencv.core.Mat
import org.opencv.core.Point
import org.opencv.dnn.Dnn
import org.opencv.dnn.Net
import java.io.File
import java.security.MessageDigest

/** Local FaceOcc runner for aligned RGB pixels. Call from one inference thread. */
internal class FaceOccResearchModel private constructor(private val net: Net) {
    companion object {
        private const val SIDE = 256
        private const val PIXELS = SIDE * SIDE
        private val MEAN = floatArrayOf(0.485f, 0.456f, 0.406f)
        private val STD = floatArrayOf(0.229f, 0.224f, 0.225f)

        fun load(graph: File, expectedSha: String): FaceOccResearchModel {
            val digest = MessageDigest.getInstance("SHA-256")
            graph.inputStream().use { input ->
                val buffer = ByteArray(65_536)
                var count = input.read(buffer)
                while (count != -1) {
                    digest.update(buffer, 0, count)
                    count = input.read(buffer)
                }
            }
            val actual = digest.digest().joinToString("") { "%02x".format(it) }
            require(actual == expectedSha) { "FaceOcc graph checksum mismatch" }
            val net = Dnn.readNetFromONNX(graph.path)
            check(!net.empty()) { "FaceOcc graph did not load" }
            net.setPreferableBackend(Dnn.DNN_BACKEND_OPENCV)
            net.setPreferableTarget(Dnn.DNN_TARGET_CPU)
            return FaceOccResearchModel(net)
        }
    }

    fun visibleMask(bgr: Mat, landmarks: List<Point>, template: DoubleArray): ByteArray {
        val aligned = FaceOccGeometry.align(bgr, landmarks, template)
        return FaceOccGeometry.reproject(logits(aligned.rgb), aligned.matrix, bgr.cols(), bgr.rows())
    }

    fun logits(rgb: ByteArray): FloatArray {
        require(rgb.size == PIXELS * 3) { "FaceOcc requires aligned RGB256" }
        val nchw = FloatArray(rgb.size)
        for (channel in 0..2) {
            for (pixel in 0 until PIXELS) {
                val code = rgb[pixel * 3 + channel].toInt() and 255
                nchw[channel * PIXELS + pixel] = (code / 255f - MEAN[channel]) / STD[channel]
            }
        }
        val origin = intArrayOf(0, 0, 0, 0)
        val input = Mat(intArrayOf(1, 3, SIDE, SIDE), CvType.CV_32F)
        try {
            check(input.put(origin, nchw) == nchw.size * Float.SIZE_BYTES)
            net.setInput(input)
            val output = net.forward()
            try {
                check(output.dims() == 4 && output.size(0) == 1 && output.size(1) == 1 &&
                    output.size(2) == SIDE && output.size(3) == SIDE && output.type() == CvType.CV_32F) {
                    "Unexpected FaceOcc output tensor"
                }
                val logits = FloatArray(PIXELS)
                check(output.get(origin, logits) == logits.size * Float.SIZE_BYTES)
                check(logits.all { it.isFinite() }) { "Nonfinite FaceOcc logits" }
                return logits
            } finally {
                output.release()
            }
        } finally {
            input.release()
        }
    }
}
