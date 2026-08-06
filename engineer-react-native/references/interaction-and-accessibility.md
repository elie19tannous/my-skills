# Interaction and accessibility

Build one interaction contract that works for touch, switch control, keyboard, VoiceOver, TalkBack, and larger text—then tune platform presentation.

## Pressable contract

Every pressable exposes:

- visible affordance;
- `accessibilityRole` when the native element does not already convey it;
- concise label from visible text or an explicit label;
- value/state for selected, checked, expanded, disabled, or busy behavior;
- immediate pressed feedback;
- disabled behavior that blocks activation and remains understandable;
- reliable target size and non-overlapping hit slop.

Do not nest unrelated press targets inside one accessible parent without testing focus and activation on both platforms.

## Labels and hints

- Label the action or destination, not the icon's shape.
- Keep visible text in the accessible name.
- Use a hint only when the result is not clear from label, role, and state.
- Set language for content that differs from the app language where supported.
- Hide decorative duplicates from accessibility.
- Expose custom actions for gestures that have no obvious assistive equivalent.

Android and iOS accessibility APIs differ. Verify platform output instead of assuming one prop maps identically.

## Dynamic updates

Use polite announcements for routine status and assertive interruption only for urgent failures. Keep updates short and avoid repeatedly announcing rapidly changing progress.

Move accessibility focus only when context changes enough to require orientation: new screen, opened modal, first invalid field, or a replaced major region. Do not steal focus for toasts.

## Dynamic type

- Let text scale by default.
- Use flexible height and wrapping.
- Set maximum scaling only for a documented exceptional control after verifying the content remains available.
- Test the largest supported accessibility text sizes.
- Keep primary actions reachable when text expands.
- Do not shrink labels until they technically fit but become unreadable.

## Keyboard and safe area

- Use safe-area insets for edge-aligned content and controls.
- Keep the focused field and its error visible when the software keyboard opens.
- Test forms with different keyboard types, suggestions, autofill, and hardware keyboard.
- Avoid one universal keyboard offset copied across navigation stacks and devices.
- Ensure keyboard dismissal does not discard input or block the first press on the intended action.

## Focus and modals

On open, move accessibility focus to the modal heading or first meaningful control. Keep background content hidden from assistive navigation. On close, restore focus to the trigger or the nearest surviving context.

Test system back, swipe dismissal, close button, and accessibility escape/dismiss action.

## Gestures

- Add a small intent threshold before a drag wins over a tap or scroll.
- Track the object with the gesture and preserve grab offset.
- Resolve gesture conflicts with parent scroll and system navigation.
- Keep continuous values on the UI-native animation path.
- Send only semantic completion/cancellation to JavaScript.
- Handle interruption, extra pointers, cancellation, and app backgrounding.
- Offer buttons or accessibility actions for drag-only results.

## Motion

Use native-driver or UI-thread animation paths supported by the installed library for continuous motion. Keep layout changes and JS callbacks out of each frame.

Under reduced motion:

- remove large translation, parallax, zoom, and bounce;
- use a short fade or immediate state;
- preserve visible selection/status cues;
- stop nonessential loops and autoplay.

Test the platform preference through `AccessibilityInfo` or the project's abstraction and confirm updates if the preference changes while the app runs.

## Screen-reader test pass

On both platforms:

1. Traverse in reading order.
2. Confirm label, role, state, value, and hint.
3. Activate every primary control.
4. Complete the primary form or flow.
5. Trigger validation, request failure, loading, and success.
6. Open and close every changed overlay.
7. Confirm custom gestures have equivalent actions.
8. Verify dynamic updates announce once and do not steal focus.

Use physical devices for final confirmation. Simulator accessibility behavior and input cannot establish parity.

## Primary references

- [React Native accessibility](https://reactnative.dev/docs/accessibility)
- [React Native `AccessibilityInfo`](https://reactnative.dev/docs/accessibilityinfo)
- [React Native `Pressable`](https://reactnative.dev/docs/pressable)
- [Expo safe areas](https://docs.expo.dev/develop/user-interface/safe-areas/)
