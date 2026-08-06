#!/usr/bin/env node

/**
 * @buivietphi/skill-mobile installer
 *
 * Installs skill-mobile-mt/ folder with subfolders for each platform.
 *
 * Usage:
 *   npx @buivietphi/skill-mobile              # Interactive checkbox UI
 *   npx @buivietphi/skill-mobile --all        # All detected agents
 *   npx @buivietphi/skill-mobile --claude     # Claude Code only
 *   npx @buivietphi/skill-mobile --gemini     # Gemini CLI
 *   npx @buivietphi/skill-mobile --kimi       # Kimi
 *   npx @buivietphi/skill-mobile --antigravity # Antigravity
 *   npx @buivietphi/skill-mobile --auto       # Auto-detect (postinstall)
 *   npx @buivietphi/skill-mobile --path DIR   # Custom path
 *   npx @buivietphi/skill-mobile --init       # Generate project-level rules (interactive)
 *   npx @buivietphi/skill-mobile --init cursor    # Generate .cursorrules
 *   npx @buivietphi/skill-mobile --init copilot   # Generate .github/copilot-instructions.md
 *   npx @buivietphi/skill-mobile --init windsurf  # Generate .windsurfrules
 *   npx @buivietphi/skill-mobile --init cline      # Generate .clinerules/mobile-rules.md
 *   npx @buivietphi/skill-mobile --init roocode    # Generate .roo/rules/mobile-rules.md
 *   npx @buivietphi/skill-mobile --init kilocode   # Generate .kilocode/rules/mobile-rules.md
 *   npx @buivietphi/skill-mobile --init kiro       # Generate .kiro/steering/mobile-rules.md
 *   npx @buivietphi/skill-mobile --init all        # Generate all project-level files
 */

import { existsSync, mkdirSync, cpSync, readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { join, resolve, dirname } from 'node:path';
import { homedir } from 'node:os';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const PKG_ROOT = resolve(__dirname, '..');
const SKILL_NAME = 'skill-mobile-mt';
const HOME = homedir();

// Structure: root files + subfolders
const ROOT_FILES = ['SKILL.md', 'AGENTS.md'];

const SUBFOLDERS = ['react-native', 'flutter', 'ios', 'android', 'shared'];

// Read all .md files from a folder dynamically
function getMdFiles(folder) {
  const dir = join(PKG_ROOT, folder);
  if (!existsSync(dir)) return [];
  return readdirSync(dir).filter(f => f.endsWith('.md'));
}

const AGENTS = {
  claude:       { name: 'Claude Code',  dir: join(HOME, '.claude', 'skills'),   detect: () => existsSync(join(HOME, '.claude')) },
  cline:        { name: 'Cline',        dir: join(HOME, '.cline', 'skills'),    detect: () => existsSync(join(HOME, '.cline')) },
  roocode:      { name: 'Roo Code',     dir: join(HOME, '.roo', 'skills'),      detect: () => existsSync(join(HOME, '.roo')) },
  cursor:       { name: 'Cursor',       dir: join(HOME, '.cursor', 'skills'),   detect: () => existsSync(join(HOME, '.cursor')) },
  windsurf:     { name: 'Windsurf',     dir: join(HOME, '.windsurf', 'skills'), detect: () => existsSync(join(HOME, '.windsurf')) },
  copilot:      { name: 'Copilot',      dir: join(HOME, '.copilot', 'skills'),  detect: () => existsSync(join(HOME, '.copilot')) },
  codex:        { name: 'Codex',        dir: join(HOME, '.codex', 'skills'),    detect: () => existsSync(join(HOME, '.codex')) },
  gemini:       { name: 'Gemini CLI',   dir: join(HOME, '.gemini', 'skills'),   detect: () => existsSync(join(HOME, '.gemini')) },
  kimi:         { name: 'Kimi',         dir: join(HOME, '.kimi', 'skills'),     detect: () => existsSync(join(HOME, '.kimi')) },
  kilocode:     { name: 'Kilo Code',    dir: join(HOME, '.kilocode', 'skills'), detect: () => existsSync(join(HOME, '.kilocode')) },
  kiro:         { name: 'Kiro',         dir: join(HOME, '.kiro', 'skills'),     detect: () => existsSync(join(HOME, '.kiro')) },
  antigravity:  { name: 'Antigravity',  dir: join(HOME, '.agents', 'skills'),   detect: () => existsSync(join(HOME, '.agents')) },
};

const c = { reset: '\x1b[0m', bold: '\x1b[1m', dim: '\x1b[2m', green: '\x1b[32m', yellow: '\x1b[33m', blue: '\x1b[34m', cyan: '\x1b[36m', red: '\x1b[31m' };
const log = m => process.stdout.write(m + '\n');
const ok  = m => log(`  ${c.green}✓${c.reset} ${m}`);
const info = m => log(`  ${c.blue}ℹ${c.reset} ${m}`);
const fail = m => log(`  ${c.red}✗${c.reset} ${m}`);

function banner() {
  log(`\n${c.bold}${c.cyan}  ┌──────────────────────────────────────────────────┐`);
  log(`  │  📱 @buivietphi/skill-mobile-mt v2.0.0           │`);
  log(`  │  Master Senior Mobile Engineer                    │`);
  log(`  │                                                  │`);
  log(`  │  Claude · Cline · Roo Code · Cursor · Windsurf  │`);
  log(`  │  Copilot · Codex · Gemini · Kimi · Kilo · Kiro  │`);
  log(`  │  Antigravity                                     │`);
  log(`  │  React Native · Flutter · iOS · Android          │`);
  log(`  └──────────────────────────────────────────────────┘${c.reset}\n`);
}

function tokenCount(filePath) {
  if (!existsSync(filePath)) return 0;
  return Math.ceil(readFileSync(filePath, 'utf-8').length / 3.5);
}

function showContext() {
  log(`${c.bold}  📊 Context budget:${c.reset}`);
  let total = 0;
  for (const f of ROOT_FILES) {
    const t = tokenCount(join(PKG_ROOT, f));
    total += t;
    log(`  ${c.dim}  ${f.padEnd(30)} ~${t.toLocaleString()} tokens${c.reset}`);
  }
  for (const folder of SUBFOLDERS) {
    let ft = 0;
    for (const f of getMdFiles(folder)) ft += tokenCount(join(PKG_ROOT, folder, f));
    total += ft;
    log(`  ${c.dim}  ${(folder + '/').padEnd(30)} ~${ft.toLocaleString()} tokens${c.reset}`);
  }
  log(`${c.dim}  ─────────────────────────────────────────${c.reset}`);
  log(`  ${c.bold}  All loaded:${c.reset}                    ~${total.toLocaleString()} tokens`);
  log(`  ${c.green}  Smart load (1 platform):${c.reset}       ~${Math.ceil(total * 0.55).toLocaleString()} tokens\n`);
}

function install(baseDir, agentName) {
  // Install main skill
  const dst = join(baseDir, SKILL_NAME);
  mkdirSync(dst, { recursive: true });
  let n = 0;
  for (const f of ROOT_FILES) {
    const src = join(PKG_ROOT, f);
    if (!existsSync(src)) continue;
    cpSync(src, join(dst, f), { force: true });
    n++;
  }
  for (const folder of SUBFOLDERS) {
    const dstFolder = join(dst, folder);
    mkdirSync(dstFolder, { recursive: true });
    for (const f of getMdFiles(folder)) {
      const src = join(PKG_ROOT, folder, f);
      cpSync(src, join(dstFolder, f), { force: true });
      n++;
    }
  }
  ok(`${c.bold}${SKILL_NAME}/${c.reset} → ${agentName} ${c.dim}(${dst})${c.reset}`);

  // Auto-install humanizer-mobile as separate skill
  const humanizerSrc = join(PKG_ROOT, 'humanizer', 'humanizer-mobile.md');
  if (existsSync(humanizerSrc)) {
    const humDst = join(baseDir, 'humanizer-mobile');
    mkdirSync(humDst, { recursive: true });
    cpSync(humanizerSrc, join(humDst, 'humanizer-mobile.md'), { force: true });
    ok(`${c.bold}humanizer-mobile/${c.reset} → ${agentName} ${c.dim}(${humDst})${c.reset}`);
  }

  return n;
}

// ─── Project Auto-Detect ─────────────────────────────────────────────────────

function detectProject(dir) {
  const has = f => existsSync(join(dir, f));
  const readJson = f => { try { return JSON.parse(readFileSync(join(dir, f), 'utf-8')); } catch { return null; } };

  let framework = '[React Native CLI / Expo / Flutter / iOS / Android]';
  let language  = '[TypeScript / Dart / Swift / Kotlin]';
  let state     = '[Redux Toolkit / Zustand / Riverpod / BLoC / StateFlow]';
  let nav       = '[React Navigation / Expo Router / GoRouter / UIKit / Jetpack]';
  let api       = '[axios / fetch / Dio / Firebase / Retrofit]';
  let pkgMgr    = '[yarn / npm / bun / flutter pub]';

  // Detect framework + language
  if (has('pubspec.yaml')) {
    framework = 'Flutter'; language = 'Dart'; pkgMgr = 'flutter pub';
  } else if (has('package.json')) {
    const pkg = readJson('package.json');
    const deps = { ...(pkg?.dependencies || {}), ...(pkg?.devDependencies || {}) };
    if (deps['expo'])                  { framework = 'Expo (React Native)'; }
    else if (deps['react-native'])     { framework = 'React Native CLI'; }
    language = deps['typescript'] || has('tsconfig.json') ? 'TypeScript' : 'JavaScript';
    // State
    if (deps['@reduxjs/toolkit'] || deps['redux'])  state = 'Redux Toolkit';
    else if (deps['zustand'])                        state = 'Zustand';
    else if (deps['mobx-react-lite'] || deps['mobx'])state = 'MobX';
    // Nav
    if (deps['expo-router'])                         nav = 'Expo Router';
    else if (deps['@react-navigation/native'])       nav = 'React Navigation';
    // API
    if (deps['axios'])                               api = 'axios';
    else if (deps['@apollo/client'])                 api = 'GraphQL (Apollo)';
    // Pkg manager
    if (has('yarn.lock'))       pkgMgr = 'yarn';
    else if (has('pnpm-lock.yaml')) pkgMgr = 'pnpm';
    else if (has('bun.lockb'))  pkgMgr = 'bun';
    else                        pkgMgr = 'npm';
  } else if (has('build.gradle') || has('build.gradle.kts')) {
    framework = 'Android Native'; language = 'Kotlin'; pkgMgr = 'Gradle';
  }
  // iOS detection (*.xcodeproj) is harder — leave as placeholder

  return { framework, language, state, nav, api, pkgMgr };
}

// ─── Project-Level File Templates ────────────────────────────────────────────

const PROJECT_AGENTS = {
  cursor: {
    name: 'Cursor',
    file: '.cursorrules',
    dir:  '.',
    generate: (p) => `# ${p.framework} Project — Cursor Rules
# Generated by @buivietphi/skill-mobile-mt

## Project
- Framework: ${p.framework}
- Language: ${p.language}
- State: ${p.state}
- Navigation: ${p.nav}
- API: ${p.api}
- Package Manager: ${p.pkgMgr}

## Code Style
- PascalCase for screens and components
- camelCase for hooks, services, utils
- Absolute imports with @/ alias (if configured)

## Auto-Check (before every completion)
- No console.log / print in production code
- No hardcoded secrets or API keys
- All async wrapped in try/catch
- All 4 states: loading / error / empty / success
- useEffect has cleanup (return () => ...)
- FlatList (not ScrollView) for dynamic lists > 20 items
- No implicit 'any' in TypeScript
- No force unwrap (! / !!) without null check
- New screens registered in navigator

## Performance
- React.memo / const widget for expensive components
- useMemo/useCallback for stable references
- Images cached and resized
- No main thread blocking

## Security (non-negotiable)
- Tokens → SecureStore / Keychain / EncryptedSharedPreferences
- API calls → HTTPS only
- Sensitive data → never in logs
- User input → sanitize before display
- Deep links → validate before navigation

## Never
- Change framework or architecture
- Change state management library
- Add packages without checking SDK compatibility
- Mix package managers
- Use ScrollView for long lists
- Leave empty catch blocks
- Store tokens in AsyncStorage / SharedPreferences / UserDefaults

## Architecture
- Dependencies flow inward: UI → Domain → Data
- Single responsibility per file (max 300 lines)
- Feature-based organization preferred

## Reference
- Full skill: ~/.cursor/skills/skill-mobile-mt/
- Patterns from 30+ production repos (200k+ GitHub stars)
`,
  },

  copilot: {
    name: 'GitHub Copilot',
    file: 'copilot-instructions.md',
    dir:  '.github',
    generate: (p) => `# Copilot Instructions — ${p.framework} Project

> Generated by @buivietphi/skill-mobile-mt

## Project Context
- **Framework:** ${p.framework}
- **Language:** ${p.language}
- **State Management:** ${p.state}
- **Navigation:** ${p.nav}
- **API:** ${p.api}
- **Package Manager:** ${p.pkgMgr}

## Conventions
- PascalCase: components, screens, classes
- camelCase: hooks, services, utilities, variables
- Files named same as their default export

## Required Patterns

### Every async function
\`\`\`typescript
try {
  setLoading(true);
  const result = await apiCall();
  setData(result);
} catch (error) {
  setError(error.message);
} finally {
  setLoading(false);
}
\`\`\`

### Every screen must handle 4 states
\`\`\`typescript
if (loading) return <LoadingScreen />;
if (error) return <ErrorScreen error={error} />;
if (!data?.length) return <EmptyScreen />;
return <DataScreen data={data} />;
\`\`\`

### Every useEffect with subscriptions
\`\`\`typescript
useEffect(() => {
  const sub = subscribe();
  return () => sub.unsubscribe(); // REQUIRED
}, []);
\`\`\`

## Rules
- No console.log / print in production
- No hardcoded secrets or API keys
- FlatList (not ScrollView) for dynamic lists
- Tokens in SecureStore / Keychain only
- No force unwrap (! / !!) without null check
- No implicit 'any' in TypeScript
- No empty catch blocks
- No inline functions in render/build
- Images cached and resized
- New screens registered in navigator

## Security
- Tokens → SecureStore / Keychain / EncryptedSharedPreferences
- API calls → HTTPS only
- Sensitive data → never in logs
- User input → sanitize before rendering
- Deep links → validate before navigation

## Never
- Suggest migrating to a different framework
- Change state management library
- Add packages without checking SDK compatibility
- Mix package managers (yarn + npm)
- Use ScrollView for lists > 20 items
- Store tokens in AsyncStorage / SharedPreferences / UserDefaults

## Architecture
- Clean Architecture: UI → Domain → Data
- Single responsibility per file (max 300 lines)
- Feature-based organization preferred

## Reference
Full skill with patterns from 30+ production repos: ~/.copilot/skills/skill-mobile-mt/
`,
  },

  cline: {
    name: 'Cline',
    file: 'mobile-rules.md',
    dir:  '.clinerules',
    generate: (p) => `# ${p.framework} Project — Mobile Rules
# Generated by @buivietphi/skill-mobile-mt

## Project
- Framework: ${p.framework}
- Language: ${p.language}
- State: ${p.state}
- Navigation: ${p.nav}
- API: ${p.api}
- Package Manager: ${p.pkgMgr}

## Code Style
- PascalCase for screens and components
- camelCase for hooks, services, utils
- Absolute imports with @/ alias (if configured)

## Auto-Check (before every completion)
- No console.log / print in production code
- No hardcoded secrets or API keys
- All async wrapped in try/catch
- All 4 states: loading / error / empty / success
- useEffect has cleanup (return () => ...)
- FlatList (not ScrollView) for dynamic lists > 20 items
- No implicit 'any' in TypeScript
- No force unwrap (! / !!) without null check
- New screens registered in navigator

## Performance
- React.memo / const widget for expensive components
- useMemo/useCallback for stable references
- Images cached and resized
- No main thread blocking

## Security (non-negotiable)
- Tokens → SecureStore / Keychain / EncryptedSharedPreferences
- API calls → HTTPS only
- Sensitive data → never in logs
- User input → sanitize before display
- Deep links → validate before navigation

## Never
- Change framework or architecture
- Change state management library
- Add packages without checking SDK compatibility
- Mix package managers
- Use ScrollView for long lists
- Leave empty catch blocks
- Store tokens in AsyncStorage / SharedPreferences / UserDefaults

## Architecture
- Dependencies flow inward: UI → Domain → Data
- Single responsibility per file (max 300 lines)
- Feature-based organization preferred

## Reference
- Full skill: ~/.cline/skills/skill-mobile-mt/
- Patterns from 30+ production repos (200k+ GitHub stars)
`,
  },

  roocode: {
    name: 'Roo Code',
    file: 'mobile-rules.md',
    dir:  '.roo/rules',
    generate: (p) => `# ${p.framework} Project — Mobile Rules
# Generated by @buivietphi/skill-mobile-mt

## Project
- Framework: ${p.framework}
- Language: ${p.language}
- State: ${p.state}
- Navigation: ${p.nav}
- API: ${p.api}
- Package Manager: ${p.pkgMgr}

## Code Style
- PascalCase for screens and components
- camelCase for hooks, services, utils
- Absolute imports with @/ alias (if configured)

## Auto-Check (before every completion)
- No console.log / print in production code
- No hardcoded secrets or API keys
- All async wrapped in try/catch
- All 4 states: loading / error / empty / success
- useEffect has cleanup (return () => ...)
- FlatList (not ScrollView) for dynamic lists > 20 items
- No implicit 'any' in TypeScript
- No force unwrap (! / !!) without null check
- New screens registered in navigator

## Performance
- React.memo / const widget for expensive components
- useMemo/useCallback for stable references
- Images cached and resized
- No main thread blocking

## Security (non-negotiable)
- Tokens → SecureStore / Keychain / EncryptedSharedPreferences
- API calls → HTTPS only
- Sensitive data → never in logs
- User input → sanitize before display
- Deep links → validate before navigation

## Never
- Change framework or architecture
- Change state management library
- Add packages without checking SDK compatibility
- Mix package managers
- Use ScrollView for long lists
- Leave empty catch blocks
- Store tokens in AsyncStorage / SharedPreferences / UserDefaults

## Architecture
- Dependencies flow inward: UI → Domain → Data
- Single responsibility per file (max 300 lines)
- Feature-based organization preferred

## Reference
- Full skill: ~/.roo/skills/skill-mobile-mt/
- Patterns from 30+ production repos (200k+ GitHub stars)
`,
  },

  kilocode: {
    name: 'Kilo Code',
    file: 'mobile-rules.md',
    dir:  '.kilocode/rules',
    generate: (p) => `# ${p.framework} Project — Mobile Rules
# Generated by @buivietphi/skill-mobile-mt

## Project
- Framework: ${p.framework}
- Language: ${p.language}
- State: ${p.state}
- Navigation: ${p.nav}
- API: ${p.api}
- Package Manager: ${p.pkgMgr}

## Code Style
- PascalCase for screens and components
- camelCase for hooks, services, utils
- Absolute imports with @/ alias (if configured)

## Auto-Check (before every completion)
- No console.log / print in production code
- No hardcoded secrets or API keys
- All async wrapped in try/catch
- All 4 states: loading / error / empty / success
- useEffect has cleanup (return () => ...)
- FlatList (not ScrollView) for dynamic lists > 20 items
- No implicit 'any' in TypeScript
- No force unwrap (! / !!) without null check
- New screens registered in navigator

## Performance
- React.memo / const widget for expensive components
- useMemo/useCallback for stable references
- Images cached and resized
- No main thread blocking

## Security (non-negotiable)
- Tokens → SecureStore / Keychain / EncryptedSharedPreferences
- API calls → HTTPS only
- Sensitive data → never in logs
- User input → sanitize before display
- Deep links → validate before navigation

## Never
- Change framework or architecture
- Change state management library
- Add packages without checking SDK compatibility
- Mix package managers
- Use ScrollView for long lists
- Leave empty catch blocks
- Store tokens in AsyncStorage / SharedPreferences / UserDefaults

## Architecture
- Dependencies flow inward: UI → Domain → Data
- Single responsibility per file (max 300 lines)
- Feature-based organization preferred

## Reference
- Full skill: ~/.kilocode/skills/skill-mobile-mt/
- Patterns from 30+ production repos (200k+ GitHub stars)
`,
  },

  kiro: {
    name: 'Kiro',
    file: 'mobile-rules.md',
    dir:  '.kiro/steering',
    generate: (p) => `---
inclusion: always
---

# ${p.framework} Project — Mobile Rules
# Generated by @buivietphi/skill-mobile-mt

## Project
- Framework: ${p.framework}
- Language: ${p.language}
- State: ${p.state}
- Navigation: ${p.nav}
- API: ${p.api}
- Package Manager: ${p.pkgMgr}

## Code Style
- PascalCase for screens and components
- camelCase for hooks, services, utils
- Absolute imports with @/ alias (if configured)

## Auto-Check (before every completion)
- No console.log / print in production code
- No hardcoded secrets or API keys
- All async wrapped in try/catch
- All 4 states: loading / error / empty / success
- useEffect has cleanup (return () => ...)
- FlatList (not ScrollView) for dynamic lists > 20 items
- No implicit 'any' in TypeScript
- No force unwrap (! / !!) without null check
- New screens registered in navigator

## Performance
- React.memo / const widget for expensive components
- useMemo/useCallback for stable references
- Images cached and resized
- No main thread blocking

## Security (non-negotiable)
- Tokens → SecureStore / Keychain / EncryptedSharedPreferences
- API calls → HTTPS only
- Sensitive data → never in logs
- User input → sanitize before display
- Deep links → validate before navigation

## Never
- Change framework or architecture
- Change state management library
- Add packages without checking SDK compatibility
- Mix package managers
- Use ScrollView for long lists
- Leave empty catch blocks
- Store tokens in AsyncStorage / SharedPreferences / UserDefaults

## Architecture
- Dependencies flow inward: UI → Domain → Data
- Single responsibility per file (max 300 lines)
- Feature-based organization preferred

## Reference
- Patterns from 30+ production repos (200k+ GitHub stars)
`,
  },

  windsurf: {
    name: 'Windsurf',
    file: '.windsurfrules',
    dir:  '.',
    generate: (p) => `# ${p.framework} Project — Windsurf Rules
# Generated by @buivietphi/skill-mobile-mt

Project: ${p.framework}
Language: ${p.language}
State management: ${p.state}
Navigation: ${p.nav}
API: ${p.api}
Package manager: ${p.pkgMgr}

## Coding Rules

Always:
- Wrap all async operations in try/catch
- Handle all 4 states: loading, error, empty, success
- Add cleanup to useEffect (return () => ...)
- Use FlatList for dynamic lists (not ScrollView)
- Use PascalCase for components and screens
- Use camelCase for hooks, services, and utilities
- No implicit 'any' in TypeScript
- No force unwrap (! / !!) without null check
- New screens registered in navigator
- React.memo / const widget for expensive components
- Images cached and resized

Never:
- Leave console.log / print in production code
- Hardcode secrets, tokens, or API keys
- Store tokens in AsyncStorage / SharedPreferences / UserDefaults
- Change the framework or architecture
- Change state management library
- Add packages without verifying SDK compatibility
- Mix yarn and npm
- Use ScrollView for lists > 20 items
- Leave empty catch blocks
- Use index as list key

## Security (non-negotiable)
- Tokens → SecureStore / Keychain / EncryptedSharedPreferences
- API calls → HTTPS only
- Sensitive data → never in logs
- User input → sanitize before display
- Deep links → validate before navigation

## Architecture
- Clean Architecture: UI → Domain → Data
- Single responsibility per file (max 300 lines)
- Feature-based organization preferred

## Reference
Full skill: ~/.windsurf/skills/skill-mobile-mt/
Patterns from 30+ production repos (200k+ GitHub stars)
`,
  },
};

// Agents that need project-level files (don't just read from skills dir)
const NEEDS_PROJECT_FILE = new Set(['cursor', 'copilot', 'windsurf', 'cline', 'roocode', 'kilocode', 'kiro']);

function initProjectFiles(dir, agents) {
  const project = detectProject(dir);
  let created = 0;

  for (const key of agents) {
    const agent = PROJECT_AGENTS[key];
    if (!agent) continue;

    const targetDir = join(dir, agent.dir);
    const targetFile = join(targetDir, agent.file);

    if (existsSync(targetFile)) {
      info(`${c.yellow}${agent.file}${c.reset} already exists — skipped (won't overwrite)`);
      continue;
    }

    mkdirSync(targetDir, { recursive: true });
    writeFileSync(targetFile, agent.generate(project), 'utf-8');
    ok(`${c.bold}${join(agent.dir, agent.file)}${c.reset} → ${agent.name} ${c.dim}(auto-detected: ${project.framework})${c.reset}`);
    created++;
  }

  return created;
}

async function selectProjectAgents() {
  if (!process.stdin.isTTY) return Object.keys(PROJECT_AGENTS);

  const keys    = Object.keys(PROJECT_AGENTS);
  const selected = new Set(keys); // all selected by default
  let cursor    = 0;

  const UP       = '\x1b[A';
  const DOWN     = '\x1b[B';
  const ERASE_DN = '\x1b[J';
  const HIDE_CUR = '\x1b[?25l';
  const SHOW_CUR = '\x1b[?25h';
  const moveUp   = n => `\x1b[${n}A`;
  const TOTAL_LINES = 3 + keys.length;

  function render(first) {
    if (!first) process.stdout.write(moveUp(TOTAL_LINES) + ERASE_DN);
    process.stdout.write(`\n${c.bold}  Select project-level files to generate:${c.reset}\n`);
    process.stdout.write(`  ${c.dim}↑↓ navigate   Space toggle   A select all   Enter confirm   Q cancel${c.reset}\n`);

    for (let i = 0; i < keys.length; i++) {
      const k     = keys[i];
      const agent = PROJECT_AGENTS[k];
      const isCur = i === cursor;
      const isSel = selected.has(k);

      const ptr   = isCur ? `${c.cyan}›${c.reset}` : ' ';
      const box   = isSel ? `${c.green}◉${c.reset}` : `${c.dim}◯${c.reset}`;
      const name  = isCur ? `${c.bold}${c.cyan}${agent.name}${c.reset}` : agent.name;
      const file  = `${c.dim}→ ${join(agent.dir, agent.file)}${c.reset}`;

      process.stdout.write(`  ${ptr} ${box} ${name.padEnd(20)}${file}\n`);
    }
  }

  process.stdout.write(HIDE_CUR);
  render(true);

  return new Promise(resolve => {
    process.stdin.setRawMode(true);
    process.stdin.resume();
    process.stdin.setEncoding('utf8');

    const onKey = key => {
      const done = result => {
        process.stdin.setRawMode(false);
        process.stdin.pause();
        process.stdin.off('data', onKey);
        process.stdout.write(SHOW_CUR + '\n');
        resolve(result);
      };

      if (key === '\x03') { done(null); process.exit(0); }
      if (key === 'q' || key === 'Q' || key === '\x1b') { done([]); return; }
      if (key === '\r' || key === '\n') { done([...selected]); return; }

      if (key === UP)    cursor = (cursor - 1 + keys.length) % keys.length;
      else if (key === DOWN) cursor = (cursor + 1) % keys.length;
      else if (key === ' ') {
        if (selected.has(keys[cursor])) selected.delete(keys[cursor]);
        else selected.add(keys[cursor]);
      } else if (key === 'a' || key === 'A') {
        if (selected.size === keys.length) selected.clear();
        else keys.forEach(k => selected.add(k));
      }

      render(false);
    };

    process.stdin.on('data', onKey);
  });
}

// ─── Checkbox UI ─────────────────────────────────────────────────────────────

async function selectAgents(detected) {
  if (!process.stdin.isTTY) {
    return detected.length ? detected : ['claude'];
  }

  const keys    = Object.keys(AGENTS);
  const selected = new Set(detected); // pre-tick detected agents
  let cursor    = 0;

  const UP       = '\x1b[A';
  const DOWN     = '\x1b[B';
  const ERASE_DN = '\x1b[J';
  const HIDE_CUR = '\x1b[?25l';
  const SHOW_CUR = '\x1b[?25h';
  const moveUp   = n => `\x1b[${n}A`;

  // header = 3 lines (title + hint + blank), items = keys.length
  const TOTAL_LINES = 3 + keys.length;

  function render(first) {
    if (!first) process.stdout.write(moveUp(TOTAL_LINES) + ERASE_DN);

    process.stdout.write(`\n${c.bold}  Select agents to install:${c.reset}\n`);
    process.stdout.write(`  ${c.dim}↑↓ navigate   Space toggle   A select all   Enter confirm   Q cancel${c.reset}\n`);

    for (let i = 0; i < keys.length; i++) {
      const k     = keys[i];
      const agent = AGENTS[k];
      const isCur = i === cursor;
      const isSel = selected.has(k);
      const isDet = detected.includes(k);

      const ptr   = isCur ? `${c.cyan}›${c.reset}` : ' ';
      const box   = isSel ? `${c.green}◉${c.reset}` : `${c.dim}◯${c.reset}`;
      const name  = isCur ? `${c.bold}${c.cyan}${agent.name}${c.reset}` : agent.name;
      const badge = isDet ? ` ${c.green}[detected]${c.reset}` : `${c.dim} [not found]${c.reset}`;

      process.stdout.write(`  ${ptr} ${box} ${name.padEnd(14)}${badge}\n`);
    }
  }

  process.stdout.write(HIDE_CUR);
  render(true);

  return new Promise(resolve => {
    process.stdin.setRawMode(true);
    process.stdin.resume();
    process.stdin.setEncoding('utf8');

    const onKey = key => {
      const done = result => {
        process.stdin.setRawMode(false);
        process.stdin.pause();
        process.stdin.off('data', onKey);
        process.stdout.write(SHOW_CUR + '\n');
        resolve(result);
      };

      if (key === '\x03') { done(null); process.exit(0); }      // Ctrl+C
      if (key === 'q' || key === 'Q' || key === '\x1b') { done([]); return; } // quit
      if (key === '\r' || key === '\n') { done([...selected]); return; }      // Enter

      if (key === UP)    cursor = (cursor - 1 + keys.length) % keys.length;
      else if (key === DOWN) cursor = (cursor + 1) % keys.length;
      else if (key === ' ') {
        if (selected.has(keys[cursor])) selected.delete(keys[cursor]);
        else selected.add(keys[cursor]);
      } else if (key === 'a' || key === 'A') {
        if (selected.size === keys.length) selected.clear();
        else keys.forEach(k => selected.add(k));
      }

      render(false);
    };

    process.stdin.on('data', onKey);
  });
}

// ─── Main ─────────────────────────────────────────────────────────────────────

async function main() {
  const args  = process.argv.slice(2);
  const flags = new Set(args.map(a => a.replace(/^--?/, '')));

  banner();

  // ─── --init mode: generate project-level files ─────────────────────────────
  if (flags.has('init')) {
    const cwd = process.cwd();
    log(`${c.bold}  📁 Project directory:${c.reset} ${c.dim}${cwd}${c.reset}`);

    const project = detectProject(cwd);
    log(`${c.bold}  🔍 Detected:${c.reset} ${c.cyan}${project.framework}${c.reset} (${project.language})\n`);

    // Determine which agents to init
    let initTargets = [];
    const initIdx = args.indexOf('--init');
    const initArg = args[initIdx + 1];

    if (initArg === 'all') {
      initTargets = Object.keys(PROJECT_AGENTS);
    } else if (initArg && PROJECT_AGENTS[initArg]) {
      initTargets = [initArg];
    } else if (initArg && !initArg.startsWith('-')) {
      fail(`Unknown agent: ${initArg}. Available: ${Object.keys(PROJECT_AGENTS).join(', ')}, all`);
      process.exit(1);
    } else {
      // Interactive selection
      const chosen = await selectProjectAgents();
      if (!chosen || chosen.length === 0) { info('Cancelled.'); return; }
      initTargets = chosen;
    }

    log(`\n${c.bold}  Generating project-level rules...${c.reset}\n`);
    const n = initProjectFiles(cwd, initTargets);

    if (n > 0) {
      log(`\n${c.green}${c.bold}  ✅ Done!${c.reset} → ${n} file(s) generated\n`);
      log(`  ${c.bold}Generated files:${c.reset}`);
      for (const k of initTargets) {
        const agent = PROJECT_AGENTS[k];
        if (agent) {
          const fp = join(agent.dir, agent.file);
          log(`    ${c.green}●${c.reset} ${agent.name.padEnd(18)} ${c.dim}${fp}${c.reset}`);
        }
      }
      log(`\n  ${c.dim}Files are auto-detected for ${project.framework}.`);
      log(`  Edit the generated files to customize for your project.${c.reset}\n`);
    } else {
      info('No files generated (all already exist).\n');
    }
    return;
  }

  // ─── Normal install mode ───────────────────────────────────────────────────
  showContext();

  let targets = [];

  if (flags.has('all')) {
    targets = Object.keys(AGENTS);
  } else if (flags.has('auto')) {
    targets = Object.keys(AGENTS).filter(k => AGENTS[k].detect());
    if (!targets.length) { info('No agents found. Using Claude.'); targets = ['claude']; }
  } else if (flags.has('humanizer')) {
    // Install humanizer-mobile as a separate skill
    const src = join(PKG_ROOT, 'humanizer', 'humanizer-mobile.md');
    if (!existsSync(src)) { fail('humanizer/humanizer-mobile.md not found'); process.exit(1); }
    const detected = Object.keys(AGENTS).filter(k => AGENTS[k].detect());
    const agentKeys = detected.length ? detected : ['claude'];
    for (const k of agentKeys) {
      const dst = join(AGENTS[k].dir, 'humanizer-mobile');
      mkdirSync(dst, { recursive: true });
      cpSync(src, join(dst, 'humanizer-mobile.md'), { force: true });
      ok(`${c.bold}humanizer-mobile/${c.reset} → ${AGENTS[k].name} ${c.dim}(${dst})${c.reset}`);
    }
    log(`\n${c.green}${c.bold}  ✅ Done!${c.reset}\n`);
    log(`  ${c.bold}Usage:${c.reset}`);
    log(`    ${c.cyan}@humanizer-mobile${c.reset}  Humanize app store copy, release notes, error messages\n`);
    return;
  } else if (flags.has('path')) {
    const p = args[args.indexOf('--path') + 1];
    if (!p) { fail('--path needs a directory'); process.exit(1); }
    install(resolve(p), 'Custom');
    log(`\n${c.green}${c.bold}  ✅ Done!${c.reset}\n`);
    return;
  } else {
    for (const k of Object.keys(AGENTS)) if (flags.has(k)) targets.push(k);
  }

  // Interactive checkbox when no flag given
  if (!targets.length) {
    const detected = Object.keys(AGENTS).filter(k => AGENTS[k].detect());
    const chosen   = await selectAgents(detected);

    if (!chosen || chosen.length === 0) {
      info('Cancelled.');
      return;
    }
    targets = chosen;
  }

  log(`\n${c.bold}  Installing...${c.reset}\n`);
  for (const k of targets) install(AGENTS[k].dir, AGENTS[k].name);

  log(`\n${c.green}${c.bold}  ✅ Done!${c.reset} → ${targets.length} agent(s)\n`);
  log(`  ${c.bold}Usage:${c.reset}`);
  log(`    ${c.cyan}@skill-mobile-mt${c.reset}         Pre-built patterns (30+ production repos)`);
  log(`    ${c.cyan}@skill-mobile-mt project${c.reset} Read current project, adapt to it\n`);
  log(`  ${c.bold}Installed to:${c.reset}`);
  for (const k of targets) {
    log(`    ${c.green}●${c.reset} ${AGENTS[k].name.padEnd(14)} ${c.dim}${AGENTS[k].dir}/${SKILL_NAME}${c.reset}`);
  }

  // Show tip for agents that need project-level files
  const needsInit = targets.filter(k => NEEDS_PROJECT_FILE.has(k));
  if (needsInit.length > 0) {
    const names = needsInit.map(k => AGENTS[k].name).join(', ');
    log('');
    log(`  ${c.yellow}${c.bold}💡 Important:${c.reset} ${names} read rules from ${c.bold}project-level files${c.reset},`);
    log(`     not from the skills directory. Run this in your project root:`);
    log('');
    log(`     ${c.cyan}npx @buivietphi/skill-mobile-mt --init${c.reset}`);
    log('');
    log(`     This generates project-level rules files`);
    log(`     (${c.bold}.cursorrules${c.reset}, ${c.bold}.clinerules/${c.reset}, ${c.bold}.roo/rules/${c.reset}, etc.) with auto-detected settings.\n`);
  } else {
    log('');
  }
}

main().catch(e => { fail(e.message); process.exit(1); });
