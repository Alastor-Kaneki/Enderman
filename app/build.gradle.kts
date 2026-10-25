plugins { id("com.android.application"); id("org.jetbrains.kotlin.android") }
android { namespace = "com.alastor.backdrops"; compileSdk = 35
 defaultConfig { applicationId = "com.alastor.backdrops"; minSdk = 26; targetSdk = 35; versionCode = 1; versionName = "The Wallpaper Goblin Has Pockets" }
 compileOptions { sourceCompatibility = JavaVersion.VERSION_17; targetCompatibility = JavaVersion.VERSION_17 }
 kotlinOptions { jvmTarget = "17" }
}