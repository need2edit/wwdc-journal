# iPad Multitasking — WWDC 2015 Analysis

**Sessions covered:** 205 (Getting Started with Multitasking on iPad in iOS 9), 211 (Multitasking Essentials for Media-Based Apps on iPad in iOS 9), 212 (Optimizing Your App for Multitasking on iPad in iOS 9), 107 (What's New in Cocoa Touch), 218 (Mysteries of Auto Layout, Part 1), 219 (Mysteries of Auto Layout, Part 2), 215 (What's New in Storyboards), 222 (New UIKit Support for International User Interfaces)

## Headline

For the first time ever, iPad gets real multitasking. Three modes:

1. **Slide Over**: a secondary app appears in a compact column from the right.
2. **Split View**: two apps side-by-side at 1/3, 1/2, or 2/3 split (Air 2 only).
3. **Picture in Picture**: video continues in a movable, resizable mini-window.

This is THE structural shift of WWDC 2015. Every iPad app must adapt or feel broken.

## Adoption Cost (205)

Three steps to get multitasking on iPad:

1. Build with the iOS 9 SDK.
2. Support all four interface orientations on iPad.
3. Use a Launch Storyboard (introduced 2014). Launch Images cannot satisfy every multitasking size.

Opt out (full screen apps like games): `UIRequiresFullScreen = YES` in Info.plist.

**HIDDEN GEM**: All NEW Xcode 7 projects ship with multitasking enabled by default — it's literally three steps because steps 1, 2, and 3 are pre-checked.

## Adaptivity Model (205, 107)

The size class system from iOS 8 was always about this — last year was the rehearsal.

- App's window bounds ≠ screen bounds anymore. Always use `view.bounds` or `window.bounds`.
- Window origin is always (0,0) regardless of which side of the split you're on.
- A multitasking resize is just a `viewWillTransition(toSize:)` call. Same code path as a rotation.
- A 1/3 column is **horizontally compact** (the "iPhone-like" experience). 2/3 and full are **horizontally regular**.
- Not every resize is a size class change. A small Split View resize at the boundary may stay regular while just shrinking — your code must distinguish.
- **BEST PRACTICE**: stop thinking "iPhone vs iPad" or "portrait vs landscape." Think "compact vs regular size class" exclusively. (Luke Hiesterman in 231: "If the word 'portrait' or 'landscape' came out of your mouth, you're already thinking about it wrong.")
- Both `willTransition(to:)` and `viewWillTransition(toSize:)` give you a `UIViewControllerTransitionCoordinator` for `animateAlongsideTransition` — same APIs as rotation.

## Six Strategies (205)

Kurt Revis's six rules:

1. **Be flexible** — no hard-coded sizes; respond to size changes; test all transitions in all 5 modes.
2. **Use Auto Layout** — and the new `NSLayoutAnchor` convenience APIs (see Auto Layout below).
3. **Use Interface Builder size class adaptations** — different constraints, fonts, and asset catalog images per size class. The IB live preview pane shows multiple device + multitasking configurations simultaneously.
4. **Adopt the size class API in code** — `willTransition(toTraitCollection:)` and `viewWillTransition(toSize:)`.
5. **Use UIPresentationController** — popovers automatically adapt to fullscreen on compact width. Implement `adaptivePresentationStyle(for:)` to customize the adaptation (e.g., add a Done button when the popover becomes a sheet).
6. **Use UISplitViewController** — handles primary/secondary collapse-to-navigation automatically when adapting to compact width.

## Performance & Memory — The Real Constraint (212)

Brittany Paine and Jon Drummond's session is the hidden masterclass on iOS memory management.

- **CPU/GPU degrade gracefully** when shared. Memory does NOT — when the system runs out, it kills processes.
- The primary app, secondary app, AND PiP all share one device. Your app might be killed even when it didn't cause the spike.
- **Working set discipline**: only keep what you need *right now* in dirty memory. The IconReel example walks through three iterations:
  - Naive (every icon in memory): scrolling smooth, memory crashes
  - One-page working set: low memory, scrolling stutters
  - Three-page working set + NSCache for evicted pages: balanced
- **HIDDEN GEM**: when the secondary app shrinks YOUR app from 4 columns to 3 columns, that's the trigger to reassess your working set, not just the size change.
- `NSCache` evicts on memory warnings AND application context (foreground/background) automatically.
- **HIDDEN GEM**: NSPurgeableData is dirty memory you've explicitly told the system can be reclaimed. `beginContentAccess()` says "I'm using it right now"; `endContentAccess()` says "you can take it." You get cache-like behavior with system-managed eviction.
- **Memory mapping for clean memory**: write your computed cache to disk as one large file with `NSData(contentsOfURL:options:[.DataReadingMappedAlways])`. The system can transparently page in/out the regions you access. Counts as **clean memory** — doesn't cost you against your memory limit.
- Caveats for memory mapping: not for tiny files (page granularity is the floor), don't open thousands of mapped files (file descriptor limits), don't memory-map a 10GB file (VM space).
- "The world outside your process should be regarded as hostile and bent upon your destruction." — design for the case where the system is forced to kill you for someone else's spike.

## QoS and Background Work (212, 718)

- All foreground apps share equal-priority QoS bands (no app gets priority over another by being primary).
- Use `dispatch_async` with proper QoS so the system can prioritize across apps.
- Auditing for `dispatch_group_wait` and `dispatch_semaphore_wait` is critical — these block the QoS override mechanism. The system can't raise the priority of work blocked behind a semaphore. Use `dispatch_block_wait` instead, which has known ownership.
- For UI-blocking I/O on a low-QoS queue: dispatch a `dispatch_sync` barrier from main onto the I/O queue to **temporarily boost** the entire queue to user-interactive QoS until the synced block runs.

## Picture in Picture (211, 107)

- Background-audio apps that already enable background playback can opt into PiP for video.
- Use `AVPictureInPictureController` (auto-managed when you use AVKit's `AVPlayerViewController`).
- Only the primary app sees the external display in multitasking. If your app starts in Slide Over and gets promoted to primary, you'll suddenly receive the screen-connected notification — make sure you handle it gracefully.

## Auto Layout — Practical Guidance (218, 219)

`NSLayoutAnchor` is the new constraint factory:
```swift
label.leadingAnchor.constraint(equalTo: view.readableContentGuide.leadingAnchor).isActive = true
```

- **UIStackView** debuts on iOS (and is enhanced on Mac via NSStackView). Vertical/horizontal axis, alignment (fill/leading/center/trailing/baseline), distribution (fill/fillEqually/fillProportionally/equalSpacing/equalCentering). Setting `isHidden = true` on an arranged subview animates it out and the others reflow.
- StackView uses a CATransformLayer (no own backing) — extremely lightweight, faster than ordinary container views.
- Two new layout guides shipped on UIView: `layoutMarginsGuide` and `readableContentGuide`. The readable guide caps line length to a comfortable reading width regardless of view size, scales with Dynamic Type, and respects platform.
- `tableView.cellLayoutMarginsFollowReadableWidth = true` makes table cell content use the readable width automatically.
- **PERFORMANCE**: prefer `NSLayoutConstraint.activate(_:)` / `deactivate(_:)`. NEVER do `view.removeConstraints(view.constraints)` — system-internal constraints are in there too. **Adding** constraints (the old way) is also strongly discouraged.
- Self-sizing table view cells: pin top and bottom of content to cell content view, set `tableView.estimatedRowHeight`, set `tableView.rowHeight = UITableView.automaticDimension`. Animate height changes with `beginUpdates()` / `endUpdates()` (NOT `reloadData`).
- Use `leading`/`trailing` (not `left`/`right`) so RTL languages flip automatically.
- `firstBaseline` / `lastBaseline` alignment is critical for lines of text adjacent to controls — top/bottom alignment looks wrong when text wraps.

## Right-to-Left UI (107, 222)

- Apps linked against iOS 9 with an RTL localization automatically reverse all UIKit controls, navigation, swipes, sliders, switches, and collection view layout.
- `UIView.semanticContentAttribute` controls per-view: `.unspecified` (default — flip), `.playback` (don't flip — playback controls feel directional), `.spatial` (don't flip — left/center/right text alignment), `.forceLeftToRight`, `.forceRightToLeft`.
- `UIImage.imageFlippedForRightToLeftLayoutDirection()` for control glyphs that should mirror.

## Storyboard References (215)

- Storyboards can now reference one another. End the era of one giant storyboard for the whole app.
- Unwind segues are now supported in IB.

## Cross-references

- Memory discipline (212) compounds with App Thinning (404, 214).
- Auto Layout cell sizing (218) is the foundation for self-sizing table cells (231).
- Adaptive presentations connect to Safari View Controller (504), which adapts the same way.

## Best Practice Summary

- Test all five multitasking states + all rotations of each.
- Use `viewWillTransition` callbacks, not interface orientation queries.
- The user controls your size — you cannot reject a transition.
- Save state when the user backgrounds you, AND restore on the size change that snaps you back to your pre-snapshot size (otherwise the home-screen snapshot crossfades to the wrong state).
