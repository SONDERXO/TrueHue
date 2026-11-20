package com.example.skintonecorrection

import android.app.Application
import android.graphics.BitmapFactory
import android.net.Uri
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.ViewModelStore
import androidx.lifecycle.ViewModelStoreOwner
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.example.skintonecorrection.data.CorrectionStage
import com.example.skintonecorrection.data.GlassesChoice
import com.example.skintonecorrection.data.GlassesChoiceRequired
import com.example.skintonecorrection.data.ResearchMaskRules
import com.example.skintonecorrection.ui.ProcessingState
import com.example.skintonecorrection.ui.SharedUiState
import com.example.skintonecorrection.ui.SharedViewModel
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.withContext
import kotlinx.coroutines.withTimeout
import org.json.JSONObject
import org.junit.Assert.*
import org.junit.Assume.assumeTrue
import org.junit.Test
import org.junit.runner.RunWith
import org.opencv.core.Rect
import java.io.File

@RunWith(AndroidJUnit4::class)
class Wb314GlassesFlowTest {
    @Test fun aBackgroundLabelDoesNotTriggerTheGlassesQuestion() {
        val categories = ByteArray(256 * 256)
        val face = Rect(40, 50, 80, 100)
        categories[49 * 256 + 40] = 6
        ResearchMaskRules.requireGlassesChoice(categories, face, GlassesChoice.UNCERTAIN)

        categories[50 * 256 + 40] = 6
        assertThrows(GlassesChoiceRequired::class.java) {
            ResearchMaskRules.requireGlassesChoice(categories, face, GlassesChoice.UNCERTAIN)
        }
        ResearchMaskRules.requireGlassesChoice(categories, face, GlassesChoice.NONE)
    }

    @Test fun pausesForGlassesAndContinuesWithSamePhoto() = runBlocking {
        val instrumentation = InstrumentationRegistry.getInstrumentation()
        assumeTrue(InstrumentationRegistry.getArguments().getString("wb314GlassesFixture") == "true")
        val app = instrumentation.targetContext.applicationContext as Application
        val fixture = File(app.filesDir, "wb314_glasses_test")
        val owner = object : ViewModelStoreOwner { override val viewModelStore = ViewModelStore() }
        val vm = withContext(Dispatchers.Main) {
            ViewModelProvider(owner, ViewModelProvider.AndroidViewModelFactory.getInstance(app))[SharedViewModel::class.java]
        }
        val runFolders = mutableSetOf<File>()
        fun report(state: SharedUiState): JSONObject {
            val file = File(requireNotNull(state.reportUri?.path))
            runFolders += requireNotNull(file.parentFile)
            return JSONObject(file.readText())
        }
        suspend fun settled() = withTimeout(40_000) {
            vm.uiState.first { it.processingState != ProcessingState.IDLE && it.processingState != ProcessingState.PROCESSING }
        }
        try {
            val glasses = Uri.fromFile(File(fixture, "glasses_input.png"))
            withContext(Dispatchers.Main) { vm.selectImage(glasses); vm.startProcessing() }
            val pending = settled()
            assertEquals(pending.message, ProcessingState.NEEDS_GLASSES_CHOICE, pending.processingState)
            assertEquals(glasses, pending.selectedImageUri)
            assertNull(pending.correctedImageUri)
            assertEquals(CorrectionStage.CORRECTING, pending.correctionStage)
            val pendingReport = report(pending)
            assertEquals("needs_glasses_choice", pendingReport.getString("status"))
            assertEquals(0, pendingReport.getJSONObject("output_sha256").length())

            withContext(Dispatchers.Main) { vm.continueWithGlasses(GlassesChoice.CLEAR) }
            val corrected = settled()
            assertEquals(corrected.message, ProcessingState.SUCCESS, corrected.processingState)
            assertEquals(glasses, corrected.selectedImageUri)
            assertEquals(CorrectionStage.SAVING, corrected.correctionStage)
            val correctedReport = report(corrected)
            assertEquals("clear", correctedReport.getString("glasses_choice"))
            assertEquals(pendingReport.getString("source_sha256"), correctedReport.getString("source_sha256"))
            assertOriginalDimensions(glasses, requireNotNull(corrected.correctedImageUri))

            withContext(Dispatchers.Main) { vm.selectImage(glasses); vm.startProcessing() }
            val confirmation = settled()
            assertEquals(ProcessingState.NEEDS_GLASSES_CHOICE, confirmation.processingState)
            assertEquals(pendingReport.getString("source_sha256"), report(confirmation).getString("source_sha256"))
            withContext(Dispatchers.Main) { vm.continueWithGlasses(GlassesChoice.NONE) }
            val noGlasses = settled()
            assertEquals(noGlasses.message, ProcessingState.SUCCESS, noGlasses.processingState)
            assertEquals(glasses, noGlasses.selectedImageUri)
            val noGlassesReport = report(noGlasses)
            assertEquals("none", noGlassesReport.getString("glasses_choice"))
            assertEquals(pendingReport.getString("source_sha256"), noGlassesReport.getString("source_sha256"))
            assertOriginalDimensions(glasses, requireNotNull(noGlasses.correctedImageUri))

            val ordinary = Uri.fromFile(File(fixture, "ordinary_input.png"))
            withContext(Dispatchers.Main) { vm.selectImage(ordinary); vm.startProcessing() }
            val direct = settled()
            assertEquals(direct.message, ProcessingState.SUCCESS, direct.processingState)
            assertEquals(ordinary, direct.selectedImageUri)
            assertEquals(CorrectionStage.SAVING, direct.correctionStage)
            assertEquals("uncertain", report(direct).getString("glasses_choice"))
            assertOriginalDimensions(ordinary, requireNotNull(direct.correctedImageUri))
        } finally {
            withContext(Dispatchers.Main) { owner.viewModelStore.clear() }
            for (folder in runFolders) {
                for (name in listOf("photo_used.png", "skin_mask.png", "experimental_correction.png", "report.json")) {
                    File(folder, name).delete()
                }
                folder.delete()
            }
        }
    }

    private fun assertOriginalDimensions(original: Uri, corrected: Uri) {
        fun size(uri: Uri) = BitmapFactory.Options().apply {
            inJustDecodeBounds = true
            BitmapFactory.decodeFile(uri.path, this)
        }.let { it.outWidth to it.outHeight }
        val expected = size(original)
        assertTrue(expected.first > 0 && expected.second > 0)
        assertEquals(expected, size(corrected))
    }
}
