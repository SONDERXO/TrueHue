package com.example.skintonecorrection.data

import org.opencv.core.Core
import org.opencv.core.CvType
import org.opencv.core.Mat
import org.opencv.core.Point
import org.opencv.core.Scalar
import org.opencv.core.Size
import org.opencv.imgproc.Imgproc
import kotlin.math.hypot

// Adapts FaceOcc's MIT-licensed POS alignment. See docs/third-party/faceocc-LICENSE.txt.
internal object FaceOccGeometry {
    const val SIDE = 256
    private val alignedSize = Size(SIDE.toDouble(), SIDE.toDouble())
    data class Alignment(val rgb: ByteArray, val matrix: DoubleArray)

    /** Landmarks use whole-frame coordinates. Template rows use the pinned FaceOcc order. */
    fun align(bgr: Mat, landmarks: List<Point>, template: DoubleArray): Alignment {
        require(!bgr.empty() && bgr.type() == CvType.CV_8UC3)
        require(landmarks.size >= 468 && landmarks.all { it.x.isFinite() && it.y.isFinite() })
        require(template.size == 15 && template.all { it.isFinite() })
        fun midpoint(a: Point, b: Point) = Point((a.x + b.x) / 2, (a.y + b.y) / 2)
        val anchors = listOf(midpoint(landmarks[33], landmarks[133]),
            midpoint(landmarks[362], landmarks[263]), landmarks[1], landmarks[61], landmarks[291])
        fun distance(a: Point, b: Point) = hypot(a.x - b.x, a.y - b.y)
        require(distance(anchors[0], anchors[1]) >= 1 && distance(anchors[3], anchors[4]) >= 1)
        val matrix = alignmentMatrix(anchors, template, bgr.rows())
        val transform = Mat(2, 3, CvType.CV_64F)
        val aligned = Mat()
        val blurred = Mat()
        try {
            val scale = matrix[0]
            val left = matrix[2].toInt().coerceAtLeast(0)
            val top = matrix[5].toInt().coerceAtLeast(0)
            val right = ((bgr.cols() - 1) * scale + matrix[2]).toInt().coerceAtMost(SIDE - 1)
            val bottom = ((bgr.rows() - 1) * scale + matrix[5]).toInt().coerceAtMost(SIDE - 1)
            require(left < SIDE && top < SIDE && right >= 0 && bottom >= 0) { "No source overlap" }
            transform.put(0, 0, *matrix)
            Imgproc.warpAffine(bgr, aligned, transform, alignedSize, Imgproc.INTER_LINEAR, Core.BORDER_REFLECT_101)
            Imgproc.cvtColor(aligned, aligned, Imgproc.COLOR_BGR2RGB)
            Imgproc.blur(aligned, blurred, Size(10.0, 10.0))
            val rgb = ByteArray(SIDE * SIDE * 3)
            val border = ByteArray(rgb.size)
            check(aligned.get(0, 0, rgb) == rgb.size && blurred.get(0, 0, border) == border.size)
            for (y in 0 until SIDE) {
                for (x in 0 until SIDE) {
                    if (y < top || y >= bottom || x < left || x >= right) {
                        val offset = (y * SIDE + x) * 3
                        border.copyInto(rgb, offset, offset, offset + 3)
                    }
                }
            }
            return Alignment(rgb, matrix)
        } finally {
            blurred.release()
            aligned.release()
            transform.release()
        }
    }

    private fun alignmentMatrix(anchors: List<Point>, template: DoubleArray, height: Int): DoubleArray {
        val design = Mat(5, 4, CvType.CV_64F)
        val points = Mat(5, 2, CvType.CV_64F)
        val fit = Mat()
        val singular = Mat()
        val u = Mat()
        val vt = Mat()
        try {
            for (row in anchors.indices) {
                val offset = row * 3
                design.put(row, 0, template[offset], template[offset + 1], template[offset + 2], 1.0)
                points.put(row, 0, anchors[row].x, height - 1 - anchors[row].y)
            }
            Core.SVDecomp(design, singular, u, vt, Core.SVD_NO_UV)
            require(singular.get(3, 0)[0] > singular.get(0, 0)[0] * 10 * Math.ulp(1.0)) {
                "Degenerate FaceOcc template"
            }
            check(Core.solve(design, points, fit, Core.DECOMP_SVD))
            val values = DoubleArray(8)
            fit.get(0, 0, values)
            val scaleEstimate = (hypot(hypot(values[0], values[2]), values[4]) +
                hypot(hypot(values[1], values[3]), values[5])) / 2
            require(scaleEstimate.isFinite() && scaleEstimate > 1e-8) { "Degenerate face scale" }
            val scale = 116.0 / scaleEstimate
            return doubleArrayOf(scale, 0.0, 128 - values[6] * scale,
                0.0, scale, 128 - (height - values[7]) * scale)
        } finally {
            vt.release()
            u.release()
            singular.release()
            fit.release()
            points.release()
            design.release()
        }
    }

    /** Remove aligned padding, then inverse-warp the strict logit > 0 mask. */
    fun reproject(logits: FloatArray, matrix: DoubleArray, width: Int, height: Int): ByteArray {
        require(logits.size == SIDE * SIDE && logits.all { it.isFinite() })
        require(matrix.size == 6 && matrix.all { it.isFinite() })
        require(width > 0 && height > 0 && kotlin.math.abs(matrix[0] * matrix[4] - matrix[1] * matrix[3]) >= 1e-12)
        val validSource = Mat(height, width, CvType.CV_8UC1, Scalar(255.0))
        val transform = Mat(2, 3, CvType.CV_64F)
        val validAligned = Mat()
        val selected = Mat(SIDE, SIDE, CvType.CV_8UC1)
        val result = Mat()
        try {
            selected.put(0, 0, ByteArray(logits.size) { if (logits[it] > 0f) 255.toByte() else 0 })
            transform.put(0, 0, *matrix)
            Imgproc.warpAffine(validSource, validAligned, transform, alignedSize, Imgproc.INTER_NEAREST)
            Core.bitwise_and(selected, validAligned, selected)
            // A destination photo pixel is sampled at its forward-mapped aligned coordinate.
            Imgproc.warpAffine(selected, result, transform, Size(width.toDouble(), height.toDouble()),
                Imgproc.INTER_NEAREST or Imgproc.WARP_INVERSE_MAP)
            return ByteArray(width * height).also { check(result.get(0, 0, it) == it.size) }
        } finally {
            result.release()
            selected.release()
            validAligned.release()
            transform.release()
            validSource.release()
        }
    }
}
