# Mobile i18n & Localization

> Multi-language support for React Native, Flutter, iOS, Android.
> Covers: setup, translation management, RTL, date/number formatting, dynamic locale switching.

---

## Decision Matrix — Pick Your Stack

```
PLATFORM        → RECOMMENDED LIBRARY
──────────────────────────────────────────────────────────────────
React Native    → i18next + react-i18next (most popular, flexible)
                  OR expo-localization + custom (Expo projects)

Flutter         → slang (type-safe, code generation) ← recommended
                  OR flutter_localizations + .arb files (official)
                  OR easy_localization (simple)

iOS Native      → .xcstrings / Localizable.strings (built-in Xcode)
Android Native  → strings.xml per locale (built-in Android Studio)
```

---

## React Native — i18next

### Setup

```bash
npm install i18next react-i18next
npm install @react-native-async-storage/async-storage  # for locale persistence
# or with expo:
npx expo install expo-localization
```

### File Structure

```
src/
├── i18n/
│   ├── index.ts              ← i18next init
│   ├── en.json               ← English (base language)
│   ├── vi.json               ← Vietnamese
│   ├── ja.json               ← Japanese
│   ├── ar.json               ← Arabic (RTL)
│   └── types.ts              ← TypeScript type for translation keys
```

### Translation Files

```json
// i18n/en.json
{
  "common": {
    "ok": "OK",
    "cancel": "Cancel",
    "loading": "Loading...",
    "error": "Something went wrong",
    "retry": "Try again",
    "empty": "No results found"
  },
  "auth": {
    "login": "Login",
    "logout": "Logout",
    "email": "Email address",
    "password": "Password",
    "forgotPassword": "Forgot password?",
    "errors": {
      "invalidEmail": "Please enter a valid email",
      "wrongPassword": "Incorrect password"
    }
  },
  "profile": {
    "title": "My Profile",
    "greeting": "Hello, {{name}}!",
    "itemCount": "{{count}} item",
    "itemCount_other": "{{count}} items"
  }
}
```

```json
// i18n/vi.json
{
  "common": {
    "ok": "Đồng ý",
    "cancel": "Hủy",
    "loading": "Đang tải...",
    "error": "Có lỗi xảy ra",
    "retry": "Thử lại",
    "empty": "Không có kết quả"
  },
  "auth": {
    "login": "Đăng nhập",
    "logout": "Đăng xuất",
    "email": "Địa chỉ email",
    "password": "Mật khẩu",
    "forgotPassword": "Quên mật khẩu?",
    "errors": {
      "invalidEmail": "Vui lòng nhập email hợp lệ",
      "wrongPassword": "Mật khẩu không đúng"
    }
  },
  "profile": {
    "title": "Hồ sơ của tôi",
    "greeting": "Xin chào, {{name}}!",
    "itemCount": "{{count}} mục"
  }
}
```

### i18next Init

```typescript
// i18n/index.ts
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import * as Localization from 'expo-localization';
import MMKV from '../storage'; // your MMKV wrapper

import en from './en.json';
import vi from './vi.json';
import ar from './ar.json';

const LANGUAGE_KEY = 'user_language';

export const SUPPORTED_LANGUAGES = ['en', 'vi', 'ja', 'ar'] as const;
export type Language = typeof SUPPORTED_LANGUAGES[number];

// Get saved or device language
const savedLang = MMKV.getString(LANGUAGE_KEY);
const deviceLang = Localization.getLocales()[0]?.languageCode ?? 'en';
const initialLang = savedLang ?? (SUPPORTED_LANGUAGES.includes(deviceLang as Language) ? deviceLang : 'en');

i18n.use(initReactI18next).init({
  resources: { en: { translation: en }, vi: { translation: vi }, ar: { translation: ar } },
  lng: initialLang,
  fallbackLng: 'en',
  interpolation: { escapeValue: false },
});

export function changeLanguage(lang: Language) {
  i18n.changeLanguage(lang);
  MMKV.setString(LANGUAGE_KEY, lang);  // persist choice
}

export default i18n;
```

### Usage in Components

```typescript
import { useTranslation } from 'react-i18next';
import { I18nManager } from 'react-native';

export function ProfileScreen() {
  const { t, i18n } = useTranslation();
  const isRTL = I18nManager.isRTL;

  return (
    <View style={[styles.container, isRTL && styles.rtl]}>
      <Text>{t('profile.title')}</Text>
      <Text>{t('profile.greeting', { name: 'Phi' })}</Text>
      <Text>{t('profile.itemCount', { count: 5 })}</Text>

      {/* Language switcher */}
      <Button title="Tiếng Việt" onPress={() => changeLanguage('vi')} />
      <Button title="English" onPress={() => changeLanguage('en')} />
    </View>
  );
}

// TypeScript type-safe keys (optional but recommended)
// Generate from en.json with i18next-resources-for-ts
```

### RTL Support (Arabic, Hebrew)

```typescript
// App.tsx — apply RTL on init
import { I18nManager } from 'react-native';
import * as Updates from 'expo-updates';

function applyRTL(language: string) {
  const isRTL = language === 'ar' || language === 'he';

  if (I18nManager.isRTL !== isRTL) {
    I18nManager.allowRTL(isRTL);
    I18nManager.forceRTL(isRTL);
    // Requires reload to take effect
    Updates.reloadAsync(); // Expo
    // RNRestart.Restart(); // react-native-restart (bare RN)
  }
}

// RTL-aware styles
const styles = StyleSheet.create({
  row: {
    flexDirection: I18nManager.isRTL ? 'row-reverse' : 'row',
  },
  text: {
    textAlign: I18nManager.isRTL ? 'right' : 'left',
    writingDirection: I18nManager.isRTL ? 'rtl' : 'ltr',
  },
});
```

### Date / Number Formatting

```typescript
// Use Intl API (built into Hermes/V8)
const locale = i18n.language;

// Date
const formatDate = (date: Date) =>
  new Intl.DateTimeFormat(locale, { dateStyle: 'medium', timeStyle: 'short' }).format(date);

// Number / Currency
const formatCurrency = (amount: number, currency = 'USD') =>
  new Intl.NumberFormat(locale, { style: 'currency', currency }).format(amount);

// Relative time (2 days ago, in 3 hours)
const formatRelative = (date: Date) =>
  new Intl.RelativeTimeFormat(locale, { numeric: 'auto' }).format(
    Math.round((date.getTime() - Date.now()) / 86400000), 'day'
  );

// Usage
formatDate(new Date());        // "Jan 15, 2025, 2:30 PM"
formatCurrency(99.99);         // "$99.99" / "99,99 €"
formatRelative(yesterday);     // "yesterday" / "hôm qua"
```

---

## Flutter — slang (Recommended)

### Setup

```yaml
# pubspec.yaml
dependencies:
  flutter_localizations:
    sdk: flutter
  slang: ^4.0.0
  slang_flutter: ^4.0.0

dev_dependencies:
  slang_build_runner: ^4.0.0
  build_runner: ^2.0.0

flutter:
  generate: true
```

### Translation Files

```json
// assets/i18n/en.i18n.json
{
  "common": {
    "ok": "OK",
    "cancel": "Cancel",
    "loading": "Loading..."
  },
  "auth": {
    "login": "Login",
    "greeting": "Hello, $name!",
    "itemCount(n)": {
      "one": "$n item",
      "other": "$n items"
    }
  }
}
```

```json
// assets/i18n/vi.i18n.json
{
  "common": {
    "ok": "Đồng ý",
    "cancel": "Hủy",
    "loading": "Đang tải..."
  },
  "auth": {
    "login": "Đăng nhập",
    "greeting": "Xin chào, $name!",
    "itemCount(n)": "$n mục"
  }
}
```

### Generate + Use

```bash
dart run build_runner build
```

```dart
// main.dart
import 'package:flutter_localizations/flutter_localizations.dart';
import 'i18n/strings.g.dart';  // generated

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  LocaleSettings.useDeviceLocale();  // or .setLocale(AppLocale.vi)
  runApp(TranslationProvider(child: MyApp()));
}

class MyApp extends StatelessWidget {
  Widget build(BuildContext context) => MaterialApp(
    locale: TranslationProvider.of(context).flutterLocale,
    supportedLocales: AppLocaleUtils.supportedLocales,
    localizationsDelegates: GlobalMaterialLocalizations.delegates,
    home: HomeScreen(),
  );
}

// Usage — fully type-safe, autocomplete
final t = Translations.of(context);

Text(t.common.ok)
Text(t.auth.greeting(name: 'Phi'))
Text(t.auth.itemCount(n: 5))

// Change language
LocaleSettings.setLocale(AppLocale.vi);
```

---

## iOS Native (Xcode .xcstrings)

```
Localizable.xcstrings (modern, Xcode 15+):
  - Edit in Xcode string catalog UI
  - Automatic plural rules per language
  - Supports all Apple platforms

File structure:
  App/
  ├── en.lproj/Localizable.xcstrings  ← base language
  ├── vi.lproj/Localizable.xcstrings
  └── ar.lproj/Localizable.xcstrings
```

```swift
// Usage
Text(String(localized: "auth.login"))  // SwiftUI (auto-localizes)
label.text = NSLocalizedString("auth.login", comment: "")  // UIKit

// With interpolation
Text("profile.greeting \(userName)")
// Localizable.xcstrings: "profile.greeting %@" → "Xin chào, %@!"

// Date/Number formatting
let formatted = Date().formatted(.dateTime.month(.wide).day().year())
let price = amount.formatted(.currency(code: "VND").locale(Locale(identifier: "vi_VN")))
```

---

## Android Native (strings.xml)

```xml
<!-- res/values/strings.xml (English, default) -->
<resources>
  <string name="common_ok">OK</string>
  <string name="auth_login">Login</string>
  <string name="profile_greeting">Hello, %s!</string>
  <plurals name="profile_item_count">
    <item quantity="one">%d item</item>
    <item quantity="other">%d items</item>
  </plurals>
</resources>

<!-- res/values-vi/strings.xml (Vietnamese) -->
<resources>
  <string name="common_ok">Đồng ý</string>
  <string name="auth_login">Đăng nhập</string>
  <string name="profile_greeting">Xin chào, %s!</string>
  <plurals name="profile_item_count">
    <item quantity="other">%d mục</item>
  </plurals>
</resources>
```

```kotlin
// Usage
getString(R.string.auth_login)
getString(R.string.profile_greeting, "Phi")
resources.getQuantityString(R.plurals.profile_item_count, 5, 5)
```

---

## i18n Checklist

```
SETUP:
  □ Translation keys are namespaced (auth.login, not just "login")
  □ Base language file has ALL keys
  □ Missing key fallback configured (falls back to English)
  □ Language preference persisted on device (MMKV/SharedPreferences)
  □ Language detected from device locale on first launch

CONTENT:
  □ No hardcoded strings in components (all through t() / getString)
  □ Plurals handled correctly (1 item vs 2 items)
  □ Interpolation used for dynamic values (name, count)
  □ Date/number/currency formatted per locale (Intl API)

RTL (if supporting Arabic/Hebrew):
  □ I18nManager.forceRTL() applied and app reloaded
  □ flexDirection mirrors on RTL
  □ textAlign mirrors on RTL
  □ Icons and chevrons mirror on RTL
  □ Back navigation arrow mirrors on RTL

TESTING:
  □ Test with locale set to each supported language
  □ Test with system language set to unsupported → falls back to English
  □ Test RTL layout on Arabic device or simulator
  □ Test long strings (German/Finnish) don't break UI layout
```
