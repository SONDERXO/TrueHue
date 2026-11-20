package com.example.skintonecorrection.ui.processing

import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.*
import androidx.compose.runtime.*
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

@Composable
fun ProcessingScreen(
    sharedViewModel: SharedViewModel,
    onProcessingFinished: () -> Unit,
    onBack: () -> Unit,
    onPickPhoto: () -> Unit
) {
    val state by sharedViewModel.uiState.collectAsStateWithLifecycle()
    LaunchedEffect(state.processingState) {
        when (state.processingState) {
            ProcessingState.SUCCESS -> onProcessingFinished()
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
                    ProcessingState.PROCESSING -> CorrectionProgress(state.correctionStage)
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
                    ProcessingState.IDLE, ProcessingState.SUCCESS -> Unit
                }
            }
        }
    }
}

@Composable
private fun CorrectionProgress(stage: CorrectionStage) {
    val (percentage, detail) = when (stage) {
        CorrectionStage.PREPARING -> 0 to "Preparing your photo…"
        CorrectionStage.CORRECTING -> 33 to "Analyzing your photo and adjusting exposure and colour…"
        CorrectionStage.SAVING -> 67 to "Getting your result ready…"
    }
    val fill by animateFloatAsState(percentage / 100f, label = "Correction progress")
    BrandMark()
    Text("Processing photo", style = MaterialTheme.typography.titleLarge)
    Text(detail, style = MaterialTheme.typography.bodyMedium, textAlign = TextAlign.Center)
    Column(Modifier.widthIn(max = 320.dp).fillMaxWidth().padding(vertical = 6.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Text("$percentage%", Modifier.align(Alignment.End), color = MaterialTheme.colorScheme.primary,
            style = MaterialTheme.typography.titleLarge)
        LinearProgressIndicator(progress = { fill }, modifier = Modifier.fillMaxWidth().height(8.dp),
            trackColor = MaterialTheme.colorScheme.surfaceVariant)
    }
    Text("Your photo stays on this device.", style = MaterialTheme.typography.bodySmall,
        color = MaterialTheme.colorScheme.onSurfaceVariant, textAlign = TextAlign.Center)
}
