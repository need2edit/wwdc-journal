# Dark Mode, Design & SF Symbols — WWDC 2019 Analysis

**Sessions covered:** 214 (Implementing Dark Mode on iOS), 244 (Visual Design and Accessibility), 808 (What's New in iOS Design), 809 (Designing iPad Apps for Mac), 802 (Designing Award Winning Apps and Games), 206 (Introducing SF Symbols), 511 (Supporting Dark Mode in Your Web Content)

## Headline

Dark Mode comes to iOS 13 (it had been on macOS since Mojave). The implementation centers on **semantic dynamic colors**, **dynamic images in the asset catalog**, and **system-provided materials** with vibrancy. SF Symbols introduces 1,500 vector glyphs that ship with every Apple platform.

## The Three Pillars of Dark Mode (214)

1. **Semantic colors** — `.label`, `.secondaryLabel`, `.systemBackground`, `.secondarySystemBackground`, `.tertiarySystemBackground`, `.systemGroupedBackground`, `.systemFill`, `.separator`, etc. These resolve to different RGB values in light vs dark modes.
2. **Materials** — `UIBlurEffect.Style.systemMaterial`, `.systemThinMaterial`, `.systemThickMaterial`, `.systemUltraThinMaterial`, `.systemChromeMaterial` plus their light/dark variants. Materials adapt automatically.
3. **Vibrancy** — new vibrancy styles for text and fills layered on top of materials: `.systemMaterial` blur with `.label` vibrancy.

## Trait Collection Resolution (214)

- `UITraitCollection.userInterfaceStyle` is `.light`, `.dark`, or `.unspecified`.
- `UITraitCollection.userInterfaceLevel` is `.base` or `.elevated`. **HIDDEN GEM**: in dark mode, system background colors are LIGHTER at the elevated level (presented sheets, popovers) to differentiate from the base black. Light mode behaves the same at both levels.
- `UITraitCollection.current` is the new global current trait collection set by UIKit before calling `draw`, `layoutSubviews`, `traitCollectionDidChange`, etc. **HIDDEN GEM**: matches macOS `NSAppearance.current` exactly.

## Resolving Dynamic Colors (214)

Three ways:
```swift
// 1. Explicit
let resolved = dynamicColor.resolvedColor(with: traitCollection)

// 2. perform-as-current closure (recommended)
traitCollection.performAsCurrent {
    layer.borderColor = dynamicColor.cgColor   // resolves correctly
}

// 3. Direct set (lightweight, thread-safe)
let saved = UITraitCollection.current
UITraitCollection.current = traitCollection
defer { UITraitCollection.current = saved }
layer.borderColor = dynamicColor.cgColor
```

**BEST PRACTICE**: outside of the UIKit-tracked methods (draw/layoutSubviews/etc.), the current trait collection is undefined. If you must access `.cgColor` on a dynamic color from a callback, wrap it in `performAsCurrent`.

## Custom Dynamic Colors (214)

```swift
let myColor = UIColor { traits in
    traits.userInterfaceStyle == .dark ? .systemTeal : .systemBlue
}
```

Or in the asset catalog: open the color, in the Inspector enable Dark Appearance, set both variants. Same for images — add a Dark slot.

## CGColor / Layer Gotcha (214)

CALayer / CGColor know nothing about dynamic colors. `layer.borderColor = UIColor.label.cgColor` resolves once at that moment — when traits change, your border color won't update. **URGENT**: override `traitCollectionDidChange` and re-set CG colors there. Or use `hasDifferentColorAppearance(comparedTo:)` to skip when only non-color traits changed.

## hasDifferentColorAppearance (214)

```swift
override func traitCollectionDidChange(_ previous: UITraitCollection?) {
    super.traitCollectionDidChange(previous)
    if traitCollection.hasDifferentColorAppearance(comparedTo: previous) {
        // re-resolve CGColors
    }
}
```

## SF Symbols (206)

- 1,500+ Apple-designed vector glyphs in 9 weights, 3 scales, with built-in alignment to text baselines.
- Free to use in any app on iOS 13 / macOS / watchOS / tvOS.
- Use the **SF Symbols app** to browse, copy names, and create custom symbols (export Pro template, edit in Illustrator/Sketch, drop into asset catalog).
- API: `UIImage(systemName: "heart.fill")`, `Image(systemName: "heart.fill")`.
- **HIDDEN GEM**: SF Symbols sized via `.font(.title)` modifier on Image — they pick up the current text style automatically and align to text. No more manually picking icon sizes per dynamic type bracket.
- **HIDDEN GEM**: hierarchical configurations (`UIImage.SymbolConfiguration`) let you set point size, weight, scale, and template/multicolor rendering mode.

## Custom Symbols Workflow (206)

- Pick the closest existing symbol → File → Export Custom Symbol Template (.svg).
- Edit each weight/scale you care about. Most apps just edit Regular at 1x and let SF Symbols app interpolate.
- Drop the SVG into the asset catalog as a Symbol Image. Reference by your custom name.

## Visual Design & Accessibility (244)

- **Differentiate Without Color** — preference in Settings → Accessibility. Provide alternate visual cues (shapes, patterns, labels) for color-coded UI.
- **Reduce Transparency** — preference. Vibrancy/materials should fall back to opaque equivalents.
- **Smart Invert vs Classic Invert** — Smart Invert preserves photos, media, and intentionally-inverted assets via `accessibilityIgnoresInvertColors = true`. **HIDDEN GEM**: set this on UIImageView/views containing photos to prevent unwanted inversion.
- **Increase Contrast** — preference. Use `UIAccessibility.isDarkerSystemColorsEnabled` and `UITraitCollection.accessibilityContrast`.
- **Bold Text** — preference. Use weighted system fonts (`.bold`, `.semibold`) so they get even bolder.

## Modal Sheets in iOS 13 — Visual Design (224)

- New default sheet style: `.pageSheet`. Card-style with rounded corners. Pull-to-dismiss for free.
- Tappable area outside the card dismisses (you can suppress with `.isModalInPresentation = true`).
- For your custom camera or fullscreen game, set `.fullScreen` explicitly.

## iPad Design for Mac (809)

- Mac apps use richer, more detailed icons (up to 512pt with transparency, no rounded rectangle mask). Provide a Mac slot in your AppIcon asset.
- Mac toolbars sit above content, not at the bottom. Use `NSToolbar` via `windowScene.titlebar`.
- Mac sidebars are translucent — use `splitViewController.primaryBackgroundStyle = .sidebar`.
- 13pt is Mac body font; 17pt is iOS body font. UIKit auto-scales content to 77% on Mac.

## Cross-references

- SwiftUI dynamic color access via `Color.label` and `.foregroundColor(.secondary)`: 216, 226.
- Web dark mode: 511 — `prefers-color-scheme` media query in CSS, `<meta name="color-scheme">` tag.
- Modernizing UI for iOS 13: 224 (the bars and sheets companion piece to dark mode).
