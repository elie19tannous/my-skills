# React testing

Test what the user can observe and what the system must preserve. Keep implementation free to change.

## Choose the narrowest credible level

| Level | Owns |
| --- | --- |
| Pure unit | Parsing, formatting, reducers, domain decisions |
| Component | Rendered states and interaction within one component boundary |
| Feature integration | Route/data/form/component behavior working together |
| Browser end-to-end | Critical user path, navigation, browser APIs, real network contract |

Do not force a browser test to prove a pure function, or a shallow unit test to prove routing and focus.

## User-centered queries

Prefer queries in this order when available:

1. role and accessible name;
2. label text;
3. visible text;
4. semantic state;
5. test ID only when the user has no perceivable handle.

This makes inaccessible or ambiguous controls harder to test—which is useful pressure on the implementation.

## Arrange realistic states

Test:

- initial and successful content;
- empty result;
- validation failure;
- request failure and retry;
- slow pending state;
- repeated activation;
- stale or out-of-order completion when inputs change;
- permission or authentication boundary where relevant.

Use fixtures that resemble production data shape and size. Avoid enormous mock objects that obscure the behavior under test.

## Interact like a user

Use the testing tool's high-level user interaction APIs rather than calling props or event handlers directly. Type, tab, click, press keys, and submit forms.

Await observable UI changes. Do not sleep for arbitrary time. Keep fake timers limited to code whose contract is genuinely time-based.

## Assert outcomes

Assert:

- visible state and accessible state;
- navigation and URL;
- persisted mutation or network request at the boundary;
- focus movement and restoration;
- error and status announcement;
- retained draft or rollback;
- absence only after the interface has reached the expected state.

Avoid asserting component state, Hook call counts, private helper order, CSS class internals, or child component existence when those are not the product contract.

## Strict Mode and cleanup

Run development tests in the project's Strict Mode configuration. A subscription, timer, or request test should tolerate setup, cleanup, and setup again.

After each test:

- restore mocked globals;
- clear pending timers and requests;
- unmount rendered roots;
- fail on unexpected console errors according to project convention.

Leaks between tests are architecture feedback, not merely test flakiness.

## Accessibility

Include automated accessibility rules where the project supports them, then manually or end-to-end test custom keyboard behavior, focus, and announcements.

For dialogs, test accessible name, initial focus, focus containment, Escape, and focus restoration. For forms, test labels, described errors, first-error focus, and busy state.

## Server and hydration tests

When server rendering is involved:

- render the route or component through the real framework boundary where possible;
- assert stable server output for deterministic inputs;
- hydrate and fail on mismatch warnings;
- test client interaction after hydration;
- keep server-only modules out of the client test graph.

## Bug workflow

1. Reproduce with the smallest user-observable test that fails for the right reason.
2. Confirm the failure without the proposed fix.
3. Implement the smallest correction.
4. Run the focused test.
5. Run adjacent and project-required checks.
6. Keep the test named after behavior, not the old implementation.

## Primary references

- [Testing Library guiding principles](https://testing-library.com/docs/guiding-principles)
- [React `act`](https://react.dev/reference/react/act)
- [React Strict Mode](https://react.dev/reference/react/StrictMode)
