---
name: github-auth-recovery
description: Automatically recover from GitHub CLI authentication failures. Use when any gh command fails with 401, SAML enforcement, token invalid, or authentication-related errors.
---

# GitHub Auth Recovery

## When Triggered

Any `gh` CLI command fails with one of these errors:
- `HTTP 401: Requires authentication`
- `Token is invalid`
- `Resource protected by organization SAML enforcement`
- `Could not resolve to a Repository`
- Any other auth/token-related GitHub CLI error

## Recovery Flow

### Step 1: Diagnose

Run `gh auth status` to determine the failure type.

### Step 2: Handle by failure type

**A) Token is invalid / expired / missing from keyring:**

1. Ask the user: "Your GitHub token is no longer in the keyring. Please paste your lifetime token and I'll set it up."
2. Once provided, run: `echo "<token>" | gh auth login --with-token`
3. Verify with `gh auth status`
4. Retry the original command

**B) SAML / SSO authorization required:**

The error will contain an authorization URL. Do this:

1. Extract the URL from the error message
2. Tell the user exactly this (nothing more):
   > Open this link and approve access, then tell me "done":
   > [the SSO authorization URL]
3. Wait for user to confirm
4. Retry the original command

**C) Token is valid but command still fails:**

Check if it's a permissions/scope issue. Inform the user which scope is missing.

### Step 3: Retry

After auth is recovered, **immediately retry the original command that failed**. Do not ask the user to repeat their request.

## Important Rules

- **NEVER** store or hardcode tokens in any file. Tokens belong only in the system keyring via `gh auth login`.
- **NEVER** log or display the full token in chat output.
- **Keep it fast** — no lengthy explanations about what went wrong. Diagnose, fix, retry.
- If SSO link is needed, give the user **just the link** — no tutorial about what SSO is or how it works.
- **NEVER ask the user to run commands in their terminal.** You have full permission to run all `gh auth` and recovery commands yourself using the Shell tool. The only thing the user should ever need to do is open a link in their browser or paste a token — everything else you handle directly.
