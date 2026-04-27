# iOS 11 Design Refresh — WWDC 2017 Analysis

**Sessions covered:** 201 (What's New in Cocoa Touch), 204 (Updating Your App for iOS 11), 207 (What's New in Cocoa), 245 (Building Apps with Dynamic Type), 230 (Advanced Animations with UIKit), 219 (Modern User Interaction on iOS), 235 (Building Visually Rich User Experiences), 242 (The Keys to a Better Text Input Experience), 802 (Essential Design Principles), 808 (Planning a Great Apple Watch Experience), 810 (What's New in iOS 11), 812 (Size Classes and Core Components), 813 (Writing Great Alerts), 815 (How to Pick a Custom Font), 817 (Rich Notifications), 218 (Choosing the Right Cocoa Container View)

## Headline

iOS 11 is the largest visual refresh since iOS 7. **Large titles, condensed nav bars, NSAttributedString-driven bar headers, full-bleed safe-area-driven layout, full Dynamic Type support, and the iPhone X edge-to-edge / notched canvas** all land together. Combined with new gesture and interaction APIs, the platform pushes apps toward bolder typography, content-forward layouts, and content-aware safe insets.

## Large Titles & Condensed Navigation (201, 204)

- `navigationItem.largeTitleDisplayMode = .always | .never | .automatic`
- `navigationController.navigationBar.prefersLargeTitles = true`
- The bar **automatically condenses** when the user scrolls — large title slides up into the standard nav bar position.
- **HIDDEN GEM**: nav bars now style their title with a full `NSAttributedString` via `largeTitleTextAttributes` and `titleTextAttributes` — kerning, color, font, baseline offset all work. No more "swap the titleView" hacks.
- Bar button items can be flexible-width with `largeContentSizeImage` for accessibility long-press magnification (see Accessibility section).

## Search In The Bar (201)

`navigationItem.searchController = UISearchController(…)` integrates the search bar into the nav bar. Set `hidesSearchBarWhenScrolling` to control visibility. **MIGRATION**: this replaces the iOS 8-era pattern of stuffing a `UISearchBar` into the table header.

## Safe Areas — The Replacement For Layout Guides (201, 204)

`UIView.safeAreaInsets` reports the inset from each edge that's safe for content (avoiding nav bar, status bar, home indicator, sensor housing on iPhone X). `safeAreaLayoutGuide` is a layout guide pinned to that area for Auto Layout.

```swift
view.addConstraint(NSLayoutConstraint.activate([
    contentView.leadingAnchor.constraint(equalTo: view.safeAreaLayoutGuide.leadingAnchor),
    contentView.trailingAnchor.constraint(equalTo: view.safeAreaLayoutGuide.trailingAnchor),
    contentView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
    contentView.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor)
]))
```

- **DEPRECATION**: `topLayoutGuide` and `bottomLayoutGuide` are deprecated. Migrate to `safeAreaLayoutGuide`.
- `UIScrollView.contentInsetAdjustmentBehavior` now controls whether the scroll view auto-applies `safeAreaInsets`. Read the COMPUTED total via `adjustedContentInset` — this is the actual inset the scroll view is using.

## iPhone X Specifics (201, 204)

- The display has **rounded corners** and a **sensor cutout (notch)** — content rendered with status-bar-relative layout will be clipped or hidden.
- `safeAreaInsets.top = 44` (instead of 20) in portrait — the notch effectively "owns" 24 pts more height for the status bar.
- `safeAreaInsets.bottom = 34` for the home indicator. **DON'T** put critical UI in this region — gestures can be intercepted.
- `prefersHomeIndicatorAutoHidden = true` returns false by default; set true for full-screen video and games to fade the indicator.
- `preferredScreenEdgesDeferringSystemGestures = .bottom` requests a two-touch gesture before the system swipe-up wins. Use sparingly.
- **WARNING**: launch images / launch storyboards must support the new screen aspect ratio (2436×1125 portrait). Apps using fixed launch images are LETTERBOXED on iPhone X — bad first impression. Adopt launch storyboards.

## Dynamic Type — Now Mandatory (245)

Dynamic Type sizes range from `.extraSmall` to `.accessibilityExtraExtraExtraLarge`. iOS 11 adds:

- **`UIFontMetrics.scaledFont(for:)`** — wraps any custom font, scaling it to the user's preferred size while preserving design.
- **`UIFontMetrics.default.scaledValue(for:)`** — scale fixed dimensions (icon sizes, padding) by the same factor.
- `adjustsFontForContentSizeCategory = true` on labels/text views opts into automatic re-layout when the user changes the size in Settings.

```swift
let metrics = UIFontMetrics(forTextStyle: .body)
let custom = UIFont(name: "Avenir-Book", size: 17)!
label.font = metrics.scaledFont(for: custom)
label.adjustsFontForContentSizeCategory = true
```

- **BEST PRACTICE**: stop hardcoding font sizes. Use `.preferredFont(forTextStyle: .body)` (or any text style) and let the system scale.
- **HIDDEN GEM**: text styles get **bold variants** automatically when "Bold Text" is on in Accessibility — no extra code if you used `.preferredFont`.
- **WARNING**: at `accessibilityExtraExtraExtraLarge`, .body text reaches 53 pt. Layouts with horizontal labels next to controls WILL break. Wrap rows in vertical stacks for these size categories. Check `traitCollection.preferredContentSizeCategory.isAccessibilityCategory` to switch layouts.

## Custom Fonts in iOS 11 (815)

- For most apps, **System Font (San Francisco)** is the right answer. SF was specifically designed for screen reading at every size. It includes condensed and rounded variants.
- **HIDDEN GEM**: `UIFont.systemFont(ofSize:weight:width:)` exposes width axes (compressed/condensed/regular/expanded) on supported sizes — no need to ship custom condensed fonts.
- Custom fonts: bundle with `UIAppFonts` array in Info.plist, then load via `UIFont(name:size:)`. Use Font Book to verify the **PostScript name** — file name is rarely the right name.
- Pair custom display fonts with system text fonts; reading body copy in a quirky display font hurts comprehension and accessibility.

## Animations — UIViewPropertyAnimator Matures (230)

`UIViewPropertyAnimator` (introduced in iOS 10) gains:

- **Custom timing curves** via `UICubicTimingParameters(controlPoint1:controlPoint2:)`.
- **Interruptible animations**: `pauseAnimation()` converts the active timing curve to **linear** automatically so your `fractionComplete` scrub maps 1:1 to elapsed time.
- **Continuation timing parameters**: when you `continueAnimation(withTimingParameters: …)` after a scrub, you can supply a different timing curve for the tail (e.g. spring out after a linear scrub) without snapping.
- **Multi-stage animations** via `addAnimations { … } delayFactor:` — chain phases inside one animator without blocking the queue.

**HIDDEN GEM**: keyframe animations are no longer needed for "first half does X, second half does Y" choreography. `UIViewPropertyAnimator` plus a `delayFactor` of 0.5 in the second `addAnimations` call is enough.

**HIDDEN GEM**: `addCompletion { position in … }` runs even if the animation is canceled. The `position` argument tells you whether it ended at `.start`, `.end`, or `.current` (interrupted) — the canonical place to revert ghost effects, restore alphas, etc.

## Document-Forward UI (235)

- Wide-color, P3-aware UIImageView and CALayer rendering by default in iOS 11. Asset Catalog supports per-display-gamut variants. **PERFORMANCE**: ship Display P3 PNG/HEIC if you can; the system downsamples for sRGB devices.
- `UIGraphicsImageRenderer` (iOS 10) gains P3 support — render once, get correct color on every device.
- HEIF / HEVC support throughout (see `heif-hevc-photos.md`).

## Modal Presentation Style Refresh (810)

iPhone X aside, sheets and full-screen presentations now respect safe areas automatically. Form sheets reflow on rotation. **WARNING**: assumptions like "this view's frame matches `UIScreen.main.bounds`" break on iPad Split View — always use `view.bounds` and `view.safeAreaInsets`.

## Notifications: Critical Alerts and Rich Content (817)

- Notifications can attach inline media (image/audio/video) and dynamic content via `UNNotificationContentExtension`.
- New: **HIDDEN HOOK**: notification content extensions can be made INTERACTIVE in iOS 11 (`mediaPlayPauseButtonType = .default | .none | .overlay`). Rich notifications can scrub video, vote, etc., without launching the app.
- **PERFORMANCE**: notification service extensions get ~30 seconds of wall time. If you're downloading inline imagery, fall back to the no-image notification on timeout — the system will deliver the original.

## Apple Watch (808) — Companion Considerations

- Independent watch apps don't yet exist (that's 2019), but watchOS 4's complications and custom controls reward apps that **show one number well** rather than reproducing the iPhone UI.
- The "Modular" face is the most code-friendly canvas — design first there, scale down to "Utility" and "Infograph".

## Writing Great Alerts (813)

- Use 2 buttons. Three is the absolute max.
- The **destructive** button goes on the left (cancel-side) on iOS — a deliberate friction. The default is the safe action.
- Title in sentence case, no period. Message in full sentences with periods.
- **WARNING**: never present an alert from `applicationDidBecomeActive` — use viewWillAppear of your foreground VC. Alerts at app launch race with the launch image and look broken.

## Touch Bar (211, 222)

- Touch Bar APIs come to UIKit on Catalyst-precursor terms — but for 2017 specifically, the message is "Mac apps use NSTouchBar; iPad apps don't get a touch bar". Plan for NSTouchBar adoption in companion Mac apps.

## Cross-references

- See `swift4-language-codable.md` — `safeAreaInsets`/Codable refresh.
- See `accessibility-everywhere.md` — Dynamic Type pairs with VoiceOver and Smart Invert.
- See `arkit-debut.md` — full-bleed AR camera passthrough requires safe-area-aware layout.
