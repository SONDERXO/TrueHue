package com.example.skintonecorrection.ml;

import java.math.BigDecimal;
import java.math.RoundingMode;

/** First 281 WB314 inputs, in the frozen Python model's feature order. */
public final class Wb314ImageFeatures {
    public static final int DEFAULT_MINIMUM_MEASUREMENT_PIXELS = 1_000;
    private static final int PIXELS = 256 * 256;
    private static final float LAB_LIGHT_SCALE = 100f / 255f;

    private Wb314ImageFeatures() {}

    /** RGB and encoded OpenCV Lab share the same 256x256 grid and row order. */
    public static float[] extract(byte[] rgb, byte[] lab, byte[] measurement,
                                  double[] itaKnots, double[] mstKnots) {
        return extract(rgb, lab, measurement, itaKnots, mstKnots, DEFAULT_MINIMUM_MEASUREMENT_PIXELS);
    }

    static float[] extract(byte[] rgb, byte[] lab, byte[] measurement,
                           double[] itaKnots, double[] mstKnots, int minimumMeasurementPixels) {
        if (minimumMeasurementPixels <= 0 || minimumMeasurementPixels > DEFAULT_MINIMUM_MEASUREMENT_PIXELS) {
            throw new IllegalArgumentException("Invalid facial measurement minimum");
        }
        if (rgb.length != 3 * PIXELS || lab.length != rgb.length || measurement.length != PIXELS) {
            throw new IllegalArgumentException("Matching 256x256 RGB8, Lab8 and measurement required");
        }
        // Histograms support linear percentiles without sorting a copy of the image.
        int[][] channels = new int[3][256];
        int[] light = new int[256];
        int[] skinGreen = new int[256];
        long[] sums = new long[3];
        float[] skinLight = new float[PIXELS];
        int selected = 0, aSum = 0, bSum = 0, zero = 0, full = 0;
        for (int pixel = 0; pixel < PIXELS; pixel++) {
            int i = 3 * pixel;
            int r = rgb[i] & 255, g = rgb[i + 1] & 255, b = rgb[i + 2] & 255;
            int l = lab[i] & 255;
            channels[0][r]++;
            channels[1][g]++;
            channels[2][b]++;
            light[l]++;
            sums[0] += r;
            sums[1] += g;
            sums[2] += b;
            if (r == 0 || g == 0 || b == 0) zero++;
            if (r == 255 || g == 255 || b == 255) full++;
            int mask = measurement[pixel] & 255;
            if (mask == 255) {
                skinLight[selected++] = l * LAB_LIGHT_SCALE;
                aSum += (lab[i + 1] & 255) - 128;
                bSum += (lab[i + 2] & 255) - 128;
                skinGreen[g]++;
            } else if (mask != 0) {
                throw new IllegalArgumentException("Measurement mask must be binary 0/255");
            }
        }
        if (selected < minimumMeasurementPixels) {
            throw new IllegalArgumentException("Too little facial measurement support");
        }
        double lMean = round4(sumFloat32(skinLight, 0, selected) / selected);
        double aMean = round4((float) aSum / selected);
        double bMean = round4((float) bSum / selected);
        if (Math.abs(bMean) < 1e-6) throw new IllegalArgumentException("ITA is undefined");
        double ita = round4(Math.toDegrees(Math.atan((lMean - 50) / bMean)));

        float[] out = new float[281];
        out[0] = (float) lMean;
        out[1] = (float) aMean;
        out[2] = (float) bMean;
        out[3] = (float) ita;
        out[4] = (float) mst(ita, itaKnots, mstKnots);
        double gMean = (double) sums[1] / PIXELS;
        out[5] = (float) Math.log(((double) sums[0] / PIXELS + 1) / (gMean + 1));
        out[6] = (float) Math.log(((double) sums[2] / PIXELS + 1) / (gMean + 1));
        for (int i = 0; i < 3; i++) {
            double q = i == 0 ? 0.1 : i == 1 ? 0.5 : 0.9;
            out[7 + i] = (float) percentile(light, PIXELS, q, true);
            out[12 + i] = (float) percentile(skinGreen, selected, q, false);
        }
        out[11] = (float) ((double) full / PIXELS);
        out[10] = (float) ((double) zero / PIXELS);
        out[15] = (float) Math.log((percentile(skinGreen, selected, 0.9, false) + 1) /
                (percentile(skinGreen, selected, 0.1, false) + 1));
        for (int channel = 0; channel < 3; channel++) {
            int[] counts = channels[channel];
            int lo = 0, hi = 255;
            while (counts[lo] == 0) lo++;
            while (counts[hi] == 0) hi--;
            out[16 + 2 * channel] = gap(counts, lo, Math.min(127, hi));
            out[17 + 2 * channel] = gap(counts, Math.max(128, lo), hi);
        }
        joint(rgb, out);
        return out;
    }

    private static double round4(double value) {
        return new BigDecimal(value).setScale(4, RoundingMode.HALF_EVEN).doubleValue();
    }

    /** Match the blocking and float32 additions of the Python NumPy mean. */
    private static float sumFloat32(float[] values, int offset, int length) {
        if (length < 8) {
            float total = 0;
            for (int i = 0; i < length; i++) total += values[offset + i];
            return total;
        }
        if (length <= 128) {
            float[] sums = new float[8];
            System.arraycopy(values, offset, sums, 0, 8);
            int i = 8;
            for (; i <= length - 8; i += 8) {
                for (int slot = 0; slot < 8; slot++) sums[slot] += values[offset + i + slot];
            }
            float total = ((sums[0] + sums[1]) + (sums[2] + sums[3])) +
                    ((sums[4] + sums[5]) + (sums[6] + sums[7]));
            for (; i < length; i++) total += values[offset + i];
            return total;
        }
        int split = (length / 2) & ~7;
        return sumFloat32(values, offset, split) + sumFloat32(values, offset + split, length - split);
    }

    private static double mst(double ita, double[] xs, double[] ys) {
        if (xs.length == 0 || xs.length != ys.length) throw new IllegalArgumentException("Invalid MST knots");
        for (int i = 0; i < xs.length; i++) {
            if (!Double.isFinite(xs[i]) || !(ys[i] >= 1 && ys[i] <= 10) ||
                    (i > 0 && (xs[i] <= xs[i - 1] || ys[i] > ys[i - 1]))) {
                throw new IllegalArgumentException("Invalid MST knot order or value");
            }
        }
        if (ita <= xs[0]) return ys[0];
        for (int i = 1; i < xs.length; i++) {
            if (ita <= xs[i]) return ys[i - 1] + (ys[i] - ys[i - 1]) * (ita - xs[i - 1]) / (xs[i] - xs[i - 1]);
        }
        return ys[ys.length - 1];
    }

    private static double percentile(int[] counts, int size, double fraction, boolean labLight) {
        double index = (size - 1) * fraction;
        int lower = (int) index;
        int low = ranked(counts, lower), high = ranked(counts, Math.min(size - 1, lower + 1));
        double a = labLight ? low * LAB_LIGHT_SCALE : low;
        double b = labLight ? high * LAB_LIGHT_SCALE : high;
        double delta = labLight ? (float) (b - a) : b - a;
        double weight = index - lower;
        return weight < 0.5 ? a + weight * delta : b - (1 - weight) * delta;
    }

    private static int ranked(int[] counts, int rank) {
        for (int i = 0; i < counts.length; i++) {
            rank -= counts[i];
            if (rank < 0) return i;
        }
        throw new IllegalArgumentException("Percentile rank exceeds available pixels");
    }

    private static float gap(int[] counts, int lo, int hi) {
        if (lo > hi) return 0;
        int empty = 0;
        for (int i = lo; i <= hi; i++) if (counts[i] == 0) empty++;
        return (float) ((double) empty / (hi - lo + 1));
    }

    private static void joint(byte[] rgb, float[] out) {
        // Precalculate coordinates to accumulate in the same four passes as NumPy.
        int[] u = new int[PIXELS], v = new int[PIXELS];
        double[] wu = new double[PIXELS], wv = new double[PIXELS];
        int positive = 0, clipped = 0;
        for (int i = 0; i < rgb.length; i += 3) {
            int r = rgb[i] & 255, g = rgb[i + 1] & 255, b = rgb[i + 2] & 255;
            if (r == 0 || g == 0 || b == 0) continue;
            double logU = Math.log((double) r / g), logV = Math.log((double) b / g);
            if (Math.abs(logU) > 2 || Math.abs(logV) > 2) clipped++;
            double posU = (Math.min(2, Math.max(-2, logU)) + 2) * 3.75;
            double posV = (Math.min(2, Math.max(-2, logV)) + 2) * 3.75;
            u[positive] = (int) posU;
            v[positive] = (int) posV;
            wu[positive] = posU - u[positive];
            wv[positive] = posV - v[positive];
            positive++;
        }
        if (positive == 0) return;
        double[] histogram = new double[256];
        for (int a = 0; a <= 1; a++) for (int b = 0; b <= 1; b++) {
            for (int i = 0; i < positive; i++) {
                int cell = 16 * Math.min(15, u[i] + a) + Math.min(15, v[i] + b);
                histogram[cell] += (a == 0 ? 1 - wu[i] : wu[i]) * (b == 0 ? 1 - wv[i] : wv[i]);
            }
        }
        out[22] = 1;
        out[23] = (float) ((double) positive / PIXELS);
        out[24] = (float) ((double) clipped / positive);
        for (int i = 0; i < histogram.length; i++) out[25 + i] = (float) (histogram[i] / positive);
    }
}
