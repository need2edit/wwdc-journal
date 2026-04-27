# Drag and Drop on iPad — WWDC 2017 Analysis

**Sessions covered:** 203 (Introducing Drag and Drop), 213 (Mastering Drag and Drop), 223 (Drag and Drop with Collection and Table View), 227 (Data Delivery with Drag and Drop), 219 (Modern User Interaction on iOS — drag-aware gesture system), 201 (What's New in Cocoa Touch — drag/drop API summary)

## Headline

iOS 11 introduces **system-wide drag and drop** on iPad: between apps, within apps, with multi-touch (drag with one hand, tap to flock more items with the other), with live previews, with type-safe asynchronous data delivery via `NSItemProvider`. On iPhone, drag and drop is **app-internal only** — disabled by default and opt-in.

## Three New Interactions (203, 213)

- **`UIDragInteraction`** — install on any `UIView`. Handles long-press lift, snapshot, gesture bookkeeping, and preview animation. Implement `UIDragInteractionDelegate` (one required method: `dragInteraction(_:itemsForBeginning:)`).
- **`UIDropInteraction`** — install on the destination view; implement `canHandle:`, `sessionDidUpdate:`, `performDrop:`, and `concludeDrop:`.
- **No subclassing** required. No need to mutate existing UIView superclasses or call out to gesture recognizers manually.

## NSItemProvider — The Universal Currency (227)

Every drag item is an `NSItemProvider`. It can produce one or more representations of the same content (e.g. a UIImage as both `public.jpeg` data and a `UIImage` instance), each loaded asynchronously.

```swift
let provider = NSItemProvider(object: messageView.snapshot())
provider.registerObject(message, visibility: .ownProcess)
provider.preferredPresentationSize = CGSize(width: 280, height: 200)
let item = UIDragItem(itemProvider: provider)
item.localObject = message  // for fast in-app reference
```

- **HIDDEN GEM**: `preferredPresentationSize` is a side-channel hint that lets the destination size the drop preview **before** the data finishes loading. That's how Mail's compose sheet pre-allocates space for an image dragged from Photos.
- **HIDDEN GEM**: `localObject` is the easy-mode for in-app drag-and-drop. Skip building an itemProvider for cross-app transfer; just stash a Swift reference. Read it back via `session.items.first?.localObject as? Message`.

## Flocking (213)

Native iOS apps let you start a drag, then tap subsequent items with another finger to add them to the same drag session.

```swift
func dragInteraction(_ interaction: UIDragInteraction,
                     itemsForAddingTo session: UIDragSession,
                     withTouchAt point: CGPoint) -> [UIDragItem] {
    // Filter to compatible types only:
    let allCompatible = session.items.allSatisfy {
        $0.itemProvider.hasItemConformingToTypeIdentifier("public.example.mail")
    }
    guard allCompatible else { return [] }   // empty array aborts → other gesture recognizers can recognize
    // Avoid re-flocking the same model object:
    let already = session.items.compactMap { $0.localObject as? Message }
    guard !already.contains(message) else { return [] }
    return [makeDragItem(for: message)]
}
```

**BEST PRACTICE**: returning `[]` from `itemsForAddingTo` lets other gestures (like a tap to select) win. Returning items consumes the tap.

## Drag Previews (213)

Three customization points:

1. **`UITargetedDragPreview`** — a snapshot of a view, with optional `parameters` (background color, visible Bezier path) and a `target` (container view + center point + transform). Returned from `previewForLifting item:` and `previewForCancelling item:`.
2. **`UIDragPreviewParameters`** — `backgroundColor` (typically `.clear`) and `visiblePath` (a `UIBezierPath` that crops the lifted shape; can extend BEYOND the source bounds for "platter" effects like Mail's compose).
3. **`UIDragPreview` (without target)** — used to UPDATE the preview AFTER lift via `dragItem.previewProvider = { … return UIDragPreview(…) }`. Maps showing a map snippet replacing the source row is built this way. Set `previewProvider` inside `sessionDidMove(_:)` after the user has dragged outside the source view.

**HIDDEN GEM**: the preview block may NOT be called for every dragged item — if you lift many, the system shows only the top few. Don't run heavy work outside the block.

## Animating Alongside Lift / Drop / Cancel (213)

Each lifecycle hook gets a `UIDragAnimating` animator (`UIViewPropertyAnimator`-shaped):

```swift
func dragInteraction(_ interaction: UIDragInteraction,
                     willAnimateLiftWith animator: UIDragAnimating,
                     session: UIDragSession) {
    animator.addAnimations { sourceView.alpha = 0.5 }   // ghost the original
    animator.addCompletion { _ in sourceView.alpha = 1.0 }  // restore on cancel
}
```

The view is LIVE during the animation — changes you make in the animator block ARE captured in the snapshot taken at finger-move start. So fade out highlight overlays before snapshot.

## The Drop Side (213)

Drop session lifecycle:

```
canHandle → sessionDidEnter → sessionDidUpdate (repeated) → performDrop → concludeDrop → sessionDidEnd
                                  ↘ sessionDidExit ↗ (if user wanders out)
```

`sessionDidUpdate` returns a `UIDropProposal` with:

- `operation`: `.copy`, `.move`, `.cancel`, `.forbidden`
- `isPrecise`: hit-test ABOVE the finger position so users can see what they're targeting (text-cursor placement uses this)
- `prefersFullSizePreviews`: ask not to scale down (e.g., for in-app reordering of large rows)

**WARNING**: `sessionDidUpdate` is called constantly — keep it cheap or you'll drop frames.

## Async Data Loading (213, 227)

**Data is only loadable inside `performDrop`.** All earlier callbacks return nothing useful from `loadObject(of:)`. Use the homogeneous shortcut for simple cases:

```swift
session.loadObjects(ofClass: UIImage.self) { images in
    // Called on main queue. Add images to grid.
}
```

For mixed types, iterate `session.items` and call `loadObject(ofClass:)` / `loadDataRepresentation(forTypeIdentifier:)` per item. Those completion blocks fire on a background queue — dispatch back to main.

**WARNING**: every load is asynchronous. Photos may live in iCloud and take seconds to fetch. **Never assume data has arrived.** The system shows a modal progress indicator with a Cancel button automatically; if you'd rather show inline progress, set `session.progressIndicatorStyle = .none` and observe `session.progress` (`Progress` object) yourself, plus per-item progresses from each `loadObject` call.

## Default Preview vs Custom Preview at Drop (213)

`previewForDropping item: withDefault defaultPreview:` — return:

- `nil` to accept defaults
- `defaultPreview.retargetedPreview(with: target)` to keep the source-side appearance but animate to a new location
- a brand-new `UITargetedDragPreview` for full custom UI (e.g., a spinning loader for slow data)

**HIDDEN GEM**: when a drag finishes with many items in a flock, the system asks for previews only for the visible top items, never the hidden ones. Don't pre-compute previews for invisible items.

## In-App Drag and Drop (213)

- **`session.localDragSession`** on a `UIDropSession` — non-nil only for in-app drags. Lets you reach into the original drag's items, including their `localObject`.
- **`session.localContext`** on a `UIDragSession` — a free `Any?` slot to stash whole-session state across drag/drop.
- **`dragInteraction(_:sessionIsRestrictedToDraggingApplication:)`** — return `true` to BLOCK drags from leaving your app. Visually identical, but cross-app drops fail.
- **iPhone**: `dragInteraction.isEnabled = true` is required (iPad: enabled by default). This is intentional — UIKit assumes single-app contexts on iPhone.

## Collection & Table View Integration (223)

Pre-built drag/drop conformances:

- `UICollectionViewDragDelegate` / `UICollectionViewDropDelegate`
- `UITableViewDragDelegate` / `UITableViewDropDelegate`

Provide `itemsForBeginning:atIndexPath:`, `dropSessionDidUpdate:withDestinationIndexPath:`, and `performDropWith:`. The collection/table view handles **placeholder cells with built-in spinners** for slow async data — set `dragItem.previewProvider`, the cell shrinks/expands automatically.

**BEST PRACTICE** (223): use `coordinator.drop(_:to: placeholder)` for async drops — UIKit shows a placeholder cell with a progress indicator and replaces it once your `loadObject` completes. Zero code for the spinner.

## Gesture System Updates (219)

`UIDragInteraction` integrates into the existing gesture system. **Drag-and-drop now cancels touches more often**: any in-progress responder-based touch handling will receive `touchesCancelled(_:with:)` if a drag begins on top of it.

- **WARNING**: implement `touchesCancelled` in custom views. Without it, you'll have stale state pointers after drags.
- **HIDDEN GEM**: `UIGestureRecognizer.name` (new in iOS 11) gives you a debugging label visible in lldb. Apple promises not to mess with it — use freely.

## Cross-references

- See `files-document-browser.md` for the `UIDocumentBrowserViewController` flow which builds atop drag-and-drop.
- See `ios11-design-language.md` for adoption guidelines and visual conventions.
