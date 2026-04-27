# Design, SF Symbols & Accessibility (2022)

WWDC22's design lineup focuses on iOS 16's new lock screen, the redesigned iPad multitasking model, the major iPad redesign exemplified by System Settings on macOS Ventura, SF Symbols 4 (with Variable Color), and accessibility advances spanning Quick Actions, audio graphs, and Single App Mode.

## Sessions covered
- WWDC22-10001 — Explore navigation design for iOS
- WWDC22-10009 — What's new in iPad app design
- WWDC22-10015 — Design for Collaboration with Messages
- WWDC22-10037 — Writing for interfaces
- WWDC22-10157 — What's new in SF Symbols 4
- WWDC22-10158 — Adopt Variable Color in SF Symbols
- WWDC22-103 — Apple Design Awards
- WWDC22-110340 — Design an effective chart
- WWDC22-110342 — Design app experiences with charts
- WWDC22-110381 — Meet the expanded San Francisco font family
- WWDC22-10034 — Design for Arabic
- WWDC22-110441 — Design for Arabic · صمّم بالعربي
- WWDC22-10107 — Get it right (to left)
- WWDC22-10110 — Build global apps: Localization by example
- WWDC22-10151 — Add accessibility to your Unity games
- WWDC22-10152 — Create accessible Single App Mode experiences
- WWDC22-10153 — What's new in web accessibility

## Navigation design fundamentals (10001)

### Tab bar guidance
- **Tabs reflect your information hierarchy.** Each tab is a top-level destination.
- **Distribute functionality.** Avoid loading the first tab with everything.
- **Don't make a "Home" tab** that duplicates other tabs' functionality. Creates dissociation between content and how to act on it.
- **Never auto-jump tabs.** Disorienting.
- **Keep tabs persistent.** Don't hide them on push.
- **Clear, concise labels.** Tabs should hint at app purpose without explanation.

### Push vs. modal
- **Push** for moving through hierarchy, frequently-toggled views, anywhere a chevron is shown.
- **Modal** for self-contained tasks (simple, multi-step, or full-screen content). Always present from bottom on iOS. Modal hides the tab bar to enforce focus.

### Modal anatomy
- Right action = preferred action (bold). Should be a concise verb. Inactive until input is provided.
- Left action = "Cancel" — show alert if user has entered data.
- Close (X) symbol: only for content with no input (e.g., articles).
- Limit modals-over-modals. They're sometimes necessary (e.g., adding a photo within an itinerary modal) but jarring otherwise.

## SF Symbols 4 (10157, 10158)

### 700+ new symbols, 4000+ total
New categories:
- Camera & Photos
- Accessibility
- Privacy & Security
- Home (lights, blinds, windows, doors, switches, outlets)
- Fitness (figures)
- Currency (expanded)

### Variable Color (the major new feature)
Symbols with sequential paths (waves, bars, signal strength) can now be rendered at any value 0–1. Used for volume, signal, capacity, etc. Available in **all four rendering modes** (monochrome, hierarchical, palette, multicolor).

```swift
Image(systemName: "speaker.3.wave.fill", variableValue: 0.6)
```

Layers either opt-in or opt-out of Variable Color. Designer chooses the grouping (e.g., "outer waves first, then inner waves" for a signal symbol).

### Automatic rendering mode
Previously: monochrome unless you specified. Now: each symbol has a **preferred rendering mode**. Use `.preferringMonochrome()` to force monochrome when needed (e.g., small symbols on low-contrast backgrounds).

### Unified annotations
For custom symbols, you now annotate **once** for all rendering modes. Use **Draw** vs. **Erase** layer options to control how overlapping shapes render — e.g., make the plus shape erase into the badge to get a punched-out look.

### Hierarchical and Palette
- **Hierarchical** — single hue with depth. Foreground/background distinction.
- **Palette** — multiple distinct colors per layer. For prominence.
- **Multicolor** — intrinsic colors of the represented object.

## Charts as design (110340, 110342)

The design sessions complement the engineering sessions (10136, 10137):
- Choose the chart type that matches the question being answered. Bar for comparison, line for trends, area for cumulative, scatter for correlation.
- **Annotation** is critical — a chart without labels is uninterpretable. Use `chart` modifiers for axis tick formatting, legends, and value annotations.
- **Color contrast** must work in both light and dark mode. Use system semantic colors.
- **Sonification (audio graphs)** is automatic in Swift Charts — provide good `.value(_:_:)` descriptions.

## San Francisco font family (110381)
- New widths: **Compressed** (densest), Condensed, Standard, Expanded.
- Designed for use in tight spaces (sports scores, headlines) and for visual balance.
- Always available via `Font` APIs without manual font registration.

## Right-to-left and Arabic design (10034, 10107, 110441)
- **Mirror layouts** for RTL — push transitions flip direction, navigation paths reverse.
- **Don't mirror** content that has direction (clocks, charts, video controls), iconography that doesn't have a directional analog (camera, microphone), or numbers.
- **Test with pseudo-locales** in Xcode (Edit Scheme → Run → Options → App Language).
- **Arabic-specific design** considerations: right-to-left number/punctuation handling, custom typography for the Arabic script, native-feeling layouts beyond just mirroring.

## Localization by example (10110)
- **Use semantic resources** (`String(localized:)`, not raw strings).
- **Format numbers, dates, currencies** through `.formatted()` — never manual string concatenation.
- **Pseudolocalize early** — find layout breaks before they ship.
- **Pluralization via `.stringsdict`** — required for grammatically correct plurals in many languages.
- **Test with bidirectional locales, not just RTL** — most real-world apps mix scripts.

## Accessibility (10151, 10152, 10153)

### Single App Mode (10152)
For kiosks, museums, point-of-sale: lock the device to a single app. New iOS 16 APIs let your app:
- Detect Single App Mode is active and adapt UI.
- Auto-restart on crash.
- Customize what's accessible (no Control Center, no Notification Center).
- Provide accessible interactions for visitors who can't use standard touch.

### Web accessibility (10153)
Safari and WKWebView updates:
- New ARIA attribute support (e.g., `aria-description`, `aria-current`).
- Improved table semantics.
- Better Live Region announcements.
- Enhanced focus management for SPA navigation.

### Quick Actions (covered in widgets/10133)
Hand-clench gesture on Apple Watch invokes a primary action. Wire up via `.handGestureShortcut(.primaryAction)` modifier. **Quick Actions for accessibility** lets users with limited mobility perform an action without touching the watch.

### Unity accessibility (10151)
Apple's Unity plug-in now exposes Unity GameObjects to VoiceOver/Switch Control with attributes for label, value, and traits. Build game UIs that are accessible by default.

## Writing for interfaces (10037)
- Be **concise.** "Save" not "Save changes to your document."
- Be **clear.** Avoid jargon, technical terms, internal codenames.
- Use **active voice.** "Send a message" not "A message can be sent."
- Use **consistent terminology** throughout the app — don't say "delete" in one place and "remove" in another for the same action.
- **Sentence-style capitalization** for buttons and labels (except titles where appropriate).
- **Avoid placeholder text as labels** — users lose context when they start typing.

## Best practices
- **BEST PRACTICE**: Variable Color is opacity-based, available in all four rendering modes. Use for inherently sequential symbols (waves, bars, layers).
- **BEST PRACTICE**: Always test apps in pseudo-locale early to catch layout breaks.
- **BEST PRACTICE**: For RTL, mirror layout but NOT content with intrinsic direction (clocks, charts, numbers).
- **BEST PRACTICE**: Use semantic system colors (`Color.accentColor`, `.primary`, `.secondary`) — they adapt to dark mode and Increase Contrast accessibility settings.
- **HIDDEN GEM**: SF Symbols' "Automatic" rendering mode picks the right rendering per-symbol — can vary across your UI. Override only when contextually necessary.
- **HIDDEN GEM**: New SF Symbols Categories include Privacy & Security and Accessibility — use them rather than rolling your own iconography.
- **HIDDEN GEM**: `String(localized:)` and `.formatted()` are the only correct way to handle text — never concatenate.
- **URGENT**: Hide the close (X) symbol in modals that require input — users won't know whether close means save or cancel.

## Cross-references
- SF Symbols 4 supports Variable Color used by widgets (10050) for accessory presentations.
- Writing for interfaces (10037) pairs with Localization by example (10110) for international UX.
- Charts design (110340, 110342) builds on the engineering sessions (10136, 10137).
- iPad design (10009) directly informs the SwiftUI on iPad sessions (10058, 110343).
