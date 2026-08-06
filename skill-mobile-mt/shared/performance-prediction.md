# Performance Prediction — Simulate Before Deploy

> Calculate frame rates, bridge calls, and memory before deploying code.

## Performance Prophet Pattern

**Predict behavior BEFORE deployment** using mathematical models.

### Frame Budget Calculation

```
TARGET: 60 FPS = 16.67ms per frame
PROMOTION: 120 FPS = 8.33ms per frame

BUDGET BREAKDOWN (React Native):
- JavaScript execution: 8ms
- Bridge calls: 3ms
- Native rendering: 4ms
- Layout: 1.67ms

RULE: Total < 16.67ms for 60 FPS
```

### Predict List Performance

```typescript
// Given code:
<FlatList
  data={items}  // 50 items
  renderItem={({ item }) => (
    <Item
      title={item.title}  // 1 bridge call
      image={item.image}  // 1 bridge call
      onPress={() => logEvent(item.id)}  // 1 bridge call
    />
  )}
/>

// Calculate:
Bridge calls per item: 3
Total items: 50
Total bridge calls: 50 × 3 = 150 calls
Time per call: ~0.3ms
Total time: 150 × 0.3ms = 45ms per frame

// Prediction:
16.67ms (60 FPS budget) vs 45ms (actual)
Result: 16.67 / 45 = 0.37 → 37% of 60 FPS = 22 FPS
Verdict: ❌ JANK - Users will notice lag

// Auto-fix suggestions:
1. Use getItemLayout (saves layout calculations)
2. Memoize renderItem component
3. Defer logEvent to InteractionManager
4. Use native driver for animations
5. Implement virtualization (windowSize: 5)

Expected after fix: ~12ms per frame → 60 FPS ✓
```

### Predict Memory Usage

```
IMAGE CALCULATION:
- Image: 1000×1000 pixels
- Color depth: 4 bytes (RGBA)
- Memory: 1000 × 1000 × 4 = 4MB per image

List with 50 images:
- No optimization: 50 × 4MB = 200MB
- With thumbnail (200×200): 50 × 0.16MB = 8MB
- Verdict: Use thumbnails + lazy load

MEMORY BUDGET:
- iOS: ~120MB baseline
- Android: ~80MB baseline (varies by device)
- Target: < 150MB total for stability
```

### Predict Bundle Impact

```
NEW PACKAGE: moment.js
Size: 230KB minified
Bundle before: 2.1MB
Bundle after: 2.33MB
Impact: +11% bundle size

Alternatives:
- date-fns/esm: 50KB (modular)
- day.js: 2KB (minimal)
Recommendation: Use day.js → 98% size reduction
```

## Quick Calculations

### 1. FlatList Frame Rate
```
Formula: FPS = 16.67ms / (bridge_calls × 0.3ms + render_time)

Example:
- 100 items
- 5 bridge calls per item
- 2ms render time per item

Time per frame: (100 × 5 × 0.3ms) + (100 × 2ms) = 150ms + 200ms = 350ms
FPS: 16.67 / 350 = 0.048 → 4.8 FPS

Verdict: ❌ UNUSABLE - Must optimize
```

### 2. Animation Smoothness
```
Rule: Use native driver when possible

With native driver:
- Runs at 60 FPS (or 120 FPS ProMotion)
- No bridge calls per frame
- Smooth animations

Without native driver:
- JavaScript thread: ~16.67ms budget
- Each frame: ~2-3 bridge calls
- Often drops to 30-45 FPS

Verdict: Always use { useNativeDriver: true }
```

### 3. Network Overhead
```
API Response: 500KB JSON
Parse time: ~50ms (varies by device)
UI block: 50ms = 3 frames dropped

Optimization:
- Paginate: 50KB per page → 5ms parse
- Background thread: 0 frames dropped
```

## Platform-Specific Predictions

### React Native
```
KNOWN BOTTLENECKS:
1. Bridge calls: 0.3ms each
2. console.log: 10-50ms (dev mode)
3. Inline styles: Re-creates every render
4. Anonymous functions in render: Creates new reference

OPTIMIZATION PRIORITY:
1. Remove console.log (50ms → 0ms)
2. StyleSheet.create (5ms → 0.1ms)
3. useCallback/useMemo (prevents re-renders)
4. Native driver animations (60 FPS guaranteed)
```

### Flutter
```
KNOWN BOTTLENECKS:
1. Build method: Should be < 8ms
2. setState: Triggers full rebuild
3. Large widget trees: O(n) complexity

OPTIMIZATION PRIORITY:
1. const constructors (immutable widgets)
2. ListView.builder vs ListView (O(visible) vs O(n))
3. RepaintBoundary (isolate repaints)
4. Selective rebuilds (Consumer vs rebuild all)
```

## Prediction Workflow

```
BEFORE IMPLEMENTING:
1. Estimate bridge calls (RN) or build time (Flutter)
2. Calculate frame budget impact
3. Predict FPS: 16.67ms / total_time
4. If < 60 FPS: redesign or optimize first

AFTER IMPLEMENTING:
1. Profile with React DevTools / Flutter DevTools
2. Compare predicted vs actual
3. Adjust model if off by > 20%
4. Document learnings for next time
```

## Auto-Suggestions

```
If prediction shows < 60 FPS:

FOR LISTS:
✓ Use getItemLayout
✓ Memoize renderItem
✓ Reduce bridge calls
✓ Virtualization (windowSize)
✓ Thumbnail images

FOR ANIMATIONS:
✓ Use native driver
✓ Avoid layout animations
✓ Prefer transform/opacity
✓ Use InteractionManager

FOR MEMORY:
✓ Image optimization
✓ Lazy loading
✓ Pagination
✓ Clear caches
```
