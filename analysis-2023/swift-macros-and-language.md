# WWDC 2023 — Swift 5.9: Macros, Concurrency, and Language Evolution

Swift 5.9 was the largest single language update since Swift Concurrency. Macros are the headline feature, but parameter packs, ownership, and C++ interop are equally significant.

## Sessions Analyzed
- 10164 — What's new in Swift (gateway)
- 10166 — Write Swift macros
- 10167 — Expand on Swift macros
- 10168 — Generalize APIs with parameter packs
- 10170 — Beyond the basics of structured concurrency
- 10172 — Mix Swift and C++
- 10171 — Meet Swift OpenAPI Generator

## Swift Macros

Macros are compile-time code generators written in Swift. They run as compiler PLUGINS — separate processes that take a SwiftSyntax tree and return a SwiftSyntax tree.

### Two Top-Level Categories

1. **Freestanding macros** — invoked with `#`, like `#stringify(2+3)`. Replace the macro expression with generated code.
2. **Attached macros** — invoked with `@`, attached to a declaration. Augment the declaration in five possible ways.

### Five Attached Macro Roles

- `@attached(member)` — adds new methods/properties to the type. Ex: `@CaseDetection` adds `isAbsolute`, `isRelative` getters to an enum.
- `@attached(memberAttribute)` — applies attributes to existing members.
- `@attached(peer)` — adds sibling declarations. Ex: generate a callback version next to an async function.
- `@attached(accessor)` — turns stored properties into computed ones with custom getters/setters. Used by `@Observable` to install observation hooks.
- `@attached(extension)` (formerly conformance) — adds protocol conformances and extension members.

These can be composed: `@Observable` is a member + memberAttribute + extension macro all rolled into one.

### How They Work

1. You write `#myMacro(args)` or `@MyMacro` in your code.
2. Compiler type-checks the arguments AGAINST the macro declaration BEFORE expansion. If args don't typecheck, you get a normal error — no expansion happens.
3. Compiler serializes the syntax tree, sends it to the plugin process.
4. Plugin (a Swift program) receives a SwiftSyntax tree, transforms it, returns new syntax.
5. New syntax is parsed and inserted into the program.

### Macro Hygiene

Macros are HYGIENIC — generated identifiers don't collide with user code. Macros can also emit DIAGNOSTICS (errors/warnings/fix-its) via the `MacroExpansionContext`.

### Testing Macros

Macros are PURE FUNCTIONS over syntax trees. Best practice: use `assertMacroExpansion` from SwiftSyntax to write deterministic unit tests. Don't rely on integration tests through the compiler.

```swift
assertMacroExpansion(
  "@CaseDetection enum Foo { case a, b }",
  expandedSource: "...",
  macros: ["CaseDetection": CaseDetectionMacro.self]
)
```

### Where Macros Are Used

- `@Observable` (Observation framework)
- `@Model`, `@Query`, `@Attribute`, `@Relationship`, `@Transient` (SwiftData)
- `#Predicate { ... }` (Foundation)
- `#Preview` (SwiftUI/UIKit/AppKit, replacing `PreviewProvider`)
- `#URL`, `#hexLiteral`, etc.
- `@DebugDescription`-style helpers in third-party packages

### Inspect & Debug

- Right-click → "Expand Macro" shows the generated code in Xcode.
- Set breakpoints in macro plugin code (they run as separate processes that Xcode can attach to).
- Errors in generated code show the expansion in the error message.
- Option-click documents the macro inline.

## Parameter Packs

Solves a real pain: variadic generics. Before 5.9, APIs like `evaluate<R1>(_:)`, `evaluate<R1, R2>(_:_:)` had to be written with hand-rolled overloads up to some arbitrary arity. Pass 7 args, you got a compile error.

```swift
func evaluate<each Result>(_ requests: repeat Request<each Result>) -> (repeat each Result)
```

`each Result` is a TYPE PARAMETER PACK — represents zero or more types. `repeat` introduces a pack expansion. The result type `(repeat each Result)` is a tuple of all results in order.

Used by SwiftUI's `TupleView`, by `Regex` capture groups, by `KeyPath` builders, by SwiftData query builders. The generic system finally has the expressive power to model "any arity" cleanly.

## Non-Copyable Types & Ownership

```swift
struct FileDescriptor: ~Copyable {
  let fd: Int32
  consuming func close() { syscall_close(fd) }
  deinit { /* runs when value goes out of scope */ }
}
```

`~Copyable` (read: "not Copyable") removes the implicit copy-on-assign. Suppresses bugs like accidentally sharing a file descriptor across threads.

- `consuming` methods take ownership of `self`. After the call, the value can no longer be used.
- `borrowing` (default for non-self params) takes a temporary read-only reference.
- `inout` is mutable borrow.
- `deinit` on structs is allowed only for non-copyable types.

This is the foundation for systems-level Swift (think kernel drivers, embedded). Future versions extend to generics over ~Copyable types.

## if/switch as Expressions

```swift
let icon: String = if isError { "x" } else if isWarning { "!" } else { "check" }

let style = switch theme {
  case .dark: DarkStyle()
  case .light: LightStyle()
  case .auto: SystemStyle()
}
```

No more closure-immediately-invoked workarounds. Stored properties and globals get clean conditional initialization.

## Custom Actor Executors

You can now make an actor schedule its work on a SPECIFIC dispatch queue:

```swift
actor DatabaseConnection {
  let queue = DispatchSerialQueue(label: "db")
  nonisolated var unownedExecutor: UnownedSerialExecutor {
    queue.asUnownedSerialExecutor()
  }
}
```

Critical for migrating Objective-C code that already runs on a known queue — your new actor now synchronizes WITH that existing code instead of spinning up a parallel scheduler.

`SerialExecutor` is the protocol; `DispatchSerialQueue` conforms. You can write your own executor for embedded systems or single-threaded environments.

## Beyond Structured Concurrency (10170)

Key advanced patterns:
- **Discarding task groups** (`withDiscardingTaskGroup`) — don't accumulate child results; safer for "fire many tasks" scenarios. Avoids unbounded memory growth.
- **Task cancellation** — cooperative; check `Task.isCancelled` or use `try Task.checkCancellation()`. `withTaskCancellationHandler` runs cleanup synchronously on cancellation.
- **Task locals** — `@TaskLocal` for context propagation through async boundaries (e.g., logging request IDs).
- Avoid unstructured `Task { }` when you can use a child task — child tasks inherit cancellation, priority, and task locals automatically.

## Swift Foundation Rewrite

Foundation is being rewritten in pure Swift, open-source. Real perf wins shipped in iOS 17 / macOS Sonoma:
- JSON encoding/decoding: 2x–5x faster (no Obj-C bridging).
- Calendar calculations: ~20% faster.
- Date FormatStyle: ~150% faster.
- New Swift Predicate replaces NSPredicate.

For Linux/Windows: a single shared Foundation now ships across platforms, reducing behavior divergence.

## Swift ↔ C++ Interop

Direct, no bridging layer needed. Swift can:
- Call C++ functions and methods directly.
- Use C++ value types (with copy/move/destructor semantics).
- Iterate `std::vector`, `std::map` as Swift collections.
- Subscript and member access work natively.

C++ can call Swift via a generated header — no `@objc` requirement. C++ can use Swift structs, classes, methods, properties, initializers.

CMake supports mixed Swift/C++ targets in a single build, file by file.

This is HUGE for projects like LLVM and FoundationDB that have massive C++ codebases.

## Macro Anti-Patterns to Avoid

- Don't write macros that have SIDE EFFECTS (file I/O, network, env access). They run during build and break determinism.
- Don't generate code that depends on identifiers from the surrounding context unless you intend to. Hygiene helps but is not a perfect shield.
- Always emit DIAGNOSTICS for misuse rather than generating broken code. Adopters shouldn't have to read expanded source to debug.

## Pathways

- **New macro author**: 10164 → 10166 → 10167
- **Concurrency advanced**: 10164 → 10170
- **Generic library author**: 10164 → 10168
- **Mixed C++ codebase**: 10164 → 10172

## Hidden Gems

- The macro plugin runs in a SANDBOXED process. It can't read environment, files, or make network calls. This is enforced.
- `assertMacroExpansion` produces git-diff-style diffs when a macro's output doesn't match expected. Use it religiously.
- Parameter packs use `each` for the binding name and `repeat` for expansion. The keyword pair mirrors `for ... in` — readable once you've seen it twice.
- `consuming` and `borrowing` work on COPYABLE types too — they're not exclusive to ~Copyable. Use `consuming` to express that you want to take ownership and dispose.
- Custom executors finally let you bridge Swift Concurrency into legacy GCD code WITHOUT having every async call hop threads.
- The Swift OpenAPI Generator is now an official Apple-maintained package. Run it as a SwiftPM build plugin to generate type-safe API clients from OpenAPI YAML.
