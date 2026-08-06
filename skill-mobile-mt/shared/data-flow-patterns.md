# Data Flow Patterns — Fetching, Caching, Real-Time

> On-demand module. Loaded when implementing pagination, optimistic updates, cache invalidation, or real-time features.
> Contains production patterns that handle edge cases (race conditions, stale data, error recovery).

---

## Pagination — Infinite Scroll

### React Native (TanStack Query)

```typescript
// hooks/useProductList.ts
import { useInfiniteQuery } from '@tanstack/react-query';

interface ProductPage {
  items: Product[];
  nextCursor: string | null; // null = no more pages
}

export function useProductList(category?: string) {
  return useInfiniteQuery({
    queryKey: ['products', { category }],
    queryFn: async ({ pageParam }) => {
      const res = await productService.getProducts({
        cursor: pageParam,
        limit: 20,
        category,
      });
      return res as ProductPage;
    },
    initialPageParam: undefined as string | undefined,
    getNextPageParam: (lastPage) => lastPage.nextCursor ?? undefined,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// ProductListScreen.tsx
function ProductListScreen() {
  const { data, fetchNextPage, hasNextPage, isFetchingNextPage, isLoading, error, refetch } = useProductList();

  const products = data?.pages.flatMap(page => page.items) ?? [];

  if (isLoading) return <ProductListSkeleton />;
  if (error) return <ErrorView error={error} onRetry={refetch} />;
  if (products.length === 0) return <EmptyView message="No products found" />;

  return (
    <FlatList
      data={products}
      keyExtractor={(item) => item.id}
      renderItem={({ item }) => <ProductCard product={item} />}
      onEndReached={() => { if (hasNextPage && !isFetchingNextPage) fetchNextPage(); }}
      onEndReachedThreshold={0.5}
      ListFooterComponent={isFetchingNextPage ? <ActivityIndicator /> : null}
      refreshControl={<RefreshControl refreshing={false} onRefresh={refetch} />}
    />
  );
}
```

### Offset-Based Pagination (alternative)

```typescript
// When API uses page numbers instead of cursors
export function useProductListPaged() {
  return useInfiniteQuery({
    queryKey: ['products'],
    queryFn: async ({ pageParam = 1 }) => {
      return productService.getProducts({ page: pageParam, limit: 20 });
    },
    initialPageParam: 1,
    getNextPageParam: (lastPage, allPages) => {
      // No more pages if last page returned fewer items than limit
      return lastPage.items.length >= 20 ? allPages.length + 1 : undefined;
    },
  });
}
```

### Flutter (Riverpod)

```dart
// providers/product_list_provider.dart
@riverpod
class ProductList extends _$ProductList {
  String? _nextCursor;
  bool _hasMore = true;

  @override
  FutureOr<List<Product>> build() => _fetchPage(null);

  Future<List<Product>> _fetchPage(String? cursor) async {
    final page = await ref.read(productRepoProvider).getProducts(cursor: cursor);
    _nextCursor = page.nextCursor;
    _hasMore = page.nextCursor != null;
    return page.items;
  }

  Future<void> loadMore() async {
    if (!_hasMore || state is AsyncLoading) return;
    final currentItems = state.value ?? [];
    final newItems = await _fetchPage(_nextCursor);
    state = AsyncData([...currentItems, ...newItems]);
  }

  bool get hasMore => _hasMore;
}
```

---

## Optimistic Updates with Rollback

### React Native (TanStack Query)

```typescript
// hooks/useToggleFavorite.ts
import { useMutation, useQueryClient } from '@tanstack/react-query';

export function useToggleFavorite() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (productId: ProductId) => productService.toggleFavorite(productId),

    // Optimistic update: change UI before API responds
    onMutate: async (productId) => {
      // Cancel outgoing refetches (they would overwrite our optimistic update)
      await queryClient.cancelQueries({ queryKey: ['product', productId] });

      // Snapshot the previous value
      const previous = queryClient.getQueryData<Product>(['product', productId]);

      // Optimistically update the cache
      queryClient.setQueryData<Product>(['product', productId], (old) =>
        old ? { ...old, isFavorite: !old.isFavorite } : old
      );

      // Return snapshot for rollback
      return { previous };
    },

    // On error: rollback to snapshot
    onError: (_error, productId, context) => {
      if (context?.previous) {
        queryClient.setQueryData(['product', productId], context.previous);
      }
    },

    // On success or error: refetch to ensure server truth
    onSettled: (_data, _error, productId) => {
      queryClient.invalidateQueries({ queryKey: ['product', productId] });
    },
  });
}

// Usage: simple one-liner
// const toggleFavorite = useToggleFavorite();
// <HeartButton onPress={() => toggleFavorite.mutate(product.id)} />
```

### Zustand Optimistic Pattern

```typescript
// stores/useCartStore.ts
addItem: async (product: Product, quantity: number) => {
  // 1. Snapshot current state
  const snapshot = get().items;

  // 2. Optimistic update
  set(state => {
    state.items.push({ productId: product.id, quantity, price: product.price });
  });

  // 3. API call
  try {
    await cartService.addItem(product.id, quantity);
  } catch {
    // 4. Rollback on error
    set(state => { state.items = snapshot; });
    throw new Error('Failed to add to cart. Please try again.');
  }
},
```

---

## Cache Invalidation Strategies

### When to Invalidate

```
AFTER MUTATION (user changes data):
  → Invalidate the entity that was changed
  → Invalidate lists that contain that entity

  Example: User edits profile
    queryClient.invalidateQueries({ queryKey: ['user', userId] });
    queryClient.invalidateQueries({ queryKey: ['users'] }); // list

ON NAVIGATION BACK (may be stale):
  → Use refetchOnWindowFocus: true (TanStack Query default)
  → Or manual: useFocusEffect(() => { refetch(); });

PERIODIC POLLING (real-time-ish data):
  useQuery({
    queryKey: ['notifications'],
    queryFn: fetchNotifications,
    refetchInterval: 30_000, // every 30 seconds
    refetchIntervalInBackground: false, // stop when app backgrounded
  });

MANUAL REFRESH (pull-to-refresh):
  <RefreshControl refreshing={isRefetching} onRefresh={refetch} />

SELECTIVE vs FULL CLEAR:
  // Selective: only affected queries
  queryClient.invalidateQueries({ queryKey: ['product', productId] });

  // Full clear (logout):
  queryClient.clear();
```

### React Navigation Focus Refetch

```typescript
// hooks/useRefetchOnFocus.ts
import { useFocusEffect } from '@react-navigation/native';
import { useCallback } from 'react';

export function useRefetchOnFocus(refetch: () => void) {
  useFocusEffect(
    useCallback(() => {
      refetch();
    }, [refetch])
  );
}

// Usage:
// const { data, refetch } = useProductDetail(id);
// useRefetchOnFocus(refetch);
```

---

## WebSocket Real-Time

### React Native — Socket Connection Manager

```typescript
// services/socket.ts
import { io, Socket } from 'socket.io-client';
import { useAuthStore } from '@/stores/useAuthStore';
import { AppState } from 'react-native';

class SocketManager {
  private socket: Socket | null = null;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private maxReconnectDelay = 30_000;
  private reconnectAttempts = 0;

  connect() {
    const token = useAuthStore.getState().token;
    if (!token || this.socket?.connected) return;

    this.socket = io(process.env.EXPO_PUBLIC_WS_URL!, {
      auth: { token },
      transports: ['websocket'],
      reconnection: false, // we handle reconnection manually
    });

    this.socket.on('connect', () => {
      this.reconnectAttempts = 0;
    });

    this.socket.on('disconnect', (reason) => {
      if (reason !== 'io client disconnect') {
        this.scheduleReconnect();
      }
    });

    this.socket.on('connect_error', () => {
      this.scheduleReconnect();
    });

    // Reconnect when app comes to foreground
    AppState.addEventListener('change', (state) => {
      if (state === 'active' && !this.socket?.connected) {
        this.connect();
      }
    });
  }

  private scheduleReconnect() {
    if (this.reconnectTimer) return;
    const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts) + Math.random() * 500, this.maxReconnectDelay);
    this.reconnectAttempts++;
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      this.connect();
    }, delay);
  }

  on<T>(event: string, callback: (data: T) => void) {
    this.socket?.on(event, callback);
    return () => { this.socket?.off(event, callback); };
  }

  emit(event: string, data?: unknown) {
    this.socket?.emit(event, data);
  }

  disconnect() {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.socket?.disconnect();
    this.socket = null;
  }
}

export const socketManager = new SocketManager();

// hooks/useSocket.ts — auto-subscribe/unsubscribe
export function useSocket<T>(event: string, callback: (data: T) => void) {
  useEffect(() => {
    const unsubscribe = socketManager.on(event, callback);
    return unsubscribe;
  }, [event, callback]);
}

// Usage:
// useSocket<Message>('new_message', (msg) => {
//   queryClient.setQueryData(['messages', chatId], (old) => [...old, msg]);
// });
```

---

## Request Queuing for Offline

### React Native — Mutation Queue

```typescript
// services/offlineQueue.ts
import NetInfo from '@react-native-community/netinfo';
import AsyncStorage from '@react-native-async-storage/async-storage';

interface QueuedRequest {
  id: string;
  method: 'POST' | 'PUT' | 'DELETE';
  url: string;
  data: unknown;
  timestamp: number;
}

const QUEUE_KEY = 'offline_request_queue';

export const offlineQueue = {
  async enqueue(request: Omit<QueuedRequest, 'id' | 'timestamp'>) {
    const queue = await this.getQueue();
    queue.push({
      ...request,
      id: Math.random().toString(36).slice(2),
      timestamp: Date.now(),
    });
    await AsyncStorage.setItem(QUEUE_KEY, JSON.stringify(queue));
  },

  async getQueue(): Promise<QueuedRequest[]> {
    const raw = await AsyncStorage.getItem(QUEUE_KEY);
    return raw ? JSON.parse(raw) : [];
  },

  async flush() {
    const queue = await this.getQueue();
    const remaining: QueuedRequest[] = [];

    for (const req of queue) {
      try {
        await api({ method: req.method, url: req.url, data: req.data });
      } catch {
        remaining.push(req); // retry next time
      }
    }

    await AsyncStorage.setItem(QUEUE_KEY, JSON.stringify(remaining));
  },
};

// Auto-flush when online
NetInfo.addEventListener(state => {
  if (state.isConnected) offlineQueue.flush();
});
```

---

## Data Prefetching

```typescript
// Prefetch next screen's data when user is likely to navigate
function ProductCard({ product }: { product: Product }) {
  const queryClient = useQueryClient();

  const prefetchDetail = () => {
    queryClient.prefetchQuery({
      queryKey: ['product', product.id],
      queryFn: () => productService.getById(product.id),
      staleTime: 5 * 60 * 1000,
    });
  };

  return (
    <TouchableOpacity
      onPress={() => navigation.navigate('ProductDetail', { productId: product.id })}
      onPressIn={prefetchDetail} // prefetch on touch start (before navigation)
    >
      {/* card content */}
    </TouchableOpacity>
  );
}
```
