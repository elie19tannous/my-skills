# Testing, builds, and updates

A passing JavaScript test does not prove a native binary. Verify at each boundary introduced by the change.

## Test layers

| Layer | Proves |
| --- | --- |
| Static analysis | Types, lint rules, configuration shape |
| Unit | Pure domain logic and transitions |
| Component | Rendered states and user interaction through native primitives |
| Feature integration | Navigation, storage, data, permissions, and feature boundaries |
| Device end-to-end | Real binary, OS integration, gestures, deep links, lifecycle, release config |

Prefer queries by visible text, role, label, state, and accessibility value. Avoid assertions on component internals or `testID` when a user-observable query exists.

## Native capability tests

Mock platform modules for focused component tests, but keep at least one device-level path for the real integration:

- permission prompt and denial;
- secure storage and biometric invalidation;
- notification receipt and tap;
- deep/universal/app link cold and warm entry;
- camera, media, location, files, or share sheet;
- background/foreground and process restart;
- keyboard, dynamic type, VoiceOver, and TalkBack.

A mock that always returns granted cannot protect a feature's permission state machine.

## Build types

- Use Expo Go only for capabilities it actually contains.
- Use a development build for custom native modules and realistic native configuration.
- Use release builds for performance, minification, production environment, signing, and store behavior.
- Keep internal/preview/production profiles distinct and document their endpoints, identifiers, update channels, and credentials.

Do not share a production application identifier with an internal profile unless the release process deliberately requires it.

## Device matrix

At minimum, record:

- one current and one oldest-supported OS per platform where practical;
- small and large screen class;
- representative lower/mid device for performance;
- physical iOS and Android devices for platform capabilities;
- locale, RTL, dynamic type, reduced motion, and screen-reader passes relevant to the change.

State exactly what was not tested.

## Signing and credentials

Keep signing keys, certificates, provisioning profiles, service credentials, and store access outside Git. Limit access, rotate on compromise, and document recovery ownership.

Before store submission, verify application ID, version/build numbers, entitlements, privacy declarations, permission text, icons/splash, release endpoint, analytics/crash environment, and update channel.

## OTA boundary

An over-the-air JavaScript/assets update must remain compatible with the native runtime already installed.

- Define runtime/version compatibility deliberately.
- Publish to the intended channel/branch/profile.
- Do not ship code that calls a native module absent from the target runtime.
- Roll out gradually when the update system supports it.
- Monitor adoption, startup failure, crash, and rollback signals.
- Keep a tested recovery or rollback path.
- Use a new binary for native code, entitlements, permissions, config plugins, or incompatible runtime changes.

An OTA update changes delivery speed, not the requirement for tests and review.

## Update startup behavior

Choose an update strategy that balances freshness with launch reliability:

- background download for ordinary updates;
- explicit reload only when the user will not lose work;
- bounded startup wait for truly critical updates;
- fallback to the embedded bundle when remote update load fails.

Never trap the app behind an unbounded network check at launch.

## Release verification ledger

| Check | iOS | Android | Evidence |
| --- | --- | --- | --- |
| Static and focused tests | Pass/Fail | Pass/Fail | Commands |
| Development build | Result | Result | Build/profile |
| Release smoke | Result | Result | Device/OS |
| Deep entry | Result | Result | Cold + warm paths |
| Lifecycle | Result | Result | Background + process restart |
| Accessibility | Result | Result | VoiceOver/TalkBack + text size |
| Performance | Result | Result | Build/device/trace |
| Update compatibility | Result | Result | Runtime/channel/rollback |

## Primary references

- [React Native testing overview](https://reactnative.dev/docs/testing-overview)
- [Expo build introduction](https://docs.expo.dev/build/introduction/)
- [Expo updates](https://docs.expo.dev/eas-update/introduction/)
- [Downloading Expo updates](https://docs.expo.dev/eas-update/download-updates/)
