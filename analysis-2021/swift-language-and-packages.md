# Swift Language, Packages & Foundation (WWDC 2021)

## Sessions covered
- WWDC21-10192 — What's new in Swift
- WWDC21-10109 — What's new in Foundation
- WWDC21-10216 — ARC in Swift: Basics and beyond
- WWDC21-10253 — Write a DSL in Swift using result builders
- WWDC21-10256 — Meet the Swift Algorithms and Collections packages
- WWDC21-10197 — Discover and curate Swift Packages using Collections

## Best practices

- **Adopt `@resultBuilder` (formalized as SE-0289)** for any DSL-shaped API. SwiftUI showed the pattern; now you can use it for building HTML, queries, command-line composition, etc. (WWDC21-10253).
- **Codable Enums with associated values now synthesize automatically.** Drop the manual `init(from decoder:)`/`encode(to:)` boilerplate for two-case enums with payloads (WWDC21-10192).
- **Use `Deque` instead of `Array` for FIFO queues** — O(1) append AND prepend. From the Swift Collections package (WWDC21-10256).
- **Use `OrderedSet`/`OrderedDictionary` for stable iteration order** — Dictionary's order is not specified; OrderedDictionary preserves insertion order with Set-like fast lookup (WWDC21-10256).

## Hidden gems

- **Static member chains in protocols**: declare `static var large: Self` on a protocol and you can write `.large` anywhere a conforming type is expected — Enum-style ergonomics for any value type (WWDC21-10192).
- **CGFloat ⇄ Double automatic conversion** — finally. The Swift compiler transparently bridges between the two; many redundant `Double(myCGFloat)` casts can go away (WWDC21-10192).
- **Property wrapper arguments**: `func body(@SettingValue setting: Setting)` — the wrapper applies inside the function. Closures get this too: `{ ($x, x) in … }` exposes both wrapped and projected values (WWDC21-10192).
- `#if` can now wrap **postfix expressions** (modifier chains): `text.padding() #if os(macOS) .frame(width: 200) #endif`. Eliminates duplicated `Toggle()` blocks in cross-platform SwiftUI (WWDC21-10192).
- Foundation: **`AttributedString`** is the new Swift-native rich text type. Type-safe attributes (compile-time-checked attribute keys), Markdown initializer, equality semantics. Replaces `NSAttributedString` in new Swift code (WWDC21-10109).
- Foundation: **Format styles** — `Date.now.formatted(date: .complete, time: .standard)`, `[1,2,3].formatted(.list(type: .and))`. Replaces `DateFormatter`/`NumberFormatter` allocations (WWDC21-10109).
- Foundation: **Grammatical agreement** in localization — automatic gender/number agreement for source strings. The new format-style API understands "1 file" vs "2 files" without a stringsdict (WWDC21-10109).
- ARC: new "Optimize Object Lifetimes" Xcode build setting enables more aggressive lifetime shortening. Measurably reduces retain/release calls and binary size (WWDC21-10216).

## Performance

- Foundation rewrite of JSON encoder/decoder on Linux: 2-5x faster encoding for typical app payloads (WWDC21-10192).
- Swift 5.5 incremental compilation: incremental imports + earlier dependency graph + extensions-aware recompilation cuts incremental builds by ~33% on the Swift Driver itself (WWDC21-10192).
- Float16 support comes to Apple Silicon Macs (was iOS/tvOS/watchOS only) (WWDC21-10192).

## Migration guidance

- **The Swift Driver is now Swift-native** in Xcode 13. The C++ driver is gone. If you have build customizations that hooked into driver internals, audit them.
- Adopt `AttributedString` in new code; `NSAttributedString` interop bridges both ways (WWDC21-10109).

## Cross-references

- Result Builders are now used by RegexBuilder (2022), SwiftCharts (2022), and many third-party libraries.
- Package Collections (WWDC21-10197) — JSON files of curated packages your team can subscribe to. Discoverable in Xcode 13's Package Search.
