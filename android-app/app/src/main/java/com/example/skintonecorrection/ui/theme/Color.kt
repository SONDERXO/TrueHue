package com.example.skintonecorrection.ui.theme

import androidx.compose.ui.graphics.Color

// ---------------------------------------------------------------------------
// Material 3 color roles for the "Skin Tone Correction" brand.
//
// A warm brown/coffee primary palette (skin-tone themed) with a teal tertiary accent.
// Values follow the Material tonal scale (40 = primary, 90 = container, etc.).
// ---------------------------------------------------------------------------

// Light scheme
val Brown40 = Color(0xFF6D4C41)            // primary
val Brown30 = Color(0xFF5D4037)            // secondary
val Teal40 = Color(0xFF00696E)             // tertiary
val Cream95 = Color(0xFFFEF7F5)            // background / surface
val Cream90 = Color(0xFFF2DED7)            // primary + secondary container
val CreamGrey90 = Color(0xFFF2E5E1)        // surfaceVariant
val DarkBrown20 = Color(0xFF201A18)        // onBackground / onSurface
val BrownGreyVariant50 = Color(0xFF51443F) // onSurfaceVariant
val OutlineLight = Color(0xFF83746F)
val Error40 = Color(0xFFBA1A1A)
val ErrorContainer90 = Color(0xFFFFDAD6)

// Dark scheme
val BrownLight80 = Color(0xFFE1BDB2)       // primary
val BrownLight70 = Color(0xFFD3B5AB)       // secondary
val TealLight80 = Color(0xFF78D8DE)        // tertiary
val DarkBrown10 = Color(0xFF191317)        // background / surface
val BrownContainer30 = Color(0xFF5D4037)   // primary container
val BrownContainer40 = Color(0xFF5A3A2E)   // secondary container
val TealContainerDark = Color(0xFF005257)  // tertiary container
val BrownGreyVariant80 = Color(0xFFD5C3BF) // onSurfaceVariant
val OutlineDark = Color(0xFF9E8E8A)
val ErrorLight80 = Color(0xFFFFB4AB)
val ErrorContainer40 = Color(0xFF93000A)

// Light and dark roles are assembled into color schemes in Theme.kt.