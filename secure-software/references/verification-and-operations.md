# Verification and operations

Security verification proves a requirement against an abuse path. Operations keep that proof meaningful after release.

## Build a requirement ledger

| Requirement | Threat | Enforcement point | Test | Operational signal | Owner |
| --- | --- | --- | --- | --- | --- |

Use versioned external requirement IDs when citing a standard, such as `v5.0.0-<ASVS requirement>`, then add the product-specific behavior. External standards do not know the application's tenant, workflow, or data model.

## Test layers

Choose checks based on the control:

| Layer | Best for |
| --- | --- |
| Unit/property | Parsers, policy functions, state machines, limits |
| Integration | Authentication/session, authorization against data, webhook verification, storage adapters |
| End-to-end | Complete abuse path across route, UI/API, and persistence |
| Static analysis | Dangerous sinks, insecure APIs, dataflow patterns |
| Dependency/SBOM | Known component exposure and inventory |
| Secret scan | Accidental committed or built credentials |
| Configuration/IaC scan | Unsafe deployment defaults and drift |
| Dynamic scan | Runtime exposure within explicit test scope |
| Manual review/test | Business logic, chaining, authorization, design assumptions |

Automated scans produce candidates, not confirmed findings. Vet reachability and context.

## Negative test set

Adapt relevant cases:

- no authentication;
- expired/revoked/rotated session;
- wrong user, role, tenant, object, or workflow state;
- missing, null, wrong type, unknown field, duplicate field;
- boundary lengths and one over the boundary;
- oversized count, depth, payload, file, archive, and response;
- alternate encodings/canonical forms;
- replay, duplicate submission, and out-of-order completion;
- partial dependency failure and timeout;
- unsafe redirect or outbound destination;
- forged, old, or repeated webhook;
- log and error redaction;
- rollback/recovery.

Assert both denial and non-disclosure. A `403` with another tenant's object details is still a leak.

## Authorization matrix

Generate tests from subject × action × resource × tenant × state. Keep allowed cases explicit and deny all unspecified combinations.

For bulk/list/export paths, assert every returned object is authorized; do not assume the individual-read policy automatically applies.

## Scanner safety

Before running a security tool, confirm:

- target and environment are authorized;
- test intensity and mutation behavior;
- credentials and data used;
- rate and availability impact;
- output storage sensitivity;
- network permission;
- project-approved command/config.

Use passive/static checks by default. Do not aim intrusive scanning, fuzzing, credential attacks, or exploit payloads at production without explicit authorization and safeguards.

## Logging verification

Trigger success and denial. Confirm:

- expected security event exists;
- actor, action, result, time, and correlation are usable;
- high-value object is identifiable without sensitive content;
- credentials/tokens/personal content are absent;
- repeated attacker input cannot forge log structure;
- alert threshold is actionable;
- log access and retention are appropriate.

## Detection and incident readiness

For high-impact controls, define:

- alert condition and threshold;
- triage owner and runbook;
- containment action: revoke session/key, disable route/feature, block actor, roll back artifact;
- evidence retained;
- user/customer communication owner;
- recovery and post-incident validation.

A control with no detection may fail silently. A noisy alert nobody owns is not detection.

## Vulnerability remediation

1. Preserve a safe reproduction and affected versions.
2. Identify root cause and sibling paths.
3. Contain active exposure where necessary.
4. Rotate credentials or invalidate sessions if exposure is possible.
5. Implement the smallest class-level fix.
6. Add the abuse-case regression.
7. Re-run focused and broader verification.
8. Deploy in dependency order and monitor.
9. Record residual risk and incident/disclosure actions.

Do not publish exploit details or rotate shared production secrets without the user's authority and operational plan.

## Evidence report

Use:

| Check | Scope | Result | Evidence/gap |
| --- | --- | --- | --- |
| Cross-tenant authorization test | Invoice read/update | Pass | Denied same-tenant wrong owner and wrong tenant |
| Dependency scan | Production lockfile | Not verified | Approved scanner unavailable |

Only `Pass`, `Fail`, and `Not verified`. A scanner with findings is not a failed product until candidates are vetted; record both raw tool result and confirmed status.

## Residual risk

For anything not eliminated:

- scenario and asset;
- remaining likelihood/impact;
- existing controls;
- decision and owner;
- monitoring;
- expiry or review trigger;
- required future work.

Never bury accepted risk in prose such as “probably fine.”

## Primary references

- [OWASP ASVS 5.0.0](https://owasp.org/www-project-application-security-verification-standard/)
- [OWASP Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- [OWASP MASVS](https://mas.owasp.org/MASVS/)
- [NIST SSDF](https://csrc.nist.gov/projects/ssdf)
