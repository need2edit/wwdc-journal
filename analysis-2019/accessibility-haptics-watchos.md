# Accessibility, Haptics, watchOS & Independent Apps — WWDC 2019 Analysis

**Sessions covered:** 238 (Accessibility in SwiftUI), 250 (Making Apps More Accessible With Custom Actions), 254 (Writing Great Accessibility Labels), 257 (Accessibility Inspector), 261 (Large Content Viewer), 248 (Creating an Accessible Reading Experience), 244 (Visual Design and Accessibility), 223 (Expanding the Sensory Experience with Core Haptics), 520 (Introducing Core Haptics), 810 (Designing Audio-Haptic Experiences), 208 (Creating Independent Watch Apps), 219 (SwiftUI on watchOS), 251 (Extended Runtime for watchOS Apps), 716 (Streaming Audio on watchOS 6), 252 (Advances in CarPlay Systems)

## Headline

Two big debuts: **Voice Control** brings hands-free use of iOS and macOS, and **Core Haptics** opens up the Taptic Engine to all developers for synchronized haptic + audio experiences. **watchOS 6 launches the App Store directly on Apple Watch** with fully independent apps that don't need an iPhone.

## Voice Control (238, 244)

- Brand-new accessibility feature. Hands-free control of iOS/macOS via voice.
- "Tap [label]", "Show grid", "Show numbers", "Long press [label]", "Scroll up", etc.
- Works automatically with any UIControl/AppKit control that has a proper accessibility label.
- **URGENT**: if your custom controls lack `accessibilityLabel`, Voice Control can't operate them. Audit your app.

## Full Keyboard Access (238)

- Full keyboard navigation across iOS controls (Tab to move focus, Space/Return to activate).
- Was Mac-only; comes to iOS 13.
- Get it for free with standard UIKit controls; custom controls need `isAccessibilityElement = true` and proper traits.

## Custom Actions for Accessibility (250)

- `UIAccessibilityCustomAction` lets you expose discoverable actions on any element via a single rotor gesture.
- Replace 20-tap navigation paths with a single rotor selection.
- New in iOS 13: custom actions work with **VoiceOver, Switch Control, Voice Control, AND Full Keyboard Access**.
- **BEST PRACTICE**: any cell with multiple swipe actions (delete/archive/flag/etc.) should expose them as custom actions too.

## Writing Great Labels (254)

- Labels should be **concise, descriptive nouns**.
- Don't say "button" — VoiceOver appends the trait automatically.
- **State** belongs in `accessibilityValue`, not the label. Toggle: label = "Wi-Fi", value = "On".
- For images: describe what's depicted, not the file name. "Photo of a sunset" not "sunset.jpg".
- For icons-only buttons: the label IS the action. Heart icon → "Like".
- **HIDDEN GEM**: Apple now ships an Accessibility Audit (in Accessibility Inspector) that flags missing/poor labels in your app automatically.

## SwiftUI Accessibility (238)

Already covered in `swiftui-debut.md`. Highlights:
- SwiftUI generates accessibility elements for every view.
- `.accessibility(label:value:hint:)`, `.accessibilityAction(named:)`, `.accessibility(addTraits:removeTraits:)`.
- **HIDDEN GEM**: SwiftUI sends accessibility notifications automatically when state changes — no manual `UIAccessibility.post(notification:)`.

## Large Content Viewer (261)

- Tab bars and toolbars can't grow with Dynamic Type, but they can show a heads-up display when long-pressed.
- iOS 13 brings this API to custom tab bars: implement `UILargeContentViewerInteraction`.
- Long-press a tab → magnified label + image floats over the screen.
- **BEST PRACTICE**: required for any custom tab/toolbar to be Dynamic-Type-compliant.

## Core Haptics (223, 520, 810)

A brand-new framework for designing custom haptic patterns synchronized with audio.

### CHHapticEngine

```swift
let engine = try CHHapticEngine()
try engine.start()
```

### Pattern definition

- **Transient events** — quick taps, sharpness 0-1, intensity 0-1.
- **Continuous events** — sustained vibrations with a duration.
- **Audio events** (CHHapticAudioContinuousEvent / Custom) — play synchronized audio with the haptic.

### AHAP Files

- **Apple Haptic Audio Pattern** — JSON-based file format describing patterns.
- Design in code or in the AHAP authoring tool.
- Example pattern: a "machine gun" — five transients with decreasing intensity, with a continuous low-pitched audio bed.

```json
{
  "Pattern": [
    { "Event": { "Time": 0.0, "EventType": "HapticTransient",
      "EventParameters": [
        { "ParameterID": "HapticIntensity", "ParameterValue": 1.0 },
        { "ParameterID": "HapticSharpness", "ParameterValue": 0.5 }] }}
  ]
}
```

### Use cases (810)

- Game feedback (impact, terrain, weapon recoil).
- UI response (button press confirmations, error vibrations).
- Photo capture shutters with custom haptics.
- Music apps with synchronized rhythm haptics.

**HIDDEN GEM**: Core Haptics replaces UIImpactFeedbackGenerator/UISelectionFeedbackGenerator only when you need custom patterns. The simple feedback generators are fine for common cases.

## watchOS 6: Independent Apps (208, 219)

- Apple Watch ships its own App Store. Users can install watch apps without ever opening the iOS counterpart.
- **Independent apps** — no iPhone app required. Fully standalone.
- New Watch APIs: networking (URLSession with Combine), sign in with Apple, push notifications, audio streaming (716).
- New SwiftUI for watchOS — best-in-class for building watch UI from scratch.

### Targeting watchOS 6 properly

1. Project settings → "Supports Running Without iOS App Installation" = YES.
2. Bundle ID for watchOS app must NOT include `.watchkitapp` — it stands on its own.
3. Sign in with Apple works without the iPhone via secure enclave on the watch (Series 3+).

### Extended Runtime (251)

- Workout, navigation, mindfulness, and physical-therapy session types can request extended runtime.
- `WKExtendedRuntimeSession.start(at:)` — your app continues running with the screen off.
- Replaces ad-hoc background-mode tricks and gives clear power expectations.

## CarPlay (252)

- Third-party apps can now drive CarPlay UI: Audio, Communication, Messaging, Navigation, Parking, Quick Food, EV Charging.
- Use the new `CarPlay` framework: `CPListTemplate`, `CPMapTemplate`, `CPGridTemplate`, `CPNowPlayingTemplate`.
- Custom navigation apps can finally exist on CarPlay (previously Apple Maps only).
- **URGENT**: requires Apple's MFi-style entitlement for CarPlay developers.

## Cross-references

- SwiftUI accessibility: 216, 238.
- Audio + haptic synchronization underlies game feel and music apps: 223, 510 (AVAudioEngine), 810.
- watchOS independent app implications: 706 (Sign In with Apple works without iPhone).
