# Release Checklist — Before Shipping

> Complete ALL items before submitting to App Store / Play Store.

---

## Code Quality

- [ ] No `console.log` / `print` / `NSLog` in production
- [ ] No hardcoded secrets or API keys
- [ ] No force unwraps without safety (`!` / `!!` / `as!`)
- [ ] No empty catch blocks
- [ ] No files > 500 lines
- [ ] All TODO/FIXME resolved or tracked

## Security

- [ ] Tokens stored in SecureStore / Keychain / EncryptedSharedPreferences
- [ ] Deep links validated before navigation
- [ ] No sensitive data in logs
- [ ] SSL pinning enabled (if required)
- [ ] ProGuard / R8 enabled for Android release
- [ ] Debug mode stripped from release build

## Performance

- [ ] Lists use FlatList / ListView.builder / LazyColumn (not ScrollView)
- [ ] Images optimized (resized, cached, lazy loaded)
- [ ] No main thread blocking
- [ ] No memory leaks (useEffect cleanup, dispose, [weak self])
- [ ] App launch time < 3 seconds
- [ ] Smooth scrolling (60fps)

## UI / UX

- [ ] All states handled: loading, success, error, empty
- [ ] Touch targets >= 44pt (iOS) / 48dp (Android)
- [ ] Safe area / notch handled
- [ ] Keyboard dismissal handled
- [ ] Back button works (Android)
- [ ] Accessibility labels on interactive elements
- [ ] Dark mode works (if supported)

## Platform-Specific

### iOS
- [ ] Correct deployment target set
- [ ] App icons all sizes provided
- [ ] Privacy usage descriptions in Info.plist
- [ ] `pod install` runs clean
- [ ] Tested on physical device

### Android
- [ ] `minSdk` / `targetSdk` correct
- [ ] Signing config for release
- [ ] Permissions declared in AndroidManifest.xml
- [ ] Tested on physical device
- [ ] 64-bit support included

### React Native / Flutter
- [ ] Both iOS + Android tested
- [ ] Native modules compile on both platforms
- [ ] Bundle size acceptable
- [ ] Hermes enabled (RN) / tree-shaking (Flutter)

## Testing

- [ ] Critical paths tested manually
- [ ] Edge cases: offline, slow network, empty data, expired token
- [ ] Fresh install tested (no cached data)
- [ ] Upgrade from previous version tested (if applicable)
- [ ] Crash reporting SDK integrated (Sentry / Firebase Crashlytics)

## Final

- [ ] Version number bumped
- [ ] Changelog updated
- [ ] Screenshots / store listing updated (if UI changed)

---

> Ship when ALL boxes are checked. Not before.
