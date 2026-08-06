# Server and client boundaries

Keep privileged work and initial data close to the server. Keep interaction and browser APIs in the smallest client region that needs them.

## Determine the renderer first

Identify whether the project uses:

- client-only rendering;
- SSR with hydration;
- static generation;
- streaming SSR;
- server components;
- server actions or functions;
- edge and node runtimes with different APIs.

Use the framework's exact conventions and version. React primitives do not define the route, cache, or deployment contract on their own.

## Deterministic initial render

Server output and the client's first render must agree. Watch for:

- `Date.now()`, `new Date()`, randomness, generated IDs, and locale differences;
- branching on `window`, storage, media queries, or browser extensions during render;
- data that changes between server render and hydration;
- invalid HTML nesting corrected differently by the browser;
- external scripts mutating the DOM;
- client-only authentication state replacing server assumptions.

Use stable server-provided values, React's ID APIs where appropriate, CSS for presentation differences, and an explicit post-hydration state only when the UI truly depends on the browser.

Do not use hydration-warning suppression until the mismatch is intentional, tightly scoped, and documented.

## Keep client islands small

A client boundary pulls its imports and descendants into the client graph according to framework rules.

- Put interactive state at the leaf that needs it.
- Pass serializable data or children from server composition.
- Keep server data access out of generic client modules.
- Avoid clientifying a layout for one toggle.
- Inspect bundle output after moving a boundary.

Do not pass functions, class instances, database objects, or other non-serializable values across a boundary unless the framework provides a specific transport contract.

## Secrets and authorization

- Keep service credentials, private environment variables, and privileged SDKs in server-only modules.
- Treat every client input as attacker-controlled, including hidden fields and serialized action arguments.
- Re-authenticate and authorize on the server action or endpoint.
- Return only the data the current principal may see.
- Prevent server-only modules from accidental client import with framework guards where available.

Hiding a value from rendered markup does not make it secret if it ships in the client bundle or serialized payload.

## Streaming and reveal order

Choose boundaries from product dependency:

- reveal independent regions separately;
- keep a label and the data required to interpret it together;
- keep navigation and page identity stable;
- avoid a cascade of tiny fallbacks;
- ensure streamed updates preserve heading, focus, and announcement behavior.

Streaming changes arrival order, not authorization or data ownership.

## Server actions and mutations

Where the framework supports server actions/functions:

- validate serialized input;
- authorize inside the action;
- make repeat execution safe where possible;
- handle stale forms and conflicts;
- return structured field and form errors;
- invalidate or update affected data intentionally;
- avoid leaking stack traces and internal identifiers.

Progressive enhancement matters for critical forms: preserve native form behavior when the framework supports it.

## Browser-only state

Use browser state—storage, viewport, connection, permission, device APIs—only after the client owns the component. Define the initial server-visible state so hydration remains stable.

For preference rendering such as theme, prefer framework-supported early initialization that avoids both mismatch and visible flash. Do not scatter `mounted` gates through the component tree.

## Debugging hydration

1. Capture the exact warning and component stack.
2. Compare server HTML with the first client render inputs.
3. Disable extensions or external DOM mutation.
4. Replace time, random, locale, or browser branches with stable inputs.
5. Check HTML validity.
6. Reproduce in a production build.
7. Add a regression test at the closest level that can detect the mismatch.

## Primary references

- [React DOM server APIs](https://react.dev/reference/react-dom/server)
- [`hydrateRoot`](https://react.dev/reference/react-dom/client/hydrateRoot)
- [Server Components](https://react.dev/reference/rsc/server-components)
- [Server Functions](https://react.dev/reference/rsc/server-functions)
