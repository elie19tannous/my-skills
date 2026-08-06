# Offline-First — Mobile Data Strategy

> On-demand. Load when: "offline", "offline-first", "cache", "sync", "local database", "persistence"
> Source: Mattermost, Immich, Expensify, Ignite

---

## Architecture

```
┌─────────────────────────────────────┐
│  UI Layer (reads local only)        │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│  Repository Layer (sync logic)      │
└──────┬──────────────────────┬───────┘
       │                      │
┌──────▼──────┐     ┌─────────▼───────┐
│  Local DB   │◄───►│   Remote API    │
│  (primary)  │     │   (sync only)   │
└─────────────┘     └─────────────────┘
```

**Rule:** UI always reads local. API is sync-only, never primary.

---

## React Native — WatermelonDB (Reference Implementation)

### Schema

```typescript
// db/schema.ts
export const schema = appSchema({
  version: 1,
  tables: [
    tableSchema({
      name: 'posts',
      columns: [
        { name: 'title', type: 'string' },
        { name: 'body', type: 'string' },
        { name: 'author_id', type: 'string' },
        { name: 'created_at', type: 'number' },
        { name: 'updated_at', type: 'number' },
        { name: 'is_synced', type: 'boolean' },
        { name: 'is_deleted', type: 'boolean' },  // soft delete required for sync
      ],
    }),
  ],
});
```

### Model

```typescript
export default class Post extends Model {
  static table = 'posts';
  static associations = {
    comments: { type: 'has_many', foreignKey: 'post_id' },
  };

  @field('title') title!: string;
  @field('body') body!: string;
  @field('author_id') authorId!: string;
  @readonly @date('created_at') createdAt!: Date;
  @field('updated_at') updatedAt!: number;
  @field('is_synced') isSynced!: boolean;
  @field('is_deleted') isDeleted!: boolean;

  async markAsDeleted() {
    await this.update(post => {
      post.isDeleted = true;
      post.isSynced = false;
    });
  }
}
```

### Sync Engine

```typescript
export async function syncDatabase() {
  await synchronize({
    database,
    pullChanges: async ({ lastPulledAt }) => {
      const { changes, timestamp } = await api.get('/sync', {
        params: { last_pulled_at: lastPulledAt },
      });
      return { changes, timestamp };
    },
    pushChanges: async ({ changes, lastPulledAt }) => {
      await api.post('/sync', { changes, last_pulled_at: lastPulledAt });
    },
    migrationsEnabledAtVersion: 1,
  });
}

export function startBackgroundSync() {
  const interval = setInterval(syncDatabase, 30000);
  AppState.addEventListener('change', state => {
    if (state === 'active') syncDatabase();
  });
  return () => clearInterval(interval);
}
```

### Repository

```typescript
export class PostRepository {
  private posts = database.get<Post>('posts');

  getAll() {
    return this.posts.query(
      Q.where('is_deleted', false),
      Q.sortBy('created_at', Q.desc),
    ).fetch();
  }

  observeAll() {
    return this.posts.query(
      Q.where('is_deleted', false),
      Q.sortBy('created_at', Q.desc),
    ).observe();
  }

  async create(data: { title: string; body: string; authorId: string }) {
    return database.write(async () => {
      return this.posts.create(post => {
        Object.assign(post, data);
        post.isSynced = false;
        post.isDeleted = false;
        post.updatedAt = Date.now();
      });
    });
  }

  async update(post: Post, data: Partial<{ title: string; body: string }>) {
    return database.write(async () =>
      post.update(p => { Object.assign(p, data); p.isSynced = false; p.updatedAt = Date.now(); })
    );
  }

  async delete(post: Post) {
    return database.write(async () => post.markAsDeleted());
  }
}
```

---

## Flutter — Drift + Riverpod

### Key differences from RN

```dart
// Table definition
class Posts extends Table {
  TextColumn get id => text()();
  TextColumn get title => text()();
  BoolColumn get isSynced => boolean().withDefault(const Constant(false))();
  BoolColumn get isDeleted => boolean().withDefault(const Constant(false))();
  @override Set<Column> get primaryKey => {id};
}

// Watch (reactive, like observeAll)
Stream<List<Post>> watchAllPosts() => (select(posts)
  ..where((p) => p.isDeleted.equals(false))
  ..orderBy([(p) => Ordering.desc(p.createdAt)]))
  .watch();

// Soft delete
Future<void> softDeletePost(String id) => (update(posts)).write(
  PostsCompanion(id: Value(id), isDeleted: const Value(true), isSynced: const Value(false)),
);
```

```dart
// Sync: check connectivity first
Future<void> sync() async {
  final result = await Connectivity().checkConnectivity();
  if (result == ConnectivityResult.none) return;
  await _pushChanges();
  await _pullChanges();
}

// Background sync on connectivity restore
Connectivity().onConnectivityChanged.listen((result) {
  if (result != ConnectivityResult.none) sync();
});
```

---

## iOS — SwiftData (iOS 17+) / Core Data

```swift
@Model final class Post {
    @Attribute(.unique) var id: String
    var title: String
    var isSynced: Bool = false
    var isDeleted: Bool = false
    var updatedAt: Date?
}

// Sync with NWPathMonitor
private func startNetworkMonitoring() {
    monitor.pathUpdateHandler = { [weak self] path in
        Task { @MainActor in
            if path.status == .satisfied { await self?.sync() }
        }
    }
    monitor.start(queue: queue)
}

func sync() async {
    guard isConnected else { return }
    let unsynced = try await repository.fetchUnsynced()
    for post in unsynced {
        post.isDeleted
            ? try await apiClient.deletePost(post.id)
            : try await apiClient.upsertPost(post)
        post.isSynced = true
    }
    let remote = try await apiClient.fetchPosts()
    for post in remote { try await repository.upsert(post) }
}
```

---

## Android — Room + WorkManager

```kotlin
@Entity(tableName = "posts")
data class PostEntity(
    @PrimaryKey val id: String,
    val title: String,
    val isSynced: Boolean = false,
    val isDeleted: Boolean = false,
    val updatedAt: Long? = null,
)

@Dao interface PostDao {
    @Query("SELECT * FROM posts WHERE isDeleted = 0 ORDER BY createdAt DESC")
    fun observeAll(): Flow<List<PostEntity>>

    @Query("SELECT * FROM posts WHERE isSynced = 0")
    suspend fun getUnsynced(): List<PostEntity>

    @Query("UPDATE posts SET isDeleted = 1, isSynced = 0 WHERE id = :id")
    suspend fun softDelete(id: String)
}

// Use WorkManager for background sync (respects battery/network constraints)
fun triggerSync() {
    val request = OneTimeWorkRequestBuilder<SyncWorker>()
        .setConstraints(Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build())
        .build()
    WorkManager.getInstance(context).enqueue(request)
}
```

---

## Conflict Resolution

```typescript
// 1. Last Write Wins (simple, most apps)
const resolve = (local: Post, remote: Post) =>
  local.updatedAt > remote.updatedAt ? local : remote;

// 2. Field-Level Merge (collaborative editing)
const merge = (local: Post, remote: Post, base: Post) => ({
  ...base,
  title: local.title !== base.title ? local.title : remote.title,
  body: local.body !== base.body ? local.body : remote.body,
  updatedAt: Date.now(),
});

// 3. Operational Transform (counters/accumulators)
const resolveCounter = (local: Counter, remote: Counter, base: Counter) => ({
  ...remote,
  value: base.value + (local.value - base.value) + (remote.value - base.value),
});
```

---

## UI Components

```typescript
// Offline banner
export function OfflineBanner() {
  const [isOffline, setIsOffline] = useState(false);
  useEffect(() => NetInfo.addEventListener(s => setIsOffline(!s.isConnected)), []);
  if (!isOffline) return null;
  return <Banner message="Offline — changes sync when connected." />;
}

// Sync status
type SyncStatus = 'synced' | 'pending' | 'syncing' | 'error';
const STATUS_CONFIG = {
  synced:  { icon: 'check-circle', color: 'green' },
  pending: { icon: 'clock',        color: 'orange' },
  syncing: { icon: 'sync',         color: 'blue' },
  error:   { icon: 'alert-circle', color: 'red' },
};

// Optimistic update with rollback
const updateOptimistic = async (id: string, updates: Partial<Post>) => {
  const prev = queryClient.getQueryData(['posts', id]);
  queryClient.setQueryData(['posts', id], old => ({ ...old, ...updates }));
  try {
    await repository.update(id, updates);
    await syncDatabase();
  } catch {
    queryClient.setQueryData(['posts', id], prev);
  }
};
```

---

## Database Selection

| DB | Platform | Use when |
|----|----------|----------|
| **WatermelonDB** | React Native | Complex queries, observables, built-in sync |
| **MMKV** | React Native | Key-value only, speed critical |
| **Realm** | RN / Flutter / iOS | Cross-platform, reactive |
| **SQLite** | All | Full SQL control |
| **Drift** | Flutter | Type-safe, migrations, code gen |
| **SwiftData** | iOS 17+ | Simple models, native |
| **Core Data** | iOS | Complex relationships, migrations |
| **Room** | Android | Flow/LiveData integration |

---

## Checklist

```
Data:
□ All data written to local DB first
□ Soft deletes (never hard delete)
□ isSynced flag per record
□ Conflict resolution strategy defined
□ Retry for failed syncs

UI:
□ Offline banner
□ Sync status indicator
□ Optimistic updates
□ Pull-to-refresh triggers sync

Sync:
□ Sync on app foreground
□ Sync on connectivity restore
□ Background sync (30s interval)
□ Sync doesn't block UI thread
```

---

## Anti-Patterns

```
❌ UI reads directly from API
❌ Blocking UI during sync
❌ Hard deletes (breaks sync)
❌ Syncing on every keystroke
❌ No retry for failed syncs
❌ No offline indicator
❌ Assuming network is available
❌ Losing data on conflict
```
