# Device evidence

Native claims need the environment that creates them. Record enough detail for another engineer to repeat the result.

## Evidence header

```text
Commit:
Build type/profile:
React Native / Expo:
Platform and OS:
Device or simulator model:
Architecture and JS engine:
Feature flags/account/fixture:
Network state:
Accessibility and text settings:
```

## Lifecycle reproduction

Test separately:

1. screen blur/focus inside the app;
2. app inactive through system overlay;
3. background and immediate return;
4. background long enough for stale data/session;
5. process termination from background;
6. cold relaunch and restoration.

Do not use “force quit from the app switcher” as the only process-death test; it may signal explicit user intent and differ from system reclamation.

Record persisted draft, pending request, route, subscription count, media/sensor state, and server reconciliation.

## Deep-link matrix

| Entry | iOS | Android |
| --- | --- | --- |
| App not running | Test | Test |
| App backgrounded | Test | Test |
| App active on another screen | Test | Test |
| Authenticated | Test | Test |
| Signed out/expired | Test | Test |
| Invalid/unauthorized params | Test | Test |

Use the platform's actual universal/app-link route when origin claiming is part of the behavior. A manually invoked custom scheme does not prove domain association.

## Permission matrix

Exercise with a fresh install or reset permission state:

- not determined → grant;
- not determined → deny;
- deny → request again where allowed;
- blocked/never ask again → settings recovery;
- limited/approximate permission;
- unavailable hardware or restricted device;
- permission revoked while app is backgrounded.

Capture both visible state and the native permission result.

## Accessibility evidence

On VoiceOver and TalkBack:

- traverse to the control;
- record spoken label, role, state, value, and hint;
- activate it;
- trigger changed dynamic state;
- verify focus destination after navigation/modal/error;
- exercise custom action or alternative to gesture;
- repeat at a large accessibility text size.

Accessibility Inspector is useful, but physical screen-reader output is stronger for focus order and announcements.

## Performance evidence

Use a release build and representative hardware. Capture:

- input-to-feedback latency;
- JS and UI frame rates;
- React commit duration when React is involved;
- native trace for UI/layout/image work;
- memory before, during, and after repeated interaction;
- list dataset and scroll script;
- cold/warm startup milestones.

Repeat the same script at least enough times to distinguish a stable result from one noisy run. Note thermal throttling and debugger attachment.

## Build evidence

For configuration or native integration, use:

- static config output when the workflow provides it;
- native project diff generated from a clean source;
- compile/build logs for both platforms;
- installed application identity and entitlements/permissions;
- runtime version and update channel visible from the built app or release service.

A config file looking correct does not prove the binary contains it.

## OTA evidence without publishing

Review can safely inspect:

- runtime policy and native version;
- channel/branch/profile mapping;
- diff classification: JS/assets versus native/config;
- local export/bundle when non-mutating by project convention;
- existing update metadata and monitoring.

Do not publish or repoint a channel. If installed-runtime compatibility requires a live service check not available, mark it `Not verified`.

## Source-only findings

Source alone can prove some defects: a token written to AsyncStorage, a Hook rule violation, a missing required manifest entry, or an OTA change importing a new native module. It cannot prove frame rate, gesture quality, keyboard geometry, spoken output, or real link association.

State the narrowest claim the evidence supports.
