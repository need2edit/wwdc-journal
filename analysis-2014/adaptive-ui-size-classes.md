# Adaptive UI / Size Classes — WWDC 2014 Analysis

**Sessions covered:** 216 (Building Adaptive Apps with UIKit), 214 (View Controller Advancements in iOS 8), 226 (What's New in Table and Collection Views), 411 (What's New in Interface Builder), 228 (A Look Inside Presentation Controllers), 232 (Advanced User Interfaces with Collection Views)

## Headline

iOS 8 introduces **Size Classes** and **Trait Collections** — a coordinate-free way to describe the available UI space. The "iPhone vs iPad, portrait vs landscape" four-way split is REPLACED by horizontal/vertical Compact/Regular dimensions. **Build one universal app from one storyboard** that adapts to every device, orientation, and split-screen size — including Apple Watch and the future.

## The Mental Model — Traits and Size Classes (session 216)

- A **trait collection (`UITraitCollection`)** describes the UI environment: horizontal size class (Compact/Regular), vertical size class (Compact/Regular), user interface idiom (phone/pad/tv), display scale (1x/2x/3x).
- **Size class is a magnitude, not a measurement.** It doesn't say "pixels"; it says "this dimension feels small or feels normal" (216).
- The **four canonical size class combinations** map to:
  - **Compact-W, Regular-H** → iPhone portrait (and iPhone 6+ portrait)
  - **Compact-W, Compact-H** → iPhone landscape (most models)
  - **Regular-W, Regular-H** → iPad portrait, iPad landscape
  - **Regular-W, Compact-H** → iPhone 6+ landscape (the only device in this class as of 2014)
- HIDDEN GEM: **STOP using `UIInterfaceOrientation` and `UIUserInterfaceIdiom`** for layout decisions. The old enums are kept for compatibility but Apple actively discourages them in 216 — they don't generalize to split-screen multitasking (which arrives in iOS 9), to Apple Watch (which arrives in 2015), or to whatever comes next (216).

## Trait Environment Hierarchy (session 216)

- Anything with a trait collection conforms to **`UITraitEnvironment`**: `UIScreen`, `UIWindow`, `UIView`, `UIViewController`, and `UIPresentationController`.
- Traits **flow from parent to child**. The screen's traits propagate down through window → root view controller → child view controllers → views.
- A parent can **override** the trait collection it passes to a specific child via `setOverrideTraitCollection(_:forChild:)`. The new partial trait collection is **added** to the inherited one (216).
- BEST PRACTICE: an iPhone 5/6 in landscape can be FORCED into Regular-W mode by your container view controller calling `setOverrideTraitCollection(UITraitCollection(horizontalSizeClass: .regular), forChild: splitViewController)`. The split view controller now shows two columns even on iPhone — exactly how iOS 8's built-in Mail app behaves on iPhone 6 Plus landscape (216).

## traitCollectionDidChange and willTransitionToTraitCollection (session 216)

- **`traitCollectionDidChange(_:)`**: called on a trait environment after its trait collection has changed. Use to update views/UI that depend on traits.
- **`willTransitionToTraitCollection(_:withTransitionCoordinator:)`** (UIViewController only): called BEFORE the change, with a transition coordinator. Use `coordinator.animate(alongsideTransition:)` to animate your custom UI in lockstep with the system's rotation/transition animations (216).
- BEST PRACTICE: subclass `UIView` and override `traitCollectionDidChange(_:)` if your view's drawing/layout depends on trait values (e.g. font size changes between Compact and Regular). Use `previousTraitCollection.hasDifferentColorAppearance(comparedTo: traitCollection)` style checks to avoid unnecessary work (216).

## UISplitViewController on iPhone (sessions 214, 216)

- **Split view controller works on iPhone in iOS 8**. Universal apps can now use ONE `UISplitViewController` for iPad and iPhone — no more separate iPhone-vs-iPad code paths (214).
- A split view controller has TWO states:
  - **Expanded** (Regular-W environment): two columns visible side-by-side. Toggle the primary's visibility with `displayModeButtonItem`.
  - **Collapsed** (Compact-W environment): single column; secondary view controller is pushed onto the primary's navigation stack.
- The split view controller AUTOMATICALLY collapses/expands as the trait collection changes. Your custom code only handles the merge logic via `UISplitViewControllerDelegate`:
  - `splitViewController(_:collapseSecondary:onto:)`: called when collapsing. Return `false` to let the default (push secondary onto primary's nav stack) happen, or `true` to suppress and handle yourself.
  - `splitViewController(_:separateSecondaryFrom:)`: called when expanding. Return the new secondary view controller, or `nil` to use the default behavior (214).
- HIDDEN GEM: `preferredDisplayMode = .allVisible` programmatically opens the split — same effect as the user tapping the `displayModeButtonItem` (214).

## showViewController vs showDetailViewController (sessions 214, 216)

- **`showViewController(_:sender:)`** = "show this content as a primary navigation step." In a `UINavigationController`: pushes. In a `UISplitViewController`: replaces the primary. Standalone: presents modally. Adapts to its container.
- **`showDetailViewController(_:sender:)`** = "show this as detail." In an expanded `UISplitViewController`: replaces the secondary. In a collapsed split view controller: forwards to `showViewController` on the primary (which then pushes onto the nav stack).
- HIDDEN GEM: STOP writing `self.navigationController?.pushViewController(...)`. That's a hard coupling to the container hierarchy. `showViewController(_:sender:)` walks UP the view controller chain via `targetViewController(forAction:sender:)` to find the right container — and adapts when your app is embedded differently (216).
- HIDDEN GEM: you can implement `targetViewController(forAction:sender:)` and your own `showCustomViewController(_:sender:)` methods on custom container view controllers — extending the same dispatch pattern (216).
- New notification: `UIViewControllerShowDetailTargetDidChangeNotification` fires when the split view controller collapses/expands. Use to refresh table view disclosure indicators (which should show only when tapping would push, not when it would replace the secondary) (216).

## Adaptive Image Assets (session 216)

- Asset catalogs in Xcode 6 support per-size-class images. An image set can have a "Compact" variant used when the containing view's trait collection has `horizontalSizeClass == .compact` (216).
- `UIImageView` automatically picks the right variant for its current trait collection AND updates intrinsic content size when the trait collection changes — your Auto Layout reflows for free (216).
- Programmatic access via `UIImageAsset` — wraps the multi-trait image, lets you `image(with: UITraitCollection)` for a specific environment.

## Presentation Controllers — Complete Architecture Rework (session 214)

- Every modal presentation in iOS 8 is mediated by a **`UIPresentationController`** that owns the lifetime of the presentation, the dimming view, custom shadows, the appearance/disappearance choreography.
- Old (iOS 7): your custom `UIViewControllerAnimatedTransitioning` was responsible for adding views to the hierarchy, animating, and cleaning up. Tightly coupled present and dismiss code (214).
- New (iOS 8): `UIPresentationController` adds/manages the views; the animator just animates frames/alphas. Cleaner separation; harder to leak views.
- HIDDEN GEM: all old iPad-only presentation styles (page sheet, form sheet, popover) **now work on iPhone** with automatic adaptation. By default they go full-screen in Compact-W; you control adaptation via `UIAdaptivePresentationControllerDelegate.adaptivePresentationStyle(for:)` (214).
- HIDDEN GEM: `UIPopoverController` is **soft-deprecated**. Use `UIViewController.modalPresentationStyle = .popover` — same behavior, integrated into the new architecture, adapts on iPhone via the delegate (214).
- HIDDEN GEM: when a popover adapts to full-screen on iPhone, you can **inject a navigation controller wrapper with a Done button** via `presentationController(_:viewControllerForAdaptivePresentationStyle:)`. Same code, two presentations (214).

## Self-Sizing Table View Cells (session 226)

- iOS 8 makes Dynamic Type a first-class requirement. **All system apps adopt it**; users expect third-party apps to too (226).
- **Self-sizing cells**: cells determine their own height from their Auto Layout constraints. No `tableView(_:heightForRowAt:)` needed.
- Three things to set up:
  1. `tableView.estimatedRowHeight = X` (any approximate value > 0). Required to enable self-sizing.
  2. `tableView.rowHeight = UITableView.automaticDimension` (now the default in storyboards/XIBs in seed 2+).
  3. Cells use Auto Layout constraints that resolve a unique height given the cell's width.
- HIDDEN GEM: cells can also implement `sizeThatFits(_:)` for non-Auto Layout sizing. The table view internally calls `systemLayoutSizeFitting(_:)` which falls through to `sizeThatFits` when no constraints are present (226).
- HIDDEN GEM: built-in cell labels (`textLabel`, `detailTextLabel`) automatically use Dynamic Type fonts in iOS 8. **You get scale-with-system-text-size for free** if you use the standard cell types (226).
- WARNING: setting `rowHeight` to a fixed value (44) DISABLES self-sizing. The new default is `UITableView.automaticDimension`, but if you set it explicitly in code, you opt out.

## Self-Sizing Collection View Cells + Smart Invalidation (sessions 226, 232)

- `UICollectionViewFlowLayout` gets `estimatedItemSize` (CGSize). Setting it to anything non-zero enables self-sizing — same model as table views.
- For custom collection view layouts, **invalidation contexts** (introduced in iOS 7) get a major upgrade: **fine-grained invalidation**. Override `invalidationContext(forPreferredAttributes:withOriginalAttributes:)` to tell the layout exactly which item attributes changed (226, 232).
- HIDDEN GEM (PERFORMANCE): `UICollectionViewLayoutInvalidationContext.invalidateItems(at:)`, `.invalidateSupplementaryElements(ofKind:at:)`, `.invalidateDecorationElements(ofKind:at:)`. Tell the collection view exactly which items need new attributes — avoid recomputing the whole layout (226).
- HIDDEN GEM: `contentSizeAdjustment` and `contentOffsetAdjustment` on the invalidation context let your custom layout report "the content size grew by Y points; please bump the offset accordingly" so visible items don't appear to jump (226).

## Interface Builder Live Rendering (session 411)

- **`@IBDesignable`** on a `UIView`/`NSView` subclass: Interface Builder builds your framework, runs your view's drawing live in the storyboard canvas. Iterate without build-and-run (411).
- **`@IBInspectable`** on a property: appears in the Attributes Inspector as an editable field. Storage backed by user-defined runtime attributes — no extra code needed.
- HIDDEN GEM: `prepareForInterfaceBuilder()` lets you set up design-time-only state (placeholder images, fake data) without polluting runtime. Use the `IB_PROJECT_SOURCE_DIRECTORIES` environment variable to load assets relative to your project root (411).
- HIDDEN GEM: you can **debug Interface Builder's rendering** of your `@IBDesignable` view. Set a breakpoint in your view code, choose Editor → Debug Selected Views, and Xcode attaches the debugger to IB's helper process (411).

## Best Practices

- **Build for Any-Any first**, then customize specific size classes only where Any-Any falls short. The Interface Builder size class grid mirrors this strategy (411).
- **Use Auto Layout with intrinsic content size** rather than hard-coding heights. Your views naturally adapt to font size changes (Dynamic Type) and trait changes.
- **Don't override `UIView.frame` arithmetic on rotation**. Use `viewWillTransition(to:with:)` instead (or just nothing — Auto Layout usually handles it) (214).
- **Avoid hard-coding `UIInterfaceOrientation` checks**. Use trait collections.
- **Remove explicit width/height constraints from custom views**; override `intrinsicContentSize` instead. The view declares its natural size; constraints place it (411).

## Hidden Gems

- HIDDEN GEM: `viewWillTransition(to:with:)` is the **general replacement** for `willRotate(to:duration:)`, `willAnimateRotation(to:duration:)`, and `didRotate(from:)`. The transition coordinator's target transform tells you whether you're in a rotation; the size tells you the new bounds (214).
- HIDDEN GEM: `UIScreen.coordinateSpace` (interface-oriented) vs `UIScreen.fixedCoordinateSpace` (always portrait) — convert between them with `UIScreen.coordinateSpace.convert(_:to:)`. The keyboard size notifications in iOS 8 are now in interface-oriented coordinates (214).
- HIDDEN GEM: `UIViewControllerHidesBottomBarWhenPushed` and friends DO respect trait classes — the same view controller pushed in different containers behaves consistently.
- WARNING: targeting iOS 7 from an Xcode 6 project that uses size classes requires conditional code. The size-class APIs return graceful defaults on iOS 7, but features like split view controller on iPhone simply don't work below iOS 8 (216).

## Cross-references

- **Continuity / Handoff (219)** uses the same trait/size-class model when activity views adapt across devices.
- **App Extensions (205, 217)** are themselves trait environments — your today widget gets a trait collection from Notification Center; your share extension gets one from the host's activity sheet.
- **Storyboards in OS X Yosemite (411)** — first time storyboards are available on Mac. Same paradigm as iOS storyboards but adapted for windows/scenes.
- **What's New in Cocoa Touch (202)** is a general overview of the iOS 8 SDK changes; Building Adaptive Apps (216) is the deep dive.

## Migration Guidance

- **iPhone-only apps** with iOS 7-style code: enable size classes in the storyboard (Xcode prompts to upgrade segues to adaptive types). Test in landscape — most layouts that worked in portrait still work, but Compact-H may need attention.
- **iPad-only apps**: enable size classes; test on iPhone simulator with the same storyboard. Many apps work surprisingly well; ones with split view controllers benefit massively from the unified adaptive flow.
- **Universal apps with separate XIBs/storyboards per device**: consolidate into one storyboard with size class customizations. Long-term maintainability wins; short-term effort is significant.
- **Custom transition animations**: rewrite for `UIPresentationController` if you can. The old `UIViewControllerAnimatedTransitioning` is still supported but the new architecture is cleaner and more composable (214, 228).
