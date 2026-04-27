# Swift Language Debut — WWDC 2014 Analysis

**Sessions covered:** 402 (Introduction to Swift), 403 (Intermediate Swift), 404 (Advanced Swift), 406 (Integrating Swift with Objective-C), 407 (Swift Interoperability In Depth), 408 (Swift Playgrounds), 409 (Introduction to LLDB and the Swift REPL), 410 (Advanced Swift Debugging in LLDB), 417 (What's New in LLVM)

## Headline

WWDC 2014 announced **Swift** — Apple's brand new, statically-typed, compiled programming language, ABI-compatible with Objective-C runtime. The Swift book hit 370,000 downloads in less than 24 hours. It is the first new language from Apple in two decades and will be the foundation language for all future SDK work. Swift 1.0 ships with iOS 8 in fall 2014.

## The Core Mental Model (sessions 402, 403, 404)

- **Immutability by default**: prefer `let` over `var`. The compiler can optimize harder, code is safer in multi-threaded environments, and intent is clearer (402).
- **Type inference everywhere**: types are explicit but seldom written. `let version = 1.0` infers `Double`, `let year = 2014` infers `Int`, `let isAwesome = true` infers `Bool`. Code stays compact AND type-safe (402).
- **No header files, no universal base class, no semicolons, no parentheses around `if`/`while`, mandatory braces** (402). The mandatory braces alone eliminate an entire class of trailing-`if` bugs from C.
- **Switch statements MUST be exhaustive** — compiler errors out unless every case or `default` is covered (402). Closes the "I forgot a state in my state machine" bug class.
- **Switch cases do NOT fall through implicitly** — opposite of C. No `break` needed (402).

## Optionals — Swift's Single Sentinel (sessions 402, 403)

- Optional `Int?` is literally `enum Optional<T> { case none; case some(T) }` — modeled IN the language using its own generic enum machinery (403).
- `nil` in Swift is **not** an Objective-C nil pointer. It works with **any** type — `Int?`, `Bool?`, `String?`, anything. Replaces NSNotFound, -1, and every other sentinel kludge (403).
- Two ways to unwrap: forced `value!` (traps if nil) and the safer `if let leg = possibleLegCount { ... }` pattern that tests + unwraps + binds in one step (402, 403).
- **Optional chaining**: `paul.residence?.address?.buildingNumber?.toInt()` — like Objective-C nil-messaging, but type-safe and works for any type, not just objects (403).
- Combine with `if let`: `if let address = paul.residence?.address?.buildingNumber?.toInt() { ... }` — drill through arbitrary depth, get a non-optional value at the end (403).

## Memory Management (session 403)

- ARC by default — same model as Objective-C, no GC, no manual retain/release.
- Three reference types: `strong` (default), `weak` (Optional, auto-resets to nil on deallocation), `unowned` (non-Optional, asserts on access if dangling — like `unsafe_unretained` but safe).
- **`unowned`** is the right choice when "my life depends on the owner": the credit card example — a card cannot exist without a cardholder. Avoids forcing `weak`'s Optional + mutability (403).
- **Closures capture self strongly by default** — Swift compiler will NOT let you implicitly reference self in a stored closure to prevent the silent retain cycle (403). Use the `[unowned self]` or `[weak self]` capture list inside `{ ... in ... }`.

## Initialization Rules (session 403)

- Every stored property MUST have a value before the initializer returns. Compiler enforces this.
- **Initialization order in Swift is OPPOSITE of Objective-C**: set your own properties FIRST, then call `super.init()`. This prevents calling overridden methods on a half-initialized self (403).
- Two initializer kinds: **designated** (does the work, calls super) and **convenience** (calls another init in the same class, never up the chain). Marked with `convenience` keyword.
- Initializers are **not inherited by default** — preventing accidental misuse — UNLESS the subclass adds no initializers and provides defaults for all its stored properties (403). Then it inherits everything.

## Closures (session 403)

- Closures are first-class. They have type `(Int, Int) -> Bool`. Functions are just named closures.
- **Trailing closure syntax**: if a function's last argument is a closure, hoist it OUT of the parens — `repeat(2) { println("Hello") }`. Reads like a control flow statement.
- **Implicit argument names** `$0, $1, ...` — `sorted(names) { $0 < $1 }` collapses a sort to one expression.
- Single-expression closures **implicitly return** their result — no `return` keyword needed (403).
- Closures are ARC objects, follow the same memory rules as classes. Capture lists `[unowned self]` go inside the braces, before the parameter list.

## Generics (session 404)

- Type parameters in angle brackets: `func swap<T>(inout x: T, inout y: T)` — single `T` constrains both args to the same type. No more `id` losing type info.
- **Constrain type parameters with protocols**: `func find<T: Equatable>(array: [T], value: T) -> Int?` — `T: Equatable` lets you call `==` inside the body and forces callers to pass a comparable type.
- **Associated types in protocols** (the `typealias Element` requirement in `GeneratorType`/`SequenceType`) let protocols be parametric without the caller specifying the type — Swift deduces it from method signatures (404).
- Swift's generics are **truly generic** — they conserve type information at runtime. Unlike Java/C# erasure-based generics, Swift can constrain via protocol equality (`func ==(a: T, b: T)`) and generate specialized code at the optimizer's discretion.
- **Generic specialization is an optimization, not a requirement** — Swift compiles a generic function once and can specialize per-type when profitable. Avoids C++ template bloat (404).

## Enums With Associated Values (sessions 402, 403)

- **Discriminated unions**: `enum TrainStatus { case onTime; case delayed(Int) }`. Match with `case .delayed(let minutes): ...`. Each case can carry different data of different types.
- HIDDEN GEM: **Optional itself is an enum** — `Optional<T>` is `case none; case some(T)`. Pattern matching on optionals is just enum pattern matching.
- Enums with raw values: `enum Planet: Int { case mercury = 1, venus, earth, mars }` — auto-incremented. Enums can have `String`, `Character`, or `Int` raw types.
- **Nested types**: define `Status` inside `Train` so `Train.Status.onTime` is the only access path. Encapsulation without files (402).

## Pattern Matching in Switch (sessions 403, 404)

- Match values, ranges (`case 1..<8:`), tuples `(let r, let g, let b)`, types via `as` pattern (`case let car as RaceCar:`), enums with associated data, and any combination via tuples.
- `where` clause for additional predicates: `case (let r, let g, let b) where r == g && g == b: // grayscale` (404).
- The property-list parsing example in 404 is the canonical demonstration — validate, type-check, bind, and compute in one switch with one default for failure.

## Extensions and Operator Overloading (sessions 402, 404)

- **Extend ANY type — including `Int`, `String`, `Array`** which are themselves struct definitions in the standard library. `extension Int { func repetitions(task: () -> ()) { for _ in 0..<self { task() } } }` lets you write `500.repetitions { println("Hello") }`.
- HIDDEN GEM: extensions can extend types from C (like `CGSize`) and types in other frameworks. No need for category-style class wrapping.
- **Custom operators**: declare `operator infix +++ {}`, then write `func +++(lhs: T, rhs: T) -> T`. New operators or existing operators on new types — both supported (404).

## Value vs Reference Types (session 402)

- `struct` and `enum` are value types. Passed by COPY (Swift uses copy-on-write for stdlib collections to avoid the perf cost).
- `class` is reference type. Passed by reference.
- HIDDEN GEM: with a struct, `let point2 = point1` makes the ENTIRE value immutable — you cannot even set `point2.x = 5`. Constness propagates into the struct's properties. With a class, `let window2 = window1` makes only the reference immutable; you can still call `window2.title = "..."`. This single rule eliminates a huge class of accidental shared-mutable-state bugs.
- Mutating struct methods must be marked `mutating func` — clearly documents value-type mutation and prevents calling them on a `let`-bound instance.

## Objective-C Interop (sessions 406, 407)

- **Swift String ↔ NSString, Swift Array ↔ NSArray, Swift Dictionary ↔ NSDictionary** — all interchangeable at API boundaries with zero glue. `pathComponents` on a Swift String returns a Swift `Array` even though Foundation declares `NSArray`.
- **Bridging header** (`MyApp-Bridging-Header.h`): when you add the first Swift file to an Obj-C project, Xcode offers to create one. Put `#import "MyClass.h"` lines here to expose Obj-C to Swift. CHECK IT INTO SOURCE CONTROL — Xcode creates it but you own it (406).
- **Generated header** (`MyApp-Swift.h`): auto-generated by the build, contains the entire public Swift interface translated into Obj-C. `#import "MyApp-Swift.h"` from your Obj-C `.m` files. For frameworks: `#import <MyKit/MyKit-Swift.h>`.
- **Naming translation**: a Swift `init(coder: NSCoder)` shows up in Obj-C as `initWithCoder:`. The "init" prefix's `with` is dropped in Swift — only for initializers, not regular methods (406).
- HIDDEN GEM: forward-declare a Swift class in an Obj-C header with `@class MySwiftClass;` to break import cycles (the Swift generated header imports the umbrella header, which can't re-import the generated header). Same trick as Obj-C (406).
- `@objc` annotation exposes a Swift protocol/class to Objective-C explicitly. Required for Swift-only types you want visible to Obj-C (`@objc protocol NewListControllerDelegate`) (406).
- Type cast required when Obj-C returns `id`/`AnyObject`: `let data = source.copy() as NSData` — fails fast at the boundary if the cast is wrong, instead of crashing later (406).

## Swift's Compiler Architecture (session 404, 417)

- Swift compiles via LLVM with an **extra high-level optimization phase** (SIL — Swift Intermediate Language) before the LLVM IR — language-aware optimizations like generic specialization, devirtualization, abstraction-penalty elimination.
- BEST PRACTICE: mark methods/classes `final` to enable devirtualization in places where the compiler can't prove no subclass exists (404).
- **No JIT, no GC, no warm-up pause** — Swift compiles to native code shipped in your binary. Predictable startup, predictable GC pauses (none).
- Struct types (including `Int`, `Float`) have **zero abstraction penalty** — wrapping `Int` in your own struct for type safety (`struct Meters { let value: Double }`) costs nothing at runtime (404).

## Swift Playgrounds (session 408)

- Live REPL-style file in Xcode. Edit code, see results in a sidebar in real time. Designed for exploration, prototyping, and learning.
- Render values inline (graphs, images, views, NSAttributedString). Time-travel through loop iterations. The slider/timeline replays the execution.
- BEST PRACTICE: ship sample code as playgrounds — readers can edit and re-run. Avoid demoing a static screenshot.

## LLDB + Swift REPL (sessions 409, 410)

- The Swift REPL is the same Swift compiler hooked into LLDB's command line. Drop into `swift` from a terminal, type expressions, see results.
- LLDB now understands Swift fully — `po`, breakpoints, expressions all work on Swift values. Swift symbol mangling is preserved for the debugger (410).

## Best Practices

- **Use `let` until the compiler complains** (402). Starting with `var` everywhere is a smell.
- **Make `@State`-equivalent properties `private`** — actually for Swift, private is the default access scope strategy for owned state.
- **Mark switch-pattern variable bindings with `let`** — `case .delayed(let minutes):` not `case .delayed(var minutes):` unless you need to mutate.
- **Use type inference** but annotate at API boundaries (function signatures, public properties) to lock down the contract (402).
- **Always `eraseToAnyPublisher`-style** abstraction at API boundaries — for Swift in 2014, equivalent is "expose protocol existentials, not concrete generic types" so callers aren't bound to your impl.

## Hidden Gems

- HIDDEN GEM: `Int?` and friends compose with collections — `[Int?]` is a valid array of optional ints. `[1, nil, 2, nil, 3].compactMap { $0 }` (later) — but in 1.0 you'd use `filter` then force-unwrap.
- HIDDEN GEM: tuples can be returned from functions and decomposed at the call site: `let (code, msg) = refresh()` or `let status = refresh(); status.code`. With named tuple elements `(code: Int, message: String)`, dot-access works without decomposition (402).
- HIDDEN GEM: closures can refer to local mutable vars and mutate them — no `__block` qualifier needed like Obj-C blocks (403).
- HIDDEN GEM: in Obj-C you write `[self.delegate methodIfDelegateExists]` with a nil check; in Swift you write `delegate?.methodIfDelegateExists()` — optional chaining handles the nil case naturally (406).
- PERFORMANCE: Swift's structs allocate on the stack (or inline in their parent). Composing small structs has zero heap overhead — the SIL optimizer eliminates the abstraction (404).

## Cross-references to other 2014 topics

- The new App Extensions architecture (205, 217) ships in Objective-C but Apple says "we expect new code to be in Swift."
- HealthKit (203), HomeKit (213), CloudKit (208), PhotoKit (511), Metal (603) all ship Objective-C APIs that Swift consumes via the bridge — all the new frameworks were designed knowing Swift was coming.
- Generics + protocols underpin SwiftUI's `View`/`some View` model years later (in 2019). Swift 1.0 already has the full power; SwiftUI is the application of it.

## Migration Guidance (session 406)

- **Don't rewrite, integrate**: add Swift files to existing Obj-C projects one at a time. Swift can subclass Obj-C classes (UIViewController, NSObject) seamlessly.
- **Adopt Swift in NEW model layers and view controllers** first; leave old Obj-C alone if it works.
- **Turn on `Defines Module = YES`** on your Obj-C frameworks (default in Xcode 6) so Swift can `import MyFramework`. Without it, you'd need `#import` from a bridging header.
