# Swift 4.2 — WWDC 2018 Analysis

**Sessions covered:** 401 (What's New in Swift), 406 (Swift Generics, Expanded), 411 (Getting to Know Swift Package Manager), 415 (Behind the Scenes of the Xcode Build Process), 408 (Building Faster in Xcode), 412 (Advanced Debugging with Xcode and LLDB), 410 (Creating Custom Instruments §Clips/expert systems), 102 (Platforms State of the Union §Swift)

## Headline

Swift 4.2 is the **last waypoint before Swift 5's binary stability**. The biggest shipping wins are 2× faster Debug builds (and ~3× faster Swift target builds), the new `-Osize` optimization mode (10–30% machine-code reduction), `String` shrinking from 24 to 16 bytes (with a new small-string optimization that holds up to 15 bytes inline), and a new ARC calling convention that eliminates redundant retain/release pairs. Language-side: `CaseIterable`, conditional conformances in the standard library (`Array: Equatable where Element: Equatable` etc.), synthesized `Hashable` for enums with associated values, the new `Hasher` API, generic random-number APIs, `#warning` / `#error` / `#if hasAttribute(...)` directives, and tightened Implicitly Unwrapped Optional semantics.

## Build Speed (102, 408, 415)

- Xcode 10 + Swift 4.2 hits **2× Debug-build improvement** on representative mixed Obj-C/Swift apps. Pure Swift target builds: **~3×**.
- The retooling: Apple identified that Swift's whole-module visibility was causing _redundant_ work across files. The pipeline now shares more work and parallelizes per-file better.
- **DEPRECATION** of pattern: the "whole-module compilation + no optimization" hack people used as a stopgap for fast Debug builds is no longer needed and actively hurts incremental builds. Restore Compilation Mode = `incremental` for Debug.
- Build settings now cleanly separate **Compilation Mode** (whole-module vs. incremental) from **Optimization Level** (none, fast, smaller-binary).

## -Osize: Optimize for Size (401, 102)

- New optimization level. Swift's static knowledge means it can be aggressive about inlining, devirtualization, etc., which trades some code size for speed.
- `-Osize` dials these back: **10–30% smaller machine code** with ~5% runtime cost.
- Use case: cellular over-the-air install limits (currently 200 MB), apps where startup matters more than steady-state CPU.
- Only affects machine code, not assets — full app size depends on bundled images, ML models, etc.

## ARC Calling Convention Win (401)

Old convention (Swift 4.1):
- A function call to `f(obj)` _passed ownership_ — caller +1, callee responsible for releasing.
- This required intermediate retain/release pairs for chained calls (`a(x); b(x); c(x)`).

New convention (Swift 4.2):
- Caller retains the lifetime — no obligation transfer. Intermediate retain/release pairs disappear.
- Code-size win + runtime win. **PERFORMANCE**: rebuilding without code changes nets typical apps a 1–2% runtime speedup and several percent code-size shrink.

## String Halved + Small-String Optimization (401)

- `String` is now 16 bytes (was 24).
- Strings ≤ 15 bytes are stored inline — no heap allocation for short strings (file extensions, single-char labels, dictionary keys).
- Combined with Swift 5's UTF-8-native String (transitioning), this means string-heavy code sees significant memory and CPU wins.

## CaseIterable (401)

```swift
enum Direction: CaseIterable { case north, south, east, west }
Direction.allCases   // [north, south, east, west]
```
- Eliminates the boilerplate `static let allValues: [Self] = [...]` that you forgot to update when adding a new case.
- **HIDDEN GEM**: works for any enum without associated values (or with associated values where you write `allCases` manually). Combined with `RawRepresentable`, the result is exhaustive `forEach` / picker generation in 0 lines of glue.

## Conditional Conformances Land in the Stdlib (401, 406)

Now Equatable / Hashable / Encodable / Decodable propagate through Array, Optional, Dictionary, Set _automatically_:

```swift
let outer: [[Int?]] = [[1, nil], [2, 3]]
print(outer == outer)   // works
let setOfArrays: Set<[String]> = [["a"], ["b"]]   // works
```

In Swift 4 this required boilerplate `extension Array: Equatable where Element: Equatable { ... }` per app. Now it's standard.

## Synthesized Equatable / Hashable for Enums with Associated Values (401)

```swift
enum Either<L, R> { case left(L); case right(R) }
extension Either: Equatable where L: Equatable, R: Equatable { }   // 1 line, no body needed
extension Either: Hashable where L: Hashable, R: Hashable { }       // 1 line
```
The compiler synthesizes `==` and `hash(into:)` based on the cases and their associated values. Combined with conditional conformances, this is huge for compactly-defined sum types.

## New Hasher API (401)

Old:
```swift
var hashValue: Int {
  return name.hashValue ^ state.hashValue   // bad: weak combine, fixed seed
}
```

New:
```swift
func hash(into hasher: inout Hasher) {
  hasher.combine(name)
  hasher.combine(state)
}
```

- The `Hasher` is seeded with a per-process random seed, defeating algorithmic-complexity DoS attacks (attacker can't precompute hash collisions for your dictionaries).
- Higher-quality combining than typical XOR or "math from the internet."
- **GOTCHA**: dictionary iteration order and `hashValue` are no longer deterministic across runs. Set `SWIFT_DETERMINISTIC_HASHING=1` in the scheme to disable for tests that depend on order.

## Generic Random APIs (401)

- All numeric types: `Int.random(in: 1...6)`, `Double.random(in: 0..<1)`. Uniformly distributed (Swift handles the modulo-bias problem internally; `arc4random() % 6` was wrong).
- Collections: `array.shuffled()`, `array.randomElement()` (returns optional — empty arrays return nil).
- `RandomNumberGenerator` protocol — supply your own seeded RNG for reproducible tests by passing `using:` parameter to any of the above.

## New Build-Time Directives (401)

- `#warning("FIXME")` and `#error("Not yet implemented for Linux")` — show up in Xcode's issue navigator at compile time.
- `#if canImport(UIKit)` — replaces the awkward `#if os(iOS) || os(tvOS) || os(watchOS)`.
- `#if targetEnvironment(simulator)` — replaces the `#if (arch(i386) || arch(x86_64)) && os(iOS)` incantation.

## Implicitly Unwrapped Optionals: Tightened Semantics (401)

The mental model is now strict: an IUO is **not a type**, it's an **attribute on a declaration**. The compiler first tries to type-check the value as a plain optional; only if that fails does it force-unwrap.

```swift
func f() -> String! { ... }
let x: Any = f()    // x is String? (optional, no force unwrap)
let y: String = f() // forced unwrap because Any wouldn't fit
```

Edge case: in Swift 4 you could `typealias` an IUO underlying type and use it inside a generic, getting confusing behavior. Swift 4.2 gives a compile-time warning and treats it as the underlying optional.

## Tighter Memory Exclusivity Checks (401)

- The Swift 4 enforcement caught some access conflicts at compile and runtime. Swift 4.2 catches more of the generic-closure cases that previously slipped through.
- New: opt-in **runtime** exclusivity checking in Release builds (overhead ~couple of percent). Default off; useful for pre-release builds to catch races before shipping.

## Generics: Extended Coverage (406)

- Conditional conformances: now usable in your own libraries, not just stdlib (`extension MyContainer: Codable where Element: Codable`).
- Recursive constraints (`associatedtype X where X.X == Self`) — used in `Collection.SubSequence: Collection`.
- More complete protocol composition; fewer edge cases.

## Swift Package Manager (411)

- **Package.swift schema 4.2** brings Swift language version per target, system-library dependencies, and improved package collections.
- Build-system improvements: parallelization fixes, deterministic build outputs.
- Apple-supported on macOS and Linux. Xcode integration is still 2019/Catalyst-era; in 2018 SPM is primarily a CLI workflow.

## Swift Open Source: Forums + Community CI (401)

- Mailing lists retired; **Swift Forums** (Discourse-based) are the primary discussion venue. Lower friction for proposal review.
- Community-hosted CI nodes for non-Apple platforms (Linux distros, etc.) are now part of swift.org. Easier to add Swift to a new platform.
- The Swift Programming Language book moved to docs.swift.org for canonical hosting.

## What Comes Next (Swift 5 in 2019)

- Swift 4.2 is explicitly the on-ramp to Swift 5 ABI stability. Swift 5 ships the runtime in the OS itself; apps no longer bundle it. **PERFORMANCE**: ~30 MB shaved off App Store download for typical Swift apps; no more "Swift launch tax."
- Migrate to Swift 4.2 in 2018 to reduce Swift-5-migration friction. Xcode 10 is **the last release** that supports Swift 3 compatibility mode.

## DEPRECATION (401)

- Swift 3 mode supported one more release; Xcode 11 will only have Swift 4 / 4.2 / 5 modes.
- Old `print`-style debug helpers like `NSStringFromCGRect` should move to Codable-based debug printing or `String(describing:)`.

## Cross-references

- Build settings deep-dive: 415 (Behind the Scenes of the Xcode Build Process).
- LLDB improvements (faster startup, better variable access): 412.
- Swift on Linux / server-side: outside Apple's main session track but supported in 4.2; check the Swift forums.
- Hashable in practice with custom keys: see 229 (Using Collections Effectively).
