# WWDC 2023 — Accessibility, watchOS 10, & Design

WWDC 2023 brings two highly visible UX shifts: the watchOS 10 redesign (full-screen color, vertical Digital Crown navigation), and Assistive Access (a radically simplified iOS interface for cognitive accessibility).

## Sessions Analyzed

### Accessibility & Inclusion
- 10032 — Meet Assistive Access
- 10033 — Extend Speech Synthesis with personal and custom voices
- 10034 — Create accessible spatial experiences
- 10035 — Perform accessibility audits for your app
- 10036 — Build accessible apps with SwiftUI and UIKit

### watchOS 10
- 10026 — Meet watchOS 10
- 10031 — Update your app for watchOS 10
- 10138 — Design and build apps for watchOS 10
- 10309 — Design widgets for the Smart Stack on Apple Watch
- 10029 — Build widgets for the Smart Stack on Apple Watch

### Design
- 10072 — Principles of spatial design
- 10073 — Design for spatial input
- 10075 — Design spatial SharePlay experiences
- 10076 — Design for spatial user interfaces
- 10078 — Design considerations for vision and motion
- 10115 — Design with SwiftUI
- 10193 — Design Shortcuts for Spotlight
- 10194 — Design dynamic Live Activities
- 10271 — Explore immersive sound design

## Assistive Access (10032)

Assistive Access is an iOS MODE (not just a setting) for users with cognitive disabilities. The system replaces the standard iPhone UI with a radically simplified one: large icons, high-contrast labels, fewer choices per screen, big back buttons.

The system ships built-in support for: Phone, FaceTime, Camera, Music, Photos, Messages.

YOUR APP can support Assistive Access by:
1. Detecting the mode: `UIApplication.shared.isAssistiveAccessRunning` (or equivalent SwiftUI environment).
2. Providing simplified scenes via the new `UIScene` declaration in Info.plist.
3. Each scene presents ONE primary action with a clear label and large hit targets.

```xml
<key>UIApplicationSceneManifest</key>
<dict>
  <key>UIApplicationSupportsAssistiveAccess</key>
  <true/>
</dict>
```

This is a NEW API surface — adopting it before competitors gives your app inclusive credibility.

## Personal Voice (10033)

Major Speech Synthesis update:
- USERS can train a synthetic voice that sounds like THEM (15 minutes of recorded prompts → on-device model).
- Used by people at risk of losing their voice (ALS, throat cancer).
- Apps can REQUEST permission to USE that voice via `AVSpeechSynthesisVoice.personalVoice`:

```swift
AVSpeechSynthesizer.requestPersonalVoiceAuthorization { status in
  if status == .authorized {
    let voice = AVSpeechSynthesisVoice.personalVoices.first
    let utterance = AVSpeechUtterance(string: text)
    utterance.voice = voice
    synthesizer.speak(utterance)
  }
}
```

User must explicitly grant permission. The voice model never leaves the device.

Use cases: communication apps for people with ALS, audiobook tools, personalized assistants.

## Accessibility Audits in Xcode (10035)

`XCUIApplication.performAccessibilityAudit()` runs a battery of checks:
- Hit target size (44x44 minimum)
- Sufficient contrast
- Missing accessibility labels
- Duplicate labels
- VoiceOver navigation order
- Trait misuse

```swift
func testAccessibility() throws {
  let app = XCUIApplication()
  app.launch()
  try app.performAccessibilityAudit()  // throws on failures
}
```

Add to CI to catch regressions. Audit catches the 80% of issues that are mechanical; manual VoiceOver testing still needed for the rest.

## SwiftUI/UIKit Accessibility (10036)

New APIs:
- `.accessibilityZoomAction { action in ... }` — let VoiceOver users zoom your image without using the magnification gesture.
- `.accessibilityDirectTouch` — for piano apps, drum apps where every touch matters.
- `.accessibilityShowsLargeContentViewer` — opt into the iOS large-content HUD for ANY view (not just standard controls).
- Automatic `accessibilityIdentifier` from declared types — fewer string literals.

UIKit:
- `UIAccessibilityCustomAction` now has visual representations.
- `UIAccessibilityDirectTouchOptions.silentOnTouch` for high-frequency touch interactions.

## watchOS 10 Redesign

Three big shifts:
1. **Full-screen color**: every screen has a vibrant background tied to content.
2. **Vertical Digital Crown navigation**: TabView gets a `.verticalPage` style, swipe via Crown.
3. **Smart Stack widgets**: replaces complications on most watch faces; rotating widget stack.

API additions:
- `.containerBackground(_:for:)` — full-screen backgrounds with smooth push/pop animations.
- `TabView(selection:)` with `.verticalPage` style.
- New toolbar placements: `.topBarLeading`, `.topBarTrailing` (cross-platform).
- DatePicker, list selection finally on watchOS.

If your watchOS app still ships an iOS-style UI, REDESIGN. The HIG and reference apps (Activity, Workouts) demonstrate the new visual language.

## Smart Stack Widgets (10029, 10309)

Smart Stack widgets are NOT the same as iOS widgets — they have a different size system and are displayed in a vertically scrollable stack on the watch face.

Use `WidgetConfiguration` with the `.accessoryRectangular` and `.accessoryCircular` families. The system selects which widget is FRONTMOST based on relevance signals:
- `Relevance` priority you supply.
- Time of day, location.
- Recent app usage.

Widget should reload often (timeline entries every minute or two for active widgets).

## Spatial Design Principles (10072)

Apple's design team's framework for visionOS:
- **Familiar**: SwiftUI controls look the same as on macOS, just in a 3D world.
- **Human**: design for natural sight lines, comfortable head positions; avoid full-FOV motion.
- **Dimensional**: depth is a design tool — use it sparingly, intentionally.
- **Immersive**: progressive immersion (start in a window, expand on demand).

Specific guidance:
- Place primary content 1–2m from the user.
- Avoid placing UI directly under or above the head — neck strain.
- Use SOFT, ROUNDED corners; sharp edges feel hostile in 3D.
- Audio should be SPATIAL by default; flat audio breaks immersion.

## Vision & Motion Considerations (10078)

CRITICAL guidance for visionOS apps to avoid sickness:
- DO NOT move the user's viewpoint without their explicit input.
- DO NOT animate large surfaces in their peripheral vision.
- DO use FADE for scene transitions, NOT motion.
- DO use comfort-zone palettes (avoid high-contrast strobing).
- Keep contrasts in mind — 95% of users won't have HDR at full brightness.

This session is required reading before shipping ANY visionOS app — not just games.

## Spatial SharePlay Design (10075)

When two people are in a SharePlay session in visionOS, the system maintains SHARED CONTEXT — the same virtual object appears in the same world position for both. Design for:
- Personas (the avatar) facing each other naturally.
- Pointing gestures should reach the same target.
- Spatial Persona Templates (`.sideBySide`, `.conversational`, `.surrounding`) configure participant layout.

## Pathways

- **Accessibility champion**: 10036 → 10035 → 10032 → 10033 → 10034
- **watchOS 10 adoption**: 10026 → 10031 → 10138 → 10029 → 10309
- **Spatial designer**: 10072 → 10073 → 10076 → 10078 → 10075

## Hidden Gems

- Assistive Access can launch your app DIRECTLY (skipping launch screen choice). The user's experience starts with your simplified scene.
- Personal Voice generation runs ENTIRELY on-device — no cloud upload. The training session takes ~30 minutes.
- `performAccessibilityAudit()` returns failures as an array; you can filter or `xfail` known issues without skipping the audit entirely.
- watchOS 10's `.containerBackground` is the WatchOS-recommended way to set per-screen color; it animates between screens.
- Smart Stack widget RELEVANCE scores are interpreted relatively — your app's widgets compete with each other and with the system.
- Spatial design's "comfort zone" puts primary UI between 0° and -25° below eye level — avoid forcing users to look up.
- Audio in spatial apps should NOT exceed -16dB LUFS sustained — louder audio causes long-session fatigue.
- Use the `accessibilityCustomContent` API for "screen reader can drill into more detail without flooding the announcement."
- watchOS 10 NavigationStack transitions automatically animate `containerBackground` across pushes — designers love it.
- Assistive Access scenes are SEPARATE from your normal scenes; you opt in EXPLICITLY by declaring them in Info.plist.
