# Performance, Tools & Xcode 14 (2022)

WWDC22's developer tools story is one of measurement and reduction: faster Xcode, faster builds, faster app launch via the new linker and dyld page-in linking, and a comprehensive new toolchain for tracking down hangs across the entire app lifecycle (development, beta, production).

## Sessions covered
- WWDC22-110427 — What's new in Xcode
- WWDC22-110362 — Link fast: Improve build and launch times
- WWDC22-110363 — Improve app size and runtime performance
- WWDC22-110364 — Demystify parallelization in Xcode builds
- WWDC22-110371 — Use Xcode to develop a multiplatform app
- WWDC22-10082 — Track down hangs with Xcode and on-device detection
- WWDC22-10083 — Power down: Improve battery consumption
- WWDC22-110367 — Simplify C++ templates with concepts
- WWDC22-110368 — What's new in Swift-DocC
- WWDC22-110369 — Improve discoverability of your Swift-DocC content
- WWDC22-110370 — Debug Swift debugging with LLDB
- WWDC22-110374 — Get the most out of Xcode Cloud
- WWDC22-110375 — Deep dive into Xcode Cloud for teams
- WWDC22-110361 — Author fast and reliable tests for Xcode Cloud
- WWDC22-110359 — Meet Swift Package plugins
- WWDC22-110401 — Create Swift Package plugins

## Xcode 14 itself (110427)

- **30% smaller download.** Platforms (iOS, watchOS, tvOS, visionOS) and simulators are now downloaded on demand. You can install the bare Xcode and grab platforms only when you need them.
- **Up to 25% faster builds** through better parallelism — see Link Fast (110362) and Demystify Parallelization (110364) for the underlying changes.
- **Linker is up to 2× faster.**
- **TestFlight feedback in the Organizer.** TestFlight comments and screenshots are now visible directly in Xcode without going to App Store Connect.
- **Hangs in the Organizer.** Aggregated hang reports from App Store users with main-thread stack traces (see 10082).
- **Memory debugger** now shows all reference paths in/out of an object, not just shortest path. Useful for understanding why an object is unexpectedly retained.
- **Single-Size icons.** For app icons that don't need pixel-hinting per resolution, drop in one image and Xcode generates the rest.
- **Multiplatform app target.** A single target can deploy to iOS, macOS, iPadOS, watchOS, and tvOS — you describe only what's unique per platform.

### Code completion improvements
- **Whole-initializer completion** — Xcode offers to complete the entire init signature with placeholder values, including codable methods.
- **Italicized parameters with default values** — visually distinguishes "you can skip this" from "you must provide this."
- **Parameter labels show up in completions** — including for SwiftUI modifiers.
- **Improved jump-to-definition** — when a method has multiple definitions (protocol + implementations), the list shows what's different about each result.

### SwiftUI Previews
- **Interactive by default.**
- **Preview variants** — vary color scheme, type size, or device orientation without writing variant configuration code. Side-by-side display.

### Diagnostic dimming
When you fix code, errors visually dim while Xcode reprocesses. This lets you tell which problems are stale vs. fresh — especially valuable during long builds.

## Linker improvements (110362)

### What's new in `ld64`
- **2× faster for many projects.** Multi-threaded copying, parallel LINKEDIT generation, parallel UUID/codesign hashing.
- **Hardware-accelerated crypto** for UUID computation.
- **Better string-handling algorithms** in the exports-trie builder.

### Three little-known link-time options that can dramatically speed up your build:

#### `-all_load`
Tells the linker to load all `.o` files from static libraries up-front. Eliminates the serial processing the linker normally does for archive selectivity. **If you're loading most of the static library content anyway, this is a big win.**

Pair with `-dead_strip` to remove anything the linker pulled in unnecessarily.

**Caveats:**
- If you rely on multiple static libraries with the same symbol names where command-line order matters, don't use `-all_load`.
- Without `-dead_strip`, your binary will grow.

#### `-no_exported_symbols`
Most app main executables don't need any exports — usually nothing looks up symbols in the main binary. Suppress the LINKEDIT exports trie for big speedups. One large app with ~1M exported symbols saved 2–3 seconds per link.

**Caveats:**
- Don't use if your app loads plugins that link back to it.
- Don't use if you use XCTest with your app as host environment.

Use `dyld_info -exports YourApp` to count exported symbols and decide.

#### `-no_deduplicate`
The linker has a slow pass that merges identical functions (mostly C++ template expansions). Debug builds care about speed, not size. **Xcode already passes `-no_deduplicate` for Debug configurations**, but if you have a custom build (non-standard Xcode configs or a different build system), you may be missing it.

### Chained fixups (110362)
A new compact format for binding/rebase fixups in Mach-O binaries. Smaller LINKEDIT, fixup info encoded in DATA. **Available since iOS 13.4 runtime.** If your deployment target is 13.4+, you get smaller binaries automatically.

### Page-in linking
A new dyld feature: instead of dyld applying all fixups at launch, the kernel does it lazily on page-in. **Reduces dirty memory and launch time. DATA_CONST pages stay clean and can be evicted.** Requires chained fixups → requires iOS 13.4+ deployment target.

### Static vs. dynamic library guidance
- Don't use static libraries for code under active development — every change triggers a full archive rebuild.
- Too many dylibs slows launch (more files to load, more fixups). Too many static libraries slows build.
- The "sweet spot" shifted in Xcode 14 because `ld64` got faster — you can use more static libraries than before.

### Two new tools (macOS only, also work for simulator/Catalyst)
- **`dyld_usage`** — trace dyld activity for a launching app. Shows total launch time, fixup time, init time.
- **`dyld_info`** — inspect binary fixups and exports, both on disk and in the dyld shared cache.

## Runtime size & speed wins (110363)

These are all transparent — no API changes, no code changes:

### Swift protocol checks
The Swift runtime used to spend up to 4 seconds at launch computing protocol-conformance metadata for apps with many protocols. **Now precomputed at dyld closure time.** Apps see launch times cut by hundreds of ms; some apps see launches halved.

### `objc_msgSend` stubs (Xcode 14)
Each `objc_msgSend` call site used to need 12 bytes (instructions to load the selector + the call). The compiler now generates a per-selector stub function that's shared by all call sites using that selector. **Up to 2% binary size win.** Use `-objc_stubs_small` linker flag to opt into the smallest possible variant (slightly slower at runtime).

### Smaller retain/release calls (deployment target iOS 16)
Custom calling convention for `objc_retain`/`objc_release` eliminates redundant register-mov instructions before each call. **Another ~2% binary size win.**

### Faster autorelease elision (iOS 16 runtime)
The pre-iOS-16 trick was to encode a "magic instruction" after each `objc_retainAutoreleasedReturnValue` call. The runtime would load that instruction *as data* and compare it. This is bad for CPU caches. The new technique compares saved return-address pointers instead. **Faster, and the magic-instruction byte goes away → smaller code too.**

## Hang detection — three phases (10082)

### 1. At-desk development: Thread Performance Checker
A new diagnostic in Xcode's scheme settings (Diagnostics tab). Detects two leading causes of hangs **without active tracing**:
- **Priority inversions** — a high-priority thread waiting on a lower-priority thread.
- **Non-UI work on the main thread** (e.g., synchronous network or disk I/O).

The Thread Performance Checker pops alerts directly in the Issue Navigator while you're using the app.

### 2. Active tracing: Time Profiler with hang labels
Time Profiler in Xcode 14 now detects and labels hangs in the timeline with their durations. **Triple-click a hang interval to filter all detail views to events during that hang.** New standalone "Hang Tracing" instrument can be added to other trace documents.

### 3. Beta testing: on-device hang detection
A new toggle in iOS 16's `Settings → Developer → Hang Detection`. Real-time notifications when the app hangs above a configurable threshold (250ms minimum, default higher). Works without Xcode connected. Available for development-signed and TestFlight apps.

Diagnostics include text-based hang logs and tailspins (open in Instruments). **Symbolicate the text logs with the dSYM on your Mac.**

### 4. Production: Hangs report in Organizer
Hangs reports in the Xcode Organizer aggregate main-thread stack traces from users who consented to share App Analytics. Sorted by user impact. Each signature shows OS-version and device breakdown — critical for triaging "is this 15.3-only?"

**Submit your app with symbol information for one-click jump-to-source from the stack trace.** Apple stores this securely and doesn't share it.

### Notification setup
Click the notification button at the top-right of the Regressions view in the Organizer. Xcode will alert you to sudden rises in your app's hang rate after each release.

## Network responsiveness (10078)

Network latency is the dominant factor in app responsiveness — *not* bandwidth. Bandwidth diminishing returns kick in past 4 Mbps; latency improvement is linear.

### Adopt
- **HTTP/3 / QUIC** — `URLSession` and `Network.framework` use it automatically when servers support it.
- **TLS 1.3.**
- **Connection migration** — set `multipathServiceType = .handover` on your `URLSessionConfiguration` to seamlessly migrate from Wi-Fi to cellular without dropping connections.
- **QUIC datagrams** — for custom protocols on UDP. Reacts to network congestion (unlike raw UDP) which keeps latency low.

### `networkQuality` tool (macOS Monterey+)
Run `networkQuality` to measure RPM (round trips per minute) — the inverse of latency. The metric exposes buffer-bloat in your servers and ISPs. **Apple has been working with the IETF on L4S** (Low Latency Low Loss Scalable) — opt in via `Settings → Developer → L4S` on iOS 16.

### Server tuning lessons
A streaming-server example: Apple reduced HTTP/TLS/TCP buffers from 4MB/256KB/4MB to 256KB/16KB/128KB. Result: video skip-ahead became instant instead of multi-second rebuffering. Big buffers ≠ better.

## Battery consumption (10083)
- Profile with the **CPU Profiler** and **Network instruments** in Instruments.
- New `MetricKit` `MXBackgroundExitData` reports background termination reasons (CPU resource, memory pressure, etc.).
- Heavy GPS use, repeated network requests, and idle wake-ups are the top battery killers.

## Multiplatform Xcode target (110371)
A single target can build for multiple platforms. Filter by platform:
```swift
#if os(iOS)
// iOS-specific
#endif
```
Or use destination availability checks. Removes the need for sibling targets that have to keep settings synchronized.

## Swift Package plugins (110359, 110401)
- **Command plugins** — invoke from Xcode menu or `swift package` CLI. Generate documentation, format code, run linters.
- **Build tool plugins** — inject build steps that generate code or process resources during the build. Sandboxed.

Plugins are pure Swift — no shell scripts to maintain. Open-source tools (formatters, linters) are available right inside Xcode.

## Swift-DocC (110368, 110369)
- **Now supports Objective-C and C** in addition to Swift.
- **Ships with Swift.org open-source** — same generator across platforms.
- **Improves discoverability** with metadata articles, technology overviews, and tutorial groupings.

## Best practices
- **BEST PRACTICE**: Build and submit your app to the App Store with symbol information. The Organizer's hang reports become dramatically more useful.
- **BEST PRACTICE**: Enable on-device hang detection during beta testing. Network conditions only show up in the field.
- **BEST PRACTICE**: For C++-heavy projects on custom build systems, ensure Debug builds pass `-no_deduplicate` to the linker.
- **PERFORMANCE**: Use `dyld_info -exports YourApp` before considering `-no_exported_symbols` — only useful if exports trie is large (10k+ symbols).
- **PERFORMANCE**: Set deployment target to iOS 13.4+ to enable chained fixups → smaller binaries + faster launch via page-in linking.
- **PERFORMANCE**: Set deployment target to iOS 16 to get smaller `objc_retain`/`objc_release` calls (~2% binary size).
- **HIDDEN GEM**: Reducing server buffer sizes can dramatically improve responsiveness — bigger isn't better. Test with `networkQuality`.
- **HIDDEN GEM**: Compiler-generated stubs for `objc_msgSend` save ~2% binary size with no source changes — enabled automatically in Xcode 14.
- **DEPRECATION**: `UIDevice.name` no longer returns the user's custom name (privacy) — gets the model name instead. Custom name requires entitlement.

## Cross-references
- Background tasks (10142) for SwiftUI uses Swift Concurrency from the language session (110354).
- Hangs in production link to App Analytics (10044) trends.
- Power and Performance API (Power and Performance API session) lets you integrate hang reports into your own dashboards.
- Build improvements pair with multiplatform target (110371) for code-share workflows.
