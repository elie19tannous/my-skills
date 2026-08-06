# React review catalog

Use this catalog to investigate changed behavior, not as a demand to mention every category.

## Render purity and Hooks

Look for:

- I/O, analytics, subscriptions, timers, DOM writes, or state writes during render;
- nondeterministic render values that change without input;
- mutation of props, state, context, Hook arguments, or values already passed to JSX;
- Hooks under conditions, loops, nested callbacks, or after a possible return;
- component functions invoked like ordinary functions;
- cleanup required only because setup is happening in render.

Evidence: exact render path and the repeated/concurrent render sequence that exposes it.

Do not flag pure calculation during render merely because it is nontrivial; measure it under performance only when cost matters.

## State structure and identity

Look for:

- state that duplicates props, cache, URL, or another state value;
- invalid boolean combinations;
- state lifted beyond its coordination boundary;
- index or generated keys on a changing list;
- unintended reset or preservation after identity change;
- stale state used for a compound update;
- a controlled input switching to uncontrolled or back.

Evidence: shortest sequence of insert, reorder, prop change, navigation, or update that attaches state to the wrong identity or renders an invalid state.

Do not flag an index key for a fixed, never-reordered decorative list with no row state.

## Effects

Look for:

- derived values written through an Effect;
- event-caused work delayed into an Effect;
- missing or suppressed dependencies;
- object/function dependencies recreated without reason;
- setup with no mirrored cleanup;
- cleanup that targets a different instance;
- request completion after inputs changed;
- a chain of Effects that encodes a workflow;
- state update in an Effect that causes an avoidable extra render or loop.

Evidence: name the external system. If none exists, show how render or the initiating event can own the logic.

Do not demand an Effect be removed when it correctly synchronizes an imperative or subscribed system.

## Async data and mutations

Look for:

- fetch-in-Effect bypassing a framework data boundary and causing waterfalls or duplicate requests;
- cache key missing identity inputs;
- older response overwriting current input;
- duplicate mutation under repeated activation;
- optimistic rollback clobbering a later success;
- success that leaves other visible caches stale;
- request failure that erases safe prior data or draft input;
- retry of a non-idempotent operation;
- loading and empty states conflated.

Evidence: request/event ordering with current and expected persisted state.

Do not flag a simple client-only request because a larger data library could exist; identify a real ownership, race, caching, or UX failure.

## Server, client, and hydration

Look for:

- server and first-client output differing through time, random, locale, storage, or browser branches;
- secret or privileged SDK crossing the client graph;
- authorization trusted from a hidden field or client state;
- non-serializable boundary props;
- broad client boundary introduced for one leaf interaction;
- streamed region revealing content without the context required to interpret it;
- suppression hiding a non-intentional hydration mismatch;
- invalid HTML nesting corrected by the browser.

Evidence: framework boundary, serialized output, bundle path, or captured hydration warning.

Do not flag a client boundary merely for existing. State the leaked capability, measured cost, or correctness defect.

## Component contracts

Look for:

- boolean combinations that admit an impossible mode;
- wrapper losing a ref or native prop;
- navigation implemented as a button or action as a fake link/div;
- composed handler overriding consumer cancellation or vice versa;
- default behavior that is unsafe or surprising;
- reused primitive importing feature state;
- context provider forcing unrelated high-frequency consumers to update;
- callback error/timing contract varying across callers.

Evidence: inspect representative call sites and show the invalid combination or lost native behavior.

Do not require an abstraction for one local component with no stable repeated contract.

## Performance

Look for only demonstrated cost:

- unbounded synchronous work in render or input handlers;
- broad subscription causing an expensive subtree commit;
- repeated request/subscription from unstable Effect inputs;
- unstable key causing remount and lost work;
- large dependency pulled into a common client chunk;
- non-virtualized collection with measured DOM/render failure;
- manual memoization creating stale behavior or complex identity contracts;
- compiler diagnostics ignored.

Evidence: trace, profiler, bundle report, dataset threshold, or obvious complexity on a proven hot path.

Do not report ordinary rerenders, inline functions, or unmemoized values without cost at a boundary that could skip work.

## Testing

Report a testing issue only when it leaves a changed failure path unprotected or the test passes while behavior is broken.

Look for:

- assertion on implementation instead of observable outcome that misses the regression;
- async test completing before the result;
- arbitrary sleep hiding race or flakiness;
- mock that removes the behavior under test;
- bug fix with no reproduction despite a practical test boundary;
- hydration, failure, or stale-request path changed but only success covered;
- snapshot updated across unrelated behavior without inspection.

Evidence: show how current test passes under the failing implementation or fails to exercise the changed branch.

Do not report “missing tests” generically.

## Accessibility and semantics

Keep ownership narrow: report React implementation that breaks the product's accessible contract, then hand visual/accessibility design detail to `review-interface`.

Look for lost native semantics, inaccessible name/state, focus not restored after conditional rendering, dynamic update not announced, or keyboard handler removed by a wrapper.

Evidence: rendered accessibility tree or concrete DOM/interaction path when runtime determines behavior.
