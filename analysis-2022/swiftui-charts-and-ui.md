# SwiftUI, Swift Charts & UI Frameworks (2022)

WWDC22 was a banner year for SwiftUI. Apple shipped Swift Charts (the most-requested data-viz framework), the data-driven `NavigationStack` / `NavigationSplitView`, the `Layout` protocol, the Transferable protocol, multi-platform window scenes, and finally first-class support for productive iPad apps via tables, multi-select, and toolbar customization.

## Sessions covered
- WWDC22-10052 — What's new in SwiftUI
- WWDC22-10054 — The SwiftUI cookbook for navigation
- WWDC22-10056 — Compose custom layouts with SwiftUI
- WWDC22-10058 — SwiftUI on iPad: Organize your interface
- WWDC22-110343 — SwiftUI on iPad: Add toolbars, titles, and more
- WWDC22-10059 — The craft of SwiftUI API design: Progressive disclosure
- WWDC22-10061 — Bring multiple windows to your SwiftUI app
- WWDC22-10062 — Meet Transferable
- WWDC22-10072 — Use SwiftUI with UIKit
- WWDC22-10075 — Use SwiftUI with AppKit
- WWDC22-10068 — What's new in UIKit
- WWDC22-10069 — Meet desktop-class iPad
- WWDC22-10070 — Build a desktop-class iPad app
- WWDC22-10071 — Adopt desktop-class editing interactions
- WWDC22-10074 — What's new in AppKit
- WWDC22-10090 — What's new in TextKit and text views
- WWDC22-10136 — Hello Swift Charts
- WWDC22-10137 — Swift Charts: Raise the bar

## Swift Charts (10136, 10137)

### Mental model: marks + mark properties + scales
A chart in Swift Charts is built by **composition** of marks. There are 6 mark types (`BarMark`, `LineMark`, `PointMark`, `AreaMark`, `RuleMark`, `RectangleMark`) and 6 mark properties (`x`, `y`, `foregroundStyle`, `symbol`, `lineStyle`, `position`). Combinations produce a vast array of chart designs from a tiny vocabulary.

```swift
Chart(data) { item in
  BarMark(x: .value("Style", item.name),
          y: .value("Sales", item.sales))
}
```

The `.value(_:_:)` pattern is critical: the first argument is a localized *description*, the second is the actual data. This is what makes the chart accessible to VoiceOver — it speaks the description plus the value.

### Three data domains
- **Quantitative** — `Int`, `Float`, `Double`. Get continuous axes.
- **Nominal** — `String`, enums. Get categorical axes.
- **Temporal** — `Date`. Get date-aware axes with smart tick spacing.

The mark adapts based on the data type of each axis. Plot quantity on `y` and category on `x` → vertical bar chart. Swap them → horizontal bar chart. No code changes besides argument order.

### Free, automatically:
- Dark Mode adaptation
- Localization of numbers and dates
- Dynamic Type
- VoiceOver descriptions and tap-to-explore
- **Audio Graphs** (sonification — beeps that go up/down with values)
- High-Contrast mode
- All Apple platforms (iOS, macOS, tvOS, watchOS)

### Customization
- `chartXScale(domain: 0...200)` to fix axis ranges.
- `chartXAxis { AxisMarks(values: .stride(by: .month)) { ... } }` for custom ticks.
- `chartPlotStyle { plotArea in plotArea.frame(height: ...) }` for plot-area sizing.
- `chartOverlay { proxy in ... }` exposes a `ChartProxy` that maps screen coords ↔ data values — this is how you implement interactive brushing/lollipop selection.

### HIDDEN GEM
Swift Charts ships in iOS 16, so it has the same back-deploy story as `NavigationStack`. Plan accordingly.

## NavigationStack & NavigationSplitView (10052, 10054)

### The breakthrough: data-driven navigation
The pre-iOS-16 `NavigationLink(isActive:)` API required one binding per link. The new model lifts navigation state up to the container:

```swift
@State private var path: [Recipe] = []

NavigationStack(path: $path) {
  List(categories) { category in
    Section(category.name) {
      ForEach(category.recipes) { recipe in
        NavigationLink(recipe.name, value: recipe)
      }
    }
  }
  .navigationDestination(for: Recipe.self) { recipe in
    RecipeDetail(recipe: recipe)
  }
}
```

Now you can deep-link by mutating `path`, pop to root by clearing it, push from button taps anywhere. State is fully observable and Codable.

### Type-erased path
`NavigationPath` is a heterogeneous, Codable collection that can hold any `Hashable` values — use it when your stack pushes multiple types of destinations.

### NavigationSplitView
Two and three-column layouts. Automatically collapses to a stack on iPhone or in Slide Over on iPad. Can be composed with `NavigationStack` per column. Initialize with the column count you want; the columns can each track separate selection state.

### Critical gotcha (10054): destination placement
`navigationDestination` must NOT be inside a lazy container (`List`, `LazyVGrid`, `Table`). Lazy views may not be loaded yet, so the stack won't see the modifier. Attach it to the `ScrollView` or higher, not to each cell.

### Codable navigation state
The cookbook session shows persisting navigation state by:
1. Encapsulating in a `NavigationModel` `ObservableObject`.
2. Implementing `Codable` manually — store identifiers, not whole models, so the data doesn't go stale when the underlying database changes.
3. Persisting via `@SceneStorage` and a `task` modifier that observes changes.

### URGENT migration note
`NavigationLink(isActive:)` and `NavigationLink(tag:selection:)` are **deprecated in iOS 16**. Switch to value-presenting `NavigationLink` plus `navigationDestination`. `NavigationView` with stack style → `NavigationStack`. Multi-column `NavigationView` → `NavigationSplitView`.

## The Layout protocol (10056)

For when stacks aren't enough. Implement two methods:
- `sizeThatFits(proposal:subviews:cache:)` — return the size your layout wants.
- `placeSubviews(in:proposal:subviews:cache:)` — call `subview.place(at:anchor:proposal:)` for each.

You get `Subviews` proxies (not the actual views) and `ViewSpacing` instances that let you respect each view's preferred spacing along an edge.

### When to use Layout vs. GeometryReader
**Use Layout, not GeometryReader, to size a parent based on its children.** GeometryReader measures its container and reports it down to subviews — wrong direction for "size to fit content." Layout participates correctly in the layout engine and avoids the infinite-loop hazard of GeometryReader+frame patterns.

### Custom layout values via `LayoutValueKey`
Layouts can read per-subview values that aren't part of the view itself. Define a `LayoutValueKey`, expose a convenience `View.rank(_:)` modifier wrapping `layoutValue(_:_:)`, then read `subview[RankKey.self]` inside the layout. This is how the radial layout in the demo gets ranking info from the data model.

### `AnyLayout` for transitions between layout types
`AnyLayout(isThreeWayTie ? HStackLayout() : RadialLayout())` preserves view identity across layout changes, so SwiftUI animates the transition smoothly. Without `AnyLayout` you'd get crossfades instead of fluid morphing.

### `ViewThatFits`
Picks the first child that fits. Useful for buttons that should arrange horizontally normally but stack vertically at large Dynamic Type sizes:

```swift
ViewThatFits {
  EqualWidthHStack { buttons }
  EqualWidthVStack { buttons }
}
```

## Grid (10052, 10056)
A new container, distinct from `LazyVGrid`. **Loads all views eagerly** so it can size cells in both dimensions. Use when you have a small static set; use lazy grids for scrollable content.

```swift
Grid(alignment: .leading) {
  ForEach(places) { place in
    GridRow {
      Text(place.name)
      ProgressView(value: place.percent)
      Text("\(place.count)")
        .gridColumnAlignment(.trailing)
    }
    Divider().gridCellColumns(3)
  }
}
```

## Window scenes (10052, 10061)
- **`Window`** — single, unique window (good for inspectors).
- **`WindowGroup`** — multi-document/window apps.
- **`MenuBarExtra`** — entire macOS menu-bar items in pure SwiftUI.
- New modifiers: `.defaultSize`, `.defaultPosition`, `.windowResizability`, `.presentationDetents` (resizable sheets).
- `@Environment(\.openWindow)` action lets you programmatically open scenes.

`.presentationDetents([.medium, .height(250)])` finally gives SwiftUI sheets the iOS 15 detents API.

## Transferable (10062, 10052)
A Swift-first replacement for `NSItemProvider`. Conform a type to `Transferable` and declare its representations:

```swift
extension Photo: Transferable {
  static var transferRepresentation: some TransferRepresentation {
    DataRepresentation(contentType: .jpeg) { ... }
  }
}
```

Powers `ShareLink`, `PhotosPicker`, drag-and-drop (`dropDestination(payloadType:)`). `String`, `Image`, `URL`, etc. already conform.

## SwiftUI ↔ UIKit/AppKit bridging (10072, 10075, 10068)

### `UIHostingConfiguration` — SwiftUI inside UIKit cells
The headline integration: build collection-view and table-view cells in pure SwiftUI without subclassing `UIView` or wrapping in `UIHostingController`:

```swift
cell.contentConfiguration = UIHostingConfiguration {
  HStack { ... }
}
```

This is the path forward for incrementally adopting SwiftUI inside existing UIKit apps.

### Self-resizing cells (10068)
`UICollectionView.SelfSizingInvalidation` defaults to `.enabled` in iOS 16. Cells can call `invalidateIntrinsicContentSize()` when their content changes and the layout adapts automatically. With `.enabledIncludingConstraints`, even Auto Layout changes trigger invalidation.

## Desktop-class iPad (10068, 10069, 10070, 10071)

### Three navigation-bar styles
- `.navigator` — traditional centered title (default).
- `.browser` — leading title; for Files / Safari-style apps.
- `.editor` — leading title with back button; for document editors.

The browser/editor styles free up the bar's center for `centerItemGroups` — bar buttons that the user can rearrange and the system can collapse to overflow menus.

### `UIBarButtonItemGroup` flexibility
- **Fixed group** — always present, can't be moved.
- **Movable group** — required, can be reordered.
- **Optional group** — can be removed entirely; supports `representativeItem` for collapsing into a single icon when space is tight.

### Title menu
`navigationItem.titleMenuProvider` supplies a `UIMenu` for actions on the document. Default items include Duplicate, Move, Rename, Export, Print — they're filtered based on whether the responder chain implements them.

### Document properties
`UIDocumentProperties` enables the share sheet header and drag-and-drop of the entire document from the navigation bar.

### Find & Replace
`UITextView.isFindInteractionEnabled = true` is all it takes for built-in views. Use `UIFindInteraction` for custom views.

### Edit menu modernized
`UIEditMenuInteraction` replaces the deprecated `UIMenuController`. Touch interactions get a redesigned floating menu; pointer interactions get a context menu.

### Multi-select context menus (10058)
```swift
.contextMenu(forSelectionType: PlaceID.self) { selection in
  if selection.isEmpty { Button("Add Place") { ... } }
  else if selection.count == 1 { ... }
  else { Button("Add \(selection.count) to Guide") { ... } }
}
```

### Lightweight selection on iPad
With a keyboard attached, you no longer need to enter edit mode to multi-select. Standard Shift/Cmd-click works. Without a keyboard, two-finger pan still works.

## Tables on iPad (10058)
SwiftUI's `Table` (introduced for macOS in 2021) now works on iPad. **Tables only show their first column in compact size class** — design accordingly. Tables don't scroll horizontally on iPad, so limit columns and prefer fixed widths for narrow data.

```swift
Table(places, selection: $selection, sortOrder: $sortOrder) {
  TableColumn("Name", value: \.name)
  TableColumn("Comfort", value: \.comfort) { ... }
    .width(80)
  TableColumn("Noise", value: \.noise)
}
```

## Other new controls (10052, 10068)
- **`MultiDatePicker`** — non-contiguous date selection.
- **`UICalendarView`** — UIKit standalone version of the date picker, with date decorations and disabled-date predicates. **Uses `DateComponents`, not `Date`** — and you must explicitly set `.calendar` to Gregorian if your code relies on it.
- **Mixed-state toggles & pickers** — pass an array of bindings to a single Toggle/Picker; shows a tri-state appearance when values disagree.
- **Variable-axis text fields** — `TextField(..., axis: .vertical)` plus `lineLimit(_:reservesSpace:)` for natural multi-line growth.
- **Search tokens & scopes** — `searchable` now supports tokens, suggestions, and scope bars.

## Best practices
- **BEST PRACTICE**: Always include `.value(_:_:)` descriptions in chart marks — they're read by VoiceOver. Don't pass raw values.
- **BEST PRACTICE**: Use `NavigationSplitView` even for iPhone-first apps; it auto-collapses to a stack and gives you Mac/iPad for free.
- **BEST PRACTICE**: Place `navigationDestination` modifiers OUTSIDE lazy containers, near (but not inside) `List`/`LazyVGrid`.
- **HIDDEN GEM**: `Grid` is eager and sizes both dimensions; `LazyVGrid`/`LazyHGrid` are lazy and need you to specify one dimension. Use the right one.
- **HIDDEN GEM**: `LayoutValueKey` lets a Layout read per-subview values without view-tree refactoring.
- **DEPRECATION**: `NavigationLink(isActive:)`, `NavigationLink(tag:selection:)`, and `NavigationView` with stack style are deprecated in iOS 16.

## Cross-references
- Layout protocol pairs naturally with widgets/complications (10050) since both need precise size control.
- Tables on iPad (10058) link to multi-select context menus and the toolbar story (110343, 10068, 10069).
- Transferable (10062) underpins ShareLink, PhotosPicker, and the new drag-and-drop story.
- For deeper dives, see the toolbar/title series in WWDC22-110343, 10069, 10070, 10071.
