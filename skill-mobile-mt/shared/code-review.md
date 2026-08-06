# Code Review — Senior Protocol

> 🔴 Always loaded. All platforms.
> Trained from: CodeRabbit, Qodo, obra/superpowers, Anthropic security review, WCAG 2.1.

---

## Platform Focus Rule

```
⛔ ONLY review patterns for the DETECTED platform. DO NOT cross-platform unless the code touches it.

REACT NATIVE / EXPO PROJECT:
  → Focus: RN patterns (stale closure, useEffect, FlatList, etc.)
  → Cross-reference Android/iOS ONLY IF:
    - Bug involves native module (Java/Kotlin/Swift/ObjC bridge)
    - Error comes from native layer (Logcat/Xcode console, not Metro)
    - User explicitly asks to check native code
  → SKIP: Flutter patterns entirely

FLUTTER PROJECT:
  → Focus: Flutter/Dart patterns (mounted, dispose, BuildContext, etc.)
  → Cross-reference Android/iOS ONLY IF:
    - Bug involves platform channel (MethodChannel/EventChannel)
    - Error comes from native layer (not Dart stack trace)
    - User explicitly asks to check native code
  → SKIP: React Native patterns entirely

ANDROID NATIVE PROJECT (Java/Kotlin):
  → Focus: Android patterns (lifecycle, ViewModel, coroutines, etc.)
  → SKIP: React Native AND Flutter patterns entirely
  → Cross-reference iOS ONLY IF user has KMM (Kotlin Multiplatform)

iOS NATIVE PROJECT (Swift/ObjC):
  → Focus: iOS patterns (optionals, @MainActor, Combine, etc.)
  → SKIP: React Native AND Flutter patterns entirely
  → Cross-reference Android ONLY IF user has KMM

CROSS-PLATFORM patterns (API contract, token expiry, navigation params):
  → Always applicable regardless of platform
```

---

## Review Modes (detect from user request)

```
⛔ DETECT which review mode the user wants BEFORE starting.
⛔ DO NOT default to full review — match the scope to what was asked.

USER SAYS                                    → MODE        → SCOPE
──────────────────────────────────────────────────────────────────────────────
"Review full code"                           → FULL        → Read ALL src/ files → 12-category checklist
"Review changes / review diff"               → CHANGES     → git diff (unstaged + staged) → review only changed code
"Review file X / review this file"           → FILE        → Read specific file(s) → 12-category checklist on those files only
"Review function X / review this function"   → FUNCTION    → Find function → trace callers/callees → deep review that function
"Review PR / review pull request"            → PR          → git diff [base]..HEAD → Step 0 PR-Level + 12-category on diff
"Review modified files"                      → MODIFIED    → git status (modified only) → read + review modified files
"Review commits"                             → COMMITS     → git log → git show [commit] → review each commit's changes
"Check PR"                                   → PR-CHECK    → Step 0 ONLY (size, scope, tests, commits) → quick pass/fail

═══ MODE DETAILS ═══

MODE: FULL
  → Glob "src/**/*" → read ALL source files
  → Run 12-category checklist on entire codebase
  → Report organized by file → severity
  → ⚠️ EXPENSIVE: only when user explicitly asks "review full" or "audit"
  → Estimated: 15-30 files, comprehensive

MODE: CHANGES (most common)
  → git diff --name-only → list changed files
  → git diff → read actual changes
  → Review ONLY the changed lines + their immediate context
  → Check: did the change break anything? missing state? missing test?
  → ⛔ DO NOT review unchanged code in same files (unless directly affected)

MODE: FILE
  → User specifies file path or "this file" (IDE selection)
  → Read the full file
  → Run 12-category checklist on that file
  → Also check: imports used correctly? exports consumed properly?

MODE: FUNCTION
  → User specifies function name or "this function" (IDE selection)
  → Find function definition (Grep)
  → Read the function + its context (surrounding code)
  → Trace: who calls this function? (Grep callers)
  → Trace: what does this function call? (read callees)
  → Deep review: correctness, edge cases, performance, security
  → Check: return values handled by all callers?

MODE: PR
  → Step 0: PR-Level Review (size, scope, tests, commits)
  → git diff [base-branch]..HEAD → get all changes
  → Read all changed files
  → Run 12-category checklist on changed code ONLY
  → Check: breaking changes? migration needed? tests added?
  → Output: full review format with verdict

MODE: MODIFIED
  → git status → list modified files (not untracked)
  → git diff → read actual modifications
  → Review modified code with 12-category checklist
  → Lighter than PR mode — no PR-level checks, just code quality

MODE: COMMITS
  → git log --oneline -N → list recent commits
  → For each commit: git show [hash] → read diff
  → Review each commit independently
  → Check: does each commit make sense alone? atomic changes?
  → Flag: commits that should be squashed, split, or reworded

MODE: PR-CHECK (quick — no code review)
  → Step 0 ONLY — fast pass/fail:
    □ PR size (LOC)
    □ Single responsibility
    □ Tests for logic changes
    □ Commit hygiene
    □ Description present
  → Output: ✅ PASS or 🔴 FAIL with specific issues
  → Does NOT review actual code — use MODE: PR for full review

⛔ DEFAULT: If user says just "review" without specifying:
  → Check git status first
  → If changes exist → MODE: CHANGES (review what changed)
  → If no changes → ASK: "Review full codebase or a specific file?"
```

---

## ⛔ STEP 0: PR-Level Review (Before Code Review)

```
BEFORE reviewing any code, review the PR/change itself:

PR SIZE:
  □ Under 400 LOC changed? (ideal)
  □ Under 800 LOC? (acceptable)
  □ 800+ LOC? → 🔴 SUGGEST SPLIT — "This PR does too many things. Split into:"
    → List each logical change that could be a separate PR

SINGLE RESPONSIBILITY:
  □ Does this PR do ONE thing? (1 feature OR 1 bug fix OR 1 refactor)
  □ ⛔ Mixed changes? (auth + payment + styling in one PR = bad)
    → Flag: "This PR mixes [X] and [Y]. Suggest splitting."

TEST ACCOMPANIMENT:
  □ Did changed LOGIC get new/updated tests?
  □ If no tests added AND logic changed → 🟠 FLAG:
    "Logic changed in [file] but no test added/updated."
  □ If test-only PR → good, no flag needed
  □ If config/style-only change → tests optional

COMMIT HYGIENE:
  □ Commit messages describe WHY, not just WHAT?
  □ No "fix", "update", "wip" without context?
  □ Ticket/issue reference if applicable?

⛔ If PR fails Step 0 → flag BEFORE diving into code
```

---

## Checklist (12 Categories)

### 1. Architecture
- [ ] Single responsibility per file (max 300 lines)
- [ ] Dependencies flow inward (UI → Domain → Data)
- [ ] Follows existing project patterns (naming, imports, structure)
- [ ] New files in correct directory
- [ ] No circular dependencies (A imports B imports A)
- [ ] SOLID principles not violated:
  - SRP: each class/function does ONE thing
  - OCP: can extend without modifying existing code
  - DIP: depends on abstractions, not concrete implementations

### 2. Correctness
- [ ] All states handled: loading, success, error, empty
- [ ] Edge cases: null, empty, timeout, concurrent
- [ ] Async errors caught with meaningful handling
- [ ] Cleanup on unmount/dispose (listeners, timers, subscriptions)
- [ ] No race conditions (double-tap, concurrent API calls)
- [ ] Return values checked (don't ignore function results)

### 3. Boundary Conditions (dedicated — AI code fails here most)
- [ ] **Null/undefined**: every nullable access has guard (optional chaining, null check)
- [ ] **Empty collections**: `.first`, `.last`, `[0]` on potentially empty array/list
- [ ] **Off-by-one**: loop bounds, substring ranges, pagination start/end
- [ ] **Numeric limits**: integer overflow, floating point precision, division by zero
- [ ] **String edge cases**: empty string, whitespace-only, unicode, emoji, RTL text
- [ ] **Date/time**: timezone handling, DST transitions, locale-specific formats
- [ ] **Concurrent access**: thread safety, shared mutable state guards

### 4. Test Quality
- [ ] **Test exists**: changed logic has corresponding test?
- [ ] **Happy path**: basic success case tested?
- [ ] **Error path**: error/failure cases tested?
- [ ] **Edge cases**: null, empty, boundary values tested?
- [ ] **Test behavior, not implementation**: tests assert WHAT, not HOW
- [ ] **No flaky patterns**: no `setTimeout`, no network calls in unit tests, no order-dependent tests
- [ ] **Mock correctly**: only mock boundaries (API, DB, native modules) — not internal logic
- [ ] **Meaningful assertions**: not just `expect(result).toBeDefined()` — check actual values

### 5. Readability & Maintainability
- [ ] **Naming**: variables/functions/classes named clearly — intent obvious from name
- [ ] **Cognitive complexity**: no function > 4 levels of nesting — flatten with guard clauses
- [ ] **Code duplication**: no copy-pasted blocks > 5 lines — extract shared function
- [ ] **Dead code**: no unused imports, unreachable branches, commented-out code
- [ ] **Function length**: functions under 40 lines — split if longer
- [ ] **Magic numbers/strings**: extracted to named constants
- [ ] **Early returns**: guard clauses at top, not deeply nested if/else

### 6. Performance
- [ ] Lists virtualized (FlatList / ListView.builder / LazyColumn)
- [ ] Memoized where needed (memo / const / remember / useMemo / useCallback)
- [ ] No inline functions in render/build (causes re-renders)
- [ ] Images cached and resized (no full-res from CDN)
- [ ] No main thread blocking (heavy work on background thread)
- [ ] No N+1 queries (loop with async call inside — batch instead)

### 7. Security (expanded — mobile-specific depth)
- [ ] No hardcoded secrets or API keys (check .env usage)
- [ ] Secure storage for tokens (Keychain / EncryptedSharedPreferences / SecureStore)
- [ ] Input validated and sanitized (SQL injection, XSS via WebView)
- [ ] Deep links validated before navigation (check params type + authorization)
- [ ] No sensitive data in logs (console.log user data)
- [ ] **Certificate pinning** for production API communication
- [ ] **JWT lifecycle**: access + refresh tokens, proper expiry check, secure rotation
- [ ] **Build config**: debug features disabled in release, ProGuard/obfuscation enabled
- [ ] **Native bridge security** (RN): bridge communications validated, no arbitrary eval
- [ ] **Biometric auth**: fallback to passcode, proper Keychain/Keystore integration
- [ ] **Dependency audit**: no known CVE in dependencies (npm audit / pub outdated)

### 8. Accessibility (a11y — WCAG 2.1 mobile)
- [ ] **Labels**: all interactive elements have accessibility label/hint
- [ ] **Touch targets**: minimum 44×44pt (iOS) / 48×48dp (Android) for tappable areas
- [ ] **Contrast**: text-to-background ratio ≥ 4.5:1 (normal text) / ≥ 3:1 (large text)
- [ ] **Screen reader**: content order makes sense for VoiceOver (iOS) / TalkBack (Android)
- [ ] **Font scaling**: UI doesn't break with Dynamic Type / font size settings (up to 200%)
- [ ] **Color-only info**: information NOT conveyed through color alone (add icons/text)
- [ ] **Focus management**: modal traps focus, focus restored after dismiss
- [ ] **Motion**: animations respect prefers-reduced-motion / Reduce Motion setting
- [ ] **Semantic roles**: buttons are buttons, headings are headings (not styled divs/texts)

### 9. Breaking Changes (critical for mobile — old versions persist)
- [ ] **Public API**: did exported function signature change? → backward compatible?
- [ ] **Deep links**: existing deep link URLs still work with new code?
- [ ] **Database schema**: migration added? Backward compatible with old app versions?
- [ ] **Push notification payload**: old app versions won't crash on new payload format?
- [ ] **Analytics events**: event names/properties changed? Dashboard will still work?
- [ ] **Feature flags**: new feature behind flag if risky? Gradual rollout?
- [ ] **Min SDK bump**: if SDK requirement increased, is it documented?

### 10. Platform
- [ ] Both iOS + Android tested (if cross-platform)
- [ ] Safe areas / notch / Dynamic Island handled
- [ ] Keyboard handled (dismiss, avoidance, scroll-to-input)
- [ ] Back button handled (Android hardware + gesture back)
- [ ] Permissions requested at point of use (not on app launch)
- [ ] Status bar / navigation bar styled correctly (light/dark)

### 11. Documentation
- [ ] **Complex logic commented**: non-obvious algorithms have explanation
- [ ] **Public API documented**: exported functions/components have JSDoc/dartdoc
- [ ] **Design decisions**: trade-offs explained where non-obvious ("why" not "what")
- [ ] **README updated**: if behavior changed, docs reflect it
- [ ] **TODO tracking**: TODOs have ticket/issue number (not orphaned "TODO: fix later")

### 12. i18n / Localization (if app ships internationally)
- [ ] **No hardcoded user-facing strings** — all extracted to translation files
- [ ] **RTL layout**: UI mirrors correctly for Arabic/Hebrew
- [ ] **Text expansion**: UI handles longer translations (German/French = +30-40%)
- [ ] **Locale-aware formatting**: dates, numbers, currency use Intl / locale formatters
- [ ] **Pluralization**: plural forms handled correctly (not just "1 item" / "N items")

---

## Severity

| Level | Action | Example |
|-------|--------|---------|
| 🔴 CRITICAL | Must fix before merge | Crash, security hole, data loss, PII leak |
| 🟠 HIGH | Should fix before merge | Memory leak, missing error state, race condition, no tests for logic |
| 🟡 MEDIUM | Fix in follow-up | Naming inconsistency, missing memoization, accessibility gap |
| 🔵 LOW | Nice to have | Minor style, comment improvement, dead code |

---

## Auto-Fail

**Any of these → block merge immediately:**

```
CODE AUTO-FAILS:
❌ console.log / print in production code
❌ Hardcoded secrets or API keys
❌ Force unwrap without null check (! / !! / as!)
❌ Empty catch blocks (error silently swallowed)
❌ 500+ line files
❌ Network call in render / build / Composable
❌ Index as list key (key={i})
❌ Missing loading / error / empty state (blank screen)
❌ PII in logs or analytics (email, phone, SSN)
❌ Token stored in AsyncStorage / SharedPreferences / UserDefaults (insecure)

PR AUTO-FAILS:
❌ PR > 1000 LOC with no description
❌ Logic changed but zero tests added/updated
❌ Breaking change without migration guide
❌ New dependency added without justification
```

### Grounding Auto-Fail (AI-generated code)

**If the code was generated by AI, also check:**

```
❌ Import from a package NOT in package.json / pubspec.yaml
❌ Function/method call that doesn't exist in the codebase
❌ API endpoint or response shape not verified from actual service code
❌ Library version syntax that doesn't match installed version
❌ Platform API that doesn't exist in the project's min SDK
❌ Test that tests implementation details instead of behavior
❌ Overly complex solution for a simple problem (over-engineering)
```

---

## Review Output Format

```
⛔ PR-LEVEL:
  Size: [N] LOC changed — [OK / ⚠️ LARGE / 🔴 SPLIT]
  Scope: [single-purpose / mixed — list each concern]
  Tests: [present / 🟠 missing for logic changes]
  Commits: [clean / needs cleanup]

FINDINGS:

🔴 CRITICAL — [file:line] [category]
  Issue: [description]
  Impact: [what breaks / who is affected]
  Fix: [specific code change with before/after]

🟠 HIGH — [file:line] [category]
  Issue: [description]
  Fix: [suggestion]

🟡 MEDIUM — [file:line] [category]
  Suggestion: [improvement]

🔵 LOW — [file:line]
  Note: [observation]

SUMMARY:
  Total: [N] findings ([N] critical, [N] high, [N] medium, [N] low)
  Verdict: [✅ APPROVE / ⚠️ APPROVE WITH COMMENTS / 🔴 CHANGES REQUESTED]
  Blocking: [list critical + high items that must be fixed]
```

---

## Review Workflow

```
STEP 1: PR-LEVEL REVIEW (Step 0 above)
  → Check size, scope, tests, commits BEFORE reading code
  → Flag PR-level issues first

STEP 2: SCAN ALL CHANGED FILES
  → Read every file in the diff
  → Don't skip test files or config changes
  → Note: files NOT changed but SHOULD have been (missing test, missing migration)

STEP 3: RUN CHECKLIST (12 categories above)
  → Check each category against the changed code
  → Only flag issues RELEVANT to the actual changes
  → Don't review code that wasn't changed (unless it's directly affected)

STEP 4: CHECK BREAKING CHANGES
  → Did any public API / exported function change?
  → Did any deep link / navigation route change?
  → Did any database schema change?
  → If yes to any → verify migration/backward compatibility

STEP 5: OUTPUT REVIEW (format above)
  → Organized by severity, not by file
  → Each finding cites exact file:line
  → Each finding has specific fix suggestion
  → Summary with verdict at the end

STEP 6: RE-REVIEW (after author fixes)
  → Only review the CHANGED items
  → Verify each flagged issue is actually fixed
  → Don't add NEW issues on re-review (unless critical)
```

---

## ⛔ Grounded Review Protocol (Anti-False-Positive)

**The #1 problem with AI code review: flagging things that are ACTUALLY CORRECT.**
**Every finding MUST be verified before reporting. NEVER flag based on memory alone.**

### Before Flagging ANY Issue — VERIFY:

```
⛔ RULE: If you haven't VERIFIED it, you can NOT flag it.

VERIFICATION CHECKLIST (run for EVERY finding):

1. FUNCTION/METHOD EXISTS?
   → Before saying "this function doesn't exist":
     → Grep for it in src/ AND node_modules/[package]/
     → Check package.json → is the library installed?
     → Check the library's type definitions (.d.ts) or source
     → If function exists in the installed version → DO NOT FLAG
   ⛔ NEVER say "this API doesn't exist" from memory
   ✅ ALWAYS verify: Grep "[function_name]" in project + node_modules

2. API SIGNATURE CORRECT?
   → Before saying "wrong parameters" or "wrong return type":
     → Read the actual type definition from node_modules or lib source
     → Check which VERSION of the library is installed (package.json)
     → APIs change between versions — verify against INSTALLED version
   ⛔ NEVER flag "wrong usage" based on a different version's docs
   ✅ ALWAYS check: installed version → actual API signature

3. DEPRECATED?
   → Before saying "this is deprecated":
     → WebSearch "[library] [function] deprecated [version]"
     → Check if deprecated in the INSTALLED version, not just latest
     → If not deprecated in installed version → DO NOT FLAG
   ⛔ NEVER flag "deprecated" from training data — verify live

4. IS THE PATTERN ACTUALLY WRONG?
   → Before saying "this is an anti-pattern":
     → Does the project have a REASON for this pattern? (read comments, README)
     → Is this a deliberate trade-off? (performance vs readability)
     → Does the team's own style guide allow it?
     → Is the "better" alternative actually compatible with this project?
   ⛔ NEVER impose theoretical best practice over working project conventions
   ✅ ASK: "Is there a reason for [pattern]?" before flagging

5. WILL THE FIX ACTUALLY WORK?
   → Before suggesting a fix:
     → Does the suggested replacement function/API exist?
     → Is it compatible with the project's SDK version?
     → Does it handle the same edge cases?
     → Will it break other code that depends on the current behavior?
   ⛔ NEVER suggest a fix you haven't mentally traced through
   ✅ ALWAYS show: "Replace [current] with [replacement] because [verified reason]"
```

### False Positive Prevention

```
COMMON AI FALSE POSITIVES — DO NOT FLAG THESE:

1. "Function X doesn't exist" → it DOES exist in the installed package
   FIX: Grep in node_modules/[package]/ before flagging

2. "This API is deprecated" → deprecated in v5, but project uses v3
   FIX: Check installed version first

3. "Missing error handling" → error is handled by parent/wrapper/interceptor
   FIX: Trace the full call chain before flagging

4. "Unused variable" → used in JSX below, or by framework convention
   FIX: Read the FULL file, not just the function

5. "Should use X instead of Y" → X doesn't exist in this framework version
   FIX: Verify X exists in installed version

6. "This will crash on null" → data is guaranteed non-null by API contract/types
   FIX: Check the TypeScript type or API response contract

7. "Security issue: no input validation" → validation done at API layer
   FIX: Check if validation exists elsewhere in the pipeline

8. "Performance: should memoize" → component only renders once or has no expensive children
   FIX: Check if memoization actually helps (it adds overhead too)

RULE: When in doubt → DO NOT FLAG. Ask instead:
  "I noticed [pattern]. Is there a specific reason for this approach?"
```

### Confidence Levels for Findings

```
Every finding SHOULD have a confidence level:

🟢 HIGH CONFIDENCE — Flag with certainty
  → You read the code and traced the exact bug path
  → You verified the API doesn't exist in the installed version
  → You have concrete evidence (file:line, type definition, docs)

🟡 MEDIUM CONFIDENCE — Flag with caveat
  → Pattern looks problematic but you haven't verified full context
  → Prefix: "This may be intentional, but [concern]..."
  → Ask: "Can you confirm whether [X] is expected?"

🔴 LOW CONFIDENCE — Ask, don't flag
  → You're unsure if this is actually wrong
  → You haven't verified the library API
  → You're going by general knowledge, not project-specific evidence
  → Format: "Question: [describe what you see]. Is this intentional?"

⛔ NEVER flag LOW CONFIDENCE findings as 🔴 CRITICAL
⛔ NEVER flag MEDIUM CONFIDENCE findings without caveat
✅ ONLY flag HIGH CONFIDENCE findings as blocking issues
```

---

## Practical Usage Review (Find REAL Bugs)

**Beyond checklists — find bugs that actually crash in production.**

### Runtime Behavior Analysis

```
FOR EVERY changed function, trace the REAL execution:

1. DATA FLOW TRACING
   → Where does the input come from? (API / user input / navigation params / store)
   → What happens if the input is: null? empty? wrong type? huge? malformed?
   → Where does the output go? (UI / API call / store / navigation)
   → Who ELSE calls this function? (Grep for callers — side effects?)

2. TIMING & ORDER
   → Is this function called at the right time? (after init? before dispose?)
   → What if it's called TWICE rapidly? (double-tap, React strict mode)
   → What if network is slow? (3+ second delay between request and response)
   → What if user navigates away DURING the operation?

3. STATE CONSISTENCY
   → After this function runs, is state ALWAYS valid?
   → Can this function leave state in a "half-updated" condition?
   → If it fails midway, does it roll back or leave corrupted state?
   → Does it check CURRENT state before modifying? (stale closure problem)

4. INTERACTION WITH EXISTING CODE
   → Does this change affect OTHER features? (Grep for shared dependencies)
   → Does it change a shared util/service that other screens use?
   → If it modifies an API call, does the backend expect the new format?
   → If it adds a new event listener, does it conflict with existing ones?
```

### Production Bug Patterns (real-world, not theoretical)

```
THESE PATTERNS CAUSE PRODUCTION CRASHES — check for them specifically:

═══ CROSS-PLATFORM (all mobile) ═══

1. RACE CONDITION ON MOUNT/UNMOUNT
   RN:      async in useEffect → user navigates away → setState on unmounted → crash
   Flutter:  async callback → user pops screen → setState after dispose → crash
   iOS:      Task runs → view deallocated → access self → EXC_BAD_ACCESS
   Android:  coroutine runs → Activity destroyed → update UI → IllegalStateException
   CHECK:
     RN:      useEffect has cleanup with cancelled flag or AbortController?
     Flutter:  check `mounted` before setState in every async callback?
     iOS:      [weak self] in every closure? Task cancelled in deinit?
     Android:  using viewModelScope (auto-cancels)? repeatOnLifecycle for flows?

2. NAVIGATION PARAM ASSUMPTION
   RN:      route.params.id → crashes from deep link without params
   Flutter:  ModalRoute.of(context)!.settings.arguments → null from deep link
   iOS:      force unwrap navigationController?.viewControllers → index out of range
   Android:  arguments!!.getString("id") → NPE from deep link
   CHECK: every navigation param → has default value or null guard?

3. API CONTRACT MISMATCH
   → Frontend expects { data: [...] } but backend sends { items: [...] }
   → Frontend expects string but backend sends number/null
   CHECK:
     RN:      TypeScript types match actual API response?
     Flutter:  fromJson factory handles null/missing fields?
     iOS:      Codable optional vs required fields match response?
     Android:  @SerializedName matches actual JSON keys? Nullable types correct?

4. TOKEN EXPIRY DURING LONG SESSION
   → User opens app → leaves for 2 hours → comes back → token expired
   CHECK:
     → Auth interceptor handles token refresh?
     → Handles CONCURRENT 401s? (queue refresh, replay requests)
     → Refresh token also expired → redirect to login gracefully?

5. PLATFORM-SPECIFIC CRASH
   → Works on iOS, crashes on Android (or vice versa)
   → Common: keyboard behavior, back button, permission timing, font rendering
   CHECK: any Platform.OS / Platform.isAndroid check → what happens on the OTHER platform?

═══ REACT NATIVE SPECIFIC ═══

6. STALE CLOSURE
   → useState value used inside useCallback/useEffect but not in dependency array
   → Symptom: function uses old state value, not current
   → CHECK: every state variable used inside callback → must be in deps[]

7. INFINITE RE-RENDER
   → Object/array created in render used as useEffect dependency
   → const filters = { status: 'active' }; // new ref every render
   → useEffect(() => { fetch(filters) }, [filters]); // infinite loop
   → CHECK: useEffect deps with objects/arrays → useMemo them

8. MEMORY LEAK — EVENT ACCUMULATION
   → addEventListener / on() without removeEventListener / off()
   → Each navigation adds ANOTHER listener → 50 visits → 50 listeners
   → CHECK: EVERY listener → has corresponding removal in useEffect cleanup

9. ASYNC STORAGE RACE
   → Two components read/write same AsyncStorage/MMKV key simultaneously
   → CHECK: shared storage key → is access serialized?

10. DEEP COPY vs SHALLOW COPY
    → const newState = { ...state }; // shallow — nested objects same reference
    → Mutating nested → mutates original → React skips re-render
    → CHECK: spread on nested objects → deep clone needed?

═══ FLUTTER SPECIFIC ═══

11. BUILDCONTEXT USED AFTER ASYNC GAP
    → await someAsync(); Navigator.of(context).pop(); → context may be invalid
    → CHECK: every context usage after await → guard with `if (!mounted) return;`

12. SETSTATE IN BUILD / INITSTATE SYNC
    → setState() called during build → "setState called during build" exception
    → setState() in initState without SchedulerBinding
    → CHECK: setState only in event handlers or SchedulerBinding.addPostFrameCallback

13. GLOBALKEY MISUSE
    → GlobalKey used for every list item → causes full subtree rebuild
    → CHECK: GlobalKey only for FormState, Scaffold, or explicit widget reference
    → Use ValueKey/ObjectKey for lists

14. STREAM / CONTROLLER NOT DISPOSED
    → StreamController / AnimationController / TextEditingController not disposed
    → Each screen visit creates new controller → memory leak
    → CHECK: every controller created → has dispose() in State.dispose()

15. PROVIDER/BLOC NOT FOUND
    → BlocProvider/ChangeNotifierProvider not above the widget that reads it
    → "Could not find the correct Provider" → crash on specific navigation path
    → CHECK: provider scope covers ALL screens that need it

═══ iOS SWIFT SPECIFIC ═══

16. FORCE UNWRAP CRASH (!)
    → let value = optional! → EXC_BAD_ACCESS if nil
    → Common with IBOutlet, UserDefaults, Codable
    → CHECK: every ! → should be guard let / if let / ?? default

17. RETAIN CYCLE (MEMORY LEAK)
    → closure captures self strongly → ViewController never deallocated
    → Each screen visit leaks entire VC + its views + its data
    → CHECK: every closure → [weak self] or [unowned self]
    → CHECK: delegate properties → declared as weak?

18. MAIN THREAD VIOLATION
    → UI update from background thread → crash or undefined behavior
    → URLSession callback → update label → random crash
    → CHECK: every completion handler → DispatchQueue.main.async or @MainActor

19. CODABLE CRASH ON API CHANGE
    → Backend adds/removes field → Codable decode fails → entire response lost
    → CHECK: optional properties for fields that might be absent
    → CHECK: custom init(from decoder:) with try? for graceful degradation

20. CORE DATA THREAD SAFETY
    → NSManagedObject accessed from wrong thread → crash
    → CHECK: perform() / performAndWait() for every Core Data operation
    → CHECK: NSManagedObjectID instead of passing objects between threads

═══ ANDROID KOTLIN SPECIFIC ═══

21. FORCE UNWRAP (!!) NPE
    → val value = nullable!! → NullPointerException
    → Common with Intent extras, Bundle arguments, findViewById
    → CHECK: every !! → should be ?. / ?: default / requireNotNull with message

22. ACTIVITY/FRAGMENT LIFECYCLE CRASH
    → Update UI after onDestroyView → IllegalStateException
    → Access binding after Fragment view destroyed → NPE
    → CHECK: viewLifecycleOwner for observers, _binding = null in onDestroyView

23. CONFIGURATION CHANGE CRASH
    → Activity recreated on rotation → lose state, duplicate Fragment
    → CHECK: ViewModel for state survival, savedInstanceState for transient state
    → CHECK: singleInstance/singleTask launch mode side effects

24. PARCELABLE SIZE LIMIT
    → Pass large object via Intent/Bundle → TransactionTooLargeException
    → CHECK: Bundle data < 500KB, pass ID instead of full object

25. COROUTINE EXCEPTION SWALLOWED
    → launch {} without CoroutineExceptionHandler → crash or silent failure
    → CHECK: supervisorScope for independent children
    → CHECK: try/catch inside launch, or CoroutineExceptionHandler
```

### Library-Specific Usage Traps

```
VERIFY actual library behavior — NOT what you "think" it does:

REACT NATIVE:
  → FlatList: does onEndReached fire correctly with ListHeaderComponent?
  → Animated: is useNativeDriver used where possible? (can't animate layout props)
  → Navigation: are screen options in the right place? (Stack vs Tab vs Drawer)
  → StatusBar: does it reset when navigating back? (translucent gotcha)

FLUTTER:
  → BuildContext: not used after async gap? (mounted check required)
  → Key: is GlobalKey used unnecessarily? (causes rebuild of entire subtree)
  → Dispose: are ALL controllers disposed? (TextEditingController, AnimationController)
  → Platform channels: is the native side handling null correctly?

iOS SWIFT:
  → Combine: are cancellables stored? (without store, subscription dies immediately)
  → @MainActor: all UI updates on main actor? (crash if not)
  → Task: is cancellation checked in long operations? (isCancelled)
  → Codable: optional vs required fields match actual API response?

ANDROID KOTLIN:
  → LaunchedEffect: does it cancel correctly on recomposition?
  → remember: is the key correct? (wrong key = stale value)
  → Flow: is collect happening in lifecycle-aware scope? (repeatOnLifecycle)
  → Parcelable: are all custom classes Parcelable for SavedStateHandle?

⛔ NEVER flag library usage without reading the library's ACTUAL behavior
✅ If unsure → WebSearch "[library] [function] [version] gotchas"
```

---

## Example Issues

### Before (Bad)
```typescript
// ❌ No error handling, no loading state, index as key
function ProductList() {
  const [data, setData] = useState([]);
  useEffect(() => { api.get('/products').then(r => setData(r.data)); }, []);
  return data.map((item, i) => <ProductCard key={i} item={item} />);
}
```

### After (Good)
```typescript
// ✅ All states, cleanup, stable key, error handling
function ProductList() {
  const [state, setState] = useState({ data: [], loading: true, error: null });
  useEffect(() => {
    let cancelled = false;
    api.get('/products')
      .then(r => { if (!cancelled) setState({ data: r.data, loading: false, error: null }); })
      .catch(e => { if (!cancelled) setState({ data: [], loading: false, error: e.message }); });
    return () => { cancelled = true; };
  }, []);

  if (state.loading) return <LoadingSkeleton />;
  if (state.error) return <ErrorView message={state.error} onRetry={refresh} />;
  if (!state.data.length) return <EmptyState />;
  return <FlatList data={state.data} keyExtractor={item => item.id} renderItem={...} />;
}
```

### Examples — React Native

```typescript
// ❌ No error handling, no loading state, index as key
function ProductList() {
  const [data, setData] = useState([]);
  useEffect(() => { api.get('/products').then(r => setData(r.data)); }, []);
  return data.map((item, i) => <ProductCard key={i} item={item} />);
}

// ✅ All states, cleanup, stable key
function ProductList() {
  const [state, setState] = useState({ data: [], loading: true, error: null });
  useEffect(() => {
    let cancelled = false;
    api.get('/products')
      .then(r => { if (!cancelled) setState({ data: r.data, loading: false, error: null }); })
      .catch(e => { if (!cancelled) setState({ data: [], loading: false, error: e.message }); });
    return () => { cancelled = true; };
  }, []);
  if (state.loading) return <LoadingSkeleton />;
  if (state.error) return <ErrorView message={state.error} onRetry={refresh} />;
  if (!state.data.length) return <EmptyState />;
  return <FlatList data={state.data} keyExtractor={item => item.id} renderItem={...} />;
}
```

### Examples — Flutter

```dart
// ❌ No mounted check, no error handling, setState in async
class _ProductListState extends State<ProductList> {
  List<Product> data = [];
  void initState() {
    super.initState();
    api.getProducts().then((r) => setState(() => data = r)); // crash if unmounted
  }
  Widget build(ctx) => ListView(children: data.map((e) => ProductCard(e)).toList()); // not lazy
}

// ✅ mounted check, error handling, ListView.builder
class _ProductListState extends State<ProductList> {
  List<Product> data = [];
  bool loading = true;
  String? error;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    try {
      final result = await api.getProducts();
      if (!mounted) return; // guard
      setState(() { data = result; loading = false; });
    } catch (e) {
      if (!mounted) return;
      setState(() { error = e.toString(); loading = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (loading) return const Center(child: CircularProgressIndicator());
    if (error != null) return ErrorView(message: error!, onRetry: _loadData);
    if (data.isEmpty) return const EmptyState();
    return ListView.builder(
      itemCount: data.length,
      itemBuilder: (ctx, i) => ProductCard(key: ValueKey(data[i].id), product: data[i]),
    );
  }
}
```

### Examples — iOS Swift

```swift
// ❌ Force unwrap, no error handling, main thread violation
class ProductListVC: UIViewController {
    var data: [Product] = []
    override func viewDidLoad() {
        super.viewDidLoad()
        api.getProducts { result in
            self.data = result!  // force unwrap + retain cycle + background thread UI update
            self.tableView.reloadData()
        }
    }
}

// ✅ Weak self, guard let, main thread, error handling
class ProductListVC: UIViewController {
    private var data: [Product] = []
    private var task: Task<Void, Never>?

    override func viewDidLoad() {
        super.viewDidLoad()
        loadData()
    }

    private func loadData() {
        task = Task { [weak self] in
            do {
                let result = try await api.getProducts()
                guard let self, !Task.isCancelled else { return }
                await MainActor.run {
                    self.data = result
                    self.tableView.reloadData()
                }
            } catch {
                guard let self, !Task.isCancelled else { return }
                await MainActor.run { self.showError(error.localizedDescription) }
            }
        }
    }

    deinit { task?.cancel() }
}
```

### Examples — Android Kotlin

```kotlin
// ❌ Force unwrap, no lifecycle awareness, leak
class ProductListFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        lifecycleScope.launch {
            val data = api.getProducts()!! // force unwrap
            binding.recyclerView.adapter = ProductAdapter(data) // binding may be null
        }
    }
}

// ✅ ViewModel, StateFlow, lifecycle-aware, null-safe
// ViewModel
class ProductListViewModel : ViewModel() {
    private val _uiState = MutableStateFlow<UiState<List<Product>>>(UiState.Loading)
    val uiState: StateFlow<UiState<List<Product>>> = _uiState.asStateFlow()

    init { loadData() }

    private fun loadData() {
        viewModelScope.launch {
            try {
                val data = api.getProducts()
                _uiState.value = if (data.isEmpty()) UiState.Empty else UiState.Success(data)
            } catch (e: Exception) {
                _uiState.value = UiState.Error(e.message ?: "Unknown error")
            }
        }
    }
}

// Fragment
class ProductListFragment : Fragment() {
    private val viewModel: ProductListViewModel by viewModels()
    private var _binding: FragmentProductListBinding? = null
    private val binding get() = _binding!!

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewLifecycleOwner.lifecycleScope.launch {
            viewLifecycleOwner.repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    when (state) {
                        is UiState.Loading -> showLoading()
                        is UiState.Success -> showData(state.data)
                        is UiState.Empty -> showEmpty()
                        is UiState.Error -> showError(state.message)
                    }
                }
            }
        }
    }

    override fun onDestroyView() { super.onDestroyView(); _binding = null }
}
```

### Accessibility Examples (all platforms)

```tsx
// ❌ RN — No accessibility
<TouchableOpacity onPress={onDelete}><Image source={trashIcon} /></TouchableOpacity>

// ✅ RN — Accessible
<TouchableOpacity onPress={onDelete} accessibilityLabel="Delete item"
  accessibilityRole="button" style={{ minWidth: 44, minHeight: 44 }}>
  <Image source={trashIcon} />
</TouchableOpacity>
```

```dart
// ❌ Flutter — No semantics
IconButton(icon: Icon(Icons.delete), onPressed: onDelete)

// ✅ Flutter — Accessible
Semantics(
  label: 'Delete item', button: true,
  child: IconButton(icon: Icon(Icons.delete), onPressed: onDelete,
    constraints: BoxConstraints(minWidth: 48, minHeight: 48)),
)
```

```swift
// ❌ iOS — No accessibility
button.setImage(UIImage(named: "trash"), for: .normal)

// ✅ iOS — Accessible
button.setImage(UIImage(named: "trash"), for: .normal)
button.accessibilityLabel = "Delete item"
button.accessibilityTraits = .button
// Touch target >= 44x44pt (set via constraints)
```

```xml
<!-- ❌ Android — No content description -->
<ImageButton android:src="@drawable/ic_delete" />

<!-- ✅ Android — Accessible -->
<ImageButton android:src="@drawable/ic_delete"
    android:contentDescription="@string/delete_item"
    android:minWidth="48dp" android:minHeight="48dp" />
```
