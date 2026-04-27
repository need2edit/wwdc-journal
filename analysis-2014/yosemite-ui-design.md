# macOS Yosemite UI & Vibrancy — WWDC 2014 Analysis

**Sessions covered:** 209 (Adapting Your App to the New UI of OS X Yosemite), 220 (Adopting Advanced Features of the New UI of OS X Yosemite), 227 (Creating Modern Cocoa Apps), 212 (Storyboards and Controllers on OS X)

## Headline

OS X 10.10 Yosemite is the **biggest visual overhaul of macOS since OS X 10.0**. Flat design, translucent toolbars and sidebars, the new system font (Helvetica Neue replacing Lucida Grande, then San Francisco in 10.11), `NSVisualEffectView` for blurring background content, and a re-imagined visual language called **Vibrancy**. AppKit gains storyboards, gesture recognizers, and split view controllers — all conventions that started on iOS now coming home to the Mac.

## The Mental Model — Vibrancy (session 220)

- **Vibrancy** is an abstract effect Apple coined: text and icons against a translucent surface get a special blend mode (color burn / linear burn variants) that makes them appear to "absorb" color from what's behind, looking more vibrant than a flat color overlay (220).
- Implemented by **`NSVisualEffectView`** — adds blur + vibrancy. Two blending modes:
  - **`behindWindow`** — blurs whatever's BEHIND the window (desktop, other apps). Implemented by Core Graphics + Window Server. **Out-of-process drawing** — moving the window doesn't redraw your app's content.
  - **`withinWindow`** — blurs whatever's BEHIND the visual effect view inside the same window. Implemented by Core Animation; requires layer-backed views (220).
- HIDDEN GEM: `NSVisualEffectView.appearance = NSAppearance(named: NSAppearance.Name.vibrantLight)` (or `vibrantDark`) — automatically picks the right material AND propagates the appearance to children. Vibrant child controls (text labels using `NSColor.labelColor`) automatically render vibrantly (220).

## Title Bar / Toolbar Innovations (session 220)

- **Toolbars and title bars now blur scroll view content beneath them automatically** if the scroll view is adjacent. No code required. Preview, Safari, Mail all do this for free (220).
- **`NSWindow.styleMask` gains `.fullSizeContentView`** — title bar overlays the content view rather than reducing it. The classic Reminders-and-Notes look where the sidebar texture goes all the way to the top edge (220).
- **`NSWindow.titlebarAppearsTransparent = true`** — the title bar's background goes transparent; you can paint anything underneath (220).
- **`NSWindow.titleVisibility = .hidden`** — Safari's "no title, just toolbar" look. Window widgets and toolbar share one row (220).
- HIDDEN GEM: `NSScrollView.contentInsets` adds margins so the scroller isn't obscured by an overlapping title bar. `automaticallyAdjustsContentInsets = true` — auto-computes based on `window.contentLayoutRect` (220).
- HIDDEN GEM: `NSWindow.contentLayoutGuide` is a layout guide for the unobscured area. Use Auto Layout: `myView.topAnchor.constraint(equalTo: window.contentLayoutGuide.topAnchor)` to position controls beneath an overlapping title bar (220).

## NSColor System Colors Now Adaptive (session 220)

- **System colors return different effective values per appearance**. `NSColor.controlTextColor` is dark on Aqua/VibrantLight, light on VibrantDark — automatically. Same color object, different render (220).
- New colors: **`NSColor.labelColor`** and **`NSColor.secondaryLabelColor`** — semantic text colors that participate in vibrancy when used inside a vibrant container.
- HIDDEN GEM: STORE NAMED system colors, NOT their resolved RGB values. Resolving to RGB strips the dynamic-on-appearance-change behavior. `let myColor = NSColor.labelColor` is correct; `let myColor = NSColor.labelColor.usingColorSpace(.sRGB)!.cgColor` loses adaptivity forever (220).
- BEST PRACTICE: when overriding `NSView.draw(_:)` in a custom subclass, call `NSColor.labelColor.set()` and let the system resolve the right color for the current appearance.

## allowsVibrancy on Custom Views (session 220)

- Override `NSView.allowsVibrancy` to return `true` if your custom view should render vibrantly when inside an `NSVisualEffectView` ancestor with a vibrant appearance.
- The recipe for vibrant rendering: **(1) appearance allows vibrancy**, **(2) view's `allowsVibrancy` returns true**, **(3) view is inside an NSVisualEffectView**. ALL THREE must be true (220).
- HIDDEN GEM: built-in NSImageView returns `allowsVibrancy = self.image.isTemplate` — template images (black-and-white, marked `isTemplate = true`) automatically render vibrantly when in a vibrant container; full-color images don't (220).
- WARNING: once `allowsVibrancy = true`, **all subviews render vibrantly too**. Vibrancy is "infectious" downward. To opt out specific subviews, set their `appearance` to `.aqua` explicitly (220).

## Behind-Window Blending Caveats (session 220)

- WARNING: behind-window blending uses the Window Server to **knock out** the window contents behind the visual effect view region. If you have an opaque view (e.g., a colored background) overlapping the visual effect region, the opaque view's color is REPLACED by the blur — not blended on top. Be deliberate about overlapping (220).
- WARNING: the **once-vibrant-always-vibrant** pitfall — if you have a non-vibrant blue background and overlap it with a vibrant text label, the entire region of the text label (including the blue underneath) becomes vibrant. Not always what you want (220).

## Performance (session 220)

- Vibrancy is **not free**. Both blending modes consume GPU. Behind-window blending also consumes Window Server CPU and energy.
- BEST PRACTICE: a SINGLE large `NSVisualEffectView` is cheaper than many small ones — fewer regions for the system to track. Unless flexibility (different appearances per region) requires multiple, consolidate (220).
- WARNING: frequently-updated content (animations, blinking text cursors, video) triggers a **blur recompute** on every update. Avoid putting fast-changing content INSIDE or near a vibrant region (220).
- WARNING: layer-backed views flush the **entire layer** when any sub-region is dirty. A blinking cursor in a layer-backed text view triggers full-layer flush. Refactor to put fast-changing content in a small leaf view (220).
- HIDDEN GEM: System Preferences → Accessibility → Display → "Reduce Transparency" disables ALL vibrancy. **Use this as a diagnostic tool** — if your app feels slow normally and snappy with Reduce Transparency on, you have too much vibrancy (220).

## Storyboards on OS X (sessions 212, 411)

- **Storyboards finally come to AppKit** in Yosemite. Same paradigm as iOS — scenes connected by segues, all in one document.
- **`NSSplitViewController`** and **`NSTabViewController`** are new container view controllers. Designed for storyboard composition (212).
- HIDDEN GEM: presenting a popover or a sheet on Mac is now a **segue** in the storyboard, instead of imperative code. Drag a connection from a button to a view controller, set segue type to "Show as Popover" or "Sheet". The presentation lifecycle is managed for you (411).
- WARNING: AppKit storyboards require Yosemite or later — no backward deployment to older Macs. Universal apps targeting both will need to keep XIBs around (212).

## NSImage Improvements (session 220)

- **`NSImage.capInsets`** — finally arrives on the Mac (UIImage had it for years). Specify NSEdgeInsets, get correct nine-slice stretching (220).
- **`NSImage.resizingMode`** — `.stretch` (default) or `.tile`. Tile replicates the interior region instead of stretching it. Useful for textured backgrounds (220).
- HIDDEN GEM: configure both nine-slice + tiling visually in the **Asset Catalog** in Xcode 6 (220).

## NSSegmentedControl Disjoint Style (session 220)

- New `.separated` segment style — Safari's back/forward buttons. Looks like two buttons with a gap; still a single `NSSegmentedControl` instance (220).
- BEST PRACTICE: don't use two `NSButton`s when you mean a segmented control. The `.separated` style gives you the right behavior with the right semantics.

## NSAppearance Hierarchy (session 220)

- Yosemite introduces **`NSAppearance`** that propagates through the view hierarchy.
- Built-in names: `aqua`, `vibrantLight`, `vibrantDark`. (`lightContent` was deprecated — popovers now use `vibrantLight` or `vibrantDark` (220).
- Set on a window or container view; children inherit. Override per-view to opt out.

## Best Practices

- **Adopt vibrancy** for sidebars, popovers, sheets, and HUDs. Skip it for content areas that need true color fidelity (a photo grid).
- **Use system colors** in custom drawing — they adapt across appearances.
- **Use a single large NSVisualEffectView** rather than many small ones for performance.
- **Avoid mixing vibrant + non-vibrant content in the same region** — once-vibrant-always-vibrant gotcha.
- **Test with Reduce Transparency on** — verify your app still looks good for accessibility users.
- **Use template images for toolbar icons** — they get vibrancy for free.

## Hidden Gems

- HIDDEN GEM: `NSVisualEffectView.maskImage` clips the blur region — pass an image with rounded corners to get a rounded vibrant blob without drawing your own mask (220).
- HIDDEN GEM: `NSTableView.selectionHighlightStyle = .sourceList` automatically wraps the table view in an `NSVisualEffectView` and sets the appearance to `vibrantLight`. Apps that already used the source list highlight style get the new look automatically when relinked against Yosemite (220).
- HIDDEN GEM: `NSPopover` automatically picks vibrancy in Yosemite. Existing apps benefit without code changes (220).
- HIDDEN GEM: `NSWindow.opaque` should remain at its default `true` when using visual effect views. Setting it to `false` strips info the Window Server uses to occlude windows behind yours, hurting performance (220).

## Cross-references

- **iOS Adaptive UI (216)** — the trait collection model on iOS is structurally similar to NSAppearance on Mac. Same idea: query the environment, adapt the rendering.
- **Continuity (219)** — Yosemite's visual refresh ships alongside Continuity. Many design choices (translucent dock, vibrant Notification Center) reinforce the "your devices are one continuous experience" message.
- **Building Modern Frameworks (416)** + **Storyboards on OS X (212)** + **Sharing code between iOS and OS X (233)** — together set up Mac apps to share more code with iOS counterparts than ever before.

## Migration Guidance

- **Existing AppKit apps relinked against the Yosemite SDK get many vibrancy effects automatically** (source list table views, popovers, the new system colors). Test thoroughly; the visual change is significant.
- **Apps with custom title bar drawing**: re-evaluate. The new `.fullSizeContentView` + `titlebarAppearsTransparent` model is much cleaner than custom title bar overlays.
- **Apps that drew their own translucent backgrounds**: switch to `NSVisualEffectView` — better performance (out-of-process for behind-window) and consistent look.
- **Apps using `NSAppearanceNameLightContent`**: migrate to `vibrantLight` or `vibrantDark`. The old constant is deprecated (220).
- **Custom drawing code**: audit for hard-coded RGB values; replace with `NSColor.labelColor` etc. Without this, your app will look out-of-place in vibrant containers and won't adapt to future appearances (Dark Mode arrives in macOS Mojave, 4 years later).
