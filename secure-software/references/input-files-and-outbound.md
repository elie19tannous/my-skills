# Input, files, and outbound boundaries

Validation establishes domain shape. Encoding protects an interpreter. They solve different problems and both may be required.

## Validate at the receiving boundary

Validate:

- schema and required fields;
- primitive type and canonical representation;
- length, numeric range, count, nesting depth, and total size;
- finite-domain allowlists;
- relationships and business invariants;
- authorization-sensitive identifiers after loading the resource;
- duplicate and replay behavior.

Normalize once where safe, then validate the normalized form. Keep raw signed payload bytes when signature verification requires exact content.

Reject unknown fields for sensitive commands or explicitly select writable fields. This prevents mass assignment and silent future behavior.

## Keep code and data separate

- Use parameterized database queries.
- Use argument arrays or maintained APIs for operating-system commands; avoid shell construction.
- Use safe template bindings rather than concatenating executable template/code.
- Avoid dynamic `eval`, function creation, or unsafe deserialization.
- Select table, column, sort direction, template, or algorithm from an allowlist when it cannot be a bound parameter.

Escaping for one interpreter does not protect another.

## Encode for the output context

Choose encoding for the exact sink:

- HTML text;
- HTML attribute;
- URL component;
- JavaScript string/code;
- CSS value;
- CSV/spreadsheet cell;
- log line;
- shell or query API.

Prefer framework auto-escaping and safe DOM APIs. Audit intentional raw HTML and sanitize rich content with a maintained library and minimal allowlist.

Do not “sanitize” all input globally. Stored data may later enter different contexts that require different encoding.

## File upload

For uploads:

- authenticate and authorize the operation;
- cap request, file, count, and decompressed size;
- determine type from validated content plus permitted extension, not client MIME alone;
- generate server-side storage names;
- keep untrusted files outside executable/web roots;
- remove path components and reject traversal;
- scan or transform according to risk;
- serve with safe content type/disposition and separate origin when appropriate;
- prevent public guessing with authorization or unguessable references plus access checks;
- define retention and deletion.

Image transcoding and document parsing reduce some risk but introduce parser risk. Keep processors patched, sandboxed, and resource-bounded.

## Archives and structured documents

- Reject absolute paths and `..` after canonicalization.
- Bound entry count, nested archive depth, expansion ratio, dimensions, and processing time.
- Extract into an isolated temporary directory.
- Do not follow symlinks outside the destination.
- Validate each extracted file again.
- Clean up on success and failure.

Treat XML entities, YAML tags, object deserialization, and template features as executable capabilities; disable anything not required.

## Outbound requests and SSRF

When user-controlled data influences a server request:

- prefer an allowlist of hosts/services and fixed scheme;
- parse with a standard URL parser;
- reject credentials, fragments, unsupported ports/schemes, and ambiguous forms;
- resolve and enforce address policy, including redirects and DNS changes;
- block loopback, link-local, private, metadata, and internal ranges unless explicitly required;
- set tight connect/read/total timeouts and response-size limits;
- do not forward inbound credentials or sensitive headers;
- isolate outbound network capability where architecture permits.

Validate every redirect target, not only the initial URL.

## Redirects

Prefer relative internal destinations or named destination IDs. If external redirects are required, allowlist origins and display the destination when user trust matters.

Never accept arbitrary post-login redirects that can send credentials or users to attacker-controlled sites.

## Webhooks

- Verify provider signature using the raw canonical payload and maintained library/spec.
- Select the secret by trusted endpoint/account configuration, not an untrusted payload field.
- Enforce timestamp tolerance and replay protection.
- Use constant-time comparison through the cryptographic library.
- Acknowledge within provider timeout and process idempotently.
- Authorize the event's account/tenant mapping.
- Log event ID, type, result, and correlation without full sensitive payload.

An IP allowlist may supplement signature verification; it rarely replaces it.

## Rate and resource limits

Bound attacker-controlled work at the cheapest boundary:

- request bytes and fields;
- parser depth and complexity;
- login/recovery attempts;
- expensive search/export/report operations;
- queue depth and retry count;
- concurrent jobs per principal/tenant;
- response size and pagination.

Rate limits need a product-aware key and recovery behavior; a single global IP limit can harm shared networks and is easy to distribute around.

## Primary references

- [OWASP Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)
- [OWASP File Upload Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html)
- [OWASP SSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)
- [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
