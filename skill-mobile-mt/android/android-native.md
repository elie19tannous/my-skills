# Android Native — Production Patterns

> Battle-tested patterns for Android Kotlin development.
> Multi-module Gradle, Hilt DI, Compose UI, offline-first.
> Also reference for RN/Flutter Android-side issues.

---

## Clean Architecture (Multi-Module)

```
project/
├── app/                          # Main application module
│   ├── src/main/
│   │   ├── java/com/company/app/
│   │   │   ├── di/              # Hilt modules
│   │   │   ├── presentation/
│   │   │   │   ├── features/
│   │   │   │   │   ├── auth/
│   │   │   │   │   │   ├── ui/     # Composables
│   │   │   │   │   │   └── viewmodel/
│   │   │   │   │   └── home/
│   │   │   │   ├── navigation/
│   │   │   │   └── theme/
│   │   │   └── domain/
│   │   │       ├── model/        # Domain entities
│   │   │       ├── usecase/      # Business rules
│   │   │       └── repository/   # Repository interfaces
│   │   ├── res/
│   │   └── AndroidManifest.xml
│   └── build.gradle.kts
├── data/                         # Data layer module
│   ├── src/main/java/
│   │   ├── repository/           # Repository implementations
│   │   ├── remote/               # API service, DTOs
│   │   ├── local/                # Room DAOs, entities
│   │   └── mapper/               # DTO ↔ Entity ↔ Domain mappers
│   └── build.gradle.kts
├── common/                       # Shared utilities module
│   └── src/main/java/
├── build.gradle.kts              # Root build file
├── settings.gradle.kts           # Module declarations
└── gradle/
    └── libs.versions.toml        # Version catalog
```

### Dependency Rule
```
app (presentation) → domain/ ← data/

Presentation depends on Domain. Data depends on Domain.
Domain depends on NOTHING.
app module has access to all modules.
data module implements domain interfaces.
```

## Compose UI Pattern

```kotlin
@Composable
fun ProductListScreen(
    viewModel: ProductListViewModel = hiltViewModel(),
    onProductClick: (String) -> Unit,
) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    Scaffold(
        topBar = { TopAppBar(title = { Text("Products") }) },
    ) { padding ->
        when (val state = uiState) {
            is UiState.Loading -> Box(Modifier.fillMaxSize(), Alignment.Center) {
                CircularProgressIndicator()
            }
            is UiState.Empty -> EmptyContent()
            is UiState.Error -> ErrorContent(state.message, onRetry = viewModel::load)
            is UiState.Success -> LazyColumn(
                modifier = Modifier.padding(padding),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                items(state.data, key = { it.id }) { product ->
                    ProductCard(product, onClick = { onProductClick(product.id) })
                }
            }
        }
    }
}

sealed interface UiState<out T> {
    data object Loading : UiState<Nothing>
    data object Empty : UiState<Nothing>
    data class Success<T>(val data: T) : UiState<T>
    data class Error(val message: String) : UiState<Nothing>
}
```

## ViewModel (Hilt)

```kotlin
@HiltViewModel
class ProductListViewModel @Inject constructor(
    private val getProducts: GetProductsUseCase,
) : ViewModel() {
    private val _uiState = MutableStateFlow<UiState<List<Product>>>(UiState.Loading)
    val uiState = _uiState.asStateFlow()

    init { load() }

    fun load() {
        viewModelScope.launch {
            _uiState.value = UiState.Loading
            getProducts()
                .catch { _uiState.value = UiState.Error(it.message ?: "Error") }
                .collect { items ->
                    _uiState.value = if (items.isEmpty()) UiState.Empty else UiState.Success(items)
                }
        }
    }
}
```

## DI (Hilt)

```kotlin
@Module @InstallIn(SingletonComponent::class)
object NetworkModule {
    @Provides @Singleton
    fun provideRetrofit(): Retrofit = Retrofit.Builder()
        .baseUrl(BuildConfig.API_BASE_URL)
        .addConverterFactory(Json.asConverterFactory("application/json".toMediaType()))
        .build()
}

@Module @InstallIn(SingletonComponent::class)
abstract class RepositoryModule {
    @Binds @Singleton
    abstract fun bindProductRepo(impl: ProductRepositoryImpl): ProductRepository
}
```

## Data Layer (Retrofit + Room — Offline-First)

```kotlin
// data/remote/ProductApi.kt
interface ProductApi {
    @GET("products") suspend fun getProducts(): ApiResponse<List<ProductDto>>
}

// data/local/ProductDao.kt
@Dao interface ProductDao {
    @Query("SELECT * FROM products") fun getAll(): Flow<List<ProductEntity>>
    @Upsert suspend fun upsertAll(items: List<ProductEntity>)
}

// data/repository/ProductRepositoryImpl.kt
class ProductRepositoryImpl @Inject constructor(
    private val api: ProductApi, private val dao: ProductDao,
) : ProductRepository {
    override fun getProducts(): Flow<List<Product>> = flow {
        val cached = dao.getAll().first()
        if (cached.isNotEmpty()) emit(cached.map { it.toDomain() })
        try {
            val fresh = api.getProducts()
            dao.upsertAll(fresh.data.map { it.toEntity() })
        } catch (e: Exception) { if (cached.isEmpty()) throw e }
        emitAll(dao.getAll().map { it.map { e -> e.toDomain() } })
    }
}
```

## Secure Storage

```kotlin
val prefs = EncryptedSharedPreferences.create(
    context, "secure_prefs",
    MasterKey.Builder(context).setKeyScheme(MasterKey.KeyScheme.AES256_GCM).build(),
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM,
)
```

## Multi-Module Gradle Setup

```kotlin
// settings.gradle.kts
include(":app", ":data", ":common")

// app/build.gradle.kts
dependencies {
    implementation(project(":data"))
    implementation(project(":common"))
}
```

## Compose Performance Optimization

```kotlin
// @Stable / @Immutable — tell Compose when to skip recomposition
// Use when your class isn't a data class but values never change
@Stable
class UserState(val id: String, val name: String)

@Immutable
data class ProductUiModel(val id: String, val price: Double)

// derivedStateOf — compute derived state only when inputs change
// Prevents recomposition on every scroll position change
val showFab by remember {
    derivedStateOf { listState.firstVisibleItemIndex > 0 }
}

// key() in LazyColumn — stable identity prevents full recomposition
LazyColumn {
    items(products, key = { it.id }) { product ->
        ProductCard(product)  // Only recomposes if THIS product changes
    }
}

// Stateless components — pass data + callbacks, not ViewModel
@Composable
fun ProductCard(
    product: Product,       // data only
    onClick: () -> Unit,    // callback only
) { /* no ViewModel here */ }
```

## Baseline Profiles (Startup Optimization)

```kotlin
// app/src/main/baseline-prof.txt (generated by Macrobenchmark)
// Speeds up cold start 20-30% by AOT-compiling hot code paths

// build.gradle.kts
dependencies {
    implementation("androidx.profileinstaller:profileinstaller:1.3.1")
}

// Generate with Macrobenchmark:
// ./gradlew :app:generateBaselineProfile
// Commit the generated baseline-prof.txt
```

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| `!!` assertion | `?.` / `?:` / `requireNotNull` |
| `collectAsState` | `collectAsStateWithLifecycle()` |
| Context leak | `@ApplicationContext`, never Activity |
| Missing ProGuard | Test release builds |
| Main thread blocking | `Dispatchers.IO` |
| Unstable lambdas in Compose | `remember { {} }` or move to ViewModel |
| List without keys | `items(list, key = { it.id })` |

---

## Java Interop (Legacy Projects)

> For projects still using Java. New code should use Kotlin.

### Activity + XML Layout (Java)

```java
// MainActivity.java
@AndroidEntryPoint
public class MainActivity extends AppCompatActivity {

    private MainViewModel viewModel;
    private ActivityMainBinding binding;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        binding = ActivityMainBinding.inflate(getLayoutInflater());
        setContentView(binding.getRoot());

        viewModel = new ViewModelProvider(this).get(MainViewModel.class);

        // Observe LiveData (Java equivalent of collectAsStateWithLifecycle)
        viewModel.getUiState().observe(this, state -> {
            if (state instanceof UiState.Loading) {
                binding.progressBar.setVisibility(View.VISIBLE);
                binding.recyclerView.setVisibility(View.GONE);
            } else if (state instanceof UiState.Error) {
                binding.progressBar.setVisibility(View.GONE);
                Toast.makeText(this, ((UiState.Error) state).getMessage(), Toast.LENGTH_SHORT).show();
            } else if (state instanceof UiState.Success) {
                binding.progressBar.setVisibility(View.GONE);
                binding.recyclerView.setVisibility(View.VISIBLE);
                adapter.submitList(((UiState.Success<List<Product>>) state).getData());
            }
        });

        binding.retryButton.setOnClickListener(v -> viewModel.load());
    }
}
```

### ViewModel + LiveData (Java)

```java
// ProductListViewModel.java
@HiltViewModel
public class ProductListViewModel extends ViewModel {

    private final MutableLiveData<UiState<List<Product>>> _uiState =
        new MutableLiveData<>(new UiState.Loading<>());
    private final LiveData<UiState<List<Product>>> uiState = _uiState;

    private final GetProductsUseCase getProducts;

    @Inject
    public ProductListViewModel(GetProductsUseCase getProducts) {
        this.getProducts = getProducts;
        load();
    }

    public LiveData<UiState<List<Product>>> getUiState() { return uiState; }

    public void load() {
        _uiState.setValue(new UiState.Loading<>());
        // Use RxJava or ExecutorService for async in Java
        ExecutorService executor = Executors.newSingleThreadExecutor();
        executor.execute(() -> {
            try {
                List<Product> items = getProducts.executeSync(); // blocking call
                new Handler(Looper.getMainLooper()).post(() -> {
                    if (items.isEmpty()) _uiState.setValue(new UiState.Empty<>());
                    else _uiState.setValue(new UiState.Success<>(items));
                });
            } catch (Exception e) {
                new Handler(Looper.getMainLooper()).post(() ->
                    _uiState.setValue(new UiState.Error<>(e.getMessage()))
                );
            } finally {
                executor.shutdown();
            }
        });
    }
}
```

### Retrofit + Callback (Java)

```java
// ProductApi.java
public interface ProductApi {
    @GET("products")
    Call<ApiResponse<List<ProductDto>>> getProducts();
}

// ProductRepositoryImpl.java
public class ProductRepositoryImpl implements ProductRepository {
    private final ProductApi api;
    private final ProductDao dao;

    @Inject
    public ProductRepositoryImpl(ProductApi api, ProductDao dao) {
        this.api = api;
        this.dao = dao;
    }

    @Override
    public void getProducts(Callback<List<Product>> callback) {
        api.getProducts().enqueue(new retrofit2.Callback<ApiResponse<List<ProductDto>>>() {
            @Override
            public void onResponse(Call<ApiResponse<List<ProductDto>>> call,
                                   Response<ApiResponse<List<ProductDto>>> response) {
                if (response.isSuccessful() && response.body() != null) {
                    List<Product> items = mapToDomain(response.body().getData());
                    callback.onSuccess(items);
                } else {
                    callback.onError("Server error: " + response.code());
                }
            }

            @Override
            public void onFailure(Call<ApiResponse<List<ProductDto>>> call, Throwable t) {
                callback.onError(t.getMessage());
            }
        });
    }
}
```

### Room DAO (Java)

```java
// ProductDao.java
@Dao
public interface ProductDao {
    @Query("SELECT * FROM products")
    LiveData<List<ProductEntity>> getAll();   // LiveData for Java observers

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    void insertAll(List<ProductEntity> items);

    @Query("DELETE FROM products")
    void deleteAll();
}
```

### Java-Kotlin Interop Annotations

```kotlin
// When writing Kotlin code that will be called from Java:

// @JvmStatic — allows calling companion object functions as static
class ProductMapper {
    companion object {
        @JvmStatic
        fun toDomain(dto: ProductDto): Product = Product(dto.id, dto.name)
    }
}
// Java: ProductMapper.toDomain(dto)  ✅ (without @JvmStatic: ProductMapper.Companion.toDomain(dto))

// @JvmField — exposes Kotlin property as Java field (no getter/setter)
class Config {
    companion object {
        @JvmField val BASE_URL = "https://api.example.com"
    }
}
// Java: Config.BASE_URL  ✅

// @JvmOverloads — generates overloaded methods for default parameters
class ProductService @JvmOverloads constructor(
    val baseUrl: String,
    val timeout: Int = 30,
    val retries: Int = 3,
)
// Java: new ProductService("url")  ✅  (without: must pass all 3 params)

// @Throws — declares checked exceptions for Java callers
@Throws(IOException::class)
fun readFile(path: String): String { /* ... */ }
```

### Calling Kotlin Suspend from Java (Bridge Pattern)

```java
// Use CoroutineScope from Java via CoroutinesInstrumentationHelper or wrapper
// ⚠️ Recommended: write a non-suspend wrapper in Kotlin

// Kotlin wrapper (bridge.kt)
object ProductBridge {
    @JvmStatic
    fun getProducts(scope: CoroutineScope, callback: ProductCallback) {
        scope.launch {
            try {
                val items = getProductsUseCase()
                callback.onSuccess(items)
            } catch (e: Exception) {
                callback.onError(e.message ?: "Error")
            }
        }
    }
}

// Java side
ProductBridge.getProducts(lifecycleScope, new ProductCallback() {
    @Override public void onSuccess(List<Product> items) { /* update UI */ }
    @Override public void onError(String message) { /* show error */ }
});
```

### Java Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| NullPointerException | `@NonNull` / `@Nullable` + null checks |
| Memory leak (Activity in async) | `WeakReference<Activity>` or cancel on `onDestroy` |
| Main thread network call | `Executors.newSingleThreadExecutor()` |
| No `Call.cancel()` | Store reference, cancel in `onDestroy` |
| Anonymous inner class holding outer ref | Use static inner class |

---

> Multi-module Gradle + Hilt + Compose + offline-first.
> Clean Architecture with domain module having zero dependencies.
> Java legacy: use LiveData + Retrofit callbacks. Bridge Kotlin suspend with wrapper functions.
