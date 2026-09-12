package com.example.skintonecorrection

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import com.example.skintonecorrection.ui.AppNavHost
import com.example.skintonecorrection.ui.theme.SkinToneCorrectionTheme

/**
 * The app's single Activity.
 *
 * Because the app uses Jetpack Compose, one activity is enough: the entire UI is declared
 * in [setContent], and navigation between screens happens inside the Compose [AppNavHost].
 */
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Draw the Compose UI behind the system status/navigation bars so they use our theme colors.
        enableEdgeToEdge()
        setContent {
            SkinToneCorrectionTheme {
                AppNavHost()
            }
        }
    }
}