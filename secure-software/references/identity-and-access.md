# Identity and access

Authentication establishes a principal. Session management carries that identity. Authorization decides each action. Keep all three explicit.

## Prefer an established identity system

Use a maintained identity provider or framework integration for password storage, MFA, OAuth/OIDC, recovery, session rotation, and revocation. Configure it to product risk rather than rebuilding protocols.

Verify issuer, audience, signature, time claims, nonce/state, redirect URI, and intended token type according to the protocol and library. Do not parse a token and treat its claims as trusted without cryptographic and contextual validation.

## Account enrollment and recovery

- Verify control of an email/phone before relying on it.
- Keep recovery no weaker than normal sign-in.
- Make recovery tokens random, single-use, short-lived, and bound to purpose/account.
- Invalidate or rotate relevant sessions after password or recovery changes when risk requires it.
- Notify users of sensitive account changes through an independent channel where appropriate.
- Avoid account-existence disclosure in public recovery and login responses unless explicitly accepted.
- Rate-limit and monitor abuse without allowing trivial account lockout denial of service.

Do not use knowledge questions as a primary recovery factor.

## Passwords and MFA

Follow the identity system and current organizational policy. Store password verifiers only through an approved adaptive password-hashing library/service; never reversible encryption or a fast general-purpose hash.

- Accept paste and password managers.
- Do not impose composition rules that reduce usability without evidence.
- Check compromised/common passwords where policy supports it.
- Store recovery codes as sensitive credentials and show them once.
- Provide phishing-resistant MFA for high-risk users/actions when feasible.
- Protect factor enrollment and removal with recent authentication and notification.

## Browser sessions

For cookie sessions:

- use `Secure`, `HttpOnly`, and an appropriate `SameSite` policy;
- scope domain and path narrowly;
- generate opaque, unpredictable identifiers;
- rotate after authentication and privilege changes;
- define absolute and idle expiration;
- revoke on sign-out and security events;
- protect state-changing requests against CSRF according to architecture;
- do not place session identifiers in URLs.

The session token temporarily carries the strength of the authentication. Protect it accordingly.

## Public mobile clients

- Use Authorization Code with PKCE through the system browser or an approved secure authentication session.
- Treat the app as a public client; it cannot keep a client secret.
- Prefer verified universal/app links for callbacks when supported.
- Store small tokens in platform-backed secure storage, not ordinary async storage.
- Handle biometric cancellation and invalidation.
- Keep server authorization independent of device integrity claims.

## Authorization decision

Authorize from:

```text
principal + action + resource + tenant + current resource state + policy context
```

- Load the target resource inside the trusted boundary.
- Derive tenant/owner from that resource, not client input.
- Check capability on every read and write path.
- Return only authorized fields.
- Use consistent non-disclosing absence responses when enumeration matters.
- Keep authorization rules centralized enough to test, but close enough to data/action that they cannot be skipped.

## Multi-tenancy

- Bind tenant scope to authenticated membership.
- Include tenant in every repository/query boundary or enforce it through a stronger database policy.
- Test cross-tenant IDs, search, export, background jobs, caches, object storage, and logs.
- Separate tenant-admin from platform-admin capability.
- Prevent cache keys and object paths from colliding across tenants.
- Treat tenant switching as an identity/context change: clear or re-scope cached data.

## Administrative and service access

- Use separate admin surfaces/identities where risk justifies it.
- Require stronger authentication for powerful roles.
- Make support impersonation explicit, time-bound, visible, and audited.
- Scope service accounts to one workload and purpose.
- Prefer short-lived workload identity over long-lived static keys.
- Require dual control or approval for the highest-impact operations where product risk warrants it.

## Authorization tests

For every protected object/action, cover:

- unauthenticated;
- correct user/tenant/role;
- wrong user in same tenant;
- correct role in wrong tenant;
- lower role;
- stale/revoked membership;
- direct object ID;
- list/search/export/batch path;
- background job or webhook path;
- writable-field overposting;
- state transition not allowed from current state.

## Primary references

- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [OWASP Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
- [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
- [OAuth 2.0 for native apps, RFC 8252](https://www.rfc-editor.org/rfc/rfc8252)
