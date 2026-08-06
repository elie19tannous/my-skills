# Architecture Intelligence — Patterns from 30+ Production Repos

> On-demand. Load when: "architecture", "structure", "setup project", "best practices", "how to organize"
> Source: Analyzed 30+ open-source production mobile apps (total 200k+ GitHub stars)

---

## Reference Repos (by platform)

| Platform | Repo | Stars | Key Pattern |
|----------|------|-------|-------------|
| **RN** | Ignite (infinitered) | 19.7k | MST + MMKV + generators |
| **RN** | Obytes Template | 4k | Zustand + TanStack Query + Expo Router |
| **RN** | Expensify/App | 4.7k | Onyx custom state + centralized constants |
| **RN** | Mattermost Mobile | 2.6k | WatermelonDB + offline-first + WebSocket |
| **RN** | Artsy Eigen | 3.8k | Relay/GraphQL + Scene pattern |
| **Flutter** | Immich | 93.5k | Riverpod + drift + auto_route + clean arch |
| **Flutter** | AppFlowy | 68.2k | BLoC + GetIt + startup/ pattern |
| **Flutter** | Spotube | 44.6k | Riverpod + Hooks + custom hooks folder |
| **Flutter** | Hiddify | 26.7k | Riverpod + go_router + bootstrap.dart |
| **Flutter** | Ente Photos | 24.8k | Melos monorepo + gateway pattern |
| **iOS** | TCA (Point-Free) | 14.4k | Unidirectional + TestStore + @Dependency |
| **iOS** | Clean Arch SwiftUI | 6.5k | Redux state + @Environment DI |
| **iOS** | Modern Clean Arch | 4.1k | Tuist + 5-layer DDD + MVVM+TCA coexist |
| **Android** | Now in Android | 20.7k | Official Google arch + no-mock testing |
| **Android** | Android Showcase | 6.7k | Konsist validation + Koin DI |
| **Android** | Mihon | 18.8k | Plugin/extension arch + MVI |

---

## Cross-Platform Architecture Patterns

### 1. Dual State Management (Client + Server)

**The pattern:** Separate client state (UI, forms) from server state (API cache).

| Platform | Client State | Server State |
|----------|-------------|--------------|
| React Native | Zustand / MST | TanStack Query |
| Flutter | Riverpod | Riverpod + drift |
| iOS | @Observable / TCA | URLSession cache |
| Android | ViewModel + Flow | Repository + Room |

```typescript
// RN: Zustand for client + TanStack Query for server
const useAuthStore = create((set) => ({
  token: null,
  setToken: (t) => set({ token: t }),
}));

const { data, isLoading } = useQuery({
  queryKey: ['products'],
  queryFn: () => api.getProducts(),
  staleTime: 5 * 60 * 1000,
});
```

```dart
// Flutter: Riverpod for both, but separated
@riverpod
class AuthNotifier extends _$AuthNotifier { ... } // client

@riverpod
Future<List<Product>> products(Ref ref) async { ... } // server
```

### 2. Feature-Based Module Organization

**Every top repo (100%) uses feature-based organization, NOT type-based.**

```
// ✅ CORRECT: Feature-based (Immich, Obytes, Hiddify, Now in Android)
src/features/
  auth/
    domain/         # entities, use cases, repo interfaces
    data/           # repo impl, API, DTOs, mappers
    presentation/   # screens, widgets, viewmodels

// ❌ WRONG: Type-based (no production app uses this)
src/
  models/
  services/
  screens/
  widgets/
```

### 3. Centralized Constants Pattern (Expensify)

```typescript
// src/ROUTES.ts — Prevents string duplication
const ROUTES = {
  HOME: 'home',
  SETTINGS: 'settings',
  PROFILE: 'profile/:id',
} as const;

// src/SCREENS.ts — Screen component names
const SCREENS = {
  HOME: 'HomeScreen',
  SETTINGS: 'SettingsScreen',
} as const;
```

### 4. Bootstrap / Startup Pattern (Hiddify, AppFlowy)

```dart
// bootstrap.dart — Clean app initialization
Future<void> bootstrap() async {
  WidgetsFlutterBinding.ensureInitialized();

  // 1. Core services
  await Firebase.initializeApp();
  await Hive.initFlutter();

  // 2. DI registration
  setupServiceLocator();

  // 3. Run app
  runApp(
    ProviderScope(
      observers: [RiverpodObserver()],
      child: const App(),
    ),
  );
}

// main.dart
void main() => bootstrap();

// main_prod.dart — Production flavor
void main() {
  const env = Environment.production;
  bootstrap(env: env);
}
```

### 5. Draft Pairs for Forms (Expensify)

```typescript
// Every form has FORM + FORM_DRAFT for unsaved changes
const ONYX_KEYS = {
  WORKSPACE_SETTINGS_FORM: 'workspaceSettingsForm',
  WORKSPACE_SETTINGS_FORM_DRAFT: 'workspaceSettingsFormDraft',
} as const;

// Save draft on every keystroke → restore on crash/back
// Only commit FORM when user explicitly saves
```

### 6. Database Subscription Pattern (Mattermost)

```
database/
  models/         # WatermelonDB model definitions
  schema/         # DB structure + versioning
  migration/      # Schema migrations
  operator/       # Complex query logic (keeps models clean)
  subscription/   # Reactive UI updates from DB changes
  exceptions/     # Custom error classes
  manager/        # DB lifecycle (create, reset, destroy)
```

### 7. Functional Error Handling (Flutter — dartz)

```dart
// Instead of try/catch everywhere, use Either<Failure, Success>
Future<Either<AppException, User>> getUser(String id) async {
  try {
    final response = await dio.get('/users/$id');
    return Right(User.fromJson(response.data));
  } on DioException catch (e) {
    return Left(NetworkException(e.message));
  }
}

// Usage — forces caller to handle both cases
final result = await getUser('123');
result.fold(
  (failure) => showError(failure.message),
  (user) => showProfile(user),
);
```

### 8. Architecture Validation (Android Showcase — Konsist)

```kotlin
// Programmatically enforce architecture rules
@Test
fun `domain layer should not depend on data layer`() {
  Konsist.scopeFromModule("feature-album/domain")
    .classes()
    .assertFalse { it.hasImport { import -> import.hasNameContaining("data") } }
}

@Test
fun `use cases should have 'UseCase' suffix`() {
  Konsist.scopeFromModule("feature-album/domain")
    .classes()
    .withNameContaining("UseCase")
    .assertTrue { it.hasPublicFunction("invoke") }
}
```

---

## Platform-Specific Intelligence

### React Native — Must-Know Patterns

| Pattern | Old Way | New Way (2024-2025) | Source |
|---------|---------|---------------------|--------|
| Storage | AsyncStorage | MMKV (60x faster) | Ignite, Obytes |
| Routing | React Navigation | Expo Router (file-based) | Obytes |
| Server state | Redux + thunk | TanStack Query | Obytes, TCM |
| Client state | Redux | Zustand | Obytes |
| E2E testing | Detox | Maestro | Ignite, Obytes |
| Forms | Formik + Yup | TanStack Form + Zod | Obytes |
| Styling | StyleSheet | NativeWind (TailwindCSS) | Obytes |
| Animations | Animated API | Reanimated 3 | All |
| Images | Image | expo-image / FastImage | All |

### Flutter — Must-Know Patterns

| Pattern | Old Way | New Way (2024-2025) | Source |
|---------|---------|---------------------|--------|
| State | setState / Provider | Riverpod + code-gen | Immich, Hiddify, Spotube |
| State (alt) | BLoC manual | BLoC + freezed | AppFlowy |
| Navigation | Navigator 2.0 | auto_route / go_router | Immich / Hiddify |
| Database | sqflite | drift (type-safe ORM) | Immich, Spotube |
| Models | manual fromJson | freezed + json_serializable | All |
| i18n | .arb files | slang (type-safe, generated) | Hiddify |
| HTTP | http package | dio + smart_retry | Hiddify |
| HTTP (perf) | dio on all | cronet (Android) + cupertino_http (iOS) | Immich |
| Monorepo | N/A | Melos | Ente |
| DI | manual | Riverpod providers / GetIt | Immich / AppFlowy |

### iOS Swift — Must-Know Patterns

| Pattern | Traditional | Modern (2024-2025) | Source |
|---------|-------------|---------------------|--------|
| Architecture | MVVM manual | TCA (macro-driven) | Point-Free |
| DI | Swinject | @Dependency (Point-Free) / @Environment | TCA / nalexn |
| Testing | XCTest + mocks | TestStore (deterministic) | TCA |
| Navigation | NavigationView | NavigationStack + Coordinator | sergdort |
| Modularization | One target | Tuist multi-module | sergdort |
| Data binding | Combine | @Observable macro | iOS 17+ |
| SwiftUI testing | None | ViewInspector | nalexn |
| Concurrency | GCD / Combine | async/await + actors | All |

### Android Kotlin — Must-Know Patterns

| Pattern | Traditional | Modern (2024-2025) | Source |
|---------|-------------|---------------------|--------|
| UI | XML Views | Jetpack Compose | All |
| Architecture | MVVM | MVVM + UDF (Now in Android) | Google |
| DI | Dagger 2 | Hilt | Now in Android |
| DI (lightweight) | N/A | Koin | Android Showcase |
| Testing | Mockito | No-mock test doubles | Now in Android |
| Arch validation | Manual review | Konsist | Android Showcase |
| Performance | ProGuard | Baseline Profiles + R8 | Now in Android |
| Navigation | Fragment nav | Compose Navigation (type-safe) | All |
| Build config | build.gradle | Convention Plugins | Now in Android |
| Screenshot test | None | Roborazzi | Now in Android |

---

## Production Folder Structure Templates

### React Native (Expo Router — based on Obytes)

```
src/
  app/                    # Expo Router file-based routes
    (app)/                # Authenticated group
      _layout.tsx
      (tabs)/             # Tab navigator
    login.tsx
    onboarding.tsx
    _layout.tsx           # Root layout
  features/               # Feature modules
    auth/
      hooks/
      components/
      services/
      types.ts
    products/
      hooks/
      components/
      services/
  components/
    ui/                   # Design system (Button, Input, Card)
  lib/
    api/                  # Axios + TanStack Query setup
    auth/                 # Token management (Zustand + MMKV)
    hooks/                # Shared hooks
    i18n/                 # Internationalization
    storage.ts            # MMKV wrapper
    utils.ts              # Utilities
  translations/           # Language files
```

### Flutter (Riverpod + Clean — based on Immich)

```
lib/
  main.dart
  bootstrap.dart          # App initialization
  app/
    app.dart              # MaterialApp.router
    router.dart           # auto_route / go_router config
    theme/
  features/
    auth/
      domain/             # Entities, use cases, repo interfaces
      data/               # Repo impl, datasources, DTOs
      presentation/       # Screens + widgets
      providers/          # Riverpod providers
    [feature]/
  shared/
    widgets/              # Reusable UI
    extensions/           # Dart extensions
    constants/            # App-wide constants
    interfaces/           # Abstract contracts
    models/               # Shared DTOs
    utils/                # Utilities
  l10n/                   # Localization
```

### iOS SwiftUI (TCA — based on Point-Free + sergdort)

```
App/
  AppDelegate.swift
  AppModule.swift         # Composition root
Features/
  Auth/
    AuthFeature.swift     # @Reducer
    AuthView.swift        # SwiftUI View
    AuthClient.swift      # @Dependency
  Home/
    HomeFeature.swift
    HomeView.swift
  Settings/
Shared/
  Models/
  Extensions/
  UI/                     # Shared SwiftUI components
  Clients/                # API, Storage, Keychain
Platform/
  Networking/
  Persistence/
Tests/
  AuthFeatureTests.swift  # TestStore tests
```

### Android Kotlin (Now in Android — based on Google reference)

```
app/                      # Main application
core/
  common/                 # Shared utilities
  data/                   # Repository implementations
  database/               # Room database
  datastore/              # Proto DataStore
  network/                # Retrofit + OkHttp
  model/                  # Core models
  ui/                     # Shared Compose components
  testing/                # Test utilities
feature/
  auth/
    src/main/
      AuthScreen.kt       # Compose UI
      AuthViewModel.kt    # ViewModel
      AuthUiState.kt      # UI state sealed class
      navigation/          # Feature nav graph
  home/
  settings/
build-logic/              # Convention plugins
  convention/
    AndroidApplicationConventionPlugin.kt
    AndroidFeatureConventionPlugin.kt
```

---

## Decision Matrix — When to Use What

### State Management

| Condition | RN | Flutter | iOS | Android |
|-----------|-----|---------|-----|---------|
| Simple app (<10 screens) | Zustand | Riverpod | @Observable | ViewModel + StateFlow |
| Complex app (10-50 screens) | Zustand + TanStack Query | Riverpod + freezed | TCA | MVVM + Hilt + Flow |
| Enterprise (50+ screens) | Onyx (custom) / Redux Toolkit | BLoC + GetIt | TCA + Tuist | MVVM + Hilt + Convention Plugins |
| Offline-first | TanStack Query + WatermelonDB | Riverpod + drift | TCA + SwiftData | Room + WorkManager |

### Navigation

| Condition | RN | Flutter | iOS | Android |
|-----------|-----|---------|-----|---------|
| Expo project | Expo Router | — | — | — |
| RN CLI project | React Navigation | — | — | — |
| Type-safe routes | — | auto_route | NavigationStack | Compose Navigation |
| Declarative | Expo Router | go_router | NavigationStack | Compose Navigation |
| Deep linking | Expo Linking | app_links | Universal Links | App Links |

### Testing

| What | RN | Flutter | iOS | Android |
|------|-----|---------|-----|---------|
| Unit | Jest | test + mocktail | XCTest / TestStore | JUnit + no-mock doubles |
| Widget/Component | React Testing Library | widget test | ViewInspector | Compose Testing |
| E2E | Maestro | integration_test | XCUITest | Macrobenchmark |
| Screenshot | — | golden_toolkit | — | Roborazzi |
| Architecture | Dependency Cruiser | — | — | Konsist |
| Performance | Reassure | DevTools | Instruments | Baseline Profiles |
