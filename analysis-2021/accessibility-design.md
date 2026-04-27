# Accessibility & Design (WWDC 2021)

## Sessions covered
- WWDC21-10119 — SwiftUI Accessibility: Beyond the basics
- WWDC21-10120 — Support Full Keyboard Access in your iOS app
- WWDC21-10121 — Tailor the VoiceOver experience in your data-rich apps
- WWDC21-10122 — Bring accessibility to charts in your app
- WWDC21-10220 — Localize your SwiftUI app
- WWDC21-10221 — Streamline your localized strings
- WWDC21-10223 — Create accessible experiences for watchOS
- WWDC21-10259 — Your guide to keyboard layout
- WWDC21-10275 — The practice of inclusive design
- WWDC21-10304 — The process of inclusive design
- WWDC21-10308 — Accessibility by design: An Apple Watch for everyone
- WWDC21-10318 — Developer spotlight: Accessibility
- WWDC21-10097 — What's new in SF Symbols
- WWDC21-10250 — Create custom symbols
- WWDC21-10288 — Explore the SF Symbols 3 app
- WWDC21-10349 — SF Symbols in SwiftUI
- WWDC21-10251 — SF Symbols in UIKit and AppKit
- WWDC21-10126 — Discoverable design

## Best practices

- **`accessibilityRepresentation(representation:)` is the recommended pattern for custom controls.** Wrap your bespoke view's accessibility behind a stock `Slider`/`Toggle`/`Stepper`. Inherits all the platform behaviors (WWDC21-10119).
- **Combine `accessibilityElement(children: .combine)`** for cells in a `ForEach` — VoiceOver navigates each row as a single element with merged label/actions instead of element-per-subview chaos (WWDC21-10119).
- **Default sort order is geometric (top-left → bottom-right).** Use `accessibilityElement(children: .contain)` to wrap related items in a container so navigation order matches visual grouping (WWDC21-10119).
- **Custom rotors** (`accessibilityRotor(_, entries:)`) — VoiceOver users get a "Warnings" rotor that jumps between only-warning items, instead of every list element. Massive efficiency win for power users (WWDC21-10119, WWDC21-10121).
- **For SF Symbols**: don't hardcode `.fill` — let the system pick variant via context (`tabBar` → fill, `macOS toolbar` → outline) (WWDC21-10097, WWDC21-10349).

## Hidden gems

- **Accessibility Preview tab** in Xcode 13 SwiftUI previews shows the textual accessibility tree live, in sorted order. Lets you debug VoiceOver order without leaving Xcode (WWDC21-10018, WWDC21-10119).
- **Hierarchical SF Symbols**: pass one tint color, get auto-derived opacity layers. **Palette**: explicit per-layer tints. **Multicolor**: fixed-palette symbols (WWDC21-10097, WWDC21-10251).
- **Custom SF Symbols**: the new SF Symbols 3 app exports an SVG template you fill in for all weights/scales. Imports as a single asset; renders consistently with system symbols (WWDC21-10250, WWDC21-10288).
- **Full Keyboard Access** on iOS 15: VoiceOver-style focus navigation but for sighted users with motor impairments. Audit your app with the new `accessibilityRotor` and standard `Button`/`TextField` semantics (WWDC21-10120).
- **Audio Graphs** for VoiceOver chart accessibility: `accessibilityChartDescriptor(_:)` produces a descriptor that VoiceOver renders as audio frequency sweeps representing data trends (WWDC21-10122).
- **String catalogs precursor**: Xcode 13 Swift compiler extracts `LocalizedStringKey` usage automatically into stringsdict — the explicit String Catalog format ships in 2023 (WWDC21-10221).

## Performance

- VoiceOver custom rotors are O(1) navigation between bookmarks — they don't traverse the entire accessibility tree on each gesture (WWDC21-10121).

## Migration guidance

- If you previously labeled SF Symbol-only buttons with `.accessibilityLabel("Edit")`, audit them — many SF Symbols already have correct default labels. The Accessibility Preview shows what the symbol's default label is (WWDC21-10119).
- For any view that does its own drawing (`Path`, `Canvas`, `Shape`), add at least a label. Consider `accessibilityChildren` to expose programmatic structure (WWDC21-10119, WWDC21-10122).

## Cross-references

- 2023's `accessibilityAudit()` extends this audit story to XCUITest assertions.
- 2021's "Discoverable design" (WWDC21-10126) covers progressive disclosure principles, which align with the watchOS 8 navigation redesign.
