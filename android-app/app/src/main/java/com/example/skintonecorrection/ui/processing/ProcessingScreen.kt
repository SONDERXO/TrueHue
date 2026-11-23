package com.example.skintonecorrection.ui.processing

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
    val (limit, duration, detail) = when (state.correctionStage) {
        CorrectionStage.PREPARING -> Triple(12f, 1800, "Preparing your photo…")
        CorrectionStage.CORRECTING -> Triple(91f, 45000, "Checking the portrait and applying any adjustment…")
        CorrectionStage.SAVING -> Triple(99f, 2500, "Getting your result ready…")
    }
    LaunchedEffect(state.processingState, state.correctionStage) {
        when (state.processingState) {
            ProcessingState.PROCESSING -> if (percent < limit) {
                animate(percent, limit, animationSpec = tween(duration)) { value, _ -> percent = value }
            }
            ProcessingState.SUCCESS -> {
                animate(percent, 100f, animationSpec = tween(350)) { value, _ -> percent = value }
                delay(250)
                onProcessingFinished()
            }
            ProcessingState.NEEDS_GLASSES_CHOICE -> percent = 1f
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
                    ProcessingState.PROCESSING -> CorrectionProgress(detail, percent)
                    ProcessingState.SUCCESS -> CorrectionProgress("Opening your result…", percent)
                    ProcessingState.NEEDS_GLASSES_CHOICE -> {
                        val choiceStyle = MaterialTheme.typography.labelMedium
                        AsyncImage(state.selectedImageUri, "Selected photo", Modifier.fillMaxWidth().height(120.dp)
                            .clip(PhotoShape), contentScale = ContentScale.Fit)
                        Text(stringResource(R.string.glasses_prompt_title), style = MaterialTheme.typography.titleMedium,
                            textAlign = TextAlign.Center)
                        Text(stringResource(R.string.glasses_prompt_hint), style = MaterialTheme.typography.bodySmall,
                            textAlign = TextAlign.Center)
                        WorkflowAction(stringResource(R.string.glasses_none),
                            { sharedViewModel.continueWithGlasses(GlassesChoice.NONE) }, labelStyle = choiceStyle)
                        WorkflowAction(stringResource(R.string.glasses_clear),
                            { sharedViewModel.continueWithGlasses(GlassesChoice.CLEAR) }, primary = false,
                            labelStyle = choiceStyle)
                        WorkflowAction(stringResource(R.string.glasses_protected),
                            { sharedViewModel.continueWithGlasses(GlassesChoice.OPAQUE) }, primary = false,
                            labelStyle = choiceStyle)
                        TextButton(onClick = onBack) { Text("Back to photo", style = choiceStyle) }
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
private fun CorrectionProgress(detail: String, percent: Float) {
    BrandMark()
    Text("Processing photo", style = MaterialTheme.typography.titleLarge)
    Text(detail, style = MaterialTheme.typography.bodyMedium, textAlign = TextAlign.Center)
    Column(Modifier.widthIn(max = 280.dp).fillMaxWidth(), verticalArrangement = Arrangement.spacedBy(6.dp)) {
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            Text("Estimated progress", style = MaterialTheme.typography.labelMedium)
            Text("${percent.toInt()}%", style = MaterialTheme.typography.labelMedium,
                color = MaterialTheme.colorScheme.primary)
        }
        LinearProgressIndicator(progress = { percent / 100f }, modifier = Modifier.fillMaxWidth().height(6.dp),
            trackColor = MaterialTheme.colorScheme.surfaceVariant)
    }
}
