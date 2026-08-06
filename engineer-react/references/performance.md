# React performance

Performance work begins with a user-visible delay and ends with a comparable measurement. Rerender count alone is not the goal.

## Establish the measurement

Record:

- production build and commit;
- device and browser;
- route and data size;
- exact interaction;
- warm or cold cache;
- React Profiler trace and browser performance trace where relevant;
- user-facing metric: input delay, render duration, dropped frames, loading milestone, memory, or bundle bytes.

Do not compare a development before-state with a production after-state.

## Remove work before caching it

Check in order:

1. unnecessary state and Effect-driven extra renders;
2. work repeated inside a large loop;
3. broad context or store subscriptions;
4. components mounted but not visible or needed;
5. request waterfalls and duplicate data work;
6. large client bundles and eager modules;
7. expensive layout, paint, images, and third-party scripts;
8. only then memoization.

The fastest calculation is the one the architecture no longer performs.

## Rerender diagnosis

Use React DevTools Profiler or React's profiling APIs to identify which commit is slow and why the subtree rendered.

- Find the state update that began the commit.
- Check whether context or store selection reaches too far.
- Check unstable object/function props only at confirmed memoized boundaries.
- Check list keys and remounting.
- Check expensive calculation, DOM size, and browser work after commit.

A component rerendering is normal. Optimize when the measured render or resulting browser work harms the target interaction.

## React Compiler

When enabled:

- follow the Rules of React and compiler diagnostics;
- rely on automatic memoization for ordinary update optimization;
- keep existing manual memoization during incremental adoption unless tests and traces support removal;
- use manual memoization where identity is a deliberate contract or the compiler cannot safely infer the boundary;
- pin and upgrade the compiler according to the project's risk and test coverage.

Do not “help” the compiler by adding useMemo and useCallback everywhere. More identity constraints can make code harder to change and can hide ownership problems.

## Context and external stores

- Split providers by update frequency and subscriber need.
- Keep provider values stable when their semantic value is stable.
- Expose selectors for frequently changing stores.
- Place providers as low as the sharing boundary allows.
- Separate state from commands when commands remain stable.

Measure the actual subscribed tree before replacing context with another library.

## Lists

For large collections:

- keep keys stable;
- paginate or stream data when the user does not need everything at once;
- virtualize only when DOM size and render cost are measured problems;
- keep row height and measurement strategy predictable;
- preserve keyboard, screen-reader, find-in-page, and scroll restoration behavior;
- avoid recreating expensive row content for unrelated updates.

Virtualization trades DOM cost for complexity. It is not a default for ordinary lists.

## Scheduling

Use transitions or deferred values for updates that may lag behind direct input without changing correctness. Keep the controlled input update urgent; defer the expensive result view.

Do not use scheduling to hide a blocking synchronous calculation that should be removed, moved, chunked, or performed elsewhere.

## Bundle and loading cost

- Inspect route and component chunks.
- Load heavy editors, charts, and rare dialogs when first needed.
- Keep server-only libraries out of the client graph.
- Avoid importing an entire utility or icon collection for one export.
- Preload only resources with a high probability of near-term use.
- Measure parse and execute time, not only compressed transfer size.

## Completion gate

Report before and after under the same conditions. Keep the optimization only when the target metric improves without correctness, accessibility, or maintainability regression.

## Primary references

- [React Profiler](https://react.dev/reference/react/Profiler)
- [React Developer Tools profiling](https://react.dev/learn/react-developer-tools)
- [React Compiler introduction](https://react.dev/learn/react-compiler/introduction)
- [React performance tracks](https://react.dev/reference/dev-tools/react-performance-tracks)
