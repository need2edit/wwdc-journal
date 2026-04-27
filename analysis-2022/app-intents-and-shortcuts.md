# App Intents, Focus Filters & Shortcuts (2022)

WWDC22 introduced the App Intents framework — Apple's modern, Swift-only replacement for SiriKit Intents. It powers Siri, Spotlight, Shortcuts, Focus filters, and the new Visual Lookup integrations. The headline feature: **App Shortcuts** require zero user setup, exposing your app's functionality the moment it's installed.

## Sessions covered
- WWDC22-10032 — Dive into App Intents
- WWDC22-10169 — Design App Shortcuts
- WWDC22-10170 — Implement App Shortcuts with App Intents
- WWDC22-10121 — Meet Focus filters

## App Intents architecture (10032)

### Three core concepts
- **Intent** — a single, isolated unit of functionality (`AppIntent` protocol).
- **Entity** — a concept your app exposes (`AppEntity` protocol). Used when values are dynamic (books, notes, photos). `AppEnum` for fixed sets.
- **App Shortcut** — wraps an intent with phrases and parameter mappings to make it instantly available to Siri/Spotlight/Shortcuts.

### Why this is a step-change from SiriKit
- **Code-only.** No `.intentdefinition` files. The compiler statically extracts metadata at build time into a JSON sidecar inside your app/extension bundle.
- **No app re-architecture required.** No extension required, no separate framework. Implement intents directly in your main app target.
- **Higher memory limits when running in app process.** Background-launched apps run in a special mode without scenes.

### A minimal intent
```swift
struct OpenCurrentlyReading: AppIntent {
    static var title: LocalizedStringResource = "Open Currently Reading"

    @MainActor
    func perform() async throws -> some IntentResult {
        Navigator.shared.open(.currentlyReading)
        return .result()
    }
}
```

That's it. The intent now appears in the Shortcuts editor automatically.

### Parameters and entities
```swift
@Parameter(title: "Shelf") var shelf: Shelf

static var parameterSummary: some ParameterSummary {
    Summary("Open \(\.$shelf)")
}
```

`@Parameter` is a Swift property wrapper (this kind of API requires the latest Swift property-wrapper, result-builder, and generics features). `parameterSummary` controls the Shortcut UI rendering — **always provide one**, otherwise your action looks bare.

### Property queries: free Find & Filter actions
This is the most underrated feature of App Intents. By implementing `EntityPropertyQuery`, you get `Find Books`, `Filter Books`, `Sort by` and `Limit` actions in Shortcuts **for free**, with a flexible predicate editor UI. You declare:
1. `static var properties: QueryProperties` — which properties are queryable and which comparators (`.contains`, `.equalTo`, `.lessThan`).
2. `static var sortingOptions: SortingOptions` — sortable properties.
3. `entities(matching:)` — runs the actual query.

Map each comparator combination to your own type — `NSPredicate` if you use Core Data, custom REST query types otherwise.

### User interaction patterns
- **Dialog** — text/voice feedback. Use `IntentDialog` for results.
- **Snippets** — visual SwiftUI views shown alongside results. Same constraints as widgets (no interactivity, no animations).
- **`requestValue`** — ask for a missing parameter value.
- **`requestDisambiguation`** — pick from a fixed list.
- **`requestConfirmation`** — confirm before executing destructive intents like placing orders.

### `openIntent` for "open after run"
Return another `AppIntent` as the `openIntent` of your result. Users get a "Open When Run" toggle in Shortcuts. If on, the second intent runs after yours finishes — typically pushing a UI screen.

## App Shortcuts (10170)

### Zero-setup
The huge win: with `AppShortcutsProvider` in your app, your shortcuts ship pre-configured with your app. Users can say "Start a meditation" with zero setup. No more "Add to Siri" button required.

```swift
struct MeditationShortcuts: AppShortcutsProvider {
    static var appShortcuts: [AppShortcut] {
        AppShortcut(
            intent: StartMeditationIntent(),
            phrases: [
                "Start a \(.applicationName) session",
                "Begin meditating with \(.applicationName)"
            ]
        )
    }
}
```

### Critical phrase rule
**Every phrase MUST contain `.applicationName`** — Siri uses your app name (and any synonyms from `INAlternativeAppNames` in Info.plist) to disambiguate which app the user means. Without it, the system rejects the phrase.

### Parameterized phrases
```swift
"Start a \(\.$session) \(.applicationName)"
```

Combined with `suggestedEntities()` returning your top sessions, this expands at runtime to "Start a calming meditation," "Start a walking meditation," etc.

**Critical caveat:** Parameterized phrases require your app to have launched at least once and called `updateAppShortcutParameters()`. Always include some non-parameterized fallback phrases or else first-launch users won't see your shortcuts at all.

### Limits
- Maximum **10 App Shortcuts** per app.
- The first phrase in your array is the "primary phrase" — used as the Spotlight tile label.
- The order of `appShortcuts` controls display order in Shortcuts and Siri.

### Discoverability surfaces
- **`SiriTipView`** (SwiftUI) and `SiriTipUIView` (UIKit) — replaces the Add to Siri button. Show contextually after a relevant action (e.g., after placing an order, hint at the "Order Status" shortcut).
- **`ShortcutsLink`** — opens the Shortcuts app to a list of your app's shortcuts.

### Custom UI in Siri
You can return a SwiftUI view from any of three phases: value confirmation, intent confirmation, and post-completion. Same constraints as widgets — no interactivity. The view is archived and presented in Siri's snippet area.

## Focus filters (10121)

Focus filters let users customize how your app behaves per Focus mode (Work, Personal, Sleep, etc.). Calendar uses this to filter which calendars are visible; Mail uses it to limit notifications.

### How they work
Implement `SetFocusFilterIntent` (a kind of App Intent). Declare `@Parameter`s that the user can configure per Focus. The system surfaces these in Focus settings and calls your `perform()` whenever the active Focus changes.

```swift
struct ChatFocusFilter: SetFocusFilterIntent {
    static var title: LocalizedStringResource = "Filter Chat by Account"

    @Parameter(title: "Account") var account: AccountEntity?
    @Parameter(title: "Always Use Dark Mode") var alwaysUseDarkMode: Bool = false

    func perform() async throws -> some IntentResult {
        // Update app to reflect this Focus
    }
}
```

### App vs. extension
If your filter only updates UI inside the app, you can implement `perform()` in the app target. If it needs to update widgets, badges, or notification filtering even when the app isn't running, build an App Intents extension.

### Notification filtering
Return an `AppContext` from `perform()` (or invalidate it later) with a `filterPredicate`. Set `filterCriteria` on outgoing local/push notifications. If they don't match the predicate, the notification is silenced. The criteria is also a string field on the APS payload for remote notifications.

### Updated badge API
`UNUserNotificationCenter.current().setBadgeCount(_:)` replaces the old direct `applicationIconBadgeNumber` mutation, and is what you call from the Focus filter to surface only Focus-relevant counts.

## Best practices
- **BEST PRACTICE**: Always provide a `parameterSummary` for every intent — without one, the Shortcuts UI is unattractive.
- **BEST PRACTICE**: Adopt `EntityPropertyQuery` even if you don't think you need it — you get free Find/Filter/Sort actions.
- **HIDDEN GEM**: App Intents in your main app target get higher memory limits than in an extension; only move to extension if you need Focus filters or want lightweight launch.
- **HIDDEN GEM**: For the upgrade path from SiriKit, click the "Convert to App Intent" button in your `.intentdefinition` file. SiriKit Intents stays for messaging/payments domains; App Intents replaces all custom intents.
- **URGENT**: Every App Shortcut phrase must include `\(.applicationName)`. The system rejects phrases without it.
- **URGENT**: `setBadgeCount(_:)` replaces the deprecated `applicationIconBadgeNumber` setter pattern when used with Focus filters.

## Cross-references
- Pairs with Lock Screen widgets (10050, 10051) — both surface lightweight content based on context.
- App Intents extensions are scheduled by `dasd`, similar to how background tasks (10142, 110403) are scheduled.
- Visual Look Up / Live Text (10025, 10026) integrate with App Intents via the share sheet and Spotlight.
