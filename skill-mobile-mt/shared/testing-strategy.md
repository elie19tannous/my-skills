# Mobile Testing Strategy — Unit + E2E

> Test the right things at the right layer. Don't test implementation details.

---

## Testing Pyramid

```
        ╱ E2E ╲          ← Detox / Maestro / XCUITest / Espresso
       ╱───────╲         ← Few, slow, high-confidence
      ╱Integration╲      ← API mocking, navigation flows
     ╱─────────────╲     ← Medium count
    ╱   Unit Tests   ╲   ← Jest / XCTest / JUnit
   ╱─────────────────╲   ← Many, fast, cheap

RULE: Most tests = unit. E2E = critical flows only (login, checkout, onboarding).
```

---

## Unit Tests (Jest — React Native / TypeScript)

```typescript
// Test hooks, not components
describe('useCart', () => {
  it('adds item and updates total', () => {
    const { result } = renderHook(() => useCart(), { wrapper: ReduxProvider })
    act(() => { result.current.addItem(mockProduct) })
    expect(result.current.total).toBe(mockProduct.price)
  })

  it('handles addToCart API error with rollback', async () => {
    server.use(rest.post('/cart', (req, res, ctx) => res(ctx.status(500))))
    const { result } = renderHook(() => useCart(), { wrapper: ReduxProvider })
    await act(async () => { await result.current.addItem(mockProduct) })
    expect(result.current.items).toHaveLength(0) // rolled back
    expect(result.current.error).toBeTruthy()
  })
})

// Test Redux slices directly
describe('cartSlice', () => {
  it('sets loading state on fetchCart.pending', () => {
    const state = cartReducer(initialState, fetchCart.pending('', undefined))
    expect(state.status).toBe('loading')
  })
})
```

**Rules:**
- Test business logic (hooks, services, slices) — NOT component layout
- Mock API calls with `msw` (Mock Service Worker)
- 4 states per feature: loading / success / error / empty

---

## E2E Testing — Detox (React Native)

> Best for: React Native apps, full native bridge testing.

### Setup

```bash
# Install
npm install --save-dev detox @config/detox

# iOS build (required before tests)
detox build --configuration ios.sim.debug

# Run tests
detox test --configuration ios.sim.debug
detox test --configuration android.emu.debug
```

### Config (`detox.config.js`)

```js
module.exports = {
  testRunner: {
    args: { '$0': 'jest', config: 'e2e/jest.config.js' },
    jest: { setupTimeout: 120000 }
  },
  apps: {
    'ios.debug': { type: 'ios.app', binaryPath: 'ios/build/Build/Products/Debug-iphonesimulator/MyApp.app', build: 'xcodebuild -workspace ios/MyApp.xcworkspace -scheme MyApp -configuration Debug -sdk iphonesimulator -derivedDataPath ios/build' },
    'android.debug': { type: 'android.apk', binaryPath: 'android/app/build/outputs/apk/debug/app-debug.apk', build: 'cd android && ./gradlew assembleDebug assembleAndroidTest -DtestBuildType=debug' }
  },
  devices: {
    simulator: { type: 'ios.simulator', device: { type: 'iPhone 15' } },
    emulator: { type: 'android.emulator', device: { avdName: 'Pixel_7_API_34' } }
  },
  configurations: {
    'ios.sim.debug': { device: 'simulator', app: 'ios.debug' },
    'android.emu.debug': { device: 'emulator', app: 'android.debug' }
  }
}
```

### Write Detox Tests

```typescript
// e2e/login.test.ts
describe('Login Flow', () => {
  beforeAll(async () => {
    await device.launchApp({ newInstance: true })
  })

  beforeEach(async () => {
    await device.reloadReactNative()
  })

  it('shows error on wrong password', async () => {
    await element(by.id('email-input')).typeText('user@test.com')
    await element(by.id('password-input')).typeText('wrongpass')
    await element(by.id('login-button')).tap()
    await expect(element(by.text('Invalid credentials'))).toBeVisible()
  })

  it('navigates to home on success', async () => {
    await element(by.id('email-input')).typeText('user@test.com')
    await element(by.id('password-input')).typeText('correctpass')
    await element(by.id('login-button')).tap()
    await expect(element(by.id('home-screen'))).toBeVisible()
  })
})
```

**testID rules:**
```typescript
// Add testID to interactive elements
<TextInput testID="email-input" ... />
<TouchableOpacity testID="login-button" ... />
<View testID="home-screen" ... />
```

**What to test with Detox:**
- Login / logout flow
- Onboarding (first-time user)
- Critical purchase / checkout path
- Push notification tap → navigation
- Deep link handling

**What NOT to test with Detox:** minor UI variations, loading spinners, animations.

---

## E2E Testing — Maestro (Cross-Platform)

> Best for: Simpler setup, works on React Native + Flutter + native iOS/Android.

### Setup

```bash
# macOS
brew tap mobile-dev-inc/tap
brew install maestro

# Run a flow
maestro test e2e/login.yaml
maestro test e2e/           # all flows in folder
```

### Write Maestro Flows (YAML)

```yaml
# e2e/login.yaml
appId: com.myapp
---
- launchApp:
    clearState: true

- assertVisible: "Sign In"

- tapOn:
    id: "email-input"
- inputText: "user@test.com"

- tapOn:
    id: "password-input"
- inputText: "wrongpass"

- tapOn:
    id: "login-button"

- assertVisible: "Invalid credentials"
```

```yaml
# e2e/checkout.yaml
appId: com.myapp
---
- launchApp
- tapOn: "Products"
- tapOn:
    index: 0   # first product
- tapOn: "Add to Cart"
- tapOn: "Checkout"
- assertVisible: "Order Confirmed"
```

### Maestro Cloud CI

```bash
# Run on real devices in Maestro Cloud
maestro cloud --apiKey $MAESTRO_API_KEY e2e/
```

**Maestro vs Detox:**

| | Maestro | Detox |
|--|---------|-------|
| Setup | Minutes | Hours |
| YAML / Code | YAML | TypeScript |
| Cross-platform | ✅ RN + Flutter + native | RN only |
| Speed | Slower | Faster |
| Power | Medium | High |
| CI integration | Maestro Cloud | Self-hosted |

**Use Maestro when:** simple flows, cross-platform team, quick setup.
**Use Detox when:** complex interactions, React Native only, full control.

---

## Flutter Testing

### Unit + Widget Tests

```dart
// Unit test — business logic
test('CartBloc adds item correctly', () {
  final bloc = CartBloc(cartRepository: MockCartRepository());
  bloc.add(AddToCart(product: mockProduct));
  expectLater(bloc.stream, emits(CartLoaded(items: [mockProduct])));
});

// Widget test — UI
testWidgets('ProductCard shows title and price', (tester) async {
  await tester.pumpWidget(MaterialApp(
    home: ProductCard(product: mockProduct),
  ));
  expect(find.text(mockProduct.title), findsOneWidget);
  expect(find.text('\$${mockProduct.price}'), findsOneWidget);
});
```

### Integration Test (Flutter Driver replacement)

```dart
// integration_test/login_test.dart
void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('login flow', (tester) async {
    app.main();
    await tester.pumpAndSettle();

    await tester.enterText(find.byKey(Key('email')), 'user@test.com');
    await tester.enterText(find.byKey(Key('password')), 'pass123');
    await tester.tap(find.byKey(Key('login-button')));
    await tester.pumpAndSettle();

    expect(find.byKey(Key('home-screen')), findsOneWidget);
  });
}
```

```bash
# Run on simulator
flutter test integration_test/

# Run on real device
flutter test integration_test/ -d <device-id>
```

---

## iOS — XCUITest

```swift
func testLoginFlow() throws {
    let app = XCUIApplication()
    app.launch()

    let emailField = app.textFields["email-input"]
    emailField.tap()
    emailField.typeText("user@test.com")

    let passwordField = app.secureTextFields["password-input"]
    passwordField.tap()
    passwordField.typeText("pass123")

    app.buttons["login-button"].tap()

    XCTAssertTrue(app.otherElements["home-screen"].waitForExistence(timeout: 5))
}
```

---

## Android — Espresso

```kotlin
@Test
fun testLoginFlow() {
    onView(withId(R.id.emailInput))
        .perform(typeText("user@test.com"), closeSoftKeyboard())
    onView(withId(R.id.passwordInput))
        .perform(typeText("pass123"), closeSoftKeyboard())
    onView(withId(R.id.loginButton)).perform(click())
    onView(withId(R.id.homeScreen)).check(matches(isDisplayed()))
}
```

---

## Anti-Patterns

```
❌ Testing implementation details (internal state, private methods)
❌ Testing every UI pixel (visual regression belongs in Storybook/Percy)
❌ E2E for every edge case (unit test those)
❌ Skipping testID on interactive elements
❌ Running Detox without a stable test build
❌ Using sleep() instead of waitFor()

✅ Test user flows, not code internals
✅ E2E for critical paths: login, purchase, onboarding
✅ Unit test all business logic (hooks, slices, services)
✅ Mock API calls in unit tests
✅ Add testID to every tappable + input element
✅ waitFor() over sleep() in Detox
```
