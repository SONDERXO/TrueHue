package com.example.skintonecorrection.ml;

/** Linear-light WB314 correction for opaque ARGB pixels and mapped application alpha. */
public final class Wb314PixelRenderer {
    private static final double[] LINEAR_CODES = new double[256];

    static {
        for (int code = 0; code < LINEAR_CODES.length; code++) {
            double value = code / 255.0;
            LINEAR_CODES[code] = value <= 0.04045
                    ? value / 12.92 : Math.pow((value + 0.055) / 1.055, 2.4);
        }
    }

    private final double gamma;
    private final double exposure;
    private final double redBalance;
    private final double blueBalance;
    private final double chroma;
    private final boolean identity;

    public Wb314PixelRenderer(double gamma, double exposure, double redBalance,
                              double blueBalance, double chroma) {
        this.gamma = bounded(gamma, 4);
        this.exposure = bounded(exposure, 4);
        this.redBalance = bounded(redBalance, 4);
        this.blueBalance = bounded(blueBalance, 4);
        this.chroma = bounded(chroma, 1.5);
        identity = gamma == 1 && exposure == 1 && redBalance == 1
                && blueBalance == 1 && chroma == 1;
    }

    private static double bounded(double value, double upper) {
        if (!Double.isFinite(value) || value < 0.25 || value > upper) {
            throw new IllegalArgumentException("Invalid WB314 correction control");
        }
        return value;
    }

    public int render(int argb, double alpha, boolean protectedPixel) {
        if (!Double.isFinite(alpha) || alpha < 0 || alpha > 1 || (protectedPixel && alpha != 0)) {
            throw new IllegalArgumentException("Invalid correction support");
        }
        if ((argb >>> 24) != 255) {
            throw new IllegalArgumentException("Opaque ARGB input required");
        }
        if (alpha == 0 || identity) return argb;
        int red = (argb >>> 16) & 255;
        int green = (argb >>> 8) & 255;
        int blue = argb & 255;
        double r = LINEAR_CODES[red] * redBalance;
        double g = LINEAR_CODES[green];
        double b = LINEAR_CODES[blue] * blueBalance;
        double y = 0.2126 * r + 0.7152 * g + 0.0722 * b;
        if (y == 0) return argb;
        double light = Math.min(1, exposure * Math.pow(y, gamma));
        double dr = light * chroma * (r / y - 1);
        double dg = light * chroma * (g / y - 1);
        double db = light * chroma * (b / y - 1);
        double limit = Math.min(1, Math.min(limit(light, dr), Math.min(limit(light, dg), limit(light, db))));
        int rr = blend(red, light + limit * dr, alpha);
        int gg = blend(green, light + limit * dg, alpha);
        int bb = blend(blue, light + limit * db, alpha);
        return 0xff000000 | (rr << 16) | (gg << 8) | bb;
    }

    private static double limit(double light, double delta) {
        if (delta > 0) return (1 - light) / delta;
        if (delta < 0) return -light / delta;
        return 1;
    }

    private static int blend(int original, double linear, double alpha) {
        double value = Math.min(1, Math.max(0, linear));
        double encoded = value <= 0.0031308
                ? 12.92 * value : 1.055 * Math.pow(value, 1 / 2.4) - 0.055;
        return (int) Math.rint(255 * ((1 - alpha) * (original / 255.0) + alpha * encoded));
    }
}
