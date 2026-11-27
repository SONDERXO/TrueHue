package com.example.skintonecorrection.data

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class Wb314CandidateReviewTest {
    private val safe = Wb314CandidateReview.Samples(
        face = 1000, changed = 400, brightInput = 30, brightenedHighlights = 1,
        newClipping = 0, strongEdits = 0, absoluteChange = 12_000
    )

    @Test fun allowsBoundedEditsAndBrightFaceDarkening() {
        assertNull(safe.rejection(defaultExposure = true))
        assertNull(safe.copy(brightInput = 500).rejection(defaultExposure = false))
    }

    @Test fun declinesDefaultBrighteningOnAnAlreadyBrightFace() {
        assertEquals("already_bright", safe.copy(brightInput = 200).rejection(defaultExposure = true))
    }

    @Test fun rejectsExcessiveEditsAndNoVisibleChange() {
        assertEquals("new_clipping", safe.copy(newClipping = 6).rejection(defaultExposure = false))
        assertEquals("brightened_highlights", safe.copy(brightenedHighlights = 21).rejection(defaultExposure = false))
        assertEquals("heavy_edit", safe.copy(strongEdits = 51).rejection(defaultExposure = false))
        assertEquals("no_visible_edit", safe.copy(changed = 0).rejection(defaultExposure = true))
    }
}
