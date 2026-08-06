# Component architecture

Use components to make ownership and valid variation obvious. A component boundary should reduce the number of facts a reader must hold at once.

## Choose boundaries from responsibility

Split when at least one is true:

- a region owns state or an external interaction;
- a region repeats with the same behavioral contract;
- a region changes for a different reason from its parent;
- a region has a meaningful test boundary;
- a region crosses a server/client or package boundary;
- a region's API can prevent invalid combinations.

Do not split solely because a file is long. Do not keep unrelated orchestration together solely because it appears on one screen.

## Keep ownership local

Start state at the lowest component that can make every required decision. Lift it to the nearest common coordinator only when siblings must agree.

Avoid global state for:

- one dialog's open state;
- a single form draft;
- values that are already in the URL;
- server resources already owned by a query cache;
- deterministic derived values.

Global reach is a cost: more subscribers, more invalidation, weaker locality, and harder reuse.

## Prefer semantic composition

Model meaningful slots and variants:

```tsx
<Dialog>
  <Dialog.Title>Archive project?</Dialog.Title>
  <Dialog.Body>Archived projects can be restored.</Dialog.Body>
  <Dialog.Actions>
    <Button variant="quiet">Cancel</Button>
    <Button variant="danger">Archive project</Button>
  </Dialog.Actions>
</Dialog>
```

Avoid one component with unrelated switches:

```tsx
<Dialog compact centerTitle noClose danger footerTop stickyBody />
```

When prop combinations represent distinct modes, use a discriminated union so each mode requires only its valid data.

## Design props around intent

- Prefer `onSubmit`, `onDismiss`, and `selection` to paint-level callbacks and flags.
- Keep controlled and uncontrolled modes explicit; do not drift between them after mount.
- Preserve native props, refs, and event behavior in primitives.
- Compose user and internal event handlers without swallowing cancellation.
- Do not expose internal state merely to make a test easier.
- Keep default behavior useful and safe.

Boolean props scale poorly when more than one can be true. Replace them with a mode, variant, child composition, or separate component when combinations become ambiguous.

## Use keys as identity

Keys tell React whether an element is the same object across renders.

- Use a stable domain identifier for lists.
- Do not use an array index when items can insert, delete, sort, filter, or reorder.
- Use a key intentionally to reset a subtree when its domain identity changes.
- Do not generate keys during render.
- Do not include volatile presentation values in identity.

State attached to the wrong key is a data bug, not merely a rendering quirk.

## Extract Hooks for reusable behavior

Extract a Hook when behavior—not markup—repeats or when an external-system contract deserves isolation.

A good Hook:

- has one clear responsibility;
- names inputs and outputs by domain meaning;
- follows top-level Hook rules;
- does not hide uncontrolled global effects;
- exposes status and failure when callers must render them;
- cleans up subscriptions, observers, timers, and in-flight work;
- remains testable through a component or a narrow Hook harness.

Do not extract a Hook solely to move code out of sight. If its API returns a bag of unrelated values and setters, the ownership boundary is still unresolved.

## Context is dependency injection, not a store by default

Use context for values that are stable, broadly required, and naturally scoped by a provider: theme, locale, authenticated principal, form coordinator, or a feature service.

For frequently changing data:

- split stable commands from changing state;
- split contexts by subscriber needs;
- move state closer to consumers;
- use an external store with selectors only when the project already needs that model.

One large provider value causes every consumer to pay for unrelated changes.

## Keep modules honest

- Export the smallest public surface.
- Keep route-only components beside the route until reuse is real.
- Keep reusable primitives free of feature data dependencies.
- Avoid barrel files that create cycles or pull client code into server modules.
- Keep package boundaries aligned with runtime and ownership boundaries.

## Smells

| Smell | Likely correction |
| --- | --- |
| Parent passes the same prop through many indifferent layers | Composition or appropriately scoped context |
| Component accepts many unrelated booleans | Semantic variants or separate modes |
| Hook returns state for several independent workflows | Split ownership |
| List rows retain the wrong draft after reorder | Stable identity key |
| Primitive prevents native form or link behavior | Forward native props and semantics |
| Shared component imports feature-specific data | Invert dependency through props or composition |

## Primary references

- [Thinking in React](https://react.dev/learn/thinking-in-react)
- [Sharing state between components](https://react.dev/learn/sharing-state-between-components)
- [Passing data deeply with context](https://react.dev/learn/passing-data-deeply-with-context)
- [Preserving and resetting state](https://react.dev/learn/preserving-and-resetting-state)
