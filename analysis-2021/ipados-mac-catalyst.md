# iPadOS 15 & Mac Catalyst (WWDC 2021)

The "iPad as a real laptop" push: keyboard navigation, multitasking menus, Quick Note, center-window scenes, and the maturation of Mac Catalyst into a first-class macOS app environment.

## Sessions covered
- WWDC21-10057 — Take your iPad apps to the next level
- WWDC21-10059 — What's new in UIKit
- WWDC21-10260 — Focus on iPad keyboard navigation
- WWDC21-10264 — Adopt Quick Note
- WWDC21-10052 — What's new in Mac Catalyst
- WWDC21-10053 — Qualities of a great Mac Catalyst app
- WWDC21-10054 — What's new in AppKit
- WWDC21-10056 — Qualities of great iPad and iPhone apps on Macs with M1
- WWDC21-10262 — Coordinate media playback in Safari with Group Activities (note: web-side)
- WWDC21-10282 — Build a research and care app, part 3 (mac mention)

## Best practices

- **Adopt `NSUserActivity` end-to-end.** It now powers Handoff, Spotlight, Reminders, Quick Note, and state restoration. One mechanism, six user-visible features (WWDC21-10264).
- **Quick Note identifiers must be unique, global, and stable.** Don't use file paths (device-local), session IDs (transient), or display titles (mutable). Use a stable UUID; fall back to webpageURL only if those constraints can be met (WWDC21-10264).
- **Use `UIWindowSceneActivationAction`** to opt into the new "Open in New Window" context-menu pattern. Returns a configuration with an `NSUserActivity` (WWDC21-10059).
- **Adopt `UIMenuBuilder`** for keyboard shortcuts — auto-shows in the redesigned shortcut menu, and gives parity with Mac Catalyst (WWDC21-10059).
- **Audit `translucent=false`** on UIToolbar/UITabBar — iOS 15's new scroll-edge appearance regresses if you've forced opacity. Use `scrollEdgeAppearance` instead (WWDC21-10059).

## Hidden gems

- **Quick Note suggestions** appear when you re-visit a URL or app screen that's referenced in any Quick Note — so users can jump back into the same note. NSUserActivity adoption is the hook (WWDC21-10264).
- **Center scene** multitasking placement: a new `UIWindowScene.Geometry` style that floats in the center of the iPad screen, can be tucked to a sidebar with the new window-shelf gesture (WWDC21-10059, WWDC21-10057).
- **`UIToolTipInteraction`** for Mac Catalyst — finally a tooltips API for hover-text on macOS (WWDC21-10052).
- **Pop-up buttons in Catalyst**: `changesSelectionAsPrimaryAction = true` + `showsMenuAsPrimaryAction = true` + non-nil `menu` = a real macOS pop-up button. Without all three, you get a different style (WWDC21-10052).
- **`UIScene.subtitle`** — Mac windows get a subtitle below the title, ideal for "Untitled - Modified" or "Project A · 14 items" context (WWDC21-10052).
- **Print support in Catalyst is now a one-key Info.plist opt-in**: `UIApplicationSupportsPrintCommand=true` adds Print/Export-as-PDF menu items. Still implement `printContent` on a responder — UIResponder chain finds the right target (WWDC21-10052).
- **`UIBehavioralStyle`** — opt out of "Optimize Interface for Mac" 77% scaling on a per-control basis (use `.pad` for buttons that should stretch to fill, vs `.mac` for native chrome) (WWDC21-10052).
- **iPad pointer band selection** — drag the pointer over a multi-select-enabled UICollectionView and the pointer lassos items. Free for any collection view that has selection enabled (WWDC21-10059).

## Performance

- iPadOS 15 cell prefetching gives ~2x more lead-time for cell preparation, dramatically smoothing scrolling. Free if you're on iOS 15 SDK; opt-out via `prefetchSource = .none` if your prefetch logic clashes (WWDC21-10059, WWDC21-10252).

## Migration guidance

- If you're still on the UIApplicationDelegate-based lifecycle (no UIScene), now is the time to migrate. All new UIKit features assume UIScene — multiple windows, Catalyst, state restoration improvements all require it (WWDC21-10059, WWDC21-10057).

## Cross-references

- Stage Manager (iPadOS 16, 2022) builds on the UIScene infrastructure laid in 2021.
- Universal Control (macOS Monterey, 2021 keynote) is a system feature — apps don't adopt it; existing pointer/keyboard input handling just works.
