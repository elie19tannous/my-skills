# Prompt Engineering — Intelligent Prompt Generation

> Learned from Anthropic, Cursor, Lovable, Manus, Windsurf, Kiro, Claude Code, and top 50k+ star repos.
> How to generate prompts that AI agents execute correctly.

---

## Core Principles

### 1. XML Tag Structure (Anthropic Best Practice)

**Why:** Clear structure prevents misinterpretation.

```xml
<task>
  <role>Senior React Native developer with 10+ years experience</role>

  <context>
    Project: E-commerce mobile app
    Stack: React Native 0.73 + TypeScript + Redux Toolkit
    Current: Product listing works
    Need: Add cart functionality
  </context>

  <instructions>
    1. Clone pattern from ProductList screen
    2. Create cart slice with Redux Toolkit
    3. Add items to cart with optimistic updates
    4. Handle API errors with rollback
  </instructions>

  <constraints>
    - Must work offline (cache in Redux Persist)
    - Follow existing ProductList pattern
    - Use existing Button/Card components
    - NO new dependencies without approval
  </constraints>

  <examples>
    <example>
      <input>Add product to cart</input>
      <output>
        dispatch(addToCart(product));
        // Optimistic update → API call → rollback on error
      </output>
    </example>
  </examples>

  <output_format>
    1. List files to create/modify
    2. Show code changes with before/after
    3. Specify test cases
    4. List manual verification steps
  </output_format>
</task>
```

---

## Auto-Think Templates (Enhanced)

### Fix / Debug

```xml
<think>
BUG: [description]
ERROR MESSAGE: [paste exact error]

⛔ STOP — CLASSIFY + SEARCH PROJECT FIRST (before ANY analysis):

<error_classification>
  TYPE: [RUNTIME CRASH / BUILD ERROR / TYPE MISMATCH / NETWORK ERROR /
         RENDER ERROR / NAVIGATION ERROR / PERFORMANCE / STATE ERROR /
         NATIVE ERROR / MEMORY ERROR / INVESTIGATION]

  SEARCH STRATEGY based on type:
  → RUNTIME/STATE/RENDER/NAVIGATION → Search src/ FIRST → then trace outward
  → BUILD/NATIVE                    → Search config files FIRST (tsconfig/gradle/Pod/pubspec)
  → NETWORK/API                     → Search API service files → then .env → then interceptors
  → INVESTIGATION                   → Search by feature name → read → report (don't fix yet)

  If complex bug → Read shared/debugging-intelligence.md for pattern match
</error_classification>

<project_search>
  STEP 1: Extract keywords from error:
  → File/path in stack trace: [extract]
  → Function/class/component name: [extract]
  → Module/package name: [extract]
  → Line number: [extract if available]
  → Error code / HTTP status: [extract if available]

  STEP 2: Filter noise from log (if user pasted log):
  → SKIP: node_modules/*, React internals, engine frames
  → FOCUS: lines with src/ paths, "Error:", "Caused by:", YOUR component names

  STEP 3: Search project source code (MANDATORY):
  → Grep "[keyword]" src/             ← ALWAYS start here (unless BUILD error)
  → Grep "[function_name]" src/       ← find the actual function
  → Glob "**/*[ComponentName]*"       ← find the actual file
  → Results: [list files found]

  STEP 4: Read matched files (TOP 3-5):
  → Read [file1] — [what I found: actual code, types, imports]
  → Read [file2] — [what I found: related logic, callers]
  → Read [file3] — [what I found: state/store connected to this]

  ⛔ If I skipped Step 1-4 → GO BACK AND DO THEM NOW
  ⛔ If I found 0 results in src/ → widen: lib/ → app/ → project root
</project_search>

<source_verification>
  ⚠️ Verify I have REAL project data (not assumptions):
  - [ ] Classified error type and picked correct search strategy
  - [ ] Filtered noise from log (if applicable)
  - [ ] Searched src/ with Grep for error keywords → found files
  - [ ] Read the actual file(s) where bug occurs
  - [ ] Verified function/class names exist in project (grep result)
  - [ ] Checked package versions in package.json/pubspec.yaml
  - [ ] Identified data types from actual code (not assumed)
  - [ ] Traced the call chain: who calls this → what it returns
</source_verification>

<root_cause_tracing>
  ⛔ NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST

  STEP 1 — IMMEDIATE CAUSE (what throws):
  - Error type: [from classification above]
  - Crash/error at: [file:line from project search]
  - What code does at that line: [describe from reading]
  - What value is wrong: [actual vs expected]

  STEP 2 — TRACE BACKWARD (what called this):
  - Who calls this function? → [grep callers in src/]
  - What data does caller pass? → [trace data origin]
  - Go up one level: who calls the caller? → [trace further]

  STEP 3 — ROOT CAUSE (where chain breaks):
  - Root cause at: [file:line — where correct data becomes incorrect]
  - WHY it fails: [based on actual code read, NOT guess]
  - Does this match a known pattern? → [check debugging-intelligence.md if loaded]
  - Does root cause explain ALL symptoms? YES/NO
    → If NO → theory is wrong → re-trace from Step 2
</root_cause_tracing>

<working_example>
  Search for similar working code in SAME project:
  → Grep for similar pattern that works: [search term]
  → Found working example at: [file:line] (or "none found")
  → Differences between broken vs working:
    1. [difference]
    2. [difference]
  → The fix should align broken code with working pattern
</working_example>

<hypothesis>
  ⛔ 1 HYPOTHESIS → 1 MINIMAL CHANGE → VERIFY

  HYPOTHESIS: [specific theory based on root cause]
  CHANGE: [smallest possible change to test this — 1 change only]
  EXPECTED RESULT: [what should happen if hypothesis is correct]

  ⛔ If this fails → REVERT → form NEW hypothesis (never stack fixes)
  ⛔ If 3 hypotheses fail → STOP → question architecture
</hypothesis>

<fix>
  [Specific change with code snippet — before → after]

  WHY IT WORKS:
  [Explain based on root cause tracing — not guess]
  SOURCE: [where this fix pattern comes from — project code / skill file / official docs]

  DEFENSE IN DEPTH (make bug structurally impossible):
  - Layer 1 (input): [validation added]
  - Layer 2 (state): [guard added]
  - Layer 3 (render): [null check / fallback added]
</fix>

<verification>
  ⛔ NO COMPLETION CLAIMS WITHOUT EVIDENCE

  🚩 Anti-rationalization check:
  - Am I saying "should work now" without running it? → RUN IT
  - Am I "confident" without evidence? → PROVE IT
  - Am I stacking 3+ changes? → REVERT. 1 change only.

  Evidence:
  - [ ] Fix addresses root cause (not just symptoms)
  - [ ] All symptoms explained by this root cause
  - [ ] Working example pattern followed (if found)
  - [ ] Defense-in-depth added at [N] layers
  - [ ] Side effects checked (grep for other callers)
  - [ ] Both platforms considered (iOS + Android)
</verification>

<side_effects>
  - Files that import this: [list from grep results]
  - Tests affected: [list]
  - Platform-specific: iOS [impact] / Android [impact]
</side_effects>

<test>
  1. Unit test: [specific test case]
  2. Manual: [steps to reproduce bug → verify fix]
  3. Regression: [what could this break]
</test>

<cleanup>
  - Remove debug logs
  - Update comments
  - Check for unused imports
</cleanup>
</think>
```

### Diagnostic Scan (user unsure / vague / "check this for me")

```xml
<think>
USER SAID: [what user described or asked — could be vague]
AREA: [extract: screen name / feature name / module name / file name]

<area_identification>
  What did user mention or show?
  → Screen/feature name: [extract from user's words]
  → File pasted/referenced: [if any]
  → Behavior described: [if any]
  → If unclear → I should ask: "Which screen or feature should I check?"
</area_identification>

<project_search>
  Search broadly for this area:
  → Grep "[feature]" src/            → found: [list files]
  → Glob "**/*[ScreenName]*"         → found: [list files]
  → Also search: related hooks, services, stores, utils
  → Total files to scan: [N files]
</project_search>

<diagnostic_scan>
  For EACH file, run the checklist:

  FILE: [file1:path]
  □ Crash risks:    [findings or "clean"]
  □ Memory leaks:   [findings or "clean"]
  □ Race conditions: [findings or "clean"]
  □ Security:       [findings or "clean"]
  □ Performance:    [findings or "clean"]
  □ UX/states:      [findings or "clean"]
  □ Data flow:      [trace API → state → render — any break?]
  □ Edge cases:     [empty data? error response? offline? slow?]

  FILE: [file2:path]
  □ ... (repeat for each file)
</diagnostic_scan>

<report>
  Scanned: [N files] in [area name]

  🔴 Issues found:
    1. [SEVERITY] [file:line] — [description]
    2. [SEVERITY] [file:line] — [description]

  🟡 Suspicious (might be intentional):
    1. [file:line] — [what looks off and why]

  ✅ Looks good:
    - [aspect that's well-implemented]

  Recommendation: [what to fix first / what to investigate deeper]
</report>
</think>
```

**Example:**
```xml
<think>
BUG: App crashes when tapping product with no images

<context_needed>
  - Read src/screens/ProductDetail.tsx
  - Grep for image rendering: grep "Image source" src/
  - Check Product type definition
</context_needed>

<root_cause>
  Line 42: <Image source={{uri: product.images[0]}} />
  Problem: product.images is undefined when API returns no images
  TypeScript allows this because images is Product['images']?
</root_cause>

<fix>
  {product.images?.length > 0 ? (
    <Image source={{uri: product.images[0]}} />
  ) : (
    <Image source={require('@assets/placeholder.png')} />
  )}

  WHY IT WORKS:
  Optional chaining prevents undefined access.
  Fallback image provides default visual.
</fix>

<side_effects>
  - ProductCard.tsx also renders images → apply same fix
  - No tests affected (this is a UI safety check)
  - Works same on both platforms
</side_effects>

<test>
  1. Unit: Mock product with images: undefined
  2. Manual: Find product without images in staging API
  3. Regression: Verify products WITH images still render
</test>

<cleanup>
  - No debug code added
  - Add comment: // Handle products without images
</cleanup>
</think>
```

---

### Build / Create (Multi-Phase)

**Phase 1: Discovery**
```xml
<think>
<discovery>
FEATURE: [description]
PLATFORM: [React Native / Flutter / iOS / Android]

<source_verification>
  ⚠️ GROUNDING CHECK:
  - [ ] Scanned actual project structure (not assumed)
  - [ ] Found real reference feature (not imagined)
  - [ ] Will read reference files before cloning pattern
  - [ ] Will verify all imports/packages exist before using
</source_verification>

STEP 1: SCAN PROJECT
  - List screens: ls src/screens/
  - Find similar features: grep -r "useState" src/screens/
  - Identify pattern: feature-based or layer-based?

STEP 2: FIND REFERENCE
  - Most similar feature: [name]
  - Location: [path]
  - Files in reference:
    * Screen component
    * Service/API layer
    * State management (slice/store/bloc)
    * Types/interfaces
    * Tests

STEP 3: READ REFERENCE FILES
  [List files to read - will load in next step]
</discovery>
</think>
```

**Phase 2: Analysis**
```xml
<think>
<analysis>
REFERENCE ANALYZED: src/features/product/

PATTERNS DETECTED:
  - State: Redux Toolkit slice
  - API: Axios with interceptor
  - Data: API response → map to domain entity
  - UI: Functional component + hooks
  - Navigation: React Navigation v6
  - Naming: camelCase for files, PascalCase for components

DATA FLOW:
  ProductScreen
    → useSelector(state.product.items)
    → dispatch(fetchProducts())
      → productSlice.ts (createAsyncThunk)
        → productService.ts (axios.get)
          → API response
        → map to Product entity
      → update Redux state
    → re-render with new data

ERROR HANDLING:
  - API errors: catch in thunk → set error state
  - UI errors: ErrorBoundary wraps screen
  - Network: Show offline banner

STATES: loading / success / error / empty
</analysis>
</think>
```

**Phase 3: Clone Mapping**
```xml
<think>
<clone_map>
REFERENCE → NEW FEATURE

product/ProductScreen.tsx      → cart/CartScreen.tsx
product/useProducts.ts         → cart/useCart.ts
product/productService.ts      → cart/cartService.ts
product/productSlice.ts        → cart/cartSlice.ts
product/product.types.ts       → cart/cart.types.ts
product/ProductCard.tsx        → cart/CartItem.tsx
product/ProductScreen.test.tsx → cart/CartScreen.test.tsx

MODIFICATIONS:
1. Update API endpoints:
   - GET /products → GET /cart
   - POST /cart/add → add item to cart

2. Adjust state shape:
   - items: Product[] → items: CartItem[]
   - Add: quantities, totals, discounts

3. UI changes:
   - ProductCard shows image + price
   - CartItem shows image + price + quantity + remove button

4. Navigation:
   - ProductScreen → ProductDetail
   - CartScreen → Checkout
</clone_map>
</think>
```

**Phase 4: Implementation Plan**
```xml
<think>
<implementation>
INCREMENTAL APPROACH (test after each step):

ITERATION 1: Type Definitions
  - Create cart/cart.types.ts
  - Define CartItem, Cart interfaces
  - Export types
  ✅ TEST: TypeScript compilation succeeds

ITERATION 2: API Service
  - Create cart/cartService.ts
  - Implement getCart(), addToCart(), removeFromCart()
  - Use same axios instance as productService
  ✅ TEST: Unit tests pass for API calls

ITERATION 3: Redux Slice
  - Create cart/cartSlice.ts
  - createAsyncThunk for async operations
  - Add reducers for optimistic updates
  ✅ TEST: Redux tests pass

ITERATION 4: Custom Hook
  - Create cart/useCart.ts
  - Wrap useSelector + useDispatch
  - Export cart operations
  ✅ TEST: Hook tests pass

ITERATION 5: UI Components
  - Create cart/CartItem.tsx (clone ProductCard)
  - Create cart/CartScreen.tsx (clone ProductScreen)
  - Wire up with useCart hook
  ✅ TEST: Component renders without errors

ITERATION 6: Navigation
  - Add CartScreen to navigator
  - Add "View Cart" button to header
  - Test navigation flow
  ✅ TEST: Navigation works on both platforms

DEPENDENCIES:
  - No new packages needed (reuse existing stack)
</implementation>
</think>
```

---

### Review / Audit

```xml
<think>
<review>
SCOPE: [files/feature to review]

SCAN ORDER (by severity):
1. 🔴 CRITICAL: Crash risks
   - Force unwraps (! / !!)
   - Array access without bounds check
   - Unhandled null from API

2. 🔴 CRITICAL: Security
   - Hardcoded secrets
   - Tokens in AsyncStorage (use SecureStore)
   - SQL injection / XSS vulnerabilities

3. 🟠 HIGH: Memory leaks
   - useEffect without cleanup
   - Listeners not removed
   - Timers not cleared

4. 🟡 MEDIUM: Performance
   - Inline functions in render
   - Missing React.memo
   - ScrollView for long lists (use FlatList)

5. 🟡 MEDIUM: Code quality
   - Missing types (any)
   - Duplicate code
   - Magic numbers/strings

OUTPUT FORMAT:
file:line — severity — issue — fix
</review>
</think>
```

---

### Refactor

```xml
<think>
<refactor>
TARGET: [what to improve]

CONSTRAINTS:
  ✅ NO behavior changes
  ✅ NO new dependencies
  ✅ Match existing conventions
  ✅ All tests must still pass

STEP 1: IMPACT ANALYSIS
  - Files affected: grep -r "[pattern]" src/
  - Dependencies: [what imports this]
  - Tests: find . -name "*.test.*" | grep [pattern]

STEP 2: REFACTOR PLAN
  Priority 1 (Core Logic):
    - [file]: [specific change]

  Priority 2 (Dependents):
    - [file]: [update imports/usage]

  Priority 3 (Tests):
    - [file]: [update test cases]

STEP 3: EXECUTION
  [Execute Priority 1 → run tests → proceed to Priority 2]

STEP 4: VERIFICATION
  ✅ All tests pass
  ✅ TypeScript compiles
  ✅ No new lint errors
  ✅ Git diff review (no unintended changes)
</refactor>
</think>
```

---

## Mobile-Specific Patterns

### Platform-Specific Implementation

```xml
<think>
<mobile_implementation>
FEATURE: [description]
PLATFORM: React Native

CROSS-PLATFORM STRATEGY:
  1. Identify platform differences:
     iOS: [specific behaviors]
     Android: [specific behaviors]

  2. Choose approach:
     [ ] Shared component with Platform.select
     [ ] Separate .ios.tsx and .android.tsx files
     [ ] Native module (requires native code)

EXAMPLE:
// Shared component approach
import { Platform } from 'react-native';

export const DatePicker = () => {
  const Picker = Platform.select({
    ios: () => require('./DatePicker.ios').default,
    android: () => require('./DatePicker.android').default,
  })();

  return <Picker />;
};

TESTING:
  - Jest: Test shared logic
  - Platform-specific: Manual on both devices
  - Edge cases: Different OS versions, screen sizes

CONSIDERATIONS:
  - iOS: Use native UIDatePicker
  - Android: Use native DatePickerDialog
  - Permissions: Different request flows
  - UI: Respect platform design guidelines
</mobile_implementation>
</think>
```

---

### Performance Optimization

```xml
<think>
<optimization>
COMPONENT: [name]

STEP 1: PROFILE
  - Tool: React DevTools Profiler
  - Metric: Render time, re-render count
  - Current: [value] ms per render

STEP 2: ANALYZE
  Root causes:
  - [ ] Expensive computation in render
  - [ ] Inline functions causing re-renders
  - [ ] Missing memoization
  - [ ] Large list without virtualization

STEP 3: OPTIMIZE (priority order)
  1. [ ] React.memo for pure components
  2. [ ] useMemo for expensive computations
  3. [ ] useCallback for stable callbacks
  4. [ ] FlatList with getItemLayout
  5. [ ] Image optimization (resize, cache)

STEP 4: MEASURE
  - Before: [ms] per render
  - After: [ms] per render
  - Improvement: [%]

TRADE-OFFS:
  - Code complexity: [increased/decreased]
  - Bundle size: [KB change]
  - Maintainability: [impact]

DECISION: [proceed / revert / iterate]
</optimization>
</think>
```

---

## Context Management

### Progressive Loading (Don't load everything upfront)

```
Level 1: Always Loaded
  └── SKILL.md (project overview, tech stack)

Level 2: Task-Triggered
  └── Identify reference pattern (don't read yet)

Level 3: File-Specific
  └── Read ONLY files needed for current task

Level 4: Deep Dive
  └── Load detailed docs if stuck

Level 5: Expert
  └── Invoke specialized subagent

⛔ DON'T jump to Level 5 immediately.
✅ DO progress through levels as complexity requires.
```

**Example:**
```xml
<progressive_context>
User: "Add dark mode"

Level 1: Check SKILL.md
  → React Native + TypeScript project
  → Styled with StyleSheet

Level 2: Find pattern
  → grep "theme" src/ --files-with-matches
  → Found: src/theme/theme.ts

Level 3: Read reference
  → Read src/theme/theme.ts
  → Understand current theme structure

Level 4: Implement
  → Clone pattern
  → Add dark mode values
  → No need for Level 5 (straightforward task)
</progressive_context>
```

---

### Just-In-Time File Reading

```xml
<jit_reading>
❌ BAD: Read all files upfront
  Read src/screens/HomeScreen.tsx
  Read src/screens/ProductScreen.tsx
  Read src/screens/CartScreen.tsx
  Read src/screens/ProfileScreen.tsx
  [Load 50+ files → context bloat]

✅ GOOD: Search → Read only relevant
  grep "useAuth" src/screens/ --files-with-matches
  → Found: ProfileScreen.tsx

  Read src/screens/ProfileScreen.tsx
  [Load 1 file → use ~500 tokens instead of 25,000]
</jit_reading>
```

---

### Reference Pattern System

```markdown
BEFORE reading docs, check if a REFERENCE exists:

List Screen     → src/screens/ProductList/
Form Screen     → src/screens/UserProfile/EditProfile
API Integration → src/services/productService.ts
Redux Slice     → src/store/slices/productSlice.ts
Navigation      → src/navigation/RootNavigator.tsx

Clone the reference pattern → modify → test.
Faster than reading documentation.
```

---

## Multi-AI Format

| AI | Think Format | Notes |
|----|-------------|-------|
| Claude | `<think>...</think>` | XML tags preferred |
| Gemini | `## Thinking:` block | Markdown headings |
| Kimi | `【思考】` or markdown | Supports Chinese |
| Cursor | Inline in Composer | Visible to user |
| Copilot | `// PLAN:` comments | Code comments |
| Windsurf | Inline reasoning | Similar to Cursor |

---

## Anti-Patterns (Don't Do This)

```
❌ Vague instructions
   "Make this better"
   "Optimize the app"
   "Fix all bugs"

✅ Specific instructions
   "Reduce ProductList render time from 300ms to <100ms"
   "Fix crash when product.images is undefined"
   "Add pagination to ProductList with 20 items per page"

❌ Over-loading context
   Read all 50 component files upfront

✅ Lazy loading
   Grep → identify → read only relevant files

❌ Skipping verification
   Write code → mark as done

✅ Quality gate
   Write → test → verify → then mark done

❌ Guessing root cause
   "Probably a race condition"

✅ Reading code first
   Read file → analyze flow → identify cause → fix

❌ Generic prompts
   "Create login screen"

✅ Contextual prompts
   "Create login screen following pattern in src/screens/ProductScreen
   using Redux slice from src/store/slices/authSlice
   with email/password fields + remember me checkbox"

❌ Hallucinated answers (AI "intuition")
   "Use react-native-awesome-picker for this"  ← package may not exist
   "Call the fetchUserData() method"            ← function may not exist
   "This API returns { data: [...] }"           ← response shape may be wrong

✅ Grounded answers (verified from source)
   Read package.json → verify package exists → then suggest usage
   Grep "fetchUser" src/ → find actual function → then reference it
   Read API service file → check actual response shape → then use it
```

---

## Advanced Patterns (from top AI tools)

### Verification-First Pattern (Anthropic #1 recommendation)

```
ALWAYS provide verification criteria BEFORE implementation:

<good-example>
  "Add pagination to ProductList. Verify: loads 20 items, next page
   on scroll to bottom, shows loading spinner during fetch, handles
   empty last page. Run: jest --testPathPattern=ProductList"
</good-example>

<bad-example>
  "Add pagination to ProductList"
  (no way to verify success)
</bad-example>

The single highest-leverage thing: include tests or expected outputs
so the agent can check itself.
```

### Investigate-Before-Answer Pattern (used by Cursor, Lovable)

```
NEVER speculate about code you have not opened:

STEP 1: User mentions file → Read it
STEP 2: Understand the actual code → then answer
STEP 3: If referencing a function → Grep to verify it exists

⛔ "The error is probably because..." (guessing)
✅ Read file → find line → "Line 42 accesses product.images[0]
   without null check. The API sometimes returns empty array."
```

### Assumption-Driven Progress (from Cursor — for non-blocking work)

```
When NOT blocked but details are unclear:

✅ State assumption clearly → proceed → let user correct
  "Assuming REST API (matching product feature pattern). Creating
   authService with axios. If this should use Firebase, let me know."

⛔ Ask permission for every small decision
  "Should I use axios or fetch? Should the file be named authService
   or AuthService? Should I put it in services/ or api/?"
```

### Negative Space Pattern (used by ALL top tools)

```
Explicitly state what NOT to do — prevents drift:

⛔ NEVER add new packages without checking existing deps first
⛔ NEVER create utils/ or helpers/ for one-time operations
⛔ NEVER add error handling for scenarios that can't happen
⛔ NEVER refactor surrounding code when fixing a bug
⛔ NEVER add comments to code that is self-explanatory
```

### Batched Operations (from Lovable — reduces tool call waste)

```
COMBINE operations that can run together:

<good-example>
  Read 3 files in ONE message (parallel):
    Read src/features/product/ProductScreen.tsx
    Read src/features/product/productService.ts
    Read src/features/product/product.types.ts
</good-example>

<bad-example>
  Read file 1 → wait → Read file 2 → wait → Read file 3
  (3 round-trips instead of 1)
</bad-example>
```

### Error Recovery with Escalation (from Cursor, Claude Code)

```
ATTEMPT 1: Auto-fix (missing imports, type errors, lint)
ATTEMPT 2: Read related files, check dependencies
ATTEMPT 3: Try alternative approach
ATTEMPT 4: STOP → present options to user

⛔ NEVER: loop on same error 5+ times
⛔ NEVER: suppress errors to make tests pass
✅ If corrected twice on same issue → /clear and restart with better prompt
```

---

## Quick Reference

### Good Prompt Checklist

```
✅ Role defined (Senior React Native developer)
✅ Context provided (tech stack, current state)
✅ Task is specific (what to build, not "make better")
✅ Constraints listed (platform, dependencies, patterns)
✅ Reference pattern identified (clone from X)
✅ Success criteria clear (passes tests + renders)
✅ Output format specified (code + tests + verification)
```

### Before Writing Code

```
1. 🔍 READ existing code (don't guess patterns)
2. 🗺️  IDENTIFY reference to clone
3. 📋 PLAN files to create/modify
4. 🧪 DEFINE how to test/verify
5. ⚠️  CHECK side effects (what else could break)
6. 💻 WRITE code incrementally (test each step)
7. ✅ VERIFY all quality gates pass
```

### When Stuck

```
Instead of:  "I don't know how to do this"
Do this:     grep -r "similar pattern" src/
             Read reference files
             Clone and modify

Instead of:  Load all documentation
Do this:     Start with SKILL.md overview
             Find reference pattern
             Read only needed files
             Load docs only if stuck

Instead of:  Try random fixes
Do this:     Read code → understand flow
             Analyze root cause
             Apply targeted fix
             Verify with tests
```

---

> **Golden Rule:** Think like a senior developer joining a new team.
> Read their code. Follow their patterns. Ask when unclear. Test before shipping.
