# Bug Detection — Intelligent Auto Scanner

> Always loaded. All platforms.
> This file governs HOW the AI approaches every bug, error, crash, and issue.

---

## Platform Focus Rule

```
⛔ FOCUS on the DETECTED platform. Only cross-platform when the bug actually touches native code.

REACT NATIVE / EXPO:
  → Search: src/ (JS/TS) FIRST → only check android/ ios/ if native module involved
  → Scan: RN-specific patterns (useEffect, FlatList, bridge, Metro)
  → Go native ONLY IF: error from Logcat/Xcode (not Metro), native module crash, linking issue

FLUTTER:
  → Search: lib/ (Dart) FIRST → only check android/ ios/ if platform channel involved
  → Scan: Flutter-specific patterns (mounted, dispose, BuildContext, Widget tree)
  → Go native ONLY IF: error from native layer, MethodChannel crash, plugin issue

ANDROID NATIVE (Java/Kotlin):
  → Search: app/src/ FIRST → SKIP RN and Flutter patterns entirely
  → Scan: Android-specific (lifecycle, ViewModel, coroutines, Fragment, Compose)

iOS NATIVE (Swift/ObjC):
  → Search: *.swift FIRST → SKIP RN and Flutter patterns entirely
  → Scan: iOS-specific (optionals, @MainActor, Combine, Task, Codable)

FOR BUGS: if the bug trace crosses platform boundaries (e.g., RN JS error caused by
native module) → THEN investigate the native side too. Otherwise stay in platform.
```

---

## ⛔ STEP 0: Classify Error Type FIRST

```
BEFORE doing anything — classify what the user gave you:

USER INPUT                          → TYPE              → SEARCH STRATEGY
───────────────────────────────────────────────────────────────────────────
Paste stack trace / crash log       → RUNTIME CRASH     → Parse trace → find YOUR files → Grep function in src/
"Build fail / not compile"          → BUILD ERROR       → Config files FIRST (tsconfig/gradle/Podfile/pubspec) → then deps
"Type error / TS error"             → TYPE MISMATCH     → Find interface/type definition → find caller → fix mismatch
"API error / 401 / 500 / timeout"   → NETWORK ERROR     → Find API service file → check endpoint + headers + auth + .env
"Screen blank / white / not render" → RENDER ERROR      → Find component → check props + state + conditionals + data
"Navigation fail / route not found" → NAVIGATION ERROR  → Find navigator/router config → check route names + params
"Slow / lag / freeze / ANR"         → PERFORMANCE       → Profile first → read shared/performance-prediction.md
"Check issue / investigate / review"→ INVESTIGATION     → Read → search → analyze → REPORT (don't fix yet!)
"Native module error / link fail"   → NATIVE ERROR      → Check pod/gradle linking → then JS/Dart bridge → rebuild
"State wrong / data stale / race"   → STATE ERROR       → Find store/state → trace mutations → check async timing
"Memory leak / OOM"                 → MEMORY ERROR      → Find useEffect/listeners/subscriptions without cleanup

⛔ WRONG: Skip classification → guess fix from error message
✅ RIGHT: Classify → pick search strategy → search project → then analyze
```

---

## ⛔ STEP 1: Search Project BEFORE Diagnosing

```
⛔ NON-NEGOTIABLE: You MUST search project source code BEFORE suggesting ANYTHING.

1. EXTRACT from error message / user description:
   → File name or path mentioned in stack trace
   → Function name / class name / component name / module name
   → Line number (if available)
   → Package name (if dependency error)
   → HTTP status code / error code (if API error)

2. SEARCH PROJECT (Grep + Glob) — in this EXACT order:
   → Grep "[keyword]" src/                ← ALWAYS start here
   → Grep "[keyword]" lib/ app/           ← if src/ has no results
   → Glob "**/*[ComponentName]*"          ← find the actual file
   → Glob "**/*[screenName]*"             ← try screen name
   → Read the TOP 3-5 matched files       ← understand the real code

3. ONLY THEN proceed to analysis

⛔ If you have NOT run Grep/Glob yet → GO BACK AND DO IT NOW
⛔ NEVER say "the error is probably..." without having searched first

SEARCH PRIORITY ORDER:
  src/ → lib/ → app/ → components/ → screens/ → services/ → utils/
  → hooks/ → store/ → api/ → config/ → package.json → node_modules/ (LAST resort)

EXCEPTION — BUILD ERRORS search order is different:
  package.json / pubspec.yaml → tsconfig.json / build.gradle / Podfile
  → config files → THEN src/
```

---

## ⛔ STEP 2: Filter Noise from Logs

```
When user pastes a long error log, FILTER before analyzing:

IGNORE (noise — skip these lines):
  ✗ node_modules/* paths (framework internals, not your bug)
  ✗ React internals (__callReactNativeMicrotasks, MessageQueue, BatchedBridge)
  ✗ Engine frames (JavaScriptCore, Hermes, V8, ART, libc++)
  ✗ "Warning:" lines (unless directly related to the crash)
  ✗ "at Object.<anonymous>" without your file path
  ✗ "at Module._compile" / "at Function.Module._resolveFilename" (Node internals)
  ✗ Repeated/duplicate stack frames
  ✗ "console.log" output lines (unless user points to them)

FOCUS (signal — these lines matter):
  ✓ Lines with YOUR file paths (src/, app/, lib/, screens/, components/)
  ✓ "Error:", "TypeError:", "ReferenceError:", "SyntaxError:", "Unhandled"
  ✓ LAST "Caused by:" line (= actual root cause in Java/Android/Kotlin)
  ✓ FIRST frame with YOUR code in stack trace (= closest to crash)
  ✓ "undefined is not an object" + property name (= null pointer access)
  ✓ Error codes: ENOENT, ECONNREFUSED, ETIMEDOUT, E_MISSING_*
  ✓ HTTP status codes: 400, 401, 403, 404, 500, 502, 503

TECHNIQUE: Scan log → mark signal lines → ignore everything else → THEN analyze
```

---

## ⛔ STEP 3: Parse Stack Trace by Platform

```
REACT NATIVE (Metro / Hermes / JSC):
  → Line 1 after "Error:" or "TypeError:" = THE error description
  → Find FIRST "at" line with YOUR path (not node_modules/) = crash location
  → Read call chain bottom-to-top = how you got there
  → If "Component Stack:" present = which component tree caused it
  → Red Screen title = searchable error keyword → Grep it in src/

FLUTTER (Dart):
  → "The following [ExceptionType] was thrown" = error classification
  → "#0" frame = function closest to the crash
  → Find frames with YOUR package name (not package:flutter/)
  → "When the exception was thrown, this was the stack:" = full call chain
  → "RenderBox was not laid out" = layout issue → find the widget

iOS (Xcode Console / Crash Log):
  → "*** Terminating app due to uncaught exception" = crash start
  → "reason:" = human-readable cause
  → Find YOUR binary/module name in thread stack (not UIKit/Foundation)
  → Thread marked "CRASHED" or "*" = the crashing thread
  → "EXC_BAD_ACCESS" = null pointer / deallocated memory
  → "Signal: SIGABRT" = assertion failure → check the reason string

ANDROID (Logcat / ADB):
  → Filter by "E/" (Error level) or "FATAL EXCEPTION"
  → READ LAST "Caused by:" LINE = actual root cause (not the first one!)
  → Lines with YOUR package name (com.yourapp.*) = your code
  → "java.lang.NullPointerException" → find the null variable
  → "android.view.InflateException" → layout XML issue
  → "java.lang.OutOfMemoryError" → bitmap/image loading issue
```

---

## ⛔ STEP 4: Pick the Right Flow — 4 Different Modes

```
FIRST: Detect which mode the user is in:

  User has error log / stack trace     → MODE A: Error Analysis
  User says "fix this" / "debug this"  → MODE B: Fix Bug
  User says "check issue" / "investigate" with specific issue → MODE C: Investigate
  User describes symptoms vaguely / "check giùm" / "xem thử" /
    "sao nó lạ" / "not sure why" / "take a look" / pastes code
    without error / describes behavior → MODE D: Diagnostic Scan

  ⛔ If you can't tell which mode → DEFAULT TO MODE D (Diagnostic Scan)
  ⛔ NEVER default to Mode B (Fix Bug) — don't fix what you haven't scanned
```

### MODE A: Error Analysis (user has error log)
```
  ┌─────────────────────────────────────────────────────────┐
  │ 1. Filter noise from log (Step 2 above)                 │
  │ 2. Extract signal lines (YOUR paths, Error:, Caused by:)│
  │ 3. Classify error type (Step 0 above)                   │
  │ 4. Search project src/ for extracted keywords            │
  │ 5. Read matched files → trace root cause                │
  │ 6. Explain what's happening + propose fix with citation  │
  └─────────────────────────────────────────────────────────┘
```

### MODE B: Fix Bug (user knows the bug, wants a fix)
```
  ⛔ NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
  ⛔ 1 HYPOTHESIS → 1 MINIMAL CHANGE → VERIFY → if wrong, NEW hypothesis

  PHASE 0: CHECK RECENT CHANGES (git-aware — do this FIRST)
  ┌─────────────────────────────────────────────────────────┐
  │ ⚠️ PRE-CHECK: Is this a git project?                    │
  │    → Run: git rev-parse --is-inside-work-tree 2>/dev/null│
  │    → If NOT a git repo → SKIP Phase 0 → go to Phase 1  │
  │    → If git repo with no commits → SKIP Phase 0        │
  │    → If git repo with history → proceed below           │
  │                                                         │
  │ ⛔ BEFORE deep-diving into code, check what changed:    │
  │                                                         │
  │ 1. git log --oneline -10                                │
  │    → What were the last 10 commits?                     │
  │    → Does any commit message relate to the broken area? │
  │                                                         │
  │ 2. git diff HEAD~3 --name-only                          │
  │    → What files changed in last 3 commits?              │
  │    → Is the broken file among them?                     │
  │                                                         │
  │ 3. git diff HEAD~3 -- [broken_file]                     │
  │    → What EXACTLY changed in the broken file recently?  │
  │    → Was the bug INTRODUCED by a recent change?         │
  │                                                         │
  │ 4. git log --oneline --all -- [broken_file]             │
  │    → Full history of changes to this file               │
  │    → When was the last time someone touched it?         │
  │                                                         │
  │ WHY: 80%+ of bugs are caused by RECENT CHANGES.         │
  │ If the bug appeared after a specific commit, you already │
  │ know where to look — skip the rest of Phase 1.          │
  │                                                         │
  │ If git shows the file hasn't changed recently →          │
  │ the bug is environmental/data-driven → proceed Phase 1. │
  │                                                         │
  │ SKIP PHASE 0 WHEN:                                      │
  │  → Project has NO git (not initialized)                 │
  │  → git init done but no commits yet                     │
  │  → Brand new project (no meaningful history)            │
  │  → User says "this never worked" (not a regression)     │
  │  → Build error from fresh install (dependency issue)    │
  └─────────────────────────────────────────────────────────┘

  PHASE 1: ROOT CAUSE INVESTIGATION (mandatory — NO shortcuts)
  ┌─────────────────────────────────────────────────────────┐
  │ 1. Classify error type (Step 0)                         │
  │ 2. Search project src/ (Step 1) — MANDATORY             │
  │ 3. Read matched files → trace execution path            │
  │ 4. Classify reproduction:                               │
  │    → ALWAYS reproduces = deterministic → trace step by step│
  │    → SOMETIMES reproduces = race/timing → check async flow│
  │    → ONLY on [platform] = platform-specific → check native│
  │    → ONLY after [action] = state-dependent → trace state │
  │ 5. ROOT CAUSE: cite exact file:line + WHY it fails      │
  │    ⛔ "I think..." is NOT a root cause                  │
  │    ✅ "file:line does X, but Y is null because Z"       │
  └─────────────────────────────────────────────────────────┘

  PHASE 2: PATTERN ANALYSIS (find working example FIRST)
  ┌─────────────────────────────────────────────────────────┐
  │ 1. Search SAME codebase for similar working code:       │
  │    → Grep for similar pattern that WORKS in project     │
  │    → Find a screen/service/hook that does the SAME thing│
  │      but doesn't have this bug                          │
  │ 2. Compare broken code vs working code:                 │
  │    → List EVERY difference                              │
  │    → The bug is in the differences                      │
  │ 3. If no working example exists → skip to Phase 3       │
  └─────────────────────────────────────────────────────────┘

  PHASE 3: SINGLE HYPOTHESIS + MINIMAL FIX
  ┌─────────────────────────────────────────────────────────┐
  │ 1. Form ONE hypothesis based on root cause              │
  │ 2. Make the SMALLEST possible change to test it         │
  │    ⛔ NEVER stack multiple fixes at once                │
  │    ⛔ NEVER "fix it and also refactor nearby code"      │
  │    ✅ 1 change → verify → if wrong, revert → new idea  │
  │ 3. Verify the fix:                                      │
  │    → Does it fix ALL symptoms? (not just one)           │
  │    → Does it explain intermittent behavior?             │
  │    → Does it work on both platforms?                    │
  │ 4. Grep for side effects (other files using this)       │
  └─────────────────────────────────────────────────────────┘

  PHASE 4: DEFENSE IN DEPTH (after fix is verified)
  ┌─────────────────────────────────────────────────────────┐
  │ 1. Validate at EVERY layer data passes through:         │
  │    → Input validation (caller side)                     │
  │    → Function guard (callee side)                       │
  │    → State check (store/reducer/bloc)                   │
  │    → UI render guard (component level)                  │
  │ 2. Make the bug STRUCTURALLY IMPOSSIBLE to recur:       │
  │    → Add type guard / null check / validation           │
  │    → Not just "fix this one case" but prevent the class │
  │ 3. Cite: "Fix in [file:line] — [cause] — [why works]"  │
  └─────────────────────────────────────────────────────────┘

  🚩 RED FLAGS — if you catch yourself doing these, STOP:
  ┌─────────────────────────────────────────────────────────┐
  │ "Should work now"          → RUN IT. Don't claim.       │
  │ "I'm confident this fixes" → Confidence ≠ evidence.     │
  │ "Let me also clean up..."  → STOP. Fix bug only.        │
  │ "Probably a race condition"→ PROVE IT with code trace.   │
  │ "Try changing X to Y"      → Did you READ the file?     │
  │ Stacking 3+ changes at once→ Revert. 1 change at a time.│
  │ Same fix attempt 3+ times → STOP. Question architecture.│
  └─────────────────────────────────────────────────────────┘
```

### MODE C: Investigate (user has a specific issue to check)
```
  ┌─────────────────────────────────────────────────────────┐
  │ 1. Read issue description fully (don't skim)            │
  │ 2. Extract: affected feature, expected vs actual        │
  │ 3. Search project for the affected code area            │
  │ 4. Read the code → understand current implementation    │
  │ 5. REPORT findings — explain what's happening and WHY   │
  │ 6. ⛔ DO NOT FIX unless user explicitly asks            │
  │                                                         │
  │ Output format:                                          │
  │ "I found [component] at [file:line].                    │
  │  Current behavior: [what code does].                    │
  │  The issue is: [root cause].                            │
  │  Want me to fix it?"                                    │
  └─────────────────────────────────────────────────────────┘
```

### MODE D: Diagnostic Scan (user unsure / vague / "check this for me")
```
  ⚡ THIS IS THE MOST IMPORTANT MODE — handles the most common real scenario:
     User doesn't know what's wrong, just feels something is off,
     or wants AI to proactively check their code.

  ┌─────────────────────────────────────────────────────────┐
  │ 1. EXTRACT AREA from what user said/showed:             │
  │    → What screen / feature / module did they mention?   │
  │    → Did they paste code? → that IS the area            │
  │    → Did they describe behavior? → extract the feature  │
  │    → Did they say "this file" / "this screen"?          │
  │      → use the file they're looking at                  │
  │    → Still unclear? → ASK: "Which screen or feature     │
  │      should I check?"                                   │
  │                                                         │
  │ 2. SEARCH PROJECT for that area (broad search):         │
  │    → Grep "[feature name]" src/                         │
  │    → Glob "**/*[ScreenName]*" "**/*[featureName]*"      │
  │    → Read ALL matched files (not just 1 — scan widely)  │
  │    → Also read related: imports, hooks, services, store │
  │                                                         │
  │ 3. RUN FULL SCAN CHECKLIST on code you just read:       │
  │    → Walk through Step 5 checklist below SYSTEMATICALLY │
  │    → For EACH file, check:                              │
  │      □ Crash risks (null access, missing try/catch)     │
  │      □ Memory leaks (useEffect cleanup, listeners)      │
  │      □ Race conditions (async without guard)            │
  │      □ Security (tokens, secrets, unvalidated input)    │
  │      □ Performance (inline functions, missing memo)     │
  │      □ UX (missing states, accessibility)               │
  │    → Check data flow: API call → state → render         │
  │    → Check edge cases: empty data, error response,      │
  │      network offline, slow response                     │
  │                                                         │
  │ 4. REPORT (structured — ALWAYS do this):                │
  │    ┌───────────────────────────────────────────────┐    │
  │    │ Scanned: [N files] in [area/feature name]     │    │
  │    │                                               │    │
  │    │ 🔴 Issues found:                              │    │
  │    │   1. [SEVERITY] [file:line] — [description]   │    │
  │    │   2. [SEVERITY] [file:line] — [description]   │    │
  │    │                                               │    │
  │    │ 🟡 Suspicious (might be intentional):         │    │
  │    │   1. [file:line] — [what looks off]           │    │
  │    │                                               │    │
  │    │ ✅ Looks good:                                │    │
  │    │   - [aspect that's well-implemented]          │    │
  │    │                                               │    │
  │    │ Want me to fix issue #1? Or investigate        │    │
  │    │ [suspicious area] deeper?                     │    │
  │    └───────────────────────────────────────────────┘    │
  │                                                         │
  │ 5. WAIT for user decision — don't auto-fix              │
  │                                                         │
  │ ⛔ NEVER say "I don't see any issues" without having    │
  │    actually searched and read the project files          │
  │ ⛔ NEVER skip the scan — even if code "looks fine"      │
  │    at first glance, run the full checklist               │
  │ ⛔ NEVER suggest fixes before showing the scan report   │
  └─────────────────────────────────────────────────────────┘
```

---

## STEP 5: Scan Checklist (by severity)

### 1. Crash Risks (CRITICAL)
```
├── Force unwrap (! / !! / non-null assertion)
├── Array out of bounds
├── Unhandled null on API response
├── Missing try/catch on async ops
├── Missing error boundaries (RN)
├── Infinite recursion / render loop
└── Division by zero
```

### 2. Memory Leaks (HIGH)
```
RN:      useEffect without cleanup, listeners not removed, timers not cleared
Flutter: StreamSubscription/Controller not disposed, TextEditingController leak
iOS:     [weak self] missing in closures, NotificationCenter observers not removed
Android: Context leak in static ref, BroadcastReceiver not unregistered, Cursor not closed
```

### 3. Race Conditions (HIGH)
```
├── Button tappable during async op → add isSubmitting flag
├── setState after unmount → track mounted state / AbortController
├── Multiple 401 responses → queue token refresh (single retry)
├── Optimistic update without rollback → save previous state
└── Concurrent API calls modifying same state → mutex / queue
```

### 4. Security (HIGH)
```
├── Hardcoded API keys / secrets → .env / secure config
├── Tokens in AsyncStorage/SharedPrefs → SecureStore/Keychain
├── Sensitive data in console.log → strip before logging
├── Deep links with unvalidated params → validate + sanitize
└── Debug mode flags in release build → strip via build config
```

### 5. Performance (MEDIUM)
```
├── ScrollView for 50+ items → FlatList/ListView.builder/LazyColumn
├── Inline functions in render → useCallback/useMemo/const
├── Array index as key → stable unique ID
├── Large images unoptimized → resize, compress, cache, lazy load
├── Main thread blocking → offload to background
└── Missing pagination → add cursor/offset pagination
```

### 6. UX (MEDIUM)
```
├── Touch targets < 44pt (iOS) / 48dp (Android)
├── Missing loading / error / empty states
├── No keyboard dismiss on outside tap
├── Missing safe area handling (notch/island)
└── No accessibility labels (a11y)
```

---

## Report Format

```
🐛 [SEVERITY] — [file:line]
   Type:    [error classification from Step 0]
   Issue:   [description based on actual code read]
   Cause:   [root cause from project search, NOT generic guess]
   Impact:  [what breaks for the user]
   Fix:     [specific code change with before → after]
   Source:  [file:line where fix applies]
```
