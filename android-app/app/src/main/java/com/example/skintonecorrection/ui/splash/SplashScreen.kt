package com.example.skintonecorrection.ui.splash

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import com.example.skintonecorrection.R
import kotlinx.coroutines.delay

/**
 * Optional launch/branding screen.
 *
 * Shows the app name briefly, then hands over to [onFinished] (navigates to Home).
 * It is intentionally trivial; you can delete this screen and make HOME the start
 * destination in AppNavHost if you prefer no splash at all.
 */
@Composable
fun SplashScreen(onFinished: () -> Unit) {
    // Show the screen for 1.5 s, then tell the nav host to move on.
    LaunchedEffect(Unit) {
        delay(1500)
        onFinished()
    }

    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.primary),
        contentAlignment = Alignment.Center,
    ) {
        Text(
            text = stringResource(R.string.app_title),
            style = MaterialTheme.typography.headlineMedium,
            color = MaterialTheme.colorScheme.onPrimary,
        )
    }
}