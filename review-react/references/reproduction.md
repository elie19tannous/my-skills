# Reproduction discipline

A review finding is strongest when another engineer can produce the same failure from a short event sequence.

## Build the sequence

Record:

```text
Precondition:
Initial route/state/data:
Action 1:
Action 2:
Scheduling condition, if any:
Expected:
Actual:
Persisted or visible impact:
```

Use domain values, not abstract A/B, when the data helps explain identity.

## State and key failures

For wrong identity, use the smallest mutation that distinguishes domain identity from render position:

1. Render two rows with different drafts or local state.
2. Insert, delete, filter, or reorder before them.
3. Observe which row retains the state.

For unintended reset:

1. Enter local work.
2. Trigger the parent change.
3. Identify the key or element-type change that remounts the subtree.

For unintended preservation, switch domain identity without changing element identity and observe old state under new data.

## Async races

Use controlled promises or network throttling:

1. Start request A.
2. Change the input and start request B.
3. Resolve B successfully.
4. Resolve A afterward.
5. Check visible and cached identity.

For optimistic operations, start two changes and complete them in both orders, including one failure. Verify rollback affects only its own operation.

For duplicate mutations, activate twice before the first response and inspect server or mock call count and resulting persisted records.

## Effect lifecycle

Exercise setup, cleanup, setup:

- Strict Mode development remount;
- dependency change;
- conditional removal;
- route navigation;
- rapid open/close;
- test unmount.

Count external subscriptions, listeners, timers, connections, or requests—not Effect function calls. Confirm the external system ends with exactly one live setup or none after removal.

## Hydration

1. Run the production server-rendered build.
2. Capture server HTML for stable inputs.
3. Load with console collection active.
4. Compare first-client inputs: locale, time zone, theme, storage, random values, IDs, auth, and feature flags.
5. Interact after hydration to detect replaced nodes or lost handlers.

Do not reproduce hydration through a client-only dev route.

## Performance

Keep before and after conditions identical:

- production build;
- browser/device;
- route and dataset;
- cache state;
- interaction script;
- profiler settings.

Capture the user-visible metric first. Use React's commit data to locate React work and browser traces to locate scripting, style, layout, paint, network, and third-party cost.

## Minimal test conversion

When practical, turn the sequence into a failing test at the narrowest credible level:

- reducer or pure transition → unit;
- component state/interaction → component test;
- route, cache, form, or focus → feature integration;
- hydration, browser API, or full navigation → browser test.

The test must fail before the fix for the same user-observable reason described by the finding.

## When runtime is unavailable

Source can still prove a defect when the execution follows directly—for example a Hook after a conditional return or a secret imported into an explicit client module. For timing, layout, browser, or performance claims, mark the reproduction `Not verified` and either omit the finding or state only the narrower source-proven risk.
