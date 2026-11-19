package com.example.skintonecorrection

import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.example.skintonecorrection.data.FaceLandmarks
import com.example.skintonecorrection.data.OnDevicePipeline
import com.google.mediapipe.framework.image.ByteBufferImageBuilder
import com.google.mediapipe.framework.image.MPImage
import com.google.mediapipe.tasks.core.BaseOptions
import com.google.mediapipe.tasks.core.Delegate
import com.google.mediapipe.tasks.vision.core.RunningMode
import com.google.mediapipe.tasks.vision.facelandmarker.FaceLandmarker
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
import org.opencv.imgproc.Imgproc
import java.io.DataInputStream
import java.io.File
import java.nio.ByteBuffer
import java.security.MessageDigest
import kotlin.math.hypot

@RunWith(AndroidJUnit4::class)
class FaceLandmarkInputParityTest {
    @Test fun comparesPackedRgbAndBitmapForTheSameCrop() {
        val registry = InstrumentationRegistry.getInstrumentation()
        assumeTrue(InstrumentationRegistry.getArguments().getString("landmarkInputFixture") == "true")
        assertTrue(OpenCVLoader.initLocal())
        val context = registry.targetContext
        val folder = File(context.filesDir, "faceocc_geometry")
        val output = File(folder, "input_result.txt").apply { writeText("") }
        val task = context.assets.open(OnDevicePipeline.ASSETS + "face_landmarker.task").use { it.readBytes() }
        fun sha(bytes: ByteArray) = MessageDigest.getInstance("SHA-256").digest(bytes).joinToString("") { "%02x".format(it) }
        assertEquals("64184e229b263107bc2b804c6625db1341ff2bb731874b0bcc2fe6544e0bc9ff", sha(task))
        val model = ByteBuffer.allocateDirect(task.size).apply { put(task); rewind() }
        val options = FaceLandmarker.FaceLandmarkerOptions.builder()
            .setBaseOptions(BaseOptions.builder().setModelAssetBuffer(model).setDelegate(Delegate.CPU).build())
            .setRunningMode(RunningMode.IMAGE).setNumFaces(1).setMinFaceDetectionConfidence(.5f).build()
        FaceLandmarker.createFromOptions(context, options).use { landmarker ->
            for (name in listOf("test1", "test2")) {
                DataInputStream(File(folder, "$name.bin").inputStream().buffered()).use { data ->
                    val box = Rect(data.readInt(), data.readInt(), data.readInt(), data.readInt())
                    data.readDouble()
                    val expected = List(478) { Point(data.readDouble(), data.readDouble()) }
                    repeat(6) { data.readDouble() }
                    val bytes = ByteArray(256 * 256 * 3).apply { data.readFully(this) }
                    val frame = Mat(256, 256, CvType.CV_8UC3)
                    try {
                        assertEquals(bytes.size, frame.put(0, 0, bytes))
                        val bitmap = requireNotNull(FaceLandmarks.detect(context, frame, box, task))
                        assertEquals(0.0, bitmap.marginFraction, 0.0)
                        val crop = frame.submat(box)
                        val rgbMat = Mat()
                        val rgb = try {
                            Imgproc.cvtColor(crop, rgbMat, Imgproc.COLOR_BGR2RGB)
                            ByteArray(box.width * box.height * 3).also { assertEquals(it.size, rgbMat.get(0, 0, it)) }
                        } finally {
                            rgbMat.release()
                            crop.release()
                        }
                        val packed = ByteBuffer.allocateDirect(rgb.size).apply { put(rgb); rewind() }
                        val rgbPoints = ByteBufferImageBuilder(packed, box.width, box.height, MPImage.IMAGE_FORMAT_RGB)
                            .build().use { image -> landmarker.detect(image).faceLandmarks().single() }
                            .map { Point(it.x().toDouble() * box.width + box.x, it.y().toDouble() * box.height + box.y) }
                        fun drift(a: List<Point>, b: List<Point>): Double {
                            assertEquals(a.size, b.size)
                            return a.indices.maxOf { hypot(a[it].x - b[it].x, a[it].y - b[it].y) }
                        }
                        output.appendText("$name crop_rgb_sha256=${sha(rgb)} " +
                            "packed_vs_bitmap=${drift(rgbPoints, bitmap.points)} " +
                            "packed_vs_python=${drift(rgbPoints, expected)} bitmap_vs_python=${drift(bitmap.points, expected)}\n")
                    } finally {
                        frame.release()
                    }
                }
            }
        }
        assertEquals(task.size, model.capacity())
    }
}
