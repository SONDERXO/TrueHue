package com.example.skintonecorrection.ui

import androidx.compose.runtime.Composable
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.example.skintonecorrection.ui.home.HomeScreen
import com.example.skintonecorrection.ui.processing.ProcessingScreen
import com.example.skintonecorrection.ui.result.ResultScreen
import com.example.skintonecorrection.ui.splash.SplashScreen
import com.example.skintonecorrection.util.Routes

/**
 * The app's navigation graph.
 *
 * [viewModel] is called HERE (above the [NavHost]), so it resolves against the Activity and
 * the SAME [SharedViewModel] instance is handed to every screen. If we called it inside each
 * screen instead, every destination would get its own copy and they could not share the
 * selected image URI.
 *
 * Graph:
 *   splash -> home -> processing -> result -> (back) home
 */
@Composable
fun AppNavHost(sharedViewModel: SharedViewModel = viewModel()) {
    val navController = rememberNavController()

    NavHost(navController = navController, startDestination = Routes.SPLASH) {

        composable(Routes.SPLASH) {
            // Optional branding screen; removes itself from the back stack when done.
            SplashScreen(
                onFinished = {
                    navController.navigate(Routes.HOME) {
                        popUpTo(Routes.SPLASH) { inclusive = true }
                    }
                }
            )
        }

        composable(Routes.HOME) {
            HomeScreen(
                sharedViewModel = sharedViewModel,
                onProcessClick = {
                    // Kick off the (simulated) correction, then move to the working screen.
                    sharedViewModel.startProcessing()
                    navController.navigate(Routes.PROCESSING)
                }
            )
        }

        composable(Routes.PROCESSING) {
            ProcessingScreen(
                sharedViewModel = sharedViewModel,
                // Called by the screen when processing reaches SUCCESS state.
                onProcessingFinished = {
                    navController.navigate(Routes.RESULT) {
                        // Drop the HOME back-stack entry so "Back" from Result exits home
                        // (RESULT becomes the back target via HOME->RESULT only).
                        popUpTo(Routes.HOME)
                    }
                },
                onBackToHome = {
                    navController.popBackStack(Routes.HOME, inclusive = false)
                }
            )
        }

        composable(Routes.RESULT) {
            ResultScreen(
                sharedViewModel = sharedViewModel,
                onReSelect = {
                    // Return to the Home screen to choose another photo.
                    navController.popBackStack(Routes.HOME, inclusive = false)
                }
            )
        }
    }
}