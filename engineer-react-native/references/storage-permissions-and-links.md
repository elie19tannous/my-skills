# Storage, permissions, and external entry

The app binary and device are not trusted servers. Minimize sensitive material, use platform protection, and validate every external value.

Hand a full threat model, authentication design, cryptography, or security audit to `secure-software` or `review-security`.

## Classify before storing

| Data | Default location |
| --- | --- |
| Reconstructable cache | Cache/files/database appropriate to size |
| Non-sensitive preference | Async key-value storage |
| Short-lived sensitive value | Memory where practical |
| Session/refresh token or small secret | Platform-backed secure storage |
| Irreplaceable user data | Authoritative service or designed backup/sync |
| Service API secret | Server only; never in app |

AsyncStorage and ordinary files are not secret storage. Environment variables included in the application are not secret either.

## Secure storage limits

Platform-backed secure stores are designed for small values such as credentials and keys, not arbitrary databases.

- Handle read/write failure.
- Define accessibility while the device is locked.
- Decide whether values migrate to a new device.
- Handle biometric enrollment invalidating protected values.
- Remove credentials on sign-out and account removal.
- Do not treat uninstall behavior as a guaranteed wipe or retention contract across both platforms.
- Exclude encrypted entries from backups when restoration would lose the encryption key.

Secure storage protects data at rest; it does not make a compromised session or over-privileged API safe.

## Permission states

Model:

- not determined;
- granted;
- denied but requestable;
- blocked/never ask again;
- limited or approximate;
- unavailable/restricted by device or policy.

Request in context after explaining value. If denied, keep the feature usable where possible and provide a settings path only when the system will no longer show a prompt.

Do not request every permission at startup. Do not repeatedly prompt after denial.

## Data minimization

- Request the least capability and precision needed.
- Keep only the fields and retention period required by the product.
- Remove sensitive values from logs, analytics, crash reports, screenshots, notifications, and clipboard.
- Redact request headers and payloads in network tooling.
- Obscure sensitive views in the app switcher when the product risk warrants it.

## Deep links and intents

Treat route, query, fragment, notification, share, and file values as untrusted.

- Parse with a strict allowlist of routes and parameter shapes.
- Enforce authorization after navigation resolves the target.
- Never place credentials, one-time codes, personal data, or privileged actions in a custom-scheme link.
- Prefer verified universal links and Android App Links for web-associated routes.
- Require confirmation for high-impact actions reached externally.
- Reject unsupported schemes and unexpected hosts.
- Normalize and validate file paths/content URIs before access.

Custom URL schemes can collide with another installed application and are not proof of origin.

## OAuth redirects

Use Authorization Code with PKCE through a maintained platform/browser integration. Validate state and redirect target. Prefer claimed HTTPS links where provider and platform support them.

Do not embed a client secret in the app. A mobile client is public; server-only exchanges and privileged provider credentials stay on a server.

## Network and local trust

- Require HTTPS in production.
- Keep development exceptions out of release configuration.
- Validate server authorization independently of any client UI state.
- Treat certificate pinning as a product-specific control with rotation and outage risk, not a default checkbox.
- Do not trust rooted/jailbroken-device detection as an authorization boundary.

## Primary references

- [React Native security](https://reactnative.dev/docs/security)
- [Expo SecureStore](https://docs.expo.dev/versions/latest/sdk/securestore/)
- [Expo authentication](https://docs.expo.dev/guides/authentication/)
- [OWASP MASVS](https://mas.owasp.org/MASVS/)
