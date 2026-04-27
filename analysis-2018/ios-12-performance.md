# iOS 12 Performance — WWDC 2018 Analysis

**Sessions covered:** 202 (What's New in Cocoa Touch), 220 (High Performance Auto Layout), 225 (A Tour of UICollectionView), 229 (Using Collections Effectively), 407 (Practical Approaches to Great App Performance), 416 (iOS Memory Deep Dive), 219 (Image and Graphics Best Practices), 227 (Optimizing App Assets), 405 (Measuring Performance Using Logging), 410 (Creating Custom Instruments), 408 (Building Faster in Xcode), 415 (Behind the Scenes of the Xcode Build Process), 228 (What's New in Energy Debugging), 414 (Understanding Crashes and Crash Logs)

## Headline

WWDC 2018 was the **performance year**. Apple explicitly slowed feature growth in iOS 12 and aimed every new release at making existing devices faster — even iPhone 5s/iPad Air (A7/A8) class devices. This shows up everywhere: the kernel learned to ramp CPU performance ahead of scrolling demand, Auto Layout's exponential cost in nested/dependent layouts is now linear, scrolling prefetch was reworked to avoid contention, and Apple shipped a brand-new public `os_signpost` API plus user-buildable Custom Instruments so you can measure your own app the same way Apple measures iOS itself.

## The CPU Ramp-Up Story (202)

- iOS 12 exposes scrolling activity from UIKit all the way down to the CPU performance controller. Before iOS 12, the controller waited until it observed sustained load; the burst nature of scrolling meant it had already ramped UP just as the burst was ENDING.
- **HIDDEN GEM**: counterintuitively, devices with light background work could drop _more_ scrolling frames than fully idle devices in iOS 11, because the idle-then-burst pattern looked indistinguishable to the scheduler. iOS 12 fixes this by passing scrolling intent down the stack.
- Result: smoother scrolling for free in every existing app, no code changes required.

## Cell Prefetch Bug Apple Actually Hit Themselves (202)

- The `UITableViewDataSourcePrefetching` API was added in iOS 10 to push expensive cell prep off the main thread.
- In iOS 11, Apple noticed prefetch tasks could run _concurrent_ with the visible-cell `cellForRowAt` request, causing CPU contention that made both slower.
- iOS 12 serializes these so prefetch never competes with the cell that's needed _now_. Free win for every app using the prefetch API.
- **BEST PRACTICE**: if you haven't adopted prefetch yet, do it. The serialization fix makes it strictly better than rolling your own background queue.

## Automatic Backing Stores (202) — the order-of-magnitude memory win

- Every `UIView` `drawRect` and every `UIGraphicsImageRenderer` offscreen render now picks the smallest backing-store format that fits the content drawn into it.
- A grayscale sketch rendered at full screen on iPhone X used to take 2.2 MB (375×250 pt × 9 px²/pt × 8 B/px wide-color). With automatic backing stores it now takes ~275 KB.
- **HIDDEN GEM**: this is automatic when you build with iOS 12 SDK. If you specifically need an extended-range image, opt back in via `UIGraphicsImageRendererFormat.range = .extended`.
- Don't use `UIGraphicsBeginImageContextWithOptions` anymore — it always picks 4 bytes/pixel sRGB. Switch to `UIGraphicsImageRenderer`. (See also 219, 416.)

## Auto Layout: From Exponential to Linear (220)

The Auto Layout team did major asymptotic work in iOS 12:

| Pattern | iOS 11 | iOS 12 |
|---|---|---|
| Independent siblings | linear | linear (lower constant) |
| Dependent siblings | **exponential** | linear |
| Nested views | **exponential** | linear |

- **PERFORMANCE**: nested view hierarchies and dependent-sibling layouts (any view with constraints to a sibling — i.e., most real layouts) now scale linearly. Apps with tall view trees can see massive wins by just relinking against iOS 12.
- **BEST PRACTICE**: Constraint Churn — destroying constraints in `updateConstraints` and reactivating them when nothing has changed — was the single most common bug Apple found in third-party apps. Use `setHidden` rather than ripping a view out, and keep two arrays of constraints (e.g. `imageConstraints` / `noImageConstraints`) you can deactivate/activate together.
- A new (not yet shipped at WWDC time) **Layout Instrument** specifically charts constraint churn count and UILabel sizing time, lane by lane.
- **HIDDEN GEM**: `intrinsicContentSize` returning `UIView.noIntrinsicMetric` for both axes tells the parent "I already know my size, don't bother measuring text" — a real win for text-heavy apps where the constraints fully determine size.
- `systemLayoutSizeFitting(...)` creates a **new layout engine** internally on every call. Forwarding it from a self-sizing cell to its content view defeats the optimizations UIKit added. If you do this and scrolling is bad, that's why.

## Custom UICollectionView Layouts (225)

- Custom layout subclasses must override 4 methods + 1 honorable mention: `collectionViewContentSize`, `layoutAttributesForElements(in:)`, `layoutAttributesForItem(at:)`, `prepare()`, and `shouldInvalidateLayout(forBoundsChange:)`.
- **PERFORMANCE**: in `prepare()`, cache layout attributes in an array. `layoutAttributesForElementsInRect` is called every frame during scroll — filtering a 10,000-cell array linearly there will tank scrolling.
- **BEST PRACTICE**: if your layout has cells stored top-to-bottom, the cached attributes array is sorted by minY. Use **binary search** to find the first visible cell, then walk up and down until you exit the rect. This is the difference between smooth scrolling and a janky mosaic at scale.
- `performBatchUpdates`: deletes/inserts/moves to the **collection view** can be in any order; updates to your **data source** absolutely cannot. Decompose moves into delete + insert. Apply deletes first in **descending** index order, then inserts in **ascending** index order. Reload = delete + insert internally with conflict detection — that's why "delete + reload" of overlapping index paths crashes.

## Memory: Pages, Compression, and the EXC_RESOURCE Trap (416)

- Memory is allocated in 16 KB pages. Total app memory = pages × 16 KB. The number that matters for being killed is **dirty + compressed**, not virtual.
- Clean memory (memory-mapped read-only files like JPEGs) is purgeable and free; the kernel reclaims it on demand.
- iOS has no swap. Instead it has a **memory compressor** that squeezes unaccessed pages. This means clearing a cache on a memory warning can _increase_ memory usage temporarily, because you have to decompress pages just to delete the objects. **PERFORMANCE**: respond to memory warnings with policy changes (stop caching, throttle background work) rather than mass-flushing data.
- `NSCache` allocates purgeable memory and is thread-safe. Prefer it to a `Dictionary` for caches.
- Linked frameworks have a `__DATA_CONST` section (clean) and a `__DATA_DIRTY` section (always counts against you). Singletons and global initializers in your own frameworks bloat dirty memory; minimize them.
- Xcode 10 catches `EXC_RESOURCE` exceptions and pauses your app, letting you start the Memory Debugger right at the crash point.
- **HIDDEN GEM**: command-line tools that work on `.memgraph` files exported from Xcode: `vmmap --summary`, `vmmap --pages`, `heap --sortBySize`, `heap --addresses`, `leaks --traceTree`, `malloc_history --fullStacks`. You can pipe vmmap into grep + awk to sum dirty pages from any framework. Enable malloc stack logging in the scheme's Diagnostics tab to get backtraces for every allocation.

## Image Memory: 590 KB JPEG → 10 MB in RAM (416, 219)

- Image memory cost = width × height × bytes-per-pixel, _not_ file size. A 2048×1536 sRGB image = 10 MB resident even if the JPEG on disk is 590 KB.
- **URGENT**: `UIImage(contentsOfFile:).draw(in:)` decodes the entire image, then scales. For thumbnails, use `CGImageSourceCreateThumbnailAtIndex` from ImageIO — it streams and only pays the dirty cost of the resulting image. ~50% faster as a bonus.
- Wide-color (Display P3) images are 8 bytes/pixel — double sRGB. Only use them when you need the gamut.
- Alpha-8 (single-channel mask) images are 1 byte/pixel — 75% smaller than sRGB. Perfect for monochrome icons and text masks.
- **BEST PRACTICE**: don't pick a pixel format. Use `UIGraphicsImageRenderer` and let iOS pick. As of iOS 12 it picks alpha-8 for grayscale, sRGB for color, wide for HDR — automatically.

## Image Tinting and Asset Optimization (219, 227)

- A black mask + tint via image view is "free": tint is a multiply, no allocation.
- Asset catalogs in iOS 12 do better deduplication and compression. Re-importing PNGs through the asset catalog vs. shipping them as bundle resources can cut image weight.
- Background unloading: register for `UIApplicationDidEnterBackground` (or use `viewWillDisappear`/`viewDidAppear` for tab/nav controllers) to free large images when off-screen. Reload them on foreground — invisible to the user, free RAM for the system.

## os_signpost: A Brand-New API (405, 102)

- `printf` is the wrong tool for production logging — slow, unstructured, no levels.
- `os_log` (2016) is a fast structured logger.
- **NEW in iOS 12**: `os_signpost` builds on `os_log` to emit named begin/end intervals and points-of-interest events that flow directly into Instruments. Adding signposts at the boundaries of your critical sections gives you a custom visualization with zero printf overhead.
- The special `OSLog.Category.pointsOfInterest` category is automatically picked up by Instruments and shown in a dedicated lane.
- Format strings can capture variables (`%{public}s`, `%lu`) that become column data in your Custom Instruments — no string parsing required.

## Custom Instruments (410)

- Brand-new "Instruments Package" Xcode project type lets you ship custom analysis tools as bundles of XML + Clips production rules.
- The Instruments architecture was rewritten so all instruments (including Apple's own — System Trace, Game Performance, Time Profiler) share one Standard UI and one Analysis Core. Your custom instruments use the same surface as Apple's.
- An "os_signpost interval schema" element auto-generates a modeler for you — for simple cases you write zero Clips code. Just declare the signpost name and which captured metadata maps to which column.
- Modelers can run as expert systems with Clips production rules: `(modeler::found-cause (object-playing-with-matches ?o ?t1) (app-on-fire ?t2) (test (< ?t1 ?t2)) => (assert (cause-of-fire ?o)))`. Use this to detect application-specific anti-patterns automatically.
- **BEST PRACTICE**: write multiple small instruments rather than one mega-instrument. Users drag in only what they need, minimizing recording overhead.
- **GOTCHA**: immediate (live) recording mode breaks for interval-based modelers because the modeler clock can't advance until intervals close. For anything heavy, opt out with the `<limitation>` element and use 5-second buffered mode (up to 10× faster for high-volume signposts).

## Practical Performance Methodology (407)

- Three scenarios: regression hunting, incremental tuning, and full overhaul. Choose tools per scenario.
- **HIDDEN GEM**: write **integration** performance tests, not just unit tests. The whole point is to capture how things compete for CPU at the application level. A unit test for code completion would never have caught Xcode 9's "syntax coloring eats 80% of typing CPU" bug.
- Time Profiler hot tips: enable "Charge ObjC to Callers" to remove `objc_msgSend` clutter, "Hide System Libraries" or set a min-sample threshold (`Call Tree Constraints → 20+ samples`) to focus on your code only.
- **PERFORMANCE**: stack many small wins. "You're going to get your second 30% improvement by stacking 10 separate 3% improvements." Don't dismiss small wins.
- Common patterns: batching/deferring redundant work, caching repeated computations, replacing string-keyed dictionaries with structs (Swift codes up `Equatable`+`Hashable` for free now — see 401).
- The Photos team brought launch from "many seconds + spinners" down to ~450 ms by deferring everything not on screen, loading only low-resolution thumbnails synchronously, and using a sprite-atlas-style "image strip" technique (commonly used in games) for the all-photos grid view to dramatically reduce view count.

## Cocoa Touch Polish (202)

- Swift 4.2 nests previously-global types (`UIApplicationState` → `UIApplication.State`), constants (`NSNotification.Name` is now nested under owning class), and global functions (now methods on relevant types — `UIEdgeInsets.inset(rect:)`).
- All UIKit value types (`CGRect`, `CGPoint`, `CGSize`, `CGVector`, `UIEdgeInsets`, `UIOffset`) now conform to `Codable`. **HIDDEN GEM**: you can JSON-encode a `CGRect` directly with no wrapper.
- Old global string conversion functions (`NSStringFromCGRect`, etc.) move to `NSCoder` — emphasizing they're for archive/encoding intent, not debug printing. For debug, just `print(rect)` — Swift's introspection handles it.

## Build Speed (102, 408, 415)

- Xcode 10 + Swift 4.2 incremental debug builds are typically **2× faster** than Xcode 9 — and Swift target builds alone are **3× faster**. Result of identifying that Swift's whole-module visibility was causing redundant work; the compilation pipeline is now retooled to share work across files.
- **DEPRECATION**: the old "whole-module + no-optimization" stopgap for Debug speed is no longer needed and actively hurts incremental builds. Set Compilation Mode = `incremental` for Debug.
- Optimize-for-Size (`-Osize`) is new and reduces machine code size 10–30% with ~5% runtime cost. Useful for over-the-air cellular limits.
- Memgraph load + save in Memory Debugger is much faster.
- Debug-symbol downloads from the symbol server are 5× faster.
- Test parallelism: Xcode 10 can clone simulators and fan out test bundles for **~4× faster** test runs on multi-core Macs.

## URGENT / Migration Notes

- **OpenGL/OpenCL deprecated** on all Apple platforms (macOS Mojave, iOS 12, tvOS 12). Move to Metal / MPS.
- **macOS Mojave is the last release to support 32-bit at all.** Frameworks like QuickTime and the legacy Apple Java framework are going with it.
- The `automaticallyAdjustsScrollViewInsets` property on `UIViewController` is deprecated. Use `UIScrollView.contentInsetAdjustmentBehavior` instead. (See 235.)
- `CFStreamCreatePairWithSocket*` and `CFSocket` are not yet marked deprecated but Apple wants you off them — they don't get user-space networking benefits or modern connection logic.

## Cross-references

- Network performance: 715, 713, 714 (user-space stack, Network.framework)
- Auto Layout deeper: 220 (full session)
- Memory: 416 (full session)
- Build: 408, 415 (full sessions)
- Energy: 228, 417 (in 2019 templates equivalent)
- Swift compile times: 401 (What's New in Swift)
