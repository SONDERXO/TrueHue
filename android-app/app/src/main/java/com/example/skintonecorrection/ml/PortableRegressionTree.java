package com.example.skintonecorrection.ml;

import java.util.ArrayDeque;
import java.util.Arrays;

/** Platform-independent inference. Float32 inputs, float64 thresholds, <= routing. */
public final class PortableRegressionTree {
    public static final class Node {
        private final int feature, left, right;
        private final double threshold;
        private final double[] values;

        private Node(int feature, double threshold, int left, int right, double[] values) {
            this.feature = feature;
            this.threshold = threshold;
            this.left = left;
            this.right = right;
            this.values = values == null ? null : values.clone();
        }

        public static Node split(int feature, double threshold, int left, int right) {
            return new Node(feature, threshold, left, right, null);
        }

        public static Node leaf(double... values) {
            if (values == null) throw new IllegalArgumentException("Missing leaf values");
            return new Node(-1, 0, -1, -1, values);
        }
    }

    private final Node[] nodes;
    private final int featureCount, targetCount;

    public PortableRegressionTree(Node[] nodes, int featureCount, int targetCount) {
        if (nodes == null || nodes.length == 0 || featureCount <= 0 || targetCount <= 0)
            throw new IllegalArgumentException("Nonempty tree and positive schema widths required");
        this.nodes = nodes.clone();
        this.featureCount = featureCount;
        this.targetCount = targetCount;
        boolean[] seen = new boolean[nodes.length];
        ArrayDeque<Integer> pending = new ArrayDeque<>();
        pending.push(0);
        while (!pending.isEmpty()) {
            int index = pending.pop();
            if (index < 0 || index >= nodes.length || seen[index] || this.nodes[index] == null)
                throw new IllegalArgumentException("Invalid, cyclic or shared-child graph");
            seen[index] = true;
            Node node = this.nodes[index];
            if (node.values != null) {
                if (node.values.length != targetCount)
                    throw new IllegalArgumentException("Leaf target width mismatch");
                for (double value : node.values)
                    if (!Double.isFinite(value) || value <= 0)
                        throw new IllegalArgumentException("Finite positive targets required");
            } else {
                if (node.feature < 0 || node.feature >= featureCount || !Double.isFinite(node.threshold))
                    throw new IllegalArgumentException("Invalid split feature or threshold");
                pending.push(node.left);
                pending.push(node.right);
            }
        }
        for (boolean reachable : seen)
            if (!reachable) throw new IllegalArgumentException("Unreachable node");
    }

    public int leafId(double[] features) {
        if (features == null || features.length != featureCount)
            throw new IllegalArgumentException("Feature width mismatch");
        float[] input = new float[featureCount];
        for (int i = 0; i < featureCount; i++) {
            input[i] = (float) features[i];
            if (!Double.isFinite(features[i]) || !Float.isFinite(input[i]))
                throw new IllegalArgumentException("Nonfinite or overflowing float32 feature");
        }
        int index = 0;
        while (nodes[index].values == null) {
            Node node = nodes[index];
            index = (double) input[node.feature] <= node.threshold ? node.left : node.right;
        }
        return index;
    }

    public double[] predict(double[] features) {
        return Arrays.copyOf(nodes[leafId(features)].values, targetCount);
    }
}
