# WWDC 2023 — App Intents, StoreKit, TipKit, Background, & Push

The "system services" tier of WWDC 2023 — how your app integrates with Siri, the App Store, push notifications, background tasks, and discovery surfaces.

## Sessions Analyzed
- 10103 — Explore enhancements to App Intents
- 10102 — Spotlight your app with App Shortcuts
- 10193 — Design Shortcuts for Spotlight
- 10229 — Make features discoverable with TipKit
- 10013 — Meet StoreKit for SwiftUI
- 10140 — What's new in StoreKit 2 and StoreKit Testing in Xcode
- 10142 — Explore testing in-app purchases
- 10141 — What's new in App Store server APIs
- 10143 — Meet the App Store Server Library
- 10178 — What's new in App Clips
- 10027 — Bring widgets to new places
- 10028 — Bring widgets to life
- 10184 — Meet ActivityKit
- 10185 — Update Live Activities with push notifications
- 10025 — Meet Push Notifications Console
- 10108 — What's new in Background Assets
- 10048 — What's new in VisionKit
- 10051 — Create a great ShazamKit experience
- 10104 — Integrate your media app with HomePod
- 10114 — What's new in Wallet and Apple Pay

## App Intents in 2023

App Intents debuted in 2022 (Swift-only replacement for SiriKit / Intents.intentdefinition). 2023 makes them critical infrastructure.

### Interactive Widgets (the big one)

Buttons and toggles in widgets fire `AppIntent`s. Two new protocols:
- `AudioPlaybackIntent` — start/pause/skip audio
- `LiveActivityIntent` — interact with a Live Activity

These are EXECUTED IN THE WIDGET EXTENSION, not the host app. Limitations:
- ~15s budget
- No UI presentation
- Must be deterministic / idempotent

### Dynamic Options

`AppEntity` parameters can supply `EntityQuery` types that return up-to-date suggestions when Shortcuts/Spotlight ask "which task?". Implement `suggestedEntities()` to power autocomplete.

### `@Parameter` Improvements

- New `@Parameter(requestValueDialog:)` for natural-language disambiguation.
- `@Parameter(default:)` for pre-filled values.
- `IntentFile` parameter for file-input intents.

### Continue User Activity → App Intent Bridge

Existing `NSUserActivity`-based deep linking can be wrapped in `AppIntent.perform()` to give Spotlight / Shortcuts / Siri a single entry point.

## TipKit (10229)

Brand new framework for in-app feature discovery tips.

```swift
struct FavoriteTip: Tip {
  var title: Text { Text("Save Favorites") }
  var message: Text? { Text("Tap the heart to save.") }
  var image: Image? { Image(systemName: "heart") }
  
  @Parameter static var visitCount: Int = 0
  
  var rules: [Rule] {
    #Rule(Self.$visitCount) { $0 >= 3 }
  }
}

// In view:
.popoverTip(FavoriteTip())
// or inline:
TipView(FavoriteTip())
```

TipKit handles:
- Display rate limiting (max 1 tip per session by default).
- Eligibility rules with `@Parameter` reactive state.
- Cross-device sync via iCloud.
- Lottery-style A/B variant selection.

CRITICAL: Don't ship "tutorial walls" of tips. Each tip should be DISMISSIBLE and educate ONE feature.

## StoreKit for SwiftUI (10013)

Replaces hand-rolled paywalls with declarative views:

```swift
SubscriptionStoreView(productIDs: [...]) {
  // your marketing content
  VStack { Image("hero"); Text("Pro") }
}
.subscriptionStoreControlStyle(.prominentPicker)
.storeButton(.visible, for: .restorePurchases)
.storeButton(.visible, for: .redeemCode)
```

`StoreView`, `ProductView`, and `SubscriptionStoreView` give you Apple-styled stores. Backgrounds, marketing content, and policies are configurable.

Key benefits:
- Automatic subscription group handling.
- Eligibility for intro offers handled automatically.
- Family Sharing badge appears automatically when applicable.
- Server-side receipt validation through StoreKit 2 (no parsing receipts manually).

## App Store Server Library (10143)

Apple now ships official OPEN-SOURCE server libraries for App Store Server API in:
- Swift
- Java
- Python
- Node.js
- (Go community-maintained)

Replaces hand-rolled JWT signing, decoded transaction handling, App Store notification parsing.

## Live Activities Push Updates (10185)

Live Activities can now be UPDATED VIA REMOTE PUSH:
1. App calls `Activity.request(...)` and gets a push token.
2. App sends token to your server.
3. Server pushes a JSON payload with `aps.event = "update"` and `aps.content-state = {...}`.
4. The widget extension applies the payload to render the new state.

This means a sports app can update game scores even when the app isn't running. Battery cost: managed by the system; you DON'T get unlimited push.

Activity end events use `aps.event = "end"` with optional dismissal date.

## Push Notifications Console (10025)

A web tool at `icloud.developer.apple.com/notifications` that:
- Sends test pushes (no curl/JWT needed).
- Shows delivery status.
- Decodes payloads for debugging.
- Supports both APNs and Live Activity pushes.

This is the answer to every "my push isn't arriving" Stack Overflow thread.

## Background Assets (10108)

For apps with large content (games, ML models, atlases). Background Assets framework downloads on-demand or on-update WITHOUT the app being active. Apple hosts the assets on their CDN.

```swift
class MyAssetManager: BAManager {
  func backgroundAssets() -> [BAAsset] { ... }
  func didReceiveAsset(...) { ... }
}
```

The system schedules downloads when the device is on Wi-Fi, charging, or idle. Apps register their manager via Info.plist.

## App Clips Updates (10178)

- App Clip experiences: up to 50 simultaneous configured experiences (was 10).
- App Clip Codes — physical codes scannable via Camera or NFC.
- Default Browser handling: App Clip can opt to open in Safari instead.
- Improved transition to full app via `SKOverlay`.

## VisionKit Visual Look Up (10048)

The pretzel/dog-breed identification powering iOS Photos is now an API:

```swift
let analyzer = ImageAnalyzer()
let interaction = ImageAnalysisInteraction()
hostView.addInteraction(interaction)
let analysis = try await analyzer.analyze(image, configuration: .init([.text, .machineReadableCode, .visualLookUp]))
interaction.analysis = analysis
```

Detects subjects in images that can be looked up (animals, plants, art, landmarks). The interaction adds a discoverable "Look Up" button on tap.

## ShazamKit Custom Catalog (10051)

You can now match against YOUR OWN catalog of audio (not just Shazam's music library). Powerful for:
- Theme park experiences (audio identifies rides).
- Educational apps (audio identifies a teacher's lesson).
- Accessibility (identifying sounds in environment).

Generate signatures with `SHCustomCatalog.generate(from:)` and save them as a `.shazamcatalog` resource.

## HomePod Integration (10104)

Media apps can declare audio handoff support so HomePod gets real-time playback queue access. Requires:
- `MPNowPlayingInfoCenter` updates with album art.
- Adopt `INPlayMediaIntent` (still required for Siri media intents).

## Pathways

- **App Intents adoption**: 10103 → 10102 → 10193
- **Monetization**: 10013 → 10140 → 10142 → 10143
- **Widgets & Live Activities**: 10027 → 10028 → 10184 → 10185 → 10025
- **Tips & onboarding**: 10229

## Hidden Gems

- TipKit rules can read `@Parameter` state from inside the app, so tips activate based on actual user behavior, not just install date.
- `SubscriptionStoreView` automatically enrolls a user in App Store sharing settings — you don't need to handle Family Sharing flags.
- Push Notifications Console saves the payload across sessions; great for regression-testing.
- `BAManager` runs in a separate process; you can't access UIKit/UI state from it.
- App Clip experiences can pass parameters via the URL — use them to deep-link straight to the relevant screen.
- VisualLookUp REQUIRES the device to be on Wi-Fi for the cloud lookup; offline you only get on-device subject extraction.
- StoreKit for SwiftUI handles the receipt-validation server roundtrip via the app's transaction listener — no manual receipt parsing.
- Live Activities can ENABLE a frequent-update entitlement (up to 1 per second) for sports/timer apps. Default is throttled.
