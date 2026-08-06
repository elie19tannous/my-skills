# Spec-to-Code — From Requirements to Implementation

> On-demand module. Loaded when building new features from specs, user stories, or vague descriptions.
> Bridges the gap between "what to build" and "how to implement it".

---

## Spec → Code Pipeline

```
STEP 1: PARSE SPEC (extract structured requirements)
STEP 2: DEPENDENCY GRAPH (map what depends on what)
STEP 3: FILE PLAN (which files to create/modify)
STEP 4: TYPE DEFINITIONS (interfaces + branded types)
STEP 5: IMPLEMENT (bottom-up: types → services → hooks → screens)
STEP 6: VERIFY (against original spec checklist)
```

---

## Step 1: Parse Spec → Structured Requirements

Given ANY feature description, extract these 8 items:

```
┌─────────────────────────────────────────┐
│ 1. ENTITY       What data objects?      │
│ 2. FIELDS       What properties each?   │
│ 3. ACTIONS      What can user do?       │
│ 4. STATES       Loading/error/empty/ok  │
│ 5. NAVIGATION   From where? To where?   │
│ 6. API          Which endpoints?        │
│ 7. STORAGE      Persist anything local? │
│ 8. VALIDATION   Input rules?            │
└─────────────────────────────────────────┘
```

---

## Step 2: Dependency Graph Template

```
[FeatureName]Screen
├── Components
│   ├── [Name]Header
│   ├── [Name]List / [Name]Card
│   ├── [Name]Form (if editable)
│   └── [Name]Empty / [Name]Error / [Name]Skeleton
│
├── Hook: use[FeatureName]
│   ├── Query: use[Entity]Query (GET data)
│   ├── Mutation: use[Action]Mutation (POST/PUT/DELETE)
│   └── State: use[Store]Store (local state)
│
├── Service: [entity]Service.ts
│   ├── get[Entity](params) → API call
│   ├── create[Entity](data) → API call
│   ├── update[Entity](id, data) → API call
│   └── delete[Entity](id) → API call
│
├── Types: [entity].types.ts
│   ├── [Entity] interface
│   ├── Create[Entity]Input
│   ├── Update[Entity]Input
│   └── [Entity]Params (filters, pagination)
│
└── Navigation: registered in navigator
```

---

## Step 3: File Plan — What Goes Where

```
RULE: Follow existing project structure. NEVER invent new patterns.
RULE: Scan project for a SIMILAR feature. Clone its file structure.

TYPICAL FILE PLAN:

  src/features/[feature]/
  ├── [Feature]Screen.tsx          ← Screen component (4 states)
  ├── components/
  │   ├── [Feature]Header.tsx      ← Header with title + actions
  │   ├── [Feature]List.tsx        ← List/grid of items
  │   ├── [Feature]Card.tsx        ← Single item card
  │   ├── [Feature]Form.tsx        ← Form (if editable)
  │   ├── [Feature]Skeleton.tsx    ← Loading skeleton
  │   └── [Feature]Empty.tsx       ← Empty state
  ├── hooks/
  │   └── use[Feature].ts          ← Business logic hook
  ├── services/
  │   └── [feature]Service.ts      ← API calls
  └── types/
      └── [feature].types.ts       ← TypeScript interfaces

  ALSO UPDATE:
  ├── navigation/                  ← Register new screen
  └── stores/ (if new store)       ← Only if feature needs global state
```

---

## Step 4: Type-First Development

```
ALWAYS write types BEFORE implementation.

ORDER:
  1. Entity types (what data looks like)
  2. Input types (what user submits)
  3. API response types (what server returns)
  4. Screen param types (navigation params)

WHY: Types catch integration errors before runtime.
     Types serve as documentation for the feature.
     Types make code review faster (reviewer reads types first).
```

---

## Step 5: Implementation Order (Bottom-Up)

```
WRONG ORDER (causes integration bugs):
  Screen → Hook → Service → Types
  (screen written before knowing what data looks like)

RIGHT ORDER:
  1. types/[feature].types.ts     ← Define the contract
  2. services/[feature]Service.ts ← Implement API calls
  3. hooks/use[Feature].ts        ← Wire service + state
  4. components/                   ← Build UI pieces
  5. [Feature]Screen.tsx           ← Compose everything
  6. navigation/                   ← Register route

Each step VERIFIES against the previous:
  Service matches types? ✓
  Hook calls service correctly? ✓
  Component renders hook data? ✓
  Screen composes components? ✓
```

---

## Full Walkthrough Example

### Spec: "Product Detail Screen"

**User says:** "I need a product detail screen showing images, title, price, description, reviews, and an 'Add to Cart' button. Cart persists offline."

### Parse:

```
1. ENTITY:      Product, CartItem, Review
2. FIELDS:
   Product  → id, title, price, description, images[], category, inStock
   CartItem → productId, quantity, price
   Review   → id, userId, rating, comment, createdAt
3. ACTIONS:     View product, Add to cart, View reviews, Share
4. STATES:      Loading (skeleton), Error (retry), Empty (404), Success
5. NAVIGATION:  From: ProductList → To: Cart, ReviewList
6. API:         GET /products/:id, POST /cart/items, GET /products/:id/reviews
7. STORAGE:     Cart stored locally (MMKV) for offline
8. VALIDATION:  Quantity ≥ 1, max 99
```

### Dependency Graph:

```
ProductDetailScreen
├── ImageCarousel          ← Horizontal scroll, snap, indicators
├── ProductInfo            ← Title, price, description, stock badge
├── ReviewSummary          ← Average rating, count, "See all" link
├── AddToCartButton        ← Quantity selector + CTA
│
├── useProductDetail(id)
│   ├── useQuery(['product', id], () => productService.getById(id))
│   └── useQuery(['reviews', id], () => productService.getReviews(id))
│
├── useCartStore (Zustand + MMKV persist)
│   ├── addItem(productId, quantity, price)
│   ├── removeItem(productId)
│   └── items: CartItem[]
│
├── productService.ts
│   ├── getById(id: ProductId): Promise<Product>
│   └── getReviews(id: ProductId): Promise<Review[]>
│
└── Types
    ├── Product, CartItem, Review
    ├── ProductDetailParams = { productId: ProductId }
    └── AddToCartInput = { productId: ProductId; quantity: number }
```

### File Plan:

```
src/features/product/
├── ProductDetailScreen.tsx
├── components/
│   ├── ImageCarousel.tsx
│   ├── ProductInfo.tsx
│   ├── ReviewSummary.tsx
│   ├── AddToCartButton.tsx
│   └── ProductDetailSkeleton.tsx
├── hooks/
│   └── useProductDetail.ts
├── services/
│   └── productService.ts
└── types/
    └── product.types.ts

src/stores/useCartStore.ts           ← Global (shared across features)
navigation/types.ts                  ← Add ProductDetail params
```

### Implementation (abbreviated — types first):

```typescript
// 1. types/product.types.ts
export interface Product {
  id: ProductId;
  title: string;
  price: number;
  description: string;
  images: string[];
  category: string;
  inStock: boolean;
}

export interface Review {
  id: string;
  userId: UserId;
  rating: number;  // 1-5
  comment: string;
  createdAt: string;
}

export interface AddToCartInput {
  productId: ProductId;
  quantity: number;
}

// 2. services/productService.ts
export const productService = {
  getById: (id: ProductId) => api.get<Product>(`/products/${id}`),
  getReviews: (id: ProductId) => api.get<Review[]>(`/products/${id}/reviews`),
};

// 3. hooks/useProductDetail.ts
export function useProductDetail(productId: ProductId) {
  const product = useQuery({ queryKey: ['product', productId], queryFn: () => productService.getById(productId) });
  const reviews = useQuery({ queryKey: ['reviews', productId], queryFn: () => productService.getReviews(productId) });
  const addToCart = useCartStore(state => state.addItem);

  return {
    product: product.data,
    reviews: reviews.data,
    isLoading: product.isLoading,
    error: product.error,
    refetch: product.refetch,
    handleAddToCart: (quantity: number) => {
      if (!product.data) return;
      addToCart(product.data.id, quantity, product.data.price);
    },
  };
}

// 4-5. Screen composes hook + components with 4 states
// → Loading: <ProductDetailSkeleton />
// → Error: <ErrorView onRetry={refetch} />
// → Empty: <NotFoundView />
// → Success: <ImageCarousel /> + <ProductInfo /> + <ReviewSummary /> + <AddToCartButton />
```

---

## Checklist: Verify Against Spec

```
After implementing, check EVERY item from the parsed spec:

□ All ENTITIES defined in types?
□ All FIELDS present in interfaces?
□ All ACTIONS wired to handlers?
□ All 4 STATES rendered?
□ NAVIGATION registered + params typed?
□ All API endpoints called correctly?
□ STORAGE persisted where needed?
□ VALIDATION applied to inputs?
□ Accessibility labels on interactive elements?
□ Platform-specific behavior handled (iOS vs Android)?
```
