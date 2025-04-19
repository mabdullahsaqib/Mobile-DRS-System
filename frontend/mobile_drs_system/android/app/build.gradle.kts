plugins {
    id("com.android.application")
    id("kotlin-android")
    // The Flutter Gradle Plugin must be applied after the Android and Kotlin Gradle plugins.
    id("dev.flutter.flutter-gradle-plugin")
}

android {
    namespace = "com.example.mobile_drs_system" // Make sure to set this to your app’s namespace
    compileSdk = 35  // Use SDK 34 to match ARCore's requirements

    defaultConfig {
        applicationId = "com.example.mobile_drs_system"
        minSdk = 24  // Update to a higher minimum SDK version if required
        targetSdk = 34  // Set to SDK 34, as per ARCore's requirements
        versionCode = 1
        versionName = "1.0"
    }

    ndkVersion = "27.0.12077973" // Make sure to set this to match ARCore's NDK version

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }

    kotlinOptions {
        jvmTarget = JavaVersion.VERSION_11.toString()
    }

    buildTypes {
    getByName("release") {
        signingConfig = signingConfigs.getByName("debug")
        isMinifyEnabled = false
        isShrinkResources = false
        
    }
}

}


flutter {
    source = "../.."
}
