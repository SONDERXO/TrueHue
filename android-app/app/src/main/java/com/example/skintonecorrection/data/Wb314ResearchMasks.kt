package com.example.skintonecorrection.data

import android.content.Context
import android.graphics.Bitmap
import com.example.skintonecorrection.R
import org.json.JSONArray
import org.json.JSONObject
import org.opencv.android.Utils
import org.opencv.core.CvType
import org.opencv.core.Mat
import org.opencv.core.Point
import org.opencv.core.Rect
import org.opencv.core.Size
import org.opencv.imgproc.Imgproc
import org.opencv.objdetect.FaceDetectorYN
import java.io.DataInputStream
import java.io.File
import java.security.MessageDigest

/** Generates research masks from the same area-normalized BGR256 analysis image as WB314. */
internal class Wb314ResearchMasks(
    private val context: Context, folder: File, faceOccSha: String, private val landmarker: ByteArray
) {
    private val side = FaceOccGeometry.SIDE
    private val detector = File(folder, "yunet.onnx").let { graph ->
        ResearchVision.checkDigest(graph, "8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4")
        FaceDetectorYN.create(graph.path, "", Size(side.toDouble(), side.toDouble()), .85f, .3f, 5000)
    }
    private val template = File(folder, "template.bin").let { file ->
        ResearchVision.checkDigest(file, "3f4f5ef1f0f9ae1acbf4d4756aaa2c1b4a4de1287a3ed570c427e467db3cdd90")
        DataInputStream(file.inputStream()).use { input ->
            DoubleArray(15) { input.readDouble() }.also { check(input.read() == -1) }
        }
    }
    private val faceOcc = FaceOccResearchModel.load(File(folder, "faceocc.onnx"), faceOccSha)
    private val parser = ResearchFaceParser(File(folder, "parser.onnx"))

    init {
        val digest = MessageDigest.getInstance("SHA-256").digest(landmarker).joinToString("") { "%02x".format(it) }
        require(digest == "64184e229b263107bc2b804c6625db1341ff2bb731874b0bcc2fe6544e0bc9ff") {
            "Face landmarker checksum mismatch"
        }
    }

    data class Result(val faceBox: Rect, val categories: ByteArray, val visibility: ByteArray,
                      val masks: ResearchMaskRules.Result, val visionSide: Int)

    /** Reuse the loaded graphs on one inference thread. A missing stage fails before correction. */
    fun generate(bgr: Mat, glasses: GlassesChoice, protectUncertainBoundary: Boolean = false,
                 repairSkinEdges: Boolean = false, softenEdge: Boolean = false,
                 repairJaw: Boolean = false, originalForRetry: Bitmap? = null, attempts: JSONArray? = null): Result {
        require(bgr.type() == CvType.CV_8UC3 && bgr.rows() == side && bgr.cols() == side)
        fun analyze(vision: Mat): Result {
            val attempt = attempts?.let { log -> JSONObject().put("vision_side", vision.cols()).also { log.put(it) } }
            try {
                return analyze(bgr, vision, glasses, protectUncertainBoundary, repairSkinEdges, softenEdge, repairJaw, attempt)
            } catch (error: PhotoProcessingException) {
                attempt?.put("reason", error.message)
                throw error
            }
        }
        try {
            return analyze(bgr)
        } catch (error: PhotoProcessingException) {
            if (originalForRetry == null || !error.retryFaceAnalysis) throw error
        }
        val original = checkNotNull(originalForRetry)
        val largerSide = side * 2
        val bitmap = Bitmap.createScaledBitmap(original, largerSide, largerSide, true)
        val rgba = Mat()
        val vision = Mat()
        try {
            Utils.bitmapToMat(bitmap, rgba)
            Imgproc.cvtColor(rgba, vision, Imgproc.COLOR_RGBA2BGR)
            return analyze(vision)
        } finally {
            if (bitmap !== original) bitmap.recycle()
            rgba.release()
            vision.release()
        }
    }

    private fun analyze(bgr: Mat, vision: Mat, glasses: GlassesChoice,
                        protectUncertainBoundary: Boolean, repairSkinEdges: Boolean,
                        softenEdge: Boolean, repairJaw: Boolean, attempt: JSONObject?): Result {
        val visionSide = vision.cols()
        val detected = detectFace(vision)
        attempt?.put("face_width", detected.width)?.put("face_height", detected.height)
        val landmarks = FaceLandmarks.detect(context, vision, detected, landmarker)
            ?: throw PhotoProcessingException(R.string.error_face_unclear, "Required landmarks unavailable",
                retryFaceAnalysis = true)
        val scale = side.toDouble() / visionSide
        val face = if (visionSide == side) detected else Rect(
            (detected.x * scale).toInt(), (detected.y * scale).toInt(),
            (detected.width * scale).toInt().coerceAtLeast(1),
            (detected.height * scale).toInt().coerceAtLeast(1))
        val points = if (visionSide == side) landmarks.points
        else landmarks.points.map { Point(it.x * scale, it.y * scale) }
        val labels = parser.categories(vision)
        val categories = if (visionSide == side) labels else ByteArray(side * side) { i ->
            labels[(i / side) * visionSide * 2 + (i % side) * 2]
        }
        ResearchMaskRules.requireGlassesChoice(categories, face, glasses)
        val visibility = faceOcc.visibility(bgr, points, template, protectUncertainBoundary)
        val masks = ResearchMaskRules.build(categories, points, visibility.measurement,
            glasses, visibility.application, repairSkinEdges, softenEdge, if (repairJaw) bgr else null,
            recordMeasurement = attempt?.let { trace -> { key, count -> trace.put(key, count) } })
        return Result(face, categories, visibility.measurement, masks, visionSide)
    }

    private fun detectFace(bgr: Mat): Rect {
        val detected = Mat()
        try {
            val side = bgr.cols()
            detector.setInputSize(Size(side.toDouble(), side.toDouble()))
            detector.detect(bgr, detected)
            // Each output row is 15 scalar CV_32F entries, with confidence at column 14.
            val faces = (0 until detected.rows()).filter { row -> detected.get(row, 14)[0] >= .85f.toDouble() }
            if (faces.size != 1) {
                val message = if (faces.isEmpty()) R.string.error_no_face else R.string.error_multiple_faces
                throw PhotoProcessingException(message, "Expected one face, found ${faces.size}",
                    retryFaceAnalysis = faces.isEmpty())
            }
            val row = faces.single()
            val x = detected.get(row, 0)[0].toInt().coerceIn(0, side)
            val y = detected.get(row, 1)[0].toInt().coerceIn(0, side)
            val width = minOf(detected.get(row, 2)[0].toInt(), side - x).coerceAtLeast(1)
            val height = minOf(detected.get(row, 3)[0].toInt(), side - y).coerceAtLeast(1)
            if (x + width > side || y + height > side) {
                throw PhotoProcessingException(R.string.error_face_unclear, "Face box outside analysis frame")
            }
            return Rect(x, y, width, height)
        } finally {
            detected.release()
        }
    }
}
