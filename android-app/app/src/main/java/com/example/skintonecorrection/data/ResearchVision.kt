package com.example.skintonecorrection.data

import org.opencv.core.CvType
import org.opencv.core.Mat
import org.opencv.dnn.Dnn
import org.opencv.dnn.Net
import org.opencv.core.Size
import org.opencv.imgproc.Imgproc
import java.io.File
import java.security.MessageDigest

internal object ResearchVision {
    private val mean = floatArrayOf(0.485f, 0.456f, 0.406f)
    private val std = floatArrayOf(0.229f, 0.224f, 0.225f)

    fun checkDigest(file: File, expected: String) {
        val digest = MessageDigest.getInstance("SHA-256")
        file.inputStream().use { input ->
            val buffer = ByteArray(65_536)
            var count = input.read(buffer)
            while (count != -1) {
                digest.update(buffer, 0, count)
                count = input.read(buffer)
            }
        }
        require(digest.digest().joinToString("") { "%02x".format(it) } == expected) {
            "Checksum mismatch for ${file.name}"
        }
    }

    fun loadCpu(graph: File, expected: String): Net {
        checkDigest(graph, expected)
        return Dnn.readNetFromONNX(graph.path).apply {
            check(!empty()) { "Could not load ${graph.name}" }
            setPreferableBackend(Dnn.DNN_BACKEND_OPENCV)
            setPreferableTarget(Dnn.DNN_TARGET_CPU)
        }
    }

    fun imagenetTensor(rgb: ByteArray, side: Int): Mat {
        val pixels = side * side
        require(rgb.size == pixels * 3) { "Aligned RGB tensor dimensions do not match" }
        val nchw = FloatArray(rgb.size)
        for (channel in 0..2) {
            for (pixel in 0 until pixels) {
                val code = rgb[pixel * 3 + channel].toInt() and 255
                nchw[channel * pixels + pixel] = (code / 255f - mean[channel]) / std[channel]
            }
        }
        val tensor = Mat(intArrayOf(1, 3, side, side), CvType.CV_32F)
        if (tensor.put(intArrayOf(0, 0, 0, 0), nchw) != nchw.size * Float.SIZE_BYTES) {
            tensor.release()
            error("Could not write RGB tensor")
        }
        return tensor
    }
}

/** Pinned full-frame parser used by the Python research mask pipeline. */
internal class ResearchFaceParser(graph: File) {
    private val net = ResearchVision.loadCpu(graph, "0d9bd318e46987c3bdbfacae9e2c0f461cae1c6ac6ea6d43bbe541a91727e33f")

    init { check("output" in net.unconnectedOutLayersNames) }

    fun categories(bgr: Mat): ByteArray {
        val side = 512
        val pixels = side * side
        val rgb = Mat()
        val labels = Mat(side, side, CvType.CV_8UC1)
        val resized = Mat()
        try {
            Imgproc.cvtColor(bgr, rgb, Imgproc.COLOR_BGR2RGB)
            Imgproc.resize(rgb, rgb, Size(side.toDouble(), side.toDouble()), 0.0, 0.0, Imgproc.INTER_LINEAR)
            val channels = ByteArray(pixels * 3)
            check(rgb.get(0, 0, channels) == channels.size)
            val input = ResearchVision.imagenetTensor(channels, side)
            val categories = ByteArray(pixels)
            try {
                net.setInput(input)
                val logits = net.forward("output")
                try {
                    check(logits.dims() == 4 && logits.size(0) == 1 && logits.size(1) == 19 &&
                        logits.size(2) == side && logits.size(3) == side && logits.type() == CvType.CV_32F)
                    val best = FloatArray(pixels) { Float.NEGATIVE_INFINITY }
                    val values = FloatArray(pixels)
                    for (label in 0 until 19) {
                        check(logits.get(intArrayOf(0, label, 0, 0), values) == pixels * Float.SIZE_BYTES)
                        for (i in values.indices) {
                            val value = values[i]
                            check(value.isFinite()) { "Nonfinite face parser logits" }
                            if (value > best[i]) {
                                best[i] = value
                                categories[i] = label.toByte()
                            }
                        }
                    }
                } finally {
                    logits.release()
                }
            } finally {
                input.release()
            }
            check(labels.put(0, 0, categories) == categories.size)
            Imgproc.resize(labels, resized, Size(bgr.cols().toDouble(), bgr.rows().toDouble()),
                0.0, 0.0, Imgproc.INTER_NEAREST)
            return ByteArray(bgr.rows() * bgr.cols()).also { check(resized.get(0, 0, it) == it.size) }
        } finally {
            resized.release()
            labels.release()
            rgb.release()
        }
    }
}
