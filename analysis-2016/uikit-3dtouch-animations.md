# UIKit, 3D Touch & Animations — WWDC 2016 Analysis

**Sessions covered:** 216 (Advances in UIKit Animations and Transitions), 220 (Leveraging Touch Input on iOS), 228 (A Peek at 3D Touch), 233 (Making Apps Adaptive, Part 2), 222 (Making Apps Adaptive, Part 1), 219 (What's New in UICollectionView in iOS 10), 236 (What's New in Auto Layout)

## Headline

UIKit gets two big foundational additions in iOS 10:

1. **`UIViewPropertyAnimator`** — interruptible, scrubbable, reversible animations with custom timing functions and 2D spring vectors. Layer-driven, integrates with view-controller transitions.
2. **`UIPreviewInteraction`** — same force-processing engine as Peek-and-Pop, but with your own custom UI. Makes 3D Touch a building block for any interaction.

Plus modernized auto-layout (incremental adoption with autoresizing-mask alongside constraints), pre-fetching collection views, and the layout feedback loop debugger.

## UIViewPropertyAnimator — finally, interruptible animations

The legacy `animateWithDuration:` API is fire-and-forget. `UIViewPropertyAnimator` returns an object you can:
- Pause and scrub via `fractionComplete`.
- Reverse mid-flight (smoothly via `isReversed`, or sharply by setting new target values).
- Stop at the current visual state, promote it to model values, finish at any position.
- Continue with NEW timing parameters (different curve, different duration).
- Add more animations to a running animator.

```swift
let animator = UIViewPropertyAnimator(duration: 1.0, curve: .easeInOut) {
    self.box.center.x += 200
}
animator.addCompletion { position in
    // position: .start, .end, or .current
}
animator.startAnimation()

// Later, mid-flight:
animator.pauseAnimation()
animator.fractionComplete = 0.3   // scrub to 30%
animator.isReversed = true
animator.continueAnimation(withTimingParameters: nil, durationFactor: 0.5)
```

### Three new timing parameter types

| Type | Use |
|------|-----|
| `UICubicTimingParameters(animationCurve: .easeInOut)` | Existing canned curves |
| `UICubicTimingParameters(controlPoint1:controlPoint2:)` | Custom Bézier curve — make your own "speed in, speed out" |
| `UISpringTimingParameters()` | Critically-damped spring (matches navigation push/pop) |
| `UISpringTimingParameters(dampingRatio:initialVelocity:)` | Damped spring with explicit ratio |
| `UISpringTimingParameters(mass:stiffness:damping:initialVelocity:)` | Full physics — duration ignored, computed from the spring equation |

**HIDDEN GEM:** Spring's `initialVelocity` is now a **2D `CGVector`** — when animating a view's `center`, Apple uses both X AND Y components. Means a swipe-and-release at any angle is honored correctly (the view springs back along the gesture's actual direction, not just the connecting line).

### Stop and finish at any position

```swift
animator.stopAnimation(/*withoutFinishing*/ false)  // freeze model at current visual
// you can now drag the view yourself…
animator.finishAnimation(at: .current)             // commits position & calls completions
```

### Hit testing of moving views (HIDDEN GEM)

`UIViewPropertyAnimator.isManualHitTestingEnabled` defaults to **`false`** — the system hit-tests against the **presentation layer** (where the view APPEARS), not the model layer (where it's GOING). You can tap a moving view and "catch" it. This is why Peek-and-Pop with the new animator feels right.

If you have deep view hierarchies, the override-`hitTest:` technique from past WWDCs still works.

### Interruptible view-controller transitions

`UIViewControllerInteractiveTransitioning` gains new methods. The protocol is mostly the same — return `interruptibleAnimator(using:)` returning a `UIViewImplicitlyAnimating`. `UIPercentDrivenInteractiveTransition` now consumes that animator transparently, supporting interrupt → animate → interrupt → animate cycles freely.

The transition `pauseInteractiveTransition()` lets a transition flow into and out of interactive mode multiple times. The transition context's `wantsInteractiveStart` flag tells the system whether the initial state is interactive or animated.

**HIDDEN GEM:** Built-in `UINavigationController.interactivePopGestureRecognizer` previously couldn't coexist with custom interaction controllers. iOS 10 fixes this — set a failure requirement between your gesture and the system's, and they coexist cleanly.

### Interruptible keyframe animations

```swift
animator.addAnimations {
    UIView.animateKeyframes(withDuration: 1, delay: 0, options: []) { /* keyframes */ }
}
```

Wrapping a keyframe block inside a property animator gives you a fully scrubbable keyframe sequence — pause anywhere, reverse, blend.

## 3D Touch — UIPreviewInteraction

`UIViewControllerPreviewing` (Peek and Pop) is the cell-tap-pressure pattern. `UIPreviewInteraction` is the **NEW lower-level API** for arbitrary 3D Touch interactions with **your own UI**.

```swift
let interaction = UIPreviewInteraction(view: replyButton)
interaction.delegate = self

// Required delegate methods:
func previewInteraction(_ interaction: UIPreviewInteraction,
                        didUpdatePreviewTransition transitionProgress: CGFloat,
                        ended: Bool) {
    // 0..1 progress through preview phase
    self.replySheetView.alpha = transitionProgress
    self.replySheetView.transform = CGAffineTransform(scaleX: 0.5 + transitionProgress * 0.5,
                                                       y: 0.5 + transitionProgress * 0.5)
}

func previewInteractionDidCancel(_ interaction: UIPreviewInteraction) {
    UIView.animate(withDuration: 0.3) {
        self.replySheetView.alpha = 0
        self.replySheetView.transform = .identity
    }
}

// Optional commit phase:
func previewInteraction(_ interaction: UIPreviewInteraction,
                        didUpdateCommitTransition transitionProgress: CGFloat,
                        ended: Bool) { /* progress 0..1 from preview to commit */ }
```

The system plays haptic feedback automatically at the preview and commit thresholds — same haptics users have learned from Peek-and-Pop. Your custom UI inherits the muscle memory.

**Key insight:** progress is NOT a direct force translation. It's an intent-detection algorithm tuned to feel right. Ride the same algorithm that powers Peek-and-Pop in Mail, Messages, etc.

### Use case: in-context emoji picker (Apple's example)

A reply button that on press progressively reveals an emoji sheet. While pressed, slide finger over an emoji to select. Release to send. **One-touch interaction** end-to-end — no explicit modal, no tap-then-tap-then-tap.

## Home Screen Quick Actions (refresher)

Static (Info.plist `UIApplicationShortcutItems`) and Dynamic (`UIApplication.shared.shortcutItems`). Up to 4 total. Dynamic actions support contact-photo icons:

```swift
let icon = UIApplicationShortcutIcon(contact: cnContact)  // contact photo from address book
```

Handled in `application(_:performActionFor:completionHandler:)` (when launching from background) or via the `UIApplicationLaunchOptionsShortcutItemKey` in `application(_:didFinishLaunchingWithOptions:)` (when launched cold).

**BEST PRACTICE:** Keep dynamic actions predictable. Don't reorder them constantly — users build muscle memory for "tap → press → first action."

**HIDDEN GEM:** Be prepared for shortcut items from a previous app version. Encode a version number in the shortcut's `userInfo` so a stale shortcut from V1 launching V2 can degrade gracefully.

## Auto Layout enhancements (session 236)

### Mix autoresizing masks with constraints (NEW)

Previously, mixing the two crashed. iOS 10 / macOS Sierra:
- Views without constraints can use Springs & Struts (autoresizing masks).
- Views with constraints use the constraint engine.
- They coexist peacefully in the same hierarchy.
- The translation `translatesAutoresizingMaskIntoConstraints = true` happens at runtime now (not build time), allowing programmatic flexibility.

**Benefit:** incremental adoption. Start a new layout with autoresizing masks for simple resize behaviors; add constraints to children that need more sophisticated rules. No big-bang Auto Layout migration.

### Placeholder constraints

In Interface Builder, mark constraints as **placeholders** (removed at build time) for cases where you'll add the real constraints at runtime — useful when you don't know image aspect ratio until image data arrives. Combined with intrinsic-content-size placeholders (custom controls show a designed size in IB but use real `intrinsicContentSize` at runtime).

### Per-view ambiguity verification levels

If a view is intentionally ambiguous in IB until runtime, set its ambiguity verification level to "verify position only" or "never" — clears the IB clutter without losing real warnings elsewhere.

### NSGridView (macOS only)

A new container that aligns content across both rows AND columns (which `NSStackView` couldn't). Cells, rows, columns each have x/y placement. Cells can merge. Rows/columns can be hidden or padded. Custom constraints can override grid placement when needed. Intended primarily for static settings/preferences UI.

### Layout feedback loop debugger

Set the launch argument `-UIViewLayoutFeedbackLoopDebuggingThreshold 100` (iOS) or `-NSViewLayoutFeedbackLoopDebuggingThreshold 100` (macOS). When a view's `layoutSubviews` runs more than the threshold within one runloop turn, the system collects backtraces, identifies the top-level view, and dumps both an exception and a detailed log to the unified logging system (subsystem `com.apple.UIKit`/`com.apple.AppKit`, category `layout-loop`).

Two failure modes the log helps diagnose:
- **Upstream geometry change** — a child view modifies its superview's bounds during layout, cascading.
- **Constraint ambiguity** — variable values oscillate during update-constraints.

## UICollectionView prefetching (NEW)

```swift
class MyDataSource: NSObject, UICollectionViewDataSource, UICollectionViewDataSourcePrefetching {
    func collectionView(_ collectionView: UICollectionView,
                        prefetchItemsAt indexPaths: [IndexPath]) {
        // start network/disk loads for these upcoming cells
    }
    func collectionView(_ collectionView: UICollectionView,
                        cancelPrefetchingForItemsAt indexPaths: [IndexPath]) {
        // user scrolled away — cancel
    }
}
```

Same pattern for `UITableView` via `UITableViewDataSourcePrefetching`. Massive scrolling-perf win for media-heavy lists. Apple uses this in Photos.

**BEST PRACTICE:** Cancel prefetches aggressively in the `cancel...` callback. Otherwise you're wasting bandwidth on cells the user already scrolled past.

## Force touch APIs (low-level, session 220)

`UITouch.force` and `UITouch.maximumPossibleForce` populate on 3D-Touch-capable devices AND for Apple Pencil touches. Use directly in custom drawing/game inputs.

## Best practices summary

- Migrate animations to `UIViewPropertyAnimator` for any transition users might interrupt.
- Use `UIPreviewInteraction` to add 3D-Touch micro-interactions to your UI — leverage existing user muscle memory.
- Adopt `UIApplicationShortcutItem` — every app should have at least one.
- Implement `UICollectionViewDataSourcePrefetching` for any media-list view.
- Mix autoresizing masks with constraints freely now — incremental Auto Layout adoption is the norm.
- Set the layout feedback loop debugger threshold in your CI/test schemes — catches infinite layout loops early.

## Hidden gems summary

- `isManualHitTestingEnabled = false` (default) on `UIViewPropertyAnimator` enables hit-testing on moving views.
- Spring `initialVelocity` is now a 2D `CGVector` honoring gesture direction.
- Wrapping a keyframe block in `UIViewPropertyAnimator` makes it scrubbable.
- Built-in nav-pop interactive gesture coexists with custom transitions via failure requirements.
- Layout feedback loop debugger threshold is gated 50–1000 — set it in test schemes.
- ASTC-style asset catalog compression also applies here.

## Cross-references

- Wide color in CALayer.contentsFormat → analysis-2016/wide-color-display.md
- 3D Touch quick actions → above
- Adaptive layouts (sessions 222, 233) → covered briefly above
