# AI-DLC Workflow — Mobile Development

> AI-Driven Development Lifecycle adapted for mobile projects.
> Based on AWS AI-DLC methodology. Use for complex features (3+ screens/units).

---

## When to Activate

| Task | AI-DLC? |
|------|---------|
| Bug fix, single-file change | No — direct fix |
| Add 1 screen, minor feature | No — Feature Scaffold in SKILL.md |
| Multi-screen feature (auth, checkout, onboarding) | **Yes** |
| New project setup / architecture decision | **Yes** |
| Major refactor across multiple files | **Yes** |
| Performance optimization (app-wide) | **Yes** |

**Rule:** If task requires 3+ units of work → use AI-DLC. Otherwise → use normal flow.

---

## Phase 1: Elaboration

**Goal:** Decompose task before writing any code.

### Step 1 — Define Intent

```
Intent: [One sentence describing the goal]
Example: "Auth feature — login, register, forgot password with biometric"
```

### Step 2 — Decompose into Units

Each Unit = 1 deliverable piece (screen, service, config).

```
Units:
  1. [Screen/Component/Service name] — [what it does]
  2. [Screen/Component/Service name] — [what it does]
  ...

Example:
  1. Login screen — email/password form + validation + API call
  2. Register screen — form + password rules + terms checkbox
  3. Forgot password flow — email input → OTP verify → new password
  4. Token storage — SecureStore (RN) / Keychain (iOS) / EncryptedSharedPrefs (Android)
  5. Auth state manager — global auth state + auto-refresh
  6. Navigation guard — redirect unauthenticated users to login
```

### Step 3 — Select Operating Mode

| Mode | When | Human role |
|------|------|-----------|
| **HITL** | New team, unfamiliar codebase, critical feature | Approve each Unit before next |
| **OHOTL** | Familiar codebase, trusted patterns | Monitor, intervene if needed |
| **AHOTL** | Well-defined scope, strong test coverage | Review at end |

**Default for mobile:** HITL (present each Unit for approval).

### Step 4 — Present Plan to User

Before coding, show:
```
Intent: Auth feature
Units: 6 (listed above)
Mode: HITL
Estimated: [X files new, Y files modified]
Platform: [detected framework]

Proceed? (yes / adjust units / change mode)
```

---

## Phase 2: Construction Loop

For each Unit, cycle through 4 Hats:

### Hat 1: Architecture

**Read:** `shared/architecture-intelligence.md` + platform file

- Choose pattern (MVVM, Clean Arch, feature-based)
- Define file structure for this Unit
- Check: does this match existing project patterns?

```
Architecture decision:
  Pattern: [chosen pattern]
  Files to create: [list]
  Files to modify: [list]
  Dependencies: [new packages if any]
```

### Hat 2: Builder

**Read:** Platform file (`react-native/react-native.md`, `flutter/flutter.md`, etc.)

- Write code following platform patterns
- Apply Feature Scaffold Protocol from SKILL.md
- Use existing project conventions (naming, imports, structure)

**Builder rules:**
- One Unit at a time — finish before starting next
- Match existing code style exactly
- No premature abstraction
- Handle all 4 states: loading / error / empty / success

### Hat 3: Security

**Read:** Security rules in SKILL.md + `shared/anti-patterns.md`

Run 7-category scan on the Unit's code:

| Category | Check |
|----------|-------|
| Secrets | No hardcoded keys, tokens, URLs |
| Storage | Tokens in SecureStore/Keychain only |
| Input | User input sanitized before display |
| Network | HTTPS only, no cleartext |
| Data | No PII in logs, no sensitive data exposed |
| Auth | Token refresh, session expiry handled |
| Platform | iOS ATS, Android ProGuard, exported components |

**If any violation found → BLOCK Unit. Fix before proceeding.**

### Hat 4: Reviewer

**Read:** `shared/code-review.md` + `shared/common-pitfalls.md`

Self-review checklist:
- [ ] Clean Architecture respected (UI → Domain → Data)
- [ ] Single responsibility (max 300 lines per file)
- [ ] No console.log / print in production
- [ ] Error handling complete (try/catch, error states)
- [ ] Navigation registered
- [ ] Types complete (no implicit any)
- [ ] Platform-specific edge cases handled
- [ ] Accessibility basics (labels, contrast)

**If review fails → return to Builder Hat. Fix, then re-review.**

### Unit Complete

```
Unit [N]: [name]
  Status: ✅ complete
  Files created: [list]
  Files modified: [list]
  Security: passed
  Review: passed
  → Proceed to Unit [N+1]
```

---

## Phase 3: Backpressure Gates

Quality gates that **block** progress automatically:

```
Gate 1: TypeScript / Dart / Kotlin compiler  → must pass
Gate 2: Lint (ESLint / flutter analyze)       → must pass
Gate 3: Security scan (Hat 3)                 → must pass
Gate 4: Self-review (Hat 4)                   → must pass
Gate 5: Unit test (if test file exists)       → must pass
```

**Backpressure rule:** If any gate fails, the Builder Hat fixes the issue before moving to the next Unit. Max 3 fix attempts per gate — if still failing, ask user.

---

## Phase 4: Completion

When all Units are done:

```
Intent: [name]
  Units: [N] completed
  Files created: [list all]
  Files modified: [list all]
  Security: all Units passed
  Review: all Units passed

  Remaining:
  - [ ] Run full test suite
  - [ ] Test on both platforms (if cross-platform)
  - [ ] Verify navigation flow end-to-end
```

---

## Mobile-Specific Adaptations

### Cross-Platform Units

For React Native / Flutter projects, each screen Unit should verify:
- iOS rendering (safe area, notch, Dynamic Island)
- Android rendering (back button, status bar, edge-to-edge)
- Both platform navigation behaviors

### Native Module Units

When Unit involves native code (camera, biometric, push):
1. Builder Hat writes JS/Dart bridge first
2. Builder Hat writes iOS native (Swift/ObjC)
3. Builder Hat writes Android native (Kotlin/Java)
4. Security Hat checks permissions on both platforms

### State Management Units

Architecture Hat decides ONCE, applies to all Units:
- RN: Redux Toolkit / Zustand / Jotai / TanStack Query
- Flutter: Riverpod / BLoC / Provider
- iOS: TCA / Observable / Combine
- Android: StateFlow / LiveData

Never mix state management within one Intent.

---

## Hat ↔ Skill File Mapping

| Hat | Primary file | Secondary file |
|-----|-------------|---------------|
| Architecture | `shared/architecture-intelligence.md` | Platform file |
| Builder | Platform file (RN/Flutter/iOS/Android) | `shared/offline-first.md` (if offline) |
| Security | SKILL.md § Security | `shared/anti-patterns.md` |
| Reviewer | `shared/code-review.md` | `shared/common-pitfalls.md` |

---

> AI-DLC for mobile: Elaborate → Construct (4 Hats per Unit) → Backpressure gates → Complete.
> Default mode: HITL. Activate when task ≥ 3 units. Skip for bug fixes and small changes.
