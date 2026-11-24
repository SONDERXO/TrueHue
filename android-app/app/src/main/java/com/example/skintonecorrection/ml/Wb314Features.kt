package com.example.skintonecorrection.ml

import org.opencv.core.CvType
import org.opencv.core.Mat
import org.opencv.imgproc.Imgproc

/** Assemble the frozen feature layout after RGB normalization and facial measurement. */
object Wb314Features {
    fun extract(
        rgb: Mat,
        measurement: ByteArray,
        itaKnots: DoubleArray,
        mstKnots: DoubleArray,
        whiteBalance: FloatArray,
        minimumMeasurementPixels: Int = Wb314ImageFeatures.DEFAULT_MINIMUM_MEASUREMENT_PIXELS
    ): DoubleArray {
        require(rgb.rows() == 256 && rgb.cols() == 256 && rgb.type() == CvType.CV_8UC3) {
            "256 x 256 RGB8 analysis image required"
        }
        require(whiteBalance.size == 33 && whiteBalance.all { it.isFinite() }) {
            "33 finite white-balance coefficients required"
        }
        val rgbBytes = ByteArray(256 * 256 * 3)
        check(rgb.get(0, 0, rgbBytes) == rgbBytes.size)
        val lab = Mat()
        try {
            Imgproc.cvtColor(rgb, lab, Imgproc.COLOR_RGB2Lab)
            val labBytes = ByteArray(rgbBytes.size)
            check(lab.get(0, 0, labBytes) == labBytes.size)
            val image = Wb314ImageFeatures.extract(rgbBytes, labBytes, measurement, itaKnots, mstKnots,
                minimumMeasurementPixels)
            return DoubleArray(314) { if (it < 281) image[it].toDouble() else whiteBalance[it - 281].toDouble() }
        } finally {
            lab.release()
        }
    }
}
