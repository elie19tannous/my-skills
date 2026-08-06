# Code Generation Templates — Production-Ready Patterns

> On-demand module. Loaded when building new features, setting up state management, API clients, or forms.
> Contains COMPLETE, copy-and-adapt code templates — not snippets.

---

## State Management Templates

### Zustand (React Native) — Advanced Store

```typescript
// stores/useAuthStore.ts
import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface User { id: string; email: string; name: string; role: 'user' | 'admin'; }

interface AuthState {
  user: User | null;
  token: string | null;
  refreshToken: string | null;
  isLoading: boolean;
  error: string | null;
  // Actions
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refreshSession: () => Promise<boolean>;
  clearError: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    immer((set, get) => ({
      user: null,
      token: null,
      refreshToken: null,
      isLoading: false,
      error: null,

      login: async (email, password) => {
        set(state => { state.isLoading = true; state.error = null; });
        try {
          const res = await authService.login({ email, password });
          set(state => {
            state.user = res.user;
            state.token = res.token;
            state.refreshToken = res.refreshToken;
            state.isLoading = false;
          });
        } catch (e) {
          set(state => {
            state.isLoading = false;
            state.error = e instanceof Error ? e.message : 'Login failed';
          });
        }
      },

      logout: () => {
        set(state => {
          state.user = null;
          state.token = null;
          state.refreshToken = null;
        });
      },

      refreshSession: async () => {
        const { refreshToken } = get();
        if (!refreshToken) return false;
        try {
          const res = await authService.refresh(refreshToken);
          set(state => { state.token = res.token; state.refreshToken = res.refreshToken; });
          return true;
        } catch {
          get().logout();
          return false;
        }
      },

      clearError: () => set(state => { state.error = null; }),
    })),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => AsyncStorage),
      partialize: (state) => ({ token: state.token, refreshToken: state.refreshToken, user: state.user }),
    }
  )
);

// Selectors (memoized — prevent re-renders)
export const useIsLoggedIn = () => useAuthStore(state => !!state.token);
export const useUserRole = () => useAuthStore(state => state.user?.role);
```

### Zustand Store Composition

```typescript
// stores/index.ts — composing multiple stores
export { useAuthStore, useIsLoggedIn } from './useAuthStore';
export { useCartStore } from './useCartStore';
export { useSettingsStore } from './useSettingsStore';

// Usage: each store is independent, no single god-store
// Components subscribe to ONLY the store they need
```

### Redux Toolkit — Entity Adapter for Collections

```typescript
// features/products/productsSlice.ts
import { createSlice, createAsyncThunk, createEntityAdapter, PayloadAction } from '@reduxjs/toolkit';
import { Product } from './product.types';
import { productService } from './productService';

const productsAdapter = createEntityAdapter<Product>({
  selectId: (product) => product.id,
  sortComparer: (a, b) => b.createdAt.localeCompare(a.createdAt),
});

interface ProductsExtra { loading: boolean; error: string | null; page: number; hasMore: boolean; }

const initialState = productsAdapter.getInitialState<ProductsExtra>({
  loading: false, error: null, page: 1, hasMore: true,
});

export const fetchProducts = createAsyncThunk(
  'products/fetch',
  async (page: number, { rejectWithValue }) => {
    try {
      return await productService.getProducts(page);
    } catch (e) {
      return rejectWithValue(e instanceof Error ? e.message : 'Failed to fetch');
    }
  }
);

const productsSlice = createSlice({
  name: 'products',
  initialState,
  reducers: {
    productUpdated: productsAdapter.updateOne,
    productRemoved: productsAdapter.removeOne,
    productsReset: () => initialState,
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchProducts.pending, (state) => { state.loading = true; state.error = null; })
      .addCase(fetchProducts.fulfilled, (state, action) => {
        state.loading = false;
        state.page += 1;
        state.hasMore = action.payload.length >= 20;
        productsAdapter.upsertMany(state, action.payload);
      })
      .addCase(fetchProducts.rejected, (state, action) => {
        state.loading = false;
        state.error = action.payload as string;
      });
  },
});

export const { productUpdated, productRemoved, productsReset } = productsSlice.actions;
export default productsSlice.reducer;

// Typed selectors
export const {
  selectAll: selectAllProducts,
  selectById: selectProductById,
  selectTotal: selectProductCount,
} = productsAdapter.getSelectors((state: RootState) => state.products);
```

### Riverpod (Flutter) — Async + Family

```dart
// providers/product_provider.dart
import 'package:riverpod_annotation/riverpod_annotation.dart';
part 'product_provider.g.dart';

@riverpod
class ProductList extends _$ProductList {
  int _page = 1;
  bool _hasMore = true;

  @override
  FutureOr<List<Product>> build() => _fetch();

  Future<List<Product>> _fetch() async {
    final repo = ref.watch(productRepositoryProvider);
    return repo.getProducts(page: 1);
  }

  Future<void> loadMore() async {
    if (!_hasMore) return;
    final repo = ref.read(productRepositoryProvider);
    final next = await repo.getProducts(page: _page + 1);
    _hasMore = next.length >= 20;
    _page++;
    state = AsyncData([...state.value ?? [], ...next]);
  }

  Future<void> refresh() async {
    _page = 1;
    _hasMore = true;
    ref.invalidateSelf();
  }
}

// Family provider — parameterized by ID
@riverpod
Future<Product> productDetail(ProductDetailRef ref, String id) async {
  final repo = ref.watch(productRepositoryProvider);
  return repo.getProductById(id);
}

// Usage in widget:
// final products = ref.watch(productListProvider);
// products.when(data: (list) => ..., error: (e, _) => ..., loading: () => ...);
//
// final detail = ref.watch(productDetailProvider('abc-123'));
```

---

## API Client Templates

### React Native — Axios with Retry + Token Queue

```typescript
// services/api.ts
import axios, { AxiosError, AxiosRequestConfig, InternalAxiosRequestConfig } from 'axios';
import { useAuthStore } from '@/stores/useAuthStore';

const api = axios.create({
  baseURL: process.env.EXPO_PUBLIC_API_URL,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
});

// Token refresh queue — prevents concurrent refresh calls
let isRefreshing = false;
let failedQueue: Array<{ resolve: (token: string) => void; reject: (error: Error) => void }> = [];

const processQueue = (error: Error | null, token: string | null) => {
  failedQueue.forEach(({ resolve, reject }) => {
    error ? reject(error) : resolve(token!);
  });
  failedQueue = [];
};

// Request interceptor — attach token
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = useAuthStore.getState().token;
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// Response interceptor — auto-refresh on 401
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({
            resolve: (token) => {
              originalRequest.headers = { ...originalRequest.headers, Authorization: `Bearer ${token}` };
              resolve(api(originalRequest));
            },
            reject,
          });
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const success = await useAuthStore.getState().refreshSession();
        if (success) {
          const newToken = useAuthStore.getState().token!;
          processQueue(null, newToken);
          originalRequest.headers = { ...originalRequest.headers, Authorization: `Bearer ${newToken}` };
          return api(originalRequest);
        }
      } catch (refreshError) {
        processQueue(refreshError as Error, null);
        useAuthStore.getState().logout();
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(normalizeError(error));
  }
);

// Retry with exponential backoff
export async function apiWithRetry<T>(
  fn: () => Promise<T>,
  maxRetries = 3,
  baseDelay = 1000
): Promise<T> {
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      const isRetryable = error instanceof AppError && error.isRetryable;
      if (!isRetryable || attempt === maxRetries) throw error;
      const delay = baseDelay * Math.pow(2, attempt) + Math.random() * 500; // jitter
      await new Promise(r => setTimeout(r, delay));
    }
  }
  throw new Error('Unreachable');
}

export default api;
```

### Flutter — Dio with Interceptors

```dart
// services/api_client.dart
import 'package:dio/dio.dart';

class ApiClient {
  late final Dio _dio;
  final TokenStorage _tokenStorage;

  ApiClient({required TokenStorage tokenStorage}) : _tokenStorage = tokenStorage {
    _dio = Dio(BaseOptions(
      baseUrl: const String.fromEnvironment('API_URL'),
      connectTimeout: const Duration(seconds: 15),
      receiveTimeout: const Duration(seconds: 15),
    ));

    _dio.interceptors.addAll([
      _AuthInterceptor(_tokenStorage, _dio),
      _RetryInterceptor(maxRetries: 3),
      LogInterceptor(requestBody: true, responseBody: true),
    ]);
  }

  Future<T> get<T>(String path, {Map<String, dynamic>? params, T Function(dynamic)? fromJson}) async {
    final res = await _dio.get(path, queryParameters: params);
    return fromJson != null ? fromJson(res.data) : res.data as T;
  }

  Future<T> post<T>(String path, {dynamic data, T Function(dynamic)? fromJson}) async {
    final res = await _dio.post(path, data: data);
    return fromJson != null ? fromJson(res.data) : res.data as T;
  }
}

class _AuthInterceptor extends Interceptor {
  final TokenStorage _storage;
  final Dio _dio;

  _AuthInterceptor(this._storage, this._dio);

  @override
  void onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
    final token = await _storage.getAccessToken();
    if (token != null) options.headers['Authorization'] = 'Bearer $token';
    handler.next(options);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    if (err.response?.statusCode == 401) {
      try {
        final newToken = await _refreshToken();
        err.requestOptions.headers['Authorization'] = 'Bearer $newToken';
        final res = await _dio.fetch(err.requestOptions);
        handler.resolve(res);
        return;
      } catch (_) {
        await _storage.clear();
      }
    }
    handler.next(err);
  }

  Future<String> _refreshToken() async {
    final refresh = await _storage.getRefreshToken();
    final res = await _dio.post('/auth/refresh', data: {'refreshToken': refresh});
    final token = res.data['accessToken'] as String;
    await _storage.saveAccessToken(token);
    return token;
  }
}
```

---

## Form Templates

### React Native — TanStack Form + Zod

```typescript
// forms/useLoginForm.ts
import { useForm } from '@tanstack/react-form';
import { zodValidator } from '@tanstack/zod-form-adapter';
import { z } from 'zod';

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

export function useLoginForm(onSubmit: (data: z.infer<typeof loginSchema>) => Promise<void>) {
  return useForm({
    defaultValues: { email: '', password: '' },
    validatorAdapter: zodValidator(),
    validators: { onChange: loginSchema },
    onSubmit: async ({ value }) => {
      await onSubmit(value);
    },
  });
}

// LoginScreen.tsx — usage
function LoginScreen() {
  const form = useLoginForm(async (data) => {
    await authService.login(data.email, data.password);
  });

  return (
    <form.Provider>
      <form.Field name="email">
        {(field) => (
          <View>
            <TextInput
              value={field.state.value}
              onChangeText={field.handleChange}
              onBlur={field.handleBlur}
              placeholder="Email"
              keyboardType="email-address"
              autoCapitalize="none"
            />
            {field.state.meta.errors.length > 0 && (
              <Text style={styles.error}>{field.state.meta.errors[0]}</Text>
            )}
          </View>
        )}
      </form.Field>

      <form.Field name="password">
        {(field) => (
          <View>
            <TextInput
              value={field.state.value}
              onChangeText={field.handleChange}
              onBlur={field.handleBlur}
              placeholder="Password"
              secureTextEntry
            />
            {field.state.meta.errors.length > 0 && (
              <Text style={styles.error}>{field.state.meta.errors[0]}</Text>
            )}
          </View>
        )}
      </form.Field>

      <form.Subscribe selector={(state) => [state.canSubmit, state.isSubmitting]}>
        {([canSubmit, isSubmitting]) => (
          <Button
            title={isSubmitting ? 'Logging in...' : 'Login'}
            onPress={form.handleSubmit}
            disabled={!canSubmit || isSubmitting}
          />
        )}
      </form.Subscribe>
    </form.Provider>
  );
}
```

### Multi-Step Form Pattern

```typescript
// forms/useMultiStepForm.ts
import { useState, useCallback } from 'react';

interface StepConfig<T> {
  validate: (data: Partial<T>) => Record<string, string> | null;
}

export function useMultiStepForm<T extends Record<string, unknown>>(
  steps: StepConfig<T>[],
  initialData: Partial<T>
) {
  const [currentStep, setCurrentStep] = useState(0);
  const [data, setData] = useState<Partial<T>>(initialData);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const updateField = useCallback(<K extends keyof T>(key: K, value: T[K]) => {
    setData(prev => ({ ...prev, [key]: value }));
    setErrors(prev => { const next = { ...prev }; delete next[key as string]; return next; });
  }, []);

  const next = useCallback(() => {
    const validationErrors = steps[currentStep].validate(data);
    if (validationErrors) { setErrors(validationErrors); return false; }
    setCurrentStep(prev => Math.min(prev + 1, steps.length - 1));
    return true;
  }, [currentStep, data, steps]);

  const back = useCallback(() => {
    setCurrentStep(prev => Math.max(prev - 1, 0));
  }, []);

  return {
    currentStep,
    totalSteps: steps.length,
    data,
    errors,
    updateField,
    next,
    back,
    isFirst: currentStep === 0,
    isLast: currentStep === steps.length - 1,
    progress: (currentStep + 1) / steps.length,
  };
}
```

### File Upload with Progress

```typescript
// services/uploadService.ts
import * as ImagePicker from 'expo-image-picker';
import api from './api';

export async function pickAndUploadImage(
  onProgress?: (percent: number) => void
): Promise<{ url: string }> {
  // 1. Pick image
  const result = await ImagePicker.launchImageLibraryAsync({
    mediaTypes: ImagePicker.MediaTypeOptions.Images,
    allowsEditing: true,
    quality: 0.8,
    base64: false,
  });

  if (result.canceled) throw new Error('User cancelled');
  const asset = result.assets[0];

  // 2. Validate
  if (asset.fileSize && asset.fileSize > 5 * 1024 * 1024) {
    throw new Error('Image must be under 5MB');
  }

  // 3. Upload with progress
  const formData = new FormData();
  formData.append('file', {
    uri: asset.uri,
    type: asset.mimeType ?? 'image/jpeg',
    name: asset.fileName ?? 'photo.jpg',
  } as unknown as Blob);

  const { data } = await api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    onUploadProgress: (e) => {
      if (e.total) onProgress?.(Math.round((e.loaded / e.total) * 100));
    },
  });

  return data;
}
```

---

## Type Generation Patterns

### API Response → TypeScript Interfaces

```typescript
// types/api.types.ts — Branded types for type safety
type Brand<T, B> = T & { __brand: B };
export type UserId = Brand<string, 'UserId'>;
export type ProductId = Brand<string, 'ProductId'>;

// API response interfaces — generated from response shape
export interface ApiResponse<T> {
  data: T;
  meta?: { page: number; totalPages: number; totalItems: number };
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, string[]>;
}

// Domain entities
export interface User {
  id: UserId;
  email: string;
  name: string;
  avatarUrl: string | null;
  role: 'user' | 'admin';
  createdAt: string;
}

export interface Product {
  id: ProductId;
  title: string;
  description: string;
  price: number;
  images: string[];
  category: string;
  inStock: boolean;
}

// Discriminated union for async states
export type AsyncState<T> =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; data: T }
  | { status: 'error'; error: string };

// Type guard
export function isSuccess<T>(state: AsyncState<T>): state is { status: 'success'; data: T } {
  return state.status === 'success';
}
```

### Navigation Params Typing

```typescript
// navigation/types.ts
import { NativeStackScreenProps } from '@react-navigation/native-stack';
import { ProductId, UserId } from '@/types/api.types';

export type RootStackParamList = {
  Home: undefined;
  ProductDetail: { productId: ProductId };
  Profile: { userId: UserId };
  EditProfile: undefined;
  Settings: undefined;
};

// Screen props — use in each screen
export type ProductDetailProps = NativeStackScreenProps<RootStackParamList, 'ProductDetail'>;
export type ProfileProps = NativeStackScreenProps<RootStackParamList, 'Profile'>;

// Type-safe navigation hook
import { useNavigation } from '@react-navigation/native';
import { NativeStackNavigationProp } from '@react-navigation/native-stack';
export const useAppNavigation = () => useNavigation<NativeStackNavigationProp<RootStackParamList>>();
```
