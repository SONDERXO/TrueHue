package com.example.skintonecorrection.data

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class OriginalPhotoMemoryTest {
    @Test
    fun admitsFullSizeCameraImageWithRoomForTwoFrames() {
        val pixels = 4896L * 6528
        val required = 8L * pixels + 48L * 1024 * 1024
        assertTrue(fitsOriginalPhoto(pixels, required))
        assertFalse(fitsOriginalPhoto(pixels, required - 1))
    }

    @Test
    fun rejectsImagesThatStillExceedTheBudget() {
        assertFalse(fitsOriginalPhoto(8000L * 6000, 384L * 1024 * 1024))
        assertFalse(fitsOriginalPhoto(256L * 256, 16L * 1024 * 1024))
        assertFalse(fitsOriginalPhoto(Long.MAX_VALUE, Long.MAX_VALUE))
    }
}
