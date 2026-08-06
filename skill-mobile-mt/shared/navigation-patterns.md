# Navigation Patterns — Complex Flows

> On-demand module. Loaded when implementing auth flows, deep links, modals, or tab navigation.
> Contains production patterns for React Native, Flutter, iOS, and Android.

---

## Auth-Based Navigation Flow

### React Native (React Navigation)

```typescript
// navigation/RootNavigator.tsx
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { useAuthStore, useIsLoggedIn } from '@/stores/useAuthStore';

const Stack = createNativeStackNavigator<RootStackParamList>();

export function RootNavigator() {
  const isLoggedIn = useIsLoggedIn();
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    // Check stored token on app start
    async function bootstrap() {
      const hasToken = useAuthStore.getState().token;
      if (hasToken) {
        const valid = await useAuthStore.getState().refreshSession();
        if (!valid) useAuthStore.getState().logout();
      }
      setIsReady(true);
    }
    bootstrap();
  }, []);

  if (!isReady) return <SplashScreen />;

  return (
    <NavigationContainer>
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        {isLoggedIn ? (
          // Authenticated stack
          <>
            <Stack.Screen name="MainTabs" component={MainTabNavigator} />
            <Stack.Screen name="ProductDetail" component={ProductDetailScreen} />
            <Stack.Screen name="Settings" component={SettingsScreen} />
            {/* Modals */}
            <Stack.Group screenOptions={{ presentation: 'modal' }}>
              <Stack.Screen name="EditProfile" component={EditProfileScreen} />
              <Stack.Screen name="ImageViewer" component={ImageViewerScreen} />
            </Stack.Group>
          </>
        ) : (
          // Unauthenticated stack
          <>
            <Stack.Screen name="Onboarding" component={OnboardingScreen} />
            <Stack.Screen name="Login" component={LoginScreen} />
            <Stack.Screen name="Register" component={RegisterScreen} />
            <Stack.Screen name="ForgotPassword" component={ForgotPasswordScreen} />
          </>
        )}
      </Stack.Navigator>
    </NavigationContainer>
  );
}
```

### Flutter (GoRouter)

```dart
// navigation/app_router.dart
import 'package:go_router/go_router.dart';

final appRouter = GoRouter(
  initialLocation: '/',
  redirect: (context, state) {
    final isLoggedIn = ref.read(authProvider).isLoggedIn;
    final isAuthRoute = state.matchedLocation.startsWith('/auth');

    if (!isLoggedIn && !isAuthRoute) return '/auth/login';
    if (isLoggedIn && isAuthRoute) return '/';
    return null;
  },
  routes: [
    // Auth routes
    GoRoute(path: '/auth/login', builder: (_, __) => const LoginScreen()),
    GoRoute(path: '/auth/register', builder: (_, __) => const RegisterScreen()),

    // App routes with bottom nav shell
    ShellRoute(
      builder: (_, __, child) => ScaffoldWithNavBar(child: child),
      routes: [
        GoRoute(path: '/', builder: (_, __) => const HomeScreen()),
        GoRoute(path: '/search', builder: (_, __) => const SearchScreen()),
        GoRoute(path: '/cart', builder: (_, __) => const CartScreen()),
        GoRoute(path: '/profile', builder: (_, __) => const ProfileScreen()),
      ],
    ),

    // Detail routes (no bottom nav)
    GoRoute(
      path: '/product/:id',
      builder: (_, state) => ProductDetailScreen(id: state.pathParameters['id']!),
    ),
  ],
);
```

---

## Deep Linking

### React Native (Expo Router)

```typescript
// app/_layout.tsx — Expo Router handles deep links automatically via file structure
// URL: myapp://product/abc-123 → app/product/[id].tsx

// app/product/[id].tsx
import { useLocalSearchParams } from 'expo-router';

export default function ProductDetailScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();

  // Validate param exists
  if (!id) return <NotFoundScreen />;

  // Fetch and render
  const { data, isLoading } = useProductDetail(id as ProductId);
  // ...
}
```

### React Navigation Deep Link Config

```typescript
// navigation/linking.ts
const linking: LinkingOptions<RootStackParamList> = {
  prefixes: ['myapp://', 'https://myapp.com'],
  config: {
    screens: {
      MainTabs: {
        screens: {
          Home: 'home',
          Profile: 'profile/:userId',
        },
      },
      ProductDetail: 'product/:productId',
      Settings: 'settings',
    },
  },
};

// Handle notification deep links
import * as Notifications from 'expo-notifications';

function useNotificationDeepLink() {
  const navigation = useAppNavigation();

  useEffect(() => {
    const sub = Notifications.addNotificationResponseReceivedListener(response => {
      const data = response.notification.request.content.data;
      if (data.screen === 'ProductDetail' && data.productId) {
        navigation.navigate('ProductDetail', { productId: data.productId as ProductId });
      }
    });
    return () => sub.remove();
  }, [navigation]);
}
```

---

## Bottom Tab Navigation

### React Native — Lazy Tabs with State Preservation

```typescript
// navigation/MainTabNavigator.tsx
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';

const Tab = createBottomTabNavigator<MainTabParamList>();

export function MainTabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        // Lazy load: render tab only when first visited
        lazy: true,
        // Freeze inactive tabs (prevent re-renders)
        freezeOnBlur: true,
        tabBarActiveTintColor: theme.colors.primary,
      }}
    >
      <Tab.Screen
        name="Home"
        component={HomeScreen}
        options={{
          tabBarIcon: ({ color, size }) => <HomeIcon color={color} size={size} />,
          tabBarLabel: 'Home',
        }}
      />
      <Tab.Screen
        name="Search"
        component={SearchScreen}
        options={{
          tabBarIcon: ({ color, size }) => <SearchIcon color={color} size={size} />,
        }}
      />
      <Tab.Screen
        name="Cart"
        component={CartScreen}
        options={{
          tabBarIcon: ({ color, size }) => <CartIcon color={color} size={size} />,
          tabBarBadge: cartCount > 0 ? cartCount : undefined,
        }}
      />
      <Tab.Screen
        name="Profile"
        component={ProfileScreen}
        options={{
          tabBarIcon: ({ color, size }) => <ProfileIcon color={color} size={size} />,
        }}
      />
    </Tab.Navigator>
  );
}
```

---

## Modal Navigation

### React Native — Modal Stack

```typescript
// Present as modal (slides up from bottom on iOS)
navigation.navigate('EditProfile'); // registered in modal group

// Dismiss modal
navigation.goBack();

// Modal with result — pass callback via params or use event
// Option A: Use navigation params
navigation.navigate('SelectAddress', {
  onSelect: (address: Address) => {
    // handle selected address
  },
});

// Option B: Use event emitter
import { DeviceEventEmitter } from 'react-native';
// In modal: DeviceEventEmitter.emit('addressSelected', address);
// In parent: DeviceEventEmitter.addListener('addressSelected', handler);
```

### Flutter — Modal Bottom Sheet

```dart
// Modal bottom sheet
showModalBottomSheet(
  context: context,
  isScrollControlled: true, // full-height if needed
  useSafeArea: true,
  builder: (context) => DraggableScrollableSheet(
    initialChildSize: 0.6,
    minChildSize: 0.3,
    maxChildSize: 0.9,
    builder: (_, controller) => AddressPickerSheet(scrollController: controller),
  ),
);
```

---

## Push Notification Navigation

### React Native (Expo Notifications)

```typescript
// hooks/useNotificationSetup.ts
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';

export function useNotificationSetup() {
  useEffect(() => {
    registerForPush();
  }, []);

  async function registerForPush() {
    if (!Device.isDevice) return; // skip simulator

    const { status } = await Notifications.getPermissionsAsync();
    let finalStatus = status;

    if (status !== 'granted') {
      const { status: newStatus } = await Notifications.requestPermissionsAsync();
      finalStatus = newStatus;
    }

    if (finalStatus !== 'granted') return;

    const token = (await Notifications.getExpoPushTokenAsync()).data;
    await userService.registerPushToken(token);
  }
}

// Notification handler — runs when app receives notification
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});
```

---

## Permissions Handling Pattern

```typescript
// hooks/usePermission.ts
import * as Location from 'expo-location';
import * as Camera from 'expo-camera';
import { Alert, Linking } from 'react-native';

type PermissionType = 'camera' | 'location' | 'notifications';

export function usePermission(type: PermissionType) {
  const [granted, setGranted] = useState<boolean | null>(null);

  const request = useCallback(async () => {
    let result: { status: string };

    switch (type) {
      case 'camera':
        result = await Camera.requestCameraPermissionsAsync();
        break;
      case 'location':
        result = await Location.requestForegroundPermissionsAsync();
        break;
      case 'notifications':
        result = await Notifications.requestPermissionsAsync();
        break;
    }

    if (result.status === 'granted') {
      setGranted(true);
      return true;
    }

    // Permission denied — guide user to settings
    Alert.alert(
      'Permission Required',
      `Please enable ${type} access in Settings to use this feature.`,
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Open Settings', onPress: () => Linking.openSettings() },
      ]
    );
    setGranted(false);
    return false;
  }, [type]);

  return { granted, request };
}

// Usage:
// const camera = usePermission('camera');
// const canUse = await camera.request();
// if (canUse) { /* proceed */ }
```
