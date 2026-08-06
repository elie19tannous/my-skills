# Threat modeling

Threat modeling turns architecture into security requirements before vulnerabilities become implementation details.

## Scope the model

Name:

- feature, service, route, mobile capability, or release in scope;
- business owner and technical owner;
- deployment environments;
- assets and data classifications;
- identities, roles, tenants, and machine principals;
- external dependencies;
- explicit exclusions;
- assumptions that would change the result.

Keep the model small enough to update. Use a high-level system diagram plus focused submodels for complex or high-risk flows.

## Model the system

Capture:

| Element | Examples |
| --- | --- |
| External actor | Customer, administrator, partner, attacker, scheduled service |
| Process | Browser app, API, worker, identity provider, mobile app |
| Data store | Database, object store, device storage, queue, log platform |
| Data flow | HTTPS request, webhook, queue message, file import, deep link |
| Trust boundary | Internet edge, tenant boundary, user/admin plane, CI/runtime, device/server |
| Control | Authentication, authorization, validation, encryption, rate limit, audit |

Mark sensitive data on both flows and stores. Mark privileged operations and places where data changes interpretation.

## Ask business-logic questions

Technical controls do not catch a valid sequence that abuses the product model. Ask:

- Can steps occur out of order, be skipped, replayed, or performed twice?
- Can two actors race on the same object?
- Can one account act through several devices or sessions at once?
- What valuable output does the feature create: money, credits, access, reputation, messages, compute, or data export?
- Which limits exist only in the UI?
- Can an actor approve their own request or change the object after approval?
- Can cancellation, refund, invitation, recovery, or transfer be repeated?
- What happens when a dependency partially succeeds?

Model the legitimate workflow first, then violate one assumption at a time.

## Use threat prompts

STRIDE is a useful pass:

| Prompt | Ask |
| --- | --- |
| Spoofing | Can an actor or service impersonate another? |
| Tampering | Can data, configuration, code, or messages change without detection? |
| Repudiation | Can a consequential action occur without reliable attribution? |
| Information disclosure | Can data cross to an unauthorized actor, tenant, log, or client? |
| Denial of service | Can scarce state, compute, queue, lock, or dependency be exhausted? |
| Elevation of privilege | Can a lower-trust actor gain a protected capability? |

Add privacy, fraud, safety, abuse, supply-chain, and availability prompts appropriate to the product. A completed STRIDE table is not proof of completeness.

## Write threats as scenarios

Use:

```text
Actor with preconditions
performs action against boundary or assumption
causing impact to asset/user
because current control is absent or insufficient.
```

Avoid category-only statements such as “risk of injection.” Name the interpreter, input path, and impact.

## Rank without false precision

Use ordinal likelihood and impact supported by context:

- exposure and attacker access;
- prerequisite difficulty;
- existing controls;
- exploit repeatability and automation;
- affected users/tenants/data;
- reversibility and detectability;
- financial, privacy, safety, legal, and availability effect.

Record uncertainty. Do not multiply invented numbers into a scientific-looking score.

## Choose a response

For every accepted threat, choose:

- **Eliminate** — remove the capability, data, or trust crossing.
- **Mitigate** — reduce likelihood or impact with a testable control.
- **Transfer** — move responsibility contractually or architecturally, while documenting retained obligations.
- **Accept** — name owner, rationale, expiry/review date, and monitoring.

Security debt without an owner and review date is accidental acceptance.

## Maintain the model

Update when:

- a trust boundary or data class changes;
- a new actor, tenant model, integration, file type, or privileged action appears;
- authentication or authorization changes;
- deployment, build, mobile update, or secret ownership changes;
- an incident disproves an assumption.

Keep model, requirements, tests, and risk decisions linked.

## Primary references

- [OWASP Threat Modeling Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html)
- [OWASP Business Logic Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Business_Logic_Security_Cheat_Sheet.html)
- [OWASP ASVS 5.0.0](https://owasp.org/www-project-application-security-verification-standard/)
