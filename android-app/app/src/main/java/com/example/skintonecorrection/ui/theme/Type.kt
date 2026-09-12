package com.example.skintonecorrection.ui.theme

import androidx.compose.material3.Typography
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp

/**
 * Default Compose typography.
 *
 * System fonts are used on purpose so no font assets are needed. The thesis report will
 * likely require consistent styling later; Material 3's default scale is a good baseline.
 */
val Typography = Typography(
    bodyLarge = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Normal,
        fontSize = 16.sp,
        lineHeight = 24.sp,
        letterSpacing = 0.5.sp,
    ),
    // Other text roles fall back to Material's sensible defaults.
)