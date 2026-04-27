# Swift 2 Language — WWDC 2015 Analysis

**Sessions covered:** 106 (What's New in Swift), 408 (Protocol-Oriented Programming in Swift), 414 (Building Better Apps with Value Types in Swift), 411 (Swift in Practice), 401 (Swift and Objective-C Interoperability), 403 (Improving Your Existing Apps with Swift), 409 (Optimizing Swift Performance), 405 (Authoring Rich Playgrounds), 102 (Platforms State of the Union — open source announcement)

## Headline

WWDC 2015 was the watershed moment for Swift. The language got: a brand-new error handling model (`do/try/catch/throws/defer`), a `guard` statement, availability checking baked into the compiler, **protocol extensions** (the language feature that re-shaped the standard library), and at the end of the keynote — Swift will be **open source** by end of 2015, including a Linux port. There is no understating how foundational this year was.

## Error Handling (106)

- New `throws` keyword on function declarations marks them as failable.
- Calls to throwing functions must be marked `try`. The `try` keyword exists for the human reader: a future maintainer can immediately see which calls have an early-exit path.
- Two ways to recover: `do { try ... } catch { }` (with full pattern matching in the catch like a switch), or propagate by adding `throws` to your own signature.
- `try!` is a runtime assertion that the call doesn't throw — for cases where logic guarantees safety (e.g., resource in your own bundle).
- Errors are **untyped** — you throw any value of a type conforming to `ErrorType`. Apple consciously rejected Java-style checked exceptions ("pedantic list of every single exception").
- **HIDDEN GEM**: Performance is much closer to a single `if` branch than to traditional exception unwinding (which is "three, maybe even four orders of magnitude slower"). You can use error handling on hot paths.
- Cocoa interop: `NSError**` out-parameter + `BOOL` return is **automatically** imported as a Swift throwing function — and the `BOOL` return goes away. Same for nilable Objective-C results.
- `defer` blocks register cleanup that fires no matter how scope exits (return, throw, fall-through). This is the killer feature for paired begin/end APIs (e.g., `didStartReadingSale` / `didEndReadingSale`).

## `guard` Statement and Pattern Matching (106)

- `guard let x = optional else { return }` requires the else branch to exit scope (return, throw, break, fatalError, etc.). Compiler enforces this.
- After a successful `guard let`, the bound name is **available in the enclosing scope** — eliminates the "pyramid of doom" without forcing implicit-unwrap.
- `if case .someEnum(let x) = value` brings switch-style pattern matching to `if`, `for`, `while`.
- `for case let x? in optionalsArray` filters non-nil.

## Other Language Refinements (106)

- `enum` now carries enough reflection to print meaningfully and mix with custom `init`s.
- `indirect` keyword on enum cases enables recursive ADTs without manual boxing.
- `do { }` introduces a plain scope; old `do-while` renamed to `repeat-while` for legibility.
- Option sets adopt set-like syntax: `[.option1, .option2]`, empty as `[]`.
- Functions and methods unified: external argument labels by default for ALL functions (not just methods). The old `#` shorthand is gone.
- `@testable import` lets unit tests reach `internal` symbols without making them `public`. Release builds keep full access protection.
- Markdown-style rich documentation comments now render in Quick Help.
- Compiler emits warnings for `var` that should be `let`, unused values, and ignored results from non-mutating methods.

## Availability Checking (106, 411)

- Compiler reads SDK availability annotations and **errors** if you call an API too new for your deployment target.
- `if #available(iOS 9.0, *) { ... }` is the unified syntax. The `*` means "future platforms not enumerated still take this branch."
- Composes with `guard`: `guard #available(iOS 9, *) else { return }` raises the privilege of the rest of the function.
- Annotate your own functions/classes/methods with `@available(iOS 9.0, *)` so the compiler can transitively reason about call sites.
- **DOCS MISS THIS**: `respondsToSelector:` is a lie for availability checking — Apple often ships an API name in an earlier OS but with broken/internal-only behavior. The compiler-driven model is the only safe one.

## Protocol-Oriented Programming (408)

The most influential talk Apple has ever given on Swift. Dave Abrahams uses the character "Crusty" to argue that classes have three deep flaws: implicit sharing, monolithic single inheritance with all-or-nothing stored-property baggage, and an inability to express type relationships (Comparable's `Self` problem).

- Slogan: **"Don't start with a class. Start with a protocol."**
- Protocols + value types fix all three. Implicit sharing → values are copied. Monolithic inheritance → multiple protocol conformance, mix in capabilities. Self-requirements → static polymorphism with full type-relationship safety.
- A protocol with a `Self` requirement (or an associated type) **cannot be used as an existential type** — it's only usable as a generic constraint. Collections become homogeneous. Two worlds: dynamic-dispatch (no Self) and static-dispatch (Self/associated types).
- **Protocol Extensions** (the new feature):
  - `extension Renderer { func circleAt(...) { ... } }` provides a default for ALL conformers.
  - A protocol *requirement* creates a customization point — model types can override with dynamic dispatch.
  - A method ONLY in the extension (not declared as a requirement) is statically dispatched — model types can shadow it but only the extension version is called when the call is through the protocol existential. **HIDDEN GEM**: this is a confusing trap; if a method needs runtime customization, declare it as a requirement.
- **Constrained extensions**: `extension CollectionType where Generator.Element: Equatable` brings methods into existence only when the generic constraint is met. Powers `indexOf` on Equatable collections.
- The same constrained extension pattern lets you bridge two protocols: any `Comparable` automatically gets a default `Ordered.precedes` implementation.
- **Crusty's bridge to heterogeneity** for Equatable: provide a default `isEqualTo(_ other: Drawable) -> Bool` that conditionally downcasts to `Self` and uses `==` only when types match. This is the canonical pattern for type-erased equality across a heterogeneous protocol.
- When TO use a class: external identity (window, file handle), reference-typed sinks (renderers), or because Cocoa demands it. But mark them `final` and consider value composition inside.

## Value Types and Value Semantics (414)

- Value types: structs, enums, tuples — and the standard library's `String`, `Array`, `Set`, `Dictionary`. Two variables hold logically distinct values; mutation of one never affects the other.
- Defensive copying disappears. `let` on a value type is a strong guarantee that the value cannot change short of memory corruption.
- **Copy-on-write** for collections: copies are O(1) reference-count bumps; the actual buffer is only duplicated on mutation. The `isUniquelyReferenced` (later `isKnownUniquelyReferencedNonObjC`) primitive is the implementation hook.
- Composition: a struct of value types is a value type. `Diagram` containing `[Drawable]` works as a value type even with heterogeneous reference-style protocol existentials inside, IF the underlying conformers are themselves value types.
- **HIDDEN GEM**: free undo stack. Append the document value to `[Diagram]` on each mutation. To undo, just point at the previous element. Photoshop uses exactly this pattern at tile granularity — only the dirty tiles get duplicated.
- Free from race conditions: passing a value to another thread gives that thread a logical copy, so a subsequent local mutation does not race.
- Mixing reference inside a struct: only safe with **immutable** reference types (UIImage). For mutable references (UIBezierPath), implement copy-on-write manually with a `pathForReading` / `pathForWriting` (mutating) computed property pair backed by a private stored reference.
- Always make value types conform to `Equatable`. Equality must be reflexive, symmetric, transitive — the compiler can't enforce this; you must.

## Compile-Time Safety Patterns (411)

Alex Migicovsky's "lucid dreams" patterns:

- **Strongly-typed asset catalog identifiers**: nest an `ImageAsset: String` enum inside `UIImage`, write a convenience init taking the enum, and you get `UIImage(asset: .unicornBrowser)` with non-optional return and compile-time typo detection.
- **Strongly-typed segue identifiers**: define a `SegueIdentifier: String` enum, do a `switch` on the enum in `prepareForSegue` — the compiler enforces exhaustiveness, so adding a new segue surfaces every place that needs updating.
- **Reusable via protocol extension**: `protocol SegueHandlerType { associatedtype SegueIdentifier: RawRepresentable }`, then `extension SegueHandlerType where Self: UIViewController, SegueIdentifier.RawValue == String { ... }` provides `performSegueWithIdentifier(.someSegue)` on every conforming view controller. **BEST PRACTICE**: this is the canonical way to ship typesafe Cocoa wrappers via protocol-oriented design.

## Performance (409, 102 SOTU)

- Swift's compiler does whole-module optimization for stripped-down generics and devirtualization. The standard library is 80%+ value types specifically so generic inlining can erase abstraction cost.
- `final` on classes lets the compiler devirtualize calls.
- Use `private` to give the compiler closed-world knowledge for inlining.

## Open Sourcing Announcement

At Platforms State of the Union, Chris Lattner announced Swift will be open-sourced (compiler + standard library) by end of 2015 with a Linux port. This is the largest platform/strategy implication of the year.

## Cross-references

- Pattern matching is foundational for `do/try/catch` (106).
- Protocol extensions enable the option-set redesign (106) and the Standard Library overhaul (408).
- Availability checking complements value-type design — both push errors to compile time (411).

## Migration Notes

- Xcode 7 has a Swift 1 → Swift 2 migrator for the bulk mechanical changes.
- The most disruptive Cocoa change: throwing API import. Code that previously created `NSError` out-parameters now reads as `try`/`catch`.
