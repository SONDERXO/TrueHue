package com.example.skintonecorrection.util

/**
 * Navigation route names for the Compose NavHost.
 *
 * Keeping them in one object avoids magic strings scattered through the code and makes
 * renaming a route a one-line change.
 */
object Routes {
    /** Optional branding screen shown at launch. */
    const val SPLASH = "splash"

    /** Photo selection screen (start of the real flow). */
    const val HOME = "home"

    /** Fake "working" screen while the (future) pipeline runs. */
    const val PROCESSING = "processing"

    /** Before/after comparison screen. */
    const val RESULT = "result"
}

/**
 * How long the simulated processing step takes (milliseconds).
 *
 * TODO(ml-pipeline): remove once the real correction pipeline runs on-device.
 */
const val SIMULATED_PROCESSING_DELAY_MS = 2000L