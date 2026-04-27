# Swift Concurrency & Language (2022)

WWDC22 was the maturity year for Swift concurrency. Apple shipped Swift 5.7 with the second major wave of concurrency (after async/await/actors in 2021): Sendable checking, distributed actors, Async Algorithms, Swift Regex, parameterized protocols, and a clear path to Swift 6.

## Sessions covered
- WWDC22-110354 — What's new in Swift
- WWDC22-110351 — Eliminate data races using Swift Concurrency
- WWDC22-110355 — Meet Swift Async Algorithms
- WWDC22-110357 — Meet Swift Regex
- WWDC22-110358 — Swift Regex: Beyond the basics
- WWDC22-110353 — Design protocol interfaces in Swift
- WWDC22-110356 — Meet distributed actors in Swift

## Cross-cutting concepts

### The "boats and islands" mental model (110351)
The talk frames concurrency as boats (tasks) on a sea, isolated by default, and islands (actors) that boats must "visit" to access shared state. Key insights:
- **Tasks are self-contained**; data passing between them must go through `Sendable`.
- **Actors run highest-priority work first** — they are NOT FIFO like serial dispatch queues. This eliminates priority inversions but means you cannot rely on submission order.
- **Use `AsyncStream`** if you need ordered event delivery from multiple producers.
- **High-level data races still exist**: two `await`s on the same actor are interleaving points. The actor's state can mutate between them. Make multi-step transactions synchronous on the actor.

### Sendable checking has 3 modes (110351, 110354)
| Mode | Effect |
|------|--------|
| Minimal (default in 5.7) | Only diagnose explicit `Sendable` conformances. Same as 5.5/5.6. |
| Targeted | Diagnose code that already uses concurrency features (`Task`, `actor`, `async`). |
| Complete | Approximate Swift 6 semantics. Diagnoses everything, including dispatch-queue closures. |

**`@preconcurrency import`** silences warnings for types coming from modules that haven't audited their `Sendable` story yet. When the dependency adds explicit conformances, the warnings come back if your assumptions were wrong.

### MainActor and U-I-land
Don't put long-running work on `@MainActor`. The model is "the U-I-land is one big island; only one boat at a time." `@MainActor` annotation on a *type* makes all its instance methods main-actor-isolated by default; methods can opt out with `nonisolated`.

### Back-deployed concurrency (110354)
Swift 5.7 back-deploys the entire concurrency runtime to **iOS 13 and macOS Catalina**. Apps bundle the 5.5 concurrency runtime for older OSes. This means async/await is finally usable for real shipping iOS apps that support older OSes.

### Distributed actors (110354, 110356)
Add `distributed` keyword to mark actors and methods that may live on a different machine. Calls become `try await` — they may throw network errors. Apple shipped an open-source SwiftNIO + SWIM-protocol package for clustered server apps.

## Swift Async Algorithms (110355)
A new open-source package, separate from the standard library, that ships:
- **Combining**: `zip`, `merge`, `combineLatest` — concurrent iteration over multiple AsyncSequences with rethrowing.
- **Time-based**: `debounce(for:)`, `throttle`, `chunked(by:)` — built on the new `Clock` API.
- **Collection initializers**: `Array(asyncSequence)`, `Dictionary(asyncSequence)` — bridge back to eager collections.

### The new Clock / Instant / Duration types (Swift 5.7)
- `ContinuousClock` — like a stopwatch; advances even when the machine sleeps. Use for human-relative delays.
- `SuspendingClock` — pauses with the machine. Use for animations.
- `chunked(by:)` and `debounce` use clocks generically — write a custom `Clock` for tests.

## Swift Regex (110357, 110358, 110354)
Swift 5.7 introduces three syntaxes for the same regex engine:
1. **Literals** — `/(\w+)\s+(\d+)/` — Perl-compatible, type-checked at compile time.
2. **RegexBuilder DSL** — a SwiftUI-style declarative builder using `Regex { ... }`, `Capture`, `OneOrMore`, etc. Components are reusable and composable.
3. **Foundation interop** — drop a `Date.FormatStyle` directly into a regex and capture a `Date` value.

### Critical deployment caveat
Swift Regex requires the engine to be present in the OS. **It only runs on macOS 13 / iOS 16 or later.** This is a hard back-deployment limit unlike most of the rest of Swift 5.7.

### Unicode correctness
By default, `.` matches a whole Unicode grapheme cluster — *not* a `Unicode.Scalar` and *not* a UTF-8 byte. This avoids the entire class of bugs around emoji and combining characters that plague regex in other languages.

## Generics overhaul (110354, 110353)

### `any` keyword for existentials
Existential types now require the `any` keyword (e.g. `any Mailmap`). Without it, the compiler emits warnings (mandatory in future versions). The keyword visually separates the cheap concrete generic case (`some Mailmap`) from the expensive boxed case (`any Mailmap`).

### Implicit existential opening
When you pass `any Mailmap` to a generic parameter `<T: Mailmap>`, the compiler now silently "opens the box" so you no longer hit `Mailmap cannot conform to itself`.

### Self/associated-type-using protocols can be existentials now
Previously, `Equatable`, `Collection`, etc. could not be used as `any Equatable`. Swift 5.7 lifts this restriction. Combined with **primary associated types** — `protocol Collection<Element>` — you can write `any Collection<Int>` directly in the language, eliminating the need for the hand-written `AnyCollection` boxing struct.

### `some` for parameter types
`func addEntries<M: Mailmap>(to mailmap: inout M)` can now be written as `func addEntries(to mailmap: inout some Mailmap)`. This makes generics syntactically as cheap to use as existentials, removing the temptation to default to the slower `any` form.

### Constrained opaque return types (110353)
`-> some Collection<any Animal>` lets you hide implementation details (e.g. you used `lazy.filter`) while still exposing useful information about the element type. Previously, `some Collection` was too opaque — the caller couldn't even iterate meaningfully.

### Same-type requirements for protocol invariants
When two protocols loop back on each other through associated types (`AnimalFeed.CropType.FeedType` should equal `Self`), use `where Self.CropType.FeedType == Self` to collapse the infinite tower of associated types into a guaranteed cycle. This catches refactor mistakes at compile time.

## Build & runtime performance (110354)

- **Type checker**: a complex generic example that took 17 seconds in 5.6 now type-checks in under 1 second. Apple rewrote the requirement-machine for protocol generics.
- **Protocol checking on launch**: cached in iOS 16. Some apps see launch times **cut in half**.
- **Swift Driver as a framework**: Xcode now embeds the driver instead of forking it as a process. Build improvements range 5–25%.
- **Standalone Linux binaries**: Statically linked by default; smaller because the Unicode dependency is replaced with a native implementation.
- **TOFU** (Trust On First Use) — Swift PM records the fingerprint of a package on first download and validates on subsequent downloads.

## Module disambiguation (110354)
`moduleAliases: ["Logging": "VendorLogging"]` in your `Package.swift` lets you rename a module from outside the package that defines it. This finally solves the "two packages both define `Logging`" problem.

## Best practices
- **BEST PRACTICE**: Always specify `Sendable` constraints on generic parameters that cross isolation domains. The compiler can't help you otherwise.
- **BEST PRACTICE**: Mark `final class` types Sendable only if all storage is immutable. Use `@unchecked Sendable` only when you guarantee synchronization yourself (e.g. internal lock).
- **BEST PRACTICE**: Prefer `nonisolated` synchronous helpers — they stay in their caller's isolation domain instead of forcing a hop.
- **HIDDEN GEM**: `@preconcurrency import FarmAnimals` is the right escape hatch when working with libraries that haven't adopted `Sendable` yet — *not* `@unchecked Sendable`.
- **HIDDEN GEM**: Async actor methods should be composed of small *synchronous* transactions; treat each `await` as a public re-entrancy point.
- **PERFORMANCE**: 17→1 second type-check improvement for complex generics; iOS 16 cached protocol metadata can halve launch times.

## Cross-references
- Performance pairing: WWDC22-110363 (App size & runtime), WWDC22-110362 (Link fast).
- Patterns built on top: WWDC22-10142 (Background tasks in SwiftUI uses async/await throughout).
- Visual debugging: "Visualize and optimize Swift Concurrency" — new Swift Tasks and Swift Actors instruments.
