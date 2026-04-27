# Lock Screen Widgets, Complications & watchOS (2022)

iOS 16's redesigned Lock Screen brought widgets to the lock screen for the first time, and watchOS 9 finally unified complications with WidgetKit. After years of dragging two separate frameworks (ClockKit + WidgetKit), Apple reimagined complications **as widgets**, with a single shared codebase between iOS and watchOS.

## Sessions covered
- WWDC22-10050 — Complications and widgets: Reloaded
- WWDC22-10051 — Go further with Complications in WidgetKit
- WWDC22-10142 — Efficiency awaits: Background tasks in SwiftUI
- WWDC22-10133 — Build a productivity app for Apple Watch
- WWDC22-10135 — Get timely alerts from Bluetooth devices on watchOS
- WWDC22-110384 — Support multiple users in tvOS apps

## The new accessory widget families (10050)

WidgetKit added five new families, prefixed `accessory`:

| Family | Where it appears |
|--------|------------------|
| `accessoryRectangular` | iOS Lock Screen, watchOS rectangular complications |
| `accessoryCircular` | iOS Lock Screen, watchOS circular complications (replaces ClockKit `graphicCircular`) |
| `accessoryInline` | iOS Lock Screen above the time, watchOS inline complications |
| `accessoryCorner` | watchOS only — corner complications with gauges/text |

iOS Home Screen widgets (`systemSmall`, `systemMedium`, `systemLarge`) and the new accessory families share the same codebase. **You can deliver widgets and complications from one widget extension.**

## Three rendering modes (10050)

The system can render your widget in three ways:

- **`.fullColor`** — your view rendered exactly as specified (Home Screen, watch full-color faces).
- **`.accented`** — views split into two color groups, flatly tinted by the system. Use `.widgetAccentable()` to mark which views go in the "accent" group (vs. default).
- **`.vibrant`** — desaturated, drawn as a material on the Lock Screen. Adapts to background and tint color.

Read the current mode from the environment:
```swift
@Environment(\.widgetRenderingMode) var renderingMode
```

### CRITICAL design constraint
In `.vibrant` mode, **avoid transparent colors**. The system maps grayscale to material opacity. Use darker colors (or black) to indicate less prominent content while maintaining legibility — transparency just makes things invisible.

### `AccessoryWidgetBackground`
A new view that gives a consistent backdrop behavior across rendering modes — soft transparency in fullColor/accented, solid black in vibrant. Use it when your widget needs visual containment (e.g., a calendar with grid lines).

## Always-on display support (10050)

Apple Watch Series 5+ stays on continuously, transitioning to a low-luminance state when not actively in use. Read `\.isLuminanceReduced` from the environment:

```swift
@Environment(\.isLuminanceReduced) var isReduced
```

In always-on:
- Time-relative text and progress views switch to a reduced-fidelity update cadence.
- Remove time-sensitive content that's not relevant when glanced at.
- Auto-updating views like `Text(_:date:)` and `ProgressView(timerInterval:)` work correctly with the reduced cadence — prefer them over manual timeline updates with many entries.

### Privacy redaction
Lock Screen and always-on both can redact your widget content. Use `.privacySensitive()` on individual subviews to redact only sensitive parts:

```swift
HStack {
  Image("heart").privacySensitive()
  Text("\(heartRate) BPM").privacySensitive()
  Image("watch")  // not redacted
}
```

## Auto-updating views (10050)

Critical for accessory widgets given their tiny update budget:
- `ProgressView(timerInterval: startDate...endDate)` — auto-progressing ring, no timeline entries needed.
- `Text(_:style:.timer)` — counts up/down without re-rendering.
- `Text(_:date:.relative)` — "5m ago" updates automatically.
- `ViewThatFits` — pick the version of your widget that fits the slot. Critical for `accessoryInline` slots which differ in width.

## Recommended fonts (10050)

The system uses different font designs:
- **iOS**: regular text design.
- **watchOS**: rounded, heavier weight.

Use the standard text styles (`.headline`, `.body`, `.caption`, `.title`) — never hardcode font sizes. This ensures your widget sits consistently next to others.

## Background tasks reimagined for SwiftUI (10142)

A new unified API across watchOS, iOS, tvOS, Mac Catalyst, and widgets. Built on Swift Concurrency.

### The new `backgroundTask` scene modifier
```swift
WindowGroup { ContentView() }
  .backgroundTask(.appRefresh("StormCheck")) {
    await scheduleNextAppRefresh()
    if await isStormy() {
      await notifyForPhoto()
    }
  }
  .backgroundTask(.urlSession("StormDownload")) { ... }
```

The closure runs in the background; when it returns, the system suspends the app. Swift Concurrency's task cancellation gives you graceful "time is running out" handling — when you receive a cancellation, promote your immediate work into a true background `URLSession` task that survives suspension.

### `withTaskCancellationHandler` pattern for network requests
```swift
return await withTaskCancellationHandler {
  try await urlSession.data(from: weatherURL)
} onCancel: {
  let downloadTask = urlSession.downloadTask(with: weatherURL)
  downloadTask.resume()  // continues even after suspension
}
```

URLSession deduplicates the same in-process request, so this isn't a double network hit.

### watchOS-specific
**On watchOS, ALL background network requests must use a background URLSession** with `sessionSendsLaunchEvents = true`. This is not optional — the watch is too power-constrained for foreground-style background networking.

## productivity-app patterns (10133)

For Apple Watch productivity apps:
- Use `TextFieldLink` for text input (since you can't type on watch).
- `Chart` works on watchOS — small charts can give surprisingly informative glances.
- `ShareLink` is now available on watchOS 9 — present the system share sheet from your watch app.
- `Stepper` is now available on watchOS, including with formatted values.

### Quick Actions
Apple Watch supports "Quick Actions" — a hand-clench gesture that triggers an action. Define it the same way as a button:
```swift
.handGestureShortcut(.primaryAction)
```
Now your existing button has a hands-free invocation path.

## Best practices
- **BEST PRACTICE**: Use auto-updating views (`ProgressView(timerInterval:)`, `Text(_:date:)`, `Text(_:style:.timer)`) instead of multiple timeline entries — they work in always-on with reduced fidelity automatically.
- **BEST PRACTICE**: Always test all four states: full color × normal/redacted, vibrant × normal/redacted. Users can configure redaction per face/Lock Screen.
- **BEST PRACTICE**: Use standard text styles (`.headline`, `.body`, `.caption`) — they pick the right font design per platform.
- **HIDDEN GEM**: `ViewThatFits` is essential for `accessoryInline` widgets — provide multiple versions from longest to shortest.
- **HIDDEN GEM**: `backgroundTask(.urlSession:)` and `backgroundTask(.appRefresh:)` modifiers replace `WKApplicationDelegate` background hooks on watchOS — finally a SwiftUI-native API.
- **URGENT**: Any background network request on watchOS MUST go through a background `URLSession` with `sessionSendsLaunchEvents = true` — foreground sessions are silently killed when the watch sleeps.
- **PERFORMANCE**: `URLSession` deduplicates requests in process, so promoting an in-flight request to a background download task in `onCancel` doesn't double-request.

## Cross-references
- Widget data models often serialize through Transferable (10062) for sharing.
- Widget configuration uses App Intents (10032) — the new IntentRecommendation API surfaces fixed configurations on watchOS.
- For complex layouts, use the Layout protocol (10056).
- Focus Filters (10121) can adjust which widget content is shown.
