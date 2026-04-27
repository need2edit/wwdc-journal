# Swift Language, Concurrency, Performance & Memory -- WWDC25 Deep Analysis

Comprehensive analysis of 13 WWDC25 sessions covering Swift 6.2, concurrency, performance optimization, memory management, interoperability, and tooling.

---

## 1. Swift 6.2 Concurrency: The "Approachable Concurrency" Revolution

### 1.1 Main Actor by Default Mode (WWDC25-245, 268, 270, 266)

The single biggest conceptual shift in Swift 6.2 is **main actor by default mode**. This fundamentally changes how concurrency works for app targets.

**Key details:**
- Enabled by default for new app projects in Xcode 26 (WWDC25-268)
- All types in a module are implicitly `@MainActor` -- you do not write annotations (WWDC25-266)
- Eliminates data-race safety errors about unsafe global/static variables (WWDC25-245)
- Recommended for apps, scripts, and other executable targets; NOT for libraries (WWDC25-245)
- Driven by a build setting: "Default Actor Isolation" set to "MainActor" (WWDC25-268)

**Best practice:** "Use this primarily for your main app module and any modules that are focused on UI interactions" (WWDC25-268). Library modules should remain nonisolated by default.

**Hidden gem:** When main actor mode is on, your `@Observable` data model classes do not need any `@MainActor` annotations -- Swift infers isolation from the instantiation context (WWDC25-266). "Because I instantiate the model inside the view's declaration, Swift will make sure that the model instance is properly isolated."

### 1.2 The `@concurrent` Attribute (WWDC25-245, 268, 270)

A new attribute that explicitly offloads a function to a background thread.

```swift
@concurrent
func decodeImage(_ data: Data) async -> Image {
    // Always runs on concurrent thread pool
}
```

**Key guidance:**
- Use `@concurrent` when you have identified (via profiling) that specific work is too expensive for the main thread (WWDC25-268)
- For libraries: prefer `nonisolated` over `@concurrent` -- let the caller decide whether to offload (WWDC25-268): "For libraries, it's best to provide a nonisolated API and let clients decide whether to offload work"
- `@concurrent` functions always switch off an actor to run (WWDC25-268)
- Can also be applied to Task closures: `Task { @concurrent in ... }` (WWDC25-268)

**Migration tip:** When moving code off the main actor, the compiler shows where the function accesses main-actor state. Three strategies: (1) move main-actor code to a caller, (2) use `await` to access main actor from concurrent code, (3) mark code `nonisolated` (WWDC25-268).

### 1.3 Async Functions No Longer Eagerly Offload (WWDC25-245)

This is a critical behavioral change in Swift 6.2:

> "Instead of eagerly offloading async functions that aren't tied to a specific actor, the function will continue to run on the actor it was called from." (WWDC25-245)

This means a `nonisolated` async function called from `@MainActor` code stays on the main actor unless explicitly marked `@concurrent`. This eliminates a major class of false-positive data race errors.

### 1.4 Isolated Conformances (WWDC25-245)

New in Swift 6.2: protocol conformances can be actor-isolated.

```swift
extension StickerModel: @MainActor Exportable {
    func export() {
        photoProcessor.exportAsPNG()
    }
}
```

The compiler ensures this conformance is only used on the main actor. If you try to use it from a `nonisolated` context, you get a compile error.

### 1.5 `nonisolated` on Types (WWDC25-270)

New in Swift 6.1+: you can mark an entire struct/class as `nonisolated` to decouple all members from any actor.

```swift
nonisolated struct PhotoProcessor {
    // All properties and methods are automatically nonisolated
}
```

### 1.6 Build Settings Recommendation (WWDC25-268)

Apple recommends TWO build settings for new projects:
1. **Approachable Concurrency** -- enables a suite of upcoming features that make concurrency easier
2. **Default Actor Isolation = MainActor** -- for UI-focused modules

"We recommend that all projects adopt [Approachable Concurrency]" (WWDC25-268).

---

## 2. SwiftUI and Concurrency (WWDC25-266, 306)

### 2.1 SwiftUI Offloads Your Code to Background Threads (WWDC25-266)

**Critical insight many developers miss:** SwiftUI already runs some of your code on background threads:
- **Shape protocol** `path(in:)` methods
- **`visualEffect` closures** -- "Visual effects can get fancy, and expensive to render. So SwiftUI can choose to call this closure from a background thread" (WWDC25-266)
- **Layout protocol** requirement methods
- **`onGeometryChange`** first closure argument

These APIs use `@Sendable` annotations to express this runtime behavior. The fix for data-race errors in sendable closures: **capture values in the closure's capture list** rather than accessing `self`:

```swift
.visualEffect { [pulse] content, _ in
    content.blur(radius: pulse ? 2 : 0)
}
```

### 2.2 Synchronous Callbacks by Design (WWDC25-266)

**Why Button's action is synchronous, not async:**
- Synchronous mutations are critical for time-sensitive logic like animations
- An `await` in an async action can cause suspension past the frame deadline, making animations laggy
- Pattern: set loading state synchronously with `withAnimation`, then kick off async work in a `Task`

```swift
.onTapGesture {
    withAnimation { model.isExtracting = true }
    Task {
        await model.extractColorScheme()
        withAnimation { model.isExtracting = false }
    }
}
```

**Best practice:** Separate UI logic (synchronous) from async work. Use state as a bridge between them.

### 2.3 SwiftUI Instrument -- Cause & Effect Graph (WWDC25-306)

The new SwiftUI Instrument in Xcode 26 Instruments introduces:
- **View Body Updates** track: shows when view bodies run and flags long updates in orange/red
- **Cause & Effect Graph**: visual chain from gesture/state change to view body updates
- **Long View Body Updates summary**: filters to show only problematic updates

**Key performance pattern discovered:** Accessing an `@Observable` array property (like `favoritesCollection.landmarks`) from multiple list item views causes ALL items to update when ANY element changes. Fix: use per-item `@Observable` view models with `@ObservationIgnored` on the dictionary:

```swift
@ObservationIgnored private var viewModels: [Landmark.ID: ViewModel] = [:]
```

**Hidden gem:** Move expensive computed properties (like formatter creation) out of view bodies and cache them at the model level. Formatters like `NumberFormatter` and `MeasurementFormatter` are expensive to create.

---

## 3. Performance & Memory Deep Dive (WWDC25-312, 308, 226)

### 3.1 InlineArray (WWDC25-245, 312)

New fixed-size array type with inline storage:

```swift
var array: InlineArray<3, Int> = [1, 2, 3]
```

**Key properties:**
- Size is part of the type (value generics)
- Elements stored directly inline (stack or within containing type)
- No heap allocation, no reference counting, no copy-on-write
- No exclusivity checks needed
- Size can be inferred from array literals
- Compiler can eliminate bounds checking when index < size at compile time
- Copies eagerly on assignment (double-edged sword)

**When to use:** Fixed-size arrays that are modified in place but never copied. Perfect for caches, lookup tables, pixel buffers.

**When NOT to use:** If you need dynamic resizing, sharing references between variables, or frequent copying.

### 3.2 Span Types (WWDC25-245, 312, 308)

New family of safe, non-escapable types for accessing contiguous memory:

| Type | Purpose |
|------|---------|
| `Span<T>` | Read-only typed access |
| `MutableSpan<T>` | Mutable typed access |
| `RawSpan` | Read-only untyped access |
| `OutputRawSpan` | Write-only for initializing collections |
| `UTF8Span` | Safe Unicode processing |

**Why Spans matter:**
- Performance of `UnsafeBufferPointer` without any unsafety
- Non-escapable: compiler prevents returning or storing a Span beyond its source's lifetime
- No reference counting overhead
- Available on all container types via `.span` property

**Performance results from WWDC25-312:** Using `RawSpan` and `OutputRawSpan` instead of `Data` made parsing **6x faster** by eliminating retain/release overhead. Combined with algorithmic fixes: **700x total speedup**.

**Hidden gem from WWDC25-308:** Switching binary search from `Collection` to `Span` gave a significant speedup because it eliminated protocol witness table overhead and enabled better inlining.

### 3.3 Non-Escapable Types (~Escapable) (WWDC25-312)

The language feature underpinning Spans. A non-escapable type's lifetime is tied to its source:

```swift
// This WON'T compile -- can't return a Span with no lifetime source
func getSpan() -> Span<UInt8> { } // error

// This WON'T compile -- can't capture Span in an escaping closure
let span = array.span
return { span.count } // error
```

### 3.4 Eliminating Exclusivity Checks (WWDC25-312)

Runtime exclusivity checks (`swift_beginAccess` / `swift_endAccess`) show up when modifying class properties. Fix: move properties from nested classes to the parent struct. The session showed this by moving `previousPixel` and `pixelCache` from a `State` class to the parser struct itself.

### 3.5 Algorithmic Performance Gotchas (WWDC25-312)

**Data.dropFirst() is O(n)!** It copies the entire remaining data. Use `popFirst()` instead for O(1) shrinking from the front.

**Chained flatMap allocations:** Elegant functional chains like `readEncodedPixels().flatMap{...}.prefix(...).flatMap{...}` create massive numbers of intermediate allocations. Pre-allocate the final buffer and write directly.

### 3.6 CPU Bottleneck Analysis (WWDC25-308)

New Instruments tools:
- **CPU Profiler**: samples based on CPU clock frequency (more accurate than Time Profiler for CPU optimization)
- **Processor Trace**: shows every function call as an exact flame graph, not estimated
- **CPU Counters**: bottleneck analysis with four categories

**Optimization order matters:**
1. Fix algorithmic issues first (Collection -> Span)
2. Fix software runtime overheads (generic specialization, `@inlinable`)
3. Then do CPU micro-optimizations (branchless code, cache-friendly layouts)

**Hidden gem:** Generic functions in frameworks can't be specialized by callers. Add `@inlinable` to enable specialization, or manually specialize for performance-critical types.

**Cache-friendly data layouts:** Eytzinger layout for binary search puts search comparison points on the same cache line, yielding 2x speedup. Cache lines are 64-128 bytes; binary search is pathological for caches.

### 3.7 Power Profiling (WWDC25-226)

- **Power Profiler** in Instruments: new tool for measuring system-level and per-app power impact
- **On-device power profiling**: collect traces via Control Center without being connected to Xcode
- CPU power impact score of 21 vs 1 baseline identified a regression from loading all thumbnails upfront
- **Lazy loading** reduced CPU power impact from 21 to 4.3
- Cache expensive computations (JSON parsing, file I/O) -- don't repeat them on every event

---

## 4. Structured Concurrency Patterns (WWDC25-270, 250, 227)

### 4.1 TaskGroup for Dynamic Parallelism (WWDC25-270)

Use `withTaskGroup` when the number of parallel tasks is dynamic:

```swift
await withTaskGroup { group in
    for item in selection {
        guard processedPhotos[item.id] == nil else { continue }
        group.addTask {
            let data = await self.getData(for: item)
            let photo = await PhotoProcessor().process(data: data)
            return photo.map { ProcessedPhotoResult(id: item.id, processedPhoto: $0) }
        }
    }
    for await result in group {
        if let result { processedPhotos[result.id] = result.processedPhoto }
    }
}
```

### 4.2 async let for Known Parallelism (WWDC25-270)

When you know exactly how many parallel tasks:

```swift
async let sticker = extractSticker(from: data)
async let colors = extractColors(from: data)
guard let sticker = await sticker, let colors = await colors else { return nil }
```

### 4.3 Data Race Resolution Decision Tree (WWDC25-270)

When the compiler flags a data race:
1. **Can you avoid sharing?** Move shared state to a local variable (preferred)
2. **Can you use a Sendable value type?** `Data` implements copy-on-write, so passing it to parallel tasks is safe
3. **Must you share?** Isolate to an actor (last resort)

### 4.4 Network Framework Concurrency APIs (WWDC25-250)

New in iOS/macOS 26: `NetworkConnection`, `NetworkListener`, `NetworkBrowser` -- designed for structured concurrency:
- Declarative protocol stack (SwiftUI-like syntax)
- `Coder` protocol: send/receive `Codable` types directly without manual serialization
- `TLV` (Type-Length-Value) framer: built-in message framing
- Connections auto-cancel when their task is cancelled
- `NetworkListener.run` starts subtasks per incoming connection automatically

### 4.5 Background Task APIs (WWDC25-227)

**New: `BGContinuedProcessingTask`** -- for user-initiated work that continues in background:
- Must start from explicit user action (button tap)
- System shows progress UI
- Must report progress via `Progress` protocol or task gets expired
- Supports GPU resources (with background GPU capability)
- Wildcard identifiers for dynamic task names

**Decision framework for background APIs:**
| Need | API |
|------|-----|
| Periodic content fetch | `BGAppRefreshTask` |
| Server-pushed updates | Background Push Notifications |
| Heavy processing (ML, DB maintenance) | `BGProcessingTask` |
| Finish in-flight work | `beginBackgroundTask` / `endBackgroundTask` |
| User-initiated long task | `BGContinuedProcessingTask` (NEW) |

---

## 5. Interoperability (WWDC25-311, 307)

### 5.1 Safe C/C++ Interop (WWDC25-311)

**Strict Memory Safety mode** (`StrictMemorySafety = YES`): new compiler mode that warns about all unsafe constructs in Swift, including subtle C/C++ pointer usage.

**Key annotations for C/C++ headers:**
| Annotation | Purpose |
|------------|---------|
| `__counted_by(size)` | Bounds info for pointers -> imported as `Span` |
| `__noescape` | Lifetime info: pointer doesn't escape function |
| `__lifetimebound` | Return value lifetime depends on parameter |
| `SWIFT_NONESCAPABLE` | C++ view type -> imported as non-escapable |
| `SWIFT_SHARED_REFERENCE(retain, release)` | C++ ref-counted type -> auto memory management |
| `SWIFT_RETURNS_RETAINED` / `SWIFT_RETURNS_UNRETAINED` | Ownership for returned ref-counted types |

**C++ bounds safety tools:**
- **C++ Standard Library Hardening**: adds bounds checks to `std::span`, `std::vector` subscripts
- **Unsafe buffer usage errors**: flag raw pointer usage in C++
- **Bounds Safety extension for C**: `__counted_by` with runtime bounds checks

**Apple internal adoption:** WebKit and Messages app subsystem use strict memory safety mode.

### 5.2 Swift-Java Interop (WWDC25-307)

The `swift-java` project enables bidirectional interop:
- **Swift calling Java:** `JavaKit` macros generate Swift wrappers; use `@JavaImplementation` for JNI native methods
- **Java calling Swift:** `swift-java` CLI generates Java classes from Swift source; uses `SwiftArena` for memory management
- Uses Java's Foreign Function API (not just JNI)
- `JavaKit` handles object lifetime by promoting to global references when necessary

---

## 6. SwiftData (WWDC25-291)

### 6.1 Class Inheritance Support (New in iOS 26)

```swift
@Model class Trip { ... }
@Model class BusinessTrip: Trip { var perdiem: Double = 0.0 }
@Model class PersonalTrip: Trip { var reason: Reason }
```

**Use inheritance when:** Models form a natural "is-a" hierarchy AND you need both deep searches (all trips) and shallow searches (only business trips). Don't use it just to share a common property -- use protocols instead.

### 6.2 Query Performance Tips

- `propertiesToFetch`: fetch only needed properties during migration
- `relationshipKeyPathsForPrefetching`: prefetch relationships you know you'll traverse
- `fetchLimit`: use in widgets to avoid fetching entire dataset
- Use `#Predicate { $0 is PersonalTrip }` for type-based filtering

### 6.3 Efficient Change Tracking

Use persistent history tokens to avoid unnecessary refetches:
- Fetch latest `HistoryDescriptor` with `fetchLimit = 1` and reverse sort
- Filter history by entity names of interest
- Only refetch when changes to relevant entities exist

---

## 7. Observation Library Updates (WWDC25-245)

### 7.1 New `Observations` AsyncSequence

Stream state changes from `@Observable` types:

```swift
let values = Observations {
    "\(player.score) points and \(player.item)"
}
for await value in values { print(value) }
```

**Transactional updates:** If you synchronously update both `score` and `item`, you get ONE observation update containing both changes (not two).

---

## 8. Cross-References Between Sessions

| Session | References |
|---------|-----------|
| WWDC25-245 (What's new in Swift) | -> 270, 268, 312, 311, 307, 346 |
| WWDC25-268 (Embracing Concurrency) | -> 270, WWDC23-10170 |
| WWDC25-270 (Code-along Concurrency) | -> 268, 266, WWDC23-10248, WWDC23-10170 |
| WWDC25-266 (Concurrency in SwiftUI) | -> 270, 268, WWDC23-10156 |
| WWDC25-312 (Memory & Performance) | -> 308, 226, 245, WWDC24-10217 |
| WWDC25-311 (C/C++ Interop) | -> 312 |
| WWDC25-307 (Java Interop) | -> 312, 311, 245, WWDC23-10172 |
| WWDC25-306 (SwiftUI Instruments) | -> 308, WWDC23-10248, WWDC23-10160, WWDC21-10022 |
| WWDC25-308 (CPU Instruments) | -> 312, 306, 226, WWDC24-10217, WWDC22-110350 |
| WWDC25-226 (Power Profiling) | -> 308 |
| WWDC25-250 (Network Concurrency) | -> 268, 228 |
| WWDC25-291 (SwiftData) | -> 256, WWDC24-10075 |
| WWDC25-227 (Background Tasks) | -- (standalone) |

---

## 9. Migration Checklist: Swift 6.2 Adoption

1. **Enable Approachable Concurrency** build setting (all projects)
2. **Set Default Actor Isolation to MainActor** (app modules only)
3. **Remove explicit `@MainActor` annotations** that are now inferred
4. **Replace ad-hoc background dispatching** with `@concurrent` attribute
5. **Adopt `nonisolated` on types** for code that should run anywhere
6. **Use isolated conformances** (`extension Foo: @MainActor SomeProtocol`) where needed
7. **Profile before adding concurrency** -- use Instruments to identify actual bottlenecks
8. **Replace `UnsafeBufferPointer` with `Span`** where possible
9. **Use `InlineArray` for fixed-size hot-path arrays**
10. **Enable Strict Memory Safety** for security-sensitive modules
11. **Annotate C/C++ headers** with `__counted_by`, `__noescape`, `__lifetimebound`
12. **Adopt new SwiftUI Instrument** for view body performance analysis

---

## 10. Key Quotes

> "Concurrent code is more complex than single-threaded code, and you should only introduce concurrency as you need it." -- Doug, Swift team (WWDC25-268)

> "If it can't be made faster without concurrency, you might need to introduce concurrency." -- Doug (WWDC25-268)

> "The optimizations you make with Swift concurrency should always be based on data from analysis tools." -- Sima (WWDC25-270)

> "Synchronous mutations of observable properties, and synchronous callbacks, are the most natural types of interaction with [SwiftUI]." -- Daniel, SwiftUI team (WWDC25-266)

> "We've improved performance enough that Instruments isn't really getting enough time to inspect the parser process." -- Nate Cook (WWDC25-312)

> "This order was important: we have to ensure the CPU-focused tools aren't confused by extra software runtime overheads." -- Matt, kernel team (WWDC25-308)

> "Background execution isn't guaranteed. Instead, it's opportunistic, often discretionary, and tightly managed." -- Ryan (WWDC25-227)
