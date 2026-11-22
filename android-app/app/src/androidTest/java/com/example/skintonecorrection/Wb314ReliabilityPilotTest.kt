package com.example.skintonecorrection

import android.net.Uri
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.platform.app.InstrumentationRegistry
import com.example.skintonecorrection.data.ImageRepository
import kotlinx.coroutines.runBlocking
import org.json.JSONObject
import org.junit.Assume.assumeTrue
import org.junit.Test
import org.junit.runner.RunWith
import java.io.File

@RunWith(AndroidJUnit4::class)
class Wb314ReliabilityPilotTest {
    @Test fun processSealedInputs() = runBlocking {
        assumeTrue(InstrumentationRegistry.getArguments().getString("wb314ReliabilityPilot") == "true")
        check(BuildConfig.WB314_PICKER_FIXES)
        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val folder = File(context.filesDir, "wb314_reliability_pilot")
        val inputs = checkNotNull(folder.listFiles()).filter { it.extension == "png" }.sortedBy { it.name }
        check(inputs.size == 36)
        val repository = ImageRepository(context)
        for (input in inputs) {
            val result = repository.runCorrection(Uri.fromFile(input))
            val report = JSONObject(File(checkNotNull(result.report.path)).readText())
            val corrected = result.corrected
            if (result.success && corrected != null) {
                repository.export(corrected, Uri.fromFile(File(folder, "${input.nameWithoutExtension}.result")))
            }
            File(folder, "${input.nameWithoutExtension}.json").writeText(report.toString())
        }
    }
}
