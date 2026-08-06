# Agent Rules Template — All Agents

> Each AI agent reads a specific project-level file automatically every session.
> Copy the relevant section below to your project root.

---

## Quick Reference

| Agent | File to create | Location |
|-------|---------------|----------|
| **Claude Code** | `CLAUDE.md` | Project root |
| **Cursor** | `.cursorrules` | Project root |
| **Windsurf** | `.windsurfrules` | Project root |
| **GitHub Copilot** | `.github/copilot-instructions.md` | `.github/` folder |
| **Codex (OpenAI)** | `AGENTS.md` | Project root |
| **Gemini CLI** | `GEMINI.md` | Project root |
| **Kimi** | No auto-load file — paste rules as context | — |
| **Antigravity** | Configured in Antigravity YAML `context.rules` | Agent config |

---

## Claude Code → `CLAUDE.md`

```markdown
# Project: [Your App Name]

## Stack
- Framework: [React Native CLI / Expo SDK XX / Flutter X.X / iOS / Android]
- Language: [TypeScript / JavaScript / Dart / Swift / Kotlin]
- State: [Redux Toolkit / Zustand / Riverpod / BLoC / StateFlow]
- Navigation: [React Navigation v6 / Expo Router / GoRouter / UIKit / Jetpack]
- API: [axios / fetch / Dio / Firebase / GraphQL]
- Package Manager: [yarn / npm / pnpm / bun / flutter pub]

## Auto-Check Rules (apply after EVERY code change)

Before saying "done", verify:
- No console.log / print / NSLog in production code
- No hardcoded secrets or API keys
- All async operations wrapped in try/catch
- All 4 states handled: loading / error / empty / success
- useEffect / dispose / viewModelScope has cleanup
- FlatList (not ScrollView) for lists > 20 items
- No force unwrap (! / !! / as!) without null check
- TypeScript: no implicit 'any'
- New screens registered in navigator

If ANY check fails → fix it before marking done.

## What NOT to do
- NEVER suggest migrating to a different framework
- NEVER change state management library
- NEVER add packages without checking SDK compatibility
- NEVER mix package managers (yarn + npm)
```

---

## Cursor → `.cursorrules`

```
# [Your App Name] — Cursor Rules

## Project
- Framework: [React Native CLI / Expo SDK XX / Flutter X.X / iOS / Android]
- Language: [TypeScript / Dart / Swift / Kotlin]
- State: [Redux Toolkit / Zustand / Riverpod / BLoC]
- Package Manager: [yarn / npm / bun / flutter pub]

## Code Style
- PascalCase for screens and components
- camelCase for hooks, services, utils
- Absolute imports with @/ alias (if configured)

## Auto-Check (before every completion)
- No console.log in production code
- No hardcoded secrets or API keys
- All async wrapped in try/catch
- All 4 states: loading / error / empty / success
- useEffect has cleanup (return () => ...)
- FlatList (not ScrollView) for dynamic lists
- No implicit 'any' in TypeScript

## Never
- Change framework or architecture
- Change state management library
- Add packages without checking SDK compatibility
- Mix package managers
```

---

## Windsurf → `.windsurfrules`

```
# [Your App Name] — Windsurf Rules

Project: [Your App Name]
Framework: [React Native CLI / Expo / Flutter / iOS / Android]
Language: [TypeScript / Dart / Swift / Kotlin]
State management: [Redux Toolkit / Zustand / Riverpod / BLoC]
Package manager: [yarn / npm / bun / flutter pub]

## Coding Rules

Always:
- Wrap all async operations in try/catch
- Handle all 4 states: loading, error, empty, success
- Add cleanup to useEffect (return () => ...)
- Use FlatList for dynamic lists (not ScrollView)
- Use PascalCase for components and screens
- Use camelCase for hooks, services, and utilities
- No implicit 'any' in TypeScript

Never:
- Leave console.log in production code
- Hardcode secrets, tokens, or API keys
- Store tokens in AsyncStorage / SharedPreferences / UserDefaults
- Change the framework or architecture
- Add packages without verifying SDK compatibility
- Mix yarn and npm

## Security (non-negotiable)
- Tokens → SecureStore / Keychain / EncryptedSharedPreferences
- API calls → HTTPS only
- Sensitive data → never in logs
- User input → sanitize before display
```

---

## GitHub Copilot → `.github/copilot-instructions.md`

```markdown
# Copilot Instructions — [Your App Name]

## Project Context
- **Framework:** [React Native CLI / Expo SDK XX / Flutter X.X / iOS / Android]
- **Language:** [TypeScript / JavaScript / Dart / Swift / Kotlin]
- **State Management:** [Redux Toolkit / Zustand / Riverpod / BLoC]
- **Package Manager:** [yarn / npm / bun / flutter pub]

## Conventions
- PascalCase: components, screens, classes
- camelCase: hooks, services, utilities, variables
- Files named same as their default export

## Required Patterns

### Every async function
```typescript
try {
  setLoading(true);
  const result = await apiCall();
  setData(result);
} catch (error) {
  setError(error.message);
} finally {
  setLoading(false);
}
```

### Every screen must handle 4 states
```typescript
if (loading) return <LoadingScreen />;
if (error) return <ErrorScreen error={error} />;
if (!data?.length) return <EmptyScreen />;
return <DataScreen data={data} />;
```

### Every useEffect with subscriptions
```typescript
useEffect(() => {
  const sub = subscribe();
  return () => sub.unsubscribe(); // REQUIRED
}, []);
```

## Rules
- No console.log in production
- No hardcoded secrets or API keys
- FlatList (not ScrollView) for dynamic lists
- Tokens in SecureStore / Keychain only
- No force unwrap without null check
- No implicit 'any' in TypeScript
```

---

## Codex (OpenAI) → `AGENTS.md` (project root)

```markdown
# [Your App Name] — Agent Rules

## Project
- Framework: [React Native / Expo / Flutter / iOS / Android]
- Language: [TypeScript / Dart / Swift / Kotlin]
- State: [Redux Toolkit / Zustand / Riverpod / BLoC]
- Package Manager: [yarn / npm / bun / flutter pub]

## Rules for All Tasks

### Always
- Wrap async in try/catch
- Handle: loading / error / empty / success states
- Cleanup useEffect (return unsubscribe/cancel)
- Use FlatList for dynamic lists
- PascalCase components, camelCase hooks/services

### Never
- console.log in production
- Hardcode secrets or API keys
- Store tokens in AsyncStorage (use SecureStore/Keychain)
- Suggest changing framework or state management
- Add packages without verifying SDK compatibility
- Mix yarn and npm

### Security
- Tokens → SecureStore (RN) / Keychain (iOS) / EncryptedSharedPreferences (Android)
- API → HTTPS only
- Logs → never include sensitive data
- Input → sanitize before display

## Architecture
[FILL IN: describe your feature structure]
Example: feature-based (src/features/auth/, src/features/home/)

## Preferred Commands
- Install: [yarn install / npm install / flutter pub get]
- Run: [yarn ios / yarn android / flutter run]
- Test: [yarn test / flutter test]
```

---

## Gemini CLI → `GEMINI.md`

```markdown
# [Your App Name] — Gemini Rules

## Project Stack
- Framework: [React Native / Expo / Flutter / iOS / Android]
- Language: [TypeScript / Dart / Swift / Kotlin]
- State: [Redux Toolkit / Zustand / Riverpod / BLoC]
- Package Manager: [yarn / npm / bun / flutter pub]

## Code Quality Rules

Apply before every completion:

1. No console.log / print / NSLog in production
2. No hardcoded API keys, tokens, or secrets
3. All async wrapped in try/catch with proper error handling
4. All 4 states implemented: loading / error / empty / success
5. useEffect cleanup present when using subscriptions or timers
6. FlatList used for lists (not ScrollView with map)
7. TypeScript: no implicit 'any'
8. New screens registered in the navigator

## Security Rules
- Token storage: SecureStore / Keychain / EncryptedSharedPreferences ONLY
- API calls: HTTPS only
- Logs: no sensitive data
- User input: sanitize before rendering

## Constraints
- Do not change framework or architecture
- Do not change state management library
- Do not add packages without checking SDK compatibility
- Do not mix package managers
```

---

## Kimi — No Auto-Load

Kimi does not read a project file automatically. Options:

**Option 1 — Paste at start of conversation:**
```
Project rules:
- Framework: [React Native / Flutter / iOS / Android]
- No console.log in production
- All async in try/catch
- All 4 states: loading/error/empty/success
- Tokens in SecureStore/Keychain only
- No implicit 'any' in TypeScript
- Do not change framework or state management
```

**Option 2 — Use skill-mobile-mt:**
Load SKILL.md as context at the start of the Kimi conversation.

---

## Antigravity — YAML Config

Add to your Antigravity configuration:

```yaml
skill:
  name: skill-mobile-mt
  version: "1.0.0"

context:
  rules:
    - No console.log / print / NSLog in production code
    - No hardcoded secrets or API keys
    - Tokens in SecureStore / Keychain / EncryptedSharedPreferences ONLY
    - All async wrapped in try/catch
    - All 4 states handled: loading / error / empty / success
    - useEffect / dispose / viewModelScope has cleanup
    - FlatList (not ScrollView) for dynamic lists
    - No implicit 'any' in TypeScript

  project:
    framework: "[react-native / flutter / ios / android]"
    language: "[typescript / dart / swift / kotlin]"
    state_management: "[redux / zustand / riverpod / bloc]"
    package_manager: "[yarn / npm / bun / flutter-pub]"

  constraints:
    - NEVER suggest migrating to a different framework
    - NEVER change state management library
    - NEVER add packages without checking SDK compatibility
    - NEVER mix package managers
```

---

## Summary

| Agent | Auto-loaded? | File |
|-------|-------------|------|
| Claude Code | YES — every session | `CLAUDE.md` |
| Cursor | YES — every chat | `.cursorrules` |
| Windsurf | YES — every session | `.windsurfrules` |
| GitHub Copilot | YES — workspace context | `.github/copilot-instructions.md` |
| Codex | YES — when AGENTS.md exists | `AGENTS.md` |
| Gemini CLI | YES — when GEMINI.md exists | `GEMINI.md` |
| Kimi | NO — paste manually | (none) |
| Antigravity | YES — via YAML config | Antigravity config |
