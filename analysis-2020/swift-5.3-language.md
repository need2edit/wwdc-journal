# WWDC 2020 — Swift 5.3 & The Language Ecosystem

Swift 5.3 dropped at WWDC 2020 with multi-pattern catch, multiple trailing closures, `@main`, builder inference, runtime size & memory wins, and a noticeably better Xcode-side experience (diagnostics, code completion). The Standard Library opened up — Swift Numerics, Argument Parser, Swift System, Apple Archive, all as packages.

## Sessions Analyzed
- 10170 — What's new in Swift (gateway)
- 10165 — Embrace Swift type inference
- 10167 — Safely manage pointers in Swift
- 10168 — Explore logging in Swift
- 10169 — Swift packages: Resources and localization
- 10147 — Distribute binary frameworks as Swift packages
- 10648 — Unsafe Swift
- 10644 — Use Swift on AWS Lambda with Xcode
- 10217 — Explore numerical computing in Swift
- 10163 — Advancements in the Objective-C runtime
- 10680 — Refine Objective-C frameworks for Swift

## Runtime Performance: Quietly Huge

Three years of focused optimization landed with iOS 14:

### Code Size
A representative system app's Swift rewrite was 2.3× the size of the Objective-C version in Swift 4. With 5.3 it's now under 1.5×. The remaining gap is Swift's safety features (overflow checks, exclusivity enforcement). For a real-world SwiftUI app (MovieSwiftUI), application-logic code size dropped **40%** between Swift 5.2 and 5.3.

### Heap (Dirty) Memory
Swift's startup caches (protocol-conformance lookup tables, ObjC bridging metadata) used to be too large. In iOS 14, **Swift's heap overhead is under 1/3 of the previous release** for apps with a deployment target of iOS 14. (Pre-iOS-14 deployment targets get most of the wins, just not all.)

### The Stack Move

Swift's Standard Library now sits **below Foundation** in the stack. Frameworks underneath ObjC can finally be implemented in Swift — which is why Apple is now using Swift in low-level daemons.

## Language Features (5.2 → 5.3)

### Multiple Trailing Closure Syntax (5.3)

Before:
```swift
UIView.animate(withDuration: 0.3, animations: { ... }, completion: { _ in ... })
```
Now:
```swift
UIView.animate(withDuration: 0.3) {
  // animations
} completion: { _ in
  // completion
}
```
Big enabler for SwiftUI DSL (Gauge with `currentValueLabel`, `minimumValueLabel`, `maximumValueLabel` trailing closures).

**API design tip**: name your method assuming the first trailing closure's label gets dropped. The dropped-label call site must still be readable.

### `@main` Type-Based Entry Points (5.3)

```swift
@main
struct MyTool: ParsableCommand { ... }
```
Replaces `main.swift` for app declarations and command-line tools. Library authors implement a static `main()` method on their protocol/superclass to opt-in users. This is what makes SwiftUI's `App` protocol work as the entry point.

### Multi-Pattern Catch (5.3)
```swift
do { try ... }
catch FetchError.badRequest, FetchError.timeout { ... }
catch let .invalidJSON(reason) where reason.code == 42 { ... }
```
Catch grammar now matches `switch` cases — no more nested switches.

### Synthesized `Comparable` for Enums (5.3)

If your enum has comparable raw values (or no associated values), the compiler synthesizes `<` for free.

### Enum Cases as Static Var/Func Witnesses (5.3)

`case fileCorrupted` can now satisfy a `static var fileCorrupted: Self` protocol requirement. Site-side, both look identical.

### Implicit Self in Closures (5.3)

If `self` is in the capture list (or `self` is a value type), you can drop `self.` in escaping closure bodies. Reduces noise without losing the explicit-capture safety check.

```swift
// Before
{ [self] in self.update() }
// After (5.3)
{ [self] in update() }
```

### Builder DSL Enhancements (5.3)

Function builders (the SwiftUI ViewBuilder mechanism) gained:
- `if let` and `switch` support inside builder bodies
- **Builder inference** — protocol requirements declared with a builder no longer need the `@ViewBuilder` annotation at the top-level call site

### KeyPath as Functions (5.2)

```swift
contacts.sorted(by: \.shoeSize).chunked(by: \.shoeSize)
```
Any function expecting `(Root) -> Value` accepts a KeyPath. Eliminates the duplicate-overload boilerplate for "function or KeyPath?" APIs.

### Better Diagnostics

The Swift compiler's new diagnostic strategy produces far more precise errors with actionable fix-its. SwiftUI errors that were inscrutable in Swift 5.1 ("Generic parameter 'Subject' could not be inferred") now point at the exact problematic site.

### Code Completion Performance

Common SwiftUI completions used to take ~0.5s. In Xcode 12 they take under 0.1s — up to 15× faster. Completion also handles dynamic features better (KeyPath as functions, ternary in dictionary literals).

## New SDK APIs

### `Float16`

IEEE-754 half-precision float, 2 bytes. **Doubles SIMD throughput** on supported hardware (A11+). Caveat: limited precision and range — don't blindly substitute for `Float`.

### Apple Archive

Native modular archive format used internally for OS updates. Multithreaded compression, Finder integration, command-line tool. Idiomatic Swift API.

```swift
let stream = ArchiveByteStream.fileStream(path:filePath, mode: .writeOnly, ...)
let encoder = ArchiveStream.encodeStream(writingTo: stream)
let context = ArchiveSourceCollection(...)
encoder.writeDirectoryContents(...)
```

### Swift System

Strongly-typed wrappers over POSIX system calls. Replaces the messy weakly-typed Darwin overlay. `FileDescriptor`, `FilePath`, `Errno` as proper Swift types with namespaces, defaulted args, error throwing instead of return-value sentinels.

```swift
let fd = try FileDescriptor.open("/tmp/file", .readOnly)
defer { try? fd.close() }
```

Foundation for the Apple Archive Swift API.

### `os.Logger` (See `explore-logging-in-swift.md` Cluster)

A genuinely better `os_log` for Swift, using string interpolation. Critical idea: the message is **never fully stringified** at log-call time. The compiler & logging library produce a heavily optimized representation; full conversion happens only when the message is displayed.

```swift
import os
let log = Logger(subsystem: "com.app", category: "Network")
log.error("Failed to load \(taskID, privacy: .public): \(error)")
```

Privacy options control redaction. Strings/objects are **redacted by default** (`.private`); numerics are public by default. Use `.private(mask: .hash)` to log a stable hash without exposing the data.

Five log levels (debug, info, notice, error, fault) with different persistence:
- **debug**: never persisted, dropped if not streaming. Compiler ensures the message construction code doesn't even run when streaming is off — log verbose data freely.
- **info**: not persisted unless a `log collect` happens shortly after.
- **notice** (default): persisted for days.
- **error**: persisted longer, highlighted yellow in Console.
- **fault**: longest persistence, highlighted red, slowest to log.

Format options: width/precision/alignment, hex/octal/exponential — compile-time, zero runtime cost.

### Swift Numerics (Open-Source Package)

Generic math functions (`sin`, `log` etc.) usable in generic contexts, plus full `Complex` arithmetic with C-layout-compatible storage. Apple is using GitHub Issues/PRs to evolve approximate-equality, arbitrary-precision integers, and decimal floats in the open.

### Swift Argument Parser (Open-Source)

Declarative command-line parser. Combined with `@main`, "hello world" as a command-line tool fits on a slide:

```swift
@main
struct Greet: ParsableCommand {
  @Argument var name: String
  @Option var count: Int = 1
  mutating func run() {
    for _ in 0..<count { print("Hello, \(name)!") }
  }
}
```

### Standard Library Preview Package

A package containing accepted-but-not-yet-shipped standard-library proposals. Lowers the barrier to evolution: proposers can ship implementations as packages without building the full compiler stack.

## Cross-Platform Reach

- New official platforms: Ubuntu (updated), CentOS, Amazon Linux 2, **Windows** (initial support).
- AWS Lambda: open-source Swift runtime; deploy serverless Swift via Xcode.
- The OpenCombine and SwiftCrypto-style efforts are visible in 2020.

## Distribute Binary Frameworks as Swift Packages (10147)

Swift packages can now ship as binary frameworks via the new `.binaryTarget(_:url:checksum:)` declaration with an `.xcframework`. Critical for vendors of closed-source SDKs and for distributing computationally expensive precompiled artifacts.

## Swift Packages: Resources and Localization (10169)

Packages can now bundle resources (asset catalogs, storyboards, JSON, audio, ML models) and localized `.strings` files. Specify in `Package.swift`:

```swift
.target(name: "MyLib", resources: [.process("Resources")])
```

`Bundle.module` (a synthesized helper) lets a package access its bundled resources at runtime.

## Unsafe Swift / Pointers (10648, 10167)

Two related sessions on doing low-level work safely:
- Use `withUnsafePointer(to:)` and friends to scope pointer lifetimes.
- Prefer `UnsafeBufferPointer` over raw pointer + count.
- Memory binding rules for `UnsafePointer<T>.withMemoryRebound(to:capacity:)`.
- Watch for **dangling pointers** when binding to a let property — the compiler may free the storage immediately after the call.

## Type Inference and Code Compactness (10165)

The new diagnostic engine + type inference improvements actually let you write **less explicit type information** without paying the compile-time cost the older inference engine had. The session's motto: don't fight Swift's inference; let it work.

## Cross-References
- [swiftui-2-foundation.md](swiftui-2-foundation.md) — `@main`, multiple trailing closures, builder inference enable SwiftUI's syntax.
- [swiftui-2-foundation.md](swiftui-2-foundation.md) — `Logger` + Console is the recommended replacement for `print`.
- [xcode-tools-testing.md](xcode-tools-testing.md) — Xcode 12 tooling, code completion perf wins.

## Adoption Checklist
- [ ] Bump deployment target where you can — heap memory savings in iOS 14 are biggest at iOS 14+.
- [ ] Replace `print` with `os.Logger`. Set up Console subsystem/category filters.
- [ ] Consider `@main` for any tool-style entry points.
- [ ] Audit closure call sites — multi-trailing-closure syntax can flatten your code.
- [ ] Adopt `Float16` if you have hot-path SIMD math that fits the precision.
- [ ] If shipping a Swift package, add resources + localization with the new declarations.
- [ ] If you need pointers, audit per the Unsafe Swift session.
- [ ] If you compile cross-platform, try the Swift Numerics package for generic math.
