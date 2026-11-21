package com.example.skintonecorrection.data

import com.example.skintonecorrection.R
import org.opencv.core.CvType
import org.opencv.core.Mat
import org.opencv.core.MatOfInt
import org.opencv.core.MatOfPoint
import org.opencv.core.MatOfPoint2f
import org.opencv.core.Point
import org.opencv.core.Rect
import org.opencv.core.Scalar
import org.opencv.core.Size
import org.opencv.geometry.Geometry
import org.opencv.imgproc.Imgproc
import kotlin.math.abs
import kotlin.math.ceil

enum class GlassesChoice { CLEAR, OPAQUE, UNCERTAIN, NONE }

internal class GlassesChoiceRequired : IllegalArgumentException("Choose how to handle detected glasses.")

/** The 256 px Python WB314 support rules, with separate measurement and application. */
internal object ResearchMaskRules {
    private const val SIDE = FaceOccGeometry.SIDE
    private const val PIXELS = SIDE * SIDE
    private const val RASTER_SCALE = 4
    private const val DIST_L2 = 2 // OpenCV distance type, omitted from the Android Java constants.
    private val oval = intArrayOf(10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288,
        397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162,
        21, 54, 103, 67, 109)
    private val featurePolygons = listOf(
        intArrayOf(362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398),
        intArrayOf(33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246),
        intArrayOf(70, 63, 105, 66, 107, 55, 65, 52, 53, 46),
        intArrayOf(336, 296, 334, 293, 300, 276, 283, 282, 295, 285),
        intArrayOf(61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291, 375, 321, 405, 314, 17, 84, 181, 91, 146)
    )
    private val nasalPolygons = listOf(intArrayOf(98, 97, 2, 94, 19, 64), intArrayOf(327, 326, 2, 94, 19, 294))

    data class Result(val baseline: ByteArray, val measurement: ByteArray, val alpha: DoubleArray,
                      val protected: BooleanArray)

    fun build(categories: ByteArray, landmarks: List<Point>, visible: ByteArray, glasses: GlassesChoice,
              applicationVisibility: ByteArray = visible): Result {
        require(categories.size == PIXELS && categories.all { it in 0..18 })
        require(visible.size == PIXELS && visible.all { it == 0.toByte() || it == 255.toByte() })
        require(applicationVisibility.size == PIXELS && applicationVisibility.indices.all {
            applicationVisibility[it] == 0.toByte() || applicationVisibility[it] == visible[it]
        })
        require(landmarks.size >= 468 && landmarks.all { abs(it.x) <= 1e6 && abs(it.y) <= 1e6 })
        val outline = polygon(landmarks, oval, 1.0, false, 128)
        if (outline.none { it }) {
            throw PhotoProcessingException(R.string.error_face_unclear, "Face outline is outside the image")
        }
        val anatomical = featurePolygons.map { polygon(landmarks, it, 1.0, true, 1) }
        val nasalPolygonsRaster = nasalPolygons.map { polygon(landmarks, it, .1, true, 1) }
        val nasal = dilate(BooleanArray(PIXELS) { i -> nasalPolygonsRaster.any { it[i] } }, 1, Imgproc.MORPH_RECT)
        val skin = BooleanArray(PIXELS) { categories[it] == 1.toByte() || categories[it] == 10.toByte() }
        val associated = attached(skin, outline)
        val facial = BooleanArray(PIXELS) { i -> associated[i] && anatomical.none { it[i] } }
        requireMeasurement(facial)
        val baseline = BooleanArray(PIXELS) { facial[it] && !nasal[it] }
        requireMeasurement(baseline)
        val measurement = BooleanArray(PIXELS) { baseline[it] && visible[it] != 0.toByte() }
        requireMeasurement(measurement)

        // Neck association and blending width are based on the pre-FaceOcc, nostril-guarded mask.
        val bounds = bounds(baseline)
        val neck = associatedNeck(baseline, categories, bounds)
        val support = fillHoles(BooleanArray(PIXELS) { outline[it] || baseline[it] || neck[it] })
        val veto = BooleanArray(PIXELS) { i ->
            val face = outline[i] || (support[i] && !neck[i])
            protectedClass(categories[i].toInt()) || (face && applicationVisibility[i] == 0.toByte())
        }
        if (glasses == GlassesChoice.CLEAR) applyClearLenses(veto, categories, support, outline)
        val selected = BooleanArray(PIXELS) { support[it] && !veto[it] }
        val ears = BooleanArray(PIXELS) { (categories[it] == 7.toByte() || categories[it] == 8.toByte()) && !veto[it] }
        val selectedWithEars = attached(BooleanArray(PIXELS) { selected[it] || ears[it] }, selected)
        if (selectedWithEars.none { it }) {
            throw PhotoProcessingException(R.string.error_face_covered, "No correction support remains after protection")
        }
        val width = maxOf(2, ceil(bounds.width * .03).toInt())
        val distance = distances(selectedWithEars)
        val alpha = DoubleArray(PIXELS) { i ->
            val t = (distance[i] / width).coerceIn(0f, 1f).toDouble()
            if (selectedWithEars[i]) t * t * (3 - 2 * t) else 0.0
        }
        check(veto.indices.none { veto[it] && alpha[it] > 0.0 })
        return Result(binary(baseline), binary(measurement), alpha, veto)
    }

    fun requireGlassesChoice(categories: ByteArray, face: Rect, glasses: GlassesChoice) {
        if (glasses != GlassesChoice.UNCERTAIN) return
        for (y in face.y until face.y + face.height) {
            for (x in face.x until face.x + face.width) {
                if (categories[y * SIDE + x] == 6.toByte()) throw GlassesChoiceRequired()
            }
        }
    }

    private fun requireMeasurement(mask: BooleanArray) {
        if (mask.count { it } < 1_000) {
            throw PhotoProcessingException(R.string.error_face_covered, "Insufficient facial measurement support")
        }
    }

    private fun protectedClass(label: Int) = when (label) {
        0, 6, 9, 15, 16, 17, 18 -> true
        else -> false
    }

    private fun applyClearLenses(veto: BooleanArray, categories: ByteArray, support: BooleanArray, outline: BooleanArray) {
        val envelope = fillHoles(BooleanArray(PIXELS) { categories[it] == 6.toByte() })
        val distance = distances(envelope)
        for (i in veto.indices) {
            val label = categories[i].toInt()
            val lens = distance[i] > 2f && (label in 1..6 || label == 10) && outline[i] && support[i]
            val rim = envelope[i] && distance[i] <= 2f
            veto[i] = (veto[i] && !lens) || rim
        }
    }

    private data class Bounds(val left: Int, val right: Int, val top: Int, val bottom: Int) {
        val width get() = right - left
        val height get() = bottom - top
    }

    private fun bounds(mask: BooleanArray): Bounds {
        var left = SIDE
        var right = 0
        var top = SIDE
        var bottom = 0
        for (i in mask.indices) {
            if (mask[i]) {
                val x = i % SIDE
                val y = i / SIDE
                left = minOf(left, x)
                right = maxOf(right, x + 1)
                top = minOf(top, y)
                bottom = maxOf(bottom, y + 1)
            }
        }
        return Bounds(left, right, top, bottom)
    }

    private fun associatedNeck(face: BooleanArray, categories: ByteArray, box: Bounds): BooleanArray {
        val mid = box.top + box.height / 2
        val radius = maxOf(1, ceil(box.width * .1).toInt())
        val attachment = dilate(BooleanArray(PIXELS) { face[it] && it / SIDE >= mid }, radius, Imgproc.MORPH_ELLIPSE)
        val bottom = minOf(SIDE, box.bottom + box.height)
        val predicted = BooleanArray(PIXELS) { i ->
            categories[i] == 14.toByte() && !face[i] && i % SIDE in box.left until box.right && i / SIDE in mid until bottom
        }
        return attached(predicted, attachment)
    }

    private fun polygon(landmarks: List<Point>, indices: IntArray, minArea: Double, hull: Boolean,
                        threshold: Int): BooleanArray {
        val vertices = indices.map { landmarks[it] }.toTypedArray()
        val contour = MatOfPoint2f(*vertices)
        val high = MatOfPoint(*vertices.map { Point(Math.rint(it.x * RASTER_SCALE), Math.rint(it.y * RASTER_SCALE)) }.toTypedArray())
        val hullIndices = MatOfInt()
        val raster = Mat.zeros(SIDE * RASTER_SCALE, SIDE * RASTER_SCALE, CvType.CV_8UC1)
        val downsampled = Mat()
        try {
            if (abs(Geometry.contourArea(contour)) < minArea) {
                throw PhotoProcessingException(R.string.error_face_unclear, "Degenerate facial geometry")
            }
            var fill = high
            if (hull) {
                Geometry.convexHull(high, hullIndices)
                val points = high.toArray()
                fill = MatOfPoint(*hullIndices.toArray().map { points[it] }.toTypedArray())
            }
            try {
                Imgproc.fillPoly(raster, listOf(fill), Scalar(255.0))
                Imgproc.resize(raster, downsampled, Size(SIDE.toDouble(), SIDE.toDouble()), 0.0, 0.0, Imgproc.INTER_AREA)
                val data = ByteArray(PIXELS)
                check(downsampled.get(0, 0, data) == data.size)
                return BooleanArray(PIXELS) { (data[it].toInt() and 255) >= threshold }
            } finally {
                if (hull) fill.release()
            }
        } finally {
            downsampled.release()
            raster.release()
            hullIndices.release()
            high.release()
            contour.release()
        }
    }

    /** Select eight-connected components of foreground that intersect the seed. */
    private fun attached(foreground: BooleanArray, seed: BooleanArray): BooleanArray {
        val input = maskMat(foreground)
        val labels = Mat()
        try {
            val count = Imgproc.connectedComponents(input, labels, 8, CvType.CV_32S)
            val ids = IntArray(PIXELS)
            check(labels.get(0, 0, ids) == ids.size * Int.SIZE_BYTES)
            val keep = BooleanArray(count)
            for (i in ids.indices) if (seed[i] && ids[i] != 0) keep[ids[i]] = true
            return BooleanArray(PIXELS) { keep[ids[it]] }
        } finally {
            labels.release()
            input.release()
        }
    }

    private fun fillHoles(mask: BooleanArray): BooleanArray {
        val stride = SIDE + 2
        val data = ByteArray(stride * stride) { 1 }
        for (i in mask.indices) if (mask[i]) data[(i / SIDE + 1) * stride + i % SIDE + 1] = 0
        val padded = Mat(stride, stride, CvType.CV_8UC1)
        val floodMask = Mat()
        try {
            check(padded.put(0, 0, data) == data.size)
            Imgproc.floodFill(padded, floodMask, Point(0.0, 0.0), Scalar(2.0))
            check(padded.get(0, 0, data) == data.size)
            return BooleanArray(PIXELS) { data[(it / SIDE + 1) * stride + it % SIDE + 1] != 2.toByte() }
        } finally {
            floodMask.release()
            padded.release()
        }
    }

    private fun dilate(mask: BooleanArray, radius: Int, shape: Int): BooleanArray {
        val input = maskMat(mask)
        val side = (radius * 2 + 1).toDouble()
        val kernel = Imgproc.getStructuringElement(shape, Size(side, side))
        try {
            Imgproc.dilate(input, input, kernel)
            val result = ByteArray(PIXELS)
            check(input.get(0, 0, result) == result.size)
            return BooleanArray(PIXELS) { result[it] != 0.toByte() }
        } finally {
            kernel.release()
            input.release()
        }
    }

    private fun distances(mask: BooleanArray): FloatArray {
        val input = maskMat(mask)
        val result = Mat()
        try {
            Imgproc.distanceTransform(input, result, DIST_L2, Imgproc.DIST_MASK_PRECISE)
            return FloatArray(PIXELS).also { check(result.get(0, 0, it) == it.size * Float.SIZE_BYTES) }
        } finally {
            result.release()
            input.release()
        }
    }

    private fun binary(mask: BooleanArray) = ByteArray(mask.size) { if (mask[it]) 255.toByte() else 0 }

    private fun maskMat(mask: BooleanArray) = Mat(SIDE, SIDE, CvType.CV_8UC1).apply { put(0, 0, binary(mask)) }
}
