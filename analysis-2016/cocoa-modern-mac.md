# Cocoa Modernization & macOS Sierra — WWDC 2016 Analysis

**Sessions covered:** 203 (What's New in Cocoa), 205 (What's New in Cocoa Touch), 239 (Crafting Modern Cocoa Apps), 213 (Improving Existing Apps with Modern Best Practices), 415 (Going Server-side with Swift Open Source), 414 (Using and Extending the Xcode Source Editor)

## Headline

macOS gets renamed from OS X to **macOS Sierra**. Cocoa apps gain modern conventions: **NSGridView**, native tab support in any document-based app, persistent unique state restoration, keyboard-driven navigation, App Transport Security, and a re-energized push to drop legacy patterns (deprecated APIs, OS X 10.7-style assumptions).

## Adopting modern best practices (session 213, the universal advice)

### Set deployment targets sensibly

- Old guidance: support back to iOS 7. **New 2016 guidance:** support iOS 8.4 + 9.x → covers 95%+ of devices.
- Default formula: **target current shipping version, set deployment to one OS version back.** When iOS 10 GMs in fall 2016, set deployment to 9.3.
- Don't pick 8.2 over 8.4 — the 8.4 release contains fixes both you and your users benefit from at the framework level.

### Resolve deprecation warnings

Deprecated APIs are deprecated for a reason — better error handling, better performance, more flexibility. The replacement is documented inline. **There's no excuse to ship apps using deprecated APIs.**

### Treat warnings as errors (NEW for Swift in Xcode 8)

Previously a Cocoa-only feature; now Swift supports `-Werror` style enforcement. Forces team discipline.

### Accessibility is part of your UI, not optional

You'd never ship an app without art assets — don't ship without accessibility. Use Interface Builder's accessibility inspector or set `accessibilityLabel` etc. programmatically.

### Localization

Stop manually building locale-aware formatting. Use Foundation's:
- `Measurement` + `MeasurementFormatter` (NEW value type for units) — converts metric ↔ imperial automatically.
- `DateFormatter`, `NumberFormatter`, `LengthFormatter`, `MassFormatter`, `EnergyFormatter`, `PersonNameComponentsFormatter`, `RelativeDateTimeFormatter`.

### Adopt 3D Touch (Peek/Pop/Quick Actions)

Users expect every app to support 3D Touch in iOS 10. Quick Actions are Info.plist + a delegate method. Peek/Pop is one delegate protocol. No excuse not to.

### Run the migrator NOW against the developer preview

If it doesn't migrate cleanly, file a Radar (with a sample). Apple wants to ship a working migrator at GM time. Pre-WWDC bug reports have the highest impact on the GM build.

### Bug reports — actually file them

`bugreport.apple.com`. Get a number. Then post the number in dev forums alongside your description. Forum discussion without a Radar number is hard for Apple engineers to act on.

Dupes are NOT votes — but Apple does need them. The 5th dup may carry the reproduction details that the first 4 lacked. **A bug report is a host link. Don't worry about duping.**

## NSGridView (macOS — finally, a grid layout primitive)

Before NSGridView, building a Settings-style grid in AppKit required either Auto Layout heroics or NSStackViews-of-NSStackViews. Now:

```swift
let grid = NSGridView(views: [
    [labelOptionA, controlOptionA],
    [labelOptionB, controlOptionB],
    [labelOptionC, NSGridCell.emptyContentView]
])
grid.column(at: 0).xPlacement = .trailing       // right-justify all labels
grid.rowAlignment = .firstBaseline               // align controls by baseline
grid.cell(for: controlOptionB)?.row?.topPadding = 8
grid.row(at: 2).mergeCells(in: NSRange(0..<2))   // merge cells
```

- Rows/columns auto-size to content unless you specify.
- Per-row, per-column, per-cell placement (`.leading`, `.trailing`, `.center`, `.fill`, `.none`).
- Spacing applies between all rows/cols; padding between specific rows/cols.
- Hidden columns/rows collapse cleanly when hardware doesn't support a feature.
- Cells can be merged (spreadsheet-style) and content-views custom-positioned within merged cells via `customPlacementConstraints`.

**BEST PRACTICE:** Place all your views into the grid first, then iterate on placement and padding. Get the structure right before tweaking pixels.

**HIDDEN GEM:** Set a cell's `xPlacement = .none` to opt out of grid-managed positioning for that cell, then add your own constraints to that cell's `customPlacementConstraints` array. The grid manages activation/deactivation as the cell appears/disappears.

## Cocoa Tab Support (macOS Sierra)

Any document-based or window-based app gets system-provided tab UI for free in macOS Sierra:
- Tab bar at the top.
- "Window > Merge All Windows" automatically combines into one tabbed window.
- "Show Tab Bar" / "Show All Tabs" / "New Tab" menu items.
- Per-window override via `NSWindow.tabbingMode = .preferred` / `.disallowed` / `.automatic` and `tabbingIdentifier`.

**BEST PRACTICE:** Set a `tabbingIdentifier` per window class so tabs only merge with windows of the same type.

## Persistent state restoration

`NSWindow.identifier` and `NSDocument.encodeRestorableState(with:)` give you durable state across launches. Combined with `NSUserActivity` for Handoff, you can restore the user to exactly what they were doing across devices.

## Keyboard-driven navigation

macOS Sierra adds first-class keyboard navigation:
- Tab/Shift+Tab between control groups.
- `NSWindow.initialFirstResponder` and `keyView` chain.
- `nextKeyView`/`previousKeyView` per control.
- Programmatic `becomeFirstResponder()` for explicit focus.

For tvOS-style focus engine on macOS, see Sierra's NSFocusEngine.

## Asset catalogs (and the bundle migration carrot)

Sessions 213 reiterates: drop free-floating image files, use asset catalogs.

- Multiple catalogs per project allowed (front/back of cards, logo variations, etc.).
- Migrate via "Edit > Convert to Asset Catalog" flow.
- `pathForResource()` is broken — files no longer exist after compilation. Use `UIImage(named:)` / `NSImage(named:)`.
- `imageNamed:` caches images by name (returns same instance for repeated requests). Important for table-cell perf vs. `contentsOfFile:` which loads fresh each call.
- Vector PDF/SVG assets are scaled/rasterized at build time per device variant.

## App Transport Security at the App Store (URGENT)

Starting late 2016, App Store submission **requires justification for ATS exceptions**.

- **Most exceptions need a written reason.** "Talking to a partner server I can't update" is acceptable. "I haven't gotten around to TLS yet" is not.
- **Forward Secrecy exceptions are auto-granted** — Apple knows the ecosystem isn't there yet.
- **New exceptions** make adoption easier:
  - `NSAllowsArbitraryLoadsInWebContent` — `WKWebView` arbitrary loads exempted while everything else gets ATS.
  - `NSAllowsArbitraryLoadsForMedia` — streaming media (already encrypted in transit) loaded via AVFoundation can skip ATS.

## Other modernization items

- **Stop using `UILocalNotification`** → use `UserNotifications` framework.
- **Stop using `AVCaptureStillImageOutput`** → use `AVCapturePhotoOutput`.
- **Stop using `dispatch_*` C function calls** → use Swift `DispatchQueue` API.
- **Stop using `NSDateComponents` + mutate** → use `DateComponents(year:month:day:…)` initializer.
- **Stop using `NSURLConnection`** → use `URLSession`.
- **Stop using `setNeedsStatusBarAppearanceUpdate`** without overriding `preferredStatusBarStyle` — undefined.
- **Stop using `UIScreen.scale`** when you mean `UITraitCollection.displayScale`.

## Best practices summary

- Use NSGridView for any 2D-aligned macOS UI (Settings, Inspector, anywhere with rows-and-columns).
- Set `tabbingIdentifier` per window class for sensible tab merging.
- Drop iOS 7/8.0 support; target 8.4 minimum.
- Treat warnings as errors in Swift now that Xcode 8 supports it.
- Run the new migrator early; file Radars on what doesn't migrate.
- Justify ATS exceptions in your App Store submission text.
- Replace deprecated APIs methodically — check the Issue Navigator weekly.

## Hidden gems summary

- NSGridView with `xPlacement = .none` lets cells use custom placement constraints managed by the grid.
- macOS Sierra tabs are free for any window-based app — opt in with `tabbingIdentifier`.
- `imageNamed:` caches and returns shared instances — much faster than `contentsOfFile:` for table cells.
- `NSAllowsArbitraryLoadsInWebContent` exempts WKWebView while keeping ATS for the rest of your app.
- The migrator can find APIs your code uses that have moved to value types — re-do its output for the most idiomatic Swift 3.

## Cross-references

- Swift 3 migration → analysis-2016/swift-3-migration.md
- Foundation value types → analysis-2016/swift-3-migration.md
- Apple File System → analysis-2016/apfs-storage.md
