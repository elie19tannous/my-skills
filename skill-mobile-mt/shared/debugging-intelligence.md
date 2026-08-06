# Debugging Intelligence — Deep Pattern Database

> On-demand. Load when: complex bugs, long stack traces, issue investigation, multi-error scenarios.
> This file contains 30+ real error patterns with EXACT search strategies.

---

## Platform Focus Rule

```
⛔ ONLY use error patterns for the DETECTED platform. Don't scan all categories.

REACT NATIVE → Category A (RN crashes) + B + C + D + E + F1
FLUTTER      → Category A2 (Flutter crashes) + B4 + C + D + F3
iOS NATIVE   → Category A3 (iOS crashes) + C + D + F1
ANDROID      → Category A4 (Android crashes) + B3 + C + D + F2

Cross-platform categories (B build, C network, D state, E navigation):
  → Use the platform-specific SEARCH strategy within each category
  → e.g., C1 Network error: RN → check axios/fetch, Flutter → check http/dio,
    iOS → check URLSession, Android → check Retrofit/OkHttp

CROSS-REFERENCE native ONLY WHEN:
  → Stack trace exits JS/Dart layer into native (Java/Swift/ObjC)
  → Error message is from native runtime (not Metro/Dart VM)
  → User explicitly says the bug is in native code
```

---

## Error Pattern Database

### Category A: React Native Runtime Crashes

#### A1. "undefined is not an object (evaluating 'X.Y')"
```
CAUSE:  X is null/undefined when accessing property Y
SEARCH: Grep "X" in src/ → find where X is defined/assigned → check null cases
COMMON:
  - API response missing field → data?.field instead of data.field
  - Navigation params undefined → route.params?.id
  - State not initialized → useState(null) accessed before set
  - Unmounted component accessing state
FIX:    Add optional chaining (X?.Y) OR null guard (if (!X) return)
VERIFY: Check ALL places X is used (grep) → apply same fix
```

#### A2. "Cannot read property 'X' of undefined" / "Cannot read properties of null"
```
CAUSE:  Same as A1 (V8/Hermes variant)
SEARCH: Same strategy — Grep the variable name in src/
NOTE:   In Hermes, the variable name may not be in error → check stack trace for file:line
```

#### A3. "TypeError: X is not a function"
```
CAUSE:  X is imported wrong, or the object doesn't have method X
SEARCH: Grep "X" in src/ → check the import statement → check the module's exports
COMMON:
  - Default vs named import mismatch: import X vs import { X }
  - Calling method on wrong object: obj.X() but X is on obj.child
  - Library updated with breaking API change
  - Circular import making X undefined at call time
FIX:    Fix import OR check object shape with console.log(typeof X)
```

#### A4. "Invariant Violation: Element type is invalid"
```
CAUSE:  React component imported incorrectly (got undefined instead of component)
SEARCH: Find the component import → check its source file's export
COMMON:
  - export default vs export { Component } mismatch
  - File path typo in import
  - Circular import (A imports B imports A → one becomes undefined)
  - Re-exporting from index.ts but forgot to add new component
FIX:    Fix export/import → clear Metro cache → restart
```

#### A5. "Maximum call stack size exceeded"
```
CAUSE:  Infinite loop or infinite recursion
SEARCH: Find the function from stack trace → check for:
  - useEffect with wrong dependency array (causes infinite re-render)
  - State update inside render body (not in handler/effect)
  - Recursive function without base case
  - Component renders itself without stop condition
COMMON:
  - useEffect(() => { setState(x) }, [x]) ← x changes → effect runs → sets x → loop
  - componentDidUpdate without shouldComponentUpdate check
FIX:    Fix dependency array OR add base case OR memoize
```

#### A6. "VirtualizedList: You have a large list that is slow to update"
```
CAUSE:  FlatList re-rendering entire list on every state change
SEARCH: Find the FlatList component → check renderItem + keyExtractor
COMMON:
  - Missing keyExtractor (uses index by default → full re-render)
  - renderItem creates new function/object every render
  - Data source reference changes on every render
FIX:
  → Add keyExtractor with stable unique ID
  → Wrap renderItem in useCallback
  → Memoize list item component with React.memo
  → Use getItemLayout if fixed height
```

#### A7. "Unhandled promise rejection"
```
CAUSE:  Async function threw error without try/catch
SEARCH: Find the async function from stack trace → check error handling
COMMON:
  - fetch/axios call without try/catch
  - Promise chain without .catch()
  - async function in useEffect without error handler
FIX:    Wrap in try/catch → show user-facing error → log for debugging
```

---

### Category A2: Flutter Runtime Crashes

#### A2-1. "setState() called after dispose()"
```
CAUSE:  Async callback completes after widget unmounted, calls setState
SEARCH: Find the widget from stack trace → check async callbacks
COMMON:
  - Future.then() callback without mounted check
  - Timer callback after screen popped
  - Stream listener not cancelled in dispose()
FIX:    Add `if (!mounted) return;` before EVERY setState after async gap
VERIFY: Check ALL async callbacks in the widget → add mounted guard
```

#### A2-2. "RenderFlex overflowed by X pixels"
```
CAUSE:  Child widget exceeds parent constraint
SEARCH: Find the widget from error → check its parent Row/Column layout
COMMON:
  - Text too long in Row without Flexible/Expanded
  - Image with fixed size in constrained container
  - Column inside Column without Expanded
FIX:    Wrap with Flexible/Expanded OR add overflow: TextOverflow.ellipsis
        OR wrap with SingleChildScrollView
```

#### A2-3. "A build function returned null"
```
CAUSE:  Switch/if in build() doesn't cover all cases → returns null
SEARCH: Find the widget's build method → check conditional branches
COMMON:
  - Enum switch without default case
  - if/else if without final else
  - Late variable not initialized before build
FIX:    Ensure ALL branches return a Widget, add default/else case
```

#### A2-4. "Looking up a deactivated widget's ancestor is unsafe"
```
CAUSE:  Using BuildContext after async gap (context may be deactivated)
SEARCH: Find the async function → check context usage after await
COMMON:
  - Navigator.of(context).pop() after await
  - ScaffoldMessenger.of(context) after async call
  - showDialog after await
FIX:    Store navigator/messenger BEFORE await, OR check mounted after await
VERIFY: Check ALL context usage after await in the widget
```

#### A2-5. "type 'Null' is not a subtype of type 'X'"
```
CAUSE:  Null value assigned to non-nullable variable (sound null safety violation)
SEARCH: Find the variable from stack trace → trace where null comes from
COMMON:
  - JSON parsing: map['key'] as String (but key is absent → null)
  - API response missing expected field
  - Type cast: (object as String) when object is null
FIX:    Use null-safe parsing: map['key'] as String? ?? 'default'
        OR fix fromJson factory to handle missing fields
```

#### A2-6. "Unhandled Exception: Bad state: Stream has already been listened to"
```
CAUSE:  Single-subscription Stream listened to more than once
SEARCH: Find the StreamController → check how many widgets listen to it
COMMON:
  - StreamController (default = single-subscription) used by multiple widgets
  - Hot reload re-subscribes without cancelling previous
FIX:    Use StreamController.broadcast() for multiple listeners
        OR ensure single listener with StreamSubscription tracking
```

---

### Category A3: iOS Swift Runtime Crashes

#### A3-1. "Fatal error: Unexpectedly found nil while unwrapping an Optional value"
```
CAUSE:  Force unwrap (!) on nil value
SEARCH: Find file:line from crash log → check the ! operator
COMMON:
  - IBOutlet not connected in storyboard
  - UserDefaults.string(forKey:)! for missing key
  - as! cast that fails
  - Implicitly unwrapped optional (!) on property not set before access
FIX:    Replace ! with guard let / if let / ?? default
VERIFY: Grep "!" in the file → check ALL force unwraps
```

#### A3-2. "EXC_BAD_ACCESS (code=1/2)" / SIGSEGV
```
CAUSE:  Accessing deallocated memory (dangling pointer / use-after-free)
SEARCH: Enable Zombie Objects in Xcode → reproduce → find deallocated object
COMMON:
  - Strong reference to self in closure → VC deallocated but closure keeps pointer
  - Accessing unowned self after object deallocated
  - Core Data object accessed from wrong thread
  - C/ObjC interop with wrong pointer management
FIX:    Use [weak self] instead of [unowned self] if lifetime uncertain
        Use perform() for Core Data thread safety
```

#### A3-3. "Thread 1: signal SIGABRT" / "NSInternalInconsistencyException"
```
CAUSE:  Assertion failure in UIKit/Foundation
SEARCH: Read "reason:" line in crash log → search for that assertion
COMMON:
  - UITableView: batch update mismatch (insert/delete count != data count)
  - Storyboard: IBOutlet or segue identifier not found
  - Auto Layout: conflicting constraints
  - Collection view: invalid number of items in section
FIX:    Fix data source consistency → diffable data source recommended
        Fix storyboard connections → check identifier spelling
```

#### A3-4. "Modifications to the layout engine must not be performed from a background thread"
```
CAUSE:  UI update called from background thread
SEARCH: Find the code from stack trace → check which queue it runs on
COMMON:
  - URLSession completion handler (runs on background by default)
  - NotificationCenter observer callback
  - DispatchQueue.global() { self.label.text = "..." }
FIX:    Wrap UI updates: DispatchQueue.main.async { ... }
        OR use @MainActor on the function
        OR use MainActor.run { ... } in async context
```

#### A3-5. "Cannot decode" / "DecodingError.keyNotFound"
```
CAUSE:  JSON response doesn't match Codable struct
SEARCH: Find the Codable struct → compare with actual API response
COMMON:
  - Backend added new required field → old Codable struct missing it
  - Backend returns null for field marked as non-optional
  - Backend changed field type (string → number)
  - Snake_case vs camelCase mismatch without CodingKeys
FIX:    Mark uncertain fields as Optional → provide CodingKeys if naming differs
        Use custom init(from:) with try? for graceful degradation
```

---

### Category A4: Android Kotlin Runtime Crashes

#### A4-1. "java.lang.NullPointerException" / "KotlinNullPointerException"
```
CAUSE:  Null access — !! force unwrap, Java interop, or platform type
SEARCH: Find file:line from stack trace → check the null source
COMMON:
  - intent.extras!!.getString("key") → extras is null from deep link
  - findViewById<TextView>(R.id.title)!! → wrong layout inflated
  - Java library returning null where Kotlin expects non-null (platform types)
  - binding.textView after onDestroyView (binding is null)
FIX:    Replace !! with ?. ?: default OR requireNotNull with message
        Use _binding pattern for Fragment view binding
```

#### A4-2. "java.lang.IllegalStateException: Fragment not attached to an activity"
```
CAUSE:  Fragment operation after detach (network callback, delayed handler)
SEARCH: Find the Fragment from stack trace → check lifecycle state
COMMON:
  - requireContext() in coroutine that outlives Fragment
  - requireActivity() in async callback
  - getString(R.string.x) after detach
FIX:    Use context (nullable) instead of requireContext()
        Check isAdded before Fragment operations
        Use viewLifecycleOwner.lifecycleScope for coroutines
```

#### A4-3. "android.os.TransactionTooLargeException"
```
CAUSE:  Bundle/Intent data > 500KB (Binder transaction limit ~1MB shared)
SEARCH: Find what data is passed via Intent/Bundle → check size
COMMON:
  - Passing large Parcelable object between Activities
  - SavedInstanceState accumulating data over config changes
  - Fragment arguments with large list
FIX:    Pass ID only → load data in destination from DB/API
        Use ViewModel for data sharing between Fragments
        Clear savedInstanceState in onSaveInstanceState if too large
```

#### A4-4. "java.lang.IllegalStateException: Can not perform this action after onSaveInstanceState"
```
CAUSE:  Fragment transaction after onSaveInstanceState (state loss)
SEARCH: Find the Fragment transaction → check when it's called
COMMON:
  - commitNow() in async callback that fires after onPause
  - show()/hide() dialog after Activity paused
  - Navigation action after onStop
FIX:    Use commitAllowingStateLoss() (last resort)
        Better: check lifecycle state before transaction
        Best: use Navigation component (handles this automatically)
```

#### A4-5. "android.view.WindowManager$BadTokenException"
```
CAUSE:  Showing dialog/toast with invalid Activity context
SEARCH: Find the dialog/toast creation → check Activity lifecycle
COMMON:
  - Show AlertDialog after Activity finished
  - Toast with Activity context after destroy
  - PopupWindow with destroyed Activity reference
FIX:    Check !isFinishing && !isDestroyed before showing dialog
        Use applicationContext for Toast (not Activity context)
```

#### A4-6. "java.util.ConcurrentModificationException"
```
CAUSE:  Modifying collection while iterating over it
SEARCH: Find the collection from stack trace → check for/forEach loops
COMMON:
  - for (item in list) { list.remove(item) }
  - LiveData/Flow emitting new list while observer iterates old
  - Multiple coroutines modifying same MutableList
FIX:    Use toList() copy for iteration → modify original
        Use CopyOnWriteArrayList for concurrent access
        Use Mutex for coroutine synchronization
```

---

### Category B: Build Errors

#### B1. "Module not found: Can't resolve 'X'"
```
⚠️ SEARCH ORDER IS DIFFERENT FOR BUILD ERRORS:
  1. package.json → is X installed? → npm install X
  2. tsconfig.json → paths alias configured? → check paths mapping
  3. src/ imports → typo in import path? → fix path
  4. node_modules/ → X exists but wrong version? → update
DO NOT search src/ first — this is a dependency/config issue
```

#### B2. "Type 'X' is not assignable to type 'Y'"
```
CAUSE:  TypeScript type mismatch
SEARCH:
  1. Find type/interface Y definition → Grep "interface Y" or "type Y" in src/
  2. Find where X is created → check what shape it actually has
  3. Compare actual vs expected → find the mismatch
COMMON:
  - API response shape changed but types not updated
  - Optional field treated as required (add ?)
  - Union type not narrowed (add type guard)
FIX:    Fix the type to match reality OR fix the data to match the type
```

#### B3. "Duplicate class found in modules"
```
SEARCH: android/app/build.gradle → dependency tree
  → ./gradlew app:dependencies | grep "[class-name]"
DO NOT search src/ — this is purely a Gradle dependency issue
```

#### B4. "Pod install failed" / "CocoaPods could not find compatible versions"
```
SEARCH: ios/Podfile → check version constraints
  → pod outdated → find conflicting pods
  → Podfile.lock → check locked versions
DO NOT search src/ — this is iOS dependency management
FIX:    pod deintegrate → rm Podfile.lock → pod install --repo-update
```

---

### Category C: Network / API Errors

#### C1. "Network request failed" / HTTP 0
```
SEARCH:
  1. Find API base URL → Grep "baseURL" or "BASE_URL" in src/
  2. Find .env file → check API URL value
  3. Find the failing endpoint → Grep the endpoint path in src/
  4. Check interceptors → Grep "interceptor" in src/
COMMON:
  - Wrong BASE_URL in .env (localhost on device → use IP)
  - SSL certificate issue (dev server with self-signed cert)
  - Missing internet permission (Android: AndroidManifest.xml)
  - Request interceptor throwing error before request is sent
```

#### C2. HTTP 401 Unauthorized
```
SEARCH:
  1. Find auth token storage → Grep "token" or "accessToken" in src/
  2. Find auth interceptor → Grep "Authorization" in src/
  3. Find token refresh logic → Grep "refresh" in src/
COMMON:
  - Token expired but refresh not implemented
  - Token stored but not attached to request headers
  - Token refresh race condition (multiple 401 → multiple refresh calls)
FIX:    Check token exists → check it's attached → check expiry → add refresh
```

#### C3. HTTP 403 Forbidden
```
SEARCH: Find the API call → check headers + auth token + user role
COMMON:
  - Token valid but user lacks permission (role/scope issue)
  - CSRF token missing (web views)
  - API key vs OAuth token confusion
```

#### C4. HTTP 500 Internal Server Error
```
SEARCH: Find the API call → check request payload shape
COMMON:
  - Sending wrong data shape (missing required field)
  - Backend bug (not your mobile code) → check backend logs
  - Payload too large (file upload without compression)
NOTE:   If backend is also your project → search backend src/ for the endpoint handler
```

---

### Category D: State / Data Errors

#### D1. "Screen shows old/stale data"
```
SEARCH:
  1. Find the data-fetching function → Grep "fetch" or "query" or "useQuery" in screens/
  2. Find the cache/state management → Grep "store" or "cache" in src/
  3. Check refetch triggers → when does data refresh?
COMMON:
  - Cache not invalidated after mutation
  - Navigation doesn't trigger re-fetch (useFocusEffect missing)
  - Optimistic update didn't sync with server
FIX:    Add refetch on focus OR invalidate cache after mutation OR add pull-to-refresh
```

#### D2. "State updates not reflecting in UI"
```
SEARCH: Find the component → check state management
COMMON:
  - Mutating state directly: state.items.push(x) instead of setState([...state.items, x])
  - Object reference not changing: setState(sameObj) → React skips re-render
  - Zustand/Redux selector not selecting the changed field
  - Async state update batching issue
FIX:    Always create NEW references for state updates
```

#### D3. "Race condition — UI flickers / wrong data appears briefly"
```
SEARCH: Find the component → check useEffect deps + async calls
COMMON:
  - Two async calls racing, slower one overwrites faster result
  - State update from previous screen applied to current screen
  - Optimistic update visible before server confirms
FIX:    AbortController for fetch → cancel previous request on new one
        OR use unique request ID → ignore stale responses
```

---

### Category E: Navigation Errors

#### E1. "Screen not found / Route not registered"
```
SEARCH:
  1. Grep the screen name in src/navigation/ or src/router/
  2. Check ALL navigator files → is the screen registered?
  3. Grep "navigate(" or "push(" in src/ → find where it's called
COMMON:
  - Screen name typo: "ProductDetail" vs "ProductDetails"
  - Screen defined in wrong navigator (nested navigators)
  - Screen conditionally rendered (auth gate) but user not authenticated
```

#### E2. "Navigation params undefined"
```
SEARCH: Find the navigate call → check what params are passed → find the target screen → check what it expects
COMMON:
  - Forgot to pass params: navigate('Screen') instead of navigate('Screen', { id })
  - Param name mismatch: { itemId } vs route.params.id
  - Deep link opens screen without params → add default/fallback
```

---

### Category F: Platform-Specific Errors

#### F1. iOS: "App crashes only on real device (works on simulator)"
```
SEARCH:
  1. Check Xcode console logs on real device (connect + run)
  2. Grep for simulator-only code: __DEV__, Platform.OS checks
COMMON:
  - Missing privacy permission (camera, location, photos → Info.plist)
  - Keychain access restricted on device (not available in simulator mode)
  - ARM vs x86 architecture issue
  - Code signing / provisioning profile issue
```

#### F2. Android: "App crashes only on older devices (works on new)"
```
SEARCH:
  1. Check minSdkVersion in android/app/build.gradle
  2. Grep for API-level-specific code → missing compatibility check
COMMON:
  - Using API not available on older Android (WebView, Notification channels)
  - Missing desugaring for Java 8+ features
  - Memory limit lower on older devices → OOM on large images
```

#### F3. Flutter: "RenderFlex overflowed by X pixels"
```
SEARCH: Find the widget from error → check its parent layout constraints
COMMON:
  - Text too long in Row without Flexible/Expanded
  - Image with fixed size in constrained container
  - Column with unbounded children in ScrollView
FIX:    Wrap in Flexible/Expanded OR add overflow: TextOverflow.ellipsis OR use SingleChildScrollView
```

---

## Issue Investigation Workflow

```
When user says "check this issue" / "investigate" / "look into":

STEP 1: READ the issue fully
  → Don't skim — read every word
  → Identify: what feature? what's expected? what's actual?

STEP 2: EXTRACT search terms
  → Feature name (e.g., "checkout", "profile", "notification")
  → Component/screen name (e.g., "CartScreen", "PaymentForm")
  → Error message (if any)
  → User action that triggers it (e.g., "tap submit", "pull to refresh")

STEP 3: SEARCH project
  → Grep feature name in src/
  → Glob for screen/component files
  → Read the relevant code (3-5 files max)

STEP 4: TRACE the flow
  → User action → event handler → state change → API call → response → UI update
  → Find where the flow breaks

STEP 5: REPORT (don't fix yet)
  → "I found [component] at [file:line]."
  → "Current behavior: [what code does]."
  → "The issue is likely: [root cause based on code read]."
  → "Confidence: [high/medium/low] based on [evidence]."
  → "Want me to fix it?"

STEP 6: FIX (only if user says yes)
  → Propose specific change with before/after
  → Check side effects
  → Verify types match
```

---

## Git-Aware Debugging (Check Recent Changes First)

```
⛔ BEFORE deep-diving into code, CHECK WHAT CHANGED RECENTLY.
⛔ 80%+ of bugs are caused by RECENT CHANGES — find them first.

PRE-CHECK: IS THIS A GIT PROJECT?
  → Run: git rev-parse --is-inside-work-tree 2>/dev/null
  → If command fails / returns false → NOT a git project → SKIP this section
  → If git repo but no commits (git log fails) → SKIP this section
  → If git repo with commits → proceed below

STEP 1: CHECK GIT HISTORY
  → git log --oneline -10                        → recent commits
  → git diff HEAD~3 --name-only                  → files changed recently
  → git diff HEAD~3 -- [broken_file_path]        → exact changes to broken file
  → git log --oneline --all -- [broken_file_path] → full file history

STEP 2: ANALYZE RECENT CHANGES
  → Did any recent commit touch the broken file/feature?
  → If YES → read the diff → the bug is likely IN that diff
  → If NO → bug is environmental/data-driven → proceed to Root Cause below

STEP 3: GIT BISECT (for "it used to work" bugs)
  → If user says "it worked before" / "it broke recently":
  → Find last known-good commit: git log --oneline -20
  → Compare: git diff [good_commit]..HEAD -- [affected_files]
  → The bug is in that diff

STEP 4: DEPENDENCY CHANGES
  → git diff HEAD~5 -- package.json pubspec.yaml build.gradle Podfile
  → Did any dependency version change? → common source of breakage
  → Check: lock file changes (yarn.lock, pubspec.lock, Podfile.lock)

SKIP GIT-AWARE DEBUGGING WHEN:
  → Project has NO git initialized (no .git/ folder)
  → git init done but zero commits yet
  → Brand new project (no meaningful history)
  → User explicitly says "this never worked" (not a regression)
  → Build error from fresh install (dependency/config issue)
```

---

## Root Cause Analysis Framework (5-Step Tracing)

```
⛔ NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
⛔ NO COMPLETION CLAIMS WITHOUT FRESH VERIFICATION EVIDENCE

STEP 1: OBSERVE — What exactly happens?
  → What user action triggers it? (tap, scroll, navigate, submit)
  → What is the EXACT error/behavior? (not paraphrased — exact)
  → When does it happen? (always / sometimes / after [action] / on [platform])
  → Classify reproduction:
    ALWAYS           → deterministic — trace step by step
    SOMETIMES        → race condition / timing — check async flow
    ONLY on [device] → platform/hardware — check native layer
    ONLY after [X]   → state-dependent — trace state mutations
    FIRST TIME ONLY  → initialization — check setup/config

STEP 2: IMMEDIATE CAUSE — What code throws?
  → Find the EXACT file:line from error/stack trace
  → Read that file → what is the code doing at that line?
  → What variable/value is wrong? What should it be?
  → This is the IMMEDIATE cause (not root cause yet)

STEP 3: TRACE BACKWARD — What called this?
  → WHO calls this function? (Grep for callers in src/)
  → What data does the caller pass? Trace the data origin
  → Go one level up: who calls the CALLER?
  → Keep going until you find where the bad data ENTERED

STEP 4: FIND THE ROOT — Where does the chain break?
  → The root cause is where CORRECT data becomes INCORRECT
  → It's NOT the crash line — it's where the corruption starts
  → Common root causes:
    - API response missing field (backend changed, frontend didn't)
    - State not reset between screens (stale data leaks)
    - Race condition: async A and B, B finishes first overwrites A
    - Missing null check at data boundary (API → app)
    - Wrong assumption about data shape (type says X, reality is Y)
  → VERIFY: does this root cause explain ALL symptoms?
    - If yes → proceed to fix
    - If no → your theory is wrong → go back to Step 3

STEP 5: FIX + DEFENSE IN DEPTH
  → Fix the root cause (not just the crash line)
  → Then add validation at EVERY layer data passes through:
    Layer 1: API response validation (did backend send what we expect?)
    Layer 2: State mutation guard (is the data valid before storing?)
    Layer 3: Component prop check (does the component handle null/empty?)
    Layer 4: Render guard (does UI degrade gracefully?)
  → Goal: make the bug STRUCTURALLY IMPOSSIBLE to recur
  → Not just "fix this one case" — prevent the entire CLASS of bug
  → Cite: "Root cause: [file:line] — [explanation]"
  → Cite: "Defense: added validation at [layers]"
```

---

## Single Hypothesis Protocol

```
⛔ NEVER stack multiple fixes at once
⛔ NEVER "fix it and also refactor nearby code"

PROTOCOL:
  1. Form ONE hypothesis from root cause analysis
  2. Make the SMALLEST possible change to test it
  3. Verify: does it fix the bug?
     → YES → proceed to defense-in-depth
     → NO → REVERT the change → form NEW hypothesis
  4. Never carry forward a failed fix
  5. If 3 hypotheses fail → STOP and question architecture:
     → "I've tried 3 approaches and none fixed it.
        This suggests the issue is architectural, not a simple bug.
        Options: (1) [rethink approach], (2) [alternative pattern], (3) [ask user]"

WHY THIS MATTERS:
  - Stacking fixes hides which one actually worked
  - Multiple changes create new bugs while "fixing" old ones
  - Clean revert = clean slate for next hypothesis
```

---

## Red Flags — Anti-Rationalization Table

```
🚩 If you catch yourself saying/thinking these, STOP immediately:

WHAT YOU SAY                    WHAT IT MEANS                 WHAT TO DO
─────────────────────────────────────────────────────────────────────────
"Should work now"               You didn't verify             RUN IT. Read output.
"I'm confident this fixes it"   Confidence ≠ evidence         Show the evidence.
"I think the issue is..."       You haven't traced the code   Trace it. Cite file:line.
"Let me also clean up..."       Scope creep during bug fix    STOP. Fix bug only.
"Probably a race condition"     Buzzword without proof         PROVE with async trace.
"Try changing X to Y"           You haven't read the file      Read it FIRST.
"This is a known issue with X"  You're pattern-matching        Verify in THIS project.
Stacking 3+ changes at once     You're guessing               Revert. 1 change only.
Same fix attempted 3+ times     Architecture problem           STOP. Question approach.
"Works on my end"               Didn't test other platform     Test both. Or say untested.
```

---

## Multi-Error Triage

```
When user has MULTIPLE errors (common during upgrades/migrations):

1. SORT by dependency:
   → Which error causes other errors? Fix that one FIRST
   → Build errors before runtime errors
   → Import errors before type errors
   → Config errors before code errors

2. FIND THE ROOT:
   → 5 errors might all come from 1 root cause
   → Example: wrong package version → type errors + build errors + runtime errors
   → Fix the version → all 5 errors disappear

3. FIX IN ORDER:
   → Root cause first
   → Then verify: did other errors disappear?
   → If yes → done
   → If no → fix remaining one by one

4. NEVER fix all errors at once without understanding relationships
```

---

## Debugging Commands Cheat Sheet

```
REACT NATIVE:
  Clear all caches:     npx react-native start --reset-cache
  Rebuild iOS:          cd ios && rm -rf build && pod install && cd ..
  Rebuild Android:      cd android && ./gradlew clean && cd ..
  Full nuke:            rm -rf node_modules ios/Pods ios/build android/build && yarn && cd ios && pod install
  Check linking:        npx react-native config
  Check bundle:         npx react-native bundle --entry-file index.js --platform ios --dev false

FLUTTER:
  Clear all:            flutter clean && flutter pub get
  Analyze:              flutter analyze
  Check deps:           flutter pub outdated
  Full rebuild:         flutter clean && flutter pub get && cd ios && pod install && cd ..

EXPO:
  Clear cache:          npx expo start --clear
  Check config:         npx expo config
  Prebuild:             npx expo prebuild --clean
  Doctor:               npx expo-doctor

iOS:
  Clean build:          xcodebuild clean -workspace ios/App.xcworkspace -scheme App
  Device logs:          idevicesyslog (via libimobiledevice)
  Simulator logs:       xcrun simctl spawn booted log stream --level error

ANDROID:
  Logcat filter:        adb logcat *:E | grep "com.yourapp"
  Clear app data:       adb shell pm clear com.yourapp
  Check crash:          adb logcat -b crash
  Screenshot:           adb exec-out screencap -p > /tmp/screen.png
```
