# Data, secrets, and cryptography

The safest sensitive data is data the product never collects. Minimize first, protect what remains, and define deletion before storage.

## Classify data

For each field or dataset, record:

- purpose and lawful/product need;
- sensitivity and affected person/tenant;
- source and destinations;
- storage locations and copies;
- retention and deletion trigger;
- access roles and service identities;
- logging, analytics, support, backup, and export exposure;
- encryption and key owner;
- breach impact.

Do not classify an entire database as one level when tables/fields differ materially.

## Minimize and separate

- Collect only data needed for a named feature.
- Keep sensitive fields out of general-purpose event payloads.
- Separate identifiers from content where it reduces exposure.
- Return only fields required by the current client and principal.
- Use short retention for transient verification, upload, and processing data.
- Delete from primary, derived cache, search, analytics, and backup policy according to requirements.

Redaction after broad collection is weaker than never collecting.

## Secrets

Secrets include service credentials, signing keys, database credentials, webhook secrets, encryption keys, and privileged API tokens.

- Store in an approved secret manager.
- Inject at runtime or protected build step.
- Scope to workload, environment, and purpose.
- Prefer short-lived workload identity.
- Prevent inheritance into subprocesses or client builds unnecessarily.
- Redact from logs, errors, traces, support exports, and process listings.
- Detect accidental repository/CI exposure.
- Rotate after exposure and remove the leaked value from active history/artifacts; deleting the latest file is not rotation.

Public mobile/web configuration is not a secret even when stored in `.env`.

## Encryption decision

Encryption protects a specific threat, not “data” in the abstract. State:

- attacker and access being mitigated;
- data and lifecycle protected;
- where plaintext must exist;
- algorithm/mode from approved platform library;
- key generation, storage, access, rotation, backup, and destruction;
- authenticated metadata and context binding;
- migration and failure behavior.

Use authenticated encryption. Never reuse a nonce where the selected algorithm requires uniqueness. Never use encryption without integrity when tampering matters.

Do not invent crypto or manually compose primitives when a reviewed high-level API exists.

## Passwords and one-way secrets

Passwords require an adaptive password hashing function with unique salts and centrally managed parameters. API tokens and recovery codes may be stored as one-way verifiers when the service only needs equality validation.

- Generate tokens with a cryptographically secure random generator.
- Use enough entropy for online/offline threat model.
- Compare through maintained constant-time APIs where secret comparison is exposed.
- Bind tokens to purpose, subject, expiry, and single-use state.
- Revoke and rotate explicitly.

## Keys

- Separate keys by environment, tenant or data domain where blast radius warrants it, and by purpose.
- Use KMS/HSM/platform keystore when available.
- Limit decrypt/sign permission, not only key read permission.
- Log key use metadata without plaintext.
- Rotate with versioned ciphertext/signatures and overlap.
- Test restore, old-version read, failed decrypt, and revoked-key behavior.
- Protect backups and replicas with equivalent controls.

## Mobile data

- Keep service secrets on a server.
- Use platform-backed secure storage for small credentials.
- Keep non-sensitive cache/preferences in ordinary storage.
- Remove sensitive data from persisted application state, notifications, clipboard, screenshots, and crash payloads.
- Consider device backup and migration behavior.
- Treat root/jailbreak detection as a signal, not a trusted enforcement boundary.
- Re-authorize privileged actions on the server.

## Logging and telemetry redaction

Default to structured allowlisted fields. Redact before data reaches the logging transport.

Do not log:

- passwords, MFA/recovery codes, session IDs, authorization headers;
- cryptographic keys or full tokens;
- full payment card or government identifiers;
- sensitive request/response bodies;
- secrets embedded in URLs;
- unnecessary personal content.

Use stable correlation IDs that do not expose the protected identifier. Restrict log access and retention.

## Primary references

- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [OWASP Cryptographic Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html)
- [OWASP MASVS storage and crypto controls](https://mas.owasp.org/MASVS/)
