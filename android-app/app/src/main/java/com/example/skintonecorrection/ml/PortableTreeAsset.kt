package com.example.skintonecorrection.ml

import android.content.res.AssetManager
import org.json.JSONObject
import java.security.MessageDigest

/** Frozen development artifact only. This supplies neither MST nor image features. */
object PortableTreeAsset {
    private val featureNames = listOf("input_mean_l_star", "input_mean_a_star", "input_mean_b_star", "input_ita_degrees")
    private val targetNames = listOf("target_gamma", "target_red_gain", "target_blue_gain")

    private fun integer(node: JSONObject, key: String): Int {
        val value = node.get(key)
        require(value is Int || value is Long) { "Integer $key required" }
        val number = (value as Number).toLong()
        require(number in Int.MIN_VALUE.toLong()..Int.MAX_VALUE.toLong()) { "Integer $key overflows" }
        return number.toInt()
    }

    private fun number(value: Any): Double {
        require(value is Number) { "Numeric value required" }
        return value.toDouble().also { require(it.isFinite()) { "Finite value required" } }
    }

    fun load(assets: AssetManager): PortableRegressionTree {
        val bytes = assets.open("decision_tree.json").use { it.readBytes() }
        val expected = assets.open("decision_tree.sha256").bufferedReader().use { it.readText().trim() }
        return parse(bytes, expected)
    }

    internal fun parse(bytes: ByteArray, expected: String, expectedFeatures: List<String> = featureNames): PortableRegressionTree {
        val actual = MessageDigest.getInstance("SHA-256").digest(bytes).joinToString("") { "%02x".format(it) }
        require(expected.matches(Regex("[0-9a-f]{64}")) && actual == expected) { "Development tree checksum mismatch" }
        val payload = JSONObject(bytes.toString(Charsets.UTF_8))
        require(payload.getString("schema_version") == "truehue_regression_tree_v1")
        require(payload.getString("input_dtype") == "float32" && payload.getString("threshold_dtype") == "float64")
        require(payload.getString("comparison") == "<=" && integer(payload, "root") == 0)
        fun names(key: String): List<String> = payload.getJSONArray(key).let { a -> List(a.length()) { a.getString(it) } }
        require(names("feature_names") == expectedFeatures && names("target_names") == targetNames) { "Tree schema mismatch" }
        val source = payload.getJSONArray("nodes")
        val nodes = Array(source.length()) { i ->
            val node = source.getJSONObject(i)
            when (node.getString("kind")) {
                "split" -> PortableRegressionTree.Node.split(integer(node, "feature"), number(node.get("threshold")), integer(node, "left"), integer(node, "right"))
                "leaf" -> node.getJSONArray("values").let { a ->
                    PortableRegressionTree.Node.leaf(*DoubleArray(a.length()) { number(a.get(it)) })
                }
                else -> error("Unknown tree node kind")
            }
        }
        return PortableRegressionTree(nodes, expectedFeatures.size, targetNames.size)
    }
}
