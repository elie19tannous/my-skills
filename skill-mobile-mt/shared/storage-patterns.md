# Mobile Storage Patterns

> On-device storage — when to use what, how to implement correctly.
> Covers: AsyncStorage, MMKV, SecureStore/Keychain, SQLite, WatermelonDB, Realm, SharedPreferences.

---

## Decision Matrix — Pick Storage Type First

```
WHAT ARE YOU STORING?          → STORAGE TO USE
────────────────────────────────────────────────────────────────────
Auth tokens / secrets          → SecureStore (RN) / Keychain (iOS)
                                 EncryptedSharedPreferences (Android)
                                 flutter_secure_storage (Flutter)

App preferences / settings     → MMKV (RN, fast KV)
(theme, language, onboarding)    SharedPreferences (Android native)
                                 UserDefaults (iOS native)
                                 shared_preferences (Flutter)

Simple key-value cache         → MMKV (RN) / MMKV (Flutter)
(session data, small objects)

Structured relational data     → SQLite (via expo-sqlite / sqflite)
(offline CRUD, complex queries)  WatermelonDB (RN, reactive queries)
                                 drift (Flutter, type-safe)

Large offline datasets         → WatermelonDB (RN)
(sync with server, observables)  drift (Flutter)
                                 Room (Android native)
                                 CoreData / SwiftData (iOS native)
                                 Realm (cross-platform)

Files / images / documents     → FileSystem (expo-file-system / path_provider)
                                 AsyncStorage ❌ (NOT for binary data)

⛔ RULE: AsyncStorage is deprecated for RN. Use MMKV instead.
⛔ RULE: NEVER store tokens in AsyncStorage / SharedPreferences / UserDefaults.
```

---

## React Native

### 1. Secure Storage (Tokens, Credentials)

```typescript
// expo-secure-store (Expo) / react-native-keychain (bare RN)
import * as SecureStore from 'expo-secure-store';

// Store
await SecureStore.setItemAsync('accessToken', token);

// Read
const token = await SecureStore.getItemAsync('accessToken');

// Delete (on logout — ALWAYS do this)
await SecureStore.deleteItemAsync('accessToken');
await SecureStore.deleteItemAsync('refreshToken');

// RULE: On logout, delete ALL secure store keys
async function logout() {
  await Promise.all([
    SecureStore.deleteItemAsync('accessToken'),
    SecureStore.deleteItemAsync('refreshToken'),
    SecureStore.deleteItemAsync('userId'),
  ]);
}
```

### 2. MMKV (Preferences + KV Cache) — 60x faster than AsyncStorage

```typescript
// react-native-mmkv
import { MMKV } from 'react-native-mmkv';

// Create instance (one per app, or per domain)
export const storage = new MMKV();

// Typed wrapper (recommended)
export const Storage = {
  getString: (key: string) => storage.getString(key),
  setString: (key: string, value: string) => storage.set(key, value),
  getBoolean: (key: string) => storage.getBoolean(key) ?? false,
  setBoolean: (key: string, value: boolean) => storage.set(key, value),
  getObject: <T>(key: string): T | null => {
    const raw = storage.getString(key);
    return raw ? JSON.parse(raw) : null;
  },
  setObject: <T>(key: string, value: T) => storage.set(key, JSON.stringify(value)),
  delete: (key: string) => storage.delete(key),
  clear: () => storage.clearAll(),
};

// With Zustand persist (recommended combo)
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

const mmkvStorage = {
  getItem: (name: string) => storage.getString(name) ?? null,
  setItem: (name: string, value: string) => storage.set(name, value),
  removeItem: (name: string) => storage.delete(name),
};

export const useSettingsStore = create(
  persist(
    (set) => ({
      theme: 'light',
      language: 'en',
      setTheme: (theme: string) => set({ theme }),
      setLanguage: (lang: string) => set({ language: lang }),
    }),
    { name: 'settings', storage: createJSONStorage(() => mmkvStorage) }
  )
);
```

### 3. SQLite / WatermelonDB (Structured Offline Data)

```typescript
// expo-sqlite (simple queries)
import * as SQLite from 'expo-sqlite';

const db = SQLite.openDatabaseSync('app.db');

// Init schema
db.execSync(`
  CREATE TABLE IF NOT EXISTS tasks (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    completed INTEGER NOT NULL DEFAULT 0,
    created_at INTEGER NOT NULL
  )
`);

// Query
const tasks = db.getAllSync<Task>('SELECT * FROM tasks WHERE completed = ?', [0]);

// Insert
db.runSync('INSERT INTO tasks (id, title, completed, created_at) VALUES (?, ?, ?, ?)',
  [uuid(), 'Buy milk', 0, Date.now()]);
```

```typescript
// WatermelonDB (reactive queries, sync-ready)
// Best for: large datasets, reactive UI, server sync
import { Database } from '@nozbe/watermelondb';
import SQLiteAdapter from '@nozbe/watermelondb/adapters/sqlite';

const adapter = new SQLiteAdapter({ schema, migrations });
const database = new Database({ adapter, modelClasses: [Post, Comment] });

// Observe (reactive — auto re-renders on change)
const posts = database.get('posts').query().observe();
```

### 4. Avoid AsyncStorage (Legacy)

```typescript
// ❌ DEPRECATED — avoid in new projects
import AsyncStorage from '@react-native-async-storage/async-storage';

// ✅ Migrate to MMKV:
// Before:  await AsyncStorage.setItem('theme', 'dark');
// After:   storage.set('theme', 'dark');

// ✅ Migrate to expo-secure-store for tokens:
// Before:  await AsyncStorage.setItem('token', jwt);
// After:   await SecureStore.setItemAsync('token', jwt);
```

---

## Flutter

### 1. Secure Storage (Tokens)

```dart
// flutter_secure_storage
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

final _secureStorage = FlutterSecureStorage(
  aOptions: AndroidOptions(encryptedSharedPreferences: true),
  iOptions: IOSOptions(accessibility: KeychainAccessibility.first_unlock),
);

// Store
await _secureStorage.write(key: 'accessToken', value: token);

// Read
final token = await _secureStorage.read(key: 'accessToken');

// Delete on logout
await _secureStorage.deleteAll();
```

### 2. SharedPreferences / Hive (KV Storage)

```dart
// shared_preferences (simple, built-in)
final prefs = await SharedPreferences.getInstance();
await prefs.setString('language', 'en');
final lang = prefs.getString('language') ?? 'en';

// Hive (faster, type-safe, no codegen)
import 'package:hive_flutter/hive_flutter.dart';

await Hive.initFlutter();
final box = await Hive.openBox('settings');
box.put('theme', 'dark');
final theme = box.get('theme', defaultValue: 'light');
```

### 3. Drift (SQLite, type-safe)

```dart
// drift — type-safe SQLite with code generation
@DriftDatabase(tables: [Tasks])
class AppDatabase extends _$AppDatabase {
  AppDatabase() : super(_openConnection());

  Stream<List<Task>> watchIncompleteTasks() =>
    (select(tasks)..where((t) => t.completed.not())).watch();

  Future insertTask(TasksCompanion task) => into(tasks).insert(task);
}
```

---

## iOS Native (Swift)

```swift
// UserDefaults — preferences ONLY (not tokens)
UserDefaults.standard.set("en", forKey: "language")
let lang = UserDefaults.standard.string(forKey: "language") ?? "en"

// Keychain — tokens and secrets
import Security

func saveToKeychain(key: String, value: String) {
    let data = value.data(using: .utf8)!
    let query: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrAccount as String: key,
        kSecValueData as String: data,
        kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly,
    ]
    SecItemDelete(query as CFDictionary)
    SecItemAdd(query as CFDictionary, nil)
}

// SwiftData / CoreData — structured offline data
@Model class Task {
    var id: UUID
    var title: String
    var completed: Bool
    init(title: String) { self.id = UUID(); self.title = title; self.completed = false }
}
```

---

## Android Native (Kotlin)

```kotlin
// EncryptedSharedPreferences — tokens and secrets
val masterKey = MasterKey.Builder(context)
    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM).build()
val encryptedPrefs = EncryptedSharedPreferences.create(
    context, "secure_prefs", masterKey,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)
encryptedPrefs.edit().putString("accessToken", token).apply()

// DataStore — preferences (replaces SharedPreferences)
val Context.dataStore by preferencesDataStore(name = "settings")
val LANGUAGE_KEY = stringPreferencesKey("language")

suspend fun saveLanguage(context: Context, lang: String) {
    context.dataStore.edit { it[LANGUAGE_KEY] = lang }
}

val languageFlow = context.dataStore.data.map { it[LANGUAGE_KEY] ?: "en" }

// Room — structured offline data
@Entity data class Task(@PrimaryKey val id: String, val title: String, val completed: Boolean)
@Dao interface TaskDao {
    @Query("SELECT * FROM task WHERE completed = 0") fun getActive(): Flow<List<Task>>
    @Insert suspend fun insert(task: Task)
}
```

---

## Security Checklist

```
✅ Tokens → SecureStore / Keychain / EncryptedSharedPreferences ONLY
✅ On logout → delete ALL secure storage keys
✅ Encrypt sensitive data before storing in SQLite/MMKV
✅ Don't log stored values (console.log, print)
✅ Use device-only accessibility (not iCloud sync for tokens)

⛔ NEVER: AsyncStorage for tokens
⛔ NEVER: UserDefaults for tokens
⛔ NEVER: SharedPreferences (unencrypted) for tokens
⛔ NEVER: Log token values in debug output
⛔ NEVER: Store plain-text passwords
```
