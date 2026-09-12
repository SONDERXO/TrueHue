package com.example.skintonecorrection.ui.home

import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.PickVisualMediaRequest
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
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
import androidx.compose.ui.draw.clip
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
 * Home / gallery-selection screen.
 *
 * Responsibilities (all handled here for now):
 *  - Open the Android Photo Picker when "Select Photo" is tapped.
 *  - Show a preview of the chosen image (or a placeholder).
 *  - Confirm the selection with a Snackbar that includes the picked URI.
 *  - Enable "Process Image" once a photo exists, then hand off to the Processing screen.
 *
 * The URI is stored in the shared [SharedViewModel] so later screens can use it.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    sharedViewModel: SharedViewModel,
    onProcessClick: () -> Unit,
) {
    val uiState by sharedViewModel.uiState.collectAsStateWithLifecycle()

    val snackbarHostState = remember { SnackbarHostState() }
    val scope = rememberCoroutineScope()
    val context = LocalContext.current

    // System Photo Picker (works on all API 24+ devices; on Android 13+ it uses the
    // native photo picker, on older versions the compat library falls back gracefully).
    // NOTE: no storage permission is required - the picker grants per-URI read access.
    val pickImageLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.PickVisualMedia()
    ) { uri: Uri? ->
        when (uri) {
            // User cancelled, or the picker could not resolve an image.
            null -> scope.launch {
                snackbarHostState.showSnackbar(context.getString(R.string.error_no_image_found))
            }
            else -> {
                // Store the selection and confirm it (placeholder behaviour per the
                // milestone: just report the URI, no processing yet).
                sharedViewModel.selectImage(uri)
                scope.launch {
                    snackbarHostState.showSnackbar(context.getString(R.string.photo_selected, uri.toString()))
                }
            }
        }
    }

    Scaffold(snackbarHost = { SnackbarHost(snackbarHostState) }) { innerPadding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 24.dp, vertical = 32.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            // ---- Title + description -------------------------------------------------
            Text(
                text = stringResource(R.string.app_title),
                style = MaterialTheme.typography.headlineMedium,
                textAlign = TextAlign.Center,
            )
            Spacer(modifier = Modifier.height(12.dp))
            Text(
                text = stringResource(R.string.home_description),
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center,
            )
            Spacer(modifier = Modifier.height(24.dp))

            // ---- Selected photo preview (or placeholder) -----------------------------
            val selectedUri = uiState.selectedImageUri
            if (selectedUri != null) {
                Card(modifier = Modifier.fillMaxWidth()) {
                    AsyncImage(
                        model = selectedUri,
                        contentDescription = stringResource(R.string.selected_photo_preview),
                        modifier = Modifier
                            .fillMaxWidth()
                            .height(240.dp),
                        contentScale = ContentScale.Crop,
                    )
                }
            } else {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(240.dp)
                        .clip(RoundedCornerShape(12.dp))
                        .background(MaterialTheme.colorScheme.surfaceVariant),
                    contentAlignment = Alignment.Center,
                ) {
                    Text(
                        text = stringResource(R.string.no_photo_selected),
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
            }

            Spacer(modifier = Modifier.height(24.dp))

            // ---- Buttons --------------------------------------------------------------
            Button(
                onClick = {
                    pickImageLauncher.launch(
                        PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.ImageOnly)
                    )
                },
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text(text = stringResource(R.string.select_photo))
            }
            Spacer(modifier = Modifier.height(12.dp))
            Button(
                onClick = onProcessClick,
                enabled = selectedUri != null,
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text(text = stringResource(R.string.process_image))
            }
        }
    }
}