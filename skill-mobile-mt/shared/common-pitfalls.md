# Common Pitfalls — Problem → Symptoms → Solution

> Cross-platform mobile mistakes. Learn from production incidents.

---

## 1. setState After Unmount

| | |
|--|--|
| **Problem** | Async operation completes after screen is popped/unmounted |
| **Symptoms** | "Can't perform a React state update on an unmounted component" / crash |
| **Solution (RN)** | Track mounted state: `useRef` + cleanup in `useEffect` return |
| **Solution (Flutter)** | Check `mounted` before `setState`, cancel in `dispose()` |
| **Solution (iOS)** | Use `Task` with cancellation, `[weak self]` in closures |
| **Solution (Android)** | Use `viewModelScope` (auto-cancels), `Lifecycle`-aware coroutines |

## 2. Token Refresh Race Condition

| | |
|--|--|
| **Problem** | Multiple 401 responses trigger multiple token refresh calls |
| **Symptoms** | Duplicate refresh requests, token corruption, logout loops |
| **Solution** | Queue all 401s, refresh once, replay queued requests with new token |

## 3. List Performance (ScrollView Trap)

| | |
|--|--|
| **Problem** | Using ScrollView / Column for dynamic lists |
| **Symptoms** | Jank, high memory, slow render with 50+ items |
| **Solution (RN)** | `FlatList` with `keyExtractor`, `getItemLayout`, `removeClippedSubviews` |
| **Solution (Flutter)** | `ListView.builder` or `SliverList` (lazy rendering) |
| **Solution (Android)** | `LazyColumn` with stable `key` |

## 4. Memory Leak — Listeners Not Cleaned

| | |
|--|--|
| **Problem** | Event listeners, subscriptions, timers created but never removed |
| **Symptoms** | Memory grows over time, app slows down, eventual crash |
| **Solution (RN)** | Always return cleanup in `useEffect`: `return () => listener.remove()` |
| **Solution (Flutter)** | `StreamSubscription.cancel()` and `controller.dispose()` in `dispose()` |
| **Solution (iOS)** | Remove `NotificationCenter` observers, cancel `Task`s |
| **Solution (Android)** | Unregister `BroadcastReceiver`, cancel coroutine scopes |

## 5. Hardcoded Strings / Magic Numbers

| | |
|--|--|
| **Problem** | Colors, sizes, URLs, keys scattered as literals in code |
| **Symptoms** | Inconsistent UI, hard to maintain, hard to theme |
| **Solution** | Constants file for colors/spacing, env config for URLs/keys |

## 6. Missing Error Boundaries

| | |
|--|--|
| **Problem** | Uncaught error in one component crashes the entire app |
| **Symptoms** | White screen of death, full app crash |
| **Solution (RN)** | Wrap with `ErrorBoundary` component at screen/feature level |
| **Solution (Flutter)** | `ErrorWidget.builder` + try/catch in async providers |
| **Solution (iOS)** | Graceful error states in every View (`.error` case in ViewModel) |
| **Solution (Android)** | Sealed `UiState` with `Error` case, never let exceptions propagate to UI |

## 7. Deep Link Injection

| | |
|--|--|
| **Problem** | Deep link parameters used directly without validation |
| **Symptoms** | Navigation to unauthorized screens, data exposure |
| **Solution** | Validate all deep link params (type, format, authorization) before navigating |

## 8. Button Double-Tap

| | |
|--|--|
| **Problem** | User taps submit button twice during async operation |
| **Symptoms** | Duplicate API calls, duplicate records, charge twice |
| **Solution** | `isSubmitting` flag — disable button during async operation |

## 9. Large Images Unoptimized

| | |
|--|--|
| **Problem** | Loading full-resolution images from server |
| **Symptoms** | High memory, slow scroll, OOM crash on old devices |
| **Solution** | Request resized images from CDN, use `cached_network_image` / `FastImage`, progressive loading |

## 10. Missing Offline Handling

| | |
|--|--|
| **Problem** | App assumes network is always available |
| **Symptoms** | Crash or infinite loading when offline, data loss |
| **Solution** | Cache critical data locally, show cached data + "offline" banner, queue operations for retry |

## 11. Platform-Specific Ignoring

| | |
|--|--|
| **Problem** | Testing only on iOS, shipping broken Android (or vice versa) |
| **Symptoms** | Android back button doesn't work, keyboard covers input, notch/status bar overlap |
| **Solution** | Test on BOTH platforms. Handle: back button, safe area, keyboard avoidance, permissions |

## 12. Wrong Package Manager

| | |
|--|--|
| **Problem** | Using `npm install` in a `yarn.lock` project |
| **Symptoms** | Conflicting lock files, dependency resolution differs, CI fails |
| **Solution** | Check lock file first. `yarn.lock` → yarn. `package-lock.json` → npm. Never mix. |

---

> Every pitfall here has caused a production incident.
> Learn from others' mistakes.
