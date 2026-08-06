# Async data and errors

Async work has identity, lifetime, ownership, and failure. Model all four.

## Prefer the framework's data path

Before adding a request in a component, inspect the router and data layer. Prefer the existing mechanism that owns:

- server rendering and preloading;
- deduplication and caching;
- invalidation after mutations;
- request cancellation;
- route-level loading and error UI;
- streaming and Suspense integration;
- authentication and server-only access.

Fetch-in-Effect is appropriate for a client-only external system or a small application with no data layer, but it must still handle stale responses, cleanup, caching expectations, and waterfalls.

## Give every request identity

Request identity includes every input that changes the resource: user, route params, filters, locale, authorization scope, pagination cursor, and version.

Do not cache data from different identities under the same key. Do not include presentation-only values that do not change the resource.

## Query states

Render distinct states:

| State | Behavior |
| --- | --- |
| First load | Show a stable page shell and meaningful pending state |
| Success with data | Render the current resource |
| Success empty | Explain the empty condition and next action |
| Background refresh | Keep valid data visible and mark updating quietly |
| Recoverable failure | Keep safe prior data or input, explain, and retry |
| Unauthorized/forbidden | Use the product's auth or permission recovery path |
| Not found | Render resource-specific absence, not a generic crash |

Distinguish no data from failed data.

## Prevent stale completion

When inputs change before work completes:

- abort the previous request when supported;
- otherwise ignore completion whose request identity is no longer current;
- never let an older response overwrite a newer result;
- clean up subscriptions and streams;
- test rapid changes and navigation away.

An `isMounted` flag hides symptoms and does not cancel network or subscription work. Prefer lifecycle-aware ownership and request identity.

## Mutations

For every mutation, define:

- payload and authorization boundary;
- duplicate-submission behavior;
- idempotency expectation;
- pending UI;
- success reconciliation;
- cache invalidation or direct cache update;
- validation and request failures;
- retry and rollback;
- navigation after success.

Disable repeat activation only while it prevents an unsafe duplicate; keep the action label visible with its busy state.

## Optimistic updates

Use optimism when success is common and rollback is honest.

1. Snapshot the affected cache or state.
2. Apply the optimistic change with a temporary identity where needed.
3. Reconcile with the authoritative server response.
4. Roll back only the affected change on failure.
5. Explain failure and preserve a retry.
6. Handle two optimistic operations completing out of order.

Do not use optimism for irreversible, permission-sensitive, high-value, or conflict-heavy actions unless the product explicitly accepts the risk.

## Suspense

Use Suspense only with a framework or data source designed for it. Place boundaries around regions that can reveal independently without creating a waterfall of spinners.

- Keep stable navigation and page identity outside a frequently suspending boundary.
- Coordinate related content under one boundary when partial reveal would mislead.
- Use a transition for non-urgent navigation or filtering when keeping prior content visible is better than replacing it.
- Pair every suspending failure domain with a recoverable error boundary.

Do not wrap arbitrary promises or invent a cache protocol in product code when the framework already owns the contract.

## Error boundaries

An error boundary handles unexpected rendering or data-read failures in its subtree. It does not replace validation, rejected event promises, or server authorization checks.

Place boundaries at recovery units:

- route;
- independently reloadable dashboard region;
- plugin or third-party surface;
- editor whose draft can remain safe outside the failed preview.

Fallback UI states what failed, preserves unaffected navigation, and offers a real retry or escape. Log diagnostics without exposing them to the user.

## Primary references

- [Suspense](https://react.dev/reference/react/Suspense)
- [`useTransition`](https://react.dev/reference/react/useTransition)
- [React error boundaries](https://react.dev/reference/react/Component#catching-rendering-errors-with-an-error-boundary)
- [React `cache`](https://react.dev/reference/react/cache)
