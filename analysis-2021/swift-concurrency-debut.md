# Swift Concurrency Debut (WWDC 2021)

The most consequential language change in Swift since Swift 1: async/await, structured concurrency, actors, AsyncSequence, and `@MainActor`. Below are the high-leverage findings extracted from the 2021 transcripts.

## Sessions covered
- WWDC21-10132 — Meet async/await in Swift
- WWDC21-10133 — Protect mutable state with Swift actors
- WWDC21-10134 — Explore structured concurrency in Swift
- WWDC21-10254 — Swift concurrency: Behind the scenes
- WWDC21-10058 — Meet AsyncSequence
- WWDC21-10095 — Use async/await with URLSession
- WWDC21-10194 — Swift concurrency: Update a sample app
- WWDC21-10019 — Discover concurrency in SwiftUI
- WWDC21-10017 — Bring Core Data concurrency to Swift and SwiftUI
- WWDC21-10192 — What's new in Swift
- WWDC21-10216 — ARC in Swift: Basics and beyond

## Best practices

- **Mark UI-facing observable objects with `@MainActor`** so the SwiftUI run-loop ordering of `objectWillChange` → state mutation → next tick is guaranteed (WWDC21-10019). Mutating from off-main-actor can silently swallow updates because SwiftUI's snapshot is taken before the change actually lands.
- **Always omit `get`/`fetch`-style verbs in async function names** that previously named "leading-get" callbacks. Apple's import rule strips the leading word when generating async overloads (WWDC21-10132).
- **Use `Task {}` only to bridge sync → async; prefer structured concurrency (`async let`, `withTaskGroup`)** when work is scoped to the function (WWDC21-10134). Detached tasks lose actor inheritance, priority, and task-locals.
- **Cooperatively cancel inside loops** with `try Task.checkCancellation()` at iteration boundaries — cancellation is a flag, not a kill (WWDC21-10134).
- **Prefer `withCheckedContinuation` over `withUnsafeContinuation`** for legacy bridges; the runtime detects double-resume and missing-resume bugs (WWDC21-10132).

## Hidden gems

- `URL` itself has `.lines` and `.bytes` async sequence accessors. You don't need URLSession at all for simple line-by-line reads from files OR network endpoints (WWDC21-10058).
- `FileHandle.bytes` returns an `AsyncSequence<UInt8, Error>` — you can finally stream a file without `read` callbacks or DispatchIO (WWDC21-10058).
- `for try await line in url.lines { … }` works against an HTTP endpoint that streams JSON-Lines, giving you live-update UIs in 4 lines of code (WWDC21-10058, WWDC21-10095).
- `URLSession.bytes(from:delegate:)` returns the response headers immediately and streams the body. Pair with `prefersIncrementalDelivery = true` to opt into incremental processing (WWDC21-10094, WWDC21-10095).
- Per-task delegate on URLSession: you can attach an authentication delegate to a single request without a session-wide delegate. Strongly held until the task finishes (WWDC21-10095).
- `NotificationCenter.notifications(named:)` returns an AsyncSequence — `for await note in NotificationCenter.default.notifications(named: …) { … }` replaces add-observer/remove-observer plumbing (WWDC21-10058).
- `NSAsyncSequence`'s `firstWhere`/`drop`/`map`/`filter` all exist and behave like `Sequence` — pattern matching translates verbatim (WWDC21-10058).

## Performance

- Swift concurrency's cooperative thread pool spawns **only as many threads as CPU cores**. Compare to GCD which spawns up to 64 threads on contention. Thread explosion is impossible by construction when you stay inside the async/actor world (WWDC21-10254).
- An `await` is a **function call's worth of cost**, not a context switch. Continuations live as a singly-linked list of async frames on the heap, the OS stack is reused, and the same thread (often) resumes you (WWDC21-10254).
- Actor hopping is *not* a thread switch. When the destination actor is uncontended, the runtime turns the existing thread's work item into the new actor's work item. Two-call ping-pong is O(function-call), not O(context-switch) (WWDC21-10254).
- `MainActor` hops *are* real thread switches because the main thread is disjoint from the cooperative pool. **Batch work that touches MainActor**: process arrays in one hop instead of looping with one hop per element (WWDC21-10254).
- Foundation now has a Swift-native JSON encoder/decoder rewrite on Linux with measurable wins; on Apple platforms, ARC's new "lexical lifetimes" (Optimize Object Lifetimes setting) cuts retain/release ops noticeably (WWDC21-10192, WWDC21-10216).

## Migration guidance

- Don't async-ify everything: each task has setup cost. A child task to read a single `UserDefaults` value is slower than the synchronous read (WWDC21-10254).
- Don't hold locks across an `await`. Atomicity is broken at every suspension point — if you need critical-section semantics, wrap in synchronous code (WWDC21-10254).
- **Banned primitives inside cooperative pool work: semaphores, condition variables, `dispatch_semaphore_wait`.** They hide dependencies from the runtime and can deadlock the entire app. `os_unfair_lock`/`NSLock` are tolerated for tight critical sections only (WWDC21-10254).
- Validate this with `LIBDISPATCH_COOPERATIVE_POOL_STRICT=1` env var — Xcode's run scheme can set it. The debug runtime asserts on forward-progress violations (WWDC21-10254).
- For Core Data: `NSManagedObjectContext.perform { … }` is now async/throwing. Use `await context.perform { … }` to bridge into the context's serial queue from any async context (WWDC21-10017).

## Cross-references

- `Task.detached(priority: .background)` for fire-and-forget background work that should NOT inherit the calling actor or priority. Most other times use `Task {}` (WWDC21-10134).
- Actor reentrancy means **assumptions don't hold across `await`** — re-check cache state after suspension. Classic bug: image-cache actor resumes after a download, blindly writes a now-stale image (WWDC21-10133).
- `nonisolated` on an actor method/property treats it as outside the actor — required to satisfy synchronous protocol requirements like `Hashable.hash(into:)` (WWDC21-10133).
