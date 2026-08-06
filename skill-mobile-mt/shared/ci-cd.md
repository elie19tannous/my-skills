# CI/CD Pipelines — GitHub Actions for Mobile

> Automate: test → build → distribute. Never ship without CI.

---

## React Native — CI Pipeline

```yaml
# .github/workflows/rn-ci.yml
name: React Native CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'yarn'           # or npm, pnpm

      - name: Install dependencies
        run: yarn install --frozen-lockfile

      - name: TypeScript check
        run: yarn tsc --noEmit

      - name: Lint
        run: yarn lint

      - name: Unit tests
        run: yarn test --ci --coverage --maxWorkers=2

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          token: ${{ secrets.CODECOV_TOKEN }}

  build-android:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'yarn'

      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'

      - name: Cache Gradle
        uses: actions/cache@v4
        with:
          path: |
            ~/.gradle/caches
            ~/.gradle/wrapper
          key: ${{ runner.os }}-gradle-${{ hashFiles('**/*.gradle*') }}

      - name: Install dependencies
        run: yarn install --frozen-lockfile

      - name: Build Android APK (debug)
        run: cd android && ./gradlew assembleDebug

      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: app-debug.apk
          path: android/app/build/outputs/apk/debug/app-debug.apk

  build-ios:
    runs-on: macos-15
    needs: test
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'yarn'

      - name: Cache CocoaPods
        uses: actions/cache@v4
        with:
          path: ios/Pods
          key: ${{ runner.os }}-pods-${{ hashFiles('ios/Podfile.lock') }}

      - name: Install dependencies
        run: yarn install --frozen-lockfile && cd ios && pod install

      - name: Build iOS (simulator)
        run: |
          xcodebuild -workspace ios/MyApp.xcworkspace \
            -scheme MyApp \
            -sdk iphonesimulator \
            -configuration Debug \
            -derivedDataPath ios/build \
            CODE_SIGN_IDENTITY="" CODE_SIGNING_REQUIRED=NO
```

---

## React Native — E2E with Detox

```yaml
# .github/workflows/rn-e2e.yml
name: E2E Tests (Detox)

on:
  push:
    branches: [main]

jobs:
  e2e-ios:
    runs-on: macos-15
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'yarn'

      - name: Install dependencies
        run: yarn install --frozen-lockfile && cd ios && pod install

      - name: Install Detox CLI
        run: npm install -g detox-cli

      - name: Build for Detox
        run: detox build --configuration ios.sim.debug

      - name: Run E2E tests
        run: detox test --configuration ios.sim.debug --headless

      - name: Upload Detox artifacts on failure
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: detox-artifacts
          path: artifacts/
```

---

## Flutter — CI Pipeline

```yaml
# .github/workflows/flutter-ci.yml
name: Flutter CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.27.x'
          cache: true

      - name: Install dependencies
        run: flutter pub get

      - name: Analyze
        run: flutter analyze

      - name: Unit + Widget tests
        run: flutter test --coverage

      - name: Upload coverage
        uses: codecov/codecov-action@v4

  build-android:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'

      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.27.x'
          cache: true

      - name: Install dependencies
        run: flutter pub get

      - name: Build APK
        run: flutter build apk --debug

      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: flutter-debug.apk
          path: build/app/outputs/flutter-apk/app-debug.apk

  build-ios:
    runs-on: macos-15
    needs: test
    steps:
      - uses: actions/checkout@v4

      - uses: subosito/flutter-action@v2
        with:
          flutter-version: '3.27.x'
          cache: true

      - name: Install dependencies
        run: flutter pub get

      - name: Build iOS (no codesign)
        run: flutter build ios --debug --no-codesign
```

---

## iOS — Release to TestFlight (Fastlane)

```yaml
# .github/workflows/ios-release.yml
name: iOS Release

on:
  push:
    tags: ['v*']

jobs:
  release:
    runs-on: macos-15
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'yarn'

      - name: Install dependencies
        run: yarn install --frozen-lockfile && cd ios && pod install

      - name: Setup certificates
        uses: apple-actions/import-codesign-certs@v2
        with:
          p12-file-base64: ${{ secrets.CERTIFICATES_P12 }}
          p12-password: ${{ secrets.CERTIFICATES_P12_PASSWORD }}

      - name: Setup provisioning profile
        uses: apple-actions/download-provisioning-profiles@v1
        with:
          bundle-id: com.myapp
          issuer-id: ${{ secrets.APPSTORE_ISSUER_ID }}
          api-key-id: ${{ secrets.APPSTORE_KEY_ID }}
          api-private-key: ${{ secrets.APPSTORE_PRIVATE_KEY }}

      - name: Deploy to TestFlight
        run: bundle exec fastlane ios beta
        env:
          APP_STORE_CONNECT_API_KEY_KEY_ID: ${{ secrets.APPSTORE_KEY_ID }}
          APP_STORE_CONNECT_API_KEY_ISSUER_ID: ${{ secrets.APPSTORE_ISSUER_ID }}
          APP_STORE_CONNECT_API_KEY_KEY: ${{ secrets.APPSTORE_PRIVATE_KEY }}
```

```ruby
# ios/Fastfile
lane :beta do
  build_app(
    workspace: "MyApp.xcworkspace",
    scheme: "MyApp",
    configuration: "Release",
    export_method: "app-store"
  )
  upload_to_testflight(skip_waiting_for_build_processing: true)
end
```

---

## Android — Release to Play Store (Fastlane)

```yaml
# .github/workflows/android-release.yml
name: Android Release

on:
  push:
    tags: ['v*']

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'

      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'yarn'

      - name: Install dependencies
        run: yarn install --frozen-lockfile

      - name: Decode keystore
        run: echo "${{ secrets.KEYSTORE_BASE64 }}" | base64 -d > android/app/release.keystore

      - name: Build release AAB
        run: cd android && ./gradlew bundleRelease
        env:
          KEYSTORE_PASSWORD: ${{ secrets.KEYSTORE_PASSWORD }}
          KEY_ALIAS: ${{ secrets.KEY_ALIAS }}
          KEY_PASSWORD: ${{ secrets.KEY_PASSWORD }}

      - name: Deploy to Play Store
        uses: r0adkll/upload-google-play@v1
        with:
          serviceAccountJsonPlainText: ${{ secrets.PLAY_STORE_SERVICE_ACCOUNT_JSON }}
          packageName: com.myapp
          releaseFiles: android/app/build/outputs/bundle/release/*.aab
          track: internal
```

---

## Required GitHub Secrets

```
# iOS
CERTIFICATES_P12             ← base64-encoded .p12 file
CERTIFICATES_P12_PASSWORD    ← password for .p12
APPSTORE_KEY_ID              ← App Store Connect API key ID
APPSTORE_ISSUER_ID           ← App Store Connect issuer ID
APPSTORE_PRIVATE_KEY         ← App Store Connect private key (.p8 contents)

# Android
KEYSTORE_BASE64              ← base64-encoded release.keystore
KEYSTORE_PASSWORD            ← keystore password
KEY_ALIAS                    ← key alias
KEY_PASSWORD                 ← key password
PLAY_STORE_SERVICE_ACCOUNT_JSON  ← GCP service account JSON

# Shared
CODECOV_TOKEN                ← coverage reporting
MAESTRO_API_KEY              ← Maestro Cloud E2E (optional)
```

---

## Caching Strategy

```yaml
# Node modules — hash package-lock or yarn.lock
- uses: actions/cache@v4
  with:
    path: node_modules
    key: ${{ runner.os }}-node-${{ hashFiles('**/yarn.lock') }}
    restore-keys: ${{ runner.os }}-node-

# Gradle — hash .gradle files
- uses: actions/cache@v4
  with:
    path: |
      ~/.gradle/caches
      ~/.gradle/wrapper
    key: ${{ runner.os }}-gradle-${{ hashFiles('**/*.gradle*', '**/gradle-wrapper.properties') }}

# CocoaPods — hash Podfile.lock
- uses: actions/cache@v4
  with:
    path: ios/Pods
    key: ${{ runner.os }}-pods-${{ hashFiles('ios/Podfile.lock') }}

# Flutter pub — hash pubspec.lock
- uses: actions/cache@v4
  with:
    path: ~/.pub-cache
    key: ${{ runner.os }}-pub-${{ hashFiles('**/pubspec.lock') }}
```

---

## Anti-Patterns

```
❌ Committing signing credentials to repo
❌ Running E2E on every PR (too slow — run on main only)
❌ No caching (3x slower builds)
❌ Skipping unit tests before build jobs
❌ Building on push to every branch

✅ Store all secrets in GitHub Secrets
✅ Cache node_modules + Gradle + CocoaPods + pub-cache
✅ Unit tests on PR, E2E on merge to main
✅ needs: test before build jobs
✅ Upload build artifacts for download/QA
```
