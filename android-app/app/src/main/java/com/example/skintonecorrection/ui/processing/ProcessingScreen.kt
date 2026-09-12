package com.example.skintonecorrection.ui.processing

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
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
import com.example.skintonecorrection.ui.ProcessingState
import com.example.skintonecorrection.ui.SharedViewModel

/**
 * "Working…" screen shown while the correction pipeline runs.
 *
 * Right now the pipeline is simulated with a delay inside [SharedViewModel.startProcessing].
 * The screen simply waits: it shows a progress indicator, and as soon as the shared state
 * flips to [ProcessingState.SUCCESS] it asks the nav host to open the Result screen.
 */
@Composable
fun ProcessingScreen(
    sharedViewModel: SharedViewModel,
    onProcessingFinished: () -> Unit,
    onBackToHome: () -> Unit,
) {
    val uiState by sharedViewModel.uiState.collectAsStateWithLifecycle()

    // Trigger navigation exactly once when the run completes (state changes will not
    // re-fire because LaunchedEffect keys on the state value).
    LaunchedEffect(uiState.processingState) {
        if (uiState.processingState == ProcessingState.SUCCESS) {
            onProcessingFinished()
        }
    }

    Scaffold { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(32.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center,
        ) {
            // Small preview so the user sees *what* is being processed.
            val uri = uiState.selectedImageUri
            if (uri != null) {
                AsyncImage(
                    model = uri,
                    contentDescription = stringResource(R.string.selected_photo_preview),
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(180.dp)
                        .clip(RoundedCornerShape(12.dp)),
                    contentScale = ContentScale.Crop,
                )
                Spacer(modifier = Modifier.height(24.dp))
            }

            when (uiState.processingState) {
                ProcessingState.PROCESSING -> {
                    CircularProgressIndicator()
                    Spacer(modifier = Modifier.height(16.dp))
                    Text(
                        text = stringResource(R.string.processing_title),
                        style = MaterialTheme.typography.titleMedium,
                    )
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = stringResource(R.string.processing_hint),
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        textAlign = TextAlign.Center,
                    )
                }

                ProcessingState.SUCCESS -> {
                    // Only visible for a frame before LaunchedEffect navigates away.
                    Text(
                        text = stringResource(R.string.processing_done),
                        style = MaterialTheme.typography.titleMedium,
                    )
                }

                ProcessingState.ERROR -> {
                    Text(
                        text = stringResource(uiState.errorMessageRes ?: R.string.error_processing_failed),
                        style = MaterialTheme.typography.titleMedium,
                        color = MaterialTheme.colorScheme.error,
                        textAlign = TextAlign.Center,
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                    Button(onClick = onBackToHome) {
                        Text(text = stringResource(R.string.back_to_home))
                    }
                }

                ProcessingState.IDLE -> {
                    // Safety net: this screen was opened without starting the pipeline.
                    Text(
                        text = stringResource(R.string.processing_hint),
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
            }
        }
    }
}