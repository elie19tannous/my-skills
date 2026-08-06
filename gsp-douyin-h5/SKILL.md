---
name: gsp-douyin-h5
description: "Use when the deliverable is a portrait-first Douyin H5 interactive and the shell or adaptation model must be locked first."
---

# Game Douyin H5

## Goal
Turn a vague "Douyin H5 Interactive" request into a concrete browser delivery shape before implementation starts.

## Outputs

Follow the `gsp-orchestrator` output strategy:
- **inline** (default): present the route, shell rules, file structure, and adaptation constraints in conversation.
- **minimal** or **full**: write or update `docs/game-studio/platform-implementation.md`.

Use `../../shared/templates/douyin-h5-shell.md` whenever a persisted shell decision record would help.

## Use when
- the platform is explicitly `Douyin H5 Interactive`, `抖音互动作品`, `抖音互动空间`, or `抖音互动H5`
- the deliverable must remain `H5-only`
- the work is portrait-first and mobile-first
- the user needs guidance on app shell, screen structure, canvas vs multi-screen route, or vertical adaptation before coding

## Strong signals
- `做一个抖音互动作品`
- `做一个抖音互动空间`
- `做一个抖音互动H5`
- `平台只接受H5，要竖屏适配`
- `先定项目框架、文件结构和适配方式`
- `先别写玩法，先把H5壳和结构定下来`

Treat these as a signal to lock the platform shell before deeper implementation work.

## Use
- `../../shared/reference/douyin-h5-interactive.md`
- `../../shared/checklists/ui-ux-hard-rules.md`
- `../../shared/reference/browser-2d-specialist.md`

## Lock these before coding
- primary route: `screen-first interactive`, `canvas-playable interactive`, or `world/canvas plus DOM HUD`
- portrait shell: `viewport-fit=cover`, one `app-shell`, safe-area ownership
- adaptation model: `ratio shell only` or `design-space plus viewport mapping`
- minimum state surface: `loading`, `menu`, primary interactive state, `result`
- ownership boundaries: shell, screen state, gameplay state, adaptation math, HUD/overlay
- interaction budget: one-hand play, thumb zones, first-action clarity

## Route choice
- `screen-first interactive` for quiz, branching, reveal flow, or text-heavy participation.
- `canvas-playable interactive` for aiming, timing, physics, spatial play, or a continuous loop.
- `world/canvas plus DOM HUD` for spatial play that still needs menus, HUD, result packaging, or overlays in DOM.

If the request still mixes multiple routes, do not silently improvise a hybrid. Lock one route first.
If the route still cannot be locked from the prompt, ask a clarifying question or route upward to `gsp-requirements-brainstorm`.

## Lock the portrait shell first
- Require `viewport-fit=cover` and portrait-first layout assumptions.
- Use a single `app-shell` that owns the visual ratio, safe-area padding, and overflow behavior.
- Use a fixed design ratio or fixed design-space before tuning details.
- Treat the screen shell and the interactive core as separate layers.
- Keep critical actions in comfortable portrait thumb zones unless the concept explicitly demands otherwise.

## File shape
- shared root: `index.html`, `css/styles.css`, `assets/` or `images/`
- screen-first: `js/app.js`, `js/ui/`, `js/data/`, `js/config/`
- canvas-playable: `js/main.js`, `js/core/`, `js/game/`, `js/ui/`, `js/input/`, `js/audio/`, `js/config.js`
- world/canvas plus DOM HUD: `js/game.js` or `js/main.js`, plus `js/core/` or `js/rules/`; use `lib/` only for true shared runtime code

For the exact shell record, fill `../../shared/templates/douyin-h5-shell.md`.

## Important adaptation rules
- choose `ratio shell only` or `design-space plus viewport mapping`
- if canvas is involved, remap input into design-space before gameplay reads it
- keep HUD and overlays outside the playfield when text density or safe-area handling matters
- lock the result state early so it does not become a bolted-on screen

## Do not do these
- Do not start from a desktop layout and shrink it into portrait later.
- Do not leave route choice implicit when the request could mean either multi-screen interaction or real-time gameplay.
- Do not mix DOM state, gameplay state, and adaptation math in one oversized file.
- Do not treat safe-area padding as the full mobile adaptation problem.
- Do not overload the top and bottom bands with permanent UI just because portrait space feels available.

## Boundary with other skills
- Use this skill to lock the platform-specific H5 shape.
- Use `gsp-ux-flow-designer` to shape onboarding, menus, CTA hierarchy, and first-minute comprehension.
- Use `gsp-web-2d-specialist` after the browser route is chosen and the project needs concrete 2D implementation guidance.
- Use `gsp-feedback-design` after the shell and route are explicit.
