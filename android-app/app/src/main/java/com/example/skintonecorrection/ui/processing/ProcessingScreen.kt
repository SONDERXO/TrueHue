package com.example.skintonecorrection.ui.processing

import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
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
import com.example.skintonecorrection.data.GlassesChoice
import com.example.skintonecorrection.ui.PhotoShape
import com.example.skintonecorrection.ui.ProcessingState
import com.example.skintonecorrection.ui.SharedViewModel
import com.example.skintonecorrection.ui.WorkflowAction

@Composable
fun ProcessingScreen(sharedViewModel: SharedViewModel, onProcessingFinished: () -> Unit, onBack: () -> Unit) {
    val state by sharedViewModel.uiState.collectAsStateWithLifecycle()
    var savedMessage by remember { mutableStateOf("") }
    val saveReport = rememberLauncherForActivityResult(ActivityResultContracts.CreateDocument("application/json")) { destination ->
        val source = state.reportUri
        if (destination != null && source != null) sharedViewModel.export(source, destination) { savedMessage = it }
    }
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
                    ProcessingState.PROCESSING -> {
                        CircularProgressIndicator(Modifier.size(106.dp), strokeWidth = 7.dp,
                            trackColor = MaterialTheme.colorScheme.surfaceVariant)
                        Spacer(Modifier.height(16.dp))
                        Text("Processing photo", style = MaterialTheme.typography.titleLarge)
                        Text("Your photo is processed on this device.", style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant, textAlign = TextAlign.Center)
                    }
                    ProcessingState.NEEDS_GLASSES_CHOICE -> {
                        AsyncImage(state.selectedImageUri, "Selected photo", Modifier.fillMaxWidth().height(180.dp)
                            .clip(PhotoShape), contentScale = ContentScale.Fit)
                        Text(stringResource(R.string.glasses_prompt_title), style = MaterialTheme.typography.titleLarge)
                        Text(stringResource(R.string.glasses_prompt_hint), textAlign = TextAlign.Center)
                        WorkflowAction(stringResource(R.string.glasses_protected),
                            { sharedViewModel.continueWithGlasses(GlassesChoice.OPAQUE) })
                        WorkflowAction(stringResource(R.string.glasses_clear),
                            { sharedViewModel.continueWithGlasses(GlassesChoice.CLEAR) }, primary = false)
                        TextButton(onClick = onBack) { Text("Back to photo") }
                    }
                    ProcessingState.ERROR -> {
                        Text("Couldn’t process this photo", style = MaterialTheme.typography.titleLarge)
                        Text(state.message.ifEmpty { stringResource(R.string.error_processing_failed) },
                            color = MaterialTheme.colorScheme.error, textAlign = TextAlign.Center)
                        WorkflowAction("Back to photo", onBack)
                        if (state.reportUri != null) TextButton(onClick = { saveReport.launch("truehue_failure_report.json") }) {
                            Text("Save failure report")
                        }
                        if (savedMessage.isNotEmpty()) Text(savedMessage)
                    }
                    ProcessingState.IDLE, ProcessingState.SUCCESS -> Unit
                }
            }
        }
    }
}
