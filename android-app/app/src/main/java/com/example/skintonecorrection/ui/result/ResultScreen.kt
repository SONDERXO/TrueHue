package com.example.skintonecorrection.ui.result

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import coil.compose.AsyncImage
import com.example.skintonecorrection.R
import com.example.skintonecorrection.ui.SharedViewModel
import kotlinx.coroutines.launch

/**
 * Before/after comparison screen.
 *
 * Displays the original and the (currently placeholder) corrected image, and offers:
 *  - "Re-select Photo" -> back to Home.
 *  - "Save Corrected Image" -> for now only shows a Snackbar. Saving to gallery/media store
 *    will be implemented later (MediaStore / scoped storage).
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ResultScreen(
    sharedViewModel: SharedViewModel,
    onReSelect: () -> Unit,
) {
    val uiState by sharedViewModel.uiState.collectAsStateWithLifecycle()

    val snackbarHostState = remember { SnackbarHostState() }
    val scope = rememberCoroutineScope()
    val context = LocalContext.current

    Scaffold(snackbarHost = { SnackbarHost(snackbarHostState) }) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .verticalScroll(rememberScrollState())
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            val originalUri = uiState.selectedImageUri

            if (originalUri == null) {
                // Error state: we have nothing to show. Offer a way back.
                Text(
                    text = stringResource(R.string.error_no_image_found),
                    style = MaterialTheme.typography.titleMedium,
                    color = MaterialTheme.colorScheme.error,
                    textAlign = TextAlign.Center,
                )
                Spacer(modifier = Modifier.height(16.dp))
                Button(onClick = onReSelect) {
                    Text(text = stringResource(R.string.go_back))
                }
            } else {
                val correctedUri = uiState.correctedImageUri

                // ---- "Before" (original) ------------------------------------------------
                Text(
                    text = stringResource(R.string.result_before),
                    style = MaterialTheme.typography.titleMedium,
                    modifier = Modifier.align(Alignment.Start),
                )
                Spacer(modifier = Modifier.height(8.dp))
                Card(modifier = Modifier.fillMaxWidth()) {
                    AsyncImage(
                        model = originalUri,
                        contentDescription = stringResource(R.string.result_before),
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(240.dp),
                        contentScale = ContentScale.Crop,
                    )
                }

                Spacer(modifier = Modifier.height(24.dp))

                // ---- "After" (corrected - placeholder for now) ------------------------
                Text(
                    text = stringResource(R.string.result_after),
                    style = MaterialTheme.typography.titleMedium,
                    modifier = Modifier.align(Alignment.Start),
                )
                Spacer(modifier = Modifier.height(8.dp))
                Card(modifier = Modifier.fillMaxWidth()) {
                    // TODO(ml-pipeline): once correction exists, this shows the corrected
                    //  image. For now it falls back to the original so the UI can be demoed.
                    AsyncImage(
                        model = correctedUri ?: originalUri,
                        contentDescription = stringResource(R.string.result_after),
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(240.dp),
                        contentScale = ContentScale.Crop,
                    )
                }

                Spacer(modifier = Modifier.height(12.dp))
                Text(
                    text = stringResource(R.string.result_hint),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    textAlign = TextAlign.Center,
                )

                Spacer(modifier = Modifier.height(24.dp))

                // ---- Actions -----------------------------------------------------------
                OutlinedButton(
                    onClick = onReSelect,
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Text(text = stringResource(R.string.reselect_photo))
                }
                Spacer(modifier = Modifier.height(12.dp))
                Button(
                    onClick = {
                        // TODO(media-store): implement saving the corrected image
                        //  (MediaStore Images, scoped storage, API 29+ / legacy for 24-28).
                        scope.launch {
                            snackbarHostState.showSnackbar(context.getString(R.string.save_not_implemented))
                        }
                    },
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Text(text = stringResource(R.string.save_corrected_image))
                }
            }
        }
    }
}