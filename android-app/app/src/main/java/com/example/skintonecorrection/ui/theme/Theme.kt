package com.example.skintonecorrection.ui.theme

import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.dynamicDarkColorScheme
import androidx.compose.material3.dynamicLightColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext

// Material 3 color schemes assembled from the palette in Color.kt.
private val LightColors = lightColorScheme(
    primary = Brown40,
    onPrimary = Color.White,
    primaryContainer = Cream90,
    onPrimaryContainer = DarkBrown20,
    secondary = Brown30,
    onSecondary = Color.White,
    secondaryContainer = Cream90,
    onSecondaryContainer = DarkBrown20,
    tertiary = Teal40,
    onTertiary = Color.White,
    tertiaryContainer = Cream90,
    onTertiaryContainer = DarkBrown20,
    background = Cream95,
    onBackground = DarkBrown20,
    surface = Cream95,
    onSurface = DarkBrown20,
    surfaceVariant = CreamGrey90,
    onSurfaceVariant = BrownGreyVariant50,
    outline = OutlineLight,
    error = Error40,
    onError = Color.White,
    errorContainer = ErrorContainer90,
    onErrorContainer = Color(0xFF410002),
)

private val DarkColors = darkColorScheme(
    primary = BrownLight80,
    onPrimary = Color(0xFF44271E),
    primaryContainer = BrownContainer30,
    onPrimaryContainer = Cream90,
    secondary = BrownLight70,
    onSecondary = Color(0xFF432417),
    secondaryContainer = BrownContainer40,
    onSecondaryContainer = Cream90,
    tertiary = TealLight80,
    onTertiary = Color(0xFF00363A),
    tertiaryContainer = TealContainerDark,
    onTertiaryContainer = Color(0xFF9CF1F6),
    background = DarkBrown10,
    onBackground = Color(0xFFEFDFDA),
    surface = DarkBrown10,
    onSurface = Color(0xFFEFDFDA),
    surfaceVariant = BrownGreyVariant50,
    onSurfaceVariant = BrownGreyVariant80,
    outline = OutlineDark,
    error = ErrorLight80,
    onError = Color(0xFF690005),
    errorContainer = ErrorContainer40,
    onErrorContainer = ErrorContainer90,
)

/**
 * App theme wrapper around Material 3.
 *
 * @param darkTheme whether to use the dark palette; defaults to the system setting.
 * @param dynamicColor whether to use Android 12+ "Material You" colors instead of the
 *   fixed brand palette. Disabled by default so the thesis demo looks consistent.
 */
@Composable
fun SkinToneCorrectionTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    dynamicColor: Boolean = false,
    content: @Composable () -> Unit,
) {
    val colorScheme = when {
        dynamicColor && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
            val context = LocalContext.current
            if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
        }
        darkTheme -> DarkColors
        else -> LightColors
    }

    MaterialTheme(
        colorScheme = colorScheme,
        typography = Typography,
        content = content,
    )
}