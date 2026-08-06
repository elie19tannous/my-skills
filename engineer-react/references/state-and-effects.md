# State and Effects

State records information that changes over time and affects rendering. Effects synchronize with systems outside React. Keep those jobs separate.

## State decision table

| Question | Use |
| --- | --- |
| Can it be computed from current props/state/context? | Compute during render |
| Is it part of the route or shareable URL? | Router/search state |
| Is it remote data with cache and invalidation needs? | Framework/data layer |
| Must a change trigger rendering? | State or external store |
| Must it persist without rendering? | Ref |
| Does only one event need it? | Local variable inside the event |

Avoid mirrored state. If `fullName` comes from `firstName` and `lastName`, render `fullName`; do not store and synchronize it.

## Keep state minimal and normalized

- Store an identifier, not both the selected object and its identifier.
- Store source data, not filtered and sorted copies.
- Use one status model rather than several booleans that can contradict each other.
- Keep mutually exclusive states mutually exclusive with a union or reducer.
- Preserve domain invariants inside the update that changes them.

Replace `isLoading`, `isError`, `isSuccess`, and `isEmpty` booleans that can all be true with a state machine or query result that defines valid transitions.

## Event or Effect?

Use an event when logic is caused by a specific interaction:

- submit a form;
- add an item;
- send a request caused by pressing Save;
- show a confirmation after that request;
- update related state atomically.

Use an Effect when logic must remain synchronized because a component is rendered:

- connect to a room identified by props;
- subscribe to an external store;
- control an imperative map or media player;
- observe size, visibility, network state, or browser APIs;
- report a view impression tied to presence.

If the logic answers “what did the user just do?”, it likely belongs in the event.

## Effect contract

Before writing an Effect, complete:

```text
External system:
Setup:
Cleanup:
Reactive values:
Stale work strategy:
Strict Mode setup → cleanup → setup result:
```

If `External system` is blank, do not add the Effect.

## Dependencies describe the code

Include every reactive value read by setup or cleanup. Do not choose dependencies to control timing.

When a dependency changes too often:

1. move event-specific logic to the event;
2. move object or function creation inside the Effect when it belongs there;
3. lift stable configuration outside the component;
4. use a supported non-reactive Effect event API only when the installed React version and project conventions support it;
5. change the ownership model.

Do not suppress the exhaustive-dependencies rule as an optimization.

## Cleanup must mirror setup

- Subscribe → unsubscribe from the same source.
- Add listener → remove the same listener.
- Start timer → clear that timer.
- Open connection → close that connection.
- Begin request → abort or ignore stale completion.
- Apply an imperative state → restore or retarget it.

The user should not be able to tell whether development ran setup once or setup, cleanup, then setup again.

## Avoid Effect chains

Do not build workflows as a chain of Effects that each set state for the next. They add extra renders, create intermediate invalid states, and make the initiating event impossible to see.

Perform one transition inside the event or model a reducer/state machine when the workflow has several valid events.

## Reset and adjust state deliberately

- For a new domain identity, key the owning subtree or place state under the identity owner.
- For a value that can be calculated from new props, calculate it.
- For a user selection that may become invalid, store its ID and derive the selected item; define the fallback explicitly.
- Adjust state during render only in the rare documented pattern where it is unavoidable and guarded; prefer ownership changes first.

## Refs

Use refs for DOM handles, instance handles, timers, previous external values, and mutable data that must not schedule a render.

Do not read or write refs during render except for stable initialization patterns allowed by React. A ref is not an escape hatch from state consistency.

## Primary references

- [Rules of React](https://react.dev/reference/rules)
- [You might not need an Effect](https://react.dev/learn/you-might-not-need-an-effect)
- [Lifecycle of reactive Effects](https://react.dev/learn/lifecycle-of-reactive-effects)
- [`useEffect`](https://react.dev/reference/react/useEffect)
- [Choosing the state structure](https://react.dev/learn/choosing-the-state-structure)
