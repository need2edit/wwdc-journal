# Swift 4: Codable, KeyPaths, String, Concurrency Foundations — WWDC 2017 Analysis

**Sessions covered:** 402 (What's New in Swift), 212 (What's New in Foundation), 207 (What's New in Cocoa), 411 (What's New in LLVM), 414 (Engineering for Testability)

## Headline

Swift 4 is a **refinement** release after the upheaval of Swift 3. The big language additions: `Codable` for one-line JSON/property-list serialization, smart `KeyPath` literals with strong typing, a unified `String` overhaul (now `Collection` again), `private` extended through extensions, and the foundations laid (literally — exclusivity enforcement) for a future concurrency model. Critically, **Swift 3.2 and Swift 4 coexist in the same binary** — migrate at your own pace, target by target.

## Source Compatibility Story (402)

- Swift 4 compiler has a **Swift 3.2 mode** — same compiler, emulates Swift 3 syntax and SDK projection.
- Set `SWIFT_VERSION` per target. Mix Swift 3.2 and Swift 4 frameworks in the same app.
- The migrator is opt-in, per-target. **HIDDEN GEM**: don't migrate everything at once — flip your app target first, leave dependencies on 3.2 until they ship 4 versions.

## Codable — Effortless JSON / PList (402, 212)

Conform a type to `Codable` (= `Encodable & Decodable`). For types whose stored properties are themselves `Codable`, **the compiler auto-synthesizes `init(from:)` and `encode(to:)`**.

```swift
struct Photo: Codable {
    let id: UUID
    let title: String
    let dimensions: CGSize
    let takenAt: Date
}

let json = try JSONEncoder().encode(photo)
let restored = try JSONDecoder().decode(Photo.self, from: json)
```

- All standard library types, `Foundation` value types, `Date`, `Data`, `URL`, optionals, arrays, dictionaries, and enums with raw values are `Codable` out of the box.
- Customize via nested `enum CodingKeys: String, CodingKey` to rename JSON keys.
- Override `init(from:)` and `encode(to:)` for deeply custom mapping (e.g. inheritance, polymorphism).
- **Encoders/decoders supplied**: `JSONEncoder/Decoder`, `PropertyListEncoder/Decoder`, plus an extensible `Encoder`/`Decoder` protocol so you can roll a YAML, MessagePack, or XML adapter.

**HIDDEN GEM**: `JSONDecoder.dateDecodingStrategy = .iso8601` and `keyDecodingStrategy = .convertFromSnakeCase` cover the two most common server gotchas with one line each. The `.formatted(_:)` strategy accepts a `DateFormatter` for legacy APIs.

**HIDDEN GEM**: nested containers let you flatten or unflatten JSON shape vs Swift shape. Override `init(from decoder:)`, call `decoder.container(keyedBy:)`, then `nestedContainer(keyedBy:forKey:)` to dive into a sub-object.

**MIGRATION**: `NSCoding` + `NSKeyedArchiver` still works for Objective-C interop, but for pure-Swift types `Codable` replaces it — including for `UIDocument` save formats. Codable types can use `PropertyListEncoder` for `.plist` archives identical to `NSKeyedArchiver`'s output.

## Smart KeyPaths (402, 207)

Replace stringly-typed KVC `#keyPath()` with strongly-typed key path literals:

```swift
struct Presenter {
    var name: String
    var coPresenter: Presenter?
}

let nameKey = \Presenter.name                     // type: WritableKeyPath<Presenter, String>
let coPresenterNameKey = \Presenter.coPresenter?.name

print(me[keyPath: nameKey])                       // "Josh"
me[keyPath: nameKey] = "Doug"                     // mutating set, type-checked at compile time
```

- Literal syntax `\Type.path` resolves at compile time. Wrong path = compile error.
- Foundation adds **block-based KVO** that takes a `KeyPath`:

```swift
let token = object.observe(\.name, options: [.new, .old]) { obj, change in
    print("name changed from \(change.oldValue!) to \(change.newValue!)")
}
// token deinitializes → observation removed automatically
```

**HIDDEN GEM**: this is leak-safe. The returned `NSKeyValueObservation` token automatically `invalidate()`s on `deinit`. Just store it as a `var` and never worry about removing observers manually again.

## Class + Protocol Composition (402)

```swift
func animate(_ items: [UIControl & Shakable]) { … }
```

Swift 4 finally allows expressing "a class that also conforms to a protocol" — long present in Objective-C as `NSView<NSTextInputClient> *`. Imported APIs that previously had to drop the protocol now project correctly.

## Private Extends Through Extensions (402)

In Swift 3, `private` was per-lexical-scope. In Swift 4, `private` declarations are visible inside all extensions of the same type **in the same source file**. This kills 90% of the use cases for `fileprivate` and lets you split a type into clean extensions without artificial visibility leaks.

```swift
struct Date {
    private let secondsSinceReference: Double   // visible in extensions below
}

extension Date: Equatable {
    static func == (a: Date, b: Date) -> Bool {
        return a.secondsSinceReference == b.secondsSinceReference   // ← compiles in Swift 4
    }
}
```

## String Overhaul (402)

`String` is once again a `Collection` (it stopped being one in Swift 2):

```swift
let greeting = "Hello, world"
let count = greeting.count                    // direct, was greeting.characters.count
greeting.contains("world")                    // direct, no .characters
greeting.split(separator: ",").map { … }      // returns Substrings, not Strings
```

- `Substring` is a NEW type — a slice of a String that shares storage. Cheap to take, expensive to keep around (holds the parent's storage). Convert to `String(substring)` when persisting.
- **PERFORMANCE**: storage moved to UTF-8 internally (was UTF-16). Bridging Swift `String` to a C `char *` is now zero-copy. `String→NSString` interop is significantly faster.
- Multi-line string literals via triple-quote `"""` … `"""`. Indentation is normalized to the closing delimiter's indent.
- `String.init(unicodeScalarLiteral:)` and `String.init(unicodeCodePoints:)` for low-level construction.

## Generic Sugar (402)

- **One-sided ranges**: `array[2...]`, `array[..<5]`, `array[...]`. The third form is a synonym for `array[array.startIndex..<array.endIndex]` — useful for `ArraySlice`.
- **Generic subscripts**: index by any type that fits the constraints. Foundation uses this so `dictionary[keyPath: \Type.path]` returns a typed value.
- `MutableCollection` reordering and `RangeReplaceableCollection.removeAll(where:)` make in-place mutation natural.

## Exclusive Access to Memory (402, "Law of Exclusivity")

Swift now enforces at compile time (and runtime in debug) that no two simultaneous accesses to the same memory location overlap if at least one is a write. This rules out subtle aliasing bugs — but more importantly, it lays the groundwork for Swift's future ownership model and concurrency features.

```swift
var x = 0
modifyTwice(&x, &x)   // ERROR: simultaneous accesses to 'x'
```

**MIGRATION**: most code is unaffected. The classic violation is `swap(&array[i], &array[j])` for in-place sorting — replace with `array.swapAt(i, j)`. The standard library added overloads for the common cases.

## Foundation Refinements (212)

- **`MeasurementFormatter`** — formatted strings for `Measurement<Unit>` (e.g. `Measurement(value: 100, unit: UnitMass.grams)` → "100 g" / "3.5 oz" by locale).
- **`DateInterval`** — first-class type for "from-to" date ranges with intersection, contains, comparison.
- **`ISO8601DateFormatter`** with options for fractional seconds, time zones, week-of-year.
- **`URLSessionDataTask` async/await prefigured** — the new `URLSession` Combine-style hooks (Combine itself is two years away) and the modernized progress reporting on every load API.

## What's New in Cocoa (207)

- **`UIScrollView.adjustedContentInset`** — read-only sum of `contentInset` + `safeAreaInsets`. The new `contentInsetAdjustmentBehavior` (`.automatic` / `.scrollableAxes` / `.never` / `.always`) gives explicit control over how scroll views handle the new safe area.
- **`UIContextualAction`** in `UISwipeActionsConfiguration` — the long-rumored multi-action swipe (mail-style) is finally public API. Both leading and trailing edges supported. `performsFirstActionWithFullSwipe` mirrors Mail's full-swipe-to-archive.
- Block-based KVO (already covered above).
- **`UITableView.separatorInsetReference`** — switch between absolute insets or deltas from the system default.

## Compiler & Tools (411)

- **Index-while-building** — Xcode 9 indexes as a side effect of compilation, eliminating the standalone "indexing" pass. Search/jump-to-definition works immediately on first build.
- **Refactoring for Swift** — Rename, extract method, extract local, generate memberwise initializer, fill switch cases. The infrastructure ships in the open-source Swift project — third parties can add refactorings.
- **PERFORMANCE**: new build system (in Xcode 9, opt-in; default in Xcode 10) is written in Swift on top of LLBuild and dramatically faster at incremental builds for large projects.
- The Swift Package Manager grew Xcode IDE awareness (still preview-quality in Xcode 9, becomes first-class in 11).

## Engineering for Testability (414)

- **Dependency injection over singletons** — wrap collaborators in protocols, supply real or fake conformers. Every singleton kills testability.
- **Use `@testable import`** to test internal entities without exposing them publicly.
- **Test the SEAMS, not the whole stack** — fake the network layer; don't run real HTTP from unit tests.
- **HIDDEN GEM**: `XCTContext.runActivity(named:)` groups assertions in the test report into named sections — vastly improves failure diagnostics on long tests. Add screenshots inside an activity with `XCTAttachment(image:)`.
- `measure { }` for performance baselines — `XCTPerformanceMetric.wallClockTime` is the default; new in 2017 is per-iteration variance reporting.

## Cross-references

- See `files-document-browser.md` — `UIDocument` saving naturally pairs with `Codable`.
- See `coreml-vision-nlp.md` — model metadata JSON parses cleanly with `Codable`.
- See `ios11-design-language.md` — the `safeAreaInsets`/`adjustedContentInset` model unlocks iPhone X edge-to-edge layouts.
