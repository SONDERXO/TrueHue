package com.example.skintonecorrection.ml

import org.json.JSONObject
import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertEquals
import org.junit.Assert.assertThrows
import org.junit.Test
import java.security.MessageDigest

class PortableTreeAssetTest {
    private fun bytes() = requireNotNull(javaClass.classLoader!!.getResourceAsStream("decision_tree.json")).use { it.readBytes() }
    private fun checksum(bytes: ByteArray) = MessageDigest.getInstance("SHA-256").digest(bytes).joinToString("") { "%02x".format(it) }
    private fun modified(change: (JSONObject) -> Unit): ByteArray = JSONObject(bytes().toString(Charsets.UTF_8)).also(change).toString().toByteArray()
    private fun reject(change: (JSONObject) -> Unit) {
        val value = modified(change)
        assertThrows(IllegalArgumentException::class.java) { PortableTreeAsset.parse(value, checksum(value)) }
    }

    @Test fun packagedModelLoadsAndPredicts() {
        val data = bytes()
        val expected = requireNotNull(javaClass.classLoader!!.getResourceAsStream("decision_tree.sha256")).bufferedReader().use { it.readText().trim() }
        val tree = PortableTreeAsset.parse(data, expected)
        val input = doubleArrayOf(50.8105, 6.4101, 19.2249, 2.4141)
        assertEquals(4, tree.leafId(input))
        assertArrayEquals(doubleArrayOf(1.142857142857143, 1.157809331807554, 0.9252293736354574), tree.predict(input), 0.0)
    }

    @Test fun rejectsChangedAsset() {
        assertThrows(IllegalArgumentException::class.java) { PortableTreeAsset.parse(bytes(), "0".repeat(64)) }
    }
    @Test fun rejectsInvalidChecksumFormat() {
        assertThrows(IllegalArgumentException::class.java) { PortableTreeAsset.parse(bytes(), "not-a-hash") }
    }
    @Test fun rejectsWrongSchema() = reject { it.put("schema_version", "unknown") }
    @Test fun rejectsWrongNumericContract() = reject { it.put("input_dtype", "float64") }
    @Test fun rejectsWrongThresholdContract() = reject { it.put("threshold_dtype", "float32") }
    @Test fun rejectsWrongComparison() = reject { it.put("comparison", "<") }
    @Test fun rejectsFractionalRoot() = reject { it.put("root", 0.5) }
    @Test fun rejectsFractionalChild() = reject { it.getJSONArray("nodes").getJSONObject(0).put("left", 1.5) }
    @Test fun rejectsStringThreshold() = reject { it.getJSONArray("nodes").getJSONObject(0).put("threshold", "25.1744") }
    @Test fun rejectsWrongFeatureOrder() = reject { it.getJSONArray("feature_names").put(0, "input_ita_degrees") }
    @Test fun rejectsWrongTargetOrder() = reject { it.getJSONArray("target_names").put(0, "target_red_gain") }
    @Test fun rejectsCyclicGraph() = reject { it.getJSONArray("nodes").getJSONObject(0).put("left", 0) }
    @Test fun rejectsInvalidLeaf() = reject { it.getJSONArray("nodes").getJSONObject(1).getJSONArray("values").put(0, 0.0) }
}
