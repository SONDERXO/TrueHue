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
        // Above the observed positive logits at the four unstable visibility decisions.
        private const val APPLICATION_LOGIT_MARGIN = 1f / 32f
        fun load(graph: File, expectedSha: String) = FaceOccResearchModel(ResearchVision.loadCpu(graph, expectedSha))
    }

    data class Visibility(val measurement: ByteArray, val application: ByteArray)

    fun visibility(bgr: Mat, landmarks: List<Point>, template: DoubleArray,
                   protectUncertainBoundary: Boolean): Visibility {
        val aligned = FaceOccGeometry.align(bgr, landmarks, template)
        val scores = logits(aligned.rgb)
        val measurement = FaceOccGeometry.reproject(scores, aligned.matrix, bgr.cols(), bgr.rows())
        val application = if (protectUncertainBoundary) {
            FaceOccGeometry.reproject(scores, aligned.matrix, bgr.cols(), bgr.rows(), APPLICATION_LOGIT_MARGIN)
        } else measurement
        return Visibility(measurement, application)
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
