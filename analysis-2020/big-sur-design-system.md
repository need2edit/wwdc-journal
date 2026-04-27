# WWDC 2020 — macOS Big Sur Design System & Catalyst Modernization

macOS Big Sur was a complete visual overhaul — the design language that, in retrospect, set the direction for everything Apple shipped through the next several years. New translucent toolbars, full-height sidebars, large controls, SF Symbols on the Mac, custom accent colors, refreshed iconography. Many changes are automatic when you build against the new SDK; others require deliberate adoption.

## Sessions Analyzed
- 10104 — Adopt the new look of macOS (gateway)
- 10117 — Accessibility design for Mac Catalyst
- 10056 — Optimize the interface of your Mac Catalyst app
- 10143 — What's new in Mac Catalyst
- 10171 — What's new in watchOS design (companion design overhaul on watchOS 7)
- 10175 — The details of UI typography
- 10207 — SF Symbols 2

## Three Pillars of the Big Sur Look

1. **Window structure** — full-height sidebars, integrated toolbars, the new title styles
2. **Controls** — large size, subtle borders that appear on hover, inline title/subtitle
3. **Iconography** — SF Symbols on Mac for the first time, custom accent colors, refreshed asset catalog support

The design philosophy: **the framework does the heavy lifting**. Many things look right just by linking against the Big Sur SDK. Adoption goes from 0 → great → polished, in increments.

## Sidebars — Full-Height Done Right

The eye-catching change. Mail-style full-height sidebars that extend up under the toolbar.

Recipe (most apps will get this for free):
- Use `NSSplitViewController` with the split-view item configured `behavior = .sidebar`.
- Use the window mask `fullSizeContentView` so content can lay out under the title bar.
- Use the new safe-area APIs (now also exposed in Interface Builder via the "Safe Area Layout Guide" checkbox in the Size Inspector) to keep your content visible.
- The Interface Builder catalog has a preconfigured "sidebar" object that wires all this up.

Opt-out: `NSSplitViewItem.allowsFullHeightLayout = false` for sidebars that are typically collapsed or where toolbar space is at a premium.

### Sidebar Icon Tint System

The `NSOutlineViewDelegate.tintConfiguration(for:)` method returns an `NSTintConfiguration`:
- `.default` — uses the user's accent color
- `.monochrome` — colorless (Catalina-style)
- `.preferredColor(_:)` — your specific color, but switches to follow the user's accent if they customize it (Mail's teal folders use this)
- `.fixedColor(_:)` — never changes (Mail's yellow-star VIP folder)

Use this to **distinguish sections of the sidebar** or to de-emphasize secondary groups via `.monochrome`.

## Toolbars — Five New Styles

The big visual change is the **uninified material**: toolbars no longer have a visible separator behind them; they look like an extension of the window content. This is automatic.

Set `NSWindow.toolbarStyle` to control layout:
- `.unified` — the new default. Inline title at the leading edge next to the sidebar; large controls; bold icons. Use for most windows.
- `.unifiedCompact` — smaller height, regular-sized controls, optional inline title. Use when content is the focus and the toolbar isn't busy.
- `.preference` — selectable icons, centered, equal-sized — built for preference windows. **Free** if you use `NSTabViewController` with `tabStyle = .toolbar`.
- `.expanded` — title sits above the toolbar (the classic look). Use for very long titles or busy toolbars.
- `.automatic` — picks based on window structure; default for pre-Big-Sur-linked apps.

### Subtitle Below Title

`NSWindow.subtitle` adds secondary text under the inline title (Mail uses it for the unread count). In `.expanded` style it shows next to the primary title.

### Navigation Items in Toolbars

`NSToolbarItem.isNavigational = true` for back/forward-style buttons — the system pins them to the leading edge. Users can customize them in/out of the toolbar but cannot move them off the leading edge.

### NSSearchToolbarItem

A genuine improvement: in narrow windows the search field collapses to a button, expands when clicked. Migration is two lines:
1. Change item class to `NSSearchToolbarItem`.
2. Set `searchField` instead of `view`.

Backwards compatible — on older systems it falls back to a regular search field with no runtime checks needed.

### Track Split-View Sections in the Toolbar

The Mail look where toolbar zones align with split-view dividers and resize together. Implemented via `NSTrackingSeparatorToolbarItem` — give it a split view and a divider index, done. Plus a standard item identifier (`.sidebarTrackingSeparatorItemIdentifier`) auto-locates the full-height sidebar separator.

### Scroll Pockets vs. Separators

There's no toolbar separator line by default. Instead:
- `NSScrollView` content gets an automatic shadow/pocket beneath the toolbar when scrolled.
- For control: `NSSplitViewItem.titlebarSeparatorStyle` per-section, or `NSWindow.titlebarSeparatorStyle` for the whole window. The window value supersedes split-view-item values; set to `.automatic` to let items decide.

## Controls — Large Size & Custom Accent Colors

### Custom App Accent Color

Big Sur lets users pick "multicolor" mode and apps can declare their own brand accent color. Setup:
1. Asset catalog → new named color (e.g., "AccentColor"). Xcode creates this for you in new projects.
2. Project editor → set it as the accent color name.

Critical rule: **continue using named system colors in code**, not the hardcoded value. The named system colors automatically follow the accent preference; hardcoding breaks user personalization.

### Large Control Size

A new standard size, available across most styles of buttons (push, pop-up, pull-down), segmented controls, text fields, search fields. Just set `controlSize = .large`. The unified toolbar style uses this automatically. Also used in system alerts.

### Slider Redesign

Inline tick marks unify the layout of sliders with and without ticks. Auto-applied for apps built against the new SDK. Watch your label alignment: the track and thumb now sit differently in the frame. Fix: **baseline-align labels to the slider** — `NSSlider` provides a sensible baseline offset (works back-deployed to Catalina).

### Table Selection Styles

`NSTableView.style` is the new control:
- `.automatic` — picks based on configuration
- `.fullWidth` — Catalina-style edge-to-edge selection
- `.inset` — new Big Sur look with horizontal padding around cells, slightly taller default rows
- `.sourceList` — for sidebar source lists

`effectiveStyle` is read-only and resolves `.automatic`. Sidebars always use `.sourceList`. The `.inset` look is only auto-applied for new-SDK builds. The old `sourceList` highlight style is **soft-deprecated** — prefer `style = .sourceList`.

## Text Styles Come to macOS

Standard text styles (`.body`, `.title`, `.callout`, etc.) now exist on the Mac, sized around the **13pt body** standard (vs. iOS's 17pt). API:
- `NSFont.preferredFont(forTextStyle:options:)`
- `NSFont.preferredFontDescriptor(forTextStyle:options:)`

Crucially: **this is not Dynamic Type** — there's no system-wide slider. The styles give consistency, not user-controlled scaling.

## SF Symbols on the Mac (Major)

2,500+ symbols + your own. Symbols size and weight scale with text, so they pair perfectly with the new text styles.

API:
```swift
NSImage(systemSymbolName:accessibilityDescription:)
```

Display recipe:
1. Use `NSImageView` — it knows how to resolve size/weight against the typographic context, handles display scale, baseline-aligns to adjacent labels.
2. Set `symbolConfiguration` (size, weight, scale, or text-style-based) to specialize.

Pitfalls:
- **Never set an `NSImage` directly as `CALayer.contents`.** The image loses context-sensitivity and scale awareness; you get blurry or mis-aligned symbols. Always use `NSImageView`.
- For custom drawing, use `image.alignmentRect` (which spans baseline → cap height) — not the bounding rect.

Many existing `NSImageName*` constants now map directly to symbol images for new-SDK builds (e.g. `NSImageNameShareTemplate` → "square.and.arrow.up"). Layout/drawing of these images may shift; audit after rebuilding.

## Mac Catalyst — "Optimized for Mac" Mode

A new toggle in the project settings. Two options:
- **Scale Interface to Match iPad** (existing): renders at 77% to feel iPad-sized. Layouts preserved as-is.
- **Optimize Interface for Mac** (new): renders at 100%, swaps in real Mac controls (NSButton, NSDatePicker, NSColorPicker, NSPopUpButton looks, etc.), uses Mac standard spacing and metrics. Requires layout audit but yields a visually authentic Mac app.

This is **build-time, not runtime**, and applies to the whole app (no per-view choice).

### What Changes Visually When You Optimize

| Element | Scaled (77%) | Optimized (100%) |
|---|---|---|
| Body text style | 17pt scaled | 13pt true |
| System buttons | iOS look scaled | Mac NSButton look |
| Sliders/Switches | iOS appearance | Mac slider, checkboxes |
| Date pickers | UIDatePicker compact | AppKit inline picker |
| System spacing | iPad spacing | Mac standard spacing (larger) |
| Asset rendering | downscaled | 1:1 (sharper, pixel-perfect) |

### What Apps Benefit Most
- Text-heavy apps (Swift Playgrounds was optimized for Big Sur).
- Graphics-heavy apps (Swift Playgrounds saw higher frame rates and lower power on optimized).
- Apps with detailed iconography (MapKit's place-mark icons render dramatically sharper).
- Apps with many controls (custom popovers feel more native — checkboxes vs. switches).

### Limitations to Audit
- **Tinted system buttons** lose their tint in Mac mode (Mac users don't expect tinted buttons). Use the user's accent color via system colors instead.
- **Gesture recognizers on UIButton stop firing** when the button has adopted the native Mac appearance. Move long-press-on-button patterns to `UIButton.menu` (a real menu) or to a menu-bar item.
- **Custom UIControl event tracking overrides** (`beginTracking(_:with:)`) won't fire on Mac-style controls.
- Custom (non-system) buttons keep the iPad event model — escape hatch for must-keep-this-gesture cases.

### Adopting in Code

Trait variations and idiom checks are how you customize:
```swift
if traitCollection.userInterfaceIdiom == .mac { ... }
```
Interface Builder gained an idiom chooser in the canvas device bar; "Installed" property variations now support `.mac` to toggle views per-idiom.

Asset catalog: enable "Mac" in the Devices section to provide native Mac assets. Fallback chain: `Mac` → `Mac Scaled` → `iPad` → `Universal`.

### Universal Purchase

New this year: every Catalyst app is automatically a **Universal Purchase**. iOS users don't pay twice for the Mac version. New Catalyst apps are opted in by default; uncheck "Use iOS Bundle Identifier" to opt out. Existing Catalyst apps from Catalina need explicit opt-in via the developer portal.

### Mac Catalyst Frameworks Expansion

Many iOS frameworks that weren't previously available are now usable in Catalyst. ARKit can now be **linked** in a Catalyst target — at runtime it behaves like an iOS device that doesn't support AR. No more conditional code-stripping for missing frameworks.

### Application Lifecycle Updates

Catalyst apps now follow iPad-style scene lifecycle more closely. New scenarios that move scenes to background:
- Window minimized
- Space containing window scrolls out of view
- App is hidden

Foreground = at least one window foreground OR app owns the menu bar. Importantly, gaining/losing menu bar within an active space does NOT background the app, and a window becoming occluded does NOT background it.

App Nap applies to Catalyst apps but suspension does not — Catalyst apps stay running in the background.

## What's New in watchOS Design (Companion Overhaul)

watchOS 7 went the other direction: a complete audit of **gesture-based contextual menus** removed them and surfaced actions inline. The principles map to design philosophy on Mac and iPad:

1. **Discoverable & predictable** interactions — no hidden long-press menus.
2. **Relevant actions visible**.
3. **Eliminate gesture menus without losing functionality.**

Key new patterns:
- **Sort/filter buttons** at the top of long lists. Implementation in SwiftUI: a `Picker` nested in a `List`.
- **Swipe actions** in lists — `onDelete` modifier in SwiftUI.
- **More button** (ellipsis circle) for secondary actions in non-scrolling glanceable views (Maps).
- **Action buttons at the bottom of detail views** — most discoverable for delete/share. Red text for destructive actions, with confirmation if not retrievable.
- **Toolbar button** (new SwiftUI API) — tucked beneath the navigation bar in scrolling views. Use for occasionally-needed actions like "Compose new message". Only use in scrolling views; scrolling makes it discoverable.
- **Hierarchical navigation** — apps remember the last destination across launches (Mail's "All Inboxes" example).

## Cross-References
- [apple-silicon-mac-transition.md](apple-silicon-mac-transition.md) — Big Sur is the OS that ships with Apple Silicon Macs; the design system was rolled out together.
- [swiftui-2-foundation.md](swiftui-2-foundation.md) — SwiftUI 2.0 implements the new toolbar, label, and color systems.
- [catalyst-mac-modernization.md](catalyst-mac-modernization.md) — focused on Catalyst-specific lifecycle and framework changes.
- [accessibility.md](accessibility.md) — accessibility design for Catalyst is in 10117.

## Adoption Checklist
- [ ] Build against the Big Sur SDK and test the automatic visual changes.
- [ ] Adopt `NSSplitViewController` with `.sidebar` behavior + `fullSizeContentView` for full-height sidebars.
- [ ] Pick the right `toolbarStyle` for each window.
- [ ] Define an accent color in the asset catalog.
- [ ] Use `NSSearchToolbarItem` for any search fields in toolbars.
- [ ] Adopt SF Symbols where you used to use custom 1× PNG icons; always render via `NSImageView`.
- [ ] Replace bespoke separator inset code with `separatorLayoutGuide` constraints.
- [ ] If Catalyst: choose Scale vs. Optimize per app and audit accordingly.
- [ ] Audit `mach_absolute_time` and other portability issues (see Apple Silicon analysis).
