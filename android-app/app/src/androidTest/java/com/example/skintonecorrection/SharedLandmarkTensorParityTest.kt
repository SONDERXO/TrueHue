package com.example.skintonecorrection

import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.example.skintonecorrection.data.ResearchVision
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Assume.assumeTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.opencv.android.OpenCVLoader
import org.opencv.core.Core
import org.opencv.core.CvType
import org.opencv.core.Mat
import org.opencv.dnn.Dnn
import java.io.DataInputStream
import java.io.File
import kotlin.math.abs

/** Checks that the same graph and tensor yield the same values without the Tasks wrappers. */
@RunWith(AndroidJUnit4::class)
class SharedLandmarkTensorParityTest {
    private data class Graph(val name: String, val sha: String, val side: Int,
                            val outputs: List<String>, val shapes: List<List<Int>>)

    @Test fun comparesClassicCpuGraphOutputsWithPython() {
        assumeTrue(InstrumentationRegistry.getArguments().getString("sharedLandmarkFixture") == "true")
        assertTrue(OpenCVLoader.initLocal())
        val folder = File(InstrumentationRegistry.getInstrumentation().targetContext.filesDir, "shared_landmark")
        val output = File(folder, "result.txt").apply { writeText("") }
        val graphs = listOf(
            Graph("face_detector", "b4578f35940bf5a1a655214a1cce5cab13eba73c1297cd78e1a04c2380b0152f",
                128, listOf("regressors", "classificators"), listOf(listOf(1, 896, 16), listOf(1, 896, 1))),
            Graph("face_landmarks_detector", "c7d54204ce0448474c7f3fa9af494787c0965cbdd6f20fc72867e43046bd43d5",
                256, listOf("Identity", "Identity_1", "Identity_2"), listOf(listOf(1, 1434, 1, 1), listOf(1, 1, 1, 1), listOf(1, 1)))
        )
        var totalMismatches = 0
        val threads = Core.getNumThreads()
        Core.setNumThreads(1)
        try {
            for (graph in graphs) {
                val model = File(folder, "${graph.name}.tflite")
                ResearchVision.checkDigest(model, graph.sha)
                val net = Dnn.readNetFromTFLite(model.path, Dnn.ENGINE_CLASSIC)
                net.setPreferableBackend(Dnn.DNN_BACKEND_OPENCV)
                net.setPreferableTarget(Dnn.DNN_TARGET_CPU)
                net.enableFusion(false)
                net.enableWinograd(false)
                for (case in listOf("adjusted", "preserved")) {
                    val input = Mat(intArrayOf(1, 3, graph.side, graph.side), CvType.CV_32F)
                    val actual = mutableListOf<Mat>()
                    try {
                        val fixture = File(folder, "${graph.name}_$case.bin")
                        DataInputStream(fixture.inputStream().buffered()).use { data ->
                            val tensor = FloatArray(3 * graph.side * graph.side) { data.readFloat() }
                            assertEquals(tensor.size * Float.SIZE_BYTES, input.put(intArrayOf(0, 0, 0, 0), tensor))
                            net.setInput(input)
                            net.forward(actual, graph.outputs)
                            assertEquals(graph.outputs.size, actual.size)
                            for ((index, mat) in actual.withIndex()) {
                                val shape = List(mat.dims()) { mat.size(it) }
                                assertEquals(graph.shapes[index], shape)
                                val values = FloatArray(shape.reduce(Int::times))
                                assertEquals(values.size * Float.SIZE_BYTES, mat.get(IntArray(shape.size), values))
                                var different = 0
                                var maxDelta = 0f
                                for (value in values) {
                                    val expected = data.readFloat()
                                    assertTrue(value.isFinite())
                                    if (value.toRawBits() != expected.toRawBits()) different++
                                    maxDelta = maxOf(maxDelta, abs(value - expected))
                                }
                                totalMismatches += different
                                output.appendText("${graph.name} $case ${graph.outputs[index]} " +
                                    "values=${values.size} different=$different max_delta=$maxDelta\n")
                            }
                            assertEquals(-1, data.read())
                        }
                    } finally {
                        actual.forEach(Mat::release)
                        input.release()
                    }
                }
            }
        } finally {
            Core.setNumThreads(threads)
        }
        assertEquals("Shared runtime output bit mismatches; see result.txt", 0, totalMismatches)
    }
}
