# UI/UX Mobile — Screen Design & Implementation

> Use when: "create screen X", "build UI for Y", "design this layout", "demo screen", "mockup".
> Covers: design system, screen templates, navigation, touch, color, typography, animation, accessibility.

---

## Design Decision Framework

**Before any screen, answer these:**

```
SCREEN: [name / purpose]
PLATFORM: [iOS / Android / Cross-platform]
TYPE: [form / list / detail / dashboard / chat / auth / onboarding]
DATA: [static / API / real-time / offline-first]
PRIORITY: [speed-to-build / pixel-perfect / accessibility-first]
```

**Then auto-think:**

```
<think>
SCREEN: [description]
TEMPLATE: [closest match from templates below]
TOKENS: [which design tokens to use]
STATES: loading / error / empty / success
NAVIGATION: [how user arrives + leaves]
PLATFORM RULES: [iOS HIG / Material Design 3 specifics]
TOUCH: [primary CTA in thumb zone?]
DARK MODE: [semantic colors, no hardcoded]
A11Y: [labels, contrast, Dynamic Type]
</think>
```

---

## Design Token Architecture (3 Layers)

```
Primitive tokens:   blue-500, spacing-4         (raw values)
     ↓
Semantic tokens:    color-primary, text-error    (purpose-based)
     ↓
Component tokens:   button-bg, card-radius       (component-specific)
```

**Rule: NEVER hardcode values. Always use design tokens.**

### React Native

```typescript
// theme/tokens.ts
export const colors = {
  primary: '#007AFF',
  secondary: '#5856D6',
  background: '#FFFFFF',
  surface: '#F2F2F7',
  text: '#000000',
  textSecondary: '#8E8E93',
  error: '#FF3B30',
  success: '#34C759',
  warning: '#FF9500',
  border: '#E5E5EA',
  dark: {
    background: '#000000',    // OLED: true black = 0% battery
    surface: '#1C1C1E',       // elevation level 1
    surfaceElevated: '#2C2C2E', // elevation level 2
    text: '#E0E0E0',          // NOT pure white (causes eye strain)
    textSecondary: '#8E8E93',
    border: '#38383A',
  },
};

export const spacing = {
  xs: 4, sm: 8, md: 16, lg: 24, xl: 32, xxl: 48,
};

export const radius = {
  sm: 8, md: 12, lg: 16, xl: 24, full: 9999,
};

export const fontSize = {
  caption: 12, body: 16, title: 20, heading: 28, hero: 34,
};

export const shadow = {
  sm: { shadowOffset: { width: 0, height: 1 }, shadowOpacity: 0.1, shadowRadius: 2, elevation: 2 },
  md: { shadowOffset: { width: 0, height: 4 }, shadowOpacity: 0.15, shadowRadius: 8, elevation: 4 },
  lg: { shadowOffset: { width: 0, height: 8 }, shadowOpacity: 0.2, shadowRadius: 16, elevation: 8 },
};
```

### Flutter

```dart
// theme/app_theme.dart
class AppTheme {
  static ThemeData light() => ThemeData(
    colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF007AFF)),
    useMaterial3: true,
    textTheme: const TextTheme(
      headlineLarge: TextStyle(fontSize: 34, fontWeight: FontWeight.bold),
      titleLarge: TextStyle(fontSize: 20, fontWeight: FontWeight.w600),
      bodyLarge: TextStyle(fontSize: 16),
      bodySmall: TextStyle(fontSize: 12, color: Color(0xFF8E8E93)),
    ),
  );

  static ThemeData dark() => ThemeData(
    colorScheme: ColorScheme.fromSeed(
      seedColor: const Color(0xFF007AFF),
      brightness: Brightness.dark,
    ),
    useMaterial3: true,
  );
}
```

---

## Platform Color Rules

### iOS Semantic Colors (auto light/dark)

```
Label:        .label → primary text
SecondaryLabel: → secondary text
SystemBackground: → screen bg
SecondarySystemBackground: → card/section bg
Separator: → thin dividers
```

### Android Material You (Dynamic Color)

```
API 31+: Colors extracted from wallpaper automatically
Primary / Secondary / Tertiary + On variants
Surface: elevation = slightly lighter overlay
  0dp = 0% overlay | 4dp = 9% | 8dp = 12% | 12dp = 14%
```

### OLED Battery Impact

| Color | Battery Usage |
|-------|--------------|
| #000000 (true black) | 0% |
| #1A1A1A (near black) | ~15% |
| #333333 (dark gray) | ~30% |
| #FFFFFF (white) | 100% |

**Rule:** Dark mode backgrounds = `#000000`. Surfaces = `#0D0D0D` to `#1C1C1E`.

---

## Typography System

### iOS (SF Pro)

| Style | Size | Weight | Usage |
|-------|------|--------|-------|
| Large Title | 34pt | Bold | Screen titles |
| Title 1 | 28pt | Bold | Section titles |
| Title 3 | 20pt | Semibold | Subtitles |
| Body | 17pt | Regular | Main content |
| Callout | 16pt | Regular | Secondary content |
| Caption 1 | 12pt | Regular | Labels, timestamps |

### Android (Roboto / Material 3)

| Style | Size | Weight | Usage |
|-------|------|--------|-------|
| Display Large | 57sp | Regular | Hero text |
| Headline Medium | 28sp | Regular | Section titles |
| Title Large | 22sp | Regular | Card titles |
| Body Large | 16sp | Regular | Main content |
| Body Medium | 14sp | Regular | Supporting text |
| Label Small | 11sp | Medium | Captions, chips |

**Critical rules:**
- iOS: Dynamic Type is MANDATORY, not optional
- Android: always use `sp` for text, `dp` for everything else
- Test at 200% font scale — UI must not break
- Dark mode: text appears thinner (halation) — consider medium weight

---

## Touch & Thumb Zone

### Touch Targets

| Platform | Minimum | Recommended | Critical Actions |
|----------|---------|-------------|-----------------|
| iOS (HIG) | 44×44 pt | 48×48 pt | 56+ pt |
| Android (Material) | 48×48 dp | 48×48 dp | 56+ dp |
| Between targets | 8 dp gap | 12 dp gap | |
| WCAG 2.2 | 44×44 px | — | — |

**Rule:** Use `hitSlop` (RN) or `MaterialTapTargetSize.padded` (Flutter) if visual size is smaller.

### Thumb Zone (One-Handed Use)

```
┌─────────────────────────┐
│   HARD        HARD      │  ← Top corners (status, settings)
│                         │
│   OK          OK        │  ← Middle area
│                         │
│   EASY    ██  EASY      │  ← Bottom = PRIMARY CTAs go here
│          THUMB          │
│  [Tab1] [Tab2] [Tab3]   │  ← Tab bar in easy zone
└─────────────────────────┘

49% of users hold phone one-handed.
Primary CTA → bottom.
Destructive actions → top-left (hardest to reach = safer).
```

### Haptic Feedback

| Action | iOS | Android |
|--------|-----|---------|
| Toggle/selection | `selection` (light) | `TICK` |
| Button tap | `medium` | `CLICK` |
| Important confirm | `heavy` | `HEAVY_CLICK` |
| Success | `success` | `DOUBLE_CLICK` |
| Error | `error` | `REJECT` |

---

## Navigation Patterns

### Decision Tree

```
3-5 top-level sections  → Tab Bar / Bottom Navigation
Deep hierarchy (>2 levels) → Stack Navigation
Many destinations (>5)  → Drawer Navigation
Single linear flow       → Stack only (wizard/onboarding)
Tablet / Foldable        → Navigation Rail + List-Detail
```

### Tab Bar Rules

| Rule | iOS | Android |
|------|-----|---------|
| Max items | 5 | 5 |
| Height | 49pt | 80dp |
| Icon size | 25×25pt (SF Symbols) | 24dp (Material Symbols) |
| Labels | Always visible | Always visible |
| Active state | Filled icon + tint | Filled icon + indicator pill |
| On tab switch | Preserve each tab's navigation stack |
| Deep link | Construct full back stack |

### Critical Navigation Rules

```
✅ Each tab maintains its own navigation stack
✅ System back button works predictably
✅ Deep link URLs match navigation path
⛔ NEVER use modals for everything — use push navigation
⛔ NEVER reset tab stack on tab switch
⛔ NEVER override platform back gesture
```

---

## Screen Templates

### 1. Login Screen

```
┌─────────────────────────┐
│                         │
│         [Logo]          │
│     App Name / Tagline  │
│                         │
│  ┌───────────────────┐  │
│  │ Email             │  │
│  └───────────────────┘  │
│  ┌───────────────────┐  │
│  │ Password      👁  │  │
│  └───────────────────┘  │
│                         │
│  [  Forgot password?  ] │
│                         │
│  ┌───────────────────┐  │
│  │     Sign In       │  │  ← Primary CTA (full width)
│  └───────────────────┘  │
│                         │
│  ── or continue with ── │
│  [Google] [Apple] [FB]  │  ← Social login row
│                         │
│  Don't have account?    │
│  [Sign Up]              │
└─────────────────────────┘
```

**Rules:** `KeyboardAvoidingView` (RN) / `SingleChildScrollView` (Flutter). Password toggle. Disable button during loading. Show inline error below input, not toast.

### 2. Home / Feed

```
┌─────────────────────────┐
│  [☰]   Home    [🔔][👤]│  ← Header: menu, title, actions
├─────────────────────────┤
│  ┌───────────────────┐  │
│  │ 🔍 Search...      │  │
│  └───────────────────┘  │
│  [Filter chips scrollH] │  ← Horizontal scroll filter
│  ┌───────────────────┐  │
│  │  Card 1           │  │
│  │  Image + Title    │  │  ← FlatList / ListView.builder
│  │  Subtitle + Meta  │  │
│  └───────────────────┘  │
│  ┌───────────────────┐  │
│  │  Card 2           │  │
│  └───────────────────┘  │
│         ...             │
├─────────────────────────┤
│  [🏠] [🔍] [➕] [💬] [👤]│  ← Bottom tab bar
└─────────────────────────┘
```

**Rules:** `FlatList` / `ListView.builder` — NEVER `ScrollView` for dynamic lists. Pull-to-refresh. Pagination. Loading skeleton. Empty state. `key`/`Key` on each item.

### 3. Detail Screen

```
┌─────────────────────────┐
│  [←]   Detail    [⋮]   │
├─────────────────────────┤
│  ┌───────────────────┐  │
│  │   Hero Image      │  │  ← Full width, 16:9
│  └───────────────────┘  │
│  Title (heading)        │
│  Subtitle / category    │
│  ★★★★☆  4.2 (128)      │
│                         │
│  Description text...    │
│                         │
│  ── Related ──────────  │
│  [Card] [Card] [Card]→  │  ← Horizontal scroll
├─────────────────────────┤
│  [$29.99]  [Add to Cart]│  ← Sticky bottom CTA
└─────────────────────────┘
```

**Rules:** `ScrollView` OK (single item). Sticky bottom bar outside scroll. Safe area at bottom. Share/bookmark in header.

### 4. Profile / Settings

```
┌─────────────────────────┐
│  [←]   Profile   [Edit] │
├─────────────────────────┤
│       ┌─────┐           │
│       │ 👤  │           │  ← Avatar (circular)
│       └─────┘           │
│     John Doe            │
│     john@email.com      │
│  ┌───────────────────┐  │
│  │ Account          > │  │
│  ├───────────────────┤  │
│  │ Notifications    > │  │  ← Grouped sections with chevrons
│  ├───────────────────┤  │
│  │ Appearance       > │  │
│  ├───────────────────┤  │
│  │ Privacy          > │  │
│  └───────────────────┘  │
│  ┌───────────────────┐  │
│  │ Terms             > │  │
│  ├───────────────────┤  │
│  │ Help              > │  │
│  └───────────────────┘  │
│  [     Sign Out       ] │  ← Red/destructive
│  App v2.1.0             │
└─────────────────────────┘
```

### 5. Onboarding (Swipeable)

```
┌─────────────────────────┐
│                  [Skip] │
│     ┌───────────┐       │
│     │ Illustration │    │
│     └───────────┘       │
│    Welcome to AppName   │
│    Short description    │
│       ● ○ ○             │  ← Page indicator dots
│  ┌───────────────────┐  │
│  │    Get Started     │  │  ← Last page: primary CTA
│  └───────────────────┘  │
└─────────────────────────┘
```

**Rules:** 3-5 pages max. Skip always visible. Last page = CTA. Store `hasSeenOnboarding`.

### 6. Form / Multi-Step

```
┌─────────────────────────┐
│  [←]   Create    [Save] │
├─────────────────────────┤
│  Step 1 of 3  ●●○       │  ← Progress indicator
│                         │
│  Title *                │
│  ┌───────────────────┐  │
│  │                   │  │
│  └───────────────────┘  │
│  ⚠ Title is required    │  ← Inline error (red, below input)
│                         │
│  Category               │
│  ┌───────────────────┐  │
│  │ Select...        ▼│  │
│  └───────────────────┘  │
│                         │
│  Description            │
│  ┌───────────────────┐  │
│  │                   │  │
│  │                   │  │
│  └───────────────────┘  │
│  0/500                  │  ← Character count
│                         │
├─────────────────────────┤
│  [Back]      [Continue] │  ← Sticky bottom
└─────────────────────────┘
```

**Rules:** Validate on blur. Show errors inline below input. Disable submit while loading. `KeyboardAvoidingView`. Mark required fields with `*`. Unsaved changes warning on back.

### 7. Chat / Messages

```
┌─────────────────────────┐
│  [←]  John Doe   [📞][⋮]│
├─────────────────────────┤
│         Today           │
│                         │
│  ┌─────────────┐       │
│  │ Hey, how are │       │  ← Received (left, gray bg)
│  │ you?         │       │
│  └─────────────┘ 10:30  │
│                         │
│       ┌─────────────┐  │
│       │ I'm good!   │  │  ← Sent (right, primary color)
│       │ Thanks      │  │
│       └─────────────┘  │
│                   10:31 │
│                         │
│  ┌─────────────┐       │
│  │ ···          │       │  ← Typing indicator
│  └─────────────┘       │
├─────────────────────────┤
│  [+] [Message...   ] [→]│  ← Input bar + send
└─────────────────────────┘
```

**Rules:** `FlatList inverted` (RN) / `ListView reverse` (Flutter). Auto-scroll on new message. Typing indicator. Timestamp grouping (Today/Yesterday/date). Input bar above keyboard.

### 8. Search Results

```
┌─────────────────────────┐
│  [←] ┌───────────────┐  │
│      │ pizza nearby ✕ │  │  ← Search with clear button
│      └───────────────┘  │
├─────────────────────────┤
│  Recent: [sushi] [tacos]│  ← Search history chips
│                         │
│  3 results for "pizza"  │
│  ┌───────────────────┐  │
│  │ 🍕 Pizza Palace   │  │
│  │ ★4.5 · 0.3mi · $$ │  │
│  └───────────────────┘  │
│  ┌───────────────────┐  │
│  │ 🍕 Mario's        │  │
│  └───────────────────┘  │
└─────────────────────────┘
```

**Rules:** Debounce search input (300ms+). Show recent searches. Show "No results" with suggestions, never blank. Autocomplete dropdown as user types.

---

## Component Patterns

### Bottom Sheet

```typescript
// RN: @gorhom/bottom-sheet
<BottomSheet snapPoints={['25%', '50%', '90%']}>
  <BottomSheetView>{/* content */}</BottomSheetView>
</BottomSheet>

// Flutter: showModalBottomSheet
showModalBottomSheet(
  context: context,
  isScrollControlled: true,
  builder: (context) => DraggableScrollableSheet(...),
);
```

### Empty State

```
┌─────────────────────────┐
│     [Illustration]      │
│    No items yet         │  ← Clear title
│    Add your first item  │  ← Helpful subtitle
│    to get started.      │
│  [  + Add Item  ]       │  ← Action button
└─────────────────────────┘
```

**Rule:** Every list screen MUST have an empty state. Never show blank screen.

### Loading Skeleton

```
Show skeleton ONLY when there is no data to display.
If cached data exists → show stale data + refresh indicator.
Skeleton shape MUST match final UI layout.
Show 3-5 skeleton items.
```

### Toast / Snackbar

```
Position:  bottom (Android) or top (iOS)
Duration:  3s (info), 5s (error), persistent (action required)
Actions:   max 1 button ("Undo", "Retry")
Never:     block UI or require dismiss for non-critical info
```

### Confirmation Dialog

```
Destructive actions (delete, sign out) → ALWAYS confirm first.
Title:   "Delete item?"
Message: "This action cannot be undone."
Actions: [Cancel] [Delete] ← destructive button in red
```

---

## Dark Mode

```typescript
// RN: useColorScheme()
const scheme = useColorScheme(); // 'light' | 'dark'
const bg = scheme === 'dark' ? colors.dark.background : colors.background;

// Flutter: Theme.of(context).brightness
final isDark = Theme.of(context).brightness == Brightness.dark;
```

**Rules:**
- NEVER hardcode colors — always semantic tokens
- Dark text on dark bg: use `#E0E0E0`, NOT pure `#FFFFFF` (eye strain)
- Shadows: reduce or remove (invisible on dark backgrounds)
- Borders: use lighter shade (`#38383A`, not `#E5E5EA`)
- Images: add dark variant or semi-transparent overlay
- Elevation in dark = slightly lighter surface (Material guideline)

---

## Animation Guidelines

| Animation | Duration | Easing |
|-----------|----------|--------|
| Button press | 100ms | ease-out |
| Screen transition | 300ms | ease-in-out |
| Bottom sheet open | 250ms | spring (damping 0.8) |
| Fade in content | 200ms | ease-in |
| List item appear | 150ms stagger | ease-out |

**Rules:**
- `useNativeDriver: true` (RN) — always for transforms/opacity
- 60 FPS target — no layout animations on main thread
- Animate ONLY `transform` and `opacity` (never `width`/`height`/`top`/`left`)
- Reduce motion: `AccessibilityInfo.isReduceMotionEnabled` (RN) / `MediaQuery.disableAnimations` (Flutter)
- No animation > 500ms (feels sluggish)
- Never apply universal `transition: all` — specify properties

---

## Accessibility Checklist

| Check | RN | Flutter |
|-------|-----|---------|
| Screen reader label | `accessibilityLabel` | `Semantics(label:)` |
| Button role | `accessibilityRole="button"` | `Semantics(button: true)` |
| Image alt text | `accessible={true} accessibilityLabel` | `Semantics(image: true, label:)` |
| Focus order | `accessibilityElementsHidden` | `ExcludeSemantics` |
| Color contrast | 4.5:1 (text), 3:1 (large text) | Same ratios |
| Font scaling | Support Dynamic Type | `MediaQuery.textScaleFactor` |
| State changes | `accessibilityLiveRegion` | `Semantics(liveRegion: true)` |

**Rules:**
- Every interactive element needs a label
- Every image needs alt text (or `decorative` flag)
- Never rely on color alone to convey meaning (add icons/text)
- Test with VoiceOver (iOS) and TalkBack (Android)
- Test at 200% font scale
- Visible focus indicators on all interactive elements

---

## UX Anti-Patterns (Never Do These)

| Anti-Pattern | Why | Fix |
|-------------|------|-----|
| `ScrollView` for long lists | Memory explosion | `FlatList` / `ListView.builder` |
| Hardcoded colors | Breaks dark mode | Semantic design tokens |
| Touch target < 44pt | Frustrating taps | Min 44pt iOS / 48dp Android |
| No empty state | Confusing blank screen | Illustration + message + CTA |
| Error only at form top | User can't find which field | Inline error below each input |
| Silent failures | User doesn't know what happened | Toast/banner with retry option |
| Modal for everything | Feels trapped | Stack navigation for content flow |
| Auto-play video | Drains battery + data | Click-to-play or pause off-screen |
| Placeholder as only label | Disappears on focus | Persistent label above input |
| Layout shift on load | Jarring CLS | Reserve space / skeleton placeholders |
| `100vh` on mobile | Address bar overlap | `dvh` or platform safe area |
| No loading indicator | UI feels frozen | Skeleton or spinner after 300ms |

---

## Self-Critique Protocol

**After generating any screen, ask:**

```
1. "Does this look like a default template?" → If yes, customize tokens/spacing
2. "Would a user know what to do first?" → If unclear, strengthen visual hierarchy
3. "What happens on error/empty/loading?" → If any missing, add them
4. "Does primary CTA sit in thumb zone?" → If not, move to bottom
5. "Can I use this in dark mode?" → If hardcoded colors, fix
6. "Does it pass 44pt touch targets?" → If buttons are small, enlarge
```

**If the screen could be mistaken for a tutorial demo, it needs more design work.**

---

## Screen Sizing Reference

| Device | Width (pt/dp) | Safe Area Top | Safe Area Bottom |
|--------|--------------|---------------|-----------------|
| iPhone SE | 375 | 20 | 0 |
| iPhone 15 | 393 | 59 | 34 |
| iPhone 15 Pro Max | 430 | 59 | 34 |
| Android small | 360 | 24 (status) | 48 (nav bar) |
| Android large | 412 | 24 | 48 |
| iPad | 768-1024 | 24 | 20 |

**Rules:**
- Always use `SafeAreaView` (RN) / `SafeArea` (Flutter)
- Design for 375pt width (smallest common), scale up
- Test on smallest AND largest device
- Scrollable content — never assume fixed heights

---

> Mobile is NOT a small desktop. Touch-first, thumb-zone aware, battery conscious.
> Tokens first, 4 states always, platform rules respected, accessibility mandatory.
