# @buivietphi/skill-mobile-mt

**Master Senior Mobile Engineer** — AI skill for Claude Code, Cline, Roo Code, Cursor, Windsurf, Copilot, Codex, Gemini CLI, Kimi, Kilo Code, Kiro, and Antigravity.

Pre-built architecture patterns from **30+ production repos (200k+ GitHub stars)** including Ignite, Expensify, Mattermost, Immich, AppFlowy, Now in Android, TCA. Trained from research of **top 53k+ star skill repos** (everything-claude-code, awesome-cursorrules, planning-with-files, Lovable, Cursor, Manus Agent prompts). Auto-adaptation to your current project.

## Install

```bash
npx @buivietphi/skill-mobile-mt
```

Interactive checkbox UI — detects which AI agents are installed, lets you select with arrow keys + space.

### Install to specific agents

```bash
npx @buivietphi/skill-mobile-mt --claude       # Claude Code
npx @buivietphi/skill-mobile-mt --codex        # Codex
npx @buivietphi/skill-mobile-mt --gemini       # Gemini CLI
npx @buivietphi/skill-mobile-mt --kimi         # Kimi
npx @buivietphi/skill-mobile-mt --antigravity  # Antigravity
npx @buivietphi/skill-mobile-mt --all          # All agents
npx @buivietphi/skill-mobile-mt --path ./dir   # Custom directory
```

### Generate project-level rules

Cline, Roo Code, Cursor, Windsurf, Copilot, Kilo Code, and Kiro read rules from **project-level files**. Run `--init` inside your project to generate them:

```bash
npx @buivietphi/skill-mobile-mt --init            # Interactive selector
npx @buivietphi/skill-mobile-mt --init cursor     # .cursorrules
npx @buivietphi/skill-mobile-mt --init cline      # .clinerules/mobile-rules.md
npx @buivietphi/skill-mobile-mt --init roocode    # .roo/rules/mobile-rules.md
npx @buivietphi/skill-mobile-mt --init copilot    # .github/copilot-instructions.md
npx @buivietphi/skill-mobile-mt --init windsurf   # .windsurfrules
npx @buivietphi/skill-mobile-mt --init kilocode   # .kilocode/rules/mobile-rules.md
npx @buivietphi/skill-mobile-mt --init kiro       # .kiro/steering/mobile-rules.md
npx @buivietphi/skill-mobile-mt --init all        # All files
```

**What `--init` does:**
1. Auto-detects your project (framework, language, state management, navigation, API client, package manager)
2. Generates rules files pre-filled with your detected stack
3. Includes mobile best practices, security rules, and quality gates
4. Won't overwrite existing files (safe to run multiple times)

## Usage

### Mode 1: Pre-Built Architecture (default)

```
@skill-mobile-mt
```

Uses battle-tested patterns from 30+ production repos:
- **React Native** — Ignite (19.7k stars), Obytes Template, Expensify/App, Mattermost Mobile, Artsy Eigen
- **Flutter** — Immich (93.5k stars), AppFlowy (68.2k), Spotube (44.6k), Hiddify, Ente Photos
- **iOS** — TCA / Point-Free (14.4k), Clean Arch SwiftUI, Modern Clean Arch
- **Android** — Now in Android (20.7k), Android Showcase, Mihon (18.8k)

### Mode 2: Adapt to Your Project (project)

```
@skill-mobile-mt project
```

Reads your current project first, then follows **your** conventions:
- Detects framework, language, package manager, state management, navigation
- Matches your naming, imports, file structure, patterns
- Clones the most similar existing feature when scaffolding new ones
- Never suggests migrations or imposes different architecture

## Quick Start Examples

### Step 1: Install the skill

```bash
# Install globally (one-time setup)
npx @buivietphi/skill-mobile-mt
```

You'll see an interactive checkbox — use arrow keys to navigate, space to select, Enter to confirm:

```
  Select agents to install:
  ↑↓ navigate   Space toggle   A select all   Enter confirm   Q cancel

  › ◉ Claude Code   [detected]
    ◯ Cline          [detected]
    ◯ Roo Code       [not found]
    ◯ Cursor         [detected]
    ◯ Windsurf       [not found]
    ◯ Copilot        [not found]
    ◯ Codex          [not found]
    ◉ Gemini CLI     [detected]
    ◯ Kimi           [not found]
    ◯ Kilo Code      [not found]
    ◯ Kiro           [not found]
    ◯ Antigravity    [not found]
```

Install output:

```
  ✓ skill-mobile-mt/    → Claude Code  (~/.claude/skills/skill-mobile-mt)
  ✓ humanizer-mobile/   → Claude Code  (~/.claude/skills/humanizer-mobile)
```

Both are installed automatically. Use `@humanizer-mobile` for app store copy, release notes, and UX text.

### Step 2: Generate project rules

```bash
# cd into your mobile project first
cd ~/projects/my-app

# Generate rules for your agents
npx @buivietphi/skill-mobile-mt --init all
```

Output:

```
  📁 Project directory: /Users/you/projects/my-app
  🔍 Detected: Expo (React Native) (TypeScript)

  ✓ .cursorrules → Cursor (auto-detected: Expo (React Native))
  ✓ .github/copilot-instructions.md → GitHub Copilot
  ✓ .clinerules/mobile-rules.md → Cline
  ✓ .roo/rules/mobile-rules.md → Roo Code
  ✓ .kilocode/rules/mobile-rules.md → Kilo Code
  ✓ .kiro/steering/mobile-rules.md → Kiro
  ✓ .windsurfrules → Windsurf

  ✅ Done! → 7 file(s) generated
```

### Step 3: Use in your AI agent

#### Claude Code

```bash
# In Claude Code terminal, type:
@skill-mobile-mt

# Then ask anything:
> Create auth feature with login and register screens

# Or with project mode (reads YOUR code first):
@skill-mobile-mt project
> Add cart feature following the same pattern as ProductList
```

#### Cline / Roo Code / Kilo Code

After running `--init cline` (or `roocode`, `kilocode`), rules are auto-loaded from the project directory. Just open your project and ask:

```
> Create a login screen with email/password
> Fix the crash in ProductDetail when images is null
> Review this PR for mobile best practices
```

#### Cursor

After running `--init cursor`, Cursor auto-loads `.cursorrules` every session. Just open your project and code normally.

#### Kiro (AWS)

After running `--init kiro`, Kiro loads `.kiro/steering/mobile-rules.md` as steering context. The generated file uses `inclusion: always` frontmatter.

#### GitHub Copilot

After running `--init copilot`, Copilot reads `.github/copilot-instructions.md` as workspace context.

#### Windsurf

After running `--init windsurf`, Windsurf auto-loads `.windsurfrules`. Just code normally.

#### Gemini CLI

```bash
# In Gemini CLI:
@skill-mobile-mt
> Setup a new Flutter project with Riverpod + clean architecture
```

#### Codex / Kimi / Antigravity

Same as Claude Code — the skill is loaded from the skills directory.

### Example Prompts (all agents)

| What you want | What to type |
|--------------|-------------|
| New feature | `Create auth feature with login, register, forgot password` |
| New screen | `Add settings screen with profile, notifications, theme toggle` |
| Fix bug | `Fix crash when product.images is undefined` |
| Code review | `Review src/features/cart/ for mobile best practices` |
| Performance | `Optimize ProductList — it's janky when scrolling 100+ items` |
| Architecture | `Setup project structure for a new Expo app with Zustand + TanStack Query` |
| Release | `Prepare the app for App Store submission` |
| Security | `Audit the auth flow for security vulnerabilities` |

## Auto-Detect

The skill automatically detects before any action:

| What | How |
|------|-----|
| **Framework** | `pubspec.yaml` → Flutter, `package.json` with `react-native` → RN, `*.xcodeproj` → iOS, `build.gradle` → Android |
| **Language** | `.dart` → Dart, `.tsx/.ts` → TypeScript, `.swift` → Swift, `.kt` → Kotlin |
| **Package Manager** | `yarn.lock` → yarn, `pnpm-lock.yaml` → pnpm, `package-lock.json` → npm, `pubspec.lock` → flutter pub |
| **State Management** | Redux / MobX / Zustand / Riverpod / BLoC / StateFlow / Combine |
| **Navigation** | React Navigation / Expo Router / GoRouter / NavigationStack |

## Smart Loading

Only loads the relevant platform docs — saves **~45% context tokens** vs loading everything.

```
Flutter project?
  → Load: flutter/flutter.md + ios/ + android/ + shared/
  → Skip: react-native/

React Native project?
  → Load: react-native/react-native.md + ios/ + android/ + shared/
  → Skip: flutter/

iOS only?
  → Load: ios/ios-native.md + shared/
  → Skip: flutter/ + react-native/ + android/
```

## Context Cost

| Scenario | Tokens | % of 128K | % of 200K |
|----------|-------:|----------:|----------:|
| SKILL.md only | ~25,150 | 19.6% | 12.6% |
| **Smart load (recommended)** | **~53,350 – 57,350** | **42% – 45%** | **27% – 29%** |
| Cross-platform (RN+Flutter+iOS+Android) | ~95,350 | 74.5% | 47.7% |
| All files loaded | ~166,380 | 130.0% | 83.2% |
| | | *exceeds 128K* | *fits 200K* |

### Per-file token breakdown

| File | Tokens |
|------|-------:|
| `SKILL.md` | ~25,150 |
| `AGENTS.md` | ~6,440 |
| `react-native/react-native.md` | ~5,840 |
| `flutter/flutter.md` | ~2,350 |
| `ios/ios-native.md` | ~1,660 |
| `android/android-native.md` | ~4,370 |
| `shared/code-review.md` | ~11,600 |
| `shared/bug-detection.md` | ~7,290 |
| `shared/debugging-intelligence.md` | ~8,730 |
| `shared/prompt-engineering.md` | ~7,440 |
| `shared/architecture-intelligence.md` | ~3,860 |
| `shared/common-pitfalls.md` | ~1,330 |
| `shared/error-recovery.md` | ~2,780 |
| `shared/document-analysis.md` | ~1,520 |
| `shared/release-checklist.md` | ~670 |
| `shared/anti-patterns.md` | ~2,910 |
| `shared/performance-prediction.md` | ~1,310 |
| `shared/platform-excellence.md` | ~1,890 |
| `shared/version-management.md` | ~3,660 |
| `shared/observability.md` | ~5,750 |
| `shared/offline-first.md` | ~2,930 |
| `shared/testing-strategy.md` | ~2,500 |
| `shared/ci-cd.md` | ~2,830 |
| `shared/ai-dlc-workflow.md` | ~1,950 |
| `shared/ui-ux-mobile.md` | ~6,910 |
| `shared/storage-patterns.md` | ~2,760 |
| `shared/i18n-localization.md` | ~3,140 |
| `shared/intent-analysis.md` | ~6,250 |
| `shared/code-generation-templates.md` | ~5,370 |
| `shared/spec-to-code.md` | ~2,640 |
| `shared/navigation-patterns.md` | ~2,900 |
| `shared/complex-ui-patterns.md` | ~3,810 |
| `shared/data-flow-patterns.md` | ~3,250 |
| `shared/error-handling.md` | ~2,960 |
| `shared/testing-patterns.md` | ~3,410 |
| `shared/claude-md-template.md` | ~1,050 |
| `shared/agent-rules-template.md` | ~2,870 |
| `humanizer/humanizer-mobile.md` | ~2,630 |
| **Total** | **~166,380** |

## Installed Structure

```
~/.claude/skills/               (or ~/.cline/skills/, ~/.roo/skills/, ~/.gemini/skills/, etc.)
└── skill-mobile-mt/
    ├── SKILL.md                       Entry point + auto-detect + quality gates
    ├── AGENTS.md                      Multi-agent compatibility
    ├── react-native/
    │   └── react-native.md            React Native + Expo patterns
    ├── flutter/
    │   └── flutter.md                 Flutter + Dart patterns
    ├── ios/
    │   └── ios-native.md              iOS Swift patterns
    ├── android/
    │   └── android-native.md          Android Kotlin + Java patterns
    └── shared/
        ├── code-review.md             Senior review checklist
        ├── bug-detection.md           Auto bug scanner (4 modes + git-aware)
        ├── debugging-intelligence.md  30+ error patterns + root cause tracing
        ├── prompt-engineering.md      Auto-think + prompt templates
        ├── architecture-intelligence.md  Patterns from 30+ production repos
        ├── common-pitfalls.md         Problem → Symptoms → Solution
        ├── error-recovery.md          16 build/runtime error fixes
        ├── document-analysis.md       Parse docs/images → code
        ├── anti-patterns.md           PII, cardinality, payload detection
        ├── performance-prediction.md  Frame budget, FPS prediction
        ├── platform-excellence.md     iOS 18+ vs Android 15+ guidelines + HIG
        ├── version-management.md      SDK compatibility matrix
        ├── observability.md           Sessions as 4th pillar
        ├── release-checklist.md       Pre-release verification
        ├── offline-first.md           Local-first + sync patterns
        ├── storage-patterns.md        Storage selection matrix (AsyncStorage/MMKV/SQLite/etc.)
        ├── i18n-localization.md       Internationalization + RTL + locale patterns
        ├── testing-strategy.md        Detox + Maestro + XCUITest + Espresso E2E
        ├── ci-cd.md                   GitHub Actions CI/CD templates
        ├── ai-dlc-workflow.md         AI-DLC structured dev workflow
        ├── ui-ux-mobile.md            Design system + screen templates + touch + navigation
        ├── claude-md-template.md      CLAUDE.md template for projects
        └── agent-rules-template.md    Rules templates for all agents
```

### Project-level files (generated by `--init`)

```
your-project/
├── .cursorrules                       Cursor rules (auto-detected stack)
├── .windsurfrules                     Windsurf rules (auto-detected stack)
├── .clinerules/
│   └── mobile-rules.md               Cline rules (auto-detected stack)
├── .roo/
│   └── rules/
│       └── mobile-rules.md           Roo Code rules (auto-detected stack)
├── .kilocode/
│   └── rules/
│       └── mobile-rules.md           Kilo Code rules (auto-detected stack)
├── .kiro/
│   └── steering/
│       └── mobile-rules.md           Kiro steering (auto-detected stack)
└── .github/
    └── copilot-instructions.md        Copilot rules (auto-detected stack)
```

## What's Included

### Clean Architecture & SOLID
- Dependencies flow inward (UI → Domain → Data)
- Single responsibility per file (max 300 lines)
- Dependency injection, no hardcoded singletons

### Code Review Protocol (12-category, PR-level)
- **PR-Level Review**: size check, single responsibility, test accompaniment, commit hygiene — BEFORE code review
- **12 categories**: architecture, correctness, boundary conditions, test quality, readability, performance, security (expanded), accessibility (WCAG 2.1), breaking changes, platform, documentation, i18n
- **Severity levels**: Critical / High / Medium / Low with structured output format
- **Auto-fail patterns**: 10 code + 4 PR-level + 7 AI-specific grounding checks
- **Review output**: PR-level summary → findings by severity → verdict (APPROVE / CHANGES REQUESTED)
- **Boundary conditions**: null, empty, off-by-one, numeric limits, unicode, timezone — dedicated dimension
- **Accessibility**: touch targets (44pt/48dp), contrast ratios, screen reader, font scaling, focus management
- **Breaking change detection**: public API, deep links, DB schema, push payload, analytics events
- **Security depth**: certificate pinning, JWT lifecycle, bridge security, biometric auth, dependency audit
- **Grounded review (anti-false-positive)**: verify every finding before flagging — check actual installed APIs, don't flag from memory, confidence levels (high/medium/low)
- **Practical usage review**: 25 production crash patterns — 5 cross-platform + 5 React Native + 5 Flutter + 5 iOS Swift + 5 Android Kotlin
- **Library-specific traps**: React Native, Flutter, iOS Swift, Android Kotlin — real gotchas per platform
- **Cross-platform examples**: before/after code for all 4 platforms (not just RN)

### Bug Detection Scanner
- 4 debug modes: Error Analysis, Fix Bug, Investigate, Diagnostic Scan
- Git-aware debugging: checks recent commits before deep-diving (auto-skips if no git)
- 4-phase fix protocol: Root Cause → Pattern Analysis → Single Hypothesis → Defense in Depth
- 45+ error pattern database with exact search strategies — RN (7) + Flutter (6) + iOS Swift (5) + Android Kotlin (6) + Network (4) + State (3) + Navigation (2) + Build (4) + Platform (3)
- Anti-rationalization table: catches self-deception during debugging

### Decision Matrix Protocol
- Structured comparison format when multiple valid approaches exist
- Estimation protocol: classify effort XS/S/M/L/XL with risk assessment
- Migration/upgrade decision protocol: breaking changes analysis + impact scan

### Codebase Scan Strategy
- 3 scan levels: Quick (~5 reads), Standard (~15 reads), Deep (~30+ reads)
- Monorepo strategy: focus target package, scan shared deps
- Multi-module strategy: JS/TS vs Native vs Cross-layer task detection

### Grounding Protocol (Anti-Hallucination)
- **Source hierarchy**: project code > skill files > official docs > production repos > AI knowledge
- **Mandatory rules**: Read before answer, verify APIs exist, cite sources, say "I don't know" when unsure
- **No phantom packages**: verify package exists in package.json before suggesting
- **Version-specific**: check actual SDK version, never assume latest
- **Grounded bug fix**: read file → find exact line → verify types → cite source
- **Anti-hallucination checklist**: runs before every AI response

### Docs-First Protocol (Always Use Latest)
- **WebSearch before coding**: when setting up any library, ALWAYS search official docs first
- **Never rely on AI memory**: docs change, APIs change, syntax changes between versions
- **Package installation protocol**: verify exists → check compatibility → search install guide → test both platforms
- **Common AI traps**: React Navigation v5 vs v7, Firebase v8 vs v9 modular, Swift async/await availability
- **Version matrix + live verification**: snapshot matrix in skill + mandatory WebSearch for current data

### Security Protocol
- **7-category security scan** on every feature: secrets, token storage, input validation, network, data protection, auth flow, platform-specific
- **6 absolute rules**: never store tokens in plain storage, never hardcode secrets, never log sensitive data, never trust deep links, never disable SSL, never commit .env
- **Platform-specific checks**: iOS ATS + privacy manifest, Android cleartext + ProGuard + exported components
- **Never skip security**: even for prototypes, internal apps, or "quick fixes"

### Advanced AI Patterns (from top 53k+ star repos + Lovable, Cursor, Manus prompts)
- **7 Cardinal Rules**: Inviolable rules at the top of SKILL.md (read before write, verify before done, clone before create, cite source, 4 states always, platform parity, ask after 3 fails)
- **Self-Critique Loop**: Generate → Review own code → Refine → Verify (catch bugs before "done")
- **Context Staleness Rule**: Re-read files after 5+ messages (from Cursor's pattern)
- **Parallel Execution**: Default to parallel tool calls unless sequential dependency
- **Leverage Pyramid**: Research → Planning → Implementation (review plans, not just code)
- **Session State Tracking**: Structured progress tracking for long multi-file tasks
- **Verification-First**: Include test criteria BEFORE implementation (Anthropic's #1 recommendation)
- **Assumption-Driven Progress**: State assumptions → proceed → let user correct (don't ask for every decision)
- **Negative Space Pattern**: Explicit NEVER rules prevent drift better than positive instructions
- **Brevity Default**: 1-line status updates, detail only when asked (from Lovable, Claude Code)
- **Error Recovery Protocol**: Max 3 attempts with escalation, then ask user
- **Build & Deploy Gates**: Platform-specific pre-completion checklists
- **Mobile Anti-Patterns**: Common mistakes from AI tools (and how to avoid them)

### Intelligent Prompt Engineering
- Trained from 7 major AI tools' system prompts (Lovable, Cursor, Manus, Windsurf, Kiro, Replit, Claude Code)
- XML tag structure for clarity (`<task>`, `<context>`, `<instructions>`, `<constraints>`)
- Enhanced auto-think templates with pre-action validation
- Progressive context loading (5 levels: overview → pattern → files → docs → expert)
- Just-in-time file reading (grep first, read only needed)
- Reference pattern system (clone existing instead of reading docs)
- Multi-AI format support (Claude, Gemini, Kimi, Cursor, Copilot, Windsurf)
- Advanced patterns: verification-first, investigate-before-answer, batched operations, negative space

### Document Analysis
- Parse images (mockups, wireframes), PDFs (requirements), DOCX, XML, JSON
- UI Analysis: extract layout, components, styling, states from screenshots
- Requirements Extraction: user stories, screen flows, data models, business rules
- Document → Code pipeline: read → extract → map features → scaffold

### Architecture Intelligence (from 30+ production repos)

- **Architecture Intelligence** (`architecture-intelligence.md`): Cross-platform patterns from Ignite, Immich, AppFlowy, TCA, Now in Android and more. Includes: dual state management, feature-based modules, bootstrap/startup pattern, functional error handling, architecture validation (Konsist), production folder structure templates, and decision matrices for state/nav/testing.

### Production Patterns (from Senaiverse, Mhuxain, VoltAgent, Nexus)

- **Anti-Pattern Detection** (`anti-patterns.md`): Detect PII leaks (CRITICAL), high cardinality tags, unbounded payloads, unstructured logs, sync telemetry on main thread — with auto-fix suggestions
- **Performance Prediction** (`performance-prediction.md`): Calculate frame budget, FlatList bridge calls, and memory usage BEFORE writing code. Example: `50 items × 3 bridge calls × 0.3ms = 45ms/frame → 22 FPS ❌ JANK`
- **Platform Excellence** (`platform-excellence.md`): iOS 18+ vs Android 15+ native UX standards — navigation patterns, typography, haptic feedback types, permission timing, ratings prompt flow, Live Activities/Dynamic Island, performance targets (cold start < 1s iOS, < 1.5s Android)
- **Version Management** (`version-management.md`): Full SDK compatibility matrix for RN 0.73-0.76, Expo 50-52, Flutter 3.22-3.27, iOS 16-18, Android 13-15. Check SDK compat BEFORE `npm install`. Release-mode testing protocol.
- **Observability** (`observability.md`): Sessions as the 4th pillar (Metrics + Logs + Traces + **Sessions**). Session lifecycle, enrichment API, unified instrumentation stack, correlation queries. Every event carries `session_id` for full user journey reconstruction.

### UI/UX Mobile Design
- Screen templates with ASCII wireframes: Login, Home/Feed, Detail, Profile/Settings, Onboarding
- Design tokens system (colors, spacing, radius, shadows, typography) for RN and Flutter
- Component patterns: bottom sheet, empty state, loading skeleton, toast/snackbar
- Touch targets (44pt iOS / 48dp Android), dark mode implementation, animation guidelines
- Accessibility checklist (screen reader labels, contrast ratios, font scaling)
- Device sizing reference table (iPhone SE → Pro Max, Android small → large, iPad)

### AI-DLC Workflow (AI-Driven Development Lifecycle)
- Based on AWS AI-DLC methodology — structured development for complex features
- **Elaboration**: decompose task into Intent + Units before coding
- **Construction loop**: 4 Hats per Unit (Architecture → Builder → Security → Reviewer)
- **Backpressure gates**: compiler, lint, security, review must pass before next Unit
- **Operating modes**: HITL (human approves each Unit), OHOTL, AHOTL
- Auto-activates for multi-screen features (3+ units); skips for bug fixes

### Error Recovery
- 16 common build/runtime errors with concrete fixes
- Platform-specific solutions (RN CLI, Expo, Flutter, iOS, Android)
- General recovery protocol for systematic debugging

### Release & Review
- Pre-release checklist for App Store and Play Store submissions
- Common pitfalls with Problem → Symptoms → Solution format
- Security audit patterns

### Security Non-Negotiables
- No hardcoded secrets
- Secure token storage (Keychain / EncryptedSharedPreferences / SecureStore)
- Deep link validation, HTTPS only

## Supported Agents

| Agent | How it works | Setup command |
|-------|-------------|---------------|
| **Claude Code** | Reads from `~/.claude/skills/` | `npx skill-mobile-mt --claude` |
| **Cline** | Reads `.clinerules/` from project root | `npx skill-mobile-mt --init cline` |
| **Roo Code** | Reads `.roo/rules/` from project root | `npx skill-mobile-mt --init roocode` |
| **Cursor** | Reads `.cursorrules` from project root | `npx skill-mobile-mt --init cursor` |
| **Windsurf** | Reads `.windsurfrules` from project root | `npx skill-mobile-mt --init windsurf` |
| **Copilot** | Reads `.github/copilot-instructions.md` | `npx skill-mobile-mt --init copilot` |
| **Codex** | Reads from `~/.codex/skills/` | `npx skill-mobile-mt --codex` |
| **Gemini CLI** | Reads from `~/.gemini/skills/` | `npx skill-mobile-mt --gemini` |
| **Kimi** | Reads from `~/.kimi/skills/` | `npx skill-mobile-mt --kimi` |
| **Kilo Code** | Reads `.kilocode/rules/` from project root | `npx skill-mobile-mt --init kilocode` |
| **Kiro** | Reads `.kiro/steering/` from project root | `npx skill-mobile-mt --init kiro` |
| **Antigravity** | Reads from `~/.agents/skills/` | `npx skill-mobile-mt --antigravity` |

## Companion Skill

**humanizer-mobile** is auto-installed alongside the main skill. It humanizes AI-generated mobile copy — app store descriptions, release notes, error messages, push notifications, paywall text.

```
@humanizer-mobile
> "Humanize this app store description"
```

---

## License

MIT — by [buivietphi](https://github.com/buivietphi)
