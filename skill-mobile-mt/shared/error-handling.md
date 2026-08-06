# Error Handling — Resilient Mobile Code

> On-demand module. Loaded when implementing error handling, retry strategies, error boundaries, or user-facing error messages.
> Contains patterns that prevent crashes and provide graceful degradation.

---

## Error Type Hierarchy

### React Native / TypeScript

```typescript
// errors/AppError.ts

export class AppError extends Error {
  readonly code: string;
  readonly isRetryable: boolean;
  readonly statusCode?: number;

  constructor(message: string, code: string, isRetryable: boolean, statusCode?: number) {
    super(message);
    this.name = 'AppError';
    this.code = code;
    this.isRetryable = isRetryable;
    this.statusCode = statusCode;
  }
}

export class NetworkError extends AppError {
  constructor(message = 'Network connection failed') {
    super(message, 'NETWORK_ERROR', true);
  }
}

export class TimeoutError extends AppError {
  constructor(message = 'Request timed out') {
    super(message, 'TIMEOUT', true);
  }
}

export class AuthError extends AppError {
  constructor(message = 'Authentication failed', code = 'AUTH_ERROR') {
    super(message, code, false, 401);
  }
}

export class ForbiddenError extends AppError {
  constructor(message = 'Access denied') {
    super(message, 'FORBIDDEN', false, 403);
  }
}

export class ValidationError extends AppError {
  readonly fieldErrors: Record<string, string[]>;

  constructor(message: string, fieldErrors: Record<string, string[]> = {}) {
    super(message, 'VALIDATION', false, 422);
    this.fieldErrors = fieldErrors;
  }
}

export class ServerError extends AppError {
  constructor(message = 'Server error', statusCode = 500) {
    super(message, 'SERVER_ERROR', true, statusCode);
  }
}

export class NotFoundError extends AppError {
  constructor(message = 'Not found') {
    super(message, 'NOT_FOUND', false, 404);
  }
}

export class RateLimitError extends AppError {
  readonly retryAfter: number; // seconds

  constructor(retryAfter = 60) {
    super('Too many requests', 'RATE_LIMIT', true, 429);
    this.retryAfter = retryAfter;
  }
}
```

### Error Normalizer (from API responses)

```typescript
// errors/normalizeError.ts
import { AxiosError } from 'axios';

export function normalizeError(error: unknown): AppError {
  if (error instanceof AppError) return error;

  if (error instanceof AxiosError) {
    // No response — network error
    if (!error.response) {
      if (error.code === 'ECONNABORTED') return new TimeoutError();
      return new NetworkError();
    }

    const { status, data } = error.response;

    switch (status) {
      case 401: return new AuthError(data?.message);
      case 403: return new ForbiddenError(data?.message);
      case 404: return new NotFoundError(data?.message);
      case 422: return new ValidationError(data?.message, data?.errors);
      case 429: return new RateLimitError(parseInt(error.response.headers['retry-after'] || '60'));
      default:
        if (status >= 500) return new ServerError(data?.message, status);
        return new AppError(data?.message || 'Unknown error', 'UNKNOWN', false, status);
    }
  }

  if (error instanceof Error) {
    return new AppError(error.message, 'UNKNOWN', false);
  }

  return new AppError('An unexpected error occurred', 'UNKNOWN', false);
}
```

---

## User-Facing Error Messages

### Error Message Mapper

```typescript
// errors/errorMessages.ts

const userMessages: Record<string, string> = {
  NETWORK_ERROR: 'No internet connection. Please check your network and try again.',
  TIMEOUT: 'The request is taking too long. Please try again.',
  AUTH_ERROR: 'Your session has expired. Please log in again.',
  FORBIDDEN: "You don't have permission to do this.",
  NOT_FOUND: 'The item you are looking for no longer exists.',
  VALIDATION: 'Please check your input and try again.',
  SERVER_ERROR: 'Something went wrong on our end. Please try again later.',
  RATE_LIMIT: 'Too many requests. Please wait a moment and try again.',
  UNKNOWN: 'Something unexpected happened. Please try again.',
};

export function getUserMessage(error: AppError): string {
  return userMessages[error.code] ?? userMessages.UNKNOWN;
}

export function getRetryLabel(error: AppError): string | null {
  if (!error.isRetryable) return null;
  if (error instanceof RateLimitError) return `Retry in ${error.retryAfter}s`;
  return 'Try Again';
}
```

### Error Display Component

```typescript
// components/ErrorView.tsx
interface Props {
  error: AppError | Error;
  onRetry?: () => void;
}

export function ErrorView({ error, onRetry }: Props) {
  const appError = error instanceof AppError ? error : normalizeError(error);
  const message = getUserMessage(appError);
  const retryLabel = getRetryLabel(appError);

  return (
    <View style={styles.container}>
      <ErrorIcon size={48} color={colors.error} />
      <Text style={styles.message}>{message}</Text>
      {retryLabel && onRetry && (
        <Button title={retryLabel} onPress={onRetry} />
      )}
    </View>
  );
}
```

---

## Global Error Handling

### React Native — Error Boundary

```typescript
// components/ErrorBoundary.tsx
import React from 'react';

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends React.Component<
  { children: React.ReactNode; fallback?: React.ReactNode },
  State
> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    // Log to crash reporting service
    crashReporting.recordError(error, { componentStack: info.componentStack });
  }

  resetError = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      return this.props.fallback ?? (
        <View style={styles.center}>
          <Text>Something went wrong</Text>
          <Button title="Try Again" onPress={this.resetError} />
        </View>
      );
    }
    return this.props.children;
  }
}

// Wrap at app root:
// <ErrorBoundary>
//   <App />
// </ErrorBoundary>
```

### Unhandled Promise Rejection Handler

```typescript
// app/_layout.tsx or App.tsx — setup once at root
import { LogBox } from 'react-native';

// Capture unhandled promise rejections
if (__DEV__) {
  // Show in dev console
  LogBox.ignoreLogs(['Require cycle:']);
} else {
  // In production: log to crash service, don't crash the app
  const originalHandler = ErrorUtils.getGlobalHandler();
  ErrorUtils.setGlobalHandler((error, isFatal) => {
    crashReporting.recordError(error, { isFatal });
    if (!isFatal) return; // non-fatal: swallow
    originalHandler(error, isFatal); // fatal: let RN handle
  });
}
```

### Flutter — Global Error Handler

```dart
// main.dart
void main() {
  FlutterError.onError = (details) {
    FlutterError.presentError(details);
    // Log to Crashlytics/Sentry
    crashReporting.recordFlutterError(details);
  };

  PlatformDispatcher.instance.onError = (error, stack) {
    crashReporting.recordError(error, stack);
    return true; // handled
  };

  runApp(const MyApp());
}
```

---

## Retry Strategies

### Exponential Backoff with Jitter

```typescript
// utils/retry.ts
interface RetryOptions {
  maxRetries?: number;
  baseDelay?: number;
  maxDelay?: number;
  shouldRetry?: (error: AppError, attempt: number) => boolean;
  onRetry?: (attempt: number, delay: number) => void;
}

export async function withRetry<T>(
  fn: () => Promise<T>,
  options: RetryOptions = {}
): Promise<T> {
  const {
    maxRetries = 3,
    baseDelay = 1000,
    maxDelay = 30000,
    shouldRetry = (error) => error.isRetryable,
    onRetry,
  } = options;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      return await fn();
    } catch (error) {
      const appError = normalizeError(error);

      if (attempt === maxRetries || !shouldRetry(appError, attempt)) {
        throw appError;
      }

      // Exponential backoff: 1s, 2s, 4s + random jitter
      const delay = Math.min(
        baseDelay * Math.pow(2, attempt) + Math.random() * 500,
        maxDelay
      );

      onRetry?.(attempt + 1, delay);
      await new Promise(r => setTimeout(r, delay));
    }
  }

  throw new AppError('Max retries exceeded', 'MAX_RETRIES', false);
}

// Usage:
// const data = await withRetry(() => api.get('/products'), {
//   maxRetries: 3,
//   onRetry: (attempt) => console.log(`Retry #${attempt}`),
// });
```

### Rate Limit Handling

```typescript
// Automatic rate limit handling in API interceptor
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (error.response?.status === 429) {
      const retryAfter = parseInt(error.response.headers['retry-after'] || '5');
      await new Promise(r => setTimeout(r, retryAfter * 1000));
      return api(error.config!);
    }
    return Promise.reject(error);
  }
);
```

---

## Toast / Snackbar Error Notifications

```typescript
// hooks/useToast.ts
import { useCallback } from 'react';

type ToastType = 'success' | 'error' | 'warning' | 'info';

// Simple toast context (or use a library like react-native-toast-message)
export function useToast() {
  const show = useCallback((message: string, type: ToastType = 'info') => {
    // Use your preferred toast library
    Toast.show({ type, text1: message, visibilityTime: 4000 });
  }, []);

  const showError = useCallback((error: unknown) => {
    const appError = normalizeError(error);
    show(getUserMessage(appError), 'error');
  }, [show]);

  return { show, showError };
}

// Usage in mutation:
// const toast = useToast();
// try { await addToCart(product.id); toast.show('Added to cart', 'success'); }
// catch (e) { toast.showError(e); }
```

---

## Error Recovery Patterns

```
NETWORK ERROR → Show offline banner + retry button + queue mutations
AUTH ERROR (401) → Auto-refresh token → if fail → redirect to login
FORBIDDEN (403) → Show "Access denied" + navigate back
NOT FOUND (404) → Show "Not found" + navigate back
VALIDATION (422) → Highlight form fields with errors
SERVER ERROR (5xx) → Show retry button + log to crash service
RATE LIMIT (429) → Show countdown timer + auto-retry after delay
TIMEOUT → Retry with longer timeout (max 3 attempts)
```
