# Touch Input, 3D Touch & Cocoa Touch Best Practices — WWDC 2015 Analysis

**Sessions covered:** 233 (Advanced Touch Input on iOS), 231 (Cocoa Touch Best Practices), 229 (What's New in UIKit Dynamics and Visual Effects), 217 (Adopting New Trackpad Features), 215 (What's New in Storyboards), 232 (Best Practices for Progress Reporting), 234 (Building Document Based Apps), 222 (New UIKit Support for International User Interfaces), 227 (What's New in Internationalization), 225 (What's New in NSCollectionView)

## Headline

iOS 9 takes industry-leading touch latency from ~60ms down to **<30ms** through a combination of hardware (iPad Air 2's 120Hz touch scan rate) and software (low-latency Core Animation, touch coalescing, touch prediction). Plus the iPad Pro's pencil and the imminent iPhone 6s 3D Touch are previewed via APIs.

## The Touch Pipeline (233)

Five stages from finger to pixel:

1. **Multi-Touch hardware scan** — up to 1 display frame at 60Hz; HALF a frame at 120Hz on iPad Air 2.
2. **App's UITouch callback** — your `touchesBegan`/`touchesMoved`/`touchesEnded` runs; you update model state.
3. **Core Animation render server** — turns logical view tree into GPU commands.
4. **GPU rendering**.
5. **Display refresh** (60Hz vsync swap).

In iOS 8: 4 frames of latency. In iOS 9 with all optimizations: **1.5 frames**.

## Low-Latency Core Animation (233)

iOS 9 collapses stages 2 and 3 into a single frame when possible — your app's frame and Core Animation's translation step happen back-to-back rather than waiting for the next display refresh between them.

- Free for Core Animation content. **PERFORMANCE**: disabled when CA animations or UIKit animations are active. Cancel/pause animations during touch tracking for the absolute lowest latency.
- For Metal/OpenGL content: `CAEAGLLayer.presentsWithTransaction` and `CAMetalLayer.presentsWithTransaction`. Default false (lowest latency, GPU content may arrive 1 frame ahead of Core Animation overlay). Set true to synchronize when you must (e.g., overlays on a video that need to lock to specific frames).

## Touch Coalescing (233)

iPad Air 2 scans touches at 120Hz but the display still updates at 60Hz. Without coalescing, your app would receive twice as many `touchesMoved` callbacks → wasted work.

- `UIEvent.coalescedTouches(for: touch) -> [UITouch]?` returns the in-frame intermediate samples PLUS the main touch as the last element.
- The MAIN touch stream is delivered at 60Hz; coalesced touches give you the higher-fidelity 120Hz data on demand for things that need precision (drawing apps).
- **HIDDEN GEM**: each coalesced touch is a NEW `UITouch` instance (snapshot semantics). Main touches reuse the same instance across calls (identity). Don't compare with `===` across both worlds.
- **CRITICAL**: don't cross the streams. Use main touches OR coalesced touches consistently within a feature; mixing causes confusing `previousLocation(in:)` results.

## Touch Prediction (233)

UIKit looks at recent samples and predicts where the touch will be in ~1 frame. `UIEvent.predictedTouches(for: touch) -> [UITouch]?`.

- Use predictions to extend your line drawing into the near future.
- Each new main touch obsoletes the previous predictions — discard them.
- Drawing pattern: append predictions to the rendered line marked "predicted." Next frame, remove the predicted samples and re-add the actual ones.

Net latency wins:
- iOS 9 + low-latency CA: -1 frame
- + iPad Air 2 coalescing: -0.5 frame
- + Touch prediction: -1 effective frame
- **Total: 4 frames → 1.5 frames**

## UIKit Dynamics & Visual Effects (229)

- **Non-rectangular collision bounds**: elliptical and path-based. Realistic collisions for non-square shapes.
- New **field behaviors**: linear gravity, radial gravity, spring, drag, velocity, noise, turbulence, electric, magnetic, plus a custom field block.
- New **attachment types** simplifying multi-attachment configurations.
- **Animatable blur radius** on `UIVisualEffectView` — animate views in/out of blur smoothly.

## Cocoa Touch Best Practices (231)

Luke Hiesterman's distillation:

### Lifecycle

- `application(_:didFinishLaunchingWithOptions:)` returns FAST. Defer DB / network / heavy setup to background queue, dispatch back to main on completion.
- "Move work to background queues" is the deeper rule than "use async."
- **Memory in the background**: aggressively trim caches when going to background. Don't be the largest background app — you're the first kill candidate when the foreground app needs more memory.

### Versioning

- Target the latest 2 major iOS versions. Wider deployment is rarely worth the maintenance cost.
- NEVER write `if SystemVersion.current == "9.0.0"` — write `>=`.
- In Swift, use `#available(iOS 9.0, *)` (see swift-2-language analysis).
- Always include the else-clause when checking versions; ensure the legacy path is functional.

### Layout

- Don't think portrait/landscape. Think size class. The author is unequivocal: "If the word 'portrait' or 'landscape' came out of your mouth, you're already thinking about it wrong."
- The matrix of (iPhone sizes × iPad sizes × multitasking widths) is too large for fixed dimensions. Lay out proportionally.

### View tags vs properties

- **PERFORMANCE/SAFETY**: stop using `viewWithTag` and `tag` properties. They're integers with collision potential, no compiler typing. Use real properties of the correct type. (Audience applauded.)

### Animation timing

- Don't use `NSTimer` to fire after a guess at how long an animation takes. Use `UIViewControllerTransitionCoordinator` — it knows the actual timing AND handles cancellation/interruption.

### Auto Layout performance

- NEVER call `removeAllConstraints` on `view.constraints`. System-internal constraints live there too; you'll create unsatisfiable layouts.
- Keep references to constraints you'll change. Don't tear down and rebuild — modify in place.
- Don't OVERSPECIFY (extra implied constraints slow the engine). Don't UNDERSPECIFY (ambiguous layout).
- Debug ambiguity: `UIView.hasAmbiguousLayout` returns true if there's ambiguity in this view's subtree. `UIView.exerciseAmbiguityInLayout()` randomly chooses among ambiguous layouts to expose the problem visually. Wrap in unit tests.

### Self-sizing table view cells

- Pin top + bottom of content to content view; set `tableView.estimatedRowHeight`; `rowHeight = .automatic` (UITableView.automaticDimension).
- Animate height changes with `beginUpdates`/`endUpdates` (NOT `reloadData` and NOT `reloadRows`). You can directly modify the cell's view properties between begin/end.
- For a debugging hint: temporarily add an explicit height constraint to your content view derived from your other constraints — if the cell is sized correctly with it, your other constraints are fine; if size differs, you have ambiguity.

### Fast custom collection view layouts

- Use `UICollectionViewLayoutInvalidationContext` with targeted invalidation. The Photos sticky-header layout invalidates every frame but only the supplementary header view, not all the cells. Frame-rate scrolling stays smooth.

## 3D Touch / Force Touch (217 for Mac trackpad; iOS 6s previewed)

- Mac: `NSEvent` provides pressure values via `pressure` and `stage`. Spring-loaded actions on `NSButton`.
- WebKit Force Touch (501) covered force events with `webkitmouseforcewillbegin`, `webkitmouseforcedown`, `webkitmouseforceup`, `webkitmouseforcechanged`, plus `webkitForce` on every mouse event.
- iPhone 6s 3D Touch APIs landed September 2015 with iOS 9.0 — `UIPreviewInteraction`, peek and pop via `UIViewControllerPreviewing`. Not in WWDC 2015 sessions.

## Internationalization (227, 222)

- Right-to-left support: in iOS 9, opting into the iOS 9 SDK auto-flips ALL UIKit. Navigation reverses. Sliders, switches, table swipe actions reverse. Animations reverse. (See ipad-multitasking analysis for `semanticContentAttribute`.)
- New `UIImage` flipped variant API for control glyphs.
- Improved date/number formatting performance via cached formatters in `Foundation`.

## Storyboards (215)

- **Storyboard References**: `UIStoryboard` segue can target an external storyboard. Break up monolithic storyboards into feature-scoped ones, reference between them.
- Unwind segues in IB.
- Multiple-storyboard merge conflicts in Git get tractable.

## Document-Based Apps (234)

- `UIDocument`-based apps integrate with iCloud Drive. New "Open in Place" — instead of forcing a copy, let the document app open the actual file in iCloud Drive.
- Adoption: declare conformance via Info.plist key `LSSupportsOpeningDocumentsInPlace`, implement new delegate method.
- Improvements to `UIDocumentMenuViewController` and `UIDocumentPickerViewController`.

## NSCollectionView on macOS (225)

- macOS finally gets a proper UICollectionView equivalent (was XIB-based prior). Diffable layouts via `NSCollectionViewLayout` subclasses.
- Item-based with prefetching, supplementary views, multi-item updates, drop targets.

## Cross-references

- Touch latency work (233) intersects with energy (707) — fewer wasted draws save power.
- Cocoa Touch best practices (231) layer on iPad multitasking (205) — proportional layout becomes mandatory.
- Internationalization (222, 227) plus accessibility (201, 204) define the universal-app baseline.
