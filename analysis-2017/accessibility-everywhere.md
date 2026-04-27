# Accessibility, Sound Design & Inclusive UX — WWDC 2017 Analysis

**Sessions covered:** 215 (What's New in Accessibility), 217 (Media and Gaming Accessibility), 245 (Building Apps with Dynamic Type), 219 (Modern User Interaction on iOS — large content viewer hooks), 803 (Designing Sound), 806 (Design For Everyone), 819 (Designing for a Global Audience)

## Headline

iOS 11 ships **Smart Invert Colors**, **VoiceOver image descriptions**, **bigger Dynamic Type accessibility ranges**, and **Type-to-Siri** — most of which work for free if you use system-provided controls and follow Dynamic Type properly. The biggest coding lift is making custom controls describe themselves to assistive technologies and reflowing for the new accessibility content size categories.

## Smart Invert Colors (215)

A new accessibility setting that inverts UI colors but **preserves images, videos, and color-rich content** (the icon, photos, etc.).

```swift
view.accessibilityIgnoresInvertColors = true
```

Set this on any UIImageView / WKWebView / SCNView showing photographic or color-essential content. The system will skip color inversion for those subviews.

**HIDDEN GEM**: this is the recommended replacement for the old Classic Invert. Apps that are dark-mode-friendly natively (rare in 2017) get a much better invert experience because the system doesn't try to flip them — but you must opt out per-view to protect imagery.

## Type to Siri (215)

Activated by Settings → General → Accessibility → Siri → Type to Siri. The user types instead of speaks. SiriKit intent flows are unaffected — your domain handlers see the same `INIntent` objects. **Test your SiriKit handlers** with Type to Siri to catch confirmation/disambiguation flows that assume voice.

## Larger Dynamic Type Range (215, 245)

iOS 11 adds five **accessibility content size categories** above the regular range:

- `.accessibilityMedium`
- `.accessibilityLarge`
- `.accessibilityExtraLarge`
- `.accessibilityExtraExtraLarge`
- `.accessibilityExtraExtraExtraLarge`

At `.accessibilityExtraExtraExtraLarge`, body text reaches 53 pt. **Side-by-side controls in the same row WILL break.** Detect with:

```swift
if traitCollection.preferredContentSizeCategory.isAccessibilityCategory {
    // Switch to vertical stack layout
}
```

- `UIFontMetrics.scaledFont(for:)` is the modern way to use custom fonts with Dynamic Type. Pair with `adjustsFontForContentSizeCategory = true` on `UILabel`/`UITextView`.
- **HIDDEN GEM**: stacks (`UIStackView`) reflow naturally when contents grow. Designing in stacks now saves enormous accessibility work later.

## Large Content Viewer (215, 219)

Tab bar items get a long-press magnifier preview at large content sizes — the "what does this glyph mean?" gesture. Implement:

```swift
UILargeContentViewerInteraction()  // attach to any view
// or set largeContentImage / largeContentTitle on UIBarItem
```

For custom controls without bar-item ancestry, attach a `UILargeContentViewerInteraction` and conform to `UILargeContentViewerItem`. The system shows your `largeContentImage` and `largeContentTitle` in a magnified popup.

## VoiceOver Image Descriptions (215)

iOS 11 starts including **machine-generated image descriptions** in VoiceOver when no accessibility label is set on a UIImageView with content image. Don't rely on it — provide explicit labels. But it's a useful safety net for user-generated photos.

For decorative images: set `accessibilityElementsHidden = true` so VoiceOver skips them entirely.

## Custom Controls (215, 245)

For any custom-drawn control, implement:

```swift
override var accessibilityLabel: String? {
    get { return "Volume slider, \(Int(value * 100)) percent" }
    set { super.accessibilityLabel = newValue }
}
override var accessibilityValue: String? { … }
override var accessibilityTraits: UIAccessibilityTraits {
    get { return .adjustable }
    set { super.accessibilityTraits = newValue }
}
override func accessibilityIncrement() { value += 0.1 }
override func accessibilityDecrement() { value -= 0.1 }
```

`.adjustable` traits enable VoiceOver swipe up/down for increment/decrement.

**HIDDEN GEM**: `accessibilityCustomActions = [UIAccessibilityCustomAction(name: "Mark complete", target: self, selector: #selector(markComplete))]` lets you expose contextual actions for VoiceOver users beyond the visible UI. Mail uses this for swipe-to-archive.

## Media & Gaming Accessibility (217)

- **AVPlayer subtitles**: `AVPlayerItem.textStyleRules` lets you respect the user's `Settings → Accessibility → Subtitles & Captioning → Style` choice. Without it, subtitles render in your hardcoded style.
- Switch Control gains directional input — game controllers can act as switches with point-and-click for users with limited mobility.
- `AXSpeakSelectionEnabled` API for apps that want to provide their own speech synthesis without competing with VoiceOver.

## Designing Sound (803)

- Use sound to **augment**, never to **replace** visual feedback. The user might be deaf, in a noisy environment, or have audio off.
- Avoid sounds that mimic system events (incoming-message ding, battery-low chime) — confusing for users.
- **HIDDEN GEM**: pair sound with haptic feedback (`UINotificationFeedbackGenerator`) — the multi-modal pulse is more discoverable than either alone.
- For games, design a "sound-off mode" that uses haptics, color, motion to convey the same urgency as the audio cue. Not optional — App Review enforces accessibility.

## Designing For Everyone (806)

- Color is NEVER the only way to convey information. Pair with shape, label, or pattern.
- Maintain WCAG AA contrast minimum (4.5:1 for body text, 3:1 for large text).
- Touch targets minimum 44×44 pt (Apple HIG; bumped from 40×40 in older guidance).
- Animation: respect `UIAccessibility.isReduceMotionEnabled`. Replace cross-dissolves with simple cuts; disable parallax on launch screens.

## Globalization (819)

- Pluralization via `.stringsdict` — never concatenate "%d items". Different languages have 1-6 plural forms (Russian needs "1 яблоко" / "2 яблока" / "5 яблок").
- Right-to-left layout: use `leadingAnchor` and `trailingAnchor`, never `leftAnchor` / `rightAnchor` for content. Hebrew/Arabic flip automatically.
- Date/time/currency: `DateFormatter.localizedString(from:dateStyle:timeStyle:)` and `NumberFormatter` — never format manually.
- **HIDDEN GEM**: `Bundle.main.preferredLocalizations` returns the user's preferred languages in priority order. Use this for content negotiation with your server.

## Cross-references

- See `ios11-design-language.md` — Dynamic Type integration with the new bar styles.
- See `swift4-language-codable.md` — `Locale.current` for proper i18n with Codable.
