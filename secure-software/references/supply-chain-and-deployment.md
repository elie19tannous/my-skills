# Supply chain and deployment

A secure code change can be undone by an untrusted dependency, over-privileged build, mutable artifact, or unsafe production default.

## Dependency decision

Before adding a package, inspect:

- necessity and smaller existing alternatives;
- source repository and published registry identity;
- maintainers, ownership changes, release cadence, and issue health;
- license;
- direct and transitive dependency surface;
- install/build scripts and native code;
- runtime permissions and network/file access;
- supported versions and architecture;
- known advisories and maintenance response;
- bundle/binary and operational cost.

Prefer a narrow dependency whose behavior can be isolated. Do not install an abandoned library for a small convenience.

## Lock and verify

- Commit the correct lockfile.
- Use frozen/immutable install in CI.
- Review lockfile changes with manifest changes.
- Fetch from approved registries over authenticated transport.
- Use checksums/signatures/provenance supported by the ecosystem.
- Prevent dependency confusion through scoped/private registry configuration.
- Remove unused dependencies and stale overrides.

A lockfile pins what was resolved; it does not prove the package is trustworthy.

## Advisory remediation

1. Confirm the vulnerable package and reachable feature in the shipped artifact.
2. Identify fixed versions and compatibility impact.
3. Prefer the smallest supported upgrade.
4. Use an override only as a time-bounded bridge with tests and owner.
5. Run focused and release checks.
6. Record residual exposure when no fix exists.
7. Remove obsolete exceptions.

Do not silence or blanket-ignore advisories without reachability and ownership evidence.

## Build identity and CI

- Separate read, test, publish, sign, and deploy capabilities.
- Use short-lived federated identity where supported.
- Restrict secrets from untrusted fork/PR jobs.
- Pin third-party CI actions/plugins by immutable reference according to platform practice.
- Review script changes that run during install/build/release.
- Keep protected branches/environments and required review for production.
- Prevent artifact replacement after approval.
- Record builder, source commit, dependency state, and artifact digest.

Treat generated code and build logs as possible secret-exposure paths.

## Artifacts and releases

- Build once and promote the same immutable artifact between environments where architecture permits.
- Sign artifacts through protected identities.
- Verify signatures/digests before deploy or update.
- Keep mobile signing keys and OTA channels tightly scoped.
- Produce SBOM/provenance when required.
- Retain rollback artifacts and verify rollback compatibility.
- Keep database migrations backward-compatible with rolling deploy/rollback strategy.

## Production configuration

Disable or restrict:

- debug and profiling endpoints;
- verbose stack traces;
- default/sample credentials;
- unused ports, services, methods, routes, and admin panels;
- directory listing and public object-store access;
- permissive CORS and wildcard trusted origins;
- development transport exceptions;
- unsafe feature flags.

Validate configuration at startup and fail safely when a required secret or security setting is absent. Do not fall back to a weak default.

## Web edge controls

Centralize and test controls appropriate to the application:

- HTTPS and HSTS deployment policy;
- secure session cookies;
- content type and sniffing controls;
- framing policy;
- referrer policy;
- CSP built from actual resource needs;
- CORS allowlist and credential behavior;
- cache policy for private responses;
- upload/request/response limits.

Security headers supplement safe application behavior; they do not replace output encoding or authorization.

## Infrastructure and data access

- Separate environments and accounts/projects.
- Restrict network paths and service identities.
- Keep databases/object stores private by default.
- Scope backups and snapshots with the same sensitivity as primary data.
- Encrypt transport and storage according to threat model.
- Patch base images and runtimes.
- Minimize container image contents and runtime privileges.
- Monitor configuration drift.

## Primary references

- [NIST Secure Software Development Framework](https://csrc.nist.gov/projects/ssdf)
- [OWASP Top 10:2025 — Software Supply Chain Failures](https://owasp.org/Top10/2025/A03_2025-Software_Supply_Chain_Failures/)
- [SLSA supply-chain levels](https://slsa.dev/spec/v1.2/)
- [CISA Secure by Design](https://www.cisa.gov/securebydesign)
