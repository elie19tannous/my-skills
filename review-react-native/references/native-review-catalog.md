# Native review catalog

Use only the categories touched by the change. Each item requires an affected platform, reachable path, and correction outcome.

## Workflow and configuration

Look for:

- app config changed while committed native output remains stale;
- native files hand-edited even though prebuild/config plugins own them;
- usage description, entitlement, manifest permission, intent filter, or associated domain missing on one platform;
- environment endpoint, bundle/application ID, or update channel mapped to the wrong profile;
- native dependency requiring a development build while the documented flow uses Expo Go;
- package incompatible with installed React Native/Expo or architecture;
- secret embedded in public config or native resources.

Evidence: exact workflow source of truth, generated/native diff, build profile, and installed versions.

Do not flag a native directory merely because a managed project can generate one. Establish the repository's ownership convention.

## Navigation and external entry

Look for:

- route parameter accepted without shape validation;
- full mutable object passed where an ID is required;
- custom scheme trusted as proof of origin;
- high-impact action executed directly from a link/push payload;
- cold-start link works but warm event is unhandled, or the reverse;
- Android back exits or skips a local layer unexpectedly;
- sign-out leaves sensitive routes in history;
- restored route points to deleted or unauthorized data.

Evidence: cold and warm entry sequence, navigator state, and authorization boundary.

Do not require every screen to be deep-linkable.

## Lifecycle and subscriptions

Look for:

- listener added repeatedly on focus or render without matching removal;
- screen focus used as a substitute for app foreground state;
- timer/session/media continuing from an assumed elapsed JS timeline after background;
- draft persisted only on unmount;
- pending mutation replayed without idempotency after process restart;
- sensitive content visible in the app switcher where risk requires shielding;
- resume path trusts stale permission or authentication state.

Evidence: active/background/process-death sequence and external resource count or persisted result.

Do not report theoretical process death when the state is intentionally disposable and user impact is negligible.

## Storage and permissions

Look for:

- token or secret in AsyncStorage, ordinary files, persisted Redux/query state, logs, analytics, or crash payloads;
- secure-store failure, biometric invalidation, sign-out clearing, or backup behavior ignored;
- irreplaceable data kept only in device key-value storage;
- permission flow models only granted/denied and dead-ends on blocked/limited states;
- permission requested at launch with no user context;
- repeated prompt loop after denial;
- capability called without availability check.

Evidence: data classification, exact storage adapter, platform permission state, and recovery path.

## Lists and data

Look for:

- unbounded collection rendered through `ScrollView` and `.map`;
- unstable/index keys on changing rows;
- pagination end callback starting duplicate requests;
- page merge duplicating identity;
- refresh discarding safe prior data or scroll context;
- failed next page erasing loaded pages;
- nested same-direction virtualized list disabling windowing;
- oversized images decoded for rows;
- row-local state attached to render position.

Evidence: dataset threshold, mutation sequence, render count/trace, or visible wrong row.

Do not insist on virtualization for a small fixed collection.

## Threads, animation, and gestures

Look for:

- per-frame gesture value crossing to JavaScript;
- heavy synchronous work before pressed feedback;
- layout/image-size animation causing measured UI-thread stalls;
- animation library/native driver used outside installed support;
- gesture conflict with scrolling or platform back;
- drag-only action with no accessibility alternative;
- animation ignores reduced-motion state;
- rasterization/hardware-layer flag retained outside the motion and consuming memory.

Evidence: release trace separated by JS/UI thread, gesture reproduction, and device.

Do not report style declarations as performance defects without a measured path.

## Keyboard, safe areas, and accessibility

Look for:

- fixed-position action hidden by keyboard or gesture area;
- focused field/error unreachable above keyboard;
- touch targets or hit slop overlapping;
- visible label absent from accessible name;
- selected/disabled/expanded/busy state not exposed;
- focus lost when modal opens/closes or major state replaces;
- dynamic update unannounced or assertive for routine status;
- fixed height/disabled scaling clipping large text;
- nested accessible parents swallowing children on one platform.

Evidence: platform accessibility tree, VoiceOver/TalkBack behavior, text-size setting, or exact geometry.

## Build and OTA

Look for:

- JavaScript update references native capability missing from target runtime;
- native/config/entitlement change scheduled as OTA only;
- production profile points at staging service/channel;
- update strategy blocks launch indefinitely;
- no fallback to embedded working bundle;
- rollback path cannot reach affected users;
- version/build number or signing identity inconsistent with release target;
- monitoring cannot distinguish runtime/channel/version.

Evidence: runtime policy, profile/channel mapping, native diff, and update target.

Never publish an update to prove a review finding.
