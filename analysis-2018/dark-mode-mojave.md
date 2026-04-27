# Dark Mode & macOS Mojave — WWDC 2018 Analysis

**Sessions covered:** 210 (Introducing Dark Mode), 218 (Advanced Dark Mode), 209 (What's New in Cocoa for macOS), 102 (Platforms State of the Union §macOS), 803 (Designing Fluid Interfaces), 802 (Intentional Design)

## Headline

macOS Mojave brought the most-requested macOS feature in years — **Dark Mode** — with a deep redesign that's far more than an inverted palette. New **desktop tinting** subtly bleeds wallpaper color into window backgrounds for harmony, **eight accent colors** replace the old blue/graphite duality, and a new system of **dynamic system colors** + **semantic NSVisualEffectView materials** + asset-catalog appearance variants makes adoption straightforward — many apps need only relink.

## Three Design Principles for Dark Mode (210)

1. **Dark interfaces are cool — but not for every app.** Only media-creation and content-focused apps (Final Cut, Photos, Logic) should be _always_ dark. Most apps should follow the system appearance.
2. **Dark is not just inverted.** Apple's group boxes are recessed in light mode, _self-illuminated_ in dark mode — the visual cue (these things are related) is the same, but the technique is opposite. Window shadows stay dark in both modes (an inverted white window shadow would flatten the entire UI).
3. **Dark mode is content-focused.** Three patterns: fully-dark content area (Finder), content-as-authored (Pages, WYSIWYG editors), and user-toggleable (Mail). Choose based on whether your content is colorful (then go dark) or user-authored (then preserve fidelity).

## Desktop Tinting (210)

- The window background isn't pure gray — it samples the average color of the desktop _behind_ the window and blends it in.
- A blue desktop gives a slightly blue window background; orange gives orange. Window appearance is dynamic — it updates as you drag the window across the screen.
- This is **not translucency**. It's an opaque color computed from a desktop sample.
- "Graphite" accent color disables desktop tinting for color-sensitive workflows (medical imaging, color grading).

## The Three Dark-Mode-Sensitive Background Materials (210, 218)

Use these on `NSWindow.backgroundColor`, `NSScrollView.backgroundColor`, `NSTableView.backgroundColor`, `NSCollectionView.backgroundColor`, or `NSBox.fillColor`:

| Material | Use case |
|---|---|
| `controlBackgroundColor` | Content area for controls (table backgrounds, list backgrounds) |
| `windowBackgroundColor` | Generic window backgrounds (settings panes, accessory windows) |
| `underPageBackgroundColor` | Behind document pages (Pages, Preview, Keynote — where the "page" is on a darker surface) |
| `textBackgroundColor` | Behind editable text — switches white→black with appearance |

All four pick up desktop tint automatically. **HIDDEN GEM**: their RGB values _don't_ include the tint — the tint is a private rendering pass on top, applied asynchronously. Don't try to recreate them by reading RGBs.

## Color Palettes That Just Work (210)

- `NSColor.labelColor`, `.secondaryLabelColor`, `.tertiaryLabelColor`, `.quaternaryLabelColor` — properly anti-aliased contrast in any appearance, including high-contrast mode.
- The 12 system colors (`.systemRed`, `.systemBlue`, `.systemGreen`, `.systemYellow`, `.systemOrange`, `.systemPurple`, `.systemPink`, `.systemTeal`, `.systemIndigo`, `.systemGray` and grays 1–6) are appearance-aware variants of the static colors. Use these instead of `redColor`/`blueColor` for informational content.
- `controlAccentColor` — the user's selected accent. Use this on custom buttons that should match system controls.
- `systemBlue` — the iOS-style "always blue" for branding or non-customizable content.
- `linkColor` — for hyperlinks specifically.

**BEST PRACTICE**: do _not_ use `NSColor.currentControlTint` (Aqua/Graphite enum) anymore. With 8 accent colors it's not enough information. Use `controlAccentColor`.

## NSColor Effects API (210, 209)

- `NSColor.withSystemEffect(_:)` — `.pressed`, `.disabled`, `.deepPressed`, `.rollover`. Apply a semantic interaction to any color and get the right rendering for the current appearance + accent + contrast settings. **HIDDEN GEM**: replaces the old "darken by 30% on press" formulas which break in dark mode (where pressed should _brighten_, not darken).

## NSVisualEffectView Semantic Materials (210, 218)

The big change: don't pick a visual style ("light", "medium light", "dark"). Pick a _semantic role_ and let the system choose the look:

| Material | Where to use |
|---|---|
| `.titlebar` | Window title bars |
| `.menu` | Menu-style popovers |
| `.popover` | Generic popovers |
| `.sidebar` | Source lists / sidebars (auto on `NSSplitViewItem` source-list type) |
| `.headerView` | Headers above content |
| `.sheet` | Modal sheets |
| `.windowBackground` | Generic translucent window |
| `.hudWindow` | HUD-style auxiliary windows |
| `.fullScreenUI` | Full-screen overlays |
| `.toolTip` | Tool tips |
| `.contentBackground` | Content area background |
| `.underWindowBackground` | Below-window translucency for dock-like UIs |

**URGENT**: stop using `.light`, `.dark`, `.mediumLight`, `.ultraDark` — they don't adapt. They still compile but Apple wants you on semantic materials.

## Vibrancy: Use Grayscale Foregrounds (210)

- Vibrancy is the blur material + a foreground content blend. Get it right and translucent sidebars look gorgeous; get it wrong and text disappears.
- **CRITICAL**: vibrant foregrounds must be _opaque grayscale_, not opacity-on-white. The blend mode treats opaque black as "fully transparent" (knockout) and opaque white as "fully opaque." A 50% gray gives 50% blend.
- For colored artwork (Finder tags, app icons), opt out of vibrancy — colored content + vibrancy = washed-out.

## Asset Catalogs Get Appearance Variants (210)

- New "Appearances" section in Xcode's color/image editor: define light, dark, light high-contrast, dark high-contrast variants per asset.
- Image variants give you completely different artwork (a daytime view of North America in light, a nighttime view in dark).
- Color variants let you semantic-name a color (`.headerColor`) and define the variants without code changes.

## Template Images Done Right (210, 209)

- Template images carry only transparency; their color is replaced at render time. Use them for monochromatic glyphs.
- New `NSImageView.contentTintColor` and `NSButton.contentTintColor` (Mojave) let you tint a template image with any color, including dynamic system colors. Replaces the older approach of hardcoding 12 different colored variants.
- The button's pressed/disabled/highlighted appearance is automatic from the tint.

## NSAppearance Mental Model (210, 218)

- An `NSAppearance` is a bundle of (colors, materials, images, control artwork). When the system runs in dark mode, the dark appearance is applied to your app, and `labelColor` resolves to white-ish at draw time.
- You can override on any window or view with `view.appearance = NSAppearance(named: .darkAqua)` or `.aqua`.
- Use cases for explicit override: a WYSIWYG document area should remain `.aqua` so spell-check bubbles and selection colors look right against the user's bright document.
- **GOTCHA**: a leftover `vibrantLight` override on a table view from your iOS 11 codebase will look fine in light mode but break dark mode entirely. Search Interface Builder for hardcoded appearance overrides.

## Layer Backing Becomes Default (209)

- macOS Mojave: AppKit no longer uses the legacy window backing store when you build against the 10.14 SDK. All view content is now Core Animation-backed.
- No need to set `wantsLayer = true` on every view. AppKit is smarter — it'll merge multiple views into a single layer when possible to save GPU memory.
- **DEPRECATION**: `lockFocus`/`unlockFocus`, direct access to `window.graphicsContext`. Subclass `NSView` and override `draw(_:)` instead. Apple has not seen any Swift code use these — keep it that way.
- `NSOpenGLView` continues to work but **OpenGL is deprecated** as of Mojave. Move to `MTKView`.

## Font Antialiasing Change (209)

- Mojave drops the color-fringing subpixel antialiasing that 10.13 used.
- Text now uses grayscale antialiasing. Looks better on a wider variety of panels and at non-1x scaling.
- If you've been hard-coding subpixel rendering in custom text drawing, remove it.

## Other Cocoa Goodies (209)

- **`NSGridView` editor in Interface Builder** — finally. Embed views, drag rows/columns, configure padding visually. Backwards-deployable to 10.13.4 (or 10.12 without merged cells).
- **`NSToolbar.centeredItemIdentifier`** — pin one toolbar item to the center, regardless of other items. No more "two flexible spaces" hack.
- **`NSTextView.fieldEditor()`**, `.scrollableTextView()`, `.scrollableDocumentContentTextView()`, `.scrollablePlainDocumentContentTextView()` — factory methods that configure the textview correctly for common roles. The plain/rich variants behave differently in dark mode (rich keeps white background, plain inverts).
- **Continuity Camera** — `validRequestor(forSendType:returnType:)` lets your responder handle image data inserted from a nearby iPhone.
- **Custom Quick Actions** — Automator workflows, Action Bundles, and app extensions show up as Finder Quick Actions, in the touch bar, and in the Services menu. Drag a workflow into Touch Bar customization and you have a one-button shortcut.

## Marzipan Sneak Peek (102)

- Apple shipped four UIKit-on-Mac apps in Mojave: News, Stocks, Voice Memos, Home — all built from the iOS source.
- Public release of the framework is planned for **2019** (delivered as Catalyst). 2018 is preview-only via these four apps.
- The technical foundation: a UIKit runtime on macOS sharing the same lower-level layers as AppKit. The substrate is being unified across both.
- **HIDDEN GEM** for 2018 prep: AppKit and UIKit are getting more API-aligned (Swiftification of constants, nesting of types — see 209 and 202) precisely because Catalyst will need bridging code. If you're writing UIKit code in 2018 with the iOS 12 SDK, your code is already closer to Mac-portable than 2017 code.

## Cross-references

- Asset catalog colors back-deployable to 10.13: see 210.
- iOS dark mode comes one year later in WWDC 2019; the design principles here translate directly.
- Custom drawing tips: 218 goes deeper than 210 on tricky cases (drawing into vibrant materials, debugging appearance overrides via View Debugger).
