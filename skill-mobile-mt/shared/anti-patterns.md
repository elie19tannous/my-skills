# Anti-Pattern Detection — Scan for Common Mistakes

> Auto-detect patterns that cause crashes, leaks, or store rejections.

## When to Use

- Before committing code
- During code review
- When instrumentation/observability code is added
- Before PR submission

---

## Detection Categories

### 1. PII (Personally Identifiable Information) Leaks

**CRITICAL** - Compliance risk (GDPR, CCPA, HIPAA)

```
PATTERNS TO DETECT:
❌ email / phone / ssn / credit_card / address / dob (date of birth)
❌ properties: ["user_email": user.email]
❌ tags: ["phone": user.phone]
❌ trackEvent("login", ["ssn": ssn])
❌ console.log("User: ${user.email}")

✅ SAFE ALTERNATIVES:
✓ properties: ["has_email": user.email != nil]
✓ tags: ["user_tier": "premium"]  // Enum, not PII
✓ trackEvent("login", ["user_type": userType])
✓ console.log("User: ${user.id}")  // UUID, not PII
```

**Auto-Fix Suggestion:**
```
Found: properties: ["email": user.email]
Fix → properties: ["has_email": user.email != nil]

Found: tags: ["user_id": userId]
Fix → tags: ["user_tier": user.subscription.tier]
```

---

### 2. High Cardinality

**CRITICAL** - Explodes storage, kills query performance

```
PATTERNS TO DETECT:
❌ user_id / session_id / uuid / timestamp / device_id as TAG values
❌ tags: ["user_id": "uuid-123"]  // Unlimited unique values
❌ tags: ["timestamp": Date.now()]  // Unbounded
❌ dimensions: ["request_id": requestId]  // High cardinality

✅ SAFE ALTERNATIVES:
✓ tags: ["user_tier": "free|premium|enterprise"]  // Low cardinality (3 values)
✓ tags: ["hour": date.getHours()]  // Low cardinality (0-23)
✓ dimensions: ["status_code": "200|404|500"]  // Low cardinality

RULE: Tags should have < 100 unique values over 30 days
```

**Auto-Fix Suggestion:**
```
Found: tags: ["user_id": userId]
Why bad: user_id has unlimited unique values → storage explosion
Fix →
  Option 1: Remove tag (use session correlation instead)
  Option 2: tags: ["user_tier": user.tier]  // Categorize
  Option 3: Move to context field (not a tag)
```

---

### 3. Unbounded Payloads

**HIGH** - Hits size limits, network cost

```
PATTERNS TO DETECT:
❌ Entire objects: extras: ["state": appState]
❌ Large arrays: extras: ["cart": cart.items]  // If items can be 1000+
❌ Unfiltered user input: extras: ["search_query": query]  // No length limit
❌ Nested objects: extras: ["user": user]  // Can be recursive

✅ SAFE ALTERNATIVES:
✓ extras: ["cart_item_count": cart.items.count]  // Aggregate
✓ extras: ["has_state": appState != nil]  // Boolean
✓ extras: ["search_query_length": query.length]  // Derived
✓ extras: ["user_tier": user.tier]  // Extract specific field

RULE: Extras should be < 10KB total per event
```

**Auto-Fix Suggestion:**
```
Found: extras: ["cart": cart]
Why bad: cart can be 1000+ items → 100KB+
Fix →
  extras: [
    "cart_item_count": cart.items.count,
    "cart_total": cart.total,
    "cart_has_promo": cart.promo != nil
  ]
```

---

### 4. Unstructured Logs

**MEDIUM** - Can't query or aggregate

```
PATTERNS TO DETECT:
❌ String interpolation: console.log(`User ${userId} failed`)
❌ Free-form text: log("Something went wrong")
❌ Mixed formats: log("Error: code=500, user=123")

✅ STRUCTURED ALTERNATIVES:
✓ logger.error("user_login_failed", { user_id: userId, reason: "timeout" })
✓ trackEvent("error", {
    error_type: "login_failed",
    user_id: userId,
    reason: "timeout"
  })
```

---

### 5. Sync Telemetry on Main Thread

**HIGH** - UI freezes

```
PATTERNS TO DETECT:
❌ trackEvent(...) in render / build / Composable
❌ captureError(...) without async / background
❌ flush() on main thread
❌ Network call inside instrumentation without queue

✅ SAFE ALTERNATIVES:
✓ trackEvent(...) → batches automatically (Sentry, Amplitude)
✓ captureError(...) → sends async (Firebase Crashlytics)
✓ Use background queue: DispatchQueue.global().async { ... }
✓ InteractionManager.runAfterInteractions(() => { ... })
```

---

### 6. Missing Context

**MEDIUM** - Events without correlation

```
REQUIRED CONTEXT FOR EVERY EVENT:
□ session_id (correlation)
□ screen (where it happened)
□ job_name (business goal: "checkout", "onboarding")
□ job_step (which step: "cart_review", "payment")
□ app_version (which release)

PATTERNS TO DETECT:
❌ trackEvent("button_tapped")  // What button? Which screen?
❌ captureError(error)  // No context

✅ COMPLETE EXAMPLES:
✓ trackEvent("button_tapped", {
    button: "checkout_submit",
    screen: "CartScreen",
    job_name: "checkout",
    job_step: "cart_review",
    session_id: sessionId,
    app_version: "1.2.3"
  })

✓ captureError(error, {
    screen: "PaymentScreen",
    job_name: "checkout",
    job_step: "payment",
    session_id: sessionId
  })
```

---

### 7. Mobile-Specific Anti-Patterns

#### React Native

```
❌ console.log in production (massive bottleneck)
❌ require() in render (re-executes every frame)
❌ Anonymous functions in FlatList renderItem
❌ Inline styles in render
❌ AsyncStorage for tokens (use SecureStore)

✅ CORRECT:
✓ __DEV__ && console.log(...)
✓ const Component = React.lazy(() => import(...))
✓ const renderItem = useCallback((item) => ..., [])
✓ const styles = StyleSheet.create({ ... })
✓ SecureStore.setItemAsync('token', token)
```

#### Flutter

```
❌ print() in production
❌ setState in build()
❌ Unbounded ListView (use ListView.builder)
❌ SharedPreferences for tokens (use flutter_secure_storage)

✅ CORRECT:
✓ kDebugMode && print(...)
✓ setState in event handlers, not build
✓ ListView.builder(itemCount: items.length, ...)
✓ await secureStorage.write(key: 'token', value: token)
```

#### iOS

```
❌ Force unwrap (!) without nil check
❌ Retain cycles ([self] in closures)
❌ UserDefaults for tokens (use Keychain)
❌ Heavy work on main thread

✅ CORRECT:
✓ guard let value = optional else { return }
✓ Capture [weak self] or [unowned self]
✓ KeychainWrapper.standard.set(token, forKey: "token")
✓ DispatchQueue.global().async { ... }
```

#### Android

```
❌ !! (force unwrap) without null check
❌ Memory leaks (Activity/Context references)
❌ SharedPreferences for tokens (use EncryptedSharedPreferences)
❌ AsyncTask (deprecated, use WorkManager)

✅ CORRECT:
✓ val value = optional ?: return
✓ Use ViewModel, avoid Activity refs in background
✓ EncryptedSharedPreferences for sensitive data
✓ WorkManager for background tasks
```

---

## Detection Workflow

```
PRE-COMMIT HOOK:
1. Scan all changed files for anti-patterns
2. Flag CRITICAL (block commit) vs HIGH (warn) vs MEDIUM (suggest)
3. Provide auto-fix suggestions
4. Run again after fix

DURING CODE REVIEW:
1. Agent scans PR diff
2. Comments on lines with anti-patterns
3. Suggests fixes inline
4. Links to this doc for explanation

CONTINUOUS:
1. Periodic full codebase scan
2. Generate report: violations by severity
3. Track trends (increasing/decreasing)
4. Alert if CRITICAL violations increase
```

---

## Severity Levels

| Severity | Impact | Action |
|----------|--------|--------|
| **CRITICAL** | PII leak, compliance risk | Block commit/PR |
| **HIGH** | Performance issue, crashes | Block commit, allow override |
| **MEDIUM** | Code smell, maintainability | Warn, suggest fix |
| **LOW** | Style, best practice | Suggest, don't block |

---

## Example: Full Detection Report

```
FILE: src/features/auth/LoginScreen.tsx
LINE 45: ❌ CRITICAL - PII Leak
  Found: trackEvent("login", { email: user.email })
  Fix:   trackEvent("login", { has_email: user.email != nil })
  Why:   Email is PII → GDPR/CCPA violation

LINE 67: ❌ HIGH - High Cardinality
  Found: tags: ["user_id": userId]
  Fix:   tags: ["user_tier": user.tier]
  Why:   user_id unbounded → storage explosion

LINE 89: ❌ MEDIUM - Missing Context
  Found: captureError(error)
  Fix:   captureError(error, { screen: "LoginScreen", job_name: "auth" })
  Why:   Can't correlate error without context

FILE: src/services/analytics.ts
LINE 23: ❌ CRITICAL - Sync Telemetry on Main Thread
  Found: trackEvent(...) in render()
  Fix:   Move to useEffect or InteractionManager.runAfterInteractions
  Why:   Blocks UI rendering → janky experience

Summary:
  2 CRITICAL (block)
  1 HIGH (warn)
  1 MEDIUM (suggest)
```

---

## Auto-Fix Templates

### PII → Boolean
```typescript
// Before
trackEvent("signup", { email: user.email })

// After
trackEvent("signup", { has_email: user.email !== undefined })
```

### High Cardinality → Enum
```typescript
// Before
tags: ["user_id": userId]

// After
tags: ["user_tier": user.subscription.tier]  // "free" | "premium" | "enterprise"
```

### Unbounded → Aggregate
```typescript
// Before
extras: ["cart": cart]

// After
extras: [
  "cart_item_count": cart.items.length,
  "cart_total_cents": cart.totalCents
]
```

### Missing Context → Complete
```typescript
// Before
trackEvent("button_tapped")

// After
trackEvent("button_tapped", {
  button: "checkout_submit",
  screen: "CartScreen",
  job_name: "checkout",
  job_step: "cart_review",
  session_id: sessionManager.currentSessionId,
  app_version: Constants.expoConfig?.version
})
```

---

## Integration with CI/CD

```bash
# Pre-commit hook
.git/hooks/pre-commit:
  npm run detect-anti-patterns -- --severity=critical --block

# PR Check
.github/workflows/pr-check.yml:
  - name: Detect Anti-Patterns
    run: npm run detect-anti-patterns -- --severity=high --report

# Weekly Scan
.github/workflows/weekly-scan.yml:
  schedule: cron('0 0 * * 0')  # Every Sunday
  run: npm run detect-anti-patterns -- --full-scan --report
```

---

## Learning from AI Tools

**Common mistakes AI tools make:**

| Tool | Mistake | Why |
|------|---------|-----|
| Cursor | Logs PII directly | Doesn't know GDPR/CCPA |
| Cline | Uses user_id as tag | Doesn't understand cardinality |
| Windsurf | Passes entire state objects | Doesn't check payload size |
| Devin | Sync telemetry on main thread | Doesn't profile performance impact |

**This skill avoids these by:**
- Scanning before commit
- Auto-suggesting fixes
- Blocking CRITICAL violations
- Teaching best practices
