// app/build.gradle.kts - configuration for the :app module.
plugins {
    alias(libs.plugins.android.application) // Android application plugin
    alias(libs.plugins.kotlin.android)      // Kotlin for Android
    alias(libs.plugins.kotlin.compose)      // JetBrains Compose compiler plugin (Kotlin 2.0+)
}

android {
    namespace = "com.example.skintonecorrection"
    // Which Android SDK the code is compiled against.
    compileSdk = 35

    defaultConfig {
        applicationId = "com.example.skintonecorrection"
        // minSdk 24 = Android 7.0 (Nougat).
        //   Chosen because it covers ~97% of active devices while allowing us to use
        //   the modern AndroidX Photo Picker (backported automatically via the compat lib)
        //   and avoid legacy storage-permission code. Bumping to 26 would remove the need
        //   for any legacy code paths but reduces device coverage slightly.
        minSdk = 24
        targetSdk = 35
        versionCode = 1
        versionName = "1.0"
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildTypes {
        release {
            // No minification yet - the codebase is a skeleton. Enable R8 later if needed.
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    compileOptions {
        // Java 11 language features; safe for all supported toolchains.
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
    kotlinOptions {
        // Match the JVM target to the Java compatibility level above.
        jvmTarget = "11"
    }
    buildFeatures {
        // Enable Compose UI.
        compose = true
    }
    sourceSets.getByName("test").resources.srcDir("src/main/assets")
}

dependencies {
    implementation("org.opencv:opencv:5.0.0")
    implementation("com.google.mediapipe:tasks-vision:0.10.35")
    implementation("androidx.exifinterface:exifinterface:1.3.7")
    // Compose BOM: one version catalog entry that aligns a compatible set of
    // all androidx.compose.* libraries.
    implementation(platform(libs.androidx.compose.bom))

    // Core AndroidX.
    implementation(libs.androidx.core.ktx)
    implementation(libs.androidx.activity.compose)

    // Lifecycle / ViewModel (collectAsStateWithLifecycle, viewModel(), viewModelScope).
    implementation(libs.androidx.lifecycle.runtime.ktx)
    implementation(libs.androidx.lifecycle.runtime.compose)
    implementation(libs.androidx.lifecycle.viewmodel.compose)

    // Compose UI + Material 3 theming.
    implementation(libs.androidx.ui)
    implementation(libs.androidx.ui.graphics)
    implementation(libs.androidx.ui.tooling.preview)
    implementation(libs.androidx.material3)

    // Navigation between Compose screens.
    implementation(libs.androidx.navigation.compose)

    // Coil: async image loading (loads gallery URIs into AsyncImage).
    implementation(libs.coil.compose)

    // Tooling available only in debug builds (e.g., layout inspector preview).
    debugImplementation(libs.androidx.ui.tooling)
    testImplementation("junit:junit:4.13.2")
    // Real parser for local JVM tests; Android supplies org.json on devices.
    testImplementation("org.json:json:20240303")
    androidTestImplementation("androidx.test.ext:junit:1.2.1")
    androidTestImplementation("androidx.test:runner:1.6.2")
}
