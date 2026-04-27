# WWDC 2023 — SwiftUI Animations, Widgets, & Cross-Platform UI

WWDC 2023's SwiftUI gets a major animation overhaul (keyframes, phase animators, native springs), interactive widgets via App Intents, scroll view transformation hooks, and visionOS extensions. UIKit also gets a meaningful trait system update.

## Sessions Analyzed

### SwiftUI core
- 10148 — What's new in SwiftUI (gateway)
- 10160 — Demystify SwiftUI performance
- 10157 — Wind your way through advanced animations in SwiftUI
- 10156 — Explore SwiftUI animation
- 10158 — Animate with springs
- 10159 — Beyond scroll views
- 10161 — Inspectors in SwiftUI: discover the details
- 10162 — The SwiftUI cookbook for focus
- 10037 — Explore pie charts and interactivity in Swift Charts
- 10115 — Design with SwiftUI
- 10056 — Build better document-based apps
- 10058 — What's new with text and text interactions

### UIKit & AppKit
- 10055 — What's new in UIKit
- 10054 — What's new in AppKit
- 10057 — Unleash the UIKit trait system
- 10281 — Keep up with the keyboard

### Widgets
- 10027 — Bring widgets to new places
- 10028 — Bring widgets to life
- 10029 — Build widgets for the Smart Stack on Apple Watch
- 10309 — Design widgets for the Smart Stack on Apple Watch
- 10184 — Meet ActivityKit
- 10185 — Update Live Activities with push notifications
- 10194 — Design dynamic Live Activities

### MapKit / SF Symbols / Charts
- 10043 — Meet MapKit for SwiftUI
- 10197 — What's new in SF Symbols 5
- 10257 — Create animated symbols
- 10258 — Animate symbols in your app

## Native Spring Animations

The default animation type for new SwiftUI apps on iOS 17+ is now SPRING. Springs are physics-based: they match velocity from the previous animation and settle naturally.

```swift
.animation(.spring, value: count)              // default
.animation(.snappy, value: count)              // shorter, less bounce
.animation(.bouncy, value: count)              // more bounce
.animation(.smooth, value: count)              // slow, no bounce
.animation(.spring(duration: 0.5, bounce: 0.3), value: count)  // custom
```

Spring API simplified: `duration` (perceptual) and `bounce` (-1 to 1) replace the old `mass/stiffness/damping/initialVelocity` quartet. The old API still works.

## Phase Animator vs Keyframe Animator

Two new ways to express multi-stage animation without a Combine timer or Animatable wrappers.

### PhaseAnimator (linear sequence)
```swift
.phaseAnimator([0, 1, 2, 3], trigger: tapCount) { content, phase in
  content.scaleEffect(phase == 1 ? 1.5 : 1.0)
} animation: { phase in
  phase == 1 ? .spring(duration: 0.4) : .easeInOut
}
```
Each phase runs ONLY AFTER the previous animation completes. Great for sequential reactions (tap → bounce → settle).

### KeyframeAnimator (parallel tracks)
```swift
.keyframeAnimator(initialValue: AnimValues(), trigger: count) { content, value in
  content
    .offset(y: value.offset)
    .rotationEffect(.degrees(value.rotation))
    .scaleEffect(value.scale)
} keyframes: { _ in
  KeyframeTrack(\.offset) {
    SpringKeyframe(-30, duration: 0.25)
    CubicKeyframe(0, duration: 0.4)
    SpringKeyframe(0, duration: 0.3)
  }
  KeyframeTrack(\.rotation) { ... }
}
```
All tracks run IN PARALLEL. Each property has its own timeline. This is the API you want for cinematic transitions.

## Visual Effects (Geometry-Free Effects)

`.visualEffect { content, geometry in ... }` lets a view modify itself based on its own geometry WITHOUT a `GeometryReader`. The geometry proxy is per-view, the closure runs on the render thread, and you don't need to wrap your hierarchy in a measurement view.

```swift
DonutCircle(donut: donut)
  .visualEffect { content, geometry in
    let frame = geometry.frame(in: .named("grid"))
    let distance = frame.distance(to: focalPoint)
    return content.scaleEffect(scaleForDistance(distance))
  }
```

Works on iOS 17 / macOS Sonoma. PERF NOTE: this avoids the GeometryReader anti-pattern that historically broke layouts.

## Scroll View Power-Ups

```swift
ScrollView(.horizontal) {
  LazyHStack {
    ForEach(parks) { ParkCard($0).containerRelativeFrame(.horizontal, count: 3, span: 1, spacing: 8) }
  }
  .scrollTargetLayout()
}
.scrollTargetBehavior(.viewAligned)  // .paging, .viewAligned, or custom
.scrollPosition(id: $topItemId)       // binding to topmost item
.scrollTransition { content, phase in
  content.opacity(phase.isIdentity ? 1 : 0.5).scaleEffect(phase.isIdentity ? 1 : 0.9)
}
```

Custom `ScrollTargetBehavior` protocol lets you build snap behaviors for things like calendar pickers, tabbed content. `containerRelativeFrame(_:count:span:)` is for "show 3 cards visible, each 1 chunk wide" layouts.

## Interactive Widgets

The most-requested widget feature ever shipped in iOS 17. Widgets can now host `Button` and `Toggle` controls that fire `AppIntent`s defined in the host app.

```swift
struct CompleteTaskIntent: AppIntent {
  static var title: LocalizedStringResource = "Complete Task"
  @Parameter var taskID: String
  func perform() async throws -> some IntentResult {
    await TaskStore.shared.complete(taskID)
    return .result()
  }
}

// In widget view:
Button(intent: CompleteTaskIntent(taskID: task.id)) {
  Image(systemName: "circle")
}
```

Animations work via `.transition()` and `.contentTransition()` modifiers in widgets — but only for state changes that go through the timeline reload cycle.

### New Widget Locations
- iPad Lock Screen (iPadOS 17)
- iPhone StandBy mode (always-on, large dramatic widgets)
- macOS Sonoma desktop (live, interactive)
- watchOS 10 Smart Stack (auto-rotating)

A SINGLE widget extension can target all of these. Use `WidgetFamily` checks in your view body.

## Live Activities & ActivityKit

Live Activities promoted to a real platform feature with push-update support:
- `ActivityKit.request(...)` to start
- `activity.update(...)` from the app
- Push token gives a remote endpoint to update the widget without the app being running
- New `ActivityConfiguration` modifier with `.dynamicIsland { region in ... }` for the Dynamic Island
- Compact / minimal / expanded layouts

Smart prioritization: only one Live Activity is highlighted on the Dynamic Island at a time.

## Inspectors

`.inspector(isPresented: $showing) { detailsView }` is a new sidebar on macOS/iPadOS that complements `.sheet` (modal) and `.popover`. On iPhone it falls back to a sheet. Use for "details about the current selection."

## SwiftUI Performance (10160)

Key levers:
1. **Instrument SwiftUI updates** with the new SwiftUI Instrument template. Look for `View.body` evaluations that fire when nothing visibly changed.
2. **Identity matters**: passing the wrong `id:` to `ForEach` triggers full rebuilds. Use stable IDs.
3. **Switch to `@Observable`** — granular invalidation usually beats `ObservableObject` for free.
4. Hoist work OUT of `body`. View `body` is called many times.
5. Avoid `AnyView` — it erases identity and forces SwiftUI to redo diffing.
6. Heavy computation in computed properties on observable models forces invalidation when ANY input changes.
7. List with `.listRowSeparator(.hidden)` and proper sectioning for large data sets.

## SF Symbols 5 & Animated Symbols

SF Symbols now support ANIMATIONS. The new `.symbolEffect()` modifier:
- `.bounce` — event notification
- `.pulse` — continuous attention
- `.variableColor` — wave through layers
- `.scale` — state change (up/down)
- `.appear` / `.disappear` — entry/exit
- `.replace` — symbol-to-symbol transition

```swift
Image(systemName: "wifi")
  .symbolEffect(.variableColor.iterative.dimInactiveLayers, isActive: isLoading)
```

Author your own animated symbols in SF Symbols app 5+.

## UIKit Trait System

`UITraitCollection` finally has CUSTOM TRAITS (10057):

```swift
struct GameModeTrait: UITraitDefinition {
  static var defaultValue: GameMode = .arcade
}

view.traitOverrides.gameMode = .puzzle
view.registerForTraitChanges([GameModeTrait.self]) { (view, prev) in /* react */ }
```

This is THE pattern for propagating context (theme, user role, mode) through a UIKit hierarchy without manual wiring. Replaces the old UIAppearance abuse.

Trait change registration with closures replaces `traitCollectionDidChange(_:)` overrides — more granular, only fires for traits you care about.

## MapKit for SwiftUI (10043)

```swift
Map(position: $cameraPosition, selection: $selectedMarker) {
  Marker("Park", coordinate: park.coord)
  MapPolyline(coordinates: route).stroke(.blue, lineWidth: 4)
  UserAnnotation()
}
.mapControls {
  MapUserLocationButton()
  MapCompass()
  MapPitchToggle()
}
.mapStyle(.hybrid(elevation: .realistic))
```

This is a complete SwiftUI-native MapKit. No more `UIViewRepresentable` boilerplate. Selection is just a binding.

## Pathways

- **Animation overhaul**: 10148 → 10156 → 10157 → 10158
- **Widgets**: 10027 → 10028 → 10184 → 10185
- **Performance**: 10148 → 10160 → 10149
- **UIKit modernization**: 10055 → 10057 → 10281
- **Watch app**: 10026 → 10031 → 10138 → 10029

## Hidden Gems

- Spring animations are the default for new apps. Old apps keep ease-in-out unless deployment target is iOS 17+.
- `.containerRelativeFrame(_:count:span:)` adapts to the SCROLL VIEW size, not the device — works for split-view iPads.
- Interactive widgets deserialize the `AppIntent` from disk, so initialization must be fast and parameter values must be Codable.
- The `.scrollPosition(id:)` binding fires repeatedly during scroll — debounce if you do work in the setter.
- `Color(.brandPrimary)` (static member syntax for asset-catalog colors) is COMPILE-TIME CHECKED. Typo in asset name = build error.
- `.containerBackground(_:for:)` is the watchOS-recommended way to set per-screen backgrounds with smooth push/pop transitions.
- SF Symbols variable color animation has THREE modes: `.iterative` (one at a time), `.cumulative` (filling up), and `.dimInactiveLayers`.
- `@Observable` typically makes `ObservableObject`-based code 1.2x–3x faster for view updates because invalidation is per-property.
