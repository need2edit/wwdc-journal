# Concurrency, Performance & Energy — WWDC 2015 Analysis

**Sessions covered:** 718 (Building Responsive and Efficient Apps with GCD), 226 (Advanced NSOperations), 707 (Achieving All-day Battery Life), 708 (Debugging Energy Issues), 230 (Performance on iOS and watchOS), 412 (Profiling in Depth), 413 (Advanced Debugging and the Address Sanitizer), 712 (Low Energy, High Performance: Compression and Accelerate), 711 (Networking with NSURLSession), 232 (Best Practices for Progress Reporting)

## Headline

WWDC 2015 was about doing *less* work, doing it *later*, and doing it *more efficiently*. iOS 9 promises +1 hour of battery life across existing devices through OS-level optimization. Developers got: Quality of Service (QoS) classes propagated through GCD, NSOperation patterns codified into reusable conditions/observers, the new Energy gauges in Xcode, the Address Sanitizer for memory bugs, and Compression/Accelerate framework expansions.

## Quality of Service Classes (718)

Four classes, in priority order:

| QoS | Purpose | Examples |
|---|---|---|
| `userInteractive` | UI rendering, gesture tracking | Main thread (set automatically); animation drivers |
| `userInitiated` | User waiting, can't proceed | Loading the photo they tapped, decoding selected mail |
| `utility` | User aware, NOT blocking | Magazine issue download with progress bar |
| `background` | User unaware | DB compaction, analytics, prefetch, log rotation |

- The system uses QoS to choose scheduling priority, I/O priority, timer coalescing, and CPU efficiency mode (throughput vs. energy).
- **PERFORMANCE CRITICAL on the new fanless MacBook**: when thermals tighten, the system squeezes lower-QoS work first. Misclassifying background work as user-initiated can starve the UI thread.
- **HIDDEN GEM**: `dispatch_async` propagates the calling thread's QoS to the destination block automatically. The MAIN thread is `userInteractive` by default; propagation translates to `userInitiated` in destination blocks (so you don't accidentally call frame-rate-critical code on a background queue).
- For long-running work spawned from main, wrap your initial async block in `dispatch_block_create_with_qos_class(.utility, ...)` — the QoS sticks to all downstream work that the block spawns.
- **Detached blocks** (`dispatch_block_create(.detached, block)`) opt out of QoS propagation AND activity tracing. Use for unrelated maintenance.

### Priority Inversion Resolution (718)

- Asynchronous: a high-QoS block enqueued behind a low-QoS block on a serial queue causes GCD to **temporarily raise** the entire queue's QoS to clear the inversion.
- Synchronous: a `dispatch_sync` from a high-QoS thread onto a serial queue with low-QoS work pending raises the worker's QoS while the waiter waits.
- **WARNING**: `dispatch_semaphore_wait` and `dispatch_group_wait` do NOT participate in inversion resolution — there's no concept of ownership for the system to follow. **Use `dispatch_block_wait` when you need this behavior.** Audit your code: blocked semaphores are a major energy bug source.

### Thread Explosion (718)

The classic GCD pitfall: dispatching many blocks to a concurrent queue, each of which blocks on I/O, each of which causes GCD to spawn a new thread until the system limit. Then any further `dispatch_sync` to the queue **deadlocks**.

Mitigations:
- Use serial queues by default. Profile and selectively go concurrent.
- Use `dispatch_apply` for parallel iteration (managed parallelism).
- Use `NSOperationQueue` with `maxConcurrentOperationCount` set.
- Use a counting semaphore to gate submissions.

## NSOperation Patterns (226)

The WWDC app itself is the canonical example of an operation-driven application. Five core ideas:

1. **Operations as units of complex behavior** — wrap UI presentation (alerts, login sheets, video player) AND networking (CK requests, file downloads) AND application logic in operations so they participate in dependency graphs.
2. **Generated dependencies** — an operation that needs auth automatically generates a dependency on a "verify auth" operation, which in turn generates "verify logged in." Removing one line from `dependencyForOperation` removes the auth requirement everywhere in the app.
3. **Conditions** — protocol describing prerequisites: "this operation needs network reachability," "this needs permission to access photos," "this is mutually exclusive with other operations of type X." The condition system can produce its own dependencies AND extend readiness AND express mutual exclusivity.
4. **Observers** — protocol for getting lifecycle callbacks: started, finished, produced (a new operation). Observers we ship in the sample code: `TimeoutObserver`, `BackgroundObserver` (auto-runs `beginBackgroundTask` for the duration), `NetworkActivityObserver` (auto-shows the status bar spinner — and stays correct when multiple operations overlap).
5. **Cross-queue dependencies** for **mutual exclusivity**: enforce "only one alert at a time" by making each new alert operation depend on the previous one, regardless of queue. Even across queues, dependencies hold.

**HIDDEN GEM**: The official sample code is shipped under "Advanced NSOperations" — the same operation classes used inside the WWDC app, ready to drop into your project. Even years later this is still the gold-standard pattern for serializing async work across an iOS app.

**Composition pattern**: an `ImportDataOperation` internally creates a download operation and a parse operation, wires them, and exposes a single operation to the rest of the app. The outer app doesn't care about the chain.

**HIDDEN GEM**: cancellation is cooperative. Calling `cancel()` only flips a Boolean; an in-progress operation must check `isCancelled` and bail. The race is real: you may call `cancel()` after the operation has finished — operations cannot transition from finished to cancelled.

## Energy (707, 708)

Energy = Power × Time. Optimizing one without the other is a trap.

### iOS 9 OS-level changes (707)

- Reduced sleep timers, fewer CPU wakes when idle.
- **Face-down detection**: an incoming notification with the screen face-down processes minimally — no display wake.
- Background work deferred until plugged in (when possible).
- Networking deferred to Wi-Fi when possible.
- Improved CPU power management with much lower transition overhead.
- LTE optimizations for Apple's own radios.

### Per-app energy display

Settings → Battery now shows per-app screen-on time AND background time. **DOCS MISS THIS**: a single bad background activity can be visible to users in this UI. Audit yours.

### Low Power Mode (707)

User-toggle setting that:
- Caps CPU
- Disables background app refresh
- Disables discretionary downloads
- Disables mail fetch

Your app should detect Low Power Mode (`ProcessInfo.processInfo.isLowPowerModeEnabled` and `NSProcessInfoPowerStateDidChange` notification) and reduce its own non-essential work.

### Three pillars (707)

1. **Do less work.** No polling. Computers operate at microsecond scale; humans at second scale. Don't busy-loop.
2. **Do work later.** Defer with `URLSession` background sessions, `BackgroundTasks` (in iOS 9, the `NSURLSession` background config), Push priorities (PushKit can mark "low priority").
3. **Do work efficiently.** When you must work, batch. Use the most efficient APIs (Accelerate, vDSP, BLAS, MetalPerformanceShaders).

### The 5–10% rule (707)

On a long time scale, the average system load needs to be **between 5% and 10%** to achieve all-day battery life. Just turning the display on costs ~5% — your software gets the other 5%. On short time scales burst to 100% with priorities; the system schedules.

### Networking energy (707)

The radio is the biggest variable cost. A single 1KB upload can keep the cellular radio active for **2–10 seconds** (the post-transmission keep-alive). **Coalesce networking** — bundle pending background work into one transmission. Push notifications are inbound (cheap); use silent pushes to wake apps for batched work, not polling.

### Location energy (707)

- Precise GPS is expensive. Imprecise (Wi-Fi/cell-tower) is much cheaper.
- iOS 9's new `requestLocation()` does start+stop in one call at the requested precision — you can't accidentally leave it running.
- `allowsBackgroundLocationUpdates` defaults to false; only set to true when actively running a session.
- For workout apps: `CLLocationManager.allowsDeferredLocationUpdates(...)` lets the hardware buffer location for hours and call you back in batches — most of the system asleep.

### Background work energy (707)

- `beginBackgroundTask(...)` keeps your app awake for up to ~3 minutes. ALWAYS pair with `endBackgroundTask` on every code path.
- Use background `URLSession` for offloading network. Wait on it via callbacks; don't keep your app alive.
- Push notifications: use PushKit and tag low-priority pushes for batched delivery.

### New tools (707, 708)

- **Energy gauge** for iOS in Xcode (was OS X only). Live during debugging.
- **Location instrument** added to Instruments.
- New iOS Energy Guide and updated OS X Energy Guide on the developer site.

## Compression & Accelerate (712)

- **Compression framework**: streaming compress/decompress with LZ4, LZFSE, LZMA, ZLIB. **LZFSE is Apple-tuned** — better ratio than LZ4, faster than LZMA, energy-efficient. **HIDDEN GEM**: it's also how iOS 9 itself compresses on disk; using it gives you content cache benefits.
- Accelerate / vDSP additions for audio, signal processing, image manipulation. Each generation tuned for the chip's vector unit.
- vImage gets new APIs for image processing chains.
- BNNS (Basic Neural Network Subroutines) — neural network primitives accelerated for CPU. Predates Core ML by a year.

## Networking with NSURLSession (711)

- App Transport Security (ATS) is on by default in iOS 9 — TLS 1.2 with forward secrecy or you get an error. Specific exceptions go in `NSAppTransportSecurity` in Info.plist.
- **HIDDEN GEM**: ATS is per-domain; you can grant exceptions to specific domains while keeping the rest secure.
- HTTP/2 supported via NSURLSession transparently.
- WebSocket NOT yet first-class (lands in 2016).

## Address Sanitizer (413)

- New in Xcode 7: `-fsanitize=address` instrumentation catches buffer overflows, use-after-free, double-free, use-after-return, and stack-buffer-overflow at runtime with detailed reports.
- ~3x slowdown — turn on in your Test scheme, leave off in Release.
- Catches the bugs that are notoriously hard to reproduce in normal debugging.

## NSProgress for Reporting (232)

- New for iOS 9: `NSProgress` is composable across nested operations.
- Implicit child binding: a parent `NSProgress` becomes-current, a child progress is created during that span and inherits.
- Cancelable, pausable, resumable from outside.
- Localized description: "5 of 100" automatically formatted.
- Used by ODR (`NSBundleResourceRequest.progress`), URLSession, and your own code via `Progress.discreteProgress(withTotalUnitCount:)`.

## Cross-references

- QoS (718) connects to NSOperations (226) — operations propagate QoS through their dependency graph.
- Energy (707) is enforced by Multitasking (212): if your background work hangs, the system kills you to free resources.
- ATS (711, 703) is part of the broader privacy story.
- Address Sanitizer (413) found bugs that performance work (412) helps you avoid via better data structure choice.
