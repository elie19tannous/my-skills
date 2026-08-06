# Platform Excellence — iOS vs Android Guidelines

> Not one-size-fits-all. Follow native platform guidelines.

## Philosophy

❌ **BAD**: Same UI for both platforms
✅ **GOOD**: Platform-specific UI, shared business logic
🎯 **TARGET**: >80% code sharing, 100% platform-native UX

---

## iOS 18+ Guidelines

### Navigation
- Use NavigationStack, not legacy NavigationView
- Tab bar at bottom, always visible
- Back button top-left, standard chevron
- Swipe from left edge to go back

### Interactions
- Haptic feedback for important actions
- 3D Touch / Haptic Touch context menus
- Swipe actions (leading/trailing)
- Pull-to-refresh standard

### Typography
- SF Pro (system font)
- Dynamic Type support (accessibility)
- Hierarchy: Large Title > Title > Headline > Body

### Colors
- Support Light + Dark mode
- Use semantic colors (not hardcoded)
- Respect user's appearance preference

---

## Android 15+ / Material 3

### Navigation
- Navigation drawer from left
- Bottom navigation (3-5 items)
- Back button (system or top-left arrow)
- Floating Action Button (FAB) for primary action

### Interactions
- Ripple effect on touch
- Material You (dynamic colors from wallpaper)
- Long-press for context menu
- Swipe-to-dismiss (lists, cards)

### Typography
- Roboto (system font)
- Material Type Scale: Display > Headline > Title > Body

### Colors
- Material 3 color system (primary, secondary, tertiary)
- Support Light + Dark theme
- Dynamic color (Material You)

---

## Performance Standards

| Metric | iOS | Android |
|--------|-----|---------|
| **Cold start** | < 1.0s | < 1.5s |
| **Memory baseline** | < 120MB | < 100MB |
| **FPS** | 60 (120 ProMotion) | 60 (90/120 if supported) |
| **Battery** | < 4%/hour | < 4%/hour |
| **Touch response** | < 16ms | < 16ms |

---

## Platform-Specific Features

### iOS Only
- Face ID / Touch ID (biometrics)
- HealthKit (health data)
- Apple Pay
- SiriKit (voice)
- WidgetKit (home screen widgets)
- Live Activities (Dynamic Island)

### Android Only
- Google Pay
- Widgets (home screen, lock screen)
- Background services (more flexible)
- File system access
- USB/Bluetooth flexibility

---

## Code Sharing Strategy

```
SHARE (Business Logic):
├── API calls
├── Data models
├── State management
├── Business rules
└── Validation logic

PLATFORM-SPECIFIC (UI):
├── Navigation patterns
├── Gesture handling
├── Platform components
└── Platform animations
```

Example (React Native):
```typescript
// Shared: business logic
export const useAuth = () => {
  const login = async (email, password) => { ... }  // Shared
  return { login }
}

// Platform-specific: UI
import { LoginScreen as IOSLogin } from './LoginScreen.ios'
import { LoginScreen as AndroidLogin } from './LoginScreen.android'

export const LoginScreen = Platform.select({
  ios: IOSLogin,
  android: AndroidLogin
})
```

---

## Comparison Matrix

| Feature | iOS Guideline | Android Guideline |
|---------|---------------|-------------------|
| **Back nav** | Top-left chevron | System back / top-left arrow |
| **Tab bar** | Bottom, always visible | Bottom navigation |
| **Search** | Top, expandable | Top, collapsible |
| **FAB** | Rare, use + in nav bar | Common, bottom-right |
| **Context menu** | Haptic Touch | Long-press |
| **Swipe actions** | Leading/trailing | Swipe-to-dismiss |
| **Notifications** | Banner, center | Banner, top |
| **Dark mode** | System-controlled | System-controlled |

---

## iOS Haptics

```swift
// 3 feedback types — use the right one
UIImpactFeedbackGenerator(style: .medium).impactOccurred()  // button tap, card flip
UINotificationFeedbackGenerator().notificationOccurred(.success)  // save success / error / warning
UISelectionFeedbackGenerator().selectionChanged()  // picker scroll, toggle

// ✅ Rules
// - Impact: physical interactions (drag drop, button press)
// - Notification: outcomes (success, error, warning) — max 1 per action
// - Selection: discrete value changes (picker, slider step)
// ⛔ Never chain multiple haptics in <300ms
// ⛔ Never use for routine navigation (back, tab switch)
```

## Permission Timing (iOS/Android)

```
RULE: Ask ONLY when the feature needs it — not at launch

Permission     When to ask
─────────────────────────────────────────────────────
Camera         User taps "Take Photo" button
Location       User taps "Find Nearby" or map feature
Contacts       User taps "Invite from Contacts"
Notifications  After onboarding, show a pre-permission dialog first
Microphone     User taps "Record Voice Note"

PRE-PERMISSION DIALOG (iOS — before system prompt):
"Get notified when teammates reply"
[Allow] [Not now]
→ Only show system prompt if user taps Allow
→ Saves 1 chance at permission — don't waste it at cold start
```

## Ratings Timing

```
// 2-step flow — ask only after success
Step 1: "Is [App] helping you get things done?"
        [Yes!] [Not really]

Step 2 (if Yes): "Mind leaving a review? It helps us a lot."
                 [Sure] [Maybe later]
Step 2 (if No):  "What's getting in the way?" [Give feedback]

// iOS: Use SKStoreReviewController.requestReview() — max 3x/year
// Android: Use ReviewManager from Play Core library
// NEVER ask after an error, payment, or on app cold start
```

## Live Activities / Dynamic Island (iOS 16.1+)

```swift
// 1. Define attributes
struct DeliveryAttributes: ActivityAttributes {
    struct ContentState: Codable, Hashable {
        var status: String
        var eta: Date
    }
    var orderId: String
}

// 2. Start activity
let initialState = DeliveryAttributes.ContentState(status: "Preparing", eta: Date())
let activity = try? Activity.request(
    attributes: DeliveryAttributes(orderId: "123"),
    content: .init(state: initialState, staleDate: nil)
)

// 3. Update
await activity?.update(.init(state: .init(status: "Out for delivery", eta: Date()), staleDate: nil))

// 4. End
await activity?.end(dismissalPolicy: .default)
```

---

## Anti-Patterns

```
❌ Material Design on iOS
❌ iOS navigation on Android
❌ Ignoring platform conventions
❌ "Write once, look mediocre everywhere"
❌ Asking permissions at app launch
❌ Chaining multiple haptics back-to-back
❌ Rating prompt right after install

✅ Native look & feel per platform
✅ Shared logic, platform UI
✅ Respect platform guidelines
✅ "Write once, look native everywhere"
✅ Ask permissions at the moment they're needed
✅ Rating prompts only after clear success moments
```
