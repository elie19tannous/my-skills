# Lists and performance

Performance is two budgets: JavaScript must prepare work and respond to input; the native UI thread must draw and animate. Diagnose the budget that misses.

## Measure release behavior

Record:

- release build and exact commit;
- device model, OS, refresh rate, and thermal state;
- route, dataset size, cache state, and interaction;
- JS frame rate and UI frame rate;
- render/commit work, network, images, memory, and native trace when relevant.

At 60Hz, a frame is about 16.7ms; at 120Hz, about 8.3ms. A device can scroll smoothly on the UI thread while JavaScript input feedback stalls, or the reverse.

Do not profile a development build and call it production performance.

## Choose the collection primitive

| Data | Default |
| --- | --- |
| Small, fixed content that must render together | `ScrollView` may be appropriate |
| Unbounded or paginated homogeneous rows | `FlatList` or established virtualized list |
| Grouped data with headers | `SectionList` |
| Complex high-volume collection with measured limits | Project-approved specialized virtualizer |

Never nest same-direction virtualized lists inside a plain `ScrollView` unless the library explicitly supports the arrangement and virtualization remains active.

## Row identity

- Use stable domain keys.
- Keep row-local state attached to the item identity.
- Avoid capturing a changing outer object when a row needs a narrow value.
- Pass item updates by ID.
- Keep separators and headers stable.
- Confirm insertion, deletion, reorder, pagination, and refresh.

An index key can display or edit the wrong item after collection changes.

## Window tuning

Change list window props only from measurement. Larger windows reduce blanking but increase memory and mount work; smaller windows do the opposite.

Before tuning:

1. simplify row render;
2. resize and cache images correctly;
3. remove nested layout churn;
4. provide stable item identity;
5. paginate data;
6. add `getItemLayout` only when row geometry is fixed or exactly derivable;
7. then tune batch/window settings on target devices.

Record the before/after blanking, input response, memory, and mount cost.

## Pagination and refresh

- Guard against multiple end-reached calls.
- Keep one request identity per cursor/page.
- Merge without duplicate items.
- Preserve scroll position during background refresh when identity is stable.
- Show first load separately from incremental load.
- Expose retry at the failed page without discarding loaded pages.
- Define refresh conflict with optimistic or local edits.

## Images

- Request an image near its rendered dimensions.
- Use appropriate cache and placeholder behavior.
- Avoid decoding full-resolution photos for thumbnails.
- Keep aspect ratio stable to prevent list relayout.
- Release or avoid retaining large image data.
- Measure memory on image-heavy feeds.

Animating image dimensions can be expensive; prefer a transform for visual scaling when it preserves layout semantics.

## JS-thread stalls

Look for:

- large synchronous parsing or transformation;
- root-level state causing broad React work;
- development logging left in hot paths;
- repeated serialization across native boundaries;
- per-frame JS gesture work;
- request responses rendering too much at once;
- expensive work inside press handlers before feedback can paint.

Move or chunk work only after a trace identifies it. Preserve immediate press feedback before starting expensive follow-up.

## UI-thread stalls

Look for:

- layout and paint-heavy animation;
- large transparent layers and alpha compositing;
- overdraw;
- excessive shadow/blur;
- image resizing during motion;
- too many hardware-rasterized layers;
- native view hierarchy and memory pressure.

Use platform rasterization/hardware texture flags only for a measured animation and disable them when no longer needed; persistent layers consume memory.

## Startup

Measure cold and warm separately. Inspect:

- native initialization;
- JavaScript bundle load and evaluation;
- eager modules and polyfills;
- storage/auth bootstrap;
- initial network waterfall;
- font and image load;
- first meaningful screen and interactive readiness.

Keep the launch screen transition coherent, but do not delay first interaction for nonessential preloading.

## Primary references

- [React Native performance overview](https://reactnative.dev/docs/performance)
- [Optimizing FlatList configuration](https://reactnative.dev/docs/optimizing-flatlist-configuration)
- [React Native profiling](https://reactnative.dev/docs/profiling)
- [`FlatList`](https://reactnative.dev/docs/flatlist)
