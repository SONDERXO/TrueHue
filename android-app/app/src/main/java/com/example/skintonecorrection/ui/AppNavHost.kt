package com.example.skintonecorrection.ui

import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.PickVisualMediaRequest
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.platform.LocalContext
import androidx.core.content.FileProvider
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.example.skintonecorrection.ui.home.HomeScreen
import com.example.skintonecorrection.ui.home.SelectedPhotoScreen
import com.example.skintonecorrection.ui.processing.ProcessingScreen
import com.example.skintonecorrection.ui.result.ResultScreen
import com.example.skintonecorrection.util.Routes
import java.io.File
import java.io.IOException

@Composable
fun AppNavHost(sharedViewModel: SharedViewModel = viewModel()) {
    val navController = rememberNavController()
    val state by sharedViewModel.uiState.collectAsStateWithLifecycle()
    val context = LocalContext.current
    val cameraFolder = File(context.cacheDir, "camera_capture")
    val cameraAuthority = "${context.packageName}.camera"
    var pendingCapture by rememberSaveable { mutableStateOf<String?>(null) }
    var cameraMessage by rememberSaveable { mutableStateOf<String?>(null) }
    val selectPhoto: (Uri) -> Unit = { uri ->
        sharedViewModel.selectImage(uri)
        navController.navigate(Routes.SELECTED) {
            popUpTo(Routes.HOME)
            launchSingleTop = true
        }
    }
    val picker = rememberLauncherForActivityResult(ActivityResultContracts.PickVisualMedia()) { uri ->
        if (uri != null) selectPhoto(uri)
    }
    val camera = rememberLauncherForActivityResult(ActivityResultContracts.TakePicture()) { saved ->
        val file = pendingCapture?.let { File(cameraFolder, it) }
        pendingCapture = null
        if (saved && file != null && file.length() > 0) {
            selectPhoto(FileProvider.getUriForFile(context, cameraAuthority, file))
        } else {
            file?.delete()
            if (saved) cameraMessage = "No photo was saved. Try taking it again."
        }
    }
    val pickPhoto = {
        cameraMessage = null
        picker.launch(PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.ImageOnly))
    }
    val takePhoto: () -> Unit = {
        if (pendingCapture == null) {
            cameraMessage = null
            try {
                if (!cameraFolder.isDirectory && !cameraFolder.mkdirs()) throw IOException("Camera folder unavailable")
                val file = File.createTempFile("portrait_", ".jpg", cameraFolder)
                pendingCapture = file.name
                camera.launch(FileProvider.getUriForFile(context, cameraAuthority, file))
            } catch (_: Exception) {
                pendingCapture?.let { File(cameraFolder, it).delete() }
                pendingCapture = null
                cameraMessage = "Couldn’t open the camera. You can still choose a photo."
            }
        }
    }

    NavHost(navController, startDestination = Routes.HOME) {
        composable(Routes.HOME) { HomeScreen(pickPhoto, takePhoto, cameraMessage) }
        composable(Routes.SELECTED) {
            val selected = state.selectedImageUri
            if (selected == null) {
                LaunchedEffect(Unit) { navController.popBackStack(Routes.HOME, inclusive = false) }
            } else {
                SelectedPhotoScreen(
                    photo = selected,
                    onBack = { navController.popBackStack() },
                    onPickPhoto = pickPhoto,
                    onApply = {
                        sharedViewModel.startProcessing()
                        navController.navigate(Routes.PROCESSING)
                    }
                )
            }
        }
        composable(Routes.PROCESSING) {
            ProcessingScreen(
                sharedViewModel = sharedViewModel,
                onProcessingFinished = {
                    navController.navigate(Routes.RESULT) { popUpTo(Routes.HOME) }
                },
                onBack = { navController.popBackStack() },
                onPickPhoto = pickPhoto
            )
        }
        composable(Routes.RESULT) {
            ResultScreen(
                sharedViewModel = sharedViewModel,
                onBack = { navController.popBackStack() },
                onReSelect = pickPhoto
            )
        }
    }
}
