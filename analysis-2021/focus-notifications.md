# Focus & Notifications (WWDC 2021)

Apple's broadest notification redesign since iOS 8. Introduces system-wide Focus modes, interruption levels, communication notifications, and notification summaries.

## Sessions covered
- WWDC21-10091 — Send communication and Time Sensitive notifications
- WWDC21-10049 — Add intelligence to your widgets
- WWDC21-10048 — Principles of great widgets
- WWDC21-10283 — Design great actions for Shortcuts, Siri, and Suggestions

## Best practices

- **Use the right interruption level. Default is wrong for almost everyone.** Apple specifically calls this out — most apps over-interrupt by default (WWDC21-10091):
  - `.passive` — silent delivery; appears in next list view. Use for digests, recommendations.
  - `.active` — current default behavior. Wakes screen, plays sound. Used by 90% of legacy apps but rarely correct.
  - `.timeSensitive` — breaks through Focus and Notification Summary. Reserved for genuinely urgent: package delivery, account security, transit alerts.
  - `.critical` — bypasses ringer switch. Requires explicit Apple-granted entitlement (severe weather, AMBER, medical).
- **Communication notifications must use `INSendMessageIntent` / `INStartCallIntent`**, donated via `UNNotificationContent.updating(from: intent)` inside a Notification Service Extension. Without this you get a flat "App Name: …" notification with no avatar (WWDC21-10091).
- **Donate both incoming AND outgoing intents** — the system learns who's important from outgoing donations, which then powers the Focus break-through allow-list (WWDC21-10091).
- Provide a **relevance score** on `UNMutableNotificationContent` so the Notification Summary can promote your most important entries to the top slot (WWDC21-10091).

## Hidden gems

- Time Sensitive notifications need an entitlement (`com.apple.developer.usernotifications.time-sensitive` capability), but it's a self-grant via Xcode Capabilities — no review process for the basic level (WWDC21-10091).
- Adding `UNNotificationActionIcon` to a notification action puts a glyph next to it — communicates intent at a glance (WWDC21-10091).
- The "Allow Announcement" category option is **deprecated** in iOS 15. Communication and Time Sensitive notifications now announce by default on AirPods Pro/Max/CarPlay (WWDC21-10091).
- In CarPlay, communication notifications can announce automatically with no extra opt-in — read messages aloud during a drive (WWDC21-10091).
- Widget intelligence: use the new `relevance` API on `TimelineEntry` to declare time/location/activity relevance, and the Smart Stack rotates your widget to the top automatically (WWDC21-10049).
- Widgets can now ship multiple sizes from a single `IntentTimelineProvider`. The same intent handler powers Watch widgets in 2022's complications (WWDC21-10048).

## Migration guidance

- Apps that ship default-active notifications that don't represent urgent communication will be deprioritized by the OS. Audit each notification path and lower most to `.passive` (WWDC21-10091).
- If your app handles voice/video calls, register a CallKit-style `INStartCallIntent` even if you're not using CallKit — Siri uses these donations to populate the Focus exception list (WWDC21-10091).

## Cross-references

- Focus mode developer-side hooks come in iOS 16 (`SetFocusFilterIntent`); 2021's APIs are about producing notifications that Focus can intelligently filter, not configuring Focus itself.
- Communication intents donate the same shapes that 2022's Live Activities and Dynamic Island consume.
