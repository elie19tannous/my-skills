---
name: mobile-device-control
description: >
  Complete guide for controlling iOS Simulator and Android Emulator from an AI agent.
  Covers: setup, boot, screenshots, video recording, app navigation, auth injection into React Native apps,
  tap automation, Expo tunnels, and lessons learned. Use this for QA automation, video walkthroughs,
  and visual regression testing of any mobile app.
---

# Mobile Device Control — iOS Simulator & Android Emulator
*Complete agent reference for mobile QA automation*

---

## 1. Prerequisites

### Required Tools
| Tool | Install | Purpose |
|------|---------|---------|
| `xcrun simctl` | Xcode (Mac App Store) | iOS Simulator control |
| `ffmpeg` | `brew install ffmpeg` | Video conversion |
| `osascript` | Built-in macOS | UI automation via AppleScript |
| `cliclick` | `brew install cliclick` | Mouse click automation |
| `adb` | Android Studio or SDK | Android device bridge |
| `Maestro` | `curl -Ls "https://get.maestro.mobile.dev" \| bash` | Flow-based mobile UI testing |

### Environment Variables (Android — add to `~/.zshrc`)
```bash
export ANDROID_HOME=~/Library/Android/sdk
export PATH=$PATH:$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator
export JAVA_HOME=/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home
```
⚠️ **Java 17 strictly required** for Android — Java 21+ breaks Gradle for most React Native apps.

---

## 2. iOS Simulator

### Find Your Simulator UDID
```bash
# List all available simulators
xcrun simctl list devices

# Find booted ones
xcrun simctl list devices booted
```

### Boot & Open
```bash
UDID="YOUR-SIMULATOR-UDID"

# Boot
xcrun simctl boot $UDID

# Open the Simulator window
open -a Simulator
sleep 5

# Check status
xcrun simctl list devices booted | grep $UDID
```

### Install an App
```bash
# Install from .app build
xcrun simctl install $UDID /path/to/YourApp.app

# Or use Expo dev client / Metro bundler (see §5 Expo Tunnel)
```

### Launch & Kill
```bash
BUNDLE_ID="com.yourcompany.yourapp"

# Launch
xcrun simctl launch $UDID $BUNDLE_ID

# Kill
xcrun simctl terminate $UDID $BUNDLE_ID

# Full reset (uninstall + reinstall)
xcrun simctl uninstall $UDID $BUNDLE_ID
```

### Screenshot
```bash
xcrun simctl io $UDID screenshot /tmp/ios-screen.png
```
⚠️ Output is **Retina (2x)** — image pixel dimensions are 2× the logical screen points.

### Video Recording
```bash
# Start recording — H264 codec required
xcrun simctl io $UDID recordVideo --codec=h264 /tmp/ios-raw.mp4 &
REC_PID=$!

# ... interact with the app ...

# Stop recording
kill $REC_PID
sleep 2  # allow file flush

# Convert to H264 MP4 (always do this — raw output may not play everywhere)
ffmpeg -i /tmp/ios-raw.mp4 -c:v libx264 -c:a aac -movflags faststart /tmp/ios-final.mp4 -y
```
⚠️ **Always convert before sending** — never send raw `xcrun simctl` video output.

### Tapping / Clicking the Simulator
There is no direct `simctl tap` command. Use one of these:

**Method 1: osascript (most reliable)**
```bash
# Get simulator window bounds first
BOUNDS=$(osascript -e 'tell application "Simulator" to get bounds of window 1')
# Returns: "left, top, right, bottom"  e.g. "877, 44, 1333, 1016"

# Parse and calculate mac screen coordinates from device logical points:
# Window width = right - left, window height = bottom - top
# Device logical size = e.g. 393×852 (iPhone 16 Pro)
# mac_x = left + device_x * (window_width / device_logical_width)
# mac_y = top  + device_y * (window_height / device_logical_height)

# Click at calculated mac coordinates
MAC_X=1050
MAC_Y=965
osascript -e "tell application \"System Events\" to click at {$MAC_X, $MAC_Y}"
```

**Method 2: cliclick**
```bash
/opt/homebrew/bin/cliclick c:${MAC_X},${MAC_Y}
```

**Method 3: Maestro (best for complex flows)**
```yaml
# flows/walkthrough.yaml
appId: com.yourcompany.yourapp
---
- launchApp
- tapOn:
    id: "tab-home"
- takeScreenshot: home-screen
- tapOn:
    id: "tab-settings"
```
```bash
~/.maestro/bin/maestro test flows/walkthrough.yaml
```

### Auth Injection for React Native / Expo Apps
Many apps use AsyncStorage to persist auth tokens. You can inject tokens directly to bypass the login screen.

**How AsyncStorage stores data on iOS:**
- Directory: `~/Library/Developer/CoreSimulator/Devices/{UDID}/data/Containers/Data/Application/{CONTAINER_UUID}/Library/RCTAsyncLocalStorage_V1/`
- `manifest.json` — maps key → `"null"` (pointer to chunk file) or value inline
- Chunk files — named after MD5 of the key, contain the actual value

**Find the app container:**
```bash
find ~/Library/Developer/CoreSimulator/Devices/{UDID}/data/Containers/Data/Application \
  -name ".com.apple.mobile_container_manager.metadata.plist" | \
  xargs grep -l "com.yourcompany.yourapp" | \
  sed 's|/.com.apple.*||'
```

**Inject a token:**
```python
import json, os, hashlib

def inject_async_storage(udid, container_uuid, bundle_id, key, value_dict):
    """Inject a key-value into React Native AsyncStorage on iOS Simulator."""
    rct_path = os.path.expanduser(
        f"~/Library/Developer/CoreSimulator/Devices/{udid}"
        f"/data/Containers/Data/Application/{container_uuid}"
        f"/Library/RCTAsyncLocalStorage_V1"
    )
    os.makedirs(rct_path, exist_ok=True)
    
    # Chunk file named after MD5 of the key
    chunk_name = hashlib.md5(key.encode()).hexdigest()
    
    # Write value to chunk file
    with open(os.path.join(rct_path, chunk_name), 'w') as f:
        json.dump(value_dict, f)
    
    # Update manifest with "null" pointer (string "null", not JSON null)
    manifest_path = os.path.join(rct_path, "manifest.json")
    try:
        with open(manifest_path) as f:
            manifest = json.load(f)
    except:
        manifest = {}
    manifest[key] = "null"  # "null" string = pointer to chunk file
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f)
    
    print(f"Injected '{key}' → chunk '{chunk_name}'")

# Example: Inject Supabase auth token
inject_async_storage(
    udid="YOUR-UDID",
    container_uuid="YOUR-CONTAINER-UUID",
    bundle_id="com.yourcompany.yourapp",
    key="sb-YOUR_PROJECT_REF-auth-token",
    value_dict={"access_token": "...", "refresh_token": "...", "expires_in": 3600, ...}
)
```

**After injection — relaunch app:**
```bash
xcrun simctl terminate $UDID $BUNDLE_ID
sleep 2
xcrun simctl launch $UDID $BUNDLE_ID
sleep 10  # wait for Metro bundle + auth restore
```

---

## 3. Android Emulator

### Create & Start an Emulator
```bash
# List available AVDs
emulator -list-avds

# Start headless (recommended for QA — saves ~2GB RAM)
$ANDROID_HOME/emulator/emulator -avd YOUR_AVD_NAME -no-window -no-audio -no-snapshot &

# Wait for full boot
adb wait-for-device
until adb shell getprop sys.boot_completed 2>/dev/null | grep -q "1"; do
  echo "Waiting for boot..."; sleep 3
done
echo "Emulator ready ✅"
```

⚠️ **Never run iOS Simulator and Android Emulator simultaneously** on machines with <32GB RAM — OOM risk.

### Screenshot
```bash
adb shell screencap -p /sdcard/screen.png
adb pull /sdcard/screen.png /tmp/android-screen.png
```

### Video Recording
```bash
# Start recording (max 180s per file at 3Mbps)
adb shell screenrecord --time-limit 60 --bit-rate 3000000 /sdcard/recording.mp4 &

# ... interact with app ...

# Stop (using adb shell kill, not local kill)
adb shell killall screenrecord 2>/dev/null || true
sleep 3

# Pull and convert
adb pull /sdcard/recording.mp4 /tmp/android-raw.mp4
ffmpeg -i /tmp/android-raw.mp4 -c:v libx264 -c:a aac /tmp/android-final.mp4 -y
```

### Install & Launch App
```bash
PACKAGE="com.yourcompany.yourapp"

# Install
adb install /path/to/app-debug.apk
# Or update existing
adb install -r /path/to/app-debug.apk

# Launch
adb shell am start -a android.intent.action.MAIN \
  -c android.intent.category.LAUNCHER \
  -n $PACKAGE/.MainActivity

# Kill
adb shell am force-stop $PACKAGE
```

### Tapping
Android uses physical pixel coordinates (not logical points).

```bash
# Tap at physical pixel coordinates
adb shell input tap X Y

# Swipe
adb shell input swipe startX startY endX endY durationMs

# Type text
adb shell input text "hello"

# Press key (e.g. Back)
adb shell input keyevent 4
```

**Coordinate conversion from logical to physical:**
```
physical_x = logical_x * (screen_width_px / screen_width_dp)
physical_y = logical_y * (screen_height_px / screen_height_dp)

# Example Pixel 6 (1080×2400px, 420dpi):
# dp scale = 420/160 = 2.625
# physical_x = logical_x * 2.625
```

### Auth Injection for React Native / Expo (Android)
```bash
# AsyncStorage files (requires run-as for debug builds)
adb shell run-as $PACKAGE ls /data/data/$PACKAGE/files/RCTAsyncLocalStorage_V1/

# Inject (push file then copy into app sandbox)
# Step 1: push chunk file to sdcard
echo '{"access_token":"..."}' > /tmp/chunk
adb push /tmp/chunk /sdcard/chunk_file

# Step 2: copy into app sandbox
adb shell run-as $PACKAGE cp /sdcard/chunk_file /data/data/$PACKAGE/files/RCTAsyncLocalStorage_V1/CHUNK_MD5_NAME

# Step 3: update manifest
# (same pattern as iOS — write manifest.json with "null" pointer)
```

### Build APK (React Native / Expo)
```bash
# For Expo projects: generate native code first
npx expo prebuild --platform android

cd android
export JAVA_HOME=/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home
./gradlew assembleDebug  # ~10-15 minutes

# Install
adb install app/build/outputs/apk/debug/app-debug.apk
```

---

## 4. Expo Dev Tunnel (Physical Device + Simulator)

For testing feature branches on physical devices without building an APK/IPA:

```bash
# 1. Install ngrok support (once per project)
cd mobile && pnpm add -D @expo/ngrok@^4.1.0

# 2. Start Metro with tunnel
npx expo start --tunnel --port 8081

# 3. Get tunnel URL
curl -s http://localhost:4040/api/tunnels | python3 -c "
import sys, json
for t in json.load(sys.stdin).get('tunnels', []):
    if 'https' in t.get('public_url',''):
        print(t['public_url'])
"
```

**URL formats:**
- `exp://abc123.exp.direct` → Expo Go deep link  
- `https://abc123.exp.direct` → Browser/redirect (use this format when sharing with humans)

⚠️ If you get "non-interactive mode" error: install `@expo/ngrok` in the `mobile/` directory.

---

## 5. QA Video Workflow (Full Walkthrough)

### Pre-flight checklist
- [ ] Metro bundler running and shows "Bundled" in logs
- [ ] Correct feature branch checked out
- [ ] iOS OR Android running (not both)
- [ ] Auth injected → screenshot shows Home screen (not login)
- [ ] Correct branding/theme visible

### Recording script template
```bash
UDID="YOUR-UDID"
BUNDLE="com.yourcompany.yourapp"

# Kill, relaunch for clean start (tests startup time)
xcrun simctl terminate $UDID $BUNDLE
sleep 2
xcrun simctl launch $UDID $BUNDLE
sleep 12

# Start recording
xcrun simctl io $UDID recordVideo --codec=h264 /tmp/walkthrough-raw.mp4 &
REC=$!

sleep 5   # show home screen

# Navigate tabs (replace with your app's coordinates)
osascript -e "tell app \"System Events\" to click at {X1, Y1}"  # Tab 1
sleep 3
osascript -e "tell app \"System Events\" to click at {X2, Y2}"  # Tab 2
sleep 3
# ... etc

# Stop
kill $REC && sleep 2

# Convert
ffmpeg -i /tmp/walkthrough-raw.mp4 -c:v libx264 -c:a aac -movflags faststart /tmp/walkthrough.mp4 -y
echo "Video: $(ls -lh /tmp/walkthrough.mp4 | awk '{print $5}')"
```

### Frame analysis for QA
```bash
# Extract frames at regular intervals (30fps video)
ffmpeg -i /tmp/walkthrough.mp4 \
  -vf "select='eq(n,90)+eq(n,240)+eq(n,450)+eq(n,750)'" \
  -vsync 0 /tmp/frame-%d.png -y

# n=90 → 3s, n=240 → 8s, n=450 → 15s, n=750 → 25s
```

Use an image analysis tool on each frame. Check:
- ✅ Correct branding/colors
- ✅ Text alignment (RTL or LTR as expected)
- ✅ No overflow or clipped elements
- ✅ Tab bar fully visible, no content overlap
- ✅ No blank or loading screens

---

## 6. Common Failures & Fixes

| Problem | Symptom | Fix |
|---------|---------|-----|
| White screen after launch | App loads but no content | Metro not bundled yet — wait 15s and retry |
| Login screen despite auth inject | Auth injection silently failed | Check `manifest.json` has `"null"` (string), not `null` (JSON). Check chunk file exists. |
| `adb: command not found` | CLI error | `export PATH=$PATH:~/Library/Android/sdk/platform-tools` |
| adb Gatekeeper dialog | macOS security popup on first run | `xattr -d com.apple.quarantine $(which adb)` |
| Simulator window not found by osascript | AppleScript error | `open -a Simulator && sleep 5` before accessing bounds |
| Video file is 0 bytes | Recording killed too fast | `sleep 2` after `kill $REC_PID` before checking |
| `@expo/ngrok` not found | Tunnel error in non-interactive mode | `pnpm add -D @expo/ngrok@^4.1.0` in mobile/ dir |
| `expo/tsconfig.base not found` | TS error in git worktree | `cd mobile && pnpm install` |
| Coordinates off after Simulator restart | Clicks land in wrong place | Re-run `osascript bounds` — window position changes |
| Android screenrecord stops early | Timeout | Use `--time-limit 60` and chain files |
| Gradle build fails | Java version error | Set `JAVA_HOME` to Java 17, not 21+ |
| App installed but shows old version | Cache | `adb install -r` or uninstall first |
| cliclick coordinates unreliable | Wrong button clicked | **Use AppleScript accessibility tree instead**: find `AXButton` by title |

### AppleScript accessibility click (most reliable for buttons)
```bash
osascript << 'APPL'
tell application "System Events"
  tell process "Simulator"
    repeat with w in windows
      set allElems to entire contents of w
      repeat with e in allElems
        try
          if role of e is "AXButton" then
            set t to value of attribute "AXTitle" of e
            if t contains "YOUR_BUTTON_TITLE" then
              click e
            end if
          end if
        end try
      end repeat
    end repeat
  end tell
end tell
APPL
```

---

## 7. Lessons Learned

1. **Coordinate-based clicks fail** when window moves — always re-query bounds or use accessibility tree
2. **Container UUID changes** on app reinstall — always `find` it dynamically, never hardcode
3. **manifest.json `"null"` string** ≠ JSON `null` — the string `"null"` is the chunk file pointer
4. **Token expiry** — injected auth tokens expire (usually 1h). Re-inject before recording if >30min old
5. **Retina 2x screenshots** — iOS simctl images are 2× logical pixels; account for this in coordinate math
6. **H264 conversion** always required before sharing video — raw simctl output may not play in all players
7. **Headless Android** (`-no-window`) saves RAM and is sufficient for QA
8. **Java 17 strictly** — don't upgrade to 21+ or Gradle breaks on most RN projects
9. **adb quarantine** — clear once with `xattr -d com.apple.quarantine $(which adb)` to prevent macOS security popups
10. **Never run both simultaneously** on machines with <32GB RAM — OOM kills everything
