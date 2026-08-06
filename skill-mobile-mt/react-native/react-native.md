# React Native — Production Patterns

> Battle-tested patterns from production React Native apps.
> Supports: React Native CLI + Expo (managed & bare)
> Language: TypeScript (recommended) + JavaScript
> State: Redux, MobX, Zustand, TanStack Query, Apollo/GraphQL
> Navigation: @react-navigation (CLI) / expo-router (Expo)
> Networking: axios / fetch
> Package manager: yarn (preferred), npm, pnpm, bun

---

## Table of Contents

1. [Clean Architecture](#clean-architecture)
2. [Expo Project Structure](#expo-project-structure)
3. [State Management](#state-management)
4. [Navigation](#navigation)
5. [API Layer](#api-layer)
6. [Push Notifications](#push-notifications)
7. [Expo SDK Modules](#expo-sdk-modules)
8. [Build & Deploy](#build--deploy)
9. [Common Libraries](#common-libraries)
10. [Multi-Tenant Pattern](#multi-tenant--workspace-pattern)

---

## Clean Architecture

### React Native CLI

```
src/
├── app/                    # App entry, providers, root navigator
├── domain/                 # Business logic (pure, no dependencies)
│   ├── entities/           # Core business models
│   ├── usecases/           # Business rules
│   └── repositories/       # Repository interfaces (contracts)
├── data/                   # Data layer (implements domain interfaces)
│   ├── repositories/       # Repository implementations
│   ├── datasources/        # Remote (API) + Local (AsyncStorage, DB)
│   └── models/             # DTOs, mappers to domain entities
├── presentation/           # UI layer
│   ├── screens/            # Screen components (1 per route)
│   ├── components/
│   │   ├── common/         # Shared: Button, Input, Card, Modal
│   │   └── [feature]/      # Feature-specific components
│   ├── hooks/              # Custom hooks (useAuth, useApi)
│   └── navigation/         # Stack, Tab, Drawer navigators
├── services/               # External services (analytics, notifications)
├── utils/                  # Helpers, formatters, validators
├── constants/              # Colors, spacing, API URLs
├── types/                  # TypeScript types (if TS project)
└── assets/                 # Images, fonts
```

### Dependency Rule
```
presentation/ → domain/ ← data/

UI depends on Domain. Data depends on Domain.
Domain depends on NOTHING.
Never import data/ from presentation/ directly.
```

---

## Expo Project Structure

### Expo Router (file-based routing)

```
app/                        # File-based routes (expo-router)
├── _layout.tsx             # Root layout (providers, fonts, splash)
├── (tabs)/                 # Tab group
│   ├── _layout.tsx         # Tab navigator config
│   ├── index.tsx           # Home tab (/)
│   ├── search.tsx          # Search tab (/search)
│   └── profile.tsx         # Profile tab (/profile)
├── (auth)/                 # Auth group (no tabs)
│   ├── _layout.tsx         # Stack navigator for auth
│   ├── login.tsx           # /login
│   └── register.tsx        # /register
├── product/
│   └── [id].tsx            # Dynamic route: /product/123
├── +not-found.tsx          # 404 screen
└── +html.tsx               # Custom HTML wrapper (web)
src/
├── domain/                 # Same clean architecture as CLI
├── data/
├── components/
├── hooks/
├── services/
├── utils/
├── constants/
└── types/
```

### app.config.js / app.json

```javascript
// app.config.js — dynamic config (recommended over app.json)
export default ({ config }) => ({
  ...config,
  name: "MyApp",
  slug: "my-app",
  version: "1.0.0",
  scheme: "myapp",                    // Deep linking
  orientation: "portrait",
  icon: "./assets/icon.png",
  splash: { image: "./assets/splash.png", resizeMode: "contain" },
  ios: {
    bundleIdentifier: "com.company.myapp",
    supportsTablet: true,
  },
  android: {
    package: "com.company.myapp",
    adaptiveIcon: { foregroundImage: "./assets/adaptive-icon.png" },
  },
  plugins: [
    "expo-router",
    "expo-secure-store",
    ["expo-camera", { cameraPermission: "Allow camera access" }],
    ["expo-location", { locationAlwaysPermission: "Allow location" }],
  ],
  extra: {
    API_URL: process.env.API_URL || "https://api.example.com",
    eas: { projectId: "your-project-id" },
  },
});
```

### Root Layout (Expo Router)

```tsx
// app/_layout.tsx
import { Slot, SplashScreen } from 'expo-router';
import { useFonts } from 'expo-font';
import { useEffect } from 'react';

SplashScreen.preventAutoHideAsync();

export default function RootLayout() {
  const [fontsLoaded] = useFonts({ 'Inter': require('../assets/fonts/Inter.ttf') });

  useEffect(() => {
    if (fontsLoaded) SplashScreen.hideAsync();
  }, [fontsLoaded]);

  if (!fontsLoaded) return null;

  return <Slot />;
}
```

---

## State Management

### Redux Pattern (RTK)

```typescript
// presentation/store/slices/authSlice.ts
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

export const login = createAsyncThunk('auth/login', async (creds, { rejectWithValue }) => {
  try {
    const response = await authApi.login(creds);
    return response.data;
  } catch (error) {
    return rejectWithValue(error.response?.data);
  }
});

const authSlice = createSlice({
  name: 'auth',
  initialState: { user: null, token: null, loading: false, error: null },
  reducers: {
    logout: (state) => { state.user = null; state.token = null; },
  },
  extraReducers: (builder) => {
    builder
      .addCase(login.pending, (state) => { state.loading = true; state.error = null; })
      .addCase(login.fulfilled, (state, action) => {
        state.loading = false;
        state.user = action.payload.user;
        state.token = action.payload.token;
      })
      .addCase(login.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload;
      });
  },
});
```

### Zustand Pattern (lightweight alternative)

```typescript
// stores/useAuthStore.ts
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface AuthState {
  user: User | null;
  token: string | null;
  loading: boolean;
  login: (creds: Credentials) => Promise<void>;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      loading: false,

      login: async (creds) => {
        set({ loading: true });
        try {
          const res = await authApi.login(creds);
          set({ user: res.data.user, token: res.data.token, loading: false });
        } catch (error) {
          set({ loading: false });
          throw error;
        }
      },

      logout: () => set({ user: null, token: null }),
    }),
    { name: 'auth-storage', storage: createJSONStorage(() => AsyncStorage) }
  )
);
```

**JavaScript version:**
```javascript
// stores/useAuthStore.js
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import AsyncStorage from '@react-native-async-storage/async-storage';

export const useAuthStore = create(
  persist(
    (set) => ({
      user: null,
      token: null,
      loading: false,

      login: async (creds) => {
        set({ loading: true });
        try {
          const res = await authApi.login(creds);
          set({ user: res.data.user, token: res.data.token, loading: false });
        } catch (error) {
          set({ loading: false });
          throw error;
        }
      },

      logout: () => set({ user: null, token: null }),
    }),
    { name: 'auth-storage', storage: createJSONStorage(() => AsyncStorage) }
  )
);
```

### TanStack Query (server state)

```typescript
// hooks/useProducts.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

export function useProducts() {
  return useQuery({
    queryKey: ['products'],
    queryFn: () => api.get('/products').then(r => r.data),
    staleTime: 5 * 60 * 1000,  // 5 min cache
  });
}

export function useCreateProduct() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (product) => api.post('/products', product),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['products'] }),
  });
}

// In component:
function ProductList() {
  const { data, isLoading, error, refetch } = useProducts();
  if (isLoading) return <LoadingSkeleton />;
  if (error) return <ErrorView message={error.message} onRetry={refetch} />;
  if (!data?.length) return <EmptyState />;
  return <FlatList data={data} keyExtractor={item => item.id} renderItem={...} />;
}
```

### MobX Pattern

```typescript
import { makeAutoObservable, runInAction } from 'mobx';

class AuthStore {
  user = null;
  token = null;
  loading = false;

  constructor() { makeAutoObservable(this); }

  async login(creds) {
    this.loading = true;
    try {
      const res = await authApi.login(creds);
      runInAction(() => {
        this.user = res.data.user;
        this.token = res.data.token;
        this.loading = false;
      });
    } catch (error) {
      runInAction(() => { this.loading = false; });
      throw error;
    }
  }
}
```

---

## Navigation

### @react-navigation (React Native CLI)

```typescript
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

function MainTabs() {
  return (
    <Tab.Navigator>
      <Tab.Screen name="Home" component={HomeScreen} />
      <Tab.Screen name="Profile" component={ProfileScreen} />
    </Tab.Navigator>
  );
}

function AppNavigator() {
  const isLoggedIn = useSelector(state => state.auth.token);
  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {isLoggedIn ? (
          <Stack.Screen name="Main" component={MainTabs} />
        ) : (
          <Stack.Screen name="Auth" component={AuthStack} />
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
```

### expo-router (Expo)

```tsx
// app/(tabs)/_layout.tsx
import { Tabs } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

export default function TabLayout() {
  return (
    <Tabs screenOptions={{ tabBarActiveTintColor: '#007AFF' }}>
      <Tabs.Screen name="index" options={{
        title: 'Home',
        tabBarIcon: ({ color }) => <Ionicons name="home" size={24} color={color} />,
      }} />
      <Tabs.Screen name="profile" options={{
        title: 'Profile',
        tabBarIcon: ({ color }) => <Ionicons name="person" size={24} color={color} />,
      }} />
    </Tabs>
  );
}

// Navigation in expo-router:
import { router } from 'expo-router';

// Push screen
router.push('/product/123');
// Replace screen
router.replace('/login');
// Go back
router.back();
// Navigate with params
router.push({ pathname: '/product/[id]', params: { id: '123' } });
```

**JavaScript version:**
```jsx
// app/(tabs)/_layout.js
import { Tabs } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';

export default function TabLayout() {
  return (
    <Tabs screenOptions={{ tabBarActiveTintColor: '#007AFF' }}>
      <Tabs.Screen name="index" options={{
        title: 'Home',
        tabBarIcon: ({ color }) => <Ionicons name="home" size={24} color={color} />,
      }} />
      <Tabs.Screen name="profile" options={{
        title: 'Profile',
        tabBarIcon: ({ color }) => <Ionicons name="person" size={24} color={color} />,
      }} />
    </Tabs>
  );
}
```

### Auth-Protected Routes (expo-router)

```tsx
// app/(auth)/_layout.tsx
import { Redirect, Stack } from 'expo-router';
import { useAuthStore } from '../../stores/useAuthStore';

export default function AuthLayout() {
  const token = useAuthStore(s => s.token);
  if (token) return <Redirect href="/(tabs)" />;
  return <Stack screenOptions={{ headerShown: false }} />;
}

// app/(tabs)/_layout.tsx
import { Redirect, Tabs } from 'expo-router';
import { useAuthStore } from '../../stores/useAuthStore';

export default function TabLayout() {
  const token = useAuthStore(s => s.token);
  if (!token) return <Redirect href="/(auth)/login" />;
  return <Tabs>...</Tabs>;
}
```

---

## API Layer

### axios (with interceptors)

```typescript
import axios from 'axios';

const api = axios.create({ baseURL: API_URL, timeout: 15000 });

api.interceptors.request.use((config) => {
  const token = store.getState().auth.token;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (error) => {
    if (error.response?.status === 401) {
      store.dispatch(logout());
    }
    return Promise.reject(error);
  }
);
```

### fetch (no dependencies)

```javascript
// services/api.js — works with both TS and JS
const API_URL = 'https://api.example.com';

async function request(endpoint, options = {}) {
  const token = getToken(); // from secure storage
  const response = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token && { Authorization: `Bearer ${token}` }),
      ...options.headers,
    },
  });

  if (response.status === 401) {
    handleLogout();
    throw new Error('Unauthorized');
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.message || `HTTP ${response.status}`);
  }

  return response.json();
}

export const api = {
  get: (endpoint) => request(endpoint),
  post: (endpoint, data) => request(endpoint, { method: 'POST', body: JSON.stringify(data) }),
  put: (endpoint, data) => request(endpoint, { method: 'PUT', body: JSON.stringify(data) }),
  delete: (endpoint) => request(endpoint, { method: 'DELETE' }),
};
```

---

## Push Notifications

### Firebase (React Native CLI)

```typescript
import messaging from '@react-native-firebase/messaging';

async function requestNotificationPermission() {
  const authStatus = await messaging().requestPermission();
  if (authStatus === messaging.AuthorizationStatus.AUTHORIZED) {
    const token = await messaging().getToken();
    await api.post('/devices/register', { fcm_token: token });
  }
}
```

### expo-notifications (Expo)

```typescript
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';
import Constants from 'expo-constants';

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

async function registerForPushNotifications() {
  if (!Device.isDevice) return null; // Must be physical device

  const { status: existing } = await Notifications.getPermissionsAsync();
  let finalStatus = existing;

  if (existing !== 'granted') {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }

  if (finalStatus !== 'granted') return null;

  const token = (await Notifications.getExpoPushTokenAsync({
    projectId: Constants.expoConfig?.extra?.eas?.projectId,
  })).data;

  await api.post('/devices/register', { push_token: token });
  return token;
}
```

---

## Expo SDK Modules

| Purpose | Package | Usage |
|---------|---------|-------|
| Secure Storage | `expo-secure-store` | Tokens, secrets (Keychain/Keystore) |
| Camera | `expo-camera` | Camera access with permissions |
| Location | `expo-location` | GPS, geofencing |
| Image Picker | `expo-image-picker` | Photo library + camera |
| File System | `expo-file-system` | Read/write local files |
| Notifications | `expo-notifications` | Push + local notifications |
| Auth Session | `expo-auth-session` | OAuth (Google, Apple, etc.) |
| Linking | `expo-linking` | Deep links |
| Haptics | `expo-haptics` | Vibration feedback |
| Splash Screen | `expo-splash-screen` | Control splash visibility |
| Font | `expo-font` | Custom fonts |
| Constants | `expo-constants` | App config values |

### Expo + Native Modules

```
⚠️  If you need a native module not in Expo SDK:
1. Use "expo prebuild" to eject to bare workflow
2. Or use a config plugin: plugins: ["my-native-package"]
3. Or use EAS Build (handles native deps in cloud)
⛔ NEVER run "expo eject" — deprecated. Use "expo prebuild" instead.
```

---

## Build & Deploy

### React Native CLI

```
scripts:
  dev:     react-native run-android --variant=devDebug
  staging: react-native run-android --variant=stagingDebug
  prod:    react-native run-android --variant=prodRelease
```

### Expo (EAS Build)

```bash
# Install EAS CLI
npm install -g eas-cli

# Configure (creates eas.json)
eas build:configure

# Build for stores
eas build --platform ios --profile production
eas build --platform android --profile production

# Build for testing (internal distribution)
eas build --platform all --profile preview

# OTA update (no store review needed)
eas update --branch production --message "Fix: cart total bug"

# Submit to stores
eas submit --platform ios
eas submit --platform android
```

### eas.json

```json
{
  "build": {
    "development": {
      "developmentClient": true,
      "distribution": "internal",
      "env": { "API_URL": "https://dev-api.example.com" }
    },
    "preview": {
      "distribution": "internal",
      "env": { "API_URL": "https://staging-api.example.com" }
    },
    "production": {
      "env": { "API_URL": "https://api.example.com" }
    }
  },
  "submit": {
    "production": {
      "ios": { "appleId": "you@example.com", "ascAppId": "123456789" },
      "android": { "serviceAccountKeyPath": "./google-sa-key.json" }
    }
  }
}
```

---

## Common Libraries

### React Native CLI

| Purpose | Library |
|---------|---------|
| HTTP | axios |
| State | redux + redux-persist |
| State | mobx + mobx-react |
| State | zustand |
| Server State | @tanstack/react-query |
| State | @apollo/client |
| Nav | @react-navigation |
| Anim | react-native-reanimated |
| Gestures | react-native-gesture-handler |
| Camera | react-native-camera |
| Maps | react-native-maps |
| Push | @react-native-firebase/messaging |
| Image | react-native-image-picker |
| Fast Image | react-native-fast-image |
| Bottom Sheet | @gorhom/bottom-sheet |
| Lottie | lottie-react-native |
| Socket | socket.io-client |
| Forms | react-hook-form + zod |
| Styled | nativewind (Tailwind) / styled-components |

### Expo

| Purpose | Library |
|---------|---------|
| HTTP | axios / fetch (built-in) |
| State | zustand (recommended) / redux |
| Server State | @tanstack/react-query |
| Nav | expo-router |
| Camera | expo-camera |
| Location | expo-location |
| Image | expo-image-picker |
| Fast Image | expo-image |
| Push | expo-notifications |
| Storage | expo-secure-store |
| Auth | expo-auth-session |
| Icons | @expo/vector-icons |
| Fonts | expo-font + expo-splash-screen |
| Forms | react-hook-form + zod |
| Styled | nativewind (Tailwind) / tamagui |

---

## Multi-Tenant / Workspace Pattern

```
workspace/
├── tenants/
│   ├── tenant-a/config.js      # Tenant-specific config
│   ├── tenant-b/config.js
│   └── tenant-c/config.js
├── source/
│   ├── src/                     # Shared code
│   └── config/                  # Base config
└── package.json                 # Yarn workspaces, nohoist for RN deps
```

---

## Quick Reference

| Project Type | Navigation | Build | Push | Storage |
|-------------|-----------|-------|------|---------|
| RN CLI + TS | @react-navigation | Gradle/Xcode | Firebase | react-native-keychain |
| RN CLI + JS | @react-navigation | Gradle/Xcode | Firebase | react-native-keychain |
| Expo + TS | expo-router | EAS Build | expo-notifications | expo-secure-store |
| Expo + JS | expo-router | EAS Build | expo-notifications | expo-secure-store |

> **Zustand + TanStack Query** is the modern lightweight choice.
> **Redux** for complex apps with many cross-feature state dependencies.
> **MobX** for complex observable state patterns.
> **Apollo** for GraphQL backends.
