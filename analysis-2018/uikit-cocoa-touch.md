# UIKit & Cocoa Touch — WWDC 2018 Analysis

**Sessions covered:** 202 (What's New in Cocoa Touch), 235 (UIKit: Apps for Every Size and Shape), 220 (High Performance Auto Layout), 225 (A Tour of UICollectionView), 224 (Core Data Best Practices), 233 (Adding Delight to your iOS App), 803 (Designing Fluid Interfaces), 804 (The Life of a Button), 802 (Intentional Design)

## Headline

UIKit in iOS 12 doubles down on the iPhone X's safe-area model, the iPhone XR/XS/XS Max line (announced as imminent), and the new fluid-interface paradigm. The notable APIs: `UIScrollView.contentInsetAdjustmentBehavior` replacing the deprecated `automaticallyAdjustsScrollViewInsets`, the asset-rich Swift 4.2 nesting story (everything moves under owning classes), `UIGraphicsImageRenderer` becoming the default-good choice for offscreen drawing, and a serious push to design custom controls with continuous feedback through every phase of an interaction.

## Safe Area Refresher (235)

- `safeAreaInsets` (UIEdgeInsets) and `safeAreaLayoutGuide` (UILayoutGuide) — every UIView has them.
- `additionalSafeAreaInsets` on `UIViewController` lets you _add_ to (not replace) the inherited insets — useful when your view controller adds bottom bars or sliding panels.
- A child view's safe area inset is its parent's inset offset by overlap. **HIDDEN GEM**: a view that's moved off the bottom of its parent _doesn't_ get a growing safe area inset. The framework caps it at the parent's inset to make panel-presentation animations work correctly.
- `safeAreaInsetsDidChange()` (UIView) and `viewSafeAreaInsetsDidChange()` (UIViewController) for reacting to changes.
- Always lay out against the safe area layout guide. Never hard-code "44 points for status bar" anywhere.

## Layout Margins, Directional Layout Margins (235)

- `layoutMargins` (UIEdgeInsets, left/right) — predates RTL.
- `directionalLayoutMargins` (NSDirectionalEdgeInsets, leading/trailing) — RTL-aware. Use this in 2018+.
- `insetsLayoutMarginsFromSafeArea` (defaults true): margins are computed _after_ the safe area is subtracted. Set to false to anchor margins to the bounds.
- `preservesSuperviewLayoutMargins`: makes child margins inherit and align with parent margins. Off by default to keep layouts independent.
- `viewRespectsSystemMinimumLayoutMargins`: minimum 16-pt left/right margins on view controller views are enforced unless you turn this off (and risk Apple's "looks weird at edge of iPhone" reviews).

## Scroll View Content Inset Adjustment (235)

- `automaticallyAdjustsScrollViewInsets` (UIViewController, deprecated).
- `UIScrollView.contentInsetAdjustmentBehavior` enum: `.automatic` (default — handles safe area + bars in nav-controller-contained scroll views), `.scrollableAxes` (only on scrollable axes), `.always` (every edge), `.never` (don't touch).
- The `adjustedContentInset` read-only property = `contentInset` + system-applied insets. **HIDDEN GEM**: clearer mental model than the old single `contentInset` that the system also wrote to. Read `adjustedContentInset` to know the actual current insets; write `contentInset` to add your own.
- **GOTCHA**: setting `.never` causes safe-area insets to propagate to subviews of the scroll view as if it were a normal view. That can have surprising layout-margin side effects. Prefer `additionalSafeAreaInsets` on the parent view controller.
- For self-sizing collection-view cells, **don't** forward `systemLayoutSizeFitting(...)` from the cell to its content view — that creates new layout engines per call and tanks scrolling. (See 220.)

## Table-View Self-Sizing Default Change (235)

- `UITableView.cellLayoutMarginsFollowReadableWidth` is now **false** by default in iOS 12 (was true).
- Recommendation: leave the default, set true only on table views with lots of multi-line text where you want all cell content to align.

## Encapsulating Custom Views Inside the Safe Area (235)

- Pattern: views that aren't safe-area-aware (UIPickerView, UIDatePicker, custom controls) wrapped in a container that:
  - Reads its own `safeAreaInsets`.
  - Positions the unaware control inside that area.
  - Provides a background that extends outside the safe area for visual continuity.
- An optional + required Auto Layout pattern for "padded but not clipped" buttons:
```swift
button.bottomAnchor.constraint(equalTo: superview.bottomAnchor, constant: -16).priority = .defaultHigh   // padding
button.bottomAnchor.constraint(lessThanOrEqualTo: safeAreaLayoutGuide.bottomAnchor)                       // never clip
```
The padding constraint breaks when safe area pushes the button up; the inequality keeps it on screen.

## Asset Slimming (227)

- Image asset compression in iOS 12 catalogs is more aggressive (better LZFSE-like algorithms).
- App thinning + on-demand resources are mature; for cellular-installs over the limit, consider deferring large bundled content via ODR.
- **BEST PRACTICE**: convert PNG buttons to PDF (vector, single artwork for all scales) where possible. Resize SF Symbols equivalents arrived in 2019.

## UICollectionView (225, see also 220)

- Three core concepts to internalize: **layout** (where), **data source** (what), **delegate** (interactions / observation).
- Custom layout subclasses are not scary — only 4 required methods + 1 honorable mention. See `arkit-2-usdz.md` for the binary-search trick that makes mosaic layouts smooth.
- **PERFORMANCE**: `performBatchUpdates` rules:
  - Decompose moves into a delete + insert.
  - Apply data source changes in: deletes (descending order), then inserts (ascending order), then optional reloads.
  - Don't reload + delete the same index path; the reload internally is delete+insert and they conflict.
- Use diffable data sources... in a year (those arrive in iOS 13).

## Notifications API Updates (202, 710)

- `threadIdentifier` is now used for grouping (see `notifications-grouped.md`).
- New programmatic APIs for content extensions: dynamic actions, user-interaction touches, programmatic dismiss/launch.
- Provisional authorization for low-friction notification trials.
- Critical alerts (entitled).

## Messages App Stickers in Camera (202)

- `MSMessagesAppViewController` apps can opt into appearing in the Messages camera UI (alongside the iMessage app strip).
- `MSMessagesSupported PresentationContexts = ["messages", "media"]` in the Info.plist.
- Stickers built with the Xcode sticker template work automatically. Custom MS Messages views need to check `presentationContext` to render appropriately for camera vs. messages.
- Horizontal swipes inside the Messages compact view are now your app's swipes (used to switch apps).

## Wallet & Apple Pay (720, mention in 102)

- New `PKAddPassButton` styles. Apple Pay session can be customized with a `PKPaymentRequest` more comprehensively (paymentSummaryItems with multiple installments).
- `PKPaymentNetwork.barcode` and `.maestro` for additional regions.

## High-Volume Drawing: Use IO Surface Pixel Formats (219, 416)

- `kCVPixelFormatType_32BGRA` is the universal-compatibility default. Wide-color (P3) cameras can deliver 10-bit YpCbCr.
- For ML pipelines that just want grayscale: ask for `kCVPixelFormatType_OneComponent8` and skip the 4× memory cost.

## Cross-references

- Auto Layout best practices: 220 (full session).
- UICollectionView layouts: 225 (full session).
- UIKit dark mode is one year out (iOS 13). 2018's macOS-only dark mode is in `dark-mode-mojave.md`.
- Multi-line label measurement and intrinsic size optimization: 220.
