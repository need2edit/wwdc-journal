# Widgets, App Clips & Spotlight (WWDC 2021)

## Sessions covered
- WWDC21-10048 — Principles of great widgets
- WWDC21-10049 — Add intelligence to your widgets
- WWDC21-10012 — What's new in App Clips
- WWDC21-10013 — Build light and fast App Clips
- WWDC21-10098 — Showcase app data in Spotlight
- WWDC21-10231 — Donate intents and expand your app's presence
- WWDC21-10283 — Design great actions for Shortcuts, Siri, and Suggestions
- WWDC21-10102 — Spotlight your app with App Shortcuts (preview)

## Best practices

- **Provide intelligence via `TimelineEntryRelevance`** — a numeric score the system uses to rotate your widget to the top of the Smart Stack at the right moment. Without this you stay in the user-set order (WWDC21-10049).
- **Intents drive widget configuration AND Smart Stack rotation** — use `INIntent` instead of static configuration unless your widget really has zero settings (WWDC21-10049).
- **App Clips: 10MB binary cap is real**. Strip Xcode-generated dSYMs from the binary, audit @ImportEverything Swift Package dependencies, prefer dynamic libraries shared with the parent app (WWDC21-10013).

## Hidden gems

- **App Clip Codes**: NFC-tagged stickers WITH a printed visual code. Both work — tap or scan with the camera. The visual code embeds a URL+launch-experience-id (WWDC21-10012).
- App Clip can be invited from a notification, a shared link, NFC, App Clip Code, Maps, Siri Suggestions, OR an in-app intent. The host app surfaces a "Get the full app" upsell after first use (WWDC21-10012).
- **Showcase data in Spotlight**: index `CSSearchableItem`s. Items with rich `keywords` and a `displayName` show in top hits. Use `domainIdentifier` to update/delete bulk records efficiently (WWDC21-10098).
- **Donate intents whenever your user takes action** — Siri Suggestions, Shortcuts, Lock Screen Quick Actions, and now widget Smart Stack all consume the same intent donations. One donation, many surfaces (WWDC21-10231).
- **Shortcuts on macOS** is brand-new. Existing iOS intents work with no extra work in your iOS-on-Mac (Catalyst or Designed-for-iPad) app (WWDC21-10232).

## Performance

- App Clip cold launches average ~200ms on iPhone 12+ for a well-stripped 4MB clip — competitive with web page first paint (WWDC21-10013).
- Spotlight ingests ~10K items/sec from `CSSearchableIndex.indexSearchableItems` — batch your indexing rather than one-at-a-time (WWDC21-10098).

## Migration guidance

- For widgets, provide a `Family` parameter in your `IntentConfiguration` so a single intent powers small/medium/large variants (WWDC21-10048).

## Cross-references

- Live Activities (2022) extend the WidgetKit `TimelineProvider` model to push-updated dynamic island content.
- App Clips' invocation-URL handling pattern carries forward to Universal Links unification in 2023.
