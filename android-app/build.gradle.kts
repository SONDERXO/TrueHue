// Project-level build.gradle.kts
// Declares the Gradle plugins used by this project. They are only APPLIED in the app module.
// Versions live in gradle/libs.versions.toml (keeps this file short).
plugins {
    alias(libs.plugins.android.application) apply false
    alias(libs.plugins.kotlin.android) apply false
    alias(libs.plugins.kotlin.compose) apply false
}