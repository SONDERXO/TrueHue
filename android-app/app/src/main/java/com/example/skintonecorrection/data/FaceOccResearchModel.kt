package com.example.skintonecorrection.data

import org.opencv.core.CvType
import org.opencv.core.Mat
import org.opencv.core.Point
import org.opencv.dnn.Net
import java.io.File

/** Local FaceOcc runner for aligned RGB pixels. Call from one inference thread. */
internal class FaceOccResearchModel private constructor(private val net: Net) {
    companion object {
        private const val SIDE = 256
        private const val PIXELS = SIDE * SIDE
        fun load(graph: File, expectedSha: String) = FaceOccResearchModel(ResearchVision.loadCpu(graph, expectedSha))
    }

    fun visibleMask(bgr: Mat, landmarks: List<Point>, template: DoubleArray): ByteArray {
        val aligned = FaceOccGeometry.align(bgr, landmarks, template)
        return FaceOccGeometry.reproject(logits(aligned.rgb), aligned.matrix, bgr.cols(), bgr.rows())
    }

    fun logits(rgb: ByteArray): FloatArray {
        val origin = intArrayOf(0, 0, 0, 0)
        val input = ResearchVision.imagenetTensor(rgb, SIDE)
        try {
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
