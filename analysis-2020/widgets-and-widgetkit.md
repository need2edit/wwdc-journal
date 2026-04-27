# WWDC 2020 — WidgetKit Debut & Home-Screen Widgets

WidgetKit was one of the headline 2020 announcements: glanceable widgets on the iOS Home Screen, the iPad Today view, and macOS Big Sur Notification Center. Built **entirely in SwiftUI**, with a timeline-based, declarative data model that's distinct from "mini-apps."

## Sessions Analyzed
- 10028 — Meet WidgetKit (gateway)
- 10033 — Build SwiftUI views for widgets
- 10103 — Design Great Widgets
- 10034 — Widgets Code-along, part 1: The adventure begins
- 10035 — Widgets Code-along, part 2: Alternate timelines
- 10036 — Widgets Code-along, part 3: Advancing timelines
- 10194 — Add configuration and intelligence to your widgets
- 10046 — Create complications for Apple Watch (companion timeline model)
- 10048 — Build complications in SwiftUI
- 10049 — Keep your complications up to date
- 10100 — Meet Watch Face Sharing

## The Three Pillars of a Great Widget

Apple framed widgets around three goals:
1. **Glanceable** — content is the focus, not chrome. No scrolling, no buttons, no controls inside the widget.
2. **Relevant** — the right widget surfaces at the right time via Smart Stacks + on-device intelligence.
3. **Personalized** — three sizes (small/medium/large), and configurable via Intents.

Critical mental shift: **widgets are not mini-apps**. No interactive elements, no scrolling, no animated images, no videos. Think of a widget as "projecting content from your app onto the Home Screen."

## Architecture: Timeline-Based, Built on Complications Lessons

The design is borrowed from watchOS complications: a widget extension is a **background extension** that returns a **timeline of view hierarchies**. The system serializes these views to disk and renders them at the right time without launching your extension repeatedly.

This is what makes widgets fast: no spinner, no app launch, no fetch — pre-rendered views ready to display the moment the user goes Home.

### Defining a Widget

Four required pieces:
- `kind` — string ID; one extension can supply multiple kinds (Stocks Overview vs. Stocks Detail).
- `configuration` — `StaticConfiguration` (no user choice) or `IntentConfiguration` (user picks via Intents framework).
- `supportedFamilies` — defaults to all (small, medium, large). Specify only the ones that make sense.
- `placeholder` view — shown while the extension is being asked, on the lock screen, in the Widget Gallery preview. **Must be content-shape representative, never user data.**

### TimelineProvider Protocol

The engine of every widget. Three callbacks:
1. **`placeholder(in:)`** — instant fallback view (blank-state representation).
2. **`getSnapshot(in:completion:)`** — single entry, returned ASAP. Used in the Widget Gallery so users see your real widget when adding it.
3. **`getTimeline(in:completion:)`** — array of `TimelineEntry` values + a **reload policy**.

```swift
struct Provider: TimelineProvider {
  func getTimeline(in context: Context, completion: @escaping (Timeline<Entry>) -> Void) {
    let entries: [Entry] = makeEntries()
    let timeline = Timeline(entries: entries, policy: .atEnd)
    completion(timeline)
  }
}
```

Reload policy options:
- `.atEnd` — system asks for a new timeline when the last entry is reached
- `.after(date)` — system asks at a specific date
- `.never` — only your app explicitly forces a reload

The system uses this policy as a **hint** plus signals like "viewed frequently" to decide when to actually wake your extension.

### Reloads from the Host App

`WidgetCenter.shared.reloadAllTimelines()` or `reloadTimelines(ofKind:)` from your main app or background URLSession events. Background URL sessions deliver via the `onBackgroundURLSessionEvents` modifier on the widget configuration.

**Be judicious** — every reload costs energy budget. Only reload when your widget's content actually changed.

## Building the View — SwiftUI Only

This is the first major Apple feature where SwiftUI is **mandatory**. AppKit and UIKit cannot supply widget views. The widget extension itself can be in a Swift, AppKit, or Catalyst app, but the views are SwiftUI.

### New SwiftUI APIs Targeted at Widgets

`ContainerRelativeShape` — a shape type that adopts the path/corner radius of the **nearest container shape**. The system defines the widget's container; you get concentric rounded rects automatically as padding changes. **Critical** for proper widget design — hardcoded `.cornerRadius(12)` will break across device shapes/sizes.

`Text(date, style: .relative)` / `.timer` / `.date` / `.time` / `.offset` — date-driven text that **updates automatically** as time passes. This is how widgets feel alive without your extension running every second. Examples: "5m ago", a countdown timer, a relative-date label.

`Link` view — opens a URL when tapped. In a widget it can deep-link back into your app. `widgetURL(_:)` modifier sets a URL for the entire widget area; `Link` lets you create sub-targets in medium/large sizes.

### View Sizing for the Three Families

- `systemSmall` — single tap target, the entire widget. Simple data, single deep link.
- `systemMedium` — multiple tap targets via `Link`. Good for showing 3-4 items.
- `systemLarge` — full content view, multiple `Link` targets.

### Placeholder UI in iOS 14

`isPlaceholder(true)` modifier (available in a later seed of iOS 14): SwiftUI auto-replaces `Text` with rounded rectangles of representative shape. Apply `isPlaceholder(false)` to specific views to keep them visible. Image content auto-replaces with fill color.

### Dark Mode and Dynamic Type

Free if you use asset-catalog colors with dark variants and rely on system fonts. The samples emphasize: **build small, accessible, and Dark-Mode-correct from the start** — the placeholder system depends on it.

## IntentConfiguration & Personalization

For widgets the user can configure (e.g., "Which city's weather?"), use `IntentConfiguration` with a custom `INIntent`. The Intents framework auto-generates the entire configuration UI. Dynamic options (e.g., user's saved cities) come from your existing Intent extensions or from the **new in-app Intent handling** introduced in iOS 14.

```swift
IntentConfiguration(
  kind: "WeatherWidget",
  intent: SelectCityIntent.self,
  provider: Provider()
) { entry in
  WeatherView(entry: entry)
}
```

The TimelineProvider becomes `IntentTimelineProvider` and is passed the resolved Intent in `getTimeline`.

## Smart Stack Intelligence

Two ways to feed the system's "which widget should be on top right now?" decision:
- **Siri Shortcut donations** in your main app — when the user does X, donate the same `INIntent` your widget uses. The system learns the time/place patterns.
- **`TimelineEntryRelevance(score:duration:)`** — annotate timeline entries with relative importance scores. Score is a `Float` relative to all entries you've ever provided; `duration` is when this entry's relevance applies.

The Smart Stack rotates to your widget when its relevance is high relative to siblings. Don't game the score — your widget gets demoted if users dismiss it repeatedly.

## Widget Code-Along Series Highlights

The three-part code-along (sessions 10034, 10035, 10036) walks from a `StaticConfiguration` to an `IntentConfiguration` with personalization. Key practical takeaways:

- The widget extension target is created via Xcode's "Widget Extension" template (with or without "Include Configuration Intent").
- The widget runs in a sandboxed extension process — no shared state with the main app except via App Groups (`UserDefaults(suiteName:)`).
- Networking should use background URLSessions; timeline entries are returned via the completion handler.
- Test in Simulator with multiple sizes via the preview canvas.

## watchOS Complications: Same Mental Model, Older API

ClockKit got significant additions for watchOS 7:
- **Multiple complications per app** — `getComplicationDescriptors(handler:)` returns a list of `CLKComplicationDescriptor` (identifier, displayName, supportedFamilies, optional userInfo or userActivity).
- **SwiftUI in complications** — all `CLKFullColorImageProvider`-based templates have SwiftUI alternatives. Reuse view code from the main app.
- **Graphic Extra Large family** for the new Extra Large face.
- Always handle the `CLKDefaultComplicationIdentifier` — a user with the complication on their face from before watchOS 7 (or after sharing a watch face without the data) gets queried for it. Don't break.

### Watch Face Sharing (10100)

Brand new in watchOS 7: faces share via Messages, Mail, websites, NFC tags, QR codes. Developers can prompt users from inside their app:

```swift
CLKWatchFaceLibrary().addWatchFace(at: url) { error in ... }
```

The watch face file includes:
- All face configuration (color, style, photos, complications)
- A sample timeline entry from your complication so it previews even before the user installs your app
- userInfo dictionary contents (be careful not to leak personal data)

Best practices:
- Your app must be published to the App Store before the file references your complication.
- Use `WCSession` to detect a paired watch before offering face sharing in your iOS app.
- Provide a fallback face for Apple Watch Series 3 (some new faces aren't compatible).
- Email yourself a face to extract its preview image — that's the recommended way to get the asset for your in-app UI.
- Web hosting: serve files with the watch-face MIME type so Safari recognizes them.

## Cross-References
- [swiftui-2-foundation.md](swiftui-2-foundation.md) — widgets are SwiftUI-only; the new Apps/Scenes architecture is the same year.
- [siri-intents-shortcuts.md](siri-intents-shortcuts.md) — IntentConfiguration uses the same Intents framework as Shortcuts.
- [watchos-7.md](watchos-7.md) — for complications and the wider watchOS 7 changes.
- [big-sur-design-system.md](big-sur-design-system.md) — widgets in macOS Big Sur Notification Center.

## Adoption Checklist
- [ ] Identify which "kinds" of widget make sense — don't ship everything at once.
- [ ] For each kind, decide Static vs. Intent configuration.
- [ ] Decide which `supportedFamilies` make sense per kind.
- [ ] Build the SwiftUI view; test in placeholder mode + Dark Mode + larger Dynamic Type.
- [ ] Implement a sensible TimelineProvider with realistic reload policy.
- [ ] Wire up Smart Stack intelligence via Intent donations or `TimelineEntryRelevance`.
- [ ] Use `widgetURL` and `Link` for tap targets; deep-link into your app.
- [ ] If you have complications too, audit for `CLKDefaultComplicationIdentifier` handling.
