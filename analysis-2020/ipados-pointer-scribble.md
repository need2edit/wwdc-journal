# WWDC 2020 — iPadOS 14: Pointer, Scribble, Sidebars, Pencil

iPadOS 14 was a major iPad-as-a-laptop year. Pointer support landed in 13.4; iPadOS 14 added customization APIs, system-wide Scribble for handwritten text input anywhere, the multi-column sidebar API for SplitViewController, and PencilKit's data-model openness.

## Sessions Analyzed
- 10093 — Build for the iPadOS pointer (gateway)
- 10094 — Handle trackpad and mouse input
- 10105 — Build for iPad
- 10106 — Meet Scribble for iPad
- 10107 — What's new in PencilKit
- 10148 — Inspect, modify, and construct PencilKit drawings
- 10109 — Support hardware keyboards in your app
- 10617 — Bring keyboard and mouse gaming to iPad
- 10640 — Design for the iPadOS pointer
- 10206 — Designed for iPad
- 10026 — Lists in UICollectionView
- 10097 — Advances in UICollectionView
- 10045 — Advances in diffable data sources

## Multi-Column Sidebar (Build for iPad, 10105)

The biggest new structural API: `UISplitViewController` now supports **three columns** out of the box (primary / supplementary / secondary), with full automation of show/hide, gestures, buttons, and compact-width substitution.

```swift
let split = UISplitViewController(style: .tripleColumn)
split.setViewController(sidebar, for: .primary)
split.setViewController(messageList, for: .supplementary)
split.setViewController(messageDetail, for: .secondary)
split.setViewController(tabbedContent, for: .compact)  // alternate flow for narrow widths
```

Key points:
- The compact column is a **separate view-controller hierarchy** for narrow widths. Apple recommends one app for iPad and iPhone with two presentation styles.
- `preferredDisplayMode`, `preferredSplitBehavior` (tile/displace/overlay), `presentsWithGesture`, `showsSecondaryOnlyButton` give app-level control.
- Each column gets an automatically-created navigation controller; system inserts the right show/hide buttons in the right places.
- When transitioning between regular and compact, you must manually re-create your detail view controller (Shortcuts demonstrates this with a protocol that requires a `recreate()` method).

## Sidebars in Collection Views

The "right" way to build the sidebar is `UICollectionView` with the new **list configuration** + sidebar appearance:

```swift
var config = UICollectionLayoutListConfiguration(appearance: .sidebar)
let layout = UICollectionViewCompositionalLayout.list(using: config)
```

For content lists (the supplementary column), use `.sidebarPlain`. For multi-section detail lists, use `.insetGrouped`.

### Lists in UICollectionView (10026, 10097)

A new sub-API of compositional layout that gives you UITableView-like sections with **far more flexibility**: outline expand/collapse, swipe actions on cells, leading/trailing accessories, multi-section layouts that mix lists with grids/horizontal-scrolling sections.

The new `UICollectionViewListCell`:
- **`separatorLayoutGuide`** — a layout guide that the cell exposes; you constrain it to your primary content. The separator auto-aligns to your label/icon, including when Dynamic Type changes the layout.
- **Leading and trailing swipe actions** — configured as cell properties, not delegate methods. You can override the getter for dynamic configuration.
- **Accessories API** — multiple accessories per side, with system handling of edit-mode show/hide and tap behavior. Built-in: disclosure indicator, outline disclosure, delete, reorder, multiselect, checkmark.

### Cell Registration API (10097)

The new way to dequeue cells:
```swift
let cellRegistration = UICollectionView.CellRegistration<MyCell, Item> { cell, indexPath, item in
  var content = cell.defaultContentConfiguration()
  content.text = item.title
  content.image = item.icon
  cell.contentConfiguration = content
}
// Use:
collectionView.dequeueConfiguredReusableCell(using: cellRegistration, for: indexPath, item: item)
```

Eliminates the register-class step, the reuse-identifier strings, and provides type safety. Pair with `UICollectionViewDiffableDataSource` for automatic animations.

### Section Snapshots (Diffable Data Source)

The new `NSDiffableDataSourceSectionSnapshot<Item>` lets you compose a data source from per-section snapshots, and crucially supports **hierarchical data** (parents and children), which is what backs the outline expand/collapse pattern. You can `expand(_:)` and `collapse(_:)` on a section snapshot programmatically.

## The iPadOS Pointer

The pointer is **fluid and adaptive** — it morphs into controls when hovering over them, snaps to lines when over text, becomes a crosshair when you customize it. The system goal: a pointer that feels native to a touch-first OS, not a Mac transplant.

### What You Get for Free

A lot:
- `UIBarButtonItem`, `UISegmentedControl`, `UIMenuController` — built-in pointer effects.
- Scroll views — two-finger pan, mouse wheel, pinch-zoom.
- `UICollectionView` / `UITableView` — two-finger pan to reveal swipe actions.
- `UITextView` and `UITextInteraction` users — full Mac-style text selection.
- `UIDragInteraction` — click-and-drag now skips the long-press; immediate drag.
- `UIContextMenuInteraction` — secondary click invokes the menu in compact appearance.

### Customization: Three Levels

1. **`UIBarButtonItem` and `UIButton`** — built-in effects. `UIButton.isPointerInteractionEnabled = true` enables the automatic effect; `pointerStyleProvider` lets you tweak.

2. **`UIPointerInteraction`** — for custom views. Add the interaction; implement `regionFor` (returns rectangles within your view that get distinct effects) and `styleForRegion` (returns the `UIPointerStyle` for each region).

3. **`UIHoverGestureRecognizer`** — for direct hover handling without effect installation.

### Pointer Style Categories

Two kinds of `UIPointerStyle`:
- **Content effects** — pointer morphs into your view with a treatment. Examples: highlight (the rounded rectangle slide-under that bar buttons get with parallax), lift (for irregularly-shaped buttons like a thread spool), hover.
- **Shape customizations** — pointer becomes a specific shape. `UIPointerShape.verticalBeam(length:)` over text, `.horizontalBeam`, `.roundedRect(_:)`, custom `UIBezierPath`. Combine with `UIAxis` constraints (e.g., `.vertical` snaps the pointer to a horizontal line).

### Polish Tips

- **Expand pointer regions beyond the view bounds** to amplify magnetism. Override `hitTest` to make the larger area hit-testable.
- **Make pointer regions contiguous** to prevent the pointer dropping back to system shape in gaps between buttons (Reminders does this).
- **Coordinate animations with the pointer's transition** via the delegate's `willEnter` / `willExit` methods (UISegmentedControl hides separators between segments this way).
- Add `UIPointerInteraction` to a higher-level view when coordinating multiple regions; it gives you a global picture.

### Modifier Flags on Gestures

`UIGestureRecognizer.modifierFlags` (added in 13.4) gives you the modifier keys held during a gesture. Apps like Numbers use this to constrain shape resizing to aspect ratio (Shift) or to extend selection with click+Cmd.

## Hardware Keyboard Support (10109)

`UIKeyCommand` for explicit shortcuts; the responder chain collects them all, and Cmd-hold shows the discoverability HUD with everything visible.

For **standard editing actions** (copy/paste/select all/zoom in/zoom out), you don't need to create `UIKeyCommand` instances at all — override the corresponding `UIResponderStandardEditActions` method. The system wires up the shortcuts.

```swift
override func selectAll(_ sender: Any?) { ... }
override func copy(_ sender: Any?) { ... }
```

For **raw key events** (continuous arrow-key movement, Esc handling, modifier-only events):

```swift
override func pressesBegan(_ presses: Set<UIPress>, with event: UIPressesEvent?) { ... }
override func pressesEnded(_ presses: Set<UIPress>, with event: UIPressesEvent?) { ... }
```

Each `UIPress` has a `key.keyCode`, `key.modifierFlags`, `key.characters`. The responder chain handles delivery just like other events.

`UIKeyCommand` subclasses `UICommand`, which integrates with the macOS Catalyst command-builder API — your shortcuts become Mac menu items automatically.

### Multi-Selection in Lists

```swift
override func tableView(_:shouldBeginMultipleSelectionInteractionAt:) -> Bool { return true }
```

Enables Shift-click contiguous selection and Cmd-click extending selection. The system handles the table-view editing-mode transition for you.

## Scribble — Handwriting Anywhere on iPad

Scribble lets you write directly into any text field with Apple Pencil. It's system-level, on-device (private and offline), and supports English, Simplified/Traditional Chinese, Cantonese.

### What "Just Works"

Standard text controls (`UITextField`, `UITextView`, `UISearchBar`), web pages with editable HTML, and any custom view with a complete `UITextInput` implementation. Apple's strong recommendation: use standard controls.

### Two New Customization Interactions

- **`UIScribbleInteraction`** — install on a text field for delegate callbacks like:
  - `scribbleInteraction(shouldBeginAt:)` — disable Scribble in drawing modes
  - `scribbleInteractionWillBeginWriting(_:)` / `scribbleInteractionDidFinishWriting(_:)`
  - `UIScribbleInteraction.isPencilInputExpected` (class property) — query at view setup time to optimize layout for handwriting (e.g., make the field larger).

- **`UIIndirectScribbleInteraction`** — for views that *become* editable in response to a tap. Reminders uses this for the blank area below the list. Implement the delegate methods to declare writable elements (with frames), focus the right responder when the user starts writing, and report the focus state.

### Design Principles for Scribble-Friendly UI

- **Hide placeholders** when writing starts (auto with standard controls; do this manually for custom).
- **Stable layout** — don't shift text fields when they become first responder while a Pencil stroke is happening. Standard search controllers handle this; custom shifting fields should request a focus delay.
- **Enough space to write** — Messages widens its message field when Pencil input is detected. Apply the same pattern.

## PencilKit: Now Open (10148)

iOS 14 opens up the PencilKit data model. Drawings are arrays of strokes; strokes have a path (uniform cubic B-spline of stroke points), an ink (type + color, no width), a transform, and an optional mask.

### Path Interpolation

Stroke path's `points` are B-spline **control points**, not points on the path. Use:
- `interpolatedPoints(by: .distance(50))` — sequence of points stepping by distance
- `interpolatedPoints(by: .time(0.1))` — by time (since the user drew faster/slower in different parts)
- `interpolatedPoints(by: .parametric(1.0))` — by parametric value (allows non-integer steps for any-precision interpolation)

`parametricValue(_:offsetBy:)` lets you offset by distance forward/backward — used for animating along strokes.

### Stroke Points

Each point captures appearance (location, size, rotation, opacity), input data (force, altitude), and a time offset. Stored in a lossily compressed format — points you create may not round-trip exactly.

### Masks (From Pixel Eraser)

Strokes can have masks that clip portions out (or split a stroke into multiple new strokes). Use `maskedPathRanges` (an array of parametric value ranges) to interpret the visible portion correctly.

### What This Enables

- Per-stroke recognition (the demo built a handwriting practice app for kids).
- Generating drawings procedurally from text.
- Custom analysis/scoring of strokes.
- Image-based recognition via `PKDrawing.image(from:scale:)`.

## Trackpad and Mouse Input (10094)

For finer-grained input handling beyond pointer effects:
- `UIHoverGestureRecognizer` for hover-only interactions.
- New gesture-recognizer support for scroll wheel and pinch-to-zoom.
- Modifier flags on gestures (already covered).
- New mouse button events (right-click → secondary click).

## Cross-References
- [big-sur-design-system.md](big-sur-design-system.md) — the same sidebar/list patterns adopted in macOS Big Sur.
- [swiftui-2-foundation.md](swiftui-2-foundation.md) — SwiftUI's `List` and toolbar API parallel the UICollectionView additions.
- [accessibility.md](accessibility.md) — pointer interactions and text input affect VoiceOver.

## Adoption Checklist
- [ ] Audit your iPad app for the 3-column SplitViewController pattern.
- [ ] Migrate from `UITableView` → `UICollectionView` with list configuration.
- [ ] Adopt the cell registration API to eliminate reuse-identifier strings.
- [ ] Use diffable data source section snapshots for hierarchical / outline content.
- [ ] Add pointer effects to bar buttons (mostly free) and custom UI (`UIPointerInteraction`).
- [ ] Add `UIKeyCommand`s for primary actions; override standard edit actions for free shortcuts.
- [ ] Implement `pressesBegan`/`pressesEnded` for continuous input (arrow-key shape movement).
- [ ] Test Scribble on every text input field; add `UIScribbleInteraction` only where customization is needed.
- [ ] If your app uses PencilKit, evaluate whether stroke-level access enables new features.
