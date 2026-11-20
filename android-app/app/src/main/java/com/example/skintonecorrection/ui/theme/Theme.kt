package com.example.skintonecorrection.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

private val LightColors = lightColorScheme(
    primary = Color(0xFF087E75),
    onPrimary = Color.White,
    primaryContainer = Color(0xFFE8FAF6),
    onPrimaryContainer = Color(0xFF075B54),
    tertiaryContainer = Color(0xFFFFF6DE),
    onTertiaryContainer = Color(0xFF784600),
    background = Color(0xFFF5F7F9),
    onBackground = Color(0xFF111C2F),
    surface = Color.White,
    onSurface = Color(0xFF111C2F),
    surfaceVariant = Color(0xFFE8EEF1),
    onSurfaceVariant = Color(0xFF536174),
    outline = Color(0xFF768391)
)

private val DarkColors = darkColorScheme(
    primary = Color(0xFF78E1D4),
    onPrimary = Color(0xFF003732),
    primaryContainer = Color(0xFF123B37),
    onPrimaryContainer = Color(0xFFAFF0E5),
    tertiaryContainer = Color(0xFF44331A),
    onTertiaryContainer = Color(0xFFFFD999),
    background = Color(0xFF111820),
    onBackground = Color(0xFFE9EFF4),
    surface = Color(0xFF1A242E),
    onSurface = Color(0xFFE9EFF4),
    surfaceVariant = Color(0xFF2A3844),
    onSurfaceVariant = Color(0xFFBAC8D5),
    outline = Color(0xFF8495A4)
)

@Composable
fun SkinToneCorrectionTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = if (isSystemInDarkTheme()) DarkColors else LightColors,
        typography = Typography,
        content = content
    )
}
