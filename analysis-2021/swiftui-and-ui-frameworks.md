# SwiftUI & UI Frameworks (WWDC 2021)

## Sessions covered
- WWDC21-10018 — What's new in SwiftUI
- WWDC21-10022 — Demystify SwiftUI
- WWDC21-10019 — Discover concurrency in SwiftUI
- WWDC21-10021 — Add rich graphics to your SwiftUI app
- WWDC21-10023 — Direct and reflect focus in SwiftUI
- WWDC21-10062 — SwiftUI on the Mac: Build the fundamentals
- WWDC21-10289 — SwiftUI on the Mac: The finishing touches
- WWDC21-10119 — SwiftUI Accessibility: Beyond the basics
- WWDC21-10176 — Craft search experiences in SwiftUI
- WWDC21-10059 — What's new in UIKit
- WWDC21-10064 — Meet the UIKit button system
- WWDC21-10063 — Customize and resize sheets in UIKit
- WWDC21-10057 — Take your iPad apps to the next level
- WWDC21-10052 — What's new in Mac Catalyst
- WWDC21-10053 — Qualities of a great Mac Catalyst app
- WWDC21-10252 — Make blazing fast lists and collection views

## Best practices

- **Get a binding to a collection element by passing `$collection` to `List`/`ForEach`** — the closure receives a `Binding<Element>`. Avoid the old `indices`/subscript trick which forces SwiftUI to re-render the whole list on any change (WWDC21-10018, WWDC21-10022).
- **Use `.task { … }` instead of `.onAppear { Task { … } }`.** `.task` is async by default, ties the task lifetime to the view, and cancels automatically on disappear (WWDC21-10018, WWDC21-10019).
- **Don't over-specify SF Symbol variants.** Pass the base name (e.g. `"heart"`); SwiftUI picks `.fill` automatically inside a tab bar, `.outline` on macOS, etc. via the new `.symbolVariant(...)` system (WWDC21-10018).
- **Use `Table` for multi-column data on macOS/iPadOS**; sortable columns drop in with `KeyPathComparator`. A four-column table with selection and sorting fits on a single slide (WWDC21-10018).
- For Mac Catalyst: prefer **`UIBehavioralStyle.pad`** to keep iPad button stretch-to-fill behavior even when "Optimize Interface for Mac" is on (WWDC21-10052).

## Hidden gems

- `AsyncImage(url:)` — finally a built-in remote image loader. Customizable with phase-based content closure for placeholders, error UIs, and animations (WWDC21-10018).
- `.refreshable { … }` adds pull-to-refresh anywhere; the closure is async. Custom refresh UIs read the action from `@Environment(\.refresh)` (WWDC21-10018).
- `.swipeActions(edge:allowsFullSwipe:) { Button … }` — finally first-class custom swipe actions in SwiftUI lists (WWDC21-10018).
- `Canvas { context, size in … }` — immediate-mode drawing with SwiftUI gestures, accessibility, and Dark Mode support layered on top. `TimelineView` lets you redraw on a schedule for screensaver/Always-On effects (WWDC21-10018, WWDC21-10021).
- `.privacySensitive()` — auto-redacts a view in widgets-on-Lock-Screen and watchOS Always-On display (WWDC21-10018).
- `Material` (`.ultraThinMaterial`, etc.) is now a SwiftUI-native shape style. `.background(.ultraThinMaterial, in: Capsule())` works inline (WWDC21-10018, WWDC21-10021).
- `.searchable(text:)` adds platform-correct search to a `NavigationView` — Mac toolbar, iPad nav bar, watch, tvOS — all handled (WWDC21-10018, WWDC21-10176).
- `FocusState` property wrapper + `.focused($field, equals: .someCase)` modifier finally gives SwiftUI controllable keyboard focus (WWDC21-10018, WWDC21-10023).
- `Markdown in Text("**bold** and [link](https://...)")` works directly. Backed by the new Swift `AttributedString` (WWDC21-10018).
- `.dynamicTypeSize(...)` modifier finally lets you clamp the type-size range without disabling Dynamic Type entirely (WWDC21-10018).
- The built-in `#Preview` macro is *not* in 2021 — but the live preview now has an Accessibility Preview tab showing the textual accessibility tree (WWDC21-10018, WWDC21-10119).
- `accessibilityRepresentation(representation:)` — substitute a custom shape-based slider's accessibility with a real `Slider`. Best-in-class API for custom controls (WWDC21-10119).
- `accessibilityChildren(children:)` — when an element should expose programmatic children that don't exist visually (e.g., a `Canvas` bar chart) (WWDC21-10119).

## Performance

- `@FetchRequest` now provides a binding to its `sortDescriptors`, enabling Core-Data-driven `Table`s with sortable columns in ~5 lines (WWDC21-10018, WWDC21-10017).
- `SectionedFetchRequest` partitions Core Data results into multiple list sections via a single key-path — no manual NSFetchedResultsController section lookups (WWDC21-10017).
- iOS 15 collection-view cell prefetching can give apps **up to ~2x more lead-time** (almost two visual frames) before display, dramatically smoothing scrolling without code changes (WWDC21-10059, WWDC21-10252).
- `UIImage.prepareForDisplay(completionHandler:)` and `UIImage.byPreparingForDisplay()` — async image decode off-main-thread, ready-to-blit. Replaces hand-rolled `Renderer.image` decode kludges (WWDC21-10059, WWDC21-10252).
- `UIImage.preparingThumbnail(of:)` async API — efficient downsampled thumbnails with the system's knowledge of the display, saving memory (WWDC21-10059).

## Migration guidance

- **Audit `translucent = false` on `UIToolbar`/`UITabBar`.** iOS 15's new scroll-edge appearance system breaks visually if the bar is opaque; use `scrollEdgeAppearance` instead (WWDC21-10059).
- iOS 15 sheets gain the **medium detent** (`.medium()` or `.large()`) — your full-screen modal can become a half-sheet with one modifier (WWDC21-10063).
- Prefer the new `UIButton.Configuration` API over the legacy 6-property setup. `.plain`/`.gray`/`.tinted`/`.filled` styles cover 90% of cases. Multi-line text & DT support are baked in (WWDC21-10059, WWDC21-10064).
- Mac Catalyst: declare `UIApplicationSupportsPrintCommand=true` in Info.plist to auto-add Print/Export-as-PDF menu items, then implement `printContent(_:)` on any responder. The responder chain finds the right target (WWDC21-10052).

## Cross-references

- `wrapped value`, `projected value`, **and** `binding` — property wrappers can now expose all three to function/closure parameters via the `$`/`_` prefix on parameter names (WWDC21-10192, WWDC21-10018).
- `Section`'s header view automatically gets `.isHeader` accessibility trait — VoiceOver headings rotor lights up for free (WWDC21-10119).
- `ControlGroup` composes related controls — the back/forward menus in toolbars are a `ControlGroup` of two `Menu`s with `primaryAction` (WWDC21-10018).
- `LocalizedStringKey` initializers on `Text` and friends are auto-extracted by the Swift compiler in Xcode 13 to populate string catalogs (WWDC21-10018, WWDC21-10221).
