# Design, Accessibility & UX Writing -- WWDC24 Deep Analysis

Comprehensive analysis of WWDC 2024 design and accessibility sessions covering visionOS design principles, the next-gen CarPlay design system, accessibility in SwiftUI, dynamic type, App Intent design, and UX writing.

Sessions analyzed: 10086 (Design great visionOS apps), 10085 (Design advanced games), 10087 (Custom environments), 10096 (Interactive visionOS experiences), 10098 (Live Activities watchOS), 10112 (Next-gen CarPlay), 10140 (UX writing), 10176 (Design App Intents), 10188 (SF Symbols 6), 10073 (Accessibility in SwiftUI), 10074 (Dynamic Type).

---

## 1. visionOS Design Philosophy (WWDC24-10086)

### 1.1 The Four Pillars

Sarah from the Design Team distilled visionOS app excellence into four words:
1. **Intentional** -- find your "key moment"; build for the platform
2. **Immersive** -- across the spectrum of immersion levels
3. **Comfortable** -- minimal physical movement, ergonomic windowing
4. **Delightful** -- exceptional craft, real-world correspondence

### 1.2 The "Key Moment" Concept

> "When we first work with a team we encourage developers to find their key moment, which is the moment in an app that's optimized for visionOS." (WWDC24-10086)

Examples:
- **Mindfulness** -- the breathing flower
- **JigSpace** -- deconstructable 3D models with electrical wiring
- **Loona** -- 3D meditative puzzles that animate to life
- **Lowe's Style Studio** -- step into a virtual kitchen
- **Sky Guide** -- planetarium with constellations

**The product question:** What's the ONE moment in your app that wouldn't be possible (or as compelling) anywhere else?

### 1.3 Three Strategies for Spatial Solutions

| Strategy | Example | When |
|---|---|---|
| **Make new things possible** | JigSpace | Take your existing concept further |
| **Build something complementary** | Lowe's | Big iOS app, focused visionOS app |
| **Iterate from prototypes** | Loona | Don't port the iOS experience, redesign |

### 1.4 The Three Forms of Immersion

1. **Take people somewhere new** -- full immersion (Sky Guide planetarium)
2. **Integrate with physical surroundings** -- Super Fruit Ninja's juice splatters on real walls; Truffles the pig jumps on your real bed
3. **Meaningful audio moments** -- visionOS uses room geometry to add reverb. Sound is feedback, not just ambiance (Blackbox)

### 1.5 The "Custom Environments Are Not Always The Answer" Caveat

> "Custom Environments are not relevant for every app on Vision Pro, so don't assume that this is the only way to immerse people."

Often the better path is meaningful integration with the user's actual room (Super Fruit Ninja, PGA Tour) rather than replacing it.

### 1.6 Comfort Rules

- **Minimize movement** -- design for users who don't move (Super Fruit Ninja's geometric play-area guide)
- **Minimize windows** -- prefer one window with ornaments (PGA Tour pattern) over many
- **Use the Glass material** -- it adapts to environment lighting; don't use solid backgrounds. (Red Bull TV uses glass for content cards but allows their brand color briefly during loading)
- **60-point minimum tap targets** for hover effects
- **Hover effects only on interactive elements** -- Carrot Weather correctly excludes data-display elements

### 1.7 Delight via Real-World Correspondence (DJay)

DJay's design lessons from WWDC24-10086:
- Place interactive content WITHIN ARM'S REACH (close = interactive expectation)
- Use motion/animation to signal interactivity (the pulsing music-icon stroke)
- Map gestures to familiar real-world actions (raise hand to ear = preview track)
- Account for false positives (raising hand to fix hair shouldn't preview)
- Abstract away unnecessary complexity (auto-tempo-sync) to make the experience accessible to non-experts

---

## 2. Designing App Intents for System Experiences (WWDC24-10176)

### 2.1 The Three Questions for Every Intent

Before writing an intent, design teams answer:
1. **What's the action?** Verbs people would say to Siri
2. **What does it operate on?** Nouns from your app
3. **What does success look like?** Visual snippet or spoken dialog

### 2.2 The "Make It Self-Contained" Rule

> "App Intents should always be actions that are meaningful to someone who uses the app." (WWDC24-10210)

Example: NOT `NavigateToTrailDetailIntent`. YES `OpenTrailIntent`. The user thinks "open the trail," not "navigate the navigation manager to the detail screen."

### 2.3 ParameterSummary Is a UX Element

The natural-language summary `"Open \(\.$trail)"` is the difference between an unusable intent and a delightful Shortcut. Put time into wording.

### 2.4 Result Design

Three result types that deserve distinct treatment:
- **`.result(value:)`** -- raw value; Siri rarely uses this for ambient queries
- **`.result(dialog:)`** -- spoken response (great for HomePod/AirPods)
- **`.result(view:)`** -- snippet view (great for on-screen)

The pattern: **provide both** dialog AND view. Siri picks the right one for the context.

### 2.5 App Shortcuts -- 5 Phrase Rule

Each `AppShortcut` defines spoken phrases. **Each must contain the app name** -- this gives Siri the disambiguation hint to know which app to invoke. Provide multiple variations: "Show me trails in MyApp", "Open trails in MyApp", etc.

---

## 3. Next-Gen CarPlay Design System (WWDC24-10112, 10111)

### 3.1 The Co-Branded Experience

This is **not** classic CarPlay. The next-gen system replaces all instrument cluster screens too, with:
- Driver-cluster gauges (speedometer, tachometer, fuel/state-of-charge)
- Center display
- Passenger displays
- Custom backgrounds

### 3.2 Variable Fonts Drive Customization

SF variable fonts allow per-axis interpolation (weight, width, corner softness). The same logic applies to gauge geometry: arc length, start/end points, stroke width, tick density.

### 3.3 The Modular Layout System

Each gauge is a self-contained component that can be:
- Resized
- Repositioned
- Combined into different configurations
- Themed independently

Adapts to wide displays, irregular shapes, instrument-focused or content-focused layouts.

### 3.4 Reserved Dynamic Content Area

A space the driver controls via steering wheel: maps, now-playing, trip computer, tire pressure, ADAS. Notifications also default here. Two notifications can be shown simultaneously when needed.

### 3.5 Mandatory vs. Optional Gauges

| Mandatory | Optional |
|---|---|
| Current speed | Tachometer |
| Fuel/state-of-charge | Power meter |
| | Engine coolant temperature |
| | Hybrid combo gauges |

### 3.6 For Developers

To support next-gen CarPlay, automakers enroll in the MFi program. App developers don't need new code -- the system surfaces existing CarPlay-aware app data automatically. The companion technical session is WWDC24-10111.

---

## 4. SF Symbols 6 (WWDC24-10188)

### 4.1 New Animation Presets

| Effect | Use case | Notes |
|---|---|---|
| `.wiggle` | Draw attention | Direction or angle is configurable |
| `.breathe` | Indicate ongoing activity | Smooth scale up/down |
| `.rotate` | Spin parts around an anchor | Per-anchor configuration |

### 4.2 New Animation Behaviors

- **`.periodic`** -- repeat count + delay between repetitions
- **`.continuous`** -- seamless animation across repetitions

### 4.3 MagicReplace -- The Default Replace Behavior

In iOS 18, the default `.replace` animation prefers MagicReplace, which **smoothly animates badges and slashes** between symbols (e.g., `bell` ↔ `bell.slash`).

> "This behavior automatically falls back to a standard replace style if needed. For example, Magic Replace isn't supported across the mic and video symbols, so the DownUp replace style is automatically used as a fallback."

You can specify an explicit fallback: `.replace.magic(fallback: .downUp)`.

### 4.4 Other Improvements

- New annotations for **variable color timing** (so each segment animates at its own pace)
- Additional behaviors for `.bounce` effects
- Updated SF Symbols app with effect previews

---

## 5. Accessibility in SwiftUI (WWDC24-10073)

### 5.1 The Accessibility-Element Mental Model

> "Accessibility technologies like VoiceOver only interact with apps through their elements so only content from views that are included in an element will be accessible to them."

When you write a SwiftUI view, SwiftUI generates BOTH:
- The on-screen output (rendered)
- An accessibility tree (elements + attributes + actions)

A `Toggle` automatically becomes one element with `isToggle`, `isSelected`, label, and a press action -- you don't write any of that.

### 5.2 The View Style Guarantee

> "When changing the style using the toggle style modifier, the visuals of my toggle will update but, its element keeps its label and traits."

**Critical:** Use the framework styling system (`.toggleStyle`, `.buttonStyle`, etc.) instead of building custom views from scratch. Custom views require you to manually re-add accessibility info.

### 5.3 The `accessibilityElement(children: .combine)` Pattern

For card-like rows (label + icon + actions), combine into one element:

```swift
HStack { ... }
.accessibilityElement(children: .combine)
```

VoiceOver navigation goes from "label", "favorite button", "reply button" (3 stops) to one stop with a Custom Actions menu. Massive UX win for lists of items.

### 5.4 The Conditional Modifier (NEW in iOS 18)

```swift
.accessibilityLabel("Super favorite", isEnabled: isSuperFavorite)
```

When the condition is false, the modifier doesn't apply -- letting SwiftUI fall back to the default symbol label. This is the right pattern for symbols whose meaning changes contextually.

### 5.5 The `accessibilityActions` Modifier With a View

```swift
Image("trip")
    .accessibilityActions {
        if hasLocation { Button("Location") { ... } }
        if hasRecording { Button("Recording") { ... } }
    }
```

Hover-triggered overlays are slow for VoiceOver users. Lift those buttons into custom actions on the parent element so they're directly available.

### 5.6 The `accessibilityLabel(content:)` Initializer With View

Append computed labels (like a star rating) to existing labels without overriding SwiftUI's auto-generated description:

```swift
.accessibilityLabel { existing in
    HStack { existing; Text("\(rating) stars") }
}
```

### 5.7 Drag and Drop Accessibility

Default `.onDrag`/`.onDrop` works, but for views with **multiple drop points** in a single view (custom drop delegates), VoiceOver only sees one. Add `.accessibilityDragPoint` and `.accessibilityDropPoint` to expose each:

```swift
.accessibilityDropPoint(.top, label: "Set sound 1")
.accessibilityDropPoint(.center, label: "Set sound 2")
.accessibilityDropPoint(.bottom, label: "Set sound 3")
```

### 5.8 Widget Accessibility Actions With App Intents

Widgets can't update views in real time, so the `.accessibilityAction` modifier accepts an `AppIntent`:

```swift
.accessibilityAction(.magicTap, intent: TakePhotoIntent())
.accessibilityAction(named: "Set as favorite", intent: SetFavoriteIntent(beach: ...))
```

The intent runs and the widget refreshes. **The right pattern for accessible widgets in iOS 18.**

---

## 6. Dynamic Type (WWDC24-10074)

### 6.1 The Five Sizes Above Default

iOS supports XS / S / M / L (default) / XL / XXL / XXXL **AND** five accessibility sizes (AX1...AX5). At AX5, text can be 5x larger than default.

### 6.2 Test at AX5 -- It's the Real Compatibility Bar

> "Test at the largest accessibility size (AX5) at minimum -- if your layout works there, it works everywhere."

### 6.3 Use Dynamic Type Sizes in Code

```swift
@Environment(\.dynamicTypeSize) var dynamicTypeSize

if dynamicTypeSize >= .accessibility1 {
    VStack { ... }  // stack vertically at large sizes
} else {
    HStack { ... }  // horizontal at normal sizes
}
```

This is the **adaptive-layout pattern** for handling extreme type sizes.

### 6.4 Custom Fonts -- Use `.scaledFont`

```swift
.font(.custom("MyFont", size: 17, relativeTo: .body))
```

Without `relativeTo`, custom fonts ignore Dynamic Type. The relative-to anchor ties them to the right size class.

### 6.5 The `.dynamicTypeSize(...)` Constraint Modifier

Cap or floor the size for a specific subview:

```swift
TableHeaderView()
    .dynamicTypeSize(...DynamicTypeSize.xxxLarge)  // cap at XXXL even if user set AX5
```

Use sparingly -- usually for tabular content where AX sizes break the layout entirely.

---

## 7. UX Writing (WWDC24-10140)

### 7.1 The Three Principles

1. **Be purposeful** -- every word earns its place
2. **Be specific** -- "Continue" tells you nothing; "Save Photo" tells you everything
3. **Be human** -- write like a thoughtful person, not a system

### 7.2 Replace System Patterns Where They're Wrong

| Generic | Specific |
|---|---|
| "Are you sure?" | "Delete this trail?" |
| "Cancel" / "OK" | "Cancel" / "Delete" |
| "Loading..." | "Finding nearby trails..." |
| "Error" | "Couldn't reach the server. Try again later." |

### 7.3 Voice and Tone Calibration

Different parts of your app have different tones. Onboarding can be playful; error messages should be calm and helpful; settings should be neutral and precise.

### 7.4 Microcopy in Search and Empty States

- Search placeholder: "Search trails by name or city" (not "Search")
- Empty list: "No trails yet. Tap + to add your first one." (not "No data")

---

## 8. Design Live Activities for Apple Watch (WWDC24-10098)

### 8.1 The `.supplementalActivityFamily` Pattern

iOS Live Activities auto-appear on watchOS, but the watch screen is small. Define a supplemental version:

```swift
ActivityConfiguration(...) {
    // your iOS view
} supplementalContent: { context in
    // watch-optimized view
}
```

### 8.2 Watch Live Activity Design Rules

- **Glanceable** -- one piece of information dominates
- **Compact** -- minimum text, maximum icons
- **Hand-friendly** -- support double-tap (`.handGestureShortcut(.primaryAction)`) for the most important action

### 8.3 Use the Reference-Date Format Style

```swift
Text(.referenceDate(myDate, countsDown: true))
```

Live-updating without your code running. Saves battery, reliable. Adapts to container size.

---

## 9. Designing Advanced Games (WWDC24-10085)

### 9.1 The Three Game Categories on Apple Platforms

1. **Casual mobile** -- easy to dip into, simple controls
2. **Console-quality** -- richer experiences, controllers expected
3. **Spatial** -- visionOS-only, gestural and immersive

### 9.2 Console-Quality Mobile Best Practices

- **Default to controller support** -- don't make the user dig in settings
- **Thumb-zone aware UI** for touch fallback
- **HDR rendering** on supported displays
- **Variable refresh rate** integration for ProMotion

### 9.3 Apple Games App (NEW in iOS 18)

A dedicated games hub. Adopt:
- Game Center achievements (drives "challenges" tab)
- Apple Arcade if applicable
- Rich screenshots/preview videos in App Store Connect

---

## 10. Cross-References

For visionOS designers:
1. **WWDC24-10086** (Design great visionOS apps) -- the foundational session
2. **WWDC24-10096** (Interactive visionOS experiences)
3. **WWDC24-10087** (Custom environments) -- when full immersion matters

For App Intents UX:
1. **WWDC24-10176** (Design App Intents)
2. **WWDC24-10210** (Bring core features) -- in the AI/ML cluster

For accessibility:
1. **WWDC24-10073** (SwiftUI accessibility)
2. **WWDC24-10074** (Dynamic Type)
