// app/build.gradle.kts - configuration for the :app module.
plugins {
    alias(libs.plugins.android.application) // Android application plugin
    alias(libs.plugins.kotlin.android)      // Kotlin for Android
    alias(libs.plugins.kotlin.compose)      // JetBrains Compose compiler plugin (Kotlin 2.0+)
}

val wb314PickerTest = providers.gradleProperty("wb314PickerTest").map { it.toBooleanStrict() }.orElse(false)
val wb314EdgeTest = providers.gradleProperty("wb314EdgeTest").map { it.toBooleanStrict() }.orElse(false)
val wb314SoftEdgeTest = providers.gradleProperty("wb314SoftEdgeTest").map { it.toBooleanStrict() }.orElse(false)
val wb314JawTest = providers.gradleProperty("wb314JawTest").map { it.toBooleanStrict() }.orElse(false)
val wb314HighlightTest = providers.gradleProperty("wb314HighlightTest").map { it.toBooleanStrict() }.orElse(false)
val wb314FaceMeasurementTest = providers.gradleProperty("wb314FaceMeasurementTest").map { it.toBooleanStrict() }.orElse(false)
val wb314DiffuseBacklightTest = providers.gradleProperty("wb314DiffuseBacklightTest").map { it.toBooleanStrict() }.orElse(false)
val wb314WarmCastTest = providers.gradleProperty("wb314WarmCastTest").map { it.toBooleanStrict() }.orElse(false)
val wb314CombinedTest = providers.gradleProperty("wb314CombinedTest").map { it.toBooleanStrict() }.orElse(false)
val wb314DecisionTrace = providers.gradleProperty("wb314DecisionTrace").map { it.toBooleanStrict() }.orElse(false)
val wb314ShadowLiftTest = providers.gradleProperty("wb314ShadowLiftTest").map { it.toBooleanStrict() }.orElse(false)
val wb314BrightColourTest = providers.gradleProperty("wb314BrightColourTest").map { it.toBooleanStrict() }.orElse(false)
val wb314PhoneBrightnessFitSha = providers.gradleProperty("wb314PhoneBrightnessFitSha").orElse("")
val wb314QuarterTurnTest = providers.gradleProperty("wb314QuarterTurnTest").map { it.toBooleanStrict() }.orElse(false)
val wb314DarkFaceStrengthTest = providers.gradleProperty("wb314DarkFaceStrengthTest").map { it.toBooleanStrict() }.orElse(false)
val wb314DefaultCorrectionTest = providers.gradleProperty("wb314DefaultCorrectionTest").map { it.toBooleanStrict() }.orElse(false)
val wb314JawSeamTest = providers.gradleProperty("wb314JawSeamTest").map { it.toBooleanStrict() }.orElse(false)

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
        manifestPlaceholders["pickerLabel"] = "@string/app_name"
    }

    buildTypes {
        debug {
            val enablePickerFixes = wb314PickerTest.get()
            val enableEdgeRepair = wb314EdgeTest.get()
            val enableSoftEdge = wb314SoftEdgeTest.get()
            val enableJawRepair = wb314JawTest.get()
            val enableHighlightGuard = wb314HighlightTest.get()
            val enableFaceMeasurementRetry = wb314FaceMeasurementTest.get()
            val enableDiffuseBacklight = wb314DiffuseBacklightTest.get()
            val enableWarmCast = wb314WarmCastTest.get()
            val enableCombined = wb314CombinedTest.get()
            val enableDecisionTrace = wb314DecisionTrace.get()
            val enableShadowLift = wb314ShadowLiftTest.get()
            val enableBrightColour = wb314BrightColourTest.get()
            val brightnessFit = wb314PhoneBrightnessFitSha.get()
            val enableQuarterTurn = wb314QuarterTurnTest.get()
            val enableDarkFaceStrength = wb314DarkFaceStrengthTest.get()
            val enableDefaultCorrection = wb314DefaultCorrectionTest.get()
            val enableJawSeam = wb314JawSeamTest.get()
            require(brightnessFit.isEmpty() || (enableBrightColour && Regex("[a-f0-9]{64}").matches(brightnessFit)))
            require(!enableQuarterTurn || brightnessFit.isNotEmpty())
            require(!enableDarkFaceStrength || enableQuarterTurn)
            require(!enableDefaultCorrection || enableDarkFaceStrength)
            require(!enableJawSeam || enableDefaultCorrection)
            require(!enableEdgeRepair || enablePickerFixes) { "The edge test requires the picker test build." }
            require(!enableJawRepair || enableSoftEdge) { "The jaw test requires the soft-edge test build." }
            require(!enableSoftEdge || (enablePickerFixes && !enableEdgeRepair)) {
                "The soft-edge test requires the picker test without support expansion."
            }
            require(!enableHighlightGuard || (enableSoftEdge && !enableJawRepair)) {
                "The highlight test requires the soft-edge test without jaw expansion."
            }
            require(!enableFaceMeasurementRetry || enableHighlightGuard) {
                "The face measurement test requires the highlight test build."
            }
            require(!enableDiffuseBacklight || enableFaceMeasurementRetry) {
                "The diffuse backlight test requires the face measurement test build."
            }
            require(!enableWarmCast || enableDiffuseBacklight) {
                "The warm cast test requires the diffuse backlight test build."
            }
            require(!enableCombined || enableWarmCast) {
                "The combined edit test requires the warm cast test build."
            }
            require(!enableDecisionTrace || (enableWarmCast && !enableCombined)) {
                "The decision trace uses the warm cast build with its existing edit policy."
            }
            require(!enableShadowLift || (enableWarmCast && !enableCombined && !enableDecisionTrace)) {
                "The shadow lift test uses the warm cast build without other decision experiments."
            }
            require(!enableBrightColour || enableShadowLift) {
                "The bright colour test requires the shadow lift test build."
            }
            buildConfigField("boolean", "WB314_PICKER_FIXES", enablePickerFixes.toString())
            buildConfigField("boolean", "WB314_EDGE_REPAIR", enableEdgeRepair.toString())
            buildConfigField("boolean", "WB314_SOFT_EDGE", enableSoftEdge.toString())
            buildConfigField("boolean", "WB314_JAW_REPAIR", enableJawRepair.toString())
            buildConfigField("boolean", "WB314_HIGHLIGHT_TEST", enableHighlightGuard.toString())
            buildConfigField("boolean", "WB314_FACE_MEASUREMENT_TEST", enableFaceMeasurementRetry.toString())
            buildConfigField("boolean", "WB314_DIFFUSE_BACKLIGHT_TEST", enableDiffuseBacklight.toString())
            buildConfigField("boolean", "WB314_WARM_CAST_TEST", enableWarmCast.toString())
            buildConfigField("boolean", "WB314_COMBINED_TEST", enableCombined.toString())
            buildConfigField("boolean", "WB314_DECISION_TRACE", enableDecisionTrace.toString())
            buildConfigField("boolean", "WB314_SHADOW_LIFT_TEST", enableShadowLift.toString())
            buildConfigField("boolean", "WB314_BRIGHT_COLOUR_TEST", enableBrightColour.toString())
            buildConfigField("String", "WB314_PHONE_BRIGHTNESS_FIT_SHA", "\"$brightnessFit\"")
            buildConfigField("boolean", "WB314_QUARTER_TURN_TEST", enableQuarterTurn.toString())
            buildConfigField("boolean", "WB314_DARK_FACE_STRENGTH_TEST", enableDarkFaceStrength.toString())
            buildConfigField("boolean", "WB314_DEFAULT_CORRECTION_TEST", enableDefaultCorrection.toString())
            buildConfigField("boolean", "WB314_JAW_SEAM_TEST", enableJawSeam.toString())
            if (enablePickerFixes) {
                applicationIdSuffix = when {
                    enableJawRepair -> ".pickertest.jaw"
                    enableSoftEdge -> ".pickertest.soft"
                    enableEdgeRepair -> ".pickertest.edge"
                    else -> ".pickertest"
                }
                versionNameSuffix = when {
                    enableJawSeam -> "-wb314-highlight-test.25"
                    enableDefaultCorrection -> "-wb314-highlight-test.24"
                    enableDarkFaceStrength -> "-wb314-highlight-test.23"
                    enableQuarterTurn -> "-wb314-highlight-test.22"
                    brightnessFit.isNotEmpty() -> "-wb314-highlight-test.21"
                    enableBrightColour -> "-wb314-highlight-test.20"
                    enableShadowLift -> "-wb314-highlight-test.19"
                    enableDecisionTrace -> "-wb314-highlight-test.18"
                    enableCombined -> "-wb314-highlight-test.17"
                    enableWarmCast -> "-wb314-highlight-test.16"
                    enableDiffuseBacklight -> "-wb314-highlight-test.12"
                    enableFaceMeasurementRetry -> "-wb314-highlight-test.9"
                    enableHighlightGuard -> "-wb314-highlight-test.6"
                    enableJawRepair -> "-wb314-jaw-test.1"
                    enableSoftEdge -> "-wb314-soft-edge-test.5"
                    enableEdgeRepair -> "-wb314-edge-test.1"
                    else -> "-wb314-picker-test.2"
                }
                val appLabel = when {
                    enableJawRepair -> "TrueHue Jaw Test"
                    enableSoftEdge -> "TrueHue Soft Edge Test"
                    enableEdgeRepair -> "TrueHue Edge Test"
                    else -> "TrueHue Picker Test"
                }
                resValue("string", "picker_app_name", appLabel)
                manifestPlaceholders["pickerLabel"] = "@string/picker_app_name"
            }
        }
        release {
            buildConfigField("boolean", "WB314_PICKER_FIXES", "false")
            buildConfigField("boolean", "WB314_EDGE_REPAIR", "false")
            buildConfigField("boolean", "WB314_SOFT_EDGE", "false")
            buildConfigField("boolean", "WB314_JAW_REPAIR", "false")
            buildConfigField("boolean", "WB314_HIGHLIGHT_TEST", "false")
            buildConfigField("boolean", "WB314_FACE_MEASUREMENT_TEST", "false")
            buildConfigField("boolean", "WB314_DIFFUSE_BACKLIGHT_TEST", "false")
            buildConfigField("boolean", "WB314_WARM_CAST_TEST", "false")
            buildConfigField("boolean", "WB314_COMBINED_TEST", "false")
            buildConfigField("boolean", "WB314_DECISION_TRACE", "false")
            buildConfigField("boolean", "WB314_SHADOW_LIFT_TEST", "false")
            buildConfigField("boolean", "WB314_BRIGHT_COLOUR_TEST", "false")
            buildConfigField("String", "WB314_PHONE_BRIGHTNESS_FIT_SHA", "\"\"")
            buildConfigField("boolean", "WB314_QUARTER_TURN_TEST", "false")
            buildConfigField("boolean", "WB314_DARK_FACE_STRENGTH_TEST", "false")
            buildConfigField("boolean", "WB314_DEFAULT_CORRECTION_TEST", "false")
            buildConfigField("boolean", "WB314_JAW_SEAM_TEST", "false")
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
        buildConfig = true
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
