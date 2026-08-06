# Runtime review

Use runtime inspection for claims about pixels, focus, timing, scrolling, responsive behavior, and user-perceived state.

## Prepare a reproducible surface

Record:

- start command and URL or native route;
- commit and feature flags;
- fixture or account state;
- viewport or device;
- theme, locale, text size, motion preference, and zoom;
- console or device-log baseline before interaction.

Avoid reviewing a random development state that another person cannot reproduce.

## Responsive pass

Inspect in this order:

1. Narrowest supported size.
2. Widest supported size.
3. Just below every structural breakpoint.
4. Just above every structural breakpoint.
5. A container-constrained instance when the component can render outside the main page column.

Check page-level horizontal scroll, clipped controls, sticky overlap, content reordering, safe-area clearance, fixed-height text, and actions pushed outside reachable flow.

## Content pass

Render realistic stress data:

- zero, one, and many items;
- long translated labels;
- missing optional fields;
- long names and unbroken identifiers;
- maximum and negative values;
- failed media;
- slow and failed requests.

Capture the exact fixture with the finding. A layout that breaks only with impossible data is not a valid finding.

## Keyboard pass

Start from the address bar or app entry and use no pointer:

- reach and operate every control in the primary path;
- confirm focus order follows reading order;
- confirm focus remains visible and unobscured;
- exercise Escape, Enter, Space, arrow keys, Home, and End where the component pattern expects them;
- confirm overlays trap and restore focus;
- confirm route changes move focus to the new context when needed.

Do not infer keyboard support from `tabIndex` or a component-library name.

## Accessibility pass

Inspect the accessibility tree for name, role, value, state, relationships, and hidden content. Then use the target screen reader for custom widgets, dialogs, dynamic updates, and mobile controls.

Check:

- label is present in the accessible name;
- descriptions and errors are associated with their control;
- selected, expanded, busy, invalid, and disabled states are announced;
- dynamic updates use an appropriate announcement path;
- decorative duplicates are hidden;
- zoom and text growth preserve content and function.

Automated scans supplement this pass; they do not replace it.

## Motion pass

- Trigger each changed animation once normally.
- Slow playback to inspect origin, coordinated properties, and final state.
- Reverse or repeat the interaction before completion.
- enable reduced motion and confirm an equivalent static cue.
- profile in production or release mode if smoothness is part of the claim.

Reject a motion finding based only on source duration when rendered distance, easing, and product frequency determine the feel.

## State transition pass

For each async action:

1. Start from rest.
2. Trigger once and repeatedly.
3. Observe pending state and retained context.
4. Complete successfully.
5. Repeat with validation and request failure.
6. Navigate away or remount during pending work where plausible.
7. Recover and retry.

Watch for duplicate submissions, stale success, erased input, focus loss, unannounced errors, and a local state that disagrees with persisted data.

## Capture evidence

For a visual issue, retain a screenshot at the exact viewport. For interaction, record the shortest reproduction. For timing or performance, retain a trace or measured frame result. For accessibility, record the inspected tree or announcement.

Evidence can remain in the report; do not write artifacts into the project unless the user asks.
