package com.example.skintonecorrection

import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.example.skintonecorrection.data.FaceLandmarks
import com.example.skintonecorrection.data.FaceOccGeometry
import com.example.skintonecorrection.data.FaceOccResearchModel
import com.example.skintonecorrection.data.OnDevicePipeline
import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Assume.assumeTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.opencv.android.OpenCVLoader
import org.opencv.core.CvType
import org.opencv.core.Mat
import org.opencv.core.Point
import org.opencv.core.Rect
import java.io.DataInputStream
import java.io.File
import java.security.MessageDigest
import kotlin.math.abs
import kotlin.math.hypot

@RunWith(AndroidJUnit4::class)
class FaceOccGeometryParityTest {
    @Test fun alignsAndReprojectsToAnalysisFrame() {
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val graphSha = InstrumentationRegistry.getArguments().getString("faceOccGraphSha")
        assumeTrue("Requires the private geometry fixture", graphSha != null)
        assertTrue(OpenCVLoader.initLocal())
        val folder = File(context.filesDir, "faceocc_geometry")
        val model = FaceOccResearchModel.load(File(folder, "faceocc.onnx"), requireNotNull(graphSha))
        val template = DataInputStream(File(folder, "template.bin").inputStream()).use { data ->
            DoubleArray(15) { data.readDouble() }.also { assertEquals(-1, data.read()) }
        }
        val landmarker = context.assets.open(OnDevicePipeline.ASSETS + "face_landmarker.task").use { it.readBytes() }
        val landmarkerSha = MessageDigest.getInstance("SHA-256").digest(landmarker).joinToString("") { "%02x".format(it) }
        assertEquals("64184e229b263107bc2b804c6625db1341ff2bb731874b0bcc2fe6544e0bc9ff", landmarkerSha)
        val output = File(folder, "result.txt").apply { writeText("") }
        val pixels = FaceOccGeometry.SIDE * FaceOccGeometry.SIDE
        val maskDifferences = mutableListOf<Int>()
        for (name in listOf("test1", "test2")) {
            val frame = Mat(256, 256, CvType.CV_8UC3)
            try {
                DataInputStream(File(folder, "$name.bin").inputStream().buffered()).use { data ->
                    val box = Rect(data.readInt(), data.readInt(), data.readInt(), data.readInt())
                    val margin = data.readDouble()
                    val points = List(478) { Point(data.readDouble(), data.readDouble()) }
                    val matrix = DoubleArray(6) { data.readDouble() }
                    fun bytes(size: Int) = ByteArray(size).also { data.readFully(it) }
                    assertEquals(pixels * 3, frame.put(0, 0, bytes(pixels * 3)))
                    val rgb = bytes(pixels * 3)
                    val expectedMask = bytes(pixels)
                    assertEquals(-1, data.read())
                    val aligned = FaceOccGeometry.align(frame, points, template)
                    assertArrayEquals(matrix, aligned.matrix, 1e-8)
                    val rgbDifferences = rgb.indices.count { rgb[it] != aligned.rgb[it] }
                    val maxRgbDelta = rgb.indices.maxOf { abs((rgb[it].toInt() and 255) - (aligned.rgb[it].toInt() and 255)) }
                    val actualMask = FaceOccGeometry.reproject(model.logits(aligned.rgb), aligned.matrix, 256, 256)
                    val savedMaskDifferences = actualMask.indices.count { actualMask[it] != expectedMask[it] }

                    val detection = requireNotNull(FaceLandmarks.detect(context, frame, box, landmarker))
                    if (margin.isFinite()) assertEquals(margin, detection.marginFraction, 0.0)
                    assertEquals(points.size, detection.points.size)
                    val liveAligned = FaceOccGeometry.align(frame, detection.points, template)
                    val liveLogits = model.logits(liveAligned.rgb)
                    val liveMask = FaceOccGeometry.reproject(liveLogits, liveAligned.matrix, 256, 256)
                    val moved = detection.points.indices.maxOf {
                        hypot(detection.points[it].x - points[it].x, detection.points[it].y - points[it].y)
                    }
                    val differences = liveMask.indices.count { liveMask[it] != expectedMask[it] }
                    assertTrue(liveMask.any { it != 0.toByte() })
                    output.appendText("$name aligned_rgb_differences=$rgbDifferences max_rgb_delta=$maxRgbDelta " +
                        "saved_landmark_mask_mismatches=$savedMaskDifferences android_landmark_max_drift=$moved " +
                        "android_landmark_mask_mismatches=$differences margin=${detection.marginFraction}\n")
                    val savedLogitsFile = File(folder, "${name}_logits.bin")
                    if (savedLogitsFile.isFile) {
                        val savedLogits = DataInputStream(savedLogitsFile.inputStream().buffered()).use { input ->
                            FloatArray(pixels) { input.readFloat() }.also { assertEquals(-1, input.read()) }
                        }
                        val sameRgb = model.logits(rgb)
                        fun mismatches(logits: FloatArray, transform: DoubleArray): Int {
                            val mask = FaceOccGeometry.reproject(logits, transform, 256, 256)
                            return mask.indices.count { mask[it] != expectedMask[it] }
                        }
                        val signs = sameRgb.indices.count { (sameRgb[it] > 0f) != (savedLogits[it] > 0f) }
                        val maxLogitDelta = sameRgb.indices.maxOf { abs(sameRgb[it] - savedLogits[it]) }
                        val liveRgbDifferences = rgb.indices.count { rgb[it] != liveAligned.rgb[it] }
                        output.appendText("$name saved_logits_saved_matrix=${mismatches(savedLogits, matrix)} " +
                            "saved_logits_device_matrix=${mismatches(savedLogits, aligned.matrix)} " +
                            "saved_rgb_device_logits=${mismatches(sameRgb, matrix)} sign_differences=$signs " +
                            "max_logit_delta=$maxLogitDelta live_rgb_differences=$liveRgbDifferences " +
                            "live_logits_saved_matrix=${mismatches(liveLogits, matrix)}\n")
                    }
                    maskDifferences.add(savedMaskDifferences + differences)
                }
            } finally {
                frame.release()
            }
        }
        assertEquals("Visibility mask mismatches by fixture; see result.txt", listOf(0, 0), maskDifferences)
    }
}
