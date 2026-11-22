package com.example.skintonecorrection.data

import android.content.Context
import com.example.skintonecorrection.R
import org.opencv.core.CvType
import org.opencv.core.Mat
import org.opencv.core.Rect
import org.opencv.core.Size
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
                      val masks: ResearchMaskRules.Result)

    /** Reuse the loaded graphs on one inference thread. A missing stage fails before correction. */
    fun generate(bgr: Mat, glasses: GlassesChoice, protectUncertainBoundary: Boolean = false,
                 repairSkinEdges: Boolean = false, softenEdge: Boolean = false,
                 repairJaw: Boolean = false): Result {
        require(bgr.type() == CvType.CV_8UC3 && bgr.rows() == side && bgr.cols() == side)
        val face = detectFace(bgr)
        val landmarks = FaceLandmarks.detect(context, bgr, face, landmarker)
            ?: throw PhotoProcessingException(R.string.error_face_unclear, "Required landmarks unavailable")
        val categories = parser.categories(bgr)
        ResearchMaskRules.requireGlassesChoice(categories, face, glasses)
        val visibility = faceOcc.visibility(bgr, landmarks.points, template, protectUncertainBoundary)
        val masks = ResearchMaskRules.build(categories, landmarks.points, visibility.measurement,
            glasses, visibility.application, repairSkinEdges, softenEdge, if (repairJaw) bgr else null)
        return Result(face, categories, visibility.measurement, masks)
    }

    private fun detectFace(bgr: Mat): Rect {
        val detected = Mat()
        try {
            detector.detect(bgr, detected)
            // Each output row is 15 scalar CV_32F entries, with confidence at column 14.
            val faces = (0 until detected.rows()).filter { row -> detected.get(row, 14)[0] >= .85f.toDouble() }
            if (faces.size != 1) {
                val message = if (faces.isEmpty()) R.string.error_no_face else R.string.error_multiple_faces
                throw PhotoProcessingException(message, "Expected one face, found ${faces.size}")
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
