# CLAUDE.md Template for Mobile Projects

> Copy this file to your project root as `CLAUDE.md`.
> Claude Code reads it automatically every session — no invocation needed.

---

## How to use

1. Copy this file to your project: `cp CLAUDE.md.template CLAUDE.md`
2. Edit the sections marked with `[FILL IN]`
3. Claude will follow these rules automatically in every conversation

---

## Template (copy below this line)

---

# Project: [FILL IN: Your App Name]

## Stack

- **Framework:** [React Native CLI / Expo SDK XX / Flutter X.X / iOS / Android]
- **Language:** [TypeScript / JavaScript / Dart / Swift / Kotlin]
- **State:** [Redux Toolkit / Zustand / Riverpod / BLoC / StateFlow]
- **Navigation:** [React Navigation v6 / Expo Router / GoRouter / UIKit / Jetpack]
- **API:** [axios / fetch / Dio / Firebase / GraphQL]
- **Package Manager:** [yarn / npm / pnpm / bun / flutter pub]

## Project Structure

```
[FILL IN: paste your src/ or lib/ tree here]
src/
├── features/
│   ├── auth/
│   └── home/
├── shared/
│   ├── components/
│   └── utils/
```

## Conventions

- **Naming:** [PascalCase screens, camelCase hooks/services]
- **Imports:** [absolute @/ aliases / relative paths]
- **Styling:** [StyleSheet / NativeWind / styled-components / Compose / SwiftUI]

## Auto-Check Rules (apply after EVERY code change)

Before saying "done" on any task, automatically verify:

```
□ No console.log / print / NSLog in production code
□ No hardcoded secrets, API keys, or tokens
□ No token storage in AsyncStorage / SharedPreferences / UserDefaults
□ All async operations wrapped in try/catch
□ All 4 states handled: loading / error / empty / success
□ useEffect / dispose / viewModelScope has cleanup
□ FlatList (not ScrollView) for lists > 20 items
□ No force unwrap (! / !! / as!) without null check
□ TypeScript: no implicit 'any'
□ New screens registered in navigator
□ Imports resolve (no broken paths)
```

If ANY check fails → fix it before marking done.

## Performance Rules (apply when building lists, animations, heavy screens)

```
□ FlatList with keyExtractor + getItemLayout (if fixed height)
□ React.memo on list item components
□ useCallback on handlers passed to list items
□ Images: use FastImage / expo-image, specify width+height
□ Animations: use react-native-reanimated (not Animated API)
□ No heavy computation on main thread (use InteractionManager)
```

## Security Rules (non-negotiable)

```
□ Tokens → SecureStore / Keychain / EncryptedSharedPreferences ONLY
□ Deep link params → validate before use
□ API calls → HTTPS only
□ Sensitive data → never in logs
□ User input → sanitize before display (XSS)
```

## What NOT to do

```
□ NEVER suggest migrating to a different framework/architecture
□ NEVER change state management library
□ NEVER add packages without checking SDK compatibility first
□ NEVER mix package managers (yarn + npm)
□ NEVER create new files for one-off operations
□ NEVER add comments to code you didn't change
```

## Preferred Commands

```bash
# Install
[yarn install / npm install / flutter pub get / pod install]

# Run
[yarn ios / yarn android / flutter run / xcodebuild / ./gradlew]

# Test
[yarn test / flutter test / xcodebuild test]

# Lint
[yarn lint / flutter analyze / swiftlint]
```

## Notes

[FILL IN: any project-specific quirks, known issues, or important context]

Example:
- Auth uses custom JWT refresh logic in src/services/auth/tokenManager.ts
- Push notifications require manual certificate setup (see docs/push-setup.md)
- Android flavor: 'staging' points to staging API, 'production' to prod
