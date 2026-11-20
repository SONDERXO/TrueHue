package com.example.skintonecorrection.ui

import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.PickVisualMediaRequest
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
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

@Composable
fun AppNavHost(sharedViewModel: SharedViewModel = viewModel()) {
    val navController = rememberNavController()
    val state by sharedViewModel.uiState.collectAsStateWithLifecycle()
    val picker = rememberLauncherForActivityResult(ActivityResultContracts.PickVisualMedia()) { uri ->
        if (uri != null) {
            sharedViewModel.selectImage(uri)
            navController.navigate(Routes.SELECTED) {
                popUpTo(Routes.HOME)
                launchSingleTop = true
            }
        }
    }
    val pickPhoto = { picker.launch(PickVisualMediaRequest(ActivityResultContracts.PickVisualMedia.ImageOnly)) }

    NavHost(navController, startDestination = Routes.HOME) {
        composable(Routes.HOME) { HomeScreen(pickPhoto) }
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
                onBack = { navController.popBackStack() }
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
