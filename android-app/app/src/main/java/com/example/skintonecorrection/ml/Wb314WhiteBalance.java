package com.example.skintonecorrection.ml;

import java.util.Arrays;

/**
 * Research implementation of the WB_sRGB feature calculation by Mahmoud Afifi et al.,
 * "When Color Constancy Goes Wrong" (CVPR 2019), revision 98340313.
 * Adapted from WB_sRGB under CC BY-NC-SA 4.0.
 * https://github.com/mahmoudnafifi/WB_sRGB
 */
public final class Wb314WhiteBalance {
    private static final int BINS = 60, HIST = 3 * BINS * BINS;
    private static final int QUERY = 55, COEFFICIENTS = 33, NEIGHBOURS = 25;
    private static final double STEP = 6.4 / BINS;
    private static final double MIN = -3.2 - STEP / 2;
    private static final double MAX = 3.2 - STEP / 2;

    private final float[] offset, projection, bank, mappings, bankNorms;

    /**
     * Arrays are row-major. Norms are float32 squared norms from the frozen NumPy bank.
     * Use the hash-checked arrays from the matching research release.
     */
    public Wb314WhiteBalance(float[] offset, float[] projection, float[] bank,
                             float[] mappings, float[] bankNorms) {
        int rows = bankNorms.length;
        if (offset.length != HIST || projection.length != HIST * QUERY ||
                rows <= NEIGHBOURS || bank.length != (long) rows * QUERY ||
                mappings.length != (long) rows * COEFFICIENTS) {
            throw new IllegalArgumentException("Invalid WB_sRGB asset dimensions");
        }
        this.offset = finiteCopy(offset);
        this.projection = finiteCopy(projection);
        this.bank = finiteCopy(bank);
        this.mappings = finiteCopy(mappings);
        this.bankNorms = finiteCopy(bankNorms);
    }

    private static float[] finiteCopy(float[] values) {
        for (float value : values) {
            if (!Float.isFinite(value)) throw new IllegalArgumentException("Nonfinite WB_sRGB asset");
        }
        return values.clone();
    }

    public float[] extract(byte[] rgb) {
        if (rgb.length != 256 * 256 * 3) {
            throw new IllegalArgumentException("256 x 256 RGB8 required");
        }
        double[] hist = histogram(rgb);
        double[] query = new double[QUERY];
        for (int i = 0; i < HIST; i++) {
            double centered = hist[i] - offset[i];
            int row = i * QUERY;
            for (int j = 0; j < QUERY; j++) query[j] += centered * projection[row + j];
        }
        double norm = 0;
        for (double value : query) norm += value * value;
        // Keep one extra neighbour to detect a tie at the selection boundary.
        double[] nearest = new double[NEIGHBOURS + 1];
        int[] indices = new int[nearest.length];
        Arrays.fill(nearest, Double.POSITIVE_INFINITY);
        for (int i = 0; i < bankNorms.length; i++) {
            double dot = 0;
            for (int j = 0; j < QUERY; j++) dot += query[j] * bank[i * QUERY + j];
            double distance = bankNorms[i] + norm - 2 * dot;
            if (!Double.isFinite(distance) || distance < 0) {
                throw new IllegalArgumentException("Invalid white-balance distance");
            }
            int k = NEIGHBOURS;
            if (distance >= nearest[k]) continue;
            while (k > 0 && distance < nearest[k - 1]) {
                nearest[k] = nearest[k - 1];
                indices[k] = indices[k - 1];
                k--;
            }
            nearest[k] = distance;
            indices[k] = i;
        }
        if (nearest[NEIGHBOURS - 1] == nearest[NEIGHBOURS]) {
            verifyTie(query, norm, indices[NEIGHBOURS], nearest[NEIGHBOURS]);
        }
        double[] weights = new double[NEIGHBOURS];
        double total = 0;
        for (int i = 0; i < weights.length; i++) {
            double distance = Math.sqrt(nearest[i]);
            weights[i] = Math.exp(-(distance * distance) / 0.125);
            total += weights[i];
        }
        if (!(total > 0)) throw new IllegalArgumentException("No usable white-balance weight");
        float[] result = new float[COEFFICIENTS];
        for (int j = 0; j < result.length; j++) {
            double value = 0;
            for (int i = 0; i < weights.length; i++) {
                value += (weights[i] / total) * mappings[indices[i] * COEFFICIENTS + j];
            }
            result[j] = (float) value;
        }
        return result;
    }

    private void verifyTie(double[] query, double norm, int reference, double boundary) {
        for (int i = 0; i < bankNorms.length; i++) {
            double dot = 0;
            for (int j = 0; j < QUERY; j++) dot += query[j] * bank[i * QUERY + j];
            if (bankNorms[i] + norm - 2 * dot != boundary) continue;
            for (int j = 0; j < COEFFICIENTS; j++) {
                if (mappings[i * COEFFICIENTS + j] != mappings[reference * COEFFICIENTS + j]) {
                    throw new IllegalArgumentException("Different white-balance mappings tie at selection boundary");
                }
            }
        }
    }

    private static double[] histogram(byte[] rgb) {
        int min = 255, max = 0;
        for (byte sample : rgb) {
            int code = sample & 255;
            min = Math.min(min, code);
            max = Math.max(max, code);
        }
        if (min == max) throw new IllegalArgumentException("No white-balance histogram support");
        double scale = 1.0 / (max - min);
        double[] codes = new double[256];
        for (int i = min; i <= max; i++) codes[i] = (i - min) * scale;
        double[] hist = new double[HIST];
        for (int i = 0; i < rgb.length; i += 3) {
            double r = codes[rgb[i] & 255], g = codes[rgb[i + 1] & 255], b = codes[rgb[i + 2] & 255];
            if (!(r > 0 && g > 0 && b > 0)) continue;
            double weight = Math.sqrt(r * r + g * g + b * b);
            add(hist, 0, r / b, r / g, weight);
            add(hist, 1, g / b, g / r, weight);
            add(hist, 2, b / g, b / r, weight);
        }
        for (int band = 0; band < 3; band++) {
            int first = band * BINS * BINS;
            int end = first + BINS * BINS;
            double total = 0;
            for (int i = first; i < end; i++) total += hist[i];
            if (!(total > 0)) throw new IllegalArgumentException("No white-balance histogram support");
            for (int i = first; i < end; i++) hist[i] = Math.sqrt(hist[i] / total);
        }
        return hist;
    }

    private static void add(double[] hist, int band, double u, double v, double weight) {
        int first = bin(Math.log(u)), second = bin(Math.log(v));
        if (first >= 0 && second >= 0) hist[(band * BINS + first) * BINS + second] += weight;
    }

    private static int bin(double value) {
        if (value < MIN || value > MAX) return -1;
        if (value == MAX) return BINS - 1;
        int index = Math.min(BINS - 1, (int) ((value - MIN) / STEP));
        if (value < MIN + index * STEP) index--;
        if (index < BINS - 1 && value >= MIN + (index + 1) * STEP) index++;
        return index;
    }
}
