---
name: install-apk
description: >-
  Install APK builds to a connected Android device via adb. Scans the local
  builds folder for RC, Preview, and Feature Branch APKs. Can also fetch build
  links from Slack release channels. Use when the user wants to install an APK,
  sideload an app, install a build, push an APK to a device, mentions
  RC/Preview/feature branch builds, uses shorthand like "26.21 R W" or
  "26.21 P C", provides a .apk filename, or asks for builds from Slack
  (e.g. "26.21 slack").
---

# Install APK to Device

## Build Folders

APK files are stored locally in these locations — never in `~/Downloads/`:

- **RC & Preview builds**: `/path/to/your/builds/`
- **Feature branch builds**: `/path/to/your/builds/Feature branch/`

## Scan & Table Output

On every install request, ALWAYS do the following before installing:

1. Scan both folders (and any subfolders) for all `.apk` files:

```bash
find "/path/to/your/builds" -name "*.apk" -type f
```

2. Parse each filename to determine type, version, and region:
   - **RC builds**: filename starts with `[Company]-`, contains `Release` and `RC` (e.g. `App-26.21.0-2022211953-157-Release-RegionA-RC-Signed.apk`)
   - **Preview builds**: filename starts with `MyApp-`, contains `Debug` (e.g. `MyApp-26.21.0-26040118-157-RegionA-Debug-Signed.apk`)
   - **Feature branch builds**: any `.apk` inside the `Feature branch/` subfolder

3. Display the results in a compact table sorted in ascending order by version:
   - One row per version with four columns for each build type/region.
   - Each cell shows the shorthand the user would type to install it, or `—` if not available.
   - Only show the Feature Branch table if feature branch APKs exist.

**RC & Preview Builds**
| # | Version | RC Region A | RC Region B | Preview Region A | Preview Region B |
|---|---------|----------|----------|---------------|---------------|
| 1 | 26.18.0 | `26.18 W` | — | — | — |
| 2 | 26.21.0 | `26.21 W` | `26.21 C` | `26.21 P W` | `26.21 P C` |

**Feature Branch Builds** (only shown if feature branch APKs exist)
| # | Name | Filename |
|---|------|----------|
| 1 | EXAMPLE-PROJ-1234 | `some-feature-build.apk` |

## Shorthand Quick Install

The user will use shorthand to request installs. Match as follows:

| User says | Type | Region | Match filename containing |
|-----------|------|--------|---------------------------|
| `26.21 R W` or `26.21 W` | RC | Region A | `App-26.21.*Release-RegionA-RC` |
| `26.21 R C` or `26.21 C` | RC | Region B | `App-26.21.*Release-RegionB-RC` |
| `26.21 P W` | Preview | Region A | `MyApp-26.21.*RegionA-Debug` |
| `26.21 P C` | Preview | Region B | `MyApp-26.21.*RegionB-Debug` |
| `feature branch <name>` | Feature | — | Match `<name>` against filenames in `Feature branch/` folder |

**Default rule:** If the user only says a version + region without specifying R or P (e.g. `26.21 W` or `26.21 C`), always default to **RC (R)**.

The user may also provide a full filename — match it against scanned results.

## Install Command

Run immediately — no confirmation needed:

```bash
~/Library/Android/sdk/platform-tools/adb install "<FULL_PATH_TO_APK>"
```

If the app is already installed and the user is updating, use `-r` to replace:

```bash
~/Library/Android/sdk/platform-tools/adb install -r "<FULL_PATH_TO_APK>"
```

Always quote the path (filenames and folders contain spaces).

## Handling Errors

Do NOT ask the user for confirmation on recoverable errors. Fix them automatically.

| Error | Action |
|---|---|
| `INSTALL_FAILED_ALREADY_EXISTS` | Re-run with `-r` flag |
| `INSTALL_FAILED_UPDATE_INCOMPATIBLE` or `INSTALL_FAILED_CONFLICTING_PROVIDER` | Automatically uninstall the conflicting package, then install the new APK. Do NOT ask — just do it. |
| `INSTALL_FAILED_VERSION_DOWNGRADE` | Re-run with `-d` flag to allow downgrade: `adb install -r -d <apk>` |
| `error: no devices/emulators found` | Ask the user to connect their device via USB and enable USB Debugging |
| `INSTALL_FAILED_INSUFFICIENT_STORAGE` | Tell the user to free up space on the device |

## Examples

**User says:** "26.21 R W"

**Action:**
1. Scan folder, show table of all available builds.
2. Match `26.21 R W` → find `App-26.21.0-2022211953-157-Release-RegionA-RC-Signed.apk`
3. Install immediately:
```bash
~/Library/Android/sdk/platform-tools/adb install "/path/to/your/builds/App-26.21.0-2022211953-157-Release-RegionA-RC-Signed.apk"
```

**User says:** "26.21 P C"

**Action:**
1. Scan folder, show table of all available builds.
2. Match `26.21 P C` → find `MyApp-26.21.0-26040118-157-RegionB-Debug-Signed.apk`
3. Install immediately:
```bash
~/Library/Android/sdk/platform-tools/adb install "/path/to/your/builds/MyApp-26.21.0-26040118-157-RegionB-Debug-Signed.apk"
```

**User says:** "install feature branch EXAMPLE-PROJ-1234"

**Action:**
1. Scan `Feature branch/` subfolder, show feature branch table.
2. Match filename containing `EXAMPLE-PROJ-1234` or the card name.
3. Install immediately.

## Slack Build Lookup

Slack release channels follow the naming pattern: `yourapp-release-XX-XX` (dashes, not dots).

### Trigger

When the user mentions a version + "slack" (e.g. `26.21 slack`), use the dis-slack agent to read the channel and extract build links.

| User says | Action |
|-----------|--------|
| `26.21 slack` | Read `#yourapp-release-26-21`, list latest **Android** build links |
| `26.21 slack ios` | Read `#yourapp-release-26-21`, list latest **iOS** build links |

### Steps

1. Use the `dev-integration-server` MCP tools (preferred) or fall back to CLI (`dis call`):
   - `slack_channels` with `{"query": "yourapp-release-XX-XX"}` to find the channel ID
   - `slack_history` with `{"channel": "<CHANNEL_ID>", "limit": 20}` to get messages
2. Parse messages for build links (TestFairy URLs). iOS builds come from one message, Android from another.
3. Display the results with full build details extracted from the Slack messages:

**Android Builds — #yourapp-release-26-21**
| # | Build | Version | Build Code | Link |
|---|-------|---------|------------|------|
| 1 | RC Region A | 26.21.0 | 2022211953 | [Download](link) |
| 2 | RC Region B | 26.21.0 | 2022211953 | [Download](link) |
| 3 | Preview Region A | 26.21.0 | 26040118 | [Download](link) |
| 4 | Preview Region B | 26.21.0 | 26040118 | [Download](link) |

Always include: version, build code, download link, and who posted it with date/time. Add a "Open in Slack" permalink at the end so the user can jump directly to the message. Do NOT include package name column or rollout schedule — keep it clean.

Example footer:
`Posted by John Releaser — April 8, 2026, 9:33 PM UTC | [Open in Slack](slack://channel?team=TEAM_ID&id=CHANNEL_ID&message=MESSAGE_TS)`

Always use the `slack://` deep link format so it opens directly in the Slack desktop app — never use `https://your-org.slack.com/...` browser links.

### Adaptive Parsing

Build links are typically posted by devs in a consistent format. If the format changes over time, adapt by learning the new pattern from the messages.
