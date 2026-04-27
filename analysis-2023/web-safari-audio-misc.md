# WWDC 2023 — Safari, Web Apps, Audio, Health, & Other Frameworks

The "everything else" cluster: Safari/Web, Audio (AirPlay/AirPods), HealthKit, Wallet/Pay, Cinematic Sound Design, App Store Connect.

## Sessions Analyzed

### Safari & Web
- 10120 — What's new in web apps
- 10262 — Rediscover Safari developer features
- 10121 — What's new in CSS
- 10122 — Explore media formats for the web
- 10119 — What's new in Safari extensions
- 10118 — What's new in Web Inspector
- 10279 — Meet Safari for spatial computing

### Audio & Video
- 10239 — Add SharePlay to your app
- 10241 — Share files with SharePlay
- 10238 — Tune up your AirPlay audio experience
- 10275 — Explore AirPlay with interstitials
- 10233 — Enhance your app's audio experience with AirPods
- 10235 — What's new in voice processing
- 10271 — Explore immersive sound design

### Health
- 10016 — Build custom workouts with WorkoutKit
- 10023 — Build a multi-device workout app

### Wallet
- 10114 — What's new in Wallet and Apple Pay

### App Store
- 10117 — What's new in App Store Connect
- 10014 — What's new in App Store pricing
- 10015 — What's new in App Store pre-orders
- 10012 — Explore App Store Connect for spatial computing

## Web Apps on iOS / iPadOS / macOS (10120)

Web apps installed to the home screen are now FIRST-CLASS APPS:
- Push notifications (Web Push API).
- Badging API for unread counts.
- Standalone display mode (no browser chrome).
- File handling — open files of registered types directly into the web app.
- Share target — appear in the iOS share sheet.
- Background sync (limited).

Manifest declarations (`manifest.json`):
```json
{
  "display": "standalone",
  "icons": [...],
  "share_target": {...},
  "file_handlers": [...]
}
```

This narrows the gap with native apps significantly. PWAs are FINALLY viable on iOS for many use cases.

## Safari for visionOS (10279)

Safari runs in visionOS windows. Key behaviors:
- Web pages stay 2D; only special CSS/JS opts into spatial behavior.
- `<model>` HTML element renders 3D models (USDZ files) in the page.
- WebXR support shipped for immersive sessions.
- Page text gets the same depth-aware text rendering as native SwiftUI.

Tab pages can be PULLED OUT into separate windows (drag the tab into space).

## CSS Updates (10121)

iOS 17 / macOS Sonoma Safari supports:
- `@scope` for scoped CSS (deepest-only descendants).
- `:has()` selector — finally a parent selector.
- Container queries (`@container`).
- CSS Nesting (no preprocessor needed for nested rules).
- `text-wrap: balance` — typography wins.
- Subgrid for grid-of-grids layouts.

These bring Safari close to feature parity with Chrome/Firefox in 2023.

## Web Push (10120)

Web push works via APNs:
1. User installs the web app.
2. Site requests permission via `Notification.requestPermission()`.
3. Sub-process registers with APNs for a push token.
4. Site sends pushes via standard Web Push API; Apple translates to APNs.

No special Apple Developer account changes needed for web push — but the user MUST have installed the web app (visiting in Safari isn't enough).

## SharePlay Updates (10239)

- Group session AUTOMATIC START: when 2+ people are in a FaceTime call and one launches your app, the system can automatically suggest starting a SharePlay session.
- File sharing within SharePlay (10241): share documents (PDFs, images) inline within the call.
- New persistence: SharePlay sessions can survive app backgrounding for up to 30s.

```swift
let activity = MyActivity(...)
let result = try await activity.prepareForActivation()
if result == .activationPreferred { try await activity.activate() }
```

## AirPods Audio Experience (10233)

iOS 17 lets apps tune AirPods behavior:
- Auto-mute interruption: detect a user starting to speak and lower playback volume.
- Spatial Audio with head-tracking: opt into 5.1/7.1/Atmos mixes that respond to head movement.
- Voice processing improvements (10235): better noise rejection, especially in wind.

`AVAudioEngine.outputNode.outputFormat` gives the connected device's preferred format — adapt accordingly.

## AirPlay Interstitials (10275)

Apps can now insert ads / chapter markers / pre-roll between AirPlay tracks WITHOUT breaking the AirPlay session. The receiver shows a clear interstitial UI, and the user can skip per the app's policy.

Built on AVPlayerInterstitialEvent. Critical for ad-supported streaming services.

## Workout Kit (10016, 10023)

WorkoutKit is the BIG fitness API addition:
```swift
let workout = CustomWorkout(activity: .running, location: .outdoor, displayName: "5K Tempo")
workout.warmup = WorkoutStep(goal: .time(5, .minutes))
workout.blocks = [
  IntervalBlock(steps: [
    IntervalStep(.work, goal: .distance(1, .kilometers)),
    IntervalStep(.recovery, goal: .time(2, .minutes))
  ], iterations: 3)
]
workout.cooldown = WorkoutStep(goal: .time(5, .minutes))
try await workout.presentPreview()
```

Apps can now CREATE custom workouts and PUSH them to the user's Watch. The user starts the workout from their Apple Watch's Workout app — your app just orchestrates.

Multi-device sync (10023): workouts are synchronized across iPhone, Watch, and any peripheral devices via the new HealthKit relay APIs.

## Wallet & Apple Pay (10114)

- Order tracking expanded: ANY merchant API can register orders that show up in Wallet.
- Apple Pay Later integration in the US.
- Tap-to-Pay on iPhone expanded to more countries.
- Reusable IDs in Wallet (driver's licenses) gain biometric-bound display in supported states.

## App Store Connect (10117)

- TestFlight insights: per-build crash and feedback rates.
- App Store Pre-orders (10015): now available globally with auto-billing on release.
- New pricing model (10014): 800 price points instead of 100; per-territory pricing UI.
- App Store Connect API expanded for visionOS asset validation (10012).

## Pathways

- **Web developer (PWA)**: 10120 → 10121 → 10118
- **Audio app**: 10233 → 10238 → 10275
- **Health app**: 10016 → 10023
- **App Store admin**: 10117 → 10014 → 10015

## Hidden Gems

- iOS Web Push REQUIRES the user to install the web app to home screen. Visiting the site in Safari is not enough — many devs miss this.
- Safari's `@scope` CSS rule lets you write component-scoped styles WITHOUT a preprocessor or build step.
- WorkoutKit's `IntervalBlock` supports `iterations:` so you don't write 6 lines for a 3x interval.
- WorkoutKit workouts are scheduled to a future date — push them ahead of time for race day.
- AirPlay interstitials show with a "Now Playing" replacement — the user knows they're in an interstitial, not your content.
- Safari extensions can now persist storage in iCloud — finally, settings sync.
- The new Safari Web Inspector has a TIMELINES tab with FPS, layout shifts, and JS profile in one view.
- App Store Connect API now supports per-version metadata changes via PATCH — easier CI integration.
- Wallet order tracking takes a registered-domain JWT signed by your merchant key — a few hours of integration for support across all carriers.
- AirPods voice processing improvements (10235) include "personal voice intelligibility": iOS detects when the user is being asked a question and primes the mic for response.
