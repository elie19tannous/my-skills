# iOS Native — Production Patterns

> Battle-tested patterns for iOS Swift development.
> Also used as reference for RN/Flutter iOS native module issues.

---

## Clean Architecture

```
ProjectName/
├── ProjectName.xcodeproj
├── ProjectName.xcworkspace       # CocoaPods workspace
├── Podfile                       # CocoaPods deps
├── Gemfile                       # Ruby deps for CocoaPods
├── ProjectName/
│   ├── App/
│   │   ├── AppDelegate.swift     # Or @main App struct
│   │   └── SceneDelegate.swift
│   ├── Domain/                   # Business logic (pure)
│   │   ├── Entities/             # Core business models
│   │   ├── UseCases/             # Business rules
│   │   └── Repositories/         # Repository protocols (contracts)
│   ├── Data/                     # Data layer (implements Domain)
│   │   ├── Repositories/         # Repository implementations
│   │   ├── Network/              # APIClient, endpoints
│   │   ├── Storage/              # KeychainManager, CoreData
│   │   └── DTOs/                 # Data transfer objects + mappers
│   ├── Presentation/             # UI layer
│   │   ├── Features/
│   │   │   ├── Auth/
│   │   │   │   ├── Views/
│   │   │   │   └── ViewModels/
│   │   │   └── [Feature]/
│   │   └── Shared/
│   │       ├── Components/
│   │       └── Utils/
│   └── Resources/
│       ├── Assets.xcassets
│       └── Info.plist
└── Pods/                         # CocoaPods output
```

### Dependency Rule
```
Presentation/ → Domain/ ← Data/

Views and ViewModels depend on Domain.
Data layer implements Domain protocols.
Domain depends on NOTHING.
```

## SwiftUI View + ViewModel (MVVM)

```swift
struct ProductListView: View {
    @StateObject private var viewModel = ProductListViewModel()

    var body: some View {
        NavigationStack {
            content
                .navigationTitle("Products")
                .refreshable { await viewModel.refresh() }
        }
        .task { await viewModel.loadIfNeeded() }
    }

    @ViewBuilder
    private var content: some View {
        switch viewModel.state {
        case .loading: ProgressView()
        case .loaded(let items) where items.isEmpty:
            ContentUnavailableView("No Items", systemImage: "tray")
        case .loaded(let items):
            List(items) { item in
                NavigationLink(value: item) { ItemRow(item: item) }
            }
        case .error(let error):
            ContentUnavailableView {
                Label("Error", systemImage: "exclamationmark.triangle")
            } description: { Text(error.localizedDescription) }
            actions: { Button("Retry") { Task { await viewModel.refresh() } } }
        }
    }
}

@MainActor
final class ProductListViewModel: ObservableObject {
    enum State { case loading, loaded([Product]), error(Error) }
    @Published private(set) var state: State = .loading

    private let useCase: GetProductsUseCase
    init(useCase: GetProductsUseCase = GetProductsUseCaseImpl()) { self.useCase = useCase }

    func loadIfNeeded() async {
        guard case .loading = state else { return }
        await refresh()
    }

    func refresh() async {
        state = .loading
        do { state = .loaded(try await useCase.execute()) }
        catch { state = .error(error) }
    }
}
```

## Networking

```swift
actor APIClient {
    func request<T: Decodable>(_ endpoint: Endpoint, as: T.Type) async throws -> T {
        var req = endpoint.urlRequest(baseURL: baseURL)
        if endpoint.requiresAuth {
            req.setValue("Bearer \(try await tokenProvider.token())", forHTTPHeaderField: "Authorization")
        }
        let (data, response) = try await URLSession.shared.data(for: req)
        guard let http = response as? HTTPURLResponse, (200...299).contains(http.statusCode) else {
            throw APIError.from(response: response as? HTTPURLResponse)
        }
        return try JSONDecoder().decode(T.self, from: data)
    }
}
```

## Keychain Storage

```swift
final class KeychainManager {
    static let shared = KeychainManager()
    func save(_ data: Data, for key: String) throws {
        let query: [CFString: Any] = [
            kSecClass: kSecClassGenericPassword, kSecAttrAccount: key,
            kSecValueData: data, kSecAttrAccessible: kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly,
        ]
        SecItemDelete(query as CFDictionary)
        guard SecItemAdd(query as CFDictionary, nil) == errSecSuccess else { throw KeychainError.saveFailed }
    }
    func load(for key: String) -> Data? {
        let query: [CFString: Any] = [
            kSecClass: kSecClassGenericPassword, kSecAttrAccount: key,
            kSecReturnData: true, kSecMatchLimit: kSecMatchLimitOne,
        ]
        var result: AnyObject?
        return SecItemCopyMatching(query as CFDictionary, &result) == errSecSuccess ? result as? Data : nil
    }
}
```

## CocoaPods

```ruby
# Podfile
platform :ios, '15.0'
use_frameworks!

target 'ProjectName' do
  pod 'Alamofire'
  pod 'Kingfisher'
  pod 'SnapKit'
end
```

```bash
cd ios && pod install
bundle exec pod install  # If using Bundler
```

## Common Pitfalls

| Pitfall | Fix |
|---------|-----|
| Force unwrap `!` | `guard let` / `??` |
| Retain cycles | `[weak self]` in closures |
| Main thread violation | `@MainActor` |
| `NavigationView` deprecated | `NavigationStack` |
| Hardcoded colors | Semantic: `Color(.label)` |

---

> No force unwraps. No retain cycles. `@MainActor` for all UI state.
> MVVM + Clean Architecture. Protocols for testability.
