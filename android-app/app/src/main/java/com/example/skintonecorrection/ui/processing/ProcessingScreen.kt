package com.example.skintonecorrection.ui.processing

import androidx.compose.animation.core.EaseOutCubic
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.animate
import androidx.compose.animation.core.tween
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import coil.compose.AsyncImage
import com.example.skintonecorrection.R
import com.example.skintonecorrection.data.CorrectionStage
import com.example.skintonecorrection.data.GlassesChoice
import com.example.skintonecorrection.ui.BrandMark
import com.example.skintonecorrection.ui.PhotoShape
import com.example.skintonecorrection.ui.ProcessingState
import com.example.skintonecorrection.ui.SharedViewModel
import com.example.skintonecorrection.ui.WorkflowAction
import kotlinx.coroutines.delay

@Composable
fun ProcessingScreen(
    sharedViewModel: SharedViewModel,
    onProcessingFinished: () -> Unit,
    onBack: () -> Unit,
    onPickPhoto: () -> Unit
) {
    val state by sharedViewModel.uiState.collectAsStateWithLifecycle()
    var percent by rememberSaveable(state.selectedImageUri) { mutableFloatStateOf(1f) }
    val (estimateLimit, estimateMillis, detail) = when (state.correctionStage) {
        CorrectionStage.PREPARING -> Triple(12f, 1_800, "Preparing your photo…")
        CorrectionStage.CORRECTING -> Triple(91f, 45_000, "Analyzing your photo and adjusting exposure and colour…")
        CorrectionStage.SAVING -> Triple(99f, 2_500, "Getting your result ready…")
    }
    LaunchedEffect(state.processingState, state.correctionStage) {
        when (state.processingState) {
            ProcessingState.PROCESSING -> if (percent < estimateLimit) {
                animate(percent, estimateLimit, animationSpec = tween(estimateMillis, easing = EaseOutCubic)) { value, _ ->
                    percent = value
                }
            }
            ProcessingState.SUCCESS -> {
                animate(percent, 100f, animationSpec = tween(420, easing = LinearEasing)) { value, _ ->
                    percent = value
                }
                delay(150)
                onProcessingFinished()
            }
            ProcessingState.IDLE -> onBack()
            else -> Unit
        }
    }
    Scaffold(containerColor = MaterialTheme.colorScheme.background) { padding ->
        Box(Modifier.fillMaxSize().padding(padding), contentAlignment = Alignment.Center) {
            Column(
                Modifier.widthIn(max = 450.dp).fillMaxWidth().verticalScroll(rememberScrollState()).padding(24.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                when (state.processingState) {
                    ProcessingState.PROCESSING -> CorrectionProgress(percent, detail)
                    ProcessingState.SUCCESS -> CorrectionProgress(percent, "Opening your result…")
                    ProcessingState.NEEDS_GLASSES_CHOICE -> {
                        AsyncImage(state.selectedImageUri, "Selected photo", Modifier.fillMaxWidth().height(156.dp)
                            .clip(PhotoShape), contentScale = ContentScale.Fit)
                        Text(stringResource(R.string.glasses_prompt_title), style = MaterialTheme.typography.titleLarge)
                        Text(stringResource(R.string.glasses_prompt_hint), textAlign = TextAlign.Center)
                        WorkflowAction(stringResource(R.string.glasses_none),
                            { sharedViewModel.continueWithGlasses(GlassesChoice.NONE) })
                        WorkflowAction(stringResource(R.string.glasses_clear),
                            { sharedViewModel.continueWithGlasses(GlassesChoice.CLEAR) }, primary = false)
                        WorkflowAction(stringResource(R.string.glasses_protected),
                            { sharedViewModel.continueWithGlasses(GlassesChoice.OPAQUE) }, primary = false)
                        TextButton(onClick = onBack) { Text("Back to photo") }
                    }
                    ProcessingState.ERROR -> {
                        Text("Couldn’t process this photo", style = MaterialTheme.typography.titleLarge)
                        Text(state.message.ifEmpty { stringResource(R.string.error_processing_failed) },
                            color = MaterialTheme.colorScheme.error, textAlign = TextAlign.Center)
                        WorkflowAction("Choose another photo", onPickPhoto)
                        TextButton(onClick = onBack) { Text("Back to photo") }
                    }
                    ProcessingState.IDLE -> Unit
                }
            }
        }
    }
}

@Composable
private fun CorrectionProgress(percent: Float, detail: String) {
    BrandMark()
    Text("Processing photo", style = MaterialTheme.typography.titleLarge)
    Text(detail, style = MaterialTheme.typography.bodyMedium, textAlign = TextAlign.Center)
    Column(Modifier.widthIn(max = 320.dp).fillMaxWidth().padding(vertical = 6.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically) {
            Text("Estimated progress", style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant)
            Text("${percent.toInt()}%", color = MaterialTheme.colorScheme.primary,
                style = MaterialTheme.typography.titleLarge)
        }
        LinearProgressIndicator(progress = { percent / 100f }, modifier = Modifier.fillMaxWidth().height(8.dp),
            trackColor = MaterialTheme.colorScheme.surfaceVariant)
    }
    Text("Your photo stays on this device.", style = MaterialTheme.typography.bodySmall,
        color = MaterialTheme.colorScheme.onSurfaceVariant, textAlign = TextAlign.Center)
}
