# Swift 5 / 5.1 Language & Swift Packages — WWDC 2019 Analysis

**Sessions covered:** 402 (What's New in Swift), 415 (Modern Swift API Design), 408 (Adopting Swift Packages in Xcode), 410 (Creating Swift Packages), 416 (Binary Frameworks in Swift), 409 (What's New in Clang and LLVM)

## Headline

Swift 5 (March 2019) achieved **ABI stability** — the runtime is now part of the OS. Swift 5.1 (Xcode 11) achieved **module stability** — frameworks compiled with one compiler version can be consumed by another. Together with Swift Package Manager integrated into Xcode, this is the year Swift becomes a true platform-level language. Property wrappers, function builders, and opaque return types (`some View`) underpin SwiftUI's syntax.

## ABI Stability (402)

- Swift 5 runtime ships in iOS 12.2+ / macOS 10.14.4+ / tvOS 12.2+ / watchOS 5.2+.
- Apps built with Swift 5 use the OS runtime — **no embedded Swift runtime in the app** when running on supported OSes. **PERFORMANCE**: removes ~30MB from your IPA on download (App Store strips the embedded copy automatically).
- **HIDDEN GEM**: launch-time overhead of Swift over Objective-C apps drops from ~5% in Swift 4.2 to **0%** in Swift 5 with the in-OS runtime.

## Module Stability (402, 416)

- New `.swiftinterface` text-based module manifest format. Looks like Swift source code.
- Future Swift compilers can read interfaces produced by older compilers — no more "Compiled module was created by a newer version of the compiler" errors when sharing binary frameworks.
- Enable with **Build Libraries for Distribution** (`BUILD_LIBRARY_FOR_DISTRIBUTION = YES`).

## XCFrameworks (416)

- New bundle format: a single `.xcframework` containing variants for **device + simulator + Mac (AppKit) + Mac (Catalyst) + every other platform**. Replaces fat-binary hacks (`lipo`-merging device + simulator) which never properly worked across architectures.
- Build via `xcodebuild -create-xcframework -framework ./iOS.framework -framework ./Sim.framework -output Foo.xcframework`.
- Supports static and dynamic libraries, frameworks, headers.
- **URGENT**: pre-Swift-5 binary frameworks shipped to your users require either a source build or an XCFramework rebuild for Catalyst compatibility.

## Swift Package Manager in Xcode (408, 410)

- File → Swift Packages → Add Package Dependency. Resolve by URL. Choose version rules (semantic versioning).
- **Local packages**: drag a folder containing `Package.swift` into your project — great for refactoring shared code out of an app target.
- **Versioning rules**: Swift packages use SemVer strictly. `1.x.y` patch updates auto-resolved; minor updates added APIs only; major updates can break.
- File → New → Swift Package creates a standalone library you can publish to GitHub directly from Xcode (Source Control → Create Remote).
- Tests in `Tests/MyPackageTests` use XCTest as usual.
- **HIDDEN GEM**: SwiftPM in Xcode 11 can produce iOS, watchOS, tvOS, and Mac variants from a single `Package.swift` — no platform-specific configuration needed unless you use platform-specific APIs (in which case use `#if canImport(UIKit)`).

## Property Wrappers (Swift 5.1 Feature) (415)

The mechanism behind `@State`, `@Binding`, `@Published`, `@EnvironmentObject` in SwiftUI.

```swift
@propertyWrapper
struct UserDefault<T> {
    let key: String
    let defaultValue: T
    var wrappedValue: T {
        get { UserDefaults.standard.object(forKey: key) as? T ?? defaultValue }
        set { UserDefaults.standard.set(newValue, forKey: key) }
    }
}

struct Settings {
    @UserDefault(key: "username", defaultValue: "") var username: String
}
```

The `$` projection (e.g., `$username` for a `Binding`) comes from a `projectedValue` property on the wrapper.

## Opaque Return Types: `some View` (402, 415)

```swift
func makeView() -> some View { Text("Hi") }
```

- Reverses generics: caller knows the protocol the value conforms to but **not** the underlying type. The compiler still tracks the concrete type for performance.
- Allows you to return complex generic stacks (`HStack<TupleView<(Text, Image, Spacer)>>`) without writing them out.
- **HIDDEN GEM**: this is what makes SwiftUI's body composition syntactically clean. Without `some View`, you'd be writing 3-line generic types every function.

## Function Builders / @ViewBuilder (402)

- Swift 5.1 feature originally called `@_functionBuilder`, later renamed `@resultBuilder` (Swift 5.4).
- Translates closure code with implicit `if`, `for`, multiple statements into a single expression.
- This is what lets you write declarative SwiftUI bodies without commas, Array literals, or `return`.

## Memberwise Initializers Improvements (402)

```swift
struct Point {
    var x: Double = 0
    var y: Double = 0
}
let p = Point(x: 3)  // y defaults to 0  ← NEW in Swift 5
```

Previously this didn't compile — synthesized memberwise inits required all values. Contributed by an open-source contributor still in high school. **HIDDEN GEM**.

## SIMD Types in Standard Library (402)

- `SIMD2<Float>`, `SIMD3<Double>`, `SIMD4<Int32>`, etc. moved into the standard library.
- Pointwise operators: `let mask = a .> b` returns `SIMDMask`.
- Used heavily by RealityKit for vector math.

## String Performance (402)

- Swift 5 switched String's internal Unicode representation from UTF-16 to **UTF-8**.
- **PERFORMANCE**: passing a `String` to a C API now requires zero allocation, zero copy, zero transcoding (just pass the pointer).
- Dictionary↔NSDictionary bridging is 1.6× faster.
- String→NSString bridging operations up to 15× faster.
- Small string optimization extended from ASCII to all Unicode (~15-character inline buffer).
- SwiftNIO web server saw a 20% throughput increase from this change alone.
- New customizable `String` interpolation lets libraries build custom DSLs (e.g., `"[\(localized: key)]"`).

## Modern Swift API Design (415)

- **Drop framework prefixes** in Swift-only APIs. SwiftUI is `View`, not `SUIView`. RealityKit is `Entity`, not `RKEntity`. Module name disambiguates.
- **Prefer structs over classes** unless you need: identity, reference counting for resource management, shared mutable state, or true polymorphism.
- **Start with concrete types**, factor out a protocol only when you have multiple implementations sharing real behavior.
- **Generic types > protocol hierarchies** for some cases. SwiftUI's `Stack` views demonstrate this.
- **`@dynamicMemberLookup` with key paths** (Swift 5.1) — type-safe forwarding to wrapped types. Used inside RealityKit and SwiftUI.

## Editor / Tooling Improvements (402, 412)

- SourceKit-LSP open-sourced for use in any editor (VS Code, Sublime, Vim).
- LLDB `po` improvements; new `vo` and view-debugging hooks.
- Swift Compiler's diagnostic engine rewritten for clearer error messages.

## Cross-references

- Property wrappers in SwiftUI: 226 (Data Flow), 216 (SwiftUI Essentials).
- XCFrameworks for distribution: 235 (Catalyst).
- Swift packages workflow: 408, 410.
- Combine relies on opaque return types and function builders: 721, 722.
