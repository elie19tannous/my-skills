# Testing Patterns — Component, Integration & Snapshot

> On-demand module. Loaded when writing unit tests, component tests, or integration tests.
> Contains production test templates — not just framework setup.
> For E2E tests (Detox/Maestro), see testing-strategy.md instead.

---

## Test File Structure

```
RULE: Tests live next to the code they test.
RULE: Test file = [filename].test.ts or [filename].spec.ts

src/features/product/
├── ProductDetailScreen.tsx
├── ProductDetailScreen.test.tsx   ← Component test
├── hooks/
│   ├── useProductDetail.ts
│   └── useProductDetail.test.ts   ← Hook test
├── services/
│   ├── productService.ts
│   └── productService.test.ts     ← Service test
└── types/
    └── product.types.ts            ← No test (types are compile-time)
```

---

## React Native Component Tests (React Testing Library)

### Basic Component Test

```typescript
// components/ProductCard.test.tsx
import { render, screen, fireEvent } from '@testing-library/react-native';
import { ProductCard } from './ProductCard';
import { mockProduct } from '@/test/factories';

describe('ProductCard', () => {
  const onPress = jest.fn();

  beforeEach(() => jest.clearAllMocks());

  it('renders product title and price', () => {
    render(<ProductCard product={mockProduct()} onPress={onPress} />);

    expect(screen.getByText('Test Product')).toBeTruthy();
    expect(screen.getByText('$29.99')).toBeTruthy();
  });

  it('calls onPress when tapped', () => {
    render(<ProductCard product={mockProduct()} onPress={onPress} />);

    fireEvent.press(screen.getByText('Test Product'));
    expect(onPress).toHaveBeenCalledTimes(1);
    expect(onPress).toHaveBeenCalledWith(mockProduct().id);
  });

  it('shows out of stock badge when not in stock', () => {
    render(<ProductCard product={mockProduct({ inStock: false })} onPress={onPress} />);

    expect(screen.getByText('Out of Stock')).toBeTruthy();
  });

  it('does not show badge when in stock', () => {
    render(<ProductCard product={mockProduct({ inStock: true })} onPress={onPress} />);

    expect(screen.queryByText('Out of Stock')).toBeNull();
  });
});
```

### Test with Providers (Navigation, Theme, Query)

```typescript
// test/renderWithProviders.tsx
import { render, RenderOptions } from '@testing-library/react-native';
import { NavigationContainer } from '@react-navigation/native';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ThemeProvider } from '@/theme/ThemeProvider';

function AllProviders({ children }: { children: React.ReactNode }) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false, gcTime: 0 },
      mutations: { retry: false },
    },
  });

  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <NavigationContainer>
          {children}
        </NavigationContainer>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export function renderWithProviders(ui: React.ReactElement, options?: RenderOptions) {
  return render(ui, { wrapper: AllProviders, ...options });
}
```

### Screen Test (4 states)

```typescript
// features/product/ProductDetailScreen.test.tsx
import { renderWithProviders } from '@/test/renderWithProviders';
import { screen, waitFor } from '@testing-library/react-native';
import { ProductDetailScreen } from './ProductDetailScreen';
import { productService } from './services/productService';
import { mockProduct } from '@/test/factories';

jest.mock('./services/productService');
const mockedService = productService as jest.Mocked<typeof productService>;

const route = { params: { productId: 'prod-1' as ProductId } };

describe('ProductDetailScreen', () => {
  it('shows skeleton while loading', () => {
    mockedService.getById.mockReturnValue(new Promise(() => {})); // never resolves
    renderWithProviders(<ProductDetailScreen route={route} />);

    expect(screen.getByTestId('product-skeleton')).toBeTruthy();
  });

  it('shows product data on success', async () => {
    mockedService.getById.mockResolvedValue(mockProduct({ title: 'Blue Shirt' }));
    renderWithProviders(<ProductDetailScreen route={route} />);

    await waitFor(() => {
      expect(screen.getByText('Blue Shirt')).toBeTruthy();
    });
  });

  it('shows error view on failure', async () => {
    mockedService.getById.mockRejectedValue(new Error('Server error'));
    renderWithProviders(<ProductDetailScreen route={route} />);

    await waitFor(() => {
      expect(screen.getByText(/something went wrong/i)).toBeTruthy();
      expect(screen.getByText('Try Again')).toBeTruthy();
    });
  });

  it('retries on error button press', async () => {
    mockedService.getById
      .mockRejectedValueOnce(new Error('fail'))
      .mockResolvedValueOnce(mockProduct({ title: 'Blue Shirt' }));

    renderWithProviders(<ProductDetailScreen route={route} />);

    await waitFor(() => screen.getByText('Try Again'));
    fireEvent.press(screen.getByText('Try Again'));

    await waitFor(() => {
      expect(screen.getByText('Blue Shirt')).toBeTruthy();
    });
  });
});
```

---

## Hook Tests

```typescript
// hooks/useProductDetail.test.ts
import { renderHook, waitFor } from '@testing-library/react-native';
import { useProductDetail } from './useProductDetail';
import { QueryWrapper } from '@/test/renderWithProviders';
import { productService } from '../services/productService';
import { mockProduct } from '@/test/factories';

jest.mock('../services/productService');
const mockedService = productService as jest.Mocked<typeof productService>;

describe('useProductDetail', () => {
  it('fetches product by ID', async () => {
    const product = mockProduct();
    mockedService.getById.mockResolvedValue(product);

    const { result } = renderHook(
      () => useProductDetail('prod-1' as ProductId),
      { wrapper: QueryWrapper }
    );

    expect(result.current.isLoading).toBe(true);

    await waitFor(() => {
      expect(result.current.isLoading).toBe(false);
      expect(result.current.product).toEqual(product);
    });
  });

  it('returns error on failure', async () => {
    mockedService.getById.mockRejectedValue(new Error('Not found'));

    const { result } = renderHook(
      () => useProductDetail('bad-id' as ProductId),
      { wrapper: QueryWrapper }
    );

    await waitFor(() => {
      expect(result.current.error).toBeTruthy();
    });
  });
});
```

---

## Test Factories (Mock Data Generators)

```typescript
// test/factories.ts
import { Product, User, Review, ProductId, UserId } from '@/types/api.types';

let counter = 0;

export function mockProduct(overrides?: Partial<Product>): Product {
  counter++;
  return {
    id: `prod-${counter}` as ProductId,
    title: 'Test Product',
    description: 'A great product for testing',
    price: 29.99,
    images: ['https://example.com/img1.jpg'],
    category: 'electronics',
    inStock: true,
    ...overrides,
  };
}

export function mockUser(overrides?: Partial<User>): User {
  counter++;
  return {
    id: `user-${counter}` as UserId,
    email: `user${counter}@example.com`,
    name: 'Test User',
    avatarUrl: null,
    role: 'user',
    createdAt: new Date().toISOString(),
    ...overrides,
  };
}

export function mockReview(overrides?: Partial<Review>): Review {
  counter++;
  return {
    id: `review-${counter}`,
    userId: `user-${counter}` as UserId,
    rating: 4,
    comment: 'Great product!',
    createdAt: new Date().toISOString(),
    ...overrides,
  };
}

// Factory for lists
export function mockProductList(count = 5, overrides?: Partial<Product>): Product[] {
  return Array.from({ length: count }, () => mockProduct(overrides));
}
```

---

## Flutter Widget Tests

```dart
// widgets/product_card_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:your_app/widgets/product_card.dart';
import '../test_helpers.dart';

void main() {
  group('ProductCard', () {
    testWidgets('renders title and price', (tester) async {
      await tester.pumpWidget(wrapWithMaterial(
        ProductCard(
          product: mockProduct(title: 'Blue Shirt', price: 29.99),
          onTap: () {},
        ),
      ));

      expect(find.text('Blue Shirt'), findsOneWidget);
      expect(find.text('\$29.99'), findsOneWidget);
    });

    testWidgets('calls onTap when pressed', (tester) async {
      var tapped = false;
      await tester.pumpWidget(wrapWithMaterial(
        ProductCard(
          product: mockProduct(),
          onTap: () => tapped = true,
        ),
      ));

      await tester.tap(find.byType(ProductCard));
      expect(tapped, isTrue);
    });

    testWidgets('shows out of stock badge', (tester) async {
      await tester.pumpWidget(wrapWithMaterial(
        ProductCard(
          product: mockProduct(inStock: false),
          onTap: () {},
        ),
      ));

      expect(find.text('Out of Stock'), findsOneWidget);
    });
  });
}

// test_helpers.dart
Widget wrapWithMaterial(Widget child) {
  return MaterialApp(home: Scaffold(body: child));
}
```

---

## Service Tests (API Mocking)

```typescript
// services/productService.test.ts
import api from '@/services/api';
import { productService } from './productService';
import { mockProduct } from '@/test/factories';

jest.mock('@/services/api');
const mockedApi = api as jest.Mocked<typeof api>;

describe('productService', () => {
  it('getById calls correct endpoint', async () => {
    const product = mockProduct();
    mockedApi.get.mockResolvedValue({ data: product });

    const result = await productService.getById('prod-1' as ProductId);

    expect(mockedApi.get).toHaveBeenCalledWith('/products/prod-1');
    expect(result).toEqual(product);
  });

  it('getProducts passes pagination params', async () => {
    mockedApi.get.mockResolvedValue({ data: { items: [], nextCursor: null } });

    await productService.getProducts({ cursor: 'abc', limit: 20, category: 'shoes' });

    expect(mockedApi.get).toHaveBeenCalledWith('/products', {
      params: { cursor: 'abc', limit: 20, category: 'shoes' },
    });
  });
});
```

---

## Snapshot Testing Strategy

```
WHEN to use snapshots:
  ✅ Static components (Header, Footer, Badge, Tag)
  ✅ Design system components (Button, Card, Input variants)
  ✅ Error/empty states (they rarely change)

WHEN NOT to use snapshots:
  ⛔ Dynamic content (lists with variable data)
  ⛔ Screens with complex state (too many snapshot variants)
  ⛔ Components that change frequently (breaks snapshot every PR)

HANDLING DYNAMIC DATA:
  - Use consistent mock data (factories with fixed counter)
  - Mock Date.now() for timestamps
  - Mock Math.random() for IDs

REVIEWING SNAPSHOT CHANGES:
  - Every snapshot update in PR → reviewer MUST check diff
  - If snapshot changes are "too noisy" → switch to specific assertions
```

```typescript
// components/Badge.test.tsx
import { render } from '@testing-library/react-native';
import { Badge } from './Badge';

describe('Badge', () => {
  it('renders success variant correctly', () => {
    const tree = render(<Badge variant="success" text="Active" />);
    expect(tree.toJSON()).toMatchSnapshot();
  });

  it('renders error variant correctly', () => {
    const tree = render(<Badge variant="error" text="Failed" />);
    expect(tree.toJSON()).toMatchSnapshot();
  });
});
```

---

## Testing Checklist

```
FOR EVERY COMPONENT:
  □ Renders correctly (default state)
  □ Loading state
  □ Error state
  □ Empty state
  □ User interactions (press, type, scroll)
  □ Accessibility labels present

FOR EVERY HOOK:
  □ Returns expected data
  □ Handles loading
  □ Handles errors
  □ Cleanup on unmount

FOR EVERY SERVICE:
  □ Calls correct endpoint
  □ Passes correct params
  □ Handles success response
  □ Handles error response
```
