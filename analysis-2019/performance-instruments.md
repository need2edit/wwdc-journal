# Performance, Instruments & Battery — WWDC 2019 Analysis

**Sessions covered:** 423 (Optimizing App Launch), 411 (Getting Started with Instruments), 421 (Modeling in Custom Instruments), 414 (Developing a Great Profiling Experience), 417 (Improving Battery Life and Performance), 422 (Designing for Adverse Network and Temperature Conditions), 419 (Optimizing Storage), 429 (LLDB: Beyond "po"), 412 (Debugging in Xcode 11)

## Headline

The iOS 13 / Xcode 11 cycle introduced **MetricKit** (real-world telemetry from production users), **XCTest performance metrics** (CI-friendly perf tests), the **Xcode Metrics Organizer** (aggregated production numbers), and a brand-new **App Launch instrument template**. dyld 3 ships for third-party apps, slashing launch time.

## App Launch Anatomy (423)

Launch is a 6-phase pipeline. **Goal: render first frame in 400 ms** (so it's ready when the launch animation completes).

1. **System Interface (`dyld`)** — dynamic linker loads frameworks. **PERFORMANCE**: dyld 3 caches dependencies for warm launches, dramatic speedup. **Avoid linking unused frameworks** (hidden cost). **Avoid `dlopen`/`Bundle.load`** (forfeits the cache). **Hard-link** all dependencies.
2. **`libSystemInit`** — fixed cost, nothing for you to do.
3. **Static Runtime Initialization** — Objective-C `+load` and Swift static initializers. **BEST PRACTICE**: avoid `+load`; move work to `+initialize` (lazy). Frameworks you depend on can sneak in static init too.
4. **UIKit Init** — `UIApplication`/`UIApplicationDelegate` instantiated.
5. **Application Init** — `application(_:didFinishLaunchingWithOptions:)` (or scene `willConnect` if using UIScene). **BEST PRACTICE**: defer everything not required for first frame.
6. **First Frame Render** — view creation, layout, draw, commit, render.
7. **Extended Phase** (optional) — async data loading; UI must be interactive even if some content is placeholders.

## Cold vs Warm vs Resume (423)

- **Cold launch** — after reboot or eviction. App not in memory. Slowest, most variable.
- **Warm launch** — process spawned, but app code already in dyld cache. Faster.
- **Resume** — app already running, user comes back. Sub-second. **Don't conflate resumes with launches** in measurements.

## Reducing Launch Variance for Measurements (423)

1. Reboot device, wait a few minutes for boot work to settle.
2. Turn on airplane mode (or stub network calls). Network is the #1 source of variance.
3. Sign out of iCloud or use a stable test account.
4. Use **release builds** — Profile scheme in Xcode rebuilds in release.
5. Repeat warm launches (consistent state).
6. Use stable test data sets.
7. Test on the **oldest supported device** — performance characteristics differ wildly from newer hardware.

## XCTest Performance Tests (423, 417)

```swift
func testLaunchPerformance() {
    measure(metrics: [XCTApplicationLaunchMetric()]) {
        XCUIApplication().launch()
    }
}
```

Other metrics: `XCTCPUMetric`, `XCTMemoryMetric`, `XCTStorageMetric`, `XCTClockMetric`, `XCTOSSignpostMetric`. Run in CI to detect regressions before they ship. **HIDDEN GEM**: Xcode 11 saves baselines per-device, so an iPhone XS regression is judged against its own baseline, not an iPhone 7 baseline.

## MetricKit (417)

`import MetricKit` to receive real-world performance/battery telemetry from production users.

- `MXMetricManager.shared.add(self)` — your delegate gets `MXMetricPayload` objects daily.
- Categories: `cpuMetrics`, `gpuMetrics`, `memoryMetrics`, `displayMetrics` (avg pixel luminance), `applicationLaunchMetrics`, `applicationResponsivenessMetrics` (hangs), `diskIOMetrics`, `networkTransferMetrics`, `cellularConditionMetrics`, `applicationExitMetrics` (added later).
- **HIDDEN GEM**: average pixel luminance (APL) directly correlates to OLED battery drain. Lighter UI → more energy. Dark mode is a measurable battery win on OLED devices.
- Xcode Organizer's Metrics tab shows aggregated MetricKit data across the App Store user base.

## App Launch Instrument Template (411, 423)

New in Xcode 11. Profile → App Launch. Walks you through the launch phases visually with timestamps. Highlights:
- Time spent in each phase.
- "Spinning" red bands on the main thread (Mac wait cursor / iOS UI hang).
- OS_signpost tracks for code you've instrumented.

## Time Profiler Essentials (411)

- Click + drag to filter events by time range.
- **Heaviest stack trace** in the Extended Detail view: the call chain that appeared in the most samples.
- Option-click disclosure triangle in call tree → auto-expand until a control flow branch.
- Click any frame → "Open File in Xcode" jumps to the source line.
- **PERFORMANCE INTUITION**: Time Profiler samples ~1000 times/second. A function appearing in 50% of samples means 50% of CPU time, not 50% of calls.

## OS Signposts for Custom Instrumentation (411, 421)

```swift
let log = OSLog(subsystem: "com.example.app", category: .pointsOfInterest)
let id = OSSignpostID(log: log)
os_signpost(.begin, log: log, name: "ImageDecode", signpostID: id)
// ... work ...
os_signpost(.end, log: log, name: "ImageDecode", signpostID: id)
```

These show up in the Points of Interest instrument (and appear automatically in `XCTOSSignpostMetric` measurements). **HIDDEN GEM**: signposts have negligible overhead in release builds when no profiler is attached — leave them in.

## Custom Instruments (421)

- Build your own `.instrument` packages in Xcode using a declarative XML schema.
- Define your data schema, modeler, graph view, and CLI input.
- Distribute to your team for domain-specific profiling (e.g., an "AppleMaps Tile Loading" instrument).

## Battery Best Practices (417)

- **Networking is the biggest battery drain** — each request keeps the radio on for ~10s afterwards. Coalesce requests; use `URLSessionConfiguration.discretionary = true` to defer non-urgent work.
- **Display average pixel luminance** is OLED-specific. Dark mode → measurable battery wins.
- **Background location** — use significant location changes when you don't need second-by-second accuracy. Use deferred location updates.
- **Hangs** — anything above 250ms on the main thread is a "hang." MetricKit ships a histogram per app per day in production.

## Designing for Adverse Conditions (422)

- **Network Link Conditioner** in System Preferences (download from Hardware IO Tools for Xcode) — simulate 3G, Edge, lossy networks.
- **Thermal state**: `ProcessInfo.processInfo.thermalState` returns `.nominal`/`.fair`/`.serious`/`.critical`. **BEST PRACTICE**: down-rate frame rate, lower image quality, defer background work when serious or critical.
- `NSProcessInfoThermalStateDidChangeNotification` for live updates.
- **Low Power Mode** — `ProcessInfo.processInfo.isLowPowerModeEnabled` and `.NSProcessInfoPowerStateDidChange`. Disable visual effects, slow background syncing.

## LLDB: Beyond `po` (429)

- `po`: pretty-print using `CustomDebugStringConvertible.debugDescription` (or `description`).
- `p`: print — uses Swift's `_debugDescription` for richer output, no need for the `lldb` Objective-C bridge.
- `v` (or `frame variable`): instant print — does NOT execute code, just reads memory. Much faster than `po` for known variables. **HIDDEN GEM**.
- `expression --interpret-then-jit` (or `e -X`): start interpreted, fall back to JIT if needed. Faster for simple expressions.
- `b -E swift` to break on uncaught Swift errors.
- Custom data formatters via `type summary add` for your own types in `~/.lldbinit-Xcode`.

## Storage Optimization (419)

- New iOS 13 storage-optimization framework: `URLResourceKey.canonicalPathKey`, `volumeAvailableCapacityForOpportunisticUsageKey`.
- **`storageBudget`** (deprecated) → use `URLSessionConfiguration.discretionary` for downloads.
- iOS 13 introduced **Compressed PDF**, **HEIF/HEIC** as system formats. Use `CGImageDestinationCreateWithURL(url, kUTTypeHEIC, ...)` for 50% smaller photos.

## Cross-references

- Optimizing App Launch is THE follow-up to dyld 3 announcement: 423.
- Storage and discretionary downloads connect to background tasks: 707.
- Dark mode → battery via APL: 214 + 417.
