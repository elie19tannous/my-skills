# My Claude Skills

Collection of **14,888 skills** gathered with Claude Code since day 1.

Each top-level folder is one skill — see its `SKILL.md` for what it does and when it triggers.
16,400 `SKILL.md` files in total (some skills bundle sub-skills).

## History

| Date | Skills |
|------|--------|
| 2026-07-23 | 4,140 |
| 2026-08-06 | 14,888 |

Latest addition: a GitHub-wide sweep of 345 agent-skill repositories, 238 of them installed —
covering security/DFIR, academic publishing (per-journal packs), game development,
Apple/iOS, cloud (AWS/Azure/GCP), legal, finance/trading, design systems, and media generation.

## Install

```bash
npx -y skills@latest add elie19tannous/my-skills -g --copy --skill '*' -y
```

Or copy any single folder into `~/.claude/skills/`.

## Credit

These skills come from many open-source authors across GitHub. Each folder keeps its
original contents and license where the source repo provided one.
