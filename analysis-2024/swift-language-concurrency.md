# Swift Language, Concurrency, Performance & Testing -- WWDC24 Deep Analysis

Comprehensive analysis of WWDC24 sessions covering Swift 6, the new data-race safety language mode, noncopyable types, performance, testing, and embedded Swift.

Sessions analyzed: 10136 (What's new in Swift), 10169 (Migrate your app to Swift 6), 10184 (A Swift Tour), 10170 (Consume noncopyable types), 10217 (Explore Swift performance), 10197 (Embedded Swift), 10179 (Meet Swift Testing), 10195 (Go further with Swift Testing), 10216 (Swift on Server), 10075 (SwiftData history), 10137 (What's new in SwiftData), 10138 (Custom data store with SwiftData).

---

## 1. The Swift 6 Language Mode -- Data-Race Safety by Default

The biggest single conceptual shift in WWDC24 is **the Swift 6 language mode**, which turns data-race safety into a compile-time guarantee.

### 1.1 The Two-Setting Strategy (WWDC24-10169)

You do NOT just flip Swift 6 on. The recommended migration order is two-step, **per target**:
1. Set "Swift Concurrency Checking" to **Complete** -- stays in Swift 5 mode but emits warnings for everything Swift 6 would reject.
2. Resolve all warnings, then set "Swift Language Mode" to **Swift 6** to lock in the changes.

> "Adopting it can significantly improve the quality of your app by catching mistakes in concurrent code at compile time." (WWDC24-10169)

**Migration order best practice:** Start at the UI layer (extension/app target) BEFORE library targets. UI code typically already runs on the main actor and uses APIs (SwiftUI, UIKit) that are now annotated. This generates fewer warnings to clean up first, and lets you propagate annotations down into your own frameworks. (WWDC24-10169)

**Hidden gem:** "All SwiftUI views are now tied to the main actor in Xcode 16's SDK. You can probably REMOVE @MainActor annotations you previously added to your view types." (WWDC24-10169)

### 1.2 The Four Easy Wins for Global State (WWDC24-10169)

Most data-race warnings come from a small number of root causes. Look for these first:
1. **Mutable globals** -- change `var logger = Logger()` to `let logger = Logger()` if Sendable. The lazy initializer is atomic in Swift, so race-free.
2. **Global functions** that touch main-actor state -- annotate the *function* with `@MainActor` (the compiler offers a fix-it).
3. **Public types that should be Sendable** -- Swift does NOT infer Sendable for public types (it's a binding API contract). Add explicitly when safe.
4. **`@preconcurrency` on protocol conformances** -- shorthand for `MainActor.assumeIsolated` semantics: if the delegate is called off the main actor in production, the program traps instead of corrupting state.

### 1.3 `MainActor.assumeIsolated` -- The Escape Hatch (WWDC24-10169)

When you receive a callback from code you do NOT maintain (e.g., `CLLocationManager`), and you know it always runs on the main actor:

```swift
nonisolated func locationManager(_:didUpdate locations:) {
    MainActor.assumeIsolated {
        // Update UI state -- the assertion traps if not actually on main actor
    }
}
```

This does NOT start a new task. It tells Swift the code is already on the main actor, and traps if the assumption is false. Trapping is bad, but vastly better than data corruption.

### 1.4 Smarter Region-Based Sendable Checking (WWDC24-10136)

Swift 6 understands "send-and-forget" patterns that 5.10 rejected:

```swift
let client = NonSendableClient()
await store.add(client)  // Swift 6: OK (client no longer used after send)
client.update()          // Swift 6: ERROR (re-using after send -- data race)
```

This significantly reduces false-positive warnings compared to Swift 5.10's complete checking.

### 1.5 The `nonisolated(unsafe)` Last Resort (WWDC24-10169)

When you have external synchronization the compiler can't see (a dispatch queue, an external lock):

```swift
nonisolated(unsafe) var legacyState: SomeType = ...
```

Treat it like `unsafe` keywords elsewhere -- you assume the burden, and should plan to refactor away from it.

---

## 2. Noncopyable Types -- Unique Ownership Comes to Generics

WWDC24 expands noncopyable types from concrete-only (Swift 5.9) to full generic support (WWDC24-10170).

### 2.1 Mental Model: `~Copyable` Suppresses a Default

Every type, generic parameter, protocol, and existential implicitly conforms to `Copyable`. Writing `~Copyable` *suppresses* that default conformance -- it does NOT mean "noncopyable type". It means "may or may not be copyable."

> "A regular constraint narrows the types permitted by being more specific. Whereas a tilde constraint broadens by being less specific." (WWDC24-10170)

### 2.2 Three Parameter Ownership Modes (WWDC24-10170)

Noncopyable parameters MUST declare ownership because the compiler can't fall back to copying:

| Modifier | Semantics | Use when |
|---|---|---|
| `consuming` | Function takes the value, caller loses it | Last use; transformations |
| `borrowing` | Read-only temporary access | Inspection/queries |
| `inout` (or `mutating` on methods) | Temporary write access; must reinitialize | Mutations |

### 2.3 The BankTransfer Pattern -- Real-World Use Case (WWDC24-10170)

The headline example is a `BankTransfer` that should run exactly once:

```swift
struct BankTransfer: ~Copyable {
    consuming func run() {
        // ... transfer logic
        discard self  // skip deinit
    }
    deinit {
        // automatic rollback if dropped without running
    }
}
```

**Hidden gem:** Combining `~Copyable` + `consuming run()` + `deinit` for rollback gives you "structured resources" that are correct-by-construction. If the task is cancelled before `run()` executes, the deinit fires automatically and reverts the transaction. No manual `defer` blocks needed.

### 2.4 Conditional `Copyable` Conformance (WWDC24-10170)

For container types like `Job<Action>`, you can express "Job is Copyable when its Action is":

```swift
struct Job<Action: Runnable & ~Copyable>: ~Copyable { ... }
extension Job: Copyable where Action: Copyable { }
```

This lets the same generic type serve both copyable and noncopyable use sites.

### 2.5 Standard Library Adoption (WWDC24-10170)

Optional, UnsafePointer, and Result now support noncopyable wrapped types in Swift 6. This means you can now write:

```swift
init?(filename: String) -> File?  // failable init for noncopyable File
```

---

## 3. Swift Performance Mental Model (WWDC24-10217)

John McCall's "Explore Swift performance" is a foundational reference that maps Swift features to four low-level costs.

### 3.1 The Four Costs

Every performance concern in Swift reduces to one or more of:
1. **Function call costs** -- argument passing, dispatch resolution, frame allocation, optimization barriers
2. **Memory layout** -- inline vs. out-of-line, dynamic vs. static size
3. **Memory allocation** -- global, stack, or heap (in increasing cost)
4. **Value copying** -- including hidden retains/releases of nested references

### 3.2 Static vs. Dynamic Dispatch (WWDC24-10217)

The dispatch kind is determined by **where** a method is declared:

| Declaration site | Dispatch | Why |
|---|---|---|
| Protocol body (requirement) | Dynamic | Polymorphic |
| Protocol extension (default impl) | Static | Resolved at compile time |
| Final class / struct method | Static | Compiler inlines |
| Open class method | Dynamic | Subclass override possible |

**Performance tip:** Static dispatch enables inlining and generic specialization, often resulting in 10-100x speedups for hot loops.

### 3.3 The CallFrame Trick

Synchronous function call frames are allocated by a single subtraction from the stack pointer. The compiler emits this subtraction *unconditionally* to save the return address -- so allocating local variables in the CallFrame is "as close to free as it gets." (WWDC24-10217)

### 3.4 Async Function Internals -- The Slab Allocator

Async functions DO NOT allocate from the C stack. Each Task holds slabs of memory. When an async function "allocates a stack frame," it asks the task for memory from the current slab. Only if the slab fills does it call malloc.

> "Because this allocator is only used by a single task and uses a stack discipline, it's typically significantly faster than malloc." (WWDC24-10217)

**Hidden gem:** Async functions are split at compile time into N+1 partial functions, where N = number of suspension points. Only ONE partial function is on the C stack at any time. Suspension just returns normally, immediately freeing the C thread.

### 3.5 The 3-Pointer Existential Buffer (WWDC24-10217)

Values stored as a protocol type (`var x: AnyDataModel`) live in a fixed 3-pointer buffer. If the value fits inline -- great. If it doesn't -- heap allocation. **Practice:** Prefer homogeneous arrays of generic types (`[some MyProto]`) over heterogeneous arrays of existentials (`[any MyProto]`) when you don't actually need polymorphism per element. The generic version specializes; the existential version doesn't.

### 3.6 Defensive Copies of Class Properties (WWDC24-10217)

> "When the storage is in a class property... it can be hard for Swift to prove that the property isn't modified at the same time, so it may need to add a defensive copy."

Reading `myObject.array` to pass to a function may copy the array (retain a buffer reference). You can avoid this by binding to a local first if the lifetime is clear.

---

## 4. Embedded Swift (WWDC24-10197, 10136)

### 4.1 What It Is

Embedded Swift is a compilation mode -- not a separate language -- producing tiny standalone binaries (KB-sized) for microcontrollers (ARM, RISC-V) and even the Apple Secure Enclave Processor.

### 4.2 What's Excluded

To shrink the runtime:
- Reflection / Mirror
- `Any` type
- Existentials
- Most of Foundation

But: most idiomatic Swift code (structs, classes, protocols, generics, generic specialization) still works. Swift Concurrency is partially supported.

### 4.3 Real Adoption

> "The Apple Secure Enclave Processor uses Embedded Swift." (WWDC24-10136)

Also: Playdate games, smart-home microcontrollers. Use C/C++ interop to incrementally adopt.

---

## 5. Swift Testing -- The New Default (WWDC24-10179, 10195)

Swift Testing is the **new default** test template in Xcode 16. XCTest is not deprecated -- both can co-exist in one target -- but Swift Testing is the future.

### 5.1 The Four Building Blocks

1. **`@Test`** macro -- marks a function as a test (global or instance method, can be `async`/`throws`)
2. **`#expect` / `#require`** macros -- single check API (no `XCTAssertEqual`/`XCTAssertGreaterThan` zoo)
3. **Traits** -- attach metadata or behavior (`.disabled(...)`, `.bug(...)`, `.tags(.spicy)`, `.timeLimit(.minutes(1))`, `.serialized`)
4. **`@Suite` types** -- a fresh instance is created per test (struct preferred for value semantics; deinit replaces tearDown for class/actor suites)

### 5.2 #expect vs. #require (WWDC24-10179)

```swift
#expect(user.name == "Alice")     // logs failure, continues
let video = try #require(library["v1"])  // throws, test stops
```

`#require` is the replacement for "stop the test early" patterns -- including unwrapping optionals safely.

### 5.3 Parameterized Tests -- The Killer Feature (WWDC24-10179, 10195)

```swift
@Test(arguments: ["Scotland Coast", "Iceland Falls", "Norway Bay"])
func mentionedContinents(videoName: String) throws {
    let library = VideoLibrary()
    let video = try #require(library[videoName])
    #expect(video.continents.count == 1)
}
```

Each argument runs as an independent, **parallelized** test case. Re-runnable individually in Xcode 16. Up to 2 collections supported (every combination is tested, so use `zip` to pair instead of cross-multiply).

### 5.4 `withKnownIssue` -- Better Than Skipping (WWDC24-10195)

```swift
withKnownIssue("Server flake -- tracked in FB12345") {
    try makeIceCream()
}
```

The test still compiles and runs. If the function throws, it's reported as **expected failure** (not a real failure). When the issue is fixed and the function stops throwing, the test alerts you so you can remove the wrapper. Strictly superior to `.disabled` in most cases.

### 5.5 `CustomTestStringConvertible` -- Better Failure Output (WWDC24-10195)

Conform your model types to this protocol for concise test-only descriptions, without affecting production code.

### 5.6 Tags Are NOT a Replacement for Suites (WWDC24-10195)

Tags are cross-cutting (e.g., `.spicy`, `.caffeinated`); suites give source-level structure. The new test plan editor in Xcode 16 includes/excludes by tag with "match all" / "match any" semantics.

### 5.7 Parallelism Is On By Default (WWDC24-10195)

> "Parallel testing is enabled by default in Swift Testing... For the first time, you can run parallel tests on all physical devices."

Order is randomized. The `.serialized` trait can opt out per-suite or per-parameterized-test, but you should refactor for parallelism instead.

### 5.8 Confirmations for Multi-Fire Callbacks (WWDC24-10195)

```swift
await confirmation(expectedCount: 10) { confirm in
    eat(cookies: 10) { _ in confirm() }
}
```

Swift 6 makes `var counter = 0` from a callback unsafe -- confirmations are the safe pattern.

### 5.9 Migration Tips (WWDC24-10179)

- XCUITest, XCTMetric, performance tests -- KEEP using XCTest (unsupported in Swift Testing)
- Don't mix `XCTAssert*` calls with `#expect` in the same test
- The word "test" is no longer needed in test function names
- Xcode 16's Test Report supports both side-by-side

---

## 6. SwiftData -- History, Migration, Custom Stores

### 6.1 SwiftData History API (WWDC24-10075)

New `History` API tracks every insert/update/delete since a given timestamp. Use cases:
- Sync to a server
- Detect changes from app extensions / widgets
- Implement undo/redo

```swift
let history = try context.fetchHistory(predicate)
for transaction in history {
    for change in transaction.changes { ... }
}
```

**Hidden gem:** History entries persist across app launches. Tombstones survive deletes -- you get the deleted object's PersistentIdentifier so you can sync the deletion remotely.

### 6.2 Custom Data Stores (WWDC24-10138)

You can plug your own backend behind the SwiftData API surface (JSON file, SQLite directly, remote server). Implement the new `DataStore` protocol. Useful for read-only caches, app-extension shared stores, or migration from legacy formats.

### 6.3 `@Previewable` and Schema Updates (WWDC24-10137)

- New compound uniqueness constraints
- Reverse relationships still recommended for explicit modeling
- Better error messages for migration mistakes

---

## 7. Cross-References & Recommended Watch Order

For Swift 6 adoption:
1. **WWDC24-10136** (What's new in Swift) -- broad overview
2. **WWDC24-10169** (Migrate your app) -- hands-on
3. **WWDC24-10170** (Consume noncopyable) -- if you use them
4. **WWDC24-10217** (Explore Swift performance) -- foundational background

For testing modernization:
1. **WWDC24-10179** (Meet Swift Testing)
2. **WWDC24-10195** (Go further) -- parallelism + parameterization

For SwiftData:
1. **WWDC24-10137** (What's new) → **10075** (History) → **10138** (Custom store)
