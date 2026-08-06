# Skill Mobile MT — Agent Rules

> Multi-agent compatibility layer for Claude Code, Cline, Roo Code, Cursor, Windsurf, Copilot, Codex, Gemini CLI, Kimi, Kilo Code, Kiro, Antigravity, and all Agent Skills-compatible tools.

---

## Agent Compatibility Matrix

| Agent | How it loads rules | Setup | Think Block |
|-------|-------------------|-------|-------------|
| Claude Code | `~/.claude/skills/` (auto) | `npx skill-mobile-mt --claude` | `<think>...</think>` |
| **Cline** | **`.clinerules/` in project root** | **`npx skill-mobile-mt --init cline`** | Inline reasoning |
| **Roo Code** | **`.roo/rules/` in project root** | **`npx skill-mobile-mt --init roocode`** | Inline reasoning |
| **Cursor** | **`.cursorrules` in project root** | **`npx skill-mobile-mt --init cursor`** | Inline reasoning |
| **Windsurf** | **`.windsurfrules` in project root** | **`npx skill-mobile-mt --init windsurf`** | Inline reasoning |
| **Copilot** | **`.github/copilot-instructions.md`** | **`npx skill-mobile-mt --init copilot`** | `// PLAN:` comments |
| Codex | `~/.codex/skills/` (auto) | `npx skill-mobile-mt --codex` | `<think>...</think>` |
| Gemini CLI | `~/.gemini/skills/` (auto) | `npx skill-mobile-mt --gemini` | `## Thinking:` block |
| Kimi | `~/.kimi/skills/` (manual) | `npx skill-mobile-mt --kimi` | `【思考】` or markdown |
| **Kilo Code** | **`.kilocode/rules/` in project root** | **`npx skill-mobile-mt --init kilocode`** | Inline reasoning |
| **Kiro** | **`.kiro/steering/` in project root** | **`npx skill-mobile-mt --init kiro`** | Inline reasoning |
| Antigravity | `~/.agents/skills/` (auto) | `npx skill-mobile-mt --antigravity` | Agent-native format |

---

## Full File Structure

```
skill-mobile-mt/
├── SKILL.md                        ← Entry point. Always load first. (~25,150 tokens)
├── AGENTS.md                       ← This file. Multi-agent config.
│
├── react-native/
│   └── react-native.md             ← RN + Expo patterns (~5,840 tokens)
│
├── flutter/
│   └── flutter.md                  ← Flutter + Dart 3.x patterns (~2,350 tokens)
│
├── ios/
│   └── ios-native.md               ← Swift + UIKit/SwiftUI patterns (~1,660 tokens)
│
├── android/
│   └── android-native.md           ← Kotlin + Compose + Java legacy patterns (~4,370 tokens)
│
└── shared/
    │
    ├── ── CORE (always load) ──────────────────────────────────
    ├── code-review.md               ← 12-category PR-level review + grounded review + 25 production crash patterns (all platforms) (~11,600 tokens)
    ├── bug-detection.md             ← Intelligent bug scanner + git-aware Phase 0 + error classification + stack trace parser (~7,290 tokens)
    ├── prompt-engineering.md        ← Auto-think + XML templates + advanced patterns (~7,440 tokens)
    │
    ├── ── ON-DEMAND (load by task) ────────────────────────────
    ├── error-recovery.md            ← 16 build/runtime error fixes (~2,780 tokens)
    ├── document-analysis.md         ← Parse images/PDFs/DOCX → code (~1,520 tokens)
    ├── anti-patterns.md             ← PII, cardinality, payload detection (~2,910 tokens)
    ├── performance-prediction.md    ← Frame budget, FPS prediction (~1,310 tokens)
    ├── platform-excellence.md       ← iOS 18+ vs Android 15+ UX + HIG (~1,890 tokens)
    ├── version-management.md        ← SDK compat matrix + release testing (~3,660 tokens)
    ├── observability.md             ← Sessions as 4th pillar (~5,750 tokens)
    ├── architecture-intelligence.md ← Patterns from 30+ production repos (~3,860 tokens)
    ├── common-pitfalls.md           ← Known issue patterns (~1,330 tokens)
    ├── release-checklist.md         ← App Store/Play Store checklist (~670 tokens)
    │
    ├── offline-first.md             ← Local-first + sync patterns (~2,930 tokens)
    ├── testing-strategy.md          ← Detox + Maestro + XCUITest + Espresso E2E (~2,500 tokens)
    ├── ci-cd.md                     ← GitHub Actions CI templates (~2,830 tokens)
    ├── ai-dlc-workflow.md           ← AI-DLC structured workflow for complex features (~1,950 tokens)
    ├── ui-ux-mobile.md              ← Design system, screen templates, touch, navigation, a11y (~6,910 tokens)
    ├── storage-patterns.md          ← MMKV / SecureStore / SQLite / WatermelonDB / Keychain (~2,760 tokens)
    ├── i18n-localization.md         ← i18next / slang / .xcstrings / strings.xml / RTL / date format (~3,140 tokens)
    ├── debugging-intelligence.md    ← 45+ error patterns (RN+Flutter+iOS+Android) + git-aware debugging + search strategies (~8,730 tokens)
    ├── intent-analysis.md          ← Task extraction, scope clarification, intent understanding, spec analysis (~6,250 tokens)
    ├── code-generation-templates.md ← Zustand/Redux/Riverpod, API client, forms, type generation (~5,370 tokens)
    ├── spec-to-code.md             ← Spec → dependency graph → file plan → implementation (~2,640 tokens)
    ├── navigation-patterns.md      ← Auth flow, deep links, modals, tabs, push, permissions (~2,900 tokens)
    ├── complex-ui-patterns.md      ← Carousel, gestures, keyboard, responsive, dark mode, a11y (~3,810 tokens)
    ├── data-flow-patterns.md       ← Pagination, optimistic updates, cache, WebSocket, offline queue (~3,250 tokens)
    ├── error-handling.md           ← Error hierarchy, retry, error boundary, user messages (~2,960 tokens)
    ├── testing-patterns.md         ← Component tests, hook tests, factories, snapshots (~3,410 tokens)
    │
    ├── ── TEMPLATES (copy to your project) ────────────────────
    ├── claude-md-template.md        ← CLAUDE.md for Claude Code (copy to project root)
    └── agent-rules-template.md      ← Rules for ALL agents: Cursor/.cursorrules, Windsurf/.windsurfrules, Copilot/.github/copilot-instructions.md, Codex/AGENTS.md, Gemini/GEMINI.md, Antigravity YAML
```

**Token totals:**
- Smart load (SKILL.md + 1 platform + core shared): **~53,350 – 57,350 tokens** (42% – 45% of 128K)
- Full load (all files): **~166,380 tokens** (exceeds 128K — use smart load for 128K models)
- Full load fits within **200K context** (83% of 200K)
- On-demand files (NOT loaded unless triggered): debugging-intelligence, storage-patterns, i18n-localization, observability, architecture-intelligence, etc.
- code-review.md ~11,600 tokens — 12-category PR-level review + 25 production crash patterns (all 4 platforms)
- bug-detection.md ~7,290 tokens — git-aware Phase 0, error classification, stack trace parsing (all 4 platforms)
- debugging-intelligence.md ~8,730 tokens — 45+ error patterns across RN, Flutter, iOS Swift, Android Kotlin

---

## When Smart Load vs Full Load

### Smart Load (default — always used)

**Triggered by:** `@skill-mobile-mt` or `@skill-mobile-mt project`

**Loads automatically:**
```
SKILL.md                           (~25,150 tokens)
+ 1 platform file                  (~1,660–5,840 tokens depending on platform)
+ shared/code-review.md            (~11,600 tokens)
+ shared/bug-detection.md          (~7,290 tokens)
+ shared/prompt-engineering.md     (~7,440 tokens)
─────────────────────────────────────────────────
≈ 53,350 – 57,350 tokens total (42%–45% of 128K)
```

**Use case:** Regular coding, new features, code review. Covers 90% of daily work.

---

### On-Demand Load (triggered automatically by task type)

The agent reads the task, then decides which extra file to load:

| Task the user asks for | File loaded |
|------------------------|-------------|
| "Fix this crash / build error" | `shared/error-recovery.md` |
| "Complex bug / long stack trace / investigate issue" | `shared/debugging-intelligence.md` |
| "Read this screenshot / PDF / DOCX" | `shared/document-analysis.md` |
| "Add analytics / logging / crash tracking" | `shared/anti-patterns.md` + `shared/observability.md` |
| "Build a FlatList / animation" | `shared/performance-prediction.md` |
| "Make it feel native on iOS/Android" | `shared/platform-excellence.md` |
| "Install this package / upgrade SDK" | `shared/version-management.md` |
| "Prepare for App Store / Play Store" | `shared/release-checklist.md` |
| "Weird issue, not sure why" | `shared/common-pitfalls.md` |
| "Write / run E2E tests" | `shared/testing-strategy.md` |
| "Setup CI/CD / GitHub Actions" | `shared/ci-cd.md` |
| "Big feature / multi-screen" | `shared/ai-dlc-workflow.md` |
| "Create/design screen / demo UI" | `shared/ui-ux-mobile.md` |
| "Storage / MMKV / SecureStore / save data" | `shared/storage-patterns.md` |
| "i18n / multi-language / translation / RTL" | `shared/i18n-localization.md` |
| "Review PR / review code / accessibility check" | `shared/code-review.md` (already loaded) + `shared/anti-patterns.md` |
| "Fix multiple / fix A then B / several places" | `shared/intent-analysis.md` (Task Extraction Protocol) |
| "Make it better / fix everything / vague request" | `shared/intent-analysis.md` (Scope Clarification Protocol) |
| "It's slow / doesn't work / non-technical description" | `shared/intent-analysis.md` (Intent Understanding Protocol) |
| "Build X like other apps / vague feature spec" | `shared/intent-analysis.md` (Spec Analysis Protocol) |
| "URGENT / production down / deadline / blocker" | `shared/intent-analysis.md` (Priority Detection) |
| "Build from spec / implement requirements" | `shared/spec-to-code.md` |
| "Setup state / Zustand / Redux / API client / forms" | `shared/code-generation-templates.md` |
| "Auth flow / deep links / modals / tabs / permissions" | `shared/navigation-patterns.md` |
| "Carousel / gestures / responsive / dark mode / a11y" | `shared/complex-ui-patterns.md` |
| "Pagination / optimistic / cache / WebSocket / offline" | `shared/data-flow-patterns.md` |
| "Error handling / retry / error boundary / toast" | `shared/error-handling.md` |
| "Component tests / unit tests / mock / factory" | `shared/testing-patterns.md` |
| "Compare options / best approach / upgrade vs stay" | SKILL.md Decision Matrix Protocol (already loaded) |

**Load cost:** +600 to +5,900 tokens per on-demand file.

---

### Full Load (never automatic — AI reads all files)

**No automatic trigger.** Full load happens when the AI reads every file without being selective — either because it's over-eager, or because the user explicitly asks for it.

**Total:** ~100,880 tokens (78.8% of 128K, 50.4% of 200K)

**How it actually works:**
- `@skill-mobile-mt` only injects SKILL.md into context
- From there, the AI uses the `Read` tool to open additional files
- Smart load = AI reads selectively (only what the task needs)
- Full load = AI reads every file in shared/ + all platform files

**When full load makes sense:**
- User says "load everything" or "give me a full audit"
- New project setup where all patterns are relevant simultaneously
- Cross-platform (iOS + Android + RN) with all shared patterns needed
- Antigravity agent configured to load all files upfront

**When it's wasteful:**
- Single focused task ("fix this bug", "add this screen") — loads 3x more tokens than needed
- Single-platform projects — loading all 4 platform files is waste

---

## Antigravity Configuration

```yaml
skill:
  name: skill-mobile-mt
  version: "2.2.1"
  author: buivietphi
  category: engineering
  tags:
    - mobile
    - react-native
    - flutter
    - ios
    - android
    - clean-architecture
    - code-review
    - senior

  modes:
    default:
      description: "Use pre-built production patterns from 18 real mobile apps"
      loads:
        # Core — always
        - SKILL.md
        - "{detected-platform}/{platform}.md"
        - shared/code-review.md
        - shared/bug-detection.md
        - shared/prompt-engineering.md
        # On-demand — add based on task
        # - shared/error-recovery.md
        # - shared/anti-patterns.md
        # - shared/performance-prediction.md
        # - shared/platform-excellence.md
        # - shared/version-management.md
        # - shared/observability.md
        # - shared/document-analysis.md
        # - shared/release-checklist.md
        # - shared/common-pitfalls.md

    project:
      description: "Read current project, adapt to its framework and conventions"
      argument: "project"
      loads:
        - SKILL.md (Section: Project Adaptation)
        - "{detected-platform}/{platform}.md"
        - shared/code-review.md
        - shared/bug-detection.md
        - shared/prompt-engineering.md

  platform_detection:
    react-native:
      detect: "package.json contains 'react-native' or 'expo'"
      load: "react-native/react-native.md"
    flutter:
      detect: "pubspec.yaml exists"
      load: "flutter/flutter.md"
    ios:
      detect: "*.xcodeproj or *.xcworkspace exists (without pubspec.yaml)"
      load: "ios/ios-native.md"
    android:
      detect: "build.gradle exists (without package.json or pubspec.yaml)"
      load: "android/android-native.md"

  language_detection:
    typescript: ".tsx/.ts files in src/"
    javascript: ".jsx/.js files in src/"
    dart: ".dart files in lib/"
    swift: ".swift files"
    kotlin: ".kt files"
    java: ".java files in app/src/"

  context_budget:
    max_tokens: 166380
    smart_load_tokens: 57350
    fits_128k: "smart load only"
    fits_200k: "full load (83%)"
```

---

## File Loading Rules for All Agents

### Smart Loading Protocol

Every agent MUST follow this loading sequence:

```
1. ALWAYS load: SKILL.md (entry point, auto-detect, universal principles)

2. AUTO-DETECT project:
   - Framework (React Native / Flutter / iOS / Android)
   - Language (TypeScript / JavaScript / Dart / Swift / Kotlin / Java)
   - Package manager (yarn / npm / pnpm / bun / flutter pub / pod)
   - State management
   - Navigation

3. LOAD the matching platform subfolder:
   - react-native/react-native.md  (only if RN/Expo)
   - flutter/flutter.md            (only if Flutter)
   - ios/ios-native.md             (only if iOS native)
   - android/android-native.md     (only if Android native)

4. Cross-platform? Load multiple:
   - Flutter → also load ios/ + android/ (native modules)
   - React Native → also load ios/ + android/ (native modules)

5. ALWAYS load shared/ (core):
   - shared/code-review.md
   - shared/bug-detection.md
   - shared/prompt-engineering.md

6. LOAD shared/ (on-demand, based on task):
   - shared/error-recovery.md         (when debugging build/runtime errors)
   - shared/document-analysis.md      (when reading images, PDFs, DOCX)
   - shared/anti-patterns.md          (when reviewing or writing observability code)
   - shared/performance-prediction.md (when building lists, animations, heavy screens)
   - shared/platform-excellence.md    (when implementing platform-specific UX)
   - shared/version-management.md     (when installing packages or upgrading SDK)
   - shared/observability.md          (when adding logging, analytics, crash tracking)
   - shared/common-pitfalls.md        (when encountering unfamiliar errors)
   - shared/release-checklist.md      (when preparing for App Store/Play Store submission)
   - shared/storage-patterns.md       (when choosing or implementing local storage)
   - shared/i18n-localization.md      (when implementing multi-language or RTL)
   - shared/debugging-intelligence.md (when investigating complex bugs or long stack traces)
   - shared/intent-analysis.md      (when input is multi-part, vague, non-technical, or ambiguous)
   - shared/code-generation-templates.md (when setting up state management, API client, or forms)
   - shared/spec-to-code.md         (when building new feature from spec or requirements)
   - shared/navigation-patterns.md  (when implementing auth flow, deep links, modals, tabs, permissions)
   - shared/complex-ui-patterns.md  (when building carousel, gestures, responsive layout, dark mode, a11y)
   - shared/data-flow-patterns.md   (when implementing pagination, optimistic updates, cache, WebSocket)
   - shared/error-handling.md       (when implementing error handling, retry, error boundary)
   - shared/testing-patterns.md     (when writing component tests, hook tests, or setting up test factories)

7. SKIP non-matching platform subfolders (saves ~66% context)
```

### Loading Priority

```
Priority 1 (CRITICAL):  SKILL.md — Auto-detect, mode selection, principles
Priority 2 (HIGH):      {platform}/{platform}.md — Framework-specific patterns
Priority 3 (MEDIUM):    shared/code-review.md — Review checklist
Priority 4 (MEDIUM):    shared/bug-detection.md — Auto-scanner
Priority 5 (MEDIUM):    shared/prompt-engineering.md — Auto-think templates
Priority 6 (ON-DEMAND): shared/error-recovery.md — Build/runtime error fixes
Priority 6 (ON-DEMAND): shared/anti-patterns.md — PII, cardinality, payload detection
Priority 6 (ON-DEMAND): shared/performance-prediction.md — Frame budget calculations
Priority 6 (ON-DEMAND): shared/platform-excellence.md — iOS 18+ vs Android 15+ UX
Priority 6 (ON-DEMAND): shared/version-management.md — SDK compatibility matrix
Priority 6 (ON-DEMAND): shared/observability.md — Sessions as 4th pillar
Priority 6 (ON-DEMAND): shared/document-analysis.md — Parse images/PDFs → code
Priority 6 (ON-DEMAND): shared/release-checklist.md — Pre-release verification
Priority 6 (ON-DEMAND): shared/common-pitfalls.md — Known issue patterns
Priority 6 (ON-DEMAND): shared/testing-strategy.md — Detox + Maestro + XCUITest + Espresso E2E
Priority 6 (ON-DEMAND): shared/ci-cd.md — GitHub Actions CI/CD templates
Priority 6 (ON-DEMAND): shared/ai-dlc-workflow.md — AI-DLC structured workflow for complex features
Priority 6 (ON-DEMAND): shared/ui-ux-mobile.md — Screen templates, design tokens, components, dark mode
Priority 6 (ON-DEMAND): shared/storage-patterns.md — MMKV, SecureStore, SQLite, WatermelonDB, Keychain
Priority 6 (ON-DEMAND): shared/i18n-localization.md — i18next, slang, .xcstrings, strings.xml, RTL
Priority 6 (ON-DEMAND): shared/intent-analysis.md — Task extraction, scope clarification, intent understanding, spec analysis
Priority 6 (ON-DEMAND): shared/code-generation-templates.md — Zustand/Redux/Riverpod, API client, forms, types
Priority 6 (ON-DEMAND): shared/spec-to-code.md — Spec → dependency graph → file plan → implementation
Priority 6 (ON-DEMAND): shared/navigation-patterns.md — Auth flow, deep links, modals, tabs, push, permissions
Priority 6 (ON-DEMAND): shared/complex-ui-patterns.md — Carousel, gestures, keyboard, responsive, dark mode, a11y
Priority 6 (ON-DEMAND): shared/data-flow-patterns.md — Pagination, optimistic updates, cache, WebSocket, offline queue
Priority 6 (ON-DEMAND): shared/error-handling.md — Error hierarchy, retry, error boundary, user messages
Priority 6 (ON-DEMAND): shared/testing-patterns.md — Component tests, hook tests, factories, snapshots
Priority 6 (ON-DEMAND): shared/debugging-intelligence.md — 30+ error patterns, git-aware debugging
```

---

## Agent-Specific Behavior

### Claude Code
- Supports `$ARGUMENTS` — use `project` to trigger project mode
- Can invoke sub-files via Read tool from subfolders
- Full tool access for project scanning and auto-detect

### Codex
- Load SKILL.md as system context or prepend to conversation
- Reference subfolder files with Read tool when needed
- Use `project` keyword to trigger project adaptation mode

### Gemini CLI
- Load SKILL.md as system context
- Parse mode from user prompt ("use project mode" or default)
- Reference subfolder files as needed

### Kimi
- Load SKILL.md as knowledge base
- Supports both Chinese and English prompts
- Think blocks use `【思考】` format

### Cline
- Reads `.clinerules/` directory from project root (also supports `.clinerules` single file)
- Also reads from `~/.cline/skills/` for global skills
- Run `npx @buivietphi/skill-mobile-mt --init cline` to generate `.clinerules/mobile-rules.md`
- Supports conditional rules with YAML frontmatter `paths:` field

### Roo Code
- Reads `.roo/rules/` directory from project root (recursive, multi-file)
- Also reads from `~/.roo/skills/` for global skills
- Supports mode-specific rules: `.roo/rules-code/`, `.roo/rules-architect/`
- Run `npx @buivietphi/skill-mobile-mt --init roocode` to generate `.roo/rules/mobile-rules.md`
- Auto-loads `AGENTS.md` from workspace root

### Cursor
- Reads `.cursorrules` from project root
- Run `npx @buivietphi/skill-mobile-mt --init cursor` to generate `.cursorrules`
- The generated file includes auto-detected framework, rules, and security patterns
- Think blocks embedded as inline reasoning in Composer

### GitHub Copilot
- Reads `.github/copilot-instructions.md` from project
- Run `npx @buivietphi/skill-mobile-mt --init copilot` to generate the file
- The generated file includes code patterns, required templates, and rules
- Think blocks as `// PLAN:` comments before code

### Windsurf
- Reads `.windsurfrules` from project root
- Run `npx @buivietphi/skill-mobile-mt --init windsurf` to generate `.windsurfrules`
- The generated file includes coding rules, security rules, and architecture patterns
- Think blocks as inline reasoning

### Kilo Code
- Reads `.kilocode/rules/` directory from project root
- Also reads from `~/.kilocode/rules/` for global rules
- Supports mode-specific rules: `.kilocode/rules-code/`, `.kilocode/rules-architect/`
- Run `npx @buivietphi/skill-mobile-mt --init kilocode` to generate `.kilocode/rules/mobile-rules.md`
- Auto-loads `AGENTS.md` from workspace root

### Kiro (AWS)
- Reads `.kiro/steering/` directory from project root
- Also reads from `~/.kiro/steering/` for global steering
- Uses YAML frontmatter with `inclusion: always|fileMatch|manual|auto`
- Run `npx @buivietphi/skill-mobile-mt --init kiro` to generate `.kiro/steering/mobile-rules.md`
- Separate specs system in `.kiro/specs/` for feature development

### Antigravity
- Orchestrator loads based on detected project type
- Follows `platform_detection` rules above
- Respects `context_budget` limits

---

## Project-Level Rules (Auto-Loaded Per Agent)

Each agent reads a specific file from the **user's project root** every session.
These are separate from the skill files — they go in the user's project, not in skill-mobile-mt/.

| Agent | File | Location |
|-------|------|----------|
| Claude Code | `CLAUDE.md` | Project root |
| Cline | `.clinerules/` directory | Project root |
| Roo Code | `.roo/rules/` directory | Project root |
| Cursor | `.cursorrules` | Project root |
| Windsurf | `.windsurfrules` | Project root |
| GitHub Copilot | `.github/copilot-instructions.md` | `.github/` folder |
| Codex | `AGENTS.md` | Project root |
| Gemini CLI | `GEMINI.md` | Project root |
| Kimi | No auto-load — paste as context | — |
| Kilo Code | `.kilocode/rules/` directory | Project root |
| Kiro | `.kiro/steering/` directory | Project root |
| Antigravity | YAML `context.rules` field | Antigravity config |

**Templates for all agents:** `shared/agent-rules-template.md`
Copy the relevant section to your project to enable auto-check rules in every session.

```bash
# After installing skill-mobile-mt, find the templates at:
~/.claude/skills/skill-mobile-mt/shared/agent-rules-template.md
~/.claude/skills/skill-mobile-mt/shared/claude-md-template.md
```

---

## Installation Paths

### Skill directory install (agents that read from skills/)

```bash
# Claude Code
~/.claude/skills/skill-mobile-mt/

# Cline
~/.cline/skills/skill-mobile-mt/

# Roo Code
~/.roo/skills/skill-mobile-mt/

# Codex
~/.codex/skills/skill-mobile-mt/

# Gemini CLI
~/.gemini/skills/skill-mobile-mt/

# Kimi
~/.kimi/skills/skill-mobile-mt/

# Kilo Code
~/.kilocode/skills/skill-mobile-mt/

# Kiro
~/.kiro/skills/skill-mobile-mt/

# Antigravity (shared agent directory)
~/.agents/skills/skill-mobile-mt/

# Custom path
npx @buivietphi/skill-mobile-mt --path /your/custom/path
```

### Project-level files (agents that read from project root)

These agents read rules from project-level files. Use `--init` to generate them:

```bash
# Generate all project-level files (interactive selector)
npx @buivietphi/skill-mobile-mt --init

# Generate specific agent file
npx @buivietphi/skill-mobile-mt --init cursor     # → .cursorrules
npx @buivietphi/skill-mobile-mt --init cline      # → .clinerules/mobile-rules.md
npx @buivietphi/skill-mobile-mt --init roocode    # → .roo/rules/mobile-rules.md
npx @buivietphi/skill-mobile-mt --init copilot    # → .github/copilot-instructions.md
npx @buivietphi/skill-mobile-mt --init windsurf   # → .windsurfrules
npx @buivietphi/skill-mobile-mt --init kilocode   # → .kilocode/rules/mobile-rules.md
npx @buivietphi/skill-mobile-mt --init kiro       # → .kiro/steering/mobile-rules.md
npx @buivietphi/skill-mobile-mt --init all        # → all files
```

**What `--init` does:**
1. Auto-detects your project (framework, language, state management, etc.)
2. Generates rules files pre-filled with your detected stack
3. Includes all mobile best practices, security rules, and quality gates
4. Won't overwrite existing files (safe to run multiple times)

---

## Metadata

```json
{
  "id": "skill-mobile-mt",
  "name": "skill-mobile-mt",
  "version": "2.2.1",
  "author": "buivietphi",
  "category": "engineering",
  "description": "Master Senior Mobile Engineer. Patterns from 30+ production repos (200k+ GitHub stars) + research from top 53k+ star skill repos. Cardinal rules, self-critique loops, leverage pyramid, verification-first, decision matrix, codebase scan strategy, grounded code review (anti-false-positive), git-aware debugging, task extraction protocol, multi-fix execution, UI fix protocol, completion re-check. React Native, Flutter, iOS, Android.",
  "risk": "low",
  "source": "buivietphi (MIT)",
  "platforms": ["react-native", "flutter", "ios", "android"],
  "languages": ["typescript", "javascript", "dart", "swift", "kotlin", "java"],
  "agents": ["claude-code", "cline", "roo-code", "cursor", "windsurf", "copilot", "codex", "gemini", "kimi", "kilo-code", "kiro", "antigravity"]
}
```
