# Swift 3 Migration & Modernization — WWDC 2016 Analysis

**Sessions covered:** 402 (What's New in Swift), 403 (Swift API Design Guidelines), 416 (Understanding Swift Performance), 419 (Protocol and Value Oriented Programming), 207 (What's New in Foundation for Swift), 720 (Concurrent Programming With GCD in Swift 3), 404 (Getting Started with Swift), 405 (What's New in LLVM), 408 (Introducing Swift Playgrounds), 415 (Going Server-side with Swift Open Source)

## Headline

Swift 3 is the **single biggest source-breaking release Swift will ever ship**. The "Grand Renaming" applied the new API Design Guidelines (SE-0023) to the entire standard library, all imported Cocoa/Cocoa Touch, Core Graphics, Grand Central Dispatch, Foundation. Every Swift file in your project will change. The migrator handles ~95%; the remaining 5% benefits from a hand pass to use new initializers, new value types, and new Swift idioms.

Apple shipped Swift 2.3 alongside Swift 3 as an interim option (Swift 2.2 syntax, new SDKs, App Store accepts both) — but Playgrounds, the new documentation viewer, and Thread Sanitizer all require Swift 3.

## The Grand Renaming — apply these mental rules

### 1. Omit needless words at the call site (SE-0005)

Argument labels and base names should not repeat type information. The strong type system already conveys it.

```swift
// Swift 2
array.appendContentsOf(other)
url.URLByAppendingPathComponent("foo")
NSURL.fileURL(...)

// Swift 3
array.append(contentsOf: other)
url.appendingPathComponent("foo")
URL.init(fileURLWithPath:)  // also: url.isFileURL (was returning Bool but unclear)
```

### 2. First argument labels — read grammatically

Drop the first label only when the call reads naturally as English without it. Add prepositions (`with`, `at`, `from`) on the first label when needed.

```swift
remove(ted)               // reads: "remove ted"
remove(at: index)         // reads: "remove at index"
addChild(view, at: point) // "add child view at point"
dismiss(animated: true)   // can't say "dismiss true"
```

### 3. Methods are verbs, properties are nouns; mutating uses ed/ing

| Mutating | Non-mutating |
|----------|--------------|
| `array.sort()` | `array.sorted()` |
| `array.reverse()` | `array.reversed()` |
| `url.appendPathComponent(x)` | `url.appendingPathComponent(x)` |

### 4. Foundation enums get scoped

`NSNumberFormatterStylePadAfterPrefix` (a global) becomes `NumberFormatter.PadPosition.afterPrefix`. Done via Objective-C's new `NS_TYPED_ENUM`/`NS_EXTENSIBLE_STRING_ENUM` — even string constants like `NSNotification.Name` are strongly-typed enums now.

### 5. The NS prefix is dropped in Swift Foundation

`NSDate` → `Date`, `NSData` → `Data`, `NSURL` → `URL`, `NSURLComponents` → `URLComponents`, `NSCharacterSet` → `CharacterSet`, `NSIndexSet` → `IndexSet`, `NSIndexPath` → `IndexPath`, `NSPersonNameComponents` → `PersonNameComponents`, `NSDateComponents` → `DateComponents`, `NSCalendar` → `Calendar`, `NSTimeZone` → `TimeZone`, `NSUUID` → `UUID`, `NSAffineTransform` → `AffineTransform`, plus `NSNotification` → `Notification`, `NSError` → `Error`, more.

These are now **value types** (structs) bridging back to their NS classes via the same mechanism as `String`↔`NSString`. Mutation is in-place and copy-on-write.

## Foundation value types — the big behavior change (session 207)

`Date`, `Data`, `URL`, `IndexPath`, `IndexSet`, `CharacterSet`, `Notification`, `URLComponents`, `URLRequest`, `URLQueryItem`, `Measurement`, `MeasurementFormatter` (and many more) are now value types.

**Bridging cost (HIDDEN GEM):**
- Large value types (Data, IndexSet) hold a reference internally and copy-on-write. Crossing the Obj-C bridge into a `@NSCopying` property triggers a copy on the Obj-C side; in practice immutable data → just a retain.
- Small value types (Date) are inline. Crossing into Obj-C **allocates** an `NSDate` instance per call. NSDate allocation is heavily optimized but it's not free.
- **Don't churn back and forth across the bridge in tight loops.** Stay in Swift land for hot code.

**HIDDEN GEM:** New default-argument `DateComponents` initializer takes optional named arguments (`DateComponents(year: 2016, month: 6)`). No more mutating after construction. Migrator won't do this for you — re-do the migrator's output.

**HIDDEN GEM:** New `URLResourceValues` struct gives strongly-typed read of file attributes — `creationDate: Date?`, `isRegularFile: Bool?`, `volumeMaximumFileSize: Int?`. No more `[String: AnyObject]` dictionary lookups.

**HIDDEN GEM:** Closure-based `Timer` API — `Timer(timeInterval: 60, repeats: false) { _ in … }`. No more selectors. RunLoop and Thread also got scheduled-with-block forms.

## Performance fundamentals (session 416)

Three dimensions to consider for any Swift type:

| | Stack vs Heap | Reference counting | Method dispatch |
|---|---|---|---|
| **`struct`/`enum`** with no refs | Stack | None | Static |
| **`struct`/`enum`** with N refs | Stack (struct) + Heap (refs) | N retain/release per copy | Static |
| **`final class`** | Heap | retain/release | Static |
| **`class`** (subclassable) | Heap | retain/release | Dynamic (vtable) |
| **Protocol type** with small (≤3 word) value | Stack (existential container, 5 words: 3 buffer + value-witness-table + protocol-witness-table) | Counted on contained refs | Dynamic via PWT |
| **Protocol type** with large value | Heap (boxed in existential) | Counted | Dynamic via PWT |
| **Generic** `<T: P>` (specialized) | Same as concrete T | Same as T | Static (after specialization) |
| **Generic** `<T: P>` (unspecialized) | Heap if T large | Counted | Dynamic via PWT |

**HIDDEN GEM (BEST PRACTICE):** Protocol-typed properties with large structs cost a heap allocation per assignment. Wrap the storage in a `class LineStorage` and use copy-on-write via `isUniquelyReferenced(_:)` to convert the heap allocation cost into a cheaper retain/release cost. This is what `String`, `Array`, `Data`, `Dictionary` all do internally.

**PERFORMANCE:** Whole-Module Optimization is **on by default** in Xcode 8 for new projects. Existing projects get a one-shot modernization suggestion — accept it. WMO enables specialization across files (a protocol-typed call can devirtualize when the compiler sees both ends).

**PERFORMANCE:** Swift 3 made dictionary 1.6x faster, string→NSString conversions up to 15x faster (UTF-8 internal storage, zero-copy/zero-transcoding to C APIs). Stack-promoted class instances for array literals.

**PERFORMANCE:** DemoBots sample app shrank ~25% in binary size from Swift 2.2 → Swift 3.

## GCD modernization (session 720)

GCD is now Swift-style:

```swift
// Swift 2
let queue = dispatch_queue_create("…", DISPATCH_QUEUE_SERIAL)
dispatch_async(queue) { … }

// Swift 3
let queue = DispatchQueue(label: "com.example.foo")
queue.async { … }
DispatchQueue.main.async { … }
queue.async(group: group, qos: .userInitiated) { … }
```

**HIDDEN GEM:** New `DispatchPrecondition` — `dispatchPrecondition(condition: .onQueue(queue))` and `.notOnQueue(queue)` to enforce thread invariants.

**HIDDEN GEM:** `DispatchWorkItem` with `.assignCurrentContext` flag captures QoS at creation time, not submission time. Useful for deferred work.

**URGENT (DOCS MISS THIS):** Calling `cancel()` from inside `deinit` → assertion crash in iOS 10. The lock the dispatch source holds during deinit deadlocks if you try to unregister from a queue that is itself driving the deinit. Apple now treats this as an asserted programmer error. **Pattern:** four-step lifecycle for every concurrent object — setup, activate, **explicit `invalidate()` from the main thread**, deallocate. The crash report's "Application Specific Information" field points to the bug.

**HIDDEN GEM:** `unfair_lock` (`os_unfair_lock_t`) replaces `OSSpinLock`. OSSpinLock has a priority inversion bug (low-pri holder blocks high-pri waiter forever). Use `os_unfair_lock` from C; or wrap a mutex in an Obj-C base class (Swift's struct lock can be moved by ARC, breaking the mutex). For most cases just use a serial DispatchQueue with `.sync`.

**HIDDEN GEM:** `DispatchQueue` initialized with `.initiallyInactive` attribute lets you fully configure target/QoS/etc. before any work runs. Required for new dispatch sources too — they have a separate `activate()` API now (initial `resume()` is deprecated for that purpose; `suspend()` and `activate()` are independent counters).

## Other notable language changes

- **Implicitly-unwrapped optionals are local now.** `var x: Int! = 5; let y = x` — `y` is `Int?`, not `Int!`. The IUO is unwrapped only when type-checking *requires* it (e.g. `x + 1` works because `+` needs `Int`).
- **`UnsafePointer<T>` cannot be nil anymore** — use `UnsafePointer<T>?` like every other optional. `if let p = ptr {}` works.
- **Unused-result is now a warning by default.** Mark side-effect-only functions with `@discardableResult`. Assign to `_` to silence: `_ = doSomething()`.
- **Generic constraints moved to a `where` clause** at the end of the signature, not in `<T: P, U: Q where T == U>`. Reads top-down.
- **Argument labels for ALL parameters** by default (no more first-label-omitted-by-default for Cocoa-style methods). Override with `_`.
- **`#selector(...)` and `#keyPath(...)`** for type-safe Objective-C interop. Compiler validates the Swift name maps to an exposed `@objc` member; refactoring works; no string typos.
- **New collection indexing model** — indices are advanced *by the collection*, not by themselves. Removed types like `RandomAccessIndexType` (now subsumed by `Index` + `Collection.index(after:)`).
- **`String` is no longer a `Collection<Character>`** (this changed back in Swift 4 actually; in Swift 3 you still iterate `.characters`).
- **`Float`, `Double`, `CGFloat`, `Float80` all conform to a new `FloatingPoint` protocol family.** `CGFloat.pi` now exists per type — no more `M_PI` cast dance.

## Migration playbook

1. **Don't skip 2.3.** If you can't move to 3 immediately, set the Swift Language Version to 2.3, fix any regressions, ship. Then schedule the 3 migration as its own commit.
2. **Edit → Convert → To Current Swift Syntax** runs the migrator. Every file changes.
3. **After migration, do a hand pass:** convert reference-type creation patterns (`NSMutableData` → `Data` with `var`); use new `DateComponents(year:month:day:)` initializer; switch to closure-based `Timer`; adopt new `URLResourceValues`.
4. **Treat warnings as errors** for Swift in Xcode 8 (now supported, was Obj-C-only). Forces team to address technical debt.

## Best practices summary

- **Use structs by default.** Reach for class only when you need identity (`OperationQueue.main`), reference semantics in a delegate, or you're inheriting from an Obj-C class.
- **Mark non-subclassable classes `final`** so the compiler can devirtualize.
- **Use `@discardableResult` deliberately** — only for functions where the value is genuinely a courtesy.
- **Use `(generic) where`** — keeps signatures readable.
- **Pick `let` whenever possible** — Swift can statically optimize immutable bindings far better.
- **Use `dispatchPrecondition`** liberally to assert thread invariants.

## Hidden gems summary

- DateComponents memberwise initializer with default-nil arguments — replaces "create + mutate" pattern.
- Closure-based `Timer` (and `RunLoop`, `Thread`) — no selectors needed.
- `URLResourceValues` struct → strongly-typed file attribute access (creationDate, isRegularFile, etc.).
- `os_unfair_lock` replaces buggy `OSSpinLock`.
- `dispatchPrecondition(condition: .onQueue(q))` for thread-invariant checks.
- Deinit calling cancel/unregister now traps with a useful Application Specific Information line.
- Whole-Module Optimization is default-on for new Xcode 8 projects.
- `#keyPath(Foo.bar)` validates KVC strings at compile time.

## Cross-references

- Foundation deep dive → analysis-2016/foundation-swift-modernization.md (this file covers it inline)
- GCD invalidation pattern feeds into many subsystems — see analysis-2016/concurrency-best-practices.md
- Performance gems shape watchOS 3 architecture — see analysis-2016/watchos3-performance.md
