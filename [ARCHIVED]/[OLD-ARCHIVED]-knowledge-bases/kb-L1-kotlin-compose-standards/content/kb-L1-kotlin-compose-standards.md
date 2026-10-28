# Kotlin / Jetpack Compose Coding Standards (KS1–KS17)

> **Layer:** L1 — Technology-specific standards
> **Source:** Tasheel Finance `loan-app-ui` codebase
> **Stack:** Kotlin 2.0 · Jetpack Compose · Material Design 3 · Hilt · Room · Retrofit
> **Last reviewed:** 2026-04-21

---

## KS1 — Technology Stack

All mobile projects MUST use the following locked versions.

| Category | Technology | Version |
|---|---|---|
| Language | Kotlin | 2.0 |
| UI Framework | Jetpack Compose (BOM) | 2024.02 |
| Design System | Material Design 3 | via Compose BOM |
| DI | Hilt | 2.51 |
| Navigation | Navigation Compose | 2.7.7 |
| Local DB | Room | 2.6.1 |
| HTTP Client | Retrofit | 2.9.0 |
| HTTP Engine | OkHttp | 4.12.0 |
| Image Loading | Coil | latest stable |
| Background Work | WorkManager | latest stable |
| compileSdk | Android SDK | 34 |
| minSdk | Android SDK | 26 |
| JVM Target | JDK | 17 |

### Gradle Configuration (app/build.gradle.kts)

```kotlin
android {
    compileSdk = 34
    defaultConfig {
        minSdk = 26
        targetSdk = 34
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }
    buildFeatures {
        compose = true
        buildConfig = true
    }
}

dependencies {
    // Compose BOM — single version control
    val composeBom = platform("androidx.compose:compose-bom:2024.02.00")
    implementation(composeBom)
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.ui:ui-tooling-preview")
    debugImplementation("androidx.compose.ui:ui-tooling")

    // Navigation
    implementation("androidx.navigation:navigation-compose:2.7.7")

    // Hilt
    implementation("com.google.dagger:hilt-android:2.51")
    kapt("com.google.dagger:hilt-android-compiler:2.51")
    implementation("androidx.hilt:hilt-navigation-compose:1.2.0")

    // Networking
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.retrofit2:converter-gson:2.9.0")
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.12.0")

    // Room
    implementation("androidx.room:room-runtime:2.6.1")
    implementation("androidx.room:room-ktx:2.6.1")
    kapt("androidx.room:room-compiler:2.6.1")

    // Image loading
    implementation("io.coil-kt:coil-compose:2.6.0")

    // WorkManager
    implementation("androidx.work:work-runtime-ktx:2.9.0")
}
```

**Rules:**
- MUST NOT add dependencies outside this list without architecture review.
- MUST use Compose BOM for all Compose library versions.
- MUST NOT use `accompanist` libraries that have been absorbed into core Compose.

---

## KS2 — Project Structure

All modules follow clean-architecture layering under `app/src/main/java/com/tasheel/finance/`.

```
app/
├── src/
│   ├── main/
│   │   ├── java/com/tasheel/finance/
│   │   │   ├── core/
│   │   │   │   ├── di/                  # Hilt modules
│   │   │   │   ├── UiState.kt           # Shared sealed interface
│   │   │   │   └── Constants.kt
│   │   │   ├── data/
│   │   │   │   ├── api/                 # Retrofit interfaces
│   │   │   │   │   └── dto/             # Request/Response DTOs
│   │   │   │   ├── db/                  # Room database, entities, DAOs
│   │   │   │   └── repository/          # Repository implementations
│   │   │   ├── domain/
│   │   │   │   ├── model/               # Domain models (pure Kotlin)
│   │   │   │   └── usecase/             # Use cases (single responsibility)
│   │   │   └── ui/
│   │   │       ├── components/          # Shared composables
│   │   │       ├── theme/               # Color, Type, Theme, Dimens
│   │   │       ├── navigation/          # Screen routes + NavGraph
│   │   │       ├── products/            # Feature: Screen.kt + ViewModel.kt
│   │   │       ├── applications/        # Feature: Screen.kt + ViewModel.kt
│   │   │       ├── auth/                # Feature: Screen.kt + ViewModel.kt
│   │   │       └── dashboard/           # Feature: Screen.kt + ViewModel.kt
│   │   └── res/
│   └── test/                            # Unit tests (mirror main structure)
│   └── androidTest/                     # Instrumented / UI tests
├── build.gradle.kts
└── proguard-rules.pro
```

**Rules:**
- Each feature folder under `ui/` MUST contain exactly one `Screen.kt` and one `ViewModel.kt`.
- Domain models MUST NOT import from `data` or `ui` packages.
- DTOs MUST live in `data/api/dto/` — never in `domain/`.
- Test files MUST mirror the main source tree path.

---

## KS3 — Screen Pattern

Every screen is a `@Composable` function that receives its ViewModel via `hiltViewModel()`.

```kotlin
@Composable
fun ProductListScreen(
    navController: NavController,
    viewModel: ProductListViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Products") },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.surface
                )
            )
        }
    ) { padding ->
        when (val state = uiState) {
            is UiState.Loading -> LoadingSkeleton(modifier = Modifier.padding(padding))
            is UiState.Success -> ProductListContent(
                products = state.data,
                onProductClick = { id ->
                    navController.navigate(Screen.ProductDetail.createRoute(id))
                },
                modifier = Modifier.padding(padding)
            )
            is UiState.Error -> ErrorState(
                message = state.message,
                onRetry = { viewModel.loadProducts() },
                modifier = Modifier.padding(padding)
            )
        }
    }
}

@Composable
private fun ProductListContent(
    products: List<Product>,
    onProductClick: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    LazyColumn(modifier = modifier.fillMaxSize()) {
        items(products, key = { it.id }) { product ->
            TasheelCard(
                onClick = { onProductClick(product.id) },
                modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp)
            ) {
                ProductCardContent(product)
            }
        }
    }
}

@Preview(name = "Light", showBackground = true)
@Preview(name = "Dark", showBackground = true, uiMode = UI_MODE_NIGHT_YES)
@Composable
private fun ProductListScreenPreview() {
    TasheelTheme {
        ProductListContent(
            products = listOf(Product.preview()),
            onProductClick = {}
        )
    }
}
```

**Rules:**
- Screen composable MUST use `Scaffold` as root layout.
- MUST delegate content to private sub-composables — screen function handles only state wiring.
- MUST provide `@Preview` for both light and dark themes.
- MUST NOT perform business logic inside composables — delegate to ViewModel.
- Sub-composables MUST accept `Modifier` as last parameter with default `Modifier`.

---

## KS4 — ViewModel Pattern

ViewModels use `@HiltViewModel` with constructor injection and expose `StateFlow<UiState<T>>`.

```kotlin
@HiltViewModel
class ProductListViewModel @Inject constructor(
    private val getProductsUseCase: GetProductsUseCase
) : ViewModel() {

    private val _uiState = MutableStateFlow<UiState<List<Product>>>(UiState.Loading)
    val uiState: StateFlow<UiState<List<Product>>> = _uiState.asStateFlow()

    init {
        loadProducts()
    }

    fun loadProducts() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            try {
                val products = getProductsUseCase()
                _uiState.value = UiState.Success(products)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(
                    e.message ?: "Failed to load products"
                )
            }
        }
    }
}
```

**Rules:**
- MUST annotate with `@HiltViewModel` and use `@Inject constructor`.
- MUST expose state as `StateFlow` via `.asStateFlow()` — never expose `MutableStateFlow`.
- MUST use `viewModelScope.launch` for coroutines.
- MUST wrap async calls in `try/catch` mapping to `UiState.Error`.
- MUST NOT hold references to `Context`, `Activity`, or `View`.
- Private mutable state uses `_` prefix naming convention.

---

## KS5 — UiState Pattern

A single sealed interface used across all ViewModels for consistent state representation.

```kotlin
// core/UiState.kt
sealed interface UiState<out T> {
    data object Loading : UiState<Nothing>
    data class Success<T>(val data: T) : UiState<T>
    data class Error(val message: String) : UiState<Nothing>
}
```

### Usage in Composables

```kotlin
when (val state = uiState) {
    is UiState.Loading -> LoadingSkeleton()
    is UiState.Success -> ContentComposable(data = state.data)
    is UiState.Error -> ErrorState(message = state.message, onRetry = onRetry)
}
```

**Rules:**
- MUST use this exact sealed interface — do not create per-feature state classes.
- `Loading` is a `data object` (singleton).
- `Error` carries a user-facing `message: String`.
- `Success` is generic over `T` — the ViewModel specifies the concrete type.
- MUST handle all three states exhaustively in `when` blocks (compiler-enforced).

---

## KS6 — Navigation

Navigation uses a sealed class for type-safe route definitions and `NavHost` for graph composition.

### Route Definitions

```kotlin
// ui/navigation/Screen.kt
sealed class Screen(val route: String) {
    data object ProductList : Screen("products")
    data object Dashboard : Screen("dashboard")
    data object Auth : Screen("auth")

    data object ProductDetail : Screen("products/{productId}") {
        fun createRoute(productId: String) = "products/$productId"
    }

    data object ApplicationForm : Screen("applications/{productId}") {
        fun createRoute(productId: String) = "applications/$productId"
    }
}
```

### NavGraph

```kotlin
// ui/navigation/NavGraph.kt
@Composable
fun TasheelNavGraph(navController: NavHostController) {
    NavHost(
        navController = navController,
        startDestination = Screen.Dashboard.route
    ) {
        composable(Screen.Dashboard.route) {
            DashboardScreen(navController = navController)
        }
        composable(Screen.ProductList.route) {
            ProductListScreen(navController = navController)
        }
        composable(
            route = Screen.ProductDetail.route,
            arguments = listOf(navArgument("productId") { type = NavType.StringType })
        ) {
            ProductDetailScreen(navController = navController)
        }
        composable(Screen.Auth.route) {
            AuthScreen(navController = navController)
        }
    }
}
```

**Rules:**
- All routes MUST be defined in the `Screen` sealed class — no string literals in navigation calls.
- Parameterized routes MUST provide a `createRoute()` companion function.
- Each `composable()` block MUST use `hiltViewModel()` (injected in the Screen composable).
- MUST NOT pass complex objects via navigation — pass IDs only, load data in ViewModel.
- Deep links MUST be declared in the `composable()` block if required.

---

## KS7 — Dependency Injection (Hilt)

Hilt provides compile-time DI across the application.

### Application Class

```kotlin
@HiltAndroidApp
class TasheelApplication : Application()
```

### Network Module

```kotlin
// core/di/NetworkModule.kt
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideOkHttpClient(
        authInterceptor: AuthInterceptor
    ): OkHttpClient = OkHttpClient.Builder()
        .addInterceptor(authInterceptor)
        .addInterceptor(HttpLoggingInterceptor().apply {
            level = if (BuildConfig.DEBUG)
                HttpLoggingInterceptor.Level.BODY
            else
                HttpLoggingInterceptor.Level.NONE
        })
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()

    @Provides
    @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit =
        Retrofit.Builder()
            .baseUrl(BuildConfig.BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()

    @Provides
    @Singleton
    fun provideTasheelApi(retrofit: Retrofit): TasheelApi =
        retrofit.create(TasheelApi::class.java)
}
```

### Database Module

```kotlin
// core/di/DatabaseModule.kt
@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {

    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): AppDatabase =
        Room.databaseBuilder(context, AppDatabase::class.java, "tasheel_db")
            .fallbackToDestructiveMigration()
            .build()

    @Provides
    fun provideProductDao(db: AppDatabase): ProductDao = db.productDao()
}
```

### Repository Module

```kotlin
// core/di/RepositoryModule.kt
@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {

    @Binds
    @Singleton
    abstract fun bindProductRepository(
        impl: ProductRepositoryImpl
    ): ProductRepository
}
```

**Rules:**
- MUST use `@InstallIn(SingletonComponent::class)` for app-scoped dependencies.
- MUST use `object` for `@Provides` modules, `abstract class` for `@Binds` modules.
- MUST annotate singletons with `@Singleton`.
- ViewModels and UseCases use `@Inject constructor` — no module entry needed.
- MUST NOT use `@ActivityScoped` or `@FragmentScoped` in Compose-only apps.

---

## KS8 — Networking (Retrofit)

All API communication goes through a single Retrofit interface.

```kotlin
// data/api/TasheelApi.kt
interface TasheelApi {

    @GET("api/v1/products")
    suspend fun getProducts(): List<ProductDto>

    @GET("api/v1/products/{id}")
    suspend fun getProduct(@Path("id") id: String): ProductDto

    @POST("api/v1/applications")
    suspend fun submitApplication(@Body request: ApplicationRequest): ApplicationResponse

    @GET("api/v1/applications")
    suspend fun getApplications(): List<ApplicationDto>

    @POST("api/v1/auth/login")
    suspend fun login(@Body request: LoginRequest): AuthResponse

    @POST("api/v1/auth/refresh")
    suspend fun refreshToken(@Body request: RefreshTokenRequest): AuthResponse
}
```

### Auth Interceptor

```kotlin
// data/api/AuthInterceptor.kt
@Singleton
class AuthInterceptor @Inject constructor(
    private val tokenManager: TokenManager
) : Interceptor {

    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request().newBuilder()
        tokenManager.getAccessToken()?.let { token ->
            request.addHeader("Authorization", "Bearer $token")
        }
        return chain.proceed(request.build())
    }
}
```

**Rules:**
- All API functions MUST be `suspend` — no `Call<T>` wrappers.
- MUST use `GsonConverterFactory` for JSON serialization.
- Timeouts MUST be 30 seconds for connect, read, and write.
- Logging MUST be `BODY` level in debug, `NONE` in release.
- Base URL MUST come from `BuildConfig.BASE_URL` — never hardcoded.
- Auth tokens MUST be injected via `AuthInterceptor` — not per-request headers.

---

## KS9 — Local Storage (Room)

Room provides compile-time verified SQL with coroutine support.

### Database

```kotlin
// data/db/AppDatabase.kt
@Database(
    entities = [ProductEntity::class, ApplicationEntity::class],
    version = 1,
    exportSchema = true
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun productDao(): ProductDao
    abstract fun applicationDao(): ApplicationDao
}
```

### Entity

```kotlin
// data/db/ProductEntity.kt
@Entity(tableName = "products")
data class ProductEntity(
    @PrimaryKey val id: String,
    val name: String,
    val description: String,
    val minAmount: Double,
    val maxAmount: Double,
    val interestRate: Double,
    val updatedAt: Long
)
```

### DAO

```kotlin
// data/db/ProductDao.kt
@Dao
interface ProductDao {
    @Query("SELECT * FROM products ORDER BY name ASC")
    suspend fun getAll(): List<ProductEntity>

    @Query("SELECT * FROM products WHERE id = :id")
    suspend fun getById(id: String): ProductEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertAll(products: List<ProductEntity>)

    @Query("DELETE FROM products")
    suspend fun deleteAll()
}
```

### Secure Token Storage

```kotlin
// data/db/TokenManager.kt
@Singleton
class TokenManager @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val prefs = EncryptedSharedPreferences.create(
        "tasheel_secure_prefs",
        MasterKeys.getOrCreate(MasterKeys.AES256_GCM_SPEC),
        context,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )

    fun getAccessToken(): String? = prefs.getString("access_token", null)

    fun saveTokens(access: String, refresh: String) {
        prefs.edit()
            .putString("access_token", access)
            .putString("refresh_token", refresh)
            .apply()
    }

    fun clearTokens() {
        prefs.edit().clear().apply()
    }
}
```

**Rules:**
- All DAO functions MUST be `suspend`.
- MUST use `OnConflictStrategy.REPLACE` for upsert patterns.
- MUST export schema (`exportSchema = true`) for migration verification.
- Tokens and secrets MUST use `EncryptedSharedPreferences` — never plain `SharedPreferences`.
- MUST NOT store PII in plain Room tables without encryption.

---

## KS10 — Repository Pattern

Repositories bridge the data layer and domain layer, mapping DTOs to domain models.

```kotlin
// data/repository/ProductRepositoryImpl.kt
@Singleton
class ProductRepositoryImpl @Inject constructor(
    private val api: TasheelApi,
    private val productDao: ProductDao
) : ProductRepository {

    override suspend fun getProducts(): List<Product> {
        return try {
            val remote = api.getProducts()
            productDao.insertAll(remote.map { it.toEntity() })
            remote.map { it.toDomain() }
        } catch (e: Exception) {
            // Fallback to cache
            productDao.getAll().map { it.toDomain() }
        }
    }

    override suspend fun getProduct(id: String): Product {
        return api.getProduct(id).toDomain()
    }
}
```

### Domain Interface

```kotlin
// domain/repository/ProductRepository.kt
interface ProductRepository {
    suspend fun getProducts(): List<Product>
    suspend fun getProduct(id: String): Product
}
```

**Rules:**
- MUST define a domain interface in `domain/` — implementation in `data/repository/`.
- MUST map DTOs to domain models via `.toDomain()` extension functions.
- MUST use `@Singleton` scope.
- Network-first with local cache fallback is the default caching strategy.
- MUST NOT expose DTOs or entities outside the data layer.

---

## KS11 — UseCase Pattern

UseCases encapsulate a single business operation and are the only dependency of ViewModels.

```kotlin
// domain/usecase/GetProductsUseCase.kt
class GetProductsUseCase @Inject constructor(
    private val productRepository: ProductRepository
) {
    suspend operator fun invoke(): List<Product> {
        return productRepository.getProducts()
    }
}
```

```kotlin
// domain/usecase/GetProductDetailUseCase.kt
class GetProductDetailUseCase @Inject constructor(
    private val productRepository: ProductRepository
) {
    suspend operator fun invoke(productId: String): Product {
        return productRepository.getProduct(productId)
    }
}
```

```kotlin
// domain/usecase/SubmitApplicationUseCase.kt
class SubmitApplicationUseCase @Inject constructor(
    private val applicationRepository: ApplicationRepository
) {
    suspend operator fun invoke(request: ApplicationRequest): Application {
        return applicationRepository.submit(request)
    }
}
```

**Rules:**
- MUST use `operator fun invoke()` as the single public method.
- MUST use `@Inject constructor` — no Hilt module entry needed.
- Each UseCase MUST have exactly one responsibility.
- MUST depend on domain-layer repository interfaces — never on implementations.
- ViewModels MUST call UseCases, not repositories directly.

---

## KS12 — Design System

All visual tokens and shared components live in `ui/theme/` and `ui/components/`.

### Color Tokens

```kotlin
// ui/theme/Color.kt
// Primary
val TasheelPrimary = Color(0xFF4F6EF7)
val TasheelPrimaryVariant = Color(0xFF3A56D4)
val TasheelOnPrimary = Color(0xFFFFFFFF)

// Secondary
val TasheelSecondary = Color(0xFF2EC4B6)
val TasheelOnSecondary = Color(0xFFFFFFFF)

// Neutrals
val TasheelBackground = Color(0xFFF8F9FA)
val TasheelSurface = Color(0xFFFFFFFF)
val TasheelOnBackground = Color(0xFF1A1A2E)
val TasheelOnSurface = Color(0xFF1A1A2E)
val TasheelOutline = Color(0xFFE0E0E0)

// Semantic
val TasheelError = Color(0xFFE53E3E)
val TasheelSuccess = Color(0xFF38A169)
val TasheelWarning = Color(0xFFD69E2E)

// Dark theme overrides
val TasheelDarkBackground = Color(0xFF1A1A2E)
val TasheelDarkSurface = Color(0xFF2D2D44)
```

### Theme

```kotlin
// ui/theme/Theme.kt
private val LightColorScheme = lightColorScheme(
    primary = TasheelPrimary,
    onPrimary = TasheelOnPrimary,
    secondary = TasheelSecondary,
    onSecondary = TasheelOnSecondary,
    background = TasheelBackground,
    surface = TasheelSurface,
    onBackground = TasheelOnBackground,
    onSurface = TasheelOnSurface,
    error = TasheelError,
    outline = TasheelOutline
)

private val DarkColorScheme = darkColorScheme(
    primary = TasheelPrimary,
    onPrimary = TasheelOnPrimary,
    secondary = TasheelSecondary,
    onSecondary = TasheelOnSecondary,
    background = TasheelDarkBackground,
    surface = TasheelDarkSurface,
    onBackground = Color.White,
    onSurface = Color.White,
    error = TasheelError,
    outline = TasheelOutline
)

@Composable
fun TasheelTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    val colorScheme = if (darkTheme) DarkColorScheme else LightColorScheme
    MaterialTheme(
        colorScheme = colorScheme,
        typography = TasheelTypography,
        content = content
    )
}
```

### Typography

```kotlin
// ui/theme/Type.kt
val TasheelTypography = Typography(
    headlineLarge = TextStyle(
        fontWeight = FontWeight.Bold,
        fontSize = 28.sp,
        lineHeight = 36.sp
    ),
    headlineMedium = TextStyle(
        fontWeight = FontWeight.SemiBold,
        fontSize = 24.sp,
        lineHeight = 32.sp
    ),
    titleLarge = TextStyle(
        fontWeight = FontWeight.SemiBold,
        fontSize = 20.sp,
        lineHeight = 28.sp
    ),
    bodyLarge = TextStyle(
        fontWeight = FontWeight.Normal,
        fontSize = 16.sp,
        lineHeight = 24.sp
    ),
    bodyMedium = TextStyle(
        fontWeight = FontWeight.Normal,
        fontSize = 14.sp,
        lineHeight = 20.sp
    ),
    labelLarge = TextStyle(
        fontWeight = FontWeight.Medium,
        fontSize = 14.sp,
        lineHeight = 20.sp
    )
)
```

### Dimensions

```kotlin
// ui/theme/Dimens.kt
object Dimens {
    // Spacing
    val SpacingXs = 4.dp
    val SpacingSm = 8.dp
    val SpacingMd = 16.dp
    val SpacingLg = 24.dp
    val SpacingXl = 32.dp
    val SpacingXxl = 48.dp

    // Radii
    val RadiusSm = 8.dp
    val RadiusMd = 12.dp
    val RadiusLg = 16.dp
    val RadiusFull = 100.dp

    // Elevation
    val ElevationSm = 2.dp
    val ElevationMd = 4.dp
}
```

### Shared Components

```kotlin
// ui/components/TasheelButton.kt
@Composable
fun TasheelButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    isLoading: Boolean = false
) {
    Button(
        onClick = onClick,
        modifier = modifier.fillMaxWidth().height(48.dp),
        enabled = enabled && !isLoading,
        shape = RoundedCornerShape(Dimens.RadiusMd)
    ) {
        if (isLoading) {
            CircularProgressIndicator(
                modifier = Modifier.size(20.dp),
                color = MaterialTheme.colorScheme.onPrimary,
                strokeWidth = 2.dp
            )
        } else {
            Text(text = text, style = MaterialTheme.typography.labelLarge)
        }
    }
}

// ui/components/TasheelTextField.kt
@Composable
fun TasheelTextField(
    value: String,
    onValueChange: (String) -> Unit,
    label: String,
    modifier: Modifier = Modifier,
    isError: Boolean = false,
    errorMessage: String? = null,
    keyboardOptions: KeyboardOptions = KeyboardOptions.Default
) {
    Column(modifier = modifier) {
        OutlinedTextField(
            value = value,
            onValueChange = onValueChange,
            label = { Text(label) },
            isError = isError,
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(Dimens.RadiusSm),
            keyboardOptions = keyboardOptions,
            singleLine = true
        )
        if (isError && errorMessage != null) {
            Text(
                text = errorMessage,
                color = MaterialTheme.colorScheme.error,
                style = MaterialTheme.typography.bodySmall,
                modifier = Modifier.padding(start = Dimens.SpacingSm, top = Dimens.SpacingXs)
            )
        }
    }
}

// ui/components/TasheelCard.kt
@Composable
fun TasheelCard(
    modifier: Modifier = Modifier,
    onClick: (() -> Unit)? = null,
    content: @Composable ColumnScope.() -> Unit
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(Dimens.RadiusMd),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        elevation = CardDefaults.cardElevation(defaultElevation = Dimens.ElevationSm),
        onClick = onClick ?: {},
        content = { Column(modifier = Modifier.padding(Dimens.SpacingMd), content = content) }
    )
}

// ui/components/StatusBadge.kt
@Composable
fun StatusBadge(status: String, modifier: Modifier = Modifier) {
    val (backgroundColor, textColor) = when (status.lowercase()) {
        "approved" -> TasheelSuccess to Color.White
        "pending" -> TasheelWarning to Color.White
        "rejected" -> TasheelError to Color.White
        else -> TasheelOutline to TasheelOnSurface
    }
    Surface(
        modifier = modifier,
        shape = RoundedCornerShape(Dimens.RadiusFull),
        color = backgroundColor
    ) {
        Text(
            text = status,
            modifier = Modifier.padding(horizontal = Dimens.SpacingSm, vertical = Dimens.SpacingXs),
            color = textColor,
            style = MaterialTheme.typography.labelSmall
        )
    }
}

// ui/components/LoadingSkeleton.kt
@Composable
fun LoadingSkeleton(modifier: Modifier = Modifier) {
    Column(modifier = modifier.padding(Dimens.SpacingMd)) {
        repeat(3) {
            ShimmerCard()
            Spacer(modifier = Modifier.height(Dimens.SpacingSm))
        }
    }
}

// ui/components/ErrorState.kt
@Composable
fun ErrorState(
    message: String,
    onRetry: () -> Unit,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier.fillMaxSize(),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Icon(
            imageVector = Icons.Outlined.ErrorOutline,
            contentDescription = "Error",
            modifier = Modifier.size(48.dp),
            tint = MaterialTheme.colorScheme.error
        )
        Spacer(modifier = Modifier.height(Dimens.SpacingMd))
        Text(text = message, style = MaterialTheme.typography.bodyLarge)
        Spacer(modifier = Modifier.height(Dimens.SpacingMd))
        TasheelButton(text = "Retry", onClick = onRetry)
    }
}
```

**Rules:**
- All colors MUST use tokens from `Color.kt` — no inline hex values.
- All spacing MUST use `Dimens` constants — no magic `dp` values.
- All components MUST accept `Modifier` parameter with default `Modifier`.
- All components MUST have `@Preview` annotations (light + dark).
- MUST use `MaterialTheme.colorScheme` and `MaterialTheme.typography` — never direct token references in feature code.

---

## KS13 — DTO Pattern

DTOs are data-layer-only classes that map to/from domain models via extension functions.

### Response DTO

```kotlin
// data/api/dto/ProductDto.kt
data class ProductDto(
    val id: String,
    val name: String,
    val description: String?,
    val min_amount: Double,
    val max_amount: Double,
    val interest_rate: Double,
    val status: String?,
    val created_at: String?
)

fun ProductDto.toDomain() = Product(
    id = id,
    name = name,
    description = description.orEmpty(),
    minAmount = min_amount,
    maxAmount = max_amount,
    interestRate = interest_rate,
    status = status ?: "unknown"
)

fun ProductDto.toEntity() = ProductEntity(
    id = id,
    name = name,
    description = description.orEmpty(),
    minAmount = min_amount,
    maxAmount = max_amount,
    interestRate = interest_rate,
    updatedAt = System.currentTimeMillis()
)
```

### Request DTO

```kotlin
// data/api/dto/ApplicationRequest.kt
data class ApplicationRequest(
    val product_id: String,
    val amount: Double,
    val tenure_months: Int,
    val applicant_name: String,
    val applicant_email: String,
    val applicant_phone: String
)
```

### Domain Model

```kotlin
// domain/model/Product.kt
data class Product(
    val id: String,
    val name: String,
    val description: String,
    val minAmount: Double,
    val maxAmount: Double,
    val interestRate: Double,
    val status: String
) {
    companion object {
        fun preview() = Product(
            id = "1",
            name = "Personal Loan",
            description = "Quick personal financing",
            minAmount = 5000.0,
            maxAmount = 100000.0,
            interestRate = 12.5,
            status = "active"
        )
    }
}
```

**Rules:**
- DTOs MUST use snake_case field names matching the API contract.
- Domain models MUST use camelCase field names.
- Optional API fields MUST be nullable in DTOs (`String?`, `Double?`).
- `.toDomain()` extension MUST handle null-to-default mapping.
- Request and response DTOs MUST be separate classes — never reuse.
- Domain models SHOULD include a `preview()` factory for `@Preview` composables.

---

## KS14 — Testing

### ViewModel Unit Test

```kotlin
@ExtendWith(MockKExtension::class)
class ProductListViewModelTest {

    @MockK
    private lateinit var getProductsUseCase: GetProductsUseCase

    private lateinit var viewModel: ProductListViewModel

    @BeforeEach
    fun setup() {
        Dispatchers.setMain(UnconfinedTestDispatcher())
    }

    @AfterEach
    fun tearDown() {
        Dispatchers.resetMain()
    }

    @Test
    fun loadProducts_whenSuccess_shouldEmitSuccessState() = runTest {
        val products = listOf(Product.preview())
        coEvery { getProductsUseCase() } returns products

        viewModel = ProductListViewModel(getProductsUseCase)

        viewModel.uiState.test {
            val state = awaitItem()
            assertThat(state).isInstanceOf(UiState.Success::class.java)
            assertThat((state as UiState.Success).data).isEqualTo(products)
        }
    }

    @Test
    fun loadProducts_whenFailure_shouldEmitErrorState() = runTest {
        coEvery { getProductsUseCase() } throws RuntimeException("Network error")

        viewModel = ProductListViewModel(getProductsUseCase)

        viewModel.uiState.test {
            val state = awaitItem()
            assertThat(state).isInstanceOf(UiState.Error::class.java)
            assertThat((state as UiState.Error).message).contains("Network error")
        }
    }
}
```

### Compose UI Test

```kotlin
@HiltAndroidTest
class ProductListScreenTest {

    @get:Rule
    val composeTestRule = createAndroidComposeRule<MainActivity>()

    @Test
    fun productListScreen_displaysProducts() {
        composeTestRule.setContent {
            TasheelTheme {
                ProductListContent(
                    products = listOf(Product.preview()),
                    onProductClick = {}
                )
            }
        }

        composeTestRule.onNodeWithText("Personal Loan").assertIsDisplayed()
    }

    @Test
    fun productListScreen_showsErrorState() {
        composeTestRule.setContent {
            TasheelTheme {
                ErrorState(message = "Something went wrong", onRetry = {})
            }
        }

        composeTestRule.onNodeWithText("Something went wrong").assertIsDisplayed()
        composeTestRule.onNodeWithText("Retry").assertIsDisplayed()
    }
}
```

### Test Dependencies

```kotlin
// build.gradle.kts (test dependencies)
testImplementation("org.junit.jupiter:junit-jupiter:5.10.2")
testImplementation("io.mockk:mockk:1.13.9")
testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.8.0")
testImplementation("app.cash.turbine:turbine:1.1.0")
testImplementation("com.google.truth:truth:1.4.2")

androidTestImplementation("androidx.compose.ui:ui-test-junit4")
androidTestImplementation("com.google.dagger:hilt-android-testing:2.51")
debugImplementation("androidx.compose.ui:ui-test-manifest")
```

**Rules:**
- MUST use JUnit 5 + MockK for ViewModel/UseCase/Repository unit tests.
- MUST use Turbine for `StateFlow` / `Flow` assertions.
- MUST use Compose UI Test for screen-level tests.
- Test naming: `fun methodName_whenCondition_shouldResult()`.
- MUST set `Dispatchers.setMain(UnconfinedTestDispatcher())` in ViewModel tests.
- MUST test all three `UiState` branches (Loading, Success, Error).
- MUST NOT use Mockito — MockK is the standard mocking library.

---

## KS15 — Naming Conventions

| Element | Convention | Example |
|---|---|---|
| Screen composable | PascalCase + `Screen` suffix | `ProductListScreen` |
| ViewModel | PascalCase + `ViewModel` suffix | `ProductListViewModel` |
| Component composable | PascalCase, `Tasheel` prefix for design system | `TasheelButton`, `StatusBadge` |
| UseCase | PascalCase + `UseCase` suffix | `GetProductsUseCase` |
| Repository interface | PascalCase + `Repository` suffix | `ProductRepository` |
| Repository impl | PascalCase + `RepositoryImpl` suffix | `ProductRepositoryImpl` |
| DTO | PascalCase + `Dto`/`Request`/`Response` suffix | `ProductDto`, `LoginRequest` |
| Entity | PascalCase + `Entity` suffix | `ProductEntity` |
| DAO | PascalCase + `Dao` suffix | `ProductDao` |
| Functions | camelCase | `loadProducts()`, `onProductClick()` |
| Properties | camelCase, `_` prefix for private mutable | `uiState`, `_uiState` |
| Constants | SCREAMING_SNAKE_CASE | `BASE_URL`, `MAX_RETRY_COUNT` |
| Packages | lowercase, dot-separated | `com.tasheel.finance.ui.products` |
| Files | PascalCase.kt | `ProductListScreen.kt` |
| Hilt modules | PascalCase + `Module` suffix | `NetworkModule`, `DatabaseModule` |
| Interceptors | PascalCase + `Interceptor` suffix | `AuthInterceptor` |

**Rules:**
- MUST follow Kotlin official coding conventions.
- Boolean properties MUST use `is`/`has`/`should` prefix: `isLoading`, `hasError`.
- Event callbacks MUST use `on` prefix: `onClick`, `onRetry`, `onProductClick`.
- Private backing properties MUST use `_` prefix: `_uiState`.

---

## KS16 — Brownfield Integration Guide

When adding a new feature to the existing codebase:

### Step-by-Step

1. **Create feature folder:** `ui/{feature}/` with `{Feature}Screen.kt` and `{Feature}ViewModel.kt`.
2. **Add domain layer:** `domain/model/{Model}.kt` and `domain/usecase/{Action}UseCase.kt`.
3. **Add data layer:** DTO in `data/api/dto/`, API endpoint in `TasheelApi.kt`, repository in `data/repository/`.
4. **Register route:** Add `Screen` entry to `Screen.kt`, add `composable()` block to `NavGraph.kt`.
5. **Wire DI:** Add repository binding to `RepositoryModule.kt` (if new repository). UseCases and ViewModels auto-discovered via `@Inject`.

### Checklist

```
□ Screen.kt created with Scaffold + UiState handling
□ ViewModel.kt created with StateFlow<UiState<T>>
□ UseCase created with operator fun invoke()
□ Repository interface in domain/, impl in data/
□ DTOs in data/api/dto/ with .toDomain()
□ Route added to Screen sealed class
□ composable() block added to NavGraph
□ @Preview added (light + dark)
□ Reuses TasheelTheme, Dimens, shared components
□ Unit tests for ViewModel
□ No unrelated code modified
```

**Rules:**
- MUST reuse existing `ui/components/` and `ui/theme/` — do not duplicate.
- MUST add to existing DI modules — do not create new modules unless justified.
- MUST NOT refactor unrelated code in the same PR.
- MUST follow the exact file naming and package structure from KS2.
- New API endpoints MUST be added to the existing `TasheelApi` interface.

---

## KS17 — Cross-References

This KB maps to the following enterprise and mobile standards:

| Standard | Reference | Mapping |
|---|---|---|
| Enterprise Architecture | EA1 | Technology stack alignment — Kotlin 2.0, Compose, Hilt versions |
| Enterprise Architecture | EA10 | Mobile architecture — clean architecture layers, MVVM pattern |
| Enterprise Architecture | EA11 | Design system — Material Design 3, color tokens, typography |
| Enterprise Architecture | EA7 | Accessibility (min touch 48dp, content descriptions) + Performance (lazy lists, image caching) |
| Enterprise Architecture | EA5 | Security — EncryptedSharedPreferences, AuthInterceptor, no PII in logs |
| Mobile Standards | MC1 | Project structure and module organization |
| Mobile Standards | MC2 | Compose UI patterns and composable design |
| Mobile Standards | MC3 | ViewModel and state management |
| Mobile Standards | MC4 | Navigation architecture |
| Mobile Standards | MC5 | Dependency injection with Hilt |
| Mobile Standards | MC6 | Network layer (Retrofit + OkHttp) |
| Mobile Standards | MC7 | Local persistence (Room + encrypted storage) |
| Mobile Standards | MC8 | Repository and UseCase patterns |
| Mobile Standards | MC9 | Design system and theming |
| Mobile Standards | MC10 | DTO and data mapping |
| Mobile Standards | MC11 | Testing strategy |
| Mobile Standards | MC12 | Naming conventions and code style |

### Accessibility Requirements (from EA7)

- All interactive elements MUST have minimum 48dp touch target.
- All `Icon` composables MUST include `contentDescription`.
- All `Image` composables MUST include `contentDescription` or `decorative = true`.
- Color contrast MUST meet WCAG 2.1 AA (4.5:1 for text, 3:1 for large text).
- Screen readers MUST be able to navigate all interactive elements.

### Performance Requirements (from EA7)

- Lists MUST use `LazyColumn`/`LazyRow` with `key` parameter.
- Images MUST use Coil with memory + disk caching.
- MUST NOT perform blocking I/O on the main thread.
- Compose recomposition MUST be minimized — use `remember`, `derivedStateOf` where appropriate.
- MUST use `immutableListOf` or `@Stable` annotations for list parameters to prevent unnecessary recomposition.

---

*End of Kotlin/Compose Coding Standards (KS1–KS17)*