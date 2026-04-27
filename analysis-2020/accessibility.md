# WWDC 2020 — Accessibility

WWDC 2020's accessibility story focused on **Switch Control improvements** for severe motor impairments, **VoiceOver custom rotors**, **visually accessible** UI patterns, **speech experience**, and Catalyst-specific accessibility considerations.

## Sessions Analyzed
- 10019 — App accessibility for Switch Control
- 10020 — Make your app visually accessible
- 10116 — VoiceOver efficiency with custom rotors
- 10117 — Accessibility design for Mac Catalyst
- 10022 — Create a seamless speech experience in your apps

## Switch Control: Build for Adaptive Switches (10019)

Switch Control lets users with severe motor impairments operate iOS via external switches — single-button input that scans through interface elements. To be Switch-Control-friendly:

- **Logical accessibility hierarchy** — group related elements with `accessibilityElements` so the scanner doesn't have to step through 30 individual cells when 3 sections are meaningful.
- **Group with `accessibilityContainerType = .semanticGroup`** for collections of related items.
- **Honor `accessibilityActivate()`** correctly — when the switch user activates an element, do the right thing.
- Provide **custom actions** (`accessibilityCustomActions`) for context-menu-like or swipe-action operations that aren't trivially activatable.
- Avoid time-based interactions (drag for X seconds) — Switch Control users can't easily replicate them.

## Visual Accessibility (10020)

For users with low vision, color blindness, or sensitivity to motion:
- **Dynamic Type** — support all text styles, including the accessibility-extra-large sizes. Custom fonts must scale (use `UIFontMetrics.scaledFont(for:)`).
- **Bold Text** — UI updates automatically if you use system fonts; don't fight the system weight.
- **Reduce Motion** — check `UIAccessibility.isReduceMotionEnabled`; disable parallax, large transitions, autoplaying video. SwiftUI: use `@Environment(\.accessibilityReduceMotion)`.
- **Reduce Transparency** — solid fills instead of vibrancy.
- **Increase Contrast** — high-contrast color variants in your asset catalog.
- **Don't rely on color alone** for status indication. Pair color with shape/icon/text.
- **Color contrast** — meet WCAG AA at minimum (4.5:1 for body text, 3:1 for large text).

The **Accessibility Inspector** in Xcode can audit color contrast, dynamic-type behavior, and missing accessibility labels at build time.

## VoiceOver Custom Rotors (10116)

Custom rotors are the dial-and-turn navigation gesture in VoiceOver. Apps can declare their own rotors so VoiceOver users can navigate domain-specific elements:

```swift
let headingsRotor = UIAccessibilityCustomRotor(name: "Headings") { predicate in
  // Find next/previous heading from predicate.currentItem
  // Return UIAccessibilityCustomRotorItemResult
}
view.accessibilityCustomRotors = [headingsRotor]
```

Common custom rotors to consider:
- **Headings** in document apps
- **Links** in browsers/articles
- **Form fields** in forms
- **Comments / messages** in conversation views
- **App-specific entities** (recipes, photos, songs)

The rotor implementation works backward and forward from the user's current position; design for circularity (next item after the last loops to first).

## Catalyst Accessibility (10117)

Mac Catalyst apps inherit much of UIKit accessibility but interact with **AppKit's accessibility model**. Specific guidance:
- **VoiceOver on Mac** uses different gestures than iOS — test extensively.
- **Standard Mac shortcuts** matter more (Tab navigation, Cmd-? for help).
- **Menu bar** is the canonical location for many actions; add menu items so VoiceOver discovers them in the predictable Mac place.
- **Accessibility hint** for buttons that have ambiguous icon meaning (especially in toolbars).
- **AccessibilityElement properties** are still used; don't fight the AppKit-style preferences (e.g., explicit role naming).

## Seamless Speech Experience (10022)

Speech-input apps (dictation, voice control, accessibility tools) integration:
- Use **`SFSpeechRecognizer`** for dictation; respect `requiresOnDeviceRecognition` (iOS 13+) for privacy.
- For apps with custom voice commands, layer on top of system Voice Control rather than building parallel command grammars.
- Provide **transcription UI** that shows users what was heard (pre-confirmation).

## SwiftUI Accessibility

SwiftUI added accessibility-specific modifiers (covered in 2019 but expanded in 2020):
- `.accessibilityLabel(_:)`, `.accessibilityHint(_:)`, `.accessibilityValue(_:)`
- `.accessibilityElement(children: .combine | .ignore)` for grouping
- `.accessibilityAction(_:_:)` for custom actions
- `.accessibilityRotor(_:_:_:)` (added later but the pattern was forming)

## Cross-References
- [big-sur-design-system.md](big-sur-design-system.md) — Catalyst accessibility lives within the broader Big Sur work.
- [swiftui-2-foundation.md](swiftui-2-foundation.md) — Label view auto-handles many accessibility considerations.
- [ipados-pointer-scribble.md](ipados-pointer-scribble.md) — Pointer interactions affect VoiceOver navigation.

## Adoption Checklist
- [ ] Run the Accessibility Inspector audit on every screen.
- [ ] Verify VoiceOver navigation order is logical and uses headings/sections appropriately.
- [ ] Add custom rotors for any domain-specific entity navigation.
- [ ] Audit for color-only status indicators; add icon/text supplements.
- [ ] Verify Dynamic Type works at all sizes including the accessibility ones.
- [ ] Honor `isReduceMotionEnabled`, `isReduceTransparencyEnabled`, `isDarkerSystemColorsEnabled`.
- [ ] If a Catalyst app, test VoiceOver on Mac specifically.
- [ ] If user-facing text, target WCAG AA contrast.
- [ ] Test with Switch Control to verify your hierarchy makes sense for one-button users.
