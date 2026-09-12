package com.example.skintonecorrection.ui

import android.net.Uri
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.skintonecorrection.R
import com.example.skintonecorrection.data.ImageRepository
import com.example.skintonecorrection.util.SIMULATED_PROCESSING_DELAY_MS
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

/**
 * The stage the correction flow is currently in.
 */
enum class ProcessingState {
    /** Nothing selected / not processing. */
    IDLE,

    /** The (simulated) correction is running. */
    PROCESSING,

    /** Correction finished; the corrected image is available. */
    SUCCESS,

    /** Something went wrong; [SharedUiState.errorMessageRes] describes it. */
    ERROR,
}

/**
 * Immutable snapshot of everything the UI needs across all three screens.
 *
 * Making it a single [data class] with [kotlinx.coroutines.flow.StateFlow] means every
 * screen observes the same source of truth and the image URI is naturally shared between
 * the Home, Processing and Result screens.
 */
data class SharedUiState(
    /** Photo chosen by the user (source image). */
    val selectedImageUri: Uri? = null,

    /** Corrected result image (placeholder until the ML pipeline is wired in). */
    val correctedImageUri: Uri? = null,

    /** Current stage of the correction flow. */
    val processingState: ProcessingState = ProcessingState.IDLE,

    /** String resource id for the error message, set when [ProcessingState.ERROR]. */
    val errorMessageRes: Int? = null,
)

/**
 * Activity-scoped ViewModel holding all shared UI state.
 *
 * It is obtained once in [com.example.skintonecorrection.ui.AppNavHost] and passed to every
 * screen explicitly, so it survives configuration changes (rotation, theme switch) and is a
 * single, simple source of truth. A DI library (Hilt/Koin) is intentionally NOT used yet,
 * keeping the project approachable for a student team.
 */
class SharedViewModel(
    private val repository: ImageRepository = ImageRepository(),
) : ViewModel() {

    private val _uiState = MutableStateFlow(SharedUiState())
    val uiState: StateFlow<SharedUiState> = _uiState.asStateFlow()

    /**
     * Stores the user's chosen photo and resets any previous processing results.
     *
     * Called from the Photo Picker callback in [com.example.skintonecorrection.ui.home.HomeScreen].
     */
    fun selectImage(uri: Uri) {
        _uiState.update {
            it.copy(
                selectedImageUri = uri,
                correctedImageUri = null,
                processingState = ProcessingState.IDLE,
                errorMessageRes = null,
            )
        }
    }

    /**
     * Starts (or resumes) the correction run.
     *
     * The work is launched in [viewModelScope], so the delay keeps running even if the
     * device is rotated while the Processing screen is visible.
     *
     * TODO(ml-pipeline): replace the [delay] with the real correction call:
     *   repository.runCorrection(...) currently just passes the image through.
     */
    fun startProcessing() {
        val uri = _uiState.value.selectedImageUri
        if (uri == null) {
            _uiState.update {
                it.copy(processingState = ProcessingState.ERROR, errorMessageRes = R.string.error_no_image_selected)
            }
            return
        }

        // Ignore repeat taps while already processing.
        if (_uiState.value.processingState == ProcessingState.PROCESSING) return

        viewModelScope.launch {
            _uiState.update {
                it.copy(processingState = ProcessingState.PROCESSING, errorMessageRes = null)
            }

            // Simulated long-running work so the Processing screen is visible.
            delay(SIMULATED_PROCESSING_DELAY_MS)

            val correctedUri = try {
                repository.runCorrection(uri)
            } catch (t: Throwable) {
                // Surface failures as an ERROR state the UI can display (skeleton only;
                // the real pipeline is not wired in yet, so this path is defensive).
                _uiState.update {
                    it.copy(processingState = ProcessingState.ERROR, errorMessageRes = R.string.error_processing_failed)
                }
                return@launch
            }

            _uiState.update {
                it.copy(processingState = ProcessingState.SUCCESS, correctedImageUri = correctedUri)
            }
        }
    }
}