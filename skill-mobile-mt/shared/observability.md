# Mobile Observability — Sessions as the Fourth Pillar

> Sessions unify metrics, logs, and traces into a coherent user journey.

## The Four Pillars of Mobile Observability

```
Traditional: Metrics + Logs + Traces
Mobile:       Metrics + Logs + Traces + Sessions ← NEW

Sessions = The thread that ties everything together
```

Without sessions, you have isolated signals.
With sessions, you have a complete user story.

---

## Session Model

### Session Lifecycle

```typescript
interface MobileSession {
  // Identity
  session_id: string;           // Unique ID for this session
  user_id?: string;             // Authenticated user (nullable)
  device_id: string;            // Stable device identifier

  // Timing
  started_at: number;           // Unix timestamp (ms)
  ended_at?: number;            // Null if still active
  duration_ms?: number;         // Calculated on end

  // Mobile Context
  app_version: string;          // "2.1.3"
  build_number: string;         // "42"
  platform: 'ios' | 'android';
  os_version: string;           // "17.2", "14"
  device_model: string;         // "iPhone 15 Pro", "Pixel 8"

  // Network
  network_type: 'wifi' | '5g' | '4g' | '3g' | 'offline';
  carrier?: string;

  // State
  foreground_time_ms: number;   // Time app was visible
  background_time_ms: number;   // Time app was in background
  crash_count: number;          // Crashes in this session

  // Correlation
  previous_session_id?: string; // Chain sessions
  acquisition_channel?: string; // How user arrived (deeplink, push, organic)
}
```

### Session Events

```typescript
type SessionEvent =
  | 'session_start'
  | 'session_end'
  | 'session_pause'      // App backgrounded
  | 'session_resume'     // App foregrounded
  | 'session_crash'      // Crash detected
  | 'session_timeout';   // Inactive for N minutes

// Session starts when app becomes active
// Session ends when app is killed or inactive > 30 minutes
// Background time > 30 minutes = new session on foreground
```

---

## Implementation Pattern

### React Native / Expo

```typescript
// src/observability/session.ts
import { AppState, AppStateStatus } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { nanoid } from 'nanoid/non-secure';
import DeviceInfo from 'react-native-device-info';
import NetInfo from '@react-native-community/netinfo';

class SessionManager {
  private currentSession: MobileSession | null = null;
  private appStateSubscription: any = null;
  private backgroundTimer: NodeJS.Timeout | null = null;
  private readonly SESSION_TIMEOUT_MS = 30 * 60 * 1000; // 30 minutes

  async startSession(): Promise<MobileSession> {
    const previousSessionId = await this.getPreviousSessionId();
    const netInfo = await NetInfo.fetch();

    this.currentSession = {
      session_id: nanoid(),
      device_id: await DeviceInfo.getUniqueId(),
      app_version: DeviceInfo.getVersion(),
      build_number: DeviceInfo.getBuildNumber(),
      platform: Platform.OS as 'ios' | 'android',
      os_version: DeviceInfo.getSystemVersion(),
      device_model: DeviceInfo.getModel(),
      network_type: this.mapNetworkType(netInfo.type),
      started_at: Date.now(),
      foreground_time_ms: 0,
      background_time_ms: 0,
      crash_count: 0,
      previous_session_id: previousSessionId,
    };

    await this.saveSession(this.currentSession);
    this.trackEvent('session_start', this.currentSession);
    this.observeAppState();

    return this.currentSession;
  }

  private observeAppState() {
    let lastActiveTime = Date.now();

    this.appStateSubscription = AppState.addEventListener(
      'change',
      async (nextState: AppStateStatus) => {
        if (nextState === 'background' || nextState === 'inactive') {
          // App going to background
          this.currentSession!.foreground_time_ms += Date.now() - lastActiveTime;
          this.trackEvent('session_pause', { session_id: this.currentSession!.session_id });

          // Set timeout for new session on resume
          this.backgroundTimer = setTimeout(() => {
            this.markSessionExpired();
          }, this.SESSION_TIMEOUT_MS);

        } else if (nextState === 'active') {
          // App returning to foreground
          if (this.backgroundTimer) clearTimeout(this.backgroundTimer);

          if (this.isSessionExpired()) {
            await this.endSession('session_timeout');
            await this.startSession();
          } else {
            const backgroundStart = lastActiveTime;
            lastActiveTime = Date.now();
            this.currentSession!.background_time_ms += lastActiveTime - backgroundStart;
            this.trackEvent('session_resume', { session_id: this.currentSession!.session_id });
          }
        }
      }
    );
  }

  async endSession(reason: SessionEvent = 'session_end') {
    if (!this.currentSession) return;

    this.currentSession.ended_at = Date.now();
    this.currentSession.duration_ms =
      this.currentSession.ended_at - this.currentSession.started_at;

    this.trackEvent(reason, this.currentSession);
    await this.savePreviousSessionId(this.currentSession.session_id);
    this.currentSession = null;
  }

  getContext(): Record<string, string> {
    if (!this.currentSession) return {};
    return {
      session_id: this.currentSession.session_id,
      device_id: this.currentSession.device_id,
      app_version: this.currentSession.app_version,
      platform: this.currentSession.platform,
    };
  }

  // Inject session context into every log/metric/trace
  enrichEvent(event: Record<string, any>): Record<string, any> {
    return {
      ...event,
      ...this.getContext(),
      timestamp: Date.now(),
    };
  }
}

export const sessionManager = new SessionManager();
```

### Flutter (Dart)

```dart
// lib/observability/session_manager.dart
import 'dart:io';
import 'package:device_info_plus/device_info_plus.dart';
import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:uuid/uuid.dart';

class SessionManager {
  static final SessionManager _instance = SessionManager._internal();
  factory SessionManager() => _instance;
  SessionManager._internal();

  MobileSession? _currentSession;
  final _uuid = const Uuid();

  Future<MobileSession> startSession() async {
    final prefs = await SharedPreferences.getInstance();
    final previousId = prefs.getString('last_session_id');
    final deviceInfo = DeviceInfoPlugin();
    final connectivity = await Connectivity().checkConnectivity();

    String deviceId = '';
    String osVersion = '';
    String deviceModel = '';

    if (Platform.isIOS) {
      final iosInfo = await deviceInfo.iosInfo;
      deviceId = iosInfo.identifierForVendor ?? '';
      osVersion = iosInfo.systemVersion;
      deviceModel = iosInfo.model;
    } else if (Platform.isAndroid) {
      final androidInfo = await deviceInfo.androidInfo;
      deviceId = androidInfo.id;
      osVersion = androidInfo.version.release;
      deviceModel = androidInfo.model;
    }

    _currentSession = MobileSession(
      sessionId: _uuid.v4(),
      deviceId: deviceId,
      appVersion: '1.0.0', // From package_info_plus
      buildNumber: '1',
      platform: Platform.isIOS ? 'ios' : 'android',
      osVersion: osVersion,
      deviceModel: deviceModel,
      networkType: _mapConnectivity(connectivity),
      startedAt: DateTime.now().millisecondsSinceEpoch,
      previousSessionId: previousId,
    );

    _trackEvent('session_start', _currentSession!.toMap());
    return _currentSession!;
  }

  Map<String, String> getContext() {
    final session = _currentSession;
    if (session == null) return {};
    return {
      'session_id': session.sessionId,
      'device_id': session.deviceId,
      'app_version': session.appVersion,
      'platform': session.platform,
    };
  }

  // Call this before every log, metric, or trace
  Map<String, dynamic> enrichEvent(Map<String, dynamic> event) {
    return {
      ...event,
      ...getContext(),
      'timestamp': DateTime.now().millisecondsSinceEpoch,
    };
  }
}
```

---

## Unified Observability Stack

### Signal Unification

```typescript
// Every signal (metric/log/trace) MUST include session context

// ❌ WRONG: Missing session context
logger.info('User logged in');
metrics.increment('login_success');
tracer.startSpan('auth.login');

// ✅ CORRECT: Session context injected
const context = sessionManager.getContext();

logger.info('User logged in', { ...context, method: 'email' });
metrics.increment('login_success', { ...context });
tracer.startSpan('auth.login', { attributes: context });
```

### Correlation Architecture

```
User Journey (Session Layer)
│
├── Screen: LoginScreen (session_id: abc123)
│   ├── Metric: screen_view {session_id: abc123, screen: "login"}
│   ├── Log: "Attempting login" {session_id: abc123}
│   └── Trace: auth.login {session_id: abc123}
│       ├── span: validate_email {duration: 2ms}
│       ├── span: api.call {duration: 234ms}
│       └── span: save_token {duration: 5ms}
│
└── Screen: HomeScreen (session_id: abc123)
    ├── Metric: screen_view {session_id: abc123, screen: "home"}
    ├── Log: "Feed loaded" {session_id: abc123, items: 20}
    └── Trace: feed.load {session_id: abc123}

QUERY POWER: "Show me all logs, metrics, and traces for session abc123"
→ Complete user journey reconstruction
```

---

## Instrumentation Patterns

### Screen Tracking

```typescript
// ✅ Context-rich screen tracking
function trackScreen(screenName: string, params?: Record<string, string>) {
  const event = sessionManager.enrichEvent({
    event: 'screen_view',
    screen_name: screenName,
    screen_class: screenName,
    // Avoid PII — see anti-patterns.md
    ...params,
  });

  analytics.track(event);
  logger.debug('Screen viewed', event);
}

// Usage
trackScreen('ProductDetail', { product_id: product.id, category: product.category });
// NOT: trackScreen('ProductDetail', { user_email: user.email }); ← PII leak
```

### API Call Tracking

```typescript
// ✅ Full API instrumentation
async function trackedRequest(
  method: string,
  url: string,
  options?: RequestInit
): Promise<Response> {
  const traceId = nanoid();
  const startTime = Date.now();
  const context = sessionManager.getContext();

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        ...options?.headers,
        'X-Trace-Id': traceId,    // Correlate with backend
        'X-Session-Id': context.session_id,
      },
    });

    const duration = Date.now() - startTime;

    metrics.histogram('api.duration', duration, {
      ...context,
      method,
      endpoint: sanitizeUrl(url),  // Remove user IDs from URL
      status: String(response.status),
      success: String(response.ok),
    });

    logger.info('API call completed', {
      ...context,
      trace_id: traceId,
      method,
      endpoint: sanitizeUrl(url),
      status: response.status,
      duration_ms: duration,
    });

    return response;

  } catch (error) {
    metrics.increment('api.error', {
      ...context,
      method,
      endpoint: sanitizeUrl(url),
      error_type: error instanceof Error ? error.name : 'unknown',
    });

    logger.error('API call failed', {
      ...context,
      trace_id: traceId,
      method,
      endpoint: sanitizeUrl(url),
      error: error instanceof Error ? error.message : String(error),
    });

    throw error;
  }
}

function sanitizeUrl(url: string): string {
  // Remove UUIDs and numeric IDs from URLs
  return url
    .replace(/\/[0-9a-f-]{36}/g, '/:id')    // UUIDs
    .replace(/\/\d+/g, '/:id')               // Numeric IDs
    .replace(/\?.*$/, '');                    // Query params
}
```

### Error Tracking

```typescript
// ✅ Crash reporting with session context
function trackError(error: Error, context?: Record<string, string>) {
  const sessionContext = sessionManager.getContext();

  // Update session crash count
  sessionManager.incrementCrashCount();

  crashReporter.captureException(error, {
    tags: {
      ...sessionContext,
      ...context,
    },
    extra: {
      crash_count: sessionManager.getCrashCount(),
      // Breadcrumbs from session
      recent_screens: sessionManager.getRecentScreens(),
    },
  });

  logger.error('Application error', {
    ...sessionContext,
    error_name: error.name,
    error_message: error.message,
    // No stack traces in production logs (can contain file paths with PII)
    stack_hash: hashString(error.stack ?? ''),
  });
}

// Global error boundary (React Native)
import { ErrorBoundary } from 'react-error-boundary';

function GlobalErrorBoundary({ children }: { children: React.ReactNode }) {
  return (
    <ErrorBoundary
      onError={(error, info) => {
        trackError(error, { component: info.componentStack?.split('\n')[1] ?? 'unknown' });
      }}
      fallback={<ErrorScreen />}
    >
      {children}
    </ErrorBoundary>
  );
}
```

### Performance Tracking

```typescript
// ✅ Frame rate and rendering monitoring
import { PerformanceObserver } from 'react-native';

function trackRenderPerformance(componentName: string) {
  return function <T extends React.ComponentType<any>>(WrappedComponent: T): T {
    const displayName = componentName || WrappedComponent.displayName || 'Unknown';

    function TrackedComponent(props: React.ComponentProps<T>) {
      const renderStart = useRef(Date.now());
      const context = sessionManager.getContext();

      useEffect(() => {
        const renderDuration = Date.now() - renderStart.current;

        if (renderDuration > 16) {  // > 1 frame at 60fps
          metrics.histogram('render.duration', renderDuration, {
            ...context,
            component: displayName,
            slow: String(renderDuration > 100),  // > 6 frames
          });
        }
      }, []);

      return <WrappedComponent {...props} />;
    }

    TrackedComponent.displayName = `Tracked(${displayName})`;
    return TrackedComponent as T;
  };
}

// Usage
export default trackRenderPerformance('ProductList')(ProductListComponent);
```

---

## Alerting Based on Sessions

### Alert Patterns

```typescript
// Alert: Crash rate spike
if (session.crash_count > 0) {
  alerts.trigger('crash_detected', {
    session_id: session.session_id,
    app_version: session.app_version,
    crash_count: session.crash_count,
    platform: session.platform,
    os_version: session.os_version,
  });
}

// Alert: Long session with no screen changes (app hung?)
if (session.duration_ms > 10 * 60 * 1000 && getScreenCount() <= 1) {
  alerts.trigger('potential_freeze', {
    session_id: session.session_id,
    duration_ms: session.duration_ms,
    screen_count: getScreenCount(),
  });
}

// Alert: High background time (battery killer?)
const backgroundRatio =
  session.background_time_ms / session.duration_ms;
if (backgroundRatio > 0.5) {
  logger.warn('High background activity', {
    session_id: session.session_id,
    background_ratio: backgroundRatio.toFixed(2),
    background_ms: session.background_time_ms,
  });
}
```

### Dashboard Queries

```sql
-- Session-based queries (example for any analytics platform)

-- Active sessions by platform
SELECT platform, COUNT(DISTINCT session_id) as active_sessions
FROM sessions
WHERE started_at > NOW() - INTERVAL '1 hour'
GROUP BY platform;

-- Crash rate by app version
SELECT app_version,
  COUNT(DISTINCT session_id) as total_sessions,
  SUM(crash_count) as total_crashes,
  ROUND(SUM(crash_count)::numeric / COUNT(DISTINCT session_id) * 100, 2) as crash_rate_pct
FROM sessions
GROUP BY app_version
ORDER BY app_version DESC;

-- Session duration distribution
SELECT
  platform,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY duration_ms) as p50_ms,
  PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY duration_ms) as p90_ms,
  PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY duration_ms) as p99_ms
FROM sessions
WHERE duration_ms IS NOT NULL
GROUP BY platform;

-- Network type vs error rate
SELECT s.network_type,
  COUNT(DISTINCT s.session_id) as sessions,
  COUNT(e.error_id) as errors,
  ROUND(COUNT(e.error_id)::numeric / COUNT(DISTINCT s.session_id), 2) as errors_per_session
FROM sessions s
LEFT JOIN errors e USING (session_id)
GROUP BY s.network_type;
```

---

## Context Requirements Checklist

Every instrumented event MUST include:

```
□ session_id      (links everything together)
□ device_id       (user journey across sessions)
□ app_version     (for regression detection)
□ platform        (iOS vs Android differences)
□ timestamp       (for timeline reconstruction)

OPTIONAL but valuable:
□ screen_name     (where in the app)
□ network_type    (wifi vs cellular behavior differences)
□ os_version      (OS-specific bug detection)
□ user_tier       (free vs premium behavior)
```

Events MUST NOT include:
```
✗ user_email      (PII — see anti-patterns.md)
✗ user_name       (PII)
✗ phone_number    (PII)
✗ raw_user_id     (replace with hashed or session_id)
✗ full URL params (may contain tokens)
✗ auth_token      (security risk)
```

---

## Observability Stack Recommendations

### React Native

| Tool | Purpose | Integration |
|------|---------|-------------|
| **Sentry** | Crash reporting + error tracking | `@sentry/react-native` |
| **Datadog RUM** | Real User Monitoring | `@datadog/mobile-react-native` |
| **Firebase Crashlytics** | Crash reporting (free) | `@react-native-firebase/crashlytics` |
| **Firebase Analytics** | Event tracking (free) | `@react-native-firebase/analytics` |
| **Segment** | CDP (routes to other tools) | `@segment/analytics-react-native` |
| **New Relic Mobile** | Full observability | `newrelic-react-native-agent` |

### Flutter

| Tool | Purpose | Integration |
|------|---------|-------------|
| **Sentry** | Crash reporting + error tracking | `sentry_flutter` |
| **Firebase Crashlytics** | Crash reporting (free) | `firebase_crashlytics` |
| **Firebase Analytics** | Event tracking (free) | `firebase_analytics` |
| **Datadog** | Full observability | `datadog_flutter_plugin` |
| **Segment** | CDP | `analytics` (Flutter) |
| **OpenTelemetry** | Vendor-neutral | `opentelemetry_dart` |

---

## Session-Aware Testing

```typescript
// tests/observability/session.test.ts
describe('SessionManager', () => {
  it('enriches all events with session context', () => {
    const session = await sessionManager.startSession();

    const rawEvent = { event: 'button_tap', button: 'subscribe' };
    const enriched = sessionManager.enrichEvent(rawEvent);

    expect(enriched).toMatchObject({
      event: 'button_tap',
      button: 'subscribe',
      session_id: session.session_id,
      device_id: expect.any(String),
      app_version: expect.any(String),
      platform: expect.stringMatching(/^(ios|android)$/),
      timestamp: expect.any(Number),
    });
  });

  it('starts a new session after 30 min background', async () => {
    const session1 = await sessionManager.startSession();

    // Simulate 31 minutes in background
    jest.advanceTimersByTime(31 * 60 * 1000);

    // App comes back to foreground
    simulateAppState('active');

    const session2 = sessionManager.getCurrentSession();
    expect(session2.session_id).not.toBe(session1.session_id);
    expect(session2.previous_session_id).toBe(session1.session_id);
  });
});
```

---

## Summary

**Sessions are the fourth pillar because:**
1. **Metrics** tell you WHAT happened (count, duration, rate)
2. **Logs** tell you WHAT was happening at a moment (details)
3. **Traces** tell you HOW it happened (call chain)
4. **Sessions** tell you WHO experienced it and WHEN in their journey

Without sessions:
- "Error spike at 2pm" → Can't tell if 1 user or 1000 users
- "API timeout" → Can't tell if it always happens or only on cellular

With sessions:
- "Error spike at 2pm" → 47 unique sessions, all on iOS 17.1, v2.1.3
- "API timeout" → 89% occur on 3G sessions, not WiFi
