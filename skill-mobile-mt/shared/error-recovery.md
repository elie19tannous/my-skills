# Error Recovery — Fix Common Build/Runtime Errors

> Quick reference for fixing errors AI agents encounter during mobile development.

---

## Build Errors

### 1. Duplicate class found

**Symptom:**
```
Duplicate class X found in modules Y and Z
```

**Cause:** Multiple versions of the same library in dependency tree

**Fix:**
```bash
# Find conflict
./gradlew app:dependencies | grep "library-name"

# Force version in android/app/build.gradle
android {
    configurations.all {
        resolutionStrategy {
            force 'com.library:name:1.2.3'
        }
    }
}
```

---

### 2. Metro bundler failed: Module not found

**Symptom:**
```
Error: Unable to resolve module X from Y
```

**Cause:** Import path wrong OR package not installed OR cache stale

**Fix:**
```bash
# 1. Check import path is correct
# 2. Install missing package
yarn add package-name

# 3. Clear cache and restart
rm -rf node_modules
yarn install
yarn start --reset-cache
```

---

### 3. Pod install failed

**Symptom:**
```
[!] CDN: trunk URL couldn't be downloaded
```

**Cause:** CocoaPods CDN slow/blocked OR network issue

**Fix:**
```bash
# Option 1: Use GitHub source
cd ios
rm Podfile.lock
pod cache clean --all
pod install --repo-update

# Option 2: Add to Podfile (top)
source 'https://github.com/CocoaPods/Specs.git'

# Option 3: Deintegrate and reinstall
pod deintegrate
pod install
```

---

### 4. Gradle sync failed: Could not resolve

**Symptom:**
```
Could not resolve com.library:name:1.2.3
```

**Cause:** Maven repo unreachable OR wrong credentials OR version doesn't exist

**Fix:**
```gradle
// android/build.gradle — add backup repos
allprojects {
    repositories {
        google()
        mavenCentral()
        maven { url 'https://jitpack.io' }  // Backup
        maven { url 'https://maven.google.com' }  // Backup
    }
}
```

---

### 5. Xcode build failed: Command PhaseScriptExecution failed

**Symptom:**
```
Command PhaseScriptExecution failed with a nonzero exit code
```

**Cause:** Build script error OR missing file OR wrong Xcode version

**Fix:**
```bash
# 1. Clean build folder
cd ios
rm -rf build
xcodebuild clean

# 2. Reinstall pods
rm -rf Pods Podfile.lock
pod install

# 3. Check Xcode version matches project requirement
xcodebuild -version

# 4. Check script in Xcode → Build Phases → Run Script
```

---

### 6. Android build failed: Invoke-customs are only supported starting with Android O

**Symptom:**
```
Invoke-customs are only supported starting with Android O (--min-api 26)
```

**Cause:** Using Java 8+ features but minSdkVersion < 26

**Fix:**
```gradle
// android/app/build.gradle
android {
    defaultConfig {
        minSdkVersion 21  // Keep if targeting older devices
    }

    compileOptions {
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }

    // Enable desugaring for older Android versions
    compileOptions {
        coreLibraryDesugaringEnabled true
    }
}

dependencies {
    coreLibraryDesugaring 'com.android.tools:desugar_jdk_libs:1.1.5'
}
```

---

## Runtime Errors

### 7. App crashes on launch (no error message)

**Debug steps:**
```bash
# iOS: Check Xcode console
# Android: Check Logcat
adb logcat | grep -i "crash\|exception\|error"

# Common causes:
✅ Missing native module (forgot pod install / gradle sync)
✅ Broken import (typo in file path)
✅ Missing entry point (index.js not registered)
✅ Version mismatch (RN CLI vs RN runtime)
```

**Fix:**
1. Check native logs first (always)
2. Verify `pod install` and `./gradlew clean` were run
3. Check `AppRegistry.registerComponent` matches app name

---

### 8. White screen / blank screen

**Symptom:** App launches but shows blank white screen

**Cause:** Error caught by error boundary OR navigator not setup OR Metro bundler not running

**Debug:**
```bash
# 1. Check Metro is running
yarn start

# 2. Check console for errors (cmd+D / cmd+M → Debug)

# 3. Add error boundary
class ErrorBoundary extends React.Component {
  componentDidCatch(error, errorInfo) {
    console.log('Caught error:', error, errorInfo);
  }
  render() {
    return this.props.children;
  }
}
```

**Fix:**
- Check navigator has screens registered
- Check no circular imports
- Check entry component is exported correctly

---

### 9. API requests not working

**Symptom:** Network calls fail silently OR return 0 / undefined

**Debug:**
```bash
# Check network logs
npx react-devtools
# OR
# Install Flipper + Network plugin

# Common causes:
✅ Interceptor blocking request (check auth token attached)
✅ CORS issue (web only, not mobile)
✅ SSL pinning blocking localhost (disable in dev)
✅ Wrong base URL (check environment variable)
```

**Fix:**
```typescript
// Check interceptor logs
api.interceptors.request.use((config) => {
  console.log('Request:', config.url, config.headers);
  return config;
});

api.interceptors.response.use(
  (res) => {
    console.log('Response:', res.status, res.data);
    return res;
  },
  (error) => {
    console.log('Error:', error.response?.status, error.message);
    return Promise.reject(error);
  }
);
```

---

### 10. Images not showing

**Symptom:** `<Image source={require('./image.png')} />` shows nothing

**Cause:** Wrong path OR image not in bundle OR cache issue

**Fix:**
```typescript
// ❌ Wrong
<Image source={require('../../assets/image.png')} />

// ✅ Correct — use absolute path with babel-plugin-module-resolver
<Image source={require('@assets/image.png')} />

// OR use static method to check
Image.resolveAssetSource(require('./image.png'))
  .then(resolved => console.log(resolved))

// Clear cache
yarn start --reset-cache
```

---

### 11. Hermes crashes: Cannot read property 'X' of undefined

**Symptom:** Works on dev, crashes on release build with Hermes

**Cause:** Hermes strictness OR Proxy not supported OR polyfill missing

**Fix:**
```javascript
// Check Hermes is enabled
// android/app/build.gradle
project.ext.react = [
    enableHermes: true  // Make sure this is true
]

// Add polyfills for missing features
// index.js (top)
import 'react-native-get-random-values';  // For uuid
import 'react-native-url-polyfill/auto';  // For URL API

// Avoid Proxy (not supported)
❌ const proxy = new Proxy(obj, handler);
✅ Use plain objects instead
```

---

### 12. Navigation not working after upgrade

**Symptom:** Screen transitions broken OR `navigation.navigate` does nothing

**Cause:** Breaking changes in @react-navigation upgrade

**Fix:**
```typescript
// Check version compatibility
// React Navigation v6 requires:
"@react-navigation/native": "^6.x.x"
"react-native-screens": "^3.x.x"
"react-native-safe-area-context": "^4.x.x"

// Wrap root in NavigationContainer (only once)
<NavigationContainer>
  <RootNavigator />
</NavigationContainer>

// Check screen names match exactly
navigation.navigate('ProductDetail', { id: 123 });
// vs
<Stack.Screen name="ProductDetail" component={...} />
```

---

### 13. Android release build works, debug doesn't (or vice versa)

**Symptom:** App works in one mode but not the other

**Cause:** ProGuard stripping code OR different signing configs OR debug-only dependencies

**Fix:**
```gradle
// android/app/proguard-rules.pro
-keep class com.yourpackage.** { *; }
-keep class * extends com.facebook.react.bridge.ReactContextBaseJavaModule { *; }

// Check signing configs
android {
    buildTypes {
        debug {
            signingConfig signingConfigs.debug
        }
        release {
            signingConfig signingConfigs.release
            minifyEnabled true
        }
    }
}
```

---

## Flutter Specific

### 14. Flutter build failed: Gradle task assembleDebug failed with exit code 1

**Fix:**
```bash
# Clean and rebuild
flutter clean
flutter pub get
cd android && ./gradlew clean
cd .. && flutter build apk
```

### 15. Flutter: setState() called after dispose()

**Cause:** Async operation finished after widget unmounted

**Fix:**
```dart
// Add mounted check
if (!mounted) return;
setState(() { ... });

// OR cancel subscription in dispose
StreamSubscription? _sub;

@override
void dispose() {
  _sub?.cancel();
  super.dispose();
}
```

---

## iOS Specific

### 16. iOS: App rejected for missing privacy manifest

**Symptom:** App rejected during review — "Missing privacy manifest"

**Fix:**
```
Add PrivacyInfo.xcprivacy to Xcode project:
1. Right-click on project → New File → App Privacy File
2. Add required disclosures for tracking/data usage
3. Rebuild and resubmit
```

---

## Quick Reference

| Error | First Thing to Check |
|-------|---------------------|
| Build fails | Clean + reinstall deps (pod install / ./gradlew clean) |
| App crashes | Native logs (Xcode console / adb logcat) |
| White screen | Metro bundler running? Error boundary logs? |
| API fails | Network logs (Flipper / DevTools) + interceptor logs |
| Images missing | Correct path? Cache cleared? |
| Navigation broken | Screen names match? NavigationContainer wraps root? |

---

## General Recovery Protocol

```
1. READ ERROR MESSAGE FULLY
   Don't skim — error message has the answer 80% of the time

2. CHECK RECENT CHANGES
   What did you modify? Undo and test.

3. CLEAR CACHES
   yarn start --reset-cache
   rm -rf node_modules && yarn
   cd ios && pod deintegrate && pod install
   cd android && ./gradlew clean

4. CHECK NATIVE LOGS
   iOS: Xcode console
   Android: adb logcat

5. ISOLATE THE ISSUE
   Comment out code until it works, then narrow down

6. GOOGLE THE EXACT ERROR
   Copy full error message + framework name

7. ASK FOR HELP
   Provide: error message + platform + version + what you tried
```

---

> When in doubt: clean everything, reinstall everything, restart everything.
