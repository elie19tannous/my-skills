# Navigation and lifecycle

Mobile navigation is a restorable state machine with several entry points. The app may be backgrounded or killed between any two steps.

## Route identity

For every screen, define:

- stable route name/path;
- typed and validated parameters;
- parent navigator and back behavior;
- deep-link representation where shareable;
- title and accessibility announcement;
- state that persists across remount;
- state that must reset for a new route identity.

Keep entity identity in route parameters. Keep secrets, large objects, and mutable drafts elsewhere.

Do not pass a full object when an identifier lets the destination read authoritative data. Objects in route state become stale and may not serialize cleanly.

## Entry points

Trace each applicable entry:

- cold launch from app icon;
- warm foreground;
- push notification;
- universal link or Android App Link;
- custom URL scheme;
- share extension, file, or platform intent;
- restored navigation state.

Normalize all external entry data through one validation and routing boundary. Do not let each screen parse raw payloads differently.

## Back behavior

- Preserve iOS navigation expectations and Android system back behavior.
- Close the most local transient layer before navigating away.
- Confirm or preserve unsaved work when back would destroy it.
- Do not trap the user in a screen opened from an external entry point.
- Test gesture back, header back, hardware/system back, and programmatic back where applicable.

Avoid custom back handlers when navigator configuration can express the contract.

## AppState model

Treat lifecycle as events, not a reliable timer:

| Transition | Questions |
| --- | --- |
| active → inactive/background | Pause media? Persist draft? Obscure sensitive UI? Stop sensor? |
| background → active | Refresh authority? Recheck permission/session? Resume safely? |
| process killed | What state was durable? What pending work can replay? |
| memory pressure | Can caches or heavy views release resources? |

Time may pass and the process may disappear while backgrounded. On resume, compare authoritative timestamps and state; do not merely continue a JavaScript countdown.

## Subscriptions

Native events, AppState, keyboard, dimensions, linking, NetInfo, and navigation focus listeners all require symmetric cleanup.

- Keep the subscription handle returned by the current API.
- Remove exactly that subscription.
- Avoid registering on every focus without cleanup.
- Do not conflate screen focus with app foreground state.
- Make repeated focus/background transitions idempotent.

## Pending work

For a request or mutation during backgrounding:

- decide whether it may continue;
- persist only replay-safe intent;
- prevent duplicate replay after the original succeeds;
- reconcile with server state on return;
- surface a queued, completed, failed, or conflicted state.

Do not assume JavaScript background execution is available indefinitely. Use platform-supported background tasks only when the feature truly needs them and test operating-system limits.

## Authentication lifecycle

- Restore credentials from secure storage before choosing the authenticated route tree.
- Render an intentional bootstrap state instead of flashing the signed-out screen.
- Revalidate expired or revoked sessions.
- Clear sensitive caches and navigation history on sign-out.
- Handle biometric cancellation separately from failure.
- Return users to a safe, meaningful location after re-authentication.

## Restoration

Persist navigation state only when the product benefits and the state contains no sensitive or obsolete route data. Version the persisted shape and discard it safely after incompatible app changes.

For drafts, store domain state separately from navigator internals so recovery survives route refactors.

## Primary references

- [React Native AppState](https://reactnative.dev/docs/appstate)
- [React Native Linking](https://reactnative.dev/docs/linking)
- [Expo linking](https://docs.expo.dev/linking/overview/)
- [Expo background tasks](https://docs.expo.dev/versions/latest/sdk/background-task/)
