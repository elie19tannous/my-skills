# Version Management — SDK Compatibility First

> Treat SDK version as a first-class constraint, not an afterthought.

## Philosophy

**Traditional approach:** Install package → hope it works with current SDK
**This approach:** Check SDK compatibility BEFORE suggesting any package

---

## ⚠️ IMPORTANT: Always WebSearch for Latest

**The version matrix below is a SNAPSHOT and may be outdated.**
**Before installing ANY package or suggesting ANY version:**

```
1. WebSearch "[package] latest version [current year]"
2. WebSearch "[package] [framework version] compatibility"
3. Read the OFFICIAL changelog/migration guide
4. Cross-reference with the matrix below

⛔ NEVER rely solely on the matrix below — it was written at a point in time
✅ ALWAYS verify with WebSearch for the most current information
```

---

## Version Matrix (React Native / Expo)

### Expo SDK Compatibility

```
Expo SDK 52 (latest - Jan 2025)
├── React Native: 0.76.x
├── React: 18.3.x
├── Node: >= 18.0.0
├── TypeScript: >= 5.3.0
└── Metro: 0.80.x

Expo SDK 51
├── React Native: 0.74.x
├── React: 18.2.x
├── Node: >= 18.0.0
├── TypeScript: >= 5.3.0
└── Metro: 0.80.x

Expo SDK 50
├── React Native: 0.73.x
├── React: 18.2.x
├── Node: >= 18.0.0
├── TypeScript: >= 5.1.0
└── Metro: 0.76.x
```

### React Native CLI Compatibility

```
React Native 0.76.x (latest)
├── React: 18.3.x
├── Node: >= 18.0.0
├── TypeScript: >= 5.0.0
├── Metro: 0.80.x
├── Hermes: Latest
├── iOS: >= 13.4
└── Android: >= 6.0 (API 23)

React Native 0.74.x
├── React: 18.2.x
├── Node: >= 18.0.0
├── TypeScript: >= 5.0.0
├── Metro: 0.80.x
├── iOS: >= 13.4
└── Android: >= 6.0 (API 23)

React Native 0.73.x
├── React: 18.2.x
├── Node: >= 18.0.0
├── TypeScript: >= 5.0.0
├── Metro: 0.76.x
├── iOS: >= 13.4
└── Android: >= 6.0 (API 23)
```

---

## Flutter SDK Compatibility

```
Flutter 3.27.x (latest - Jan 2025)
├── Dart: >= 3.6.0
├── iOS: >= 12.0
├── Android: >= 21 (API 21)
├── Material: 3.x
└── Cupertino: Latest

Flutter 3.24.x
├── Dart: >= 3.5.0
├── iOS: >= 12.0
├── Android: >= 21 (API 21)
├── Material: 3.x
└── Cupertino: Latest

Flutter 3.22.x
├── Dart: >= 3.4.0
├── iOS: >= 11.0
├── Android: >= 21 (API 21)
├── Material: 3.x
└── Cupertino: Latest
```

---

## iOS Native Compatibility

```
iOS 18+ (latest - 2024)
├── Xcode: 16.0+
├── Swift: 6.0+
├── Deployment Target: iOS 13.0+ (recommended)
└── CocoaPods: 1.15.x

iOS 17
├── Xcode: 15.0+
├── Swift: 5.9+
├── Deployment Target: iOS 12.0+
└── CocoaPods: 1.14.x

iOS 16
├── Xcode: 14.0+
├── Swift: 5.7+
├── Deployment Target: iOS 11.0+
└── CocoaPods: 1.12.x
```

---

## Android Native Compatibility

```
Android 15+ (API 35, latest - 2024)
├── Android Studio: Ladybug (2024.2.1)+
├── Gradle: 8.7+
├── Kotlin: 2.0.x
├── AGP (Android Gradle Plugin): 8.7.x
├── Compose: 1.7.x
└── Min SDK: 24 (Android 7.0) recommended

Android 14 (API 34)
├── Android Studio: Hedgehog (2023.1.1)+
├── Gradle: 8.4+
├── Kotlin: 1.9.x
├── AGP: 8.2.x
├── Compose: 1.5.x
└── Min SDK: 23 (Android 6.0)

Android 13 (API 33)
├── Android Studio: Flamingo (2022.2.1)+
├── Gradle: 8.0+
├── Kotlin: 1.8.x
├── AGP: 8.0.x
├── Compose: 1.4.x
└── Min SDK: 21 (Android 5.0)
```

---

## Package Compatibility Protocol

### BEFORE suggesting ANY package:

```
STEP 1: DETECT CURRENT SDK
  React Native:
    - Read package.json → react-native version
    - Check expo.sdkVersion (if Expo)

  Flutter:
    - Read pubspec.yaml → environment.flutter

  iOS Native:
    - Read Podfile → platform :ios, 'X.X'
    - Read *.xcodeproj/project.pbxproj → IPHONEOS_DEPLOYMENT_TARGET

  Android Native:
    - Read app/build.gradle → compileSdkVersion, minSdkVersion

STEP 2: CHECK PACKAGE COMPATIBILITY
  - Search package docs for version compatibility
  - Check GitHub releases for SDK support
  - Look for "Supported Versions" in README
  - Verify peer dependencies

STEP 3: SUGGEST COMPATIBLE VERSION
  ✅ "react-native-reanimated": "^3.6.0" (works with RN 0.73+)
  ❌ "react-native-reanimated": "^3.0.0" (requires RN 0.71+, you have 0.70)

  If incompatible:
    Option 1: Suggest upgrade SDK first
    Option 2: Suggest older compatible package version
    Option 3: Suggest alternative package

STEP 4: WARN ABOUT BREAKING CHANGES
  - Major version changes (3.x → 4.x) = breaking changes
  - SDK upgrades may require migration
  - Link to migration guide if available
```

---

## Common Package Compatibility

### React Native

| Package | RN 0.76 | RN 0.74 | RN 0.73 | Notes |
|---------|---------|---------|---------|-------|
| **react-navigation** | 7.x | 7.x | 6.x | v7 requires RN 0.74+ |
| **react-native-reanimated** | 3.16+ | 3.10+ | 3.6+ | Always use latest for SDK |
| **react-native-gesture-handler** | 2.20+ | 2.18+ | 2.14+ | Match with Reanimated |
| **react-native-safe-area-context** | 4.12+ | 4.10+ | 4.8+ | Used by React Navigation |
| **react-native-screens** | 4.0+ | 3.34+ | 3.31+ | Used by React Navigation |
| **@react-native-async-storage** | 2.0+ | 1.24+ | 1.23+ | Separate from RN core |
| **react-native-mmkv** | 3.x | 3.x | 2.x | Faster than AsyncStorage |
| **@shopify/flash-list** | 1.7+ | 1.6+ | 1.6+ | Drop-in FlatList replacement |
| **axios** | 1.7.x | 1.6.x | 1.6.x | Independent of RN version |
| **zustand** | 5.x | 4.x | 4.x | Independent of RN version |
| **@tanstack/react-query** | 5.x | 5.x | 4.x | Check React version |

### Expo

| Package | Expo 52 | Expo 51 | Expo 50 | Notes |
|---------|---------|---------|---------|-------|
| **expo-router** | 4.x | 4.x | 3.x | File-based routing |
| **expo-image** | ~2.0.0 | ~1.12.0 | ~1.10.0 | Fast image component |
| **expo-camera** | ~16.0.0 | ~15.0.0 | ~14.0.0 | Camera access |
| **expo-location** | ~18.0.0 | ~17.0.0 | ~16.0.0 | GPS/location |
| **expo-notifications** | ~0.29.0 | ~0.28.0 | ~0.27.0 | Push notifications |
| **expo-secure-store** | ~14.0.0 | ~13.0.0 | ~12.0.0 | Secure storage |
| **expo-linear-gradient** | ~14.0.0 | ~13.0.0 | ~12.0.0 | Gradient backgrounds |

### Flutter

| Package | Flutter 3.27 | Flutter 3.24 | Flutter 3.22 | Notes |
|---------|--------------|--------------|--------------|-------|
| **riverpod** | 3.x | 3.x | 2.x | State management |
| **flutter_riverpod** | 3.x | 3.x | 2.x | Match with riverpod |
| **go_router** | 15.x | 14.x | 13.x | Declarative routing |
| **dio** | 5.x | 5.x | 5.x | HTTP client |
| **flutter_bloc** | 9.x | 9.x | 8.x | BLoC pattern |
| **hive** | 2.x | 2.x | 2.x | Local database |
| **sqflite** | 2.x | 2.x | 2.x | SQLite for Flutter |
| **shared_preferences** | 2.x | 2.x | 2.x | Simple key-value |
| **flutter_secure_storage** | 9.x | 9.x | 8.x | Secure storage |
| **cached_network_image** | 3.x | 3.x | 3.x | Image caching |

---

## Migration Guides

### React Native Major Upgrades

```
0.73 → 0.74:
- New Architecture enabled by default
- Update Gradle to 8.3+
- Update CMake if using C++ modules
- Review breaking changes: https://react-native-community.github.io/upgrade-helper/

0.74 → 0.76:
- React 18.3 required
- Update Metro config
- Check deprecated APIs
- Test with Hermes engine

Expo SDK 50 → 51:
- Run: npx expo install --fix
- Update app.json with new config
- Check deprecated expo-* packages
- Test deep linking configuration

Expo SDK 51 → 52:
- React Native 0.76 included
- Update expo-router if used
- Check for breaking changes in expo-* packages
```

### Flutter Major Upgrades

```
3.22 → 3.24:
- Dart 3.5 required
- Update Material widgets to Material 3
- Check for deprecated APIs
- Run: flutter pub upgrade --major-versions

3.24 → 3.27:
- Dart 3.6 required
- New widget deprecations
- Performance improvements
- Run: flutter pub upgrade --major-versions
```

---

## Pre-Installation Checklist

Before suggesting `npm install` / `yarn add` / `flutter pub add`:

```
□ Current SDK version detected
□ Package compatibility verified
□ Peer dependencies checked
□ Breaking changes reviewed
□ Migration guide (if needed) linked
□ Alternative options considered
```

---

## Version Lock Strategy

### React Native / Expo

```json
// package.json
{
  "dependencies": {
    "react-native-reanimated": "~3.6.0",  // ~ allows patch (3.6.x)
    "react-navigation": "^6.0.0",         // ^ allows minor (6.x.x)
    "axios": "1.6.2"                      // exact version
  }
}

RULES:
- Core RN libraries: Use ~ (patch updates only)
- Navigation/UI: Use ^ (minor updates OK)
- Data/API: Use exact version (full control)
```

### Flutter

```yaml
# pubspec.yaml
dependencies:
  flutter_riverpod: ^3.0.0   # ^ allows compatible updates
  dio: 5.4.0                  # exact version
  go_router: '>=13.0.0 <14.0.0'  # range constraint

RULES:
- State management: Use ^ (minor updates OK)
- HTTP/API: Use exact version
- Routing: Use range (controlled updates)
```

---

## Dependency Conflict Resolution

### React Native

```bash
# Check for conflicts
npm ls <package-name>
yarn why <package-name>

# Common conflict: react-native-reanimated + react-native
Error: react-native-reanimated@3.6.0 requires react-native@>=0.72

Fix:
1. Upgrade react-native to 0.72+
2. OR downgrade react-native-reanimated to 3.5.x
3. Check compatibility matrix above
```

### Flutter

```bash
# Check for conflicts
flutter pub deps

# Common conflict: riverpod + flutter_riverpod versions mismatch
Error: riverpod ^3.0.0 depends on flutter_riverpod ^3.0.0

Fix:
1. Ensure versions match:
   riverpod: ^3.0.0
   flutter_riverpod: ^3.0.0
```

---

## Release Mode Testing

**CRITICAL:** Always test in release mode before submitting to stores.

### React Native

```bash
# iOS Release
cd ios && pod install && cd ..
npx react-native run-ios --configuration Release

# Android Release
npx react-native run-android --variant=release

COMMON RELEASE-ONLY ISSUES:
- Hermes bytecode compilation errors
- Minification breaks code
- Missing native modules
- Performance regressions
```

### Expo

```bash
# EAS Build (production-like)
eas build --profile preview --platform ios
eas build --profile preview --platform android

# Local release build
npx expo run:ios --configuration Release
npx expo run:android --variant release
```

### Flutter

```bash
# iOS Release
flutter build ios --release
flutter run --release

# Android Release
flutter build apk --release
flutter build appbundle --release

COMMON RELEASE-ONLY ISSUES:
- Code obfuscation breaks reflection
- Missing native permissions
- Assets not bundled correctly
```

---

## Version Documentation

Always document SDK requirements in README:

```markdown
## Requirements

- **React Native:** 0.74.x
- **Expo SDK:** 51 (if using Expo)
- **Node:** >= 18.0.0
- **iOS:** >= 13.0
- **Android:** >= API 23 (Android 6.0)
- **Xcode:** 15.0+ (for iOS development)
- **Android Studio:** Hedgehog (2023.1.1)+ (for Android development)

## Dependency Versions

Key dependencies are locked to compatible versions. Do not upgrade without testing:

- `react-native-reanimated`: ~3.6.0
- `@react-navigation/native`: ^6.0.0
- `react-native-mmkv`: ^2.12.0

See `package.json` for full list.
```

---

## Auto-Detection Script

Add to project for teammates:

```javascript
// scripts/check-versions.js
const { execSync } = require('child_process');
const pkg = require('../package.json');

const RN_VERSION = pkg.dependencies['react-native'];
const NODE_VERSION = process.version;
const REQUIRED_NODE = '18.0.0';

console.log('📦 Version Check');
console.log(`React Native: ${RN_VERSION}`);
console.log(`Node: ${NODE_VERSION} (required: >=${REQUIRED_NODE})`);

// Check Node version
if (parseInt(NODE_VERSION.slice(1)) < parseInt(REQUIRED_NODE)) {
  console.error(`❌ Node version too old. Please upgrade to ${REQUIRED_NODE}+`);
  process.exit(1);
}

// Check iOS deployment target
try {
  const podfile = require('fs').readFileSync('ios/Podfile', 'utf8');
  const match = podfile.match(/platform :ios, '(\d+\.\d+)'/);
  if (match) {
    console.log(`iOS Deployment Target: ${match[1]}`);
  }
} catch {}

console.log('✅ All version checks passed');
```

Run before every install:
```json
{
  "scripts": {
    "preinstall": "node scripts/check-versions.js"
  }
}
```

---

## Summary

**Core Principle:** SDK version is the foundation. Everything else must align with it.

**Workflow:**
1. Detect SDK version FIRST
2. Check package compatibility SECOND
3. Suggest installation THIRD
4. Test in release mode BEFORE production
