# Project and native boundaries

Choose the smallest native surface that satisfies the capability. Every native dependency adds build, upgrade, platform, and release obligations.

## Identify the workflow

| Workflow | Characteristics |
| --- | --- |
| Managed | Native projects generated or managed through app config and supported modules |
| Prebuild/CNG | Native projects generated from config and plugins, with controlled regeneration |
| Bare | Native projects owned directly and edited as first-class source |

Do not infer workflow from an `ios/` or `android/` directory alone. Inspect scripts, documentation, config plugins, and whether native directories are generated or committed.

Preserve the current workflow unless the requested capability cannot fit it.

## Version map

Record together:

- React Native;
- React;
- Expo SDK and CLI where present;
- iOS deployment target and Xcode toolchain;
- Android min/target/compile SDK and Gradle/AGP/Kotlin toolchain;
- Hermes and New Architecture status;
- navigation, gesture, animation, and native dependency versions.

Use the installed version's documentation. A native API that exists in current docs may not exist in the project's version.

## Dependency gate

Before adding or upgrading a native package, answer:

1. Does the installed React Native/Expo version support it?
2. Does it support the project's architecture and renderer?
3. Does it require a development build, prebuild, pod install, Gradle change, entitlement, or config plugin?
4. Are both platforms maintained and tested?
5. Does it change app size, startup, permissions, privacy declarations, or store review?
6. Does it work in the intended update model, or require a new binary?
7. Is the license acceptable?
8. Can an existing dependency or platform API own the capability?

Prefer a maintained library with a narrow, documented native contract over a hand-rolled bridge for ordinary capabilities.

## New Architecture

Treat New Architecture support as a compatibility fact, not a marketing claim. Verify the exact installed package and build.

- Run the project's architecture-specific diagnostics.
- Build both platforms from clean native artifacts when changing integration code.
- Test codegen inputs and generated outputs through the normal build; do not edit generated files.
- Keep legacy fallback only when the supported version matrix requires it.
- Measure behavior; architecture migration does not automatically fix product-level performance.

## Native module boundary

Expose domain operations rather than leaking platform implementation throughout JavaScript:

```ts
type BiometricResult =
  | { status: "verified" }
  | { status: "unavailable"; reason: string }
  | { status: "cancelled" }
  | { status: "failed"; reason: string };
```

The adapter owns platform error mapping, capability checks, and lifecycle cleanup. Product components render domain states.

For high-frequency native calls:

- avoid serializing large payloads repeatedly;
- batch work where semantics allow;
- keep per-frame work off the JS/native boundary;
- expose cancellation;
- define thread requirements;
- profile on target hardware.

## Platform files or conditions

Use `.ios`/`.android` files when structure, capability, or lifecycle materially differs. Use a small `Platform.select` or conditional when only one property or token changes.

Avoid duplicating an entire feature to change spacing. Avoid one tangled file full of platform branches when two implementations genuinely differ.

## Configuration ownership

Classify each setting:

- build-time public configuration;
- runtime public endpoint or feature flag;
- native entitlement/manifest declaration;
- server secret;
- signing credential.

Anything included in a mobile binary is recoverable by an attacker. Public build configuration may vary by environment; it must not grant privileged access.

Keep entitlements, usage descriptions, URL schemes, associated domains, and Android intent filters aligned across app config and native projects. Generated workflows require config plugins or app config as the source of truth.

## Generated files

Do not hand-edit:

- generated codegen output;
- build intermediates;
- pods or dependency source;
- prebuild output when repository conventions regenerate it;
- bundled JavaScript output.

Change the source schema, plugin, config, or package and regenerate through the documented command.

## Primary references

- [React Native architecture overview](https://reactnative.dev/architecture/overview)
- [React Native native platform development](https://reactnative.dev/docs/native-platform)
- [Expo development builds](https://docs.expo.dev/develop/development-builds/introduction/)
- [Expo continuous native generation](https://docs.expo.dev/workflow/continuous-native-generation/)
