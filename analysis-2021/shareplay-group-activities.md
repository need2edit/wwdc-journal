# SharePlay & Group Activities (WWDC 2021)

A brand-new framework that turns FaceTime calls into the host shell for shared experiences across iOS/iPadOS/macOS/tvOS/Web. Heavily integrated with AVFoundation for synced playback.

## Sessions covered
- WWDC21-10183 — Meet Group Activities
- WWDC21-10184 — Design for Group Activities
- WWDC21-10187 — Build custom experiences with Group Activities
- WWDC21-10189 — Coordinate media playback in Safari with Group Activities
- WWDC21-10225 — Coordinate media experiences with Group Activities

## Best practices

- **Every Play button in your media app should be a SharePlay touchpoint.** When a user is in a FaceTime session, tapping Play should trigger `prepareForActivation()` automatically — Apple wants ubiquity (WWDC21-10183).
- **Always call `prepareForActivation()` first**, not `activate()`. The system shows the user a sheet asking whether to share with the group or play locally. This consent step is mandatory and prevents surprising the user (WWDC21-10183, WWDC21-10184).
- **Use the GroupSession messaging channel only for small sync data** (play/pause/seek commands, drawing strokes). Apple's media sync does NOT proxy your actual content — your servers still stream the bits (WWDC21-10183).
- **Don't add FaceTime UI inside your app.** Communication is a system-level layer; just adopt the framework and the dynamic island/system UI handles voice, video, and presence overlays (WWDC21-10183, WWDC21-10184).

## Hidden gems

- The GroupSession messaging channel is **end-to-end encrypted, even from Apple**. The framework explicitly states "no one other than your application on the device can read the data" (WWDC21-10183).
- `AVPlaybackCoordinator` automatically handles play/pause/seek sync if you wire your `AVPlayer` to the `GroupSession` (WWDC21-10183).
- For non-AVPlayer media engines, conform to `AVPlaybackCoordinatorPlaybackControlDelegate` and you still get sync messaging — your custom HLS engine, web video, or game can adopt this (WWDC21-10183, WWDC21-10225).
- **Smart volume**: when someone in the call speaks, the system automatically ducks media audio and brings it back when speech stops. Free for any AVPlayer-based app (WWDC21-10183).
- `GroupSession.activeParticipants` is an async sequence — observe joins/leaves with `for await participants in session.$activeParticipants.values { … }` (WWDC21-10187).
- `GroupSession.send(_:to:)` lets you target specific participants for partial-state sync (e.g., catch a late joiner up) (WWDC21-10187).
- The framework is available in **Safari (WebKit) on macOS** for HTML5 video — you can keep your web player and still get SharePlay sync (WWDC21-10189).
- A single `GroupSession` works across the user's *own* devices simultaneously — the same person can hand off the experience from iPhone → AppleTV without ending the activity (WWDC21-10183).

## Performance

- Sync uses NTP-style clock alignment over the encrypted messaging channel; latency targets are sub-second for play/pause/seek across continents (WWDC21-10183).

## Migration guidance

- If you have a long-running multiplayer or collaborative app, `GroupSession` is a **drop-in alternative to MultipeerConnectivity** for FaceTime-anchored experiences. No Bonjour/Wi-Fi requirements (WWDC21-10187).

## Cross-references

- Spatial SharePlay (visionOS, 2023) extends this framework with personas, spatial personas, and shared 3D anchors.
- `Design for Group Activities` (WWDC21-10184) emphasizes: prefer existing app entry points, don't fight the system communication layer, design for asymmetric joining.
