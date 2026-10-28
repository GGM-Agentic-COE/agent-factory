# KB-L1: Kotlin/Compose Project Scaffold

> Production-ready Android project scaffold — MVVM · Hilt · Room · Retrofit · Material 3 · Accessibility · CI

---

## KF1: Overview

This scaffold provides a complete, production-ready Kotlin/Jetpack Compose Android project structure following clean architecture (MVVM) with the following pillars:

- **Architecture**: MVVM with unidirectional data flow via `UiState` sealed interface
- **Dependency Injection**: Hilt with modular `@Module` classes for network, database, and repositories
- **Networking**: Retrofit + OkHttp with auth interceptor, correlation IDs, and 30-second timeouts
- **Persistence**: Room database with DAO pattern and offline-first repository strategy
- **UI**: Jetpack Compose with Material 3 design system, light/dark theme, reusable atoms
- **Accessibility**: Minimum 48dp touch targets, semantic descriptions, contrast-compliant colors
- **Navigation**: Type-safe sealed-class routes, single-Activity with `NavHost`, protected-route pattern
- **Security**: EncryptedSharedPreferences, FLAG_SECURE, ProGuard, no secrets in source
- **Testing**: JUnit 5, MockK, Turbine, Compose UI Test, Espresso — 80% coverage gate
- **CI/CD**: GitHub Actions pipeline — lint → build → test → accessibility → coverage → SCA → SAST → artifact

All dependency versions are pinned in a Gradle version catalog (`libs.versions.toml`). The scaffold targets **compileSdk 34**, **minSdk 26**, **targetSdk 34**.

---

## KF2: File Tree

```
project-root/
├── .github/
│   └── workflows/
│       └── ci.yml
├── app/
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/com/tasheel/app/
│   │   │   │   ├── TasheelApp.kt
│   │   │   │   ├── MainActivity.kt
│   │   │   │   ├── core/
│   │   │   │   │   ├── UiState.kt
│   │   │   │   │   └── di/
│   │   │   │   │       ├── NetworkModule.kt
│   │   │   │   │       ├── DatabaseModule.kt
│   │   │   │   │       └── RepositoryModule.kt
│   │   │   │   ├── data/
│   │   │   │   │   ├── api/
│   │   │   │   │   │   ├── TasheelApi.kt
│   │   │   │   │   │   └── AuthInterceptor.kt
│   │   │   │   │   ├── dto/
│   │   │   │   │   │   └── UserDto.kt
│   │   │   │   │   ├── db/
│   │   │   │   │   │   ├── AppDatabase.kt
│   │   │   │   │   │   └── UserDao.kt
│   │   │   │   │   └── repository/
│   │   │   │   │       └── UserRepositoryImpl.kt
│   │   │   │   ├── domain/
│   │   │   │   │   ├── model/
│   │   │   │   │   │   └── User.kt
│   │   │   │   │   └── usecase/
│   │   │   │   │       └── GetUserUseCase.kt
│   │   │   │   └── ui/
│   │   │   │       ├── theme/
│   │   │   │       │   ├── Color.kt
│   │   │   │       │   ├── Theme.kt
│   │   │   │       │   ├── Type.kt
│   │   │   │       │   └── Dimens.kt
│   │   │   │       ├── components/
│   │   │   │       │   ├── TasheelButton.kt
│   │   │   │       │   ├── TasheelTextField.kt
│   │   │   │       │   ├── TasheelCard.kt
│   │   │   │       │   ├── Badge.kt
│   │   │   │       │   ├── Skeleton.kt
│   │   │   │       │   └── ErrorState.kt
│   │   │   │       ├── navigation/
│   │   │   │       │   ├── Screen.kt
│   │   │   │       │   └── NavGraph.kt
│   │   │   │       ├── auth/
│   │   │   │       │   ├── LoginScreen.kt
│   │   │   │       │   └── LoginViewModel.kt
│   │   │   │       └── home/
│   │   │   │           ├── HomeScreen.kt
│   │   │   │           └── HomeViewModel.kt
│   │   │   ├── res/
│   │   │   └── AndroidManifest.xml
│   │   ├── test/
│   │   │   └── java/com/tasheel/app/
│   │   │       └── ui/home/HomeViewModelTest.kt
│   │   └── androidTest/
│   │       └── java/com/tasheel/app/
│   │           └── ui/home/HomeScreenTest.kt
│   ├── build.gradle.kts
│   └── proguard-rules.pro
├── build.gradle.kts
├── settings.gradle.kts
├── gradle/
│   └── libs.versions.toml
├── Dockerfile
└── README.md
```

---

## KF3: Version Catalog — `gradle/libs.versions.toml`

```toml
[versions]
kotlin              = "2.0.0"
agp                 = "8.3.2"
compose-bom         = "2024.02.00"
compose-compiler    = "1.5.11"
hilt                = "2.51"
navigation          = "2.7.7"
room                = "2.6.1"
retrofit            = "2.9.0"
okhttp              = "4.12.0"
coil                = "2.6.0"
workmanager         = "2.9.0"
coroutines          = "1.8.0"
lifecycle           = "2.7.0"
security-crypto     = "1.1.0-alpha06"
junit5              = "5.10.2"
mockk               = "1.13.10"
turbine             = "1.1.0"
espresso            = "3.5.1"

[libraries]
# Compose
compose-bom              = { group = "androidx.compose", name = "compose-bom", version.ref = "compose-bom" }
compose-ui               = { group = "androidx.compose.ui", name = "ui" }
compose-ui-tooling       = { group = "androidx.compose.ui", name = "ui-tooling" }
compose-material3        = { group = "androidx.compose.material3", name = "material3" }
compose-ui-test-junit4   = { group = "androidx.compose.ui", name = "ui-test-junit4" }
compose-ui-test-manifest = { group = "androidx.compose.ui", name = "ui-test-manifest" }

# Navigation
navigation-compose = { group = "androidx.navigation", name = "navigation-compose", version.ref = "navigation" }

# Hilt
hilt-android          = { group = "com.google.dagger", name = "hilt-android", version.ref = "hilt" }
hilt-compiler         = { group = "com.google.dagger", name = "hilt-android-compiler", version.ref = "hilt" }
hilt-navigation       = { group = "androidx.hilt", name = "hilt-navigation-compose", version = "1.2.0" }

# Room
room-runtime  = { group = "androidx.room", name = "room-runtime", version.ref = "room" }
room-ktx      = { group = "androidx.room", name = "room-ktx", version.ref = "room" }
room-compiler = { group = "androidx.room", name = "room-compiler", version.ref = "room" }

# Network
retrofit      = { group = "com.squareup.retrofit2", name = "retrofit", version.ref = "retrofit" }
retrofit-gson = { group = "com.squareup.retrofit2", name = "converter-gson", version.ref = "retrofit" }
okhttp        = { group = "com.squareup.okhttp3", name = "okhttp", version.ref = "okhttp" }
okhttp-logging = { group = "com.squareup.okhttp3", name = "logging-interceptor", version.ref = "okhttp" }

# Image
coil = { group = "io.coil-kt", name = "coil-compose", version.ref = "coil" }

# Lifecycle
lifecycle-runtime   = { group = "androidx.lifecycle", name = "lifecycle-runtime-compose", version.ref = "lifecycle" }
lifecycle-viewmodel = { group = "androidx.lifecycle", name = "lifecycle-viewmodel-compose", version.ref = "lifecycle" }

# Security
security-crypto = { group = "androidx.security", name = "security-crypto", version.ref = "security-crypto" }

# WorkManager
workmanager = { group = "androidx.work", name = "work-runtime-ktx", version.ref = "workmanager" }

# Coroutines
coroutines-core    = { group = "org.jetbrains.kotlinx", name = "kotlinx-coroutines-core", version.ref = "coroutines" }
coroutines-android = { group = "org.jetbrains.kotlinx", name = "kotlinx-coroutines-android", version.ref = "coroutines" }
coroutines-test    = { group = "org.jetbrains.kotlinx", name = "kotlinx-coroutines-test", version.ref = "coroutines" }

# Testing
junit5-api    = { group = "org.junit.jupiter", name = "junit-jupiter-api", version.ref = "junit5" }
junit5-engine = { group = "org.junit.jupiter", name = "junit-jupiter-engine", version.ref = "junit5" }
mockk         = { group = "io.mockk", name = "mockk", version.ref = "mockk" }
turbine       = { group = "app.cash.turbine", name = "turbine", version.ref = "turbine" }
espresso      = { group = "androidx.test.espresso", name = "espresso-core", version.ref = "espresso" }

[plugins]
android-application = { id = "com.android.application", version.ref = "agp" }
kotlin-android      = { id = "org.jetbrains.kotlin.android", version.ref = "kotlin" }
hilt                = { id = "com.google.dagger.hilt.android", version.ref = "hilt" }
ksp                 = { id = "com.google.devtools.ksp", version = "2.0.0-1.0.21" }
```

---

## KF4: `app/build.gradle.kts`

```kotlin
plugins {
    alias(libs.plugins.android.application)
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.hilt)
    alias(libs.plugins.ksp)
}

android {
    namespace = "com.tasheel.app"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.tasheel.app"
        minSdk = 26
        targetSdk = 34
        versionCode = 1
        versionName = "1.0.0"
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            isShrinkResources = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    buildFeatures {
        compose = true
        buildConfig = true
    }

    composeOptions {
        kotlinCompilerExtensionVersion = libs.versions.compose.compiler.get()
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    testOptions {
        unitTests.isReturnDefaultValues = true
    }
}

dependencies {
    // Compose BOM
    val composeBom = platform(libs.compose.bom)
    implementation(composeBom)
    androidTestImplementation(composeBom)

    implementation(libs.compose.ui)
    implementation(libs.compose.material3)
    implementation(libs.compose.ui.tooling)
    implementation(libs.navigation.compose)

    // Hilt
    implementation(libs.hilt.android)
    ksp(libs.hilt.compiler)
    implementation(libs.hilt.navigation)

    // Room
    implementation(libs.room.runtime)
    implementation(libs.room.ktx)
    ksp(libs.room.compiler)

    // Network
    implementation(libs.retrofit)
    implementation(libs.retrofit.gson)
    implementation(libs.okhttp)
    implementation(libs.okhttp.logging)

    // Image
    implementation(libs.coil)

    // Lifecycle
    implementation(libs.lifecycle.runtime)
    implementation(libs.lifecycle.viewmodel)

    // Security
    implementation(libs.security.crypto)

    // WorkManager
    implementation(libs.workmanager)

    // Coroutines
    implementation(libs.coroutines.core)
    implementation(libs.coroutines.android)

    // Testing
    testImplementation(libs.junit5.api)
    testRuntimeOnly(libs.junit5.engine)
    testImplementation(libs.mockk)
    testImplementation(libs.turbine)
    testImplementation(libs.coroutines.test)
    androidTestImplementation(libs.compose.ui.test.junit4)
    debugImplementation(libs.compose.ui.test.manifest)
    androidTestImplementation(libs.espresso)
}
```

### Project-level `build.gradle.kts`

```kotlin
plugins {
    alias(libs.plugins.android.application) apply false
    alias(libs.plugins.kotlin.android) apply false
    alias(libs.plugins.hilt) apply false
    alias(libs.plugins.ksp) apply false
}
```

### `settings.gradle.kts`

```kotlin
pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolution {
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "TasheelApp"
include(":app")
```

---

## KF5: Core Files

### `core/UiState.kt`

```kotlin
package com.tasheel.app.core

sealed interface UiState<out T> {
    data object Idle : UiState<Nothing>
    data object Loading : UiState<Nothing>
    data class Success<T>(val data: T) : UiState<T>
    data class Error(val message: String, val cause: Throwable? = null) : UiState<Nothing>
}
```

### `TasheelApp.kt`

```kotlin
package com.tasheel.app

import android.app.Application
import dagger.hilt.android.HiltAndroidApp

@HiltAndroidApp
class TasheelApp : Application()
```

### `MainActivity.kt`

```kotlin
package com.tasheel.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import dagger.hilt.android.AndroidEntryPoint
import com.tasheel.app.ui.navigation.NavGraph
import com.tasheel.app.ui.theme.TasheelTheme

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            TasheelTheme {
                NavGraph()
            }
        }
    }
}
```

### `AndroidManifest.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.INTERNET" />
    <application
        android:name=".TasheelApp"
        android:allowBackup="false"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:supportsRtl="true"
        android:theme="@style/Theme.TasheelApp">
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
```

---

## KF6: DI Modules

### `core/di/NetworkModule.kt`

```kotlin
package com.tasheel.app.core.di

import com.tasheel.app.data.api.AuthInterceptor
import com.tasheel.app.data.api.TasheelApi
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideOkHttpClient(authInterceptor: AuthInterceptor): OkHttpClient =
        OkHttpClient.Builder()
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .writeTimeout(30, TimeUnit.SECONDS)
            .addInterceptor(authInterceptor)
            .addInterceptor(HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            })
            .build()

    @Provides
    @Singleton
    fun provideRetrofit(client: OkHttpClient): Retrofit =
        Retrofit.Builder()
            .baseUrl("https://api.tasheel.app/")
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()

    @Provides
    @Singleton
    fun provideTasheelApi(retrofit: Retrofit): TasheelApi =
        retrofit.create(TasheelApi::class.java)
}
```

### `core/di/DatabaseModule.kt`

```kotlin
package com.tasheel.app.core.di

import android.content.Context
import androidx.room.Room
import com.tasheel.app.data.db.AppDatabase
import com.tasheel.app.data.db.UserDao
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {

    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): AppDatabase =
        Room.databaseBuilder(context, AppDatabase::class.java, "tasheel.db")
            .fallbackToDestructiveMigration()
            .build()

    @Provides
    fun provideUserDao(db: AppDatabase): UserDao = db.userDao()
}
```

### `core/di/RepositoryModule.kt`

```kotlin
package com.tasheel.app.core.di

import com.tasheel.app.data.repository.UserRepositoryImpl
import com.tasheel.app.domain.repository.UserRepository
import dagger.Binds
import dagger.Module
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {

    @Binds
    @Singleton
    abstract fun bindUserRepository(impl: UserRepositoryImpl): UserRepository
}
```

---

## KF7: API Client

### `data/api/AuthInterceptor.kt`

```kotlin
package com.tasheel.app.data.api

import android.content.SharedPreferences
import okhttp3.Interceptor
import okhttp3.Response
import java.util.UUID
import javax.inject.Inject

class AuthInterceptor @Inject constructor(
    private val prefs: SharedPreferences
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val token = prefs.getString("auth_token", null)
        val request = chain.request().newBuilder().apply {
            header("X-Correlation-ID", UUID.randomUUID().toString())
            if (!token.isNullOrBlank()) {
                header("Authorization", "Bearer $token")
            }
        }.build()
        return chain.proceed(request)
    }
}
```

### `data/api/TasheelApi.kt`

```kotlin
package com.tasheel.app.data.api

import com.tasheel.app.data.dto.UserDto
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Body
import retrofit2.http.Path

interface TasheelApi {

    @GET("users/{id}")
    suspend fun getUser(@Path("id") id: String): UserDto

    @GET("users")
    suspend fun getUsers(): List<UserDto>

    @POST("auth/login")
    suspend fun login(@Body credentials: Map<String, String>): Map<String, String>
}
```

---

## KF8: Design System

### `ui/theme/Color.kt`

```kotlin
package com.tasheel.app.ui.theme

import androidx.compose.ui.graphics.Color

// Primary
val Primary = Color(0xFF4F6EF7)
val PrimaryVariant = Color(0xFF3A56D4)
val OnPrimary = Color(0xFFFFFFFF)

// Neutrals
val Neutral50 = Color(0xFFFAFAFA)
val Neutral100 = Color(0xFFF5F5F5)
val Neutral200 = Color(0xFFEEEEEE)
val Neutral500 = Color(0xFF9E9E9E)
val Neutral800 = Color(0xFF424242)
val Neutral900 = Color(0xFF212121)

// Semantic
val Success = Color(0xFF4CAF50)
val Warning = Color(0xFFFF9800)
val Error = Color(0xFFE53935)
val Info = Color(0xFF2196F3)
```

### `ui/theme/Type.kt`

```kotlin
package com.tasheel.app.ui.theme

import androidx.compose.material3.Typography
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp

val TasheelTypography = Typography(
    displayLarge = TextStyle(fontSize = 32.sp, fontWeight = FontWeight.Bold, lineHeight = 40.sp),
    headlineMedium = TextStyle(fontSize = 24.sp, fontWeight = FontWeight.SemiBold, lineHeight = 32.sp),
    titleLarge = TextStyle(fontSize = 20.sp, fontWeight = FontWeight.Medium, lineHeight = 28.sp),
    bodyLarge = TextStyle(fontSize = 16.sp, fontWeight = FontWeight.Normal, lineHeight = 24.sp),
    bodyMedium = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Normal, lineHeight = 20.sp),
    labelLarge = TextStyle(fontSize = 14.sp, fontWeight = FontWeight.Medium, lineHeight = 20.sp),
    labelSmall = TextStyle(fontSize = 11.sp, fontWeight = FontWeight.Medium, lineHeight = 16.sp),
)
```

### `ui/theme/Dimens.kt`

```kotlin
package com.tasheel.app.ui.theme

import androidx.compose.ui.unit.dp

object Dimens {
    val SpacingXs = 4.dp
    val SpacingSm = 8.dp
    val SpacingMd = 16.dp
    val SpacingLg = 24.dp
    val SpacingXl = 32.dp

    val RadiusSm = 4.dp
    val RadiusMd = 8.dp
    val RadiusLg = 16.dp
    val RadiusFull = 999.dp

    val TouchTarget = 48.dp
}
```

### `ui/theme/Theme.kt`

```kotlin
package com.tasheel.app.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.*
import androidx.compose.runtime.Composable

private val LightColors = lightColorScheme(
    primary = Primary,
    onPrimary = OnPrimary,
    background = Neutral50,
    surface = Neutral100,
    onBackground = Neutral900,
    onSurface = Neutral800,
    error = Error,
)

private val DarkColors = darkColorScheme(
    primary = Primary,
    onPrimary = OnPrimary,
    background = Neutral900,
    surface = Neutral800,
    onBackground = Neutral50,
    onSurface = Neutral200,
    error = Error,
)

@Composable
fun TasheelTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    MaterialTheme(
        colorScheme = if (darkTheme) DarkColors else LightColors,
        typography = TasheelTypography,
        content = content
    )
}
```

### Atom Components

#### `ui/components/TasheelButton.kt`

```kotlin
package com.tasheel.app.ui.components

import androidx.compose.foundation.layout.heightIn
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import com.tasheel.app.ui.theme.Dimens
import com.tasheel.app.ui.theme.TasheelTheme

@Composable
fun TasheelButton(text: String, onClick: () -> Unit, modifier: Modifier = Modifier, enabled: Boolean = true) {
    Button(onClick = onClick, modifier = modifier.heightIn(min = Dimens.TouchTarget), enabled = enabled) {
        Text(text)
    }
}

@Preview(name = "Light") @Preview(name = "Dark", uiMode = android.content.res.Configuration.UI_MODE_NIGHT_YES)
@Composable private fun Preview() = TasheelTheme { TasheelButton("Submit", onClick = {}) }
```

#### `ui/components/TasheelTextField.kt`

```kotlin
package com.tasheel.app.ui.components

import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import com.tasheel.app.ui.theme.TasheelTheme

@Composable
fun TasheelTextField(value: String, onValueChange: (String) -> Unit, label: String, modifier: Modifier = Modifier) {
    OutlinedTextField(value = value, onValueChange = onValueChange, label = { Text(label) }, modifier = modifier.fillMaxWidth())
}

@Preview(name = "Light") @Preview(name = "Dark", uiMode = android.content.res.Configuration.UI_MODE_NIGHT_YES)
@Composable private fun Preview() = TasheelTheme { TasheelTextField("", onValueChange = {}, label = "Email") }
```

#### `ui/components/TasheelCard.kt`

```kotlin
package com.tasheel.app.ui.components

import androidx.compose.foundation.layout.padding
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import com.tasheel.app.ui.theme.Dimens
import com.tasheel.app.ui.theme.TasheelTheme

@Composable
fun TasheelCard(modifier: Modifier = Modifier, content: @Composable () -> Unit) {
    Card(modifier = modifier, shape = MaterialTheme.shapes.medium) {
        Surface(modifier = Modifier.padding(Dimens.SpacingMd)) { content() }
    }
}

@Preview(name = "Light") @Preview(name = "Dark", uiMode = android.content.res.Configuration.UI_MODE_NIGHT_YES)
@Composable private fun Preview() = TasheelTheme { TasheelCard { Text("Card content") } }
```

#### `ui/components/Badge.kt`

```kotlin
package com.tasheel.app.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.tooling.preview.Preview
import com.tasheel.app.ui.theme.Dimens
import com.tasheel.app.ui.theme.TasheelTheme

@Composable
fun Badge(text: String, modifier: Modifier = Modifier) {
    Text(
        text = text,
        style = MaterialTheme.typography.labelSmall,
        color = MaterialTheme.colorScheme.onPrimary,
        modifier = modifier
            .clip(RoundedCornerShape(Dimens.RadiusFull))
            .background(MaterialTheme.colorScheme.primary)
            .padding(horizontal = Dimens.SpacingSm, vertical = Dimens.SpacingXs)
    )
}

@Preview(name = "Light") @Preview(name = "Dark", uiMode = android.content.res.Configuration.UI_MODE_NIGHT_YES)
@Composable private fun Preview() = TasheelTheme { Badge("New") }
```

#### `ui/components/Skeleton.kt`

```kotlin
package com.tasheel.app.ui.components

import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import com.tasheel.app.ui.theme.Dimens
import com.tasheel.app.ui.theme.TasheelTheme

@Composable
fun Skeleton(width: Dp = 200.dp, height: Dp = 20.dp, modifier: Modifier = Modifier) {
    val transition = rememberInfiniteTransition(label = "skeleton")
    val alpha by transition.animateFloat(
        initialValue = 0.3f, targetValue = 0.7f,
        animationSpec = infiniteRepeatable(tween(800), RepeatMode.Reverse), label = "alpha"
    )
    Box(
        modifier = modifier
            .size(width, height)
            .clip(RoundedCornerShape(Dimens.RadiusSm))
            .background(MaterialTheme.colorScheme.onSurface.copy(alpha = alpha))
    )
}

@Preview(name = "Light") @Preview(name = "Dark", uiMode = android.content.res.Configuration.UI_MODE_NIGHT_YES)
@Composable private fun Preview() = TasheelTheme { Skeleton() }
```

---

## KF9: Navigation

### `ui/navigation/Screen.kt`

```kotlin
package com.tasheel.app.ui.navigation

sealed class Screen(val route: String) {
    data object Login : Screen("login")
    data object Home : Screen("home")
    data object Profile : Screen("profile/{userId}") {
        fun createRoute(userId: String) = "profile/$userId"
    }
}
```

### `ui/navigation/NavGraph.kt`

```kotlin
package com.tasheel.app.ui.navigation

import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.tasheel.app.ui.auth.LoginScreen
import com.tasheel.app.ui.auth.LoginViewModel
import com.tasheel.app.ui.home.HomeScreen
import com.tasheel.app.ui.home.HomeViewModel

@Composable
fun NavGraph(startDestination: String = Screen.Login.route) {
    val navController = rememberNavController()

    NavHost(navController = navController, startDestination = startDestination) {
        composable(Screen.Login.route) {
            val viewModel: LoginViewModel = hiltViewModel()
            LoginScreen(viewModel = viewModel, onLoginSuccess = {
                navController.navigate(Screen.Home.route) {
                    popUpTo(Screen.Login.route) { inclusive = true }
                }
            })
        }
        composable(Screen.Home.route) {
            ProtectedRoute {
                val viewModel: HomeViewModel = hiltViewModel()
                HomeScreen(viewModel = viewModel)
            }
        }
    }
}

@Composable
fun ProtectedRoute(content: @Composable () -> Unit) {
    // In production: check auth state from a shared ViewModel or token store.
    // If unauthenticated, navigate back to Login.
    content()
}
```

---

## KF10: Error Handling

### `ui/components/ErrorState.kt`

```kotlin
package com.tasheel.app.ui.components

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.tooling.preview.Preview
import com.tasheel.app.ui.theme.Dimens
import com.tasheel.app.ui.theme.TasheelTheme

@Composable
fun ErrorState(message: String, onRetry: () -> Unit, modifier: Modifier = Modifier) {
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(Dimens.SpacingLg)
            .semantics { contentDescription = "Error: $message" },
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(text = message, style = MaterialTheme.typography.bodyLarge, color = MaterialTheme.colorScheme.error)
        Spacer(modifier = Modifier.height(Dimens.SpacingMd))
        TasheelButton(text = "Retry", onClick = onRetry)
    }
}

@Preview(name = "Light") @Preview(name = "Dark", uiMode = android.content.res.Configuration.UI_MODE_NIGHT_YES)
@Composable private fun Preview() = TasheelTheme { ErrorState("Something went wrong", onRetry = {}) }
```

### ViewModel Error Pattern

Every ViewModel follows this pattern for error handling:

```kotlin
// In any ViewModel
fun loadData() {
    viewModelScope.launch {
        _uiState.value = UiState.Loading
        try {
            val result = useCase()
            _uiState.value = UiState.Success(result)
        } catch (e: Exception) {
            _uiState.value = UiState.Error(
                message = e.localizedMessage ?: "An unexpected error occurred",
                cause = e
            )
        }
    }
}
```

Screens observe `UiState` and render accordingly:

```kotlin
@Composable
fun <T> HandleUiState(state: UiState<T>, onRetry: () -> Unit, content: @Composable (T) -> Unit) {
    when (state) {
        is UiState.Idle -> {}
        is UiState.Loading -> Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) { CircularProgressIndicator() }
        is UiState.Error -> ErrorState(message = state.message, onRetry = onRetry)
        is UiState.Success -> content(state.data)
    }
}
```

---

## KF11: Security

### EncryptedSharedPreferences for Tokens

```kotlin
package com.tasheel.app.core.di

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object SecurityModule {

    @Provides
    @Singleton
    fun provideMasterKey(@ApplicationContext context: Context): MasterKey =
        MasterKey.Builder(context).setKeyScheme(MasterKey.KeyScheme.AES256_GCM).build()

    @Provides
    @Singleton
    fun provideEncryptedPrefs(@ApplicationContext context: Context, masterKey: MasterKey): SharedPreferences =
        EncryptedSharedPreferences.create(
            context, "tasheel_secure_prefs", masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )
}
```

### FLAG_SECURE on Sensitive Screens

```kotlin
// Apply in any Activity or composable hosting sensitive content
DisposableEffect(Unit) {
    val window = (context as? Activity)?.window
    window?.setFlags(WindowManager.LayoutParams.FLAG_SECURE, WindowManager.LayoutParams.FLAG_SECURE)
    onDispose { window?.clearFlags(WindowManager.LayoutParams.FLAG_SECURE) }
}
```

### Security Rules

- **No secrets in BuildConfig** — inject API keys via CI environment variables at build time
- **ProGuard enabled** for release builds (see KF14)
- **Certificate pinning** — configure via OkHttp `CertificatePinner` for production domains
- **Network security config** — restrict cleartext traffic in `AndroidManifest.xml`

---

## KF12: Testing Setup

### Test Dependencies (from KF4)

| Scope | Library | Version |
|-------|---------|---------|
| `testImplementation` | JUnit 5 API | 5.10.2 |
| `testRuntimeOnly` | JUnit 5 Engine | 5.10.2 |
| `testImplementation` | MockK | 1.13.10 |
| `testImplementation` | Turbine | 1.1.0 |
| `testImplementation` | Coroutines Test | 1.8.0 |
| `androidTestImplementation` | Compose UI Test | BOM |
| `debugImplementation` | Compose UI Test Manifest | BOM |
| `androidTestImplementation` | Espresso Core | 3.5.1 |

### Sample ViewModel Test — `HomeViewModelTest.kt`

```kotlin
package com.tasheel.app.ui.home

import app.cash.turbine.test
import com.tasheel.app.core.UiState
import com.tasheel.app.domain.model.User
import com.tasheel.app.domain.usecase.GetUserUseCase
import io.mockk.coEvery
import io.mockk.mockk
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.*
import org.junit.jupiter.api.*
import org.junit.jupiter.api.Assertions.assertEquals

@OptIn(ExperimentalCoroutinesApi::class)
class HomeViewModelTest {

    private val getUserUseCase: GetUserUseCase = mockk()
    private lateinit var viewModel: HomeViewModel
    private val testDispatcher = UnconfinedTestDispatcher()

    @BeforeEach
    fun setup() {
        Dispatchers.setMain(testDispatcher)
        viewModel = HomeViewModel(getUserUseCase)
    }

    @AfterEach
    fun tearDown() { Dispatchers.resetMain() }

    @Test
    fun `loadUser emits Success`() = runTest {
        val user = User(id = "1", name = "Test")
        coEvery { getUserUseCase("1") } returns user

        viewModel.uiState.test {
            viewModel.loadUser("1")
            assertEquals(UiState.Idle, awaitItem())
            assertEquals(UiState.Loading, awaitItem())
            assertEquals(UiState.Success(user), awaitItem())
        }
    }

    @Test
    fun `loadUser emits Error on failure`() = runTest {
        coEvery { getUserUseCase("1") } throws RuntimeException("Network error")

        viewModel.uiState.test {
            viewModel.loadUser("1")
            assertEquals(UiState.Idle, awaitItem())
            assertEquals(UiState.Loading, awaitItem())
            val error = awaitItem()
            assert(error is UiState.Error)
        }
    }
}
```

### Sample Compose Test — `HomeScreenTest.kt`

```kotlin
package com.tasheel.app.ui.home

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createComposeRule
import com.tasheel.app.ui.components.ErrorState
import com.tasheel.app.ui.theme.TasheelTheme
import org.junit.Rule
import org.junit.Test

class HomeScreenTest {

    @get:Rule val composeTestRule = createComposeRule()

    @Test
    fun errorState_displaysMessageAndRetryButton() {
        composeTestRule.setContent {
            TasheelTheme { ErrorState(message = "Something went wrong", onRetry = {}) }
        }
        composeTestRule.onNodeWithText("Something went wrong").assertIsDisplayed()
        composeTestRule.onNodeWithText("Retry").assertIsDisplayed()
    }

    @Test
    fun retryButton_meetsMinTouchTarget() {
        composeTestRule.setContent {
            TasheelTheme { ErrorState(message = "Error", onRetry = {}) }
        }
        composeTestRule.onNodeWithText("Retry")
            .assertHeightIsAtLeast(48.dp)
    }
}
```

---

## KF13: GitHub Actions CI

### `.github/workflows/ci.yml`

```yaml
name: Android CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: 17 }
      - name: Run ktlint
        run: ./gradlew ktlintCheck

  build:
    needs: lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: 17 }
      - uses: gradle/actions/setup-gradle@v3
      - run: ./gradlew assembleDebug

  unit-test:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: 17 }
      - uses: gradle/actions/setup-gradle@v3
      - run: ./gradlew testDebugUnitTest
      - name: Publish test results
        uses: mikepenz/action-junit-report@v4
        if: always()
        with: { report_paths: "**/build/test-results/**/TEST-*.xml" }

  ui-test:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: 17 }
      - name: Run UI tests on emulator
        uses: reactivecircus/android-emulator-runner@v2
        with:
          api-level: 34
          arch: x86_64
          script: ./gradlew connectedDebugAndroidTest

  accessibility:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: 17 }
      - name: Accessibility check
        uses: reactivecircus/android-emulator-runner@v2
        with:
          api-level: 34
          arch: x86_64
          script: ./gradlew connectedDebugAndroidTest -Pandroid.testInstrumentationRunnerArguments.class=com.tasheel.app.AccessibilityTest

  coverage:
    needs: unit-test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: 17 }
      - uses: gradle/actions/setup-gradle@v3
      - run: ./gradlew koverVerify
      - name: Enforce ≥80% coverage
        run: ./gradlew koverVerify -Pkover.minCoverage=80

  sca:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Snyk dependency scan
        uses: snyk/actions/gradle@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high

  sast:
    needs: build
    runs-on: ubuntu-latest
    permissions:
      security-events: write
    steps:
      - uses: actions/checkout@v4
      - name: Initialize CodeQL
        uses: github/codeql-action/init@v3
        with: { languages: java-kotlin }
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: 17 }
      - run: ./gradlew assembleDebug
      - name: Perform CodeQL Analysis
        uses: github/codeql-action/analyze@v3

  artifact:
    needs: [unit-test, ui-test, coverage, sca, sast]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: 17 }
      - uses: gradle/actions/setup-gradle@v3
      - run: ./gradlew assembleRelease
      - uses: actions/upload-artifact@v4
        with:
          name: apk-release
          path: app/build/outputs/apk/release/*.apk
```

### `Dockerfile` (for CI)

```dockerfile
FROM eclipse-temurin:17-jdk
ENV ANDROID_SDK_ROOT=/opt/android-sdk
RUN apt-get update && apt-get install -y unzip wget && \
    mkdir -p $ANDROID_SDK_ROOT/cmdline-tools && \
    wget -q https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip -O /tmp/sdk.zip && \
    unzip -q /tmp/sdk.zip -d $ANDROID_SDK_ROOT/cmdline-tools && \
    mv $ANDROID_SDK_ROOT/cmdline-tools/cmdline-tools $ANDROID_SDK_ROOT/cmdline-tools/latest && \
    rm /tmp/sdk.zip
ENV PATH="$PATH:$ANDROID_SDK_ROOT/cmdline-tools/latest/bin:$ANDROID_SDK_ROOT/platform-tools"
RUN yes | sdkmanager --licenses > /dev/null && \
    sdkmanager "platform-tools" "platforms;android-34" "build-tools;34.0.0"
WORKDIR /app
COPY . .
RUN chmod +x ./gradlew
```

---

## KF14: ProGuard Rules

### `app/proguard-rules.pro`

```proguard
# --- Retrofit ---
-keepattributes Signature
-keepattributes *Annotation*
-keep,allowobfuscation interface retrofit2.** { *; }
-keep class retrofit2.** { *; }
-keepclassmembers,allowshrinking,allowobfuscation interface * {
    @retrofit2.http.* <methods>;
}
-dontwarn retrofit2.**

# --- OkHttp ---
-dontwarn okhttp3.**
-dontwarn okio.**

# --- Gson ---
-keep class com.tasheel.app.data.dto.** { *; }
-keepclassmembers class * { @com.google.gson.annotations.SerializedName <fields>; }

# --- Hilt ---
-keep class dagger.hilt.** { *; }
-keep class * extends dagger.hilt.android.internal.managers.ViewComponentManager$FragmentContextWrapper { *; }

# --- Room ---
-keep class * extends androidx.room.RoomDatabase { *; }
-keep @androidx.room.Entity class * { *; }
-keep @androidx.room.Dao interface * { *; }

# --- Compose ---
-keep class androidx.compose.** { *; }
-dontwarn androidx.compose.**

# --- Kotlin Coroutines ---
-keepnames class kotlinx.coroutines.internal.MainDispatcherFactory {}
-keepnames class kotlinx.coroutines.CoroutineExceptionHandler {}
```

---

## KF15: Scaffold Checklist

Before considering the scaffold complete, verify all 15 checks:

| # | Check | Command / Verification |
|---|-------|----------------------|
| 1 | Build succeeds | `./gradlew assembleDebug` exits 0 |
| 2 | Lint passes | `./gradlew ktlintCheck` exits 0 |
| 3 | Unit tests pass | `./gradlew testDebugUnitTest` exits 0 |
| 4 | UI tests pass | `./gradlew connectedDebugAndroidTest` exits 0 |
| 5 | Accessibility passes | Touch targets ≥ 48dp, semantic descriptions present |
| 6 | Light theme renders | Preview composables render correctly in light mode |
| 7 | Dark theme renders | Preview composables render correctly in dark mode |
| 8 | Navigation works | Login → Home flow completes, back stack correct |
| 9 | Offline save works | Room DAO insert/query returns expected data |
| 10 | No secrets in source | `grep -r "API_KEY\|SECRET" --include="*.kt" app/` returns empty |
| 11 | Encrypted storage | Tokens stored via `EncryptedSharedPreferences` only |
| 12 | ProGuard rules valid | `./gradlew assembleRelease` succeeds without missing class warnings |
| 13 | CI pipeline passes | GitHub Actions workflow completes green on push |
| 14 | Coverage ≥ 80% | `./gradlew koverVerify` with 80% threshold passes |
| 15 | README complete | README.md contains: setup, architecture, build, test, deploy sections |

---

*End of KB-L1-Kotlin-Compose-Scaffold*

---

## Cross-References to Enterprise Architecture

| KF Section | EA/KS/MC Reference | Alignment |
|-----------|-------------------|-----------|
| KF1 Overview | EA1 Technology Stack | Kotlin 2.0, Compose, Hilt per EA1 mandatory list |
| KF5 Core (MVVM) | EA10 Mobile Architecture, MC1 | ViewModel + StateFlow, single Activity |
| KF6 DI Modules | EA2 Architecture Patterns | Dependency injection via Hilt per EA2 |
| KF7 API Client | EA3 API Standards, MC7 | Correlation ID, 30s timeout, auth interceptor |
| KF8 Design System | EA11 Design System, MC6 | Tokens, atomic components, light/dark, @Preview |
| KF9 Navigation | EA10 Mobile Architecture, MC5 | Navigation Compose, deep linking |
| KF10 Error Handling | EA2 Error Handling, MC11 | UiState sealed class, user-friendly messages |
| KF11 Security | EA5 Security, MC8 | EncryptedSharedPreferences, FLAG_SECURE, no secrets |
| KF12 Testing | EA14 Testing Standards, MC10 | 80% coverage, unit + UI + accessibility |
| KF13 CI Pipeline | EA6 Deployment, EA14 | lint → build → test → SCA → SAST → artifact |
| KF14 ProGuard | EA5 Security | Obfuscation for release builds |
