# watchOS 5: Workouts, Background Audio, Walkie-Talkie — WWDC 2018 Analysis

**Sessions covered:** 206 (What's New in watchOS), 504 (Creating Audio Apps for watchOS), 707 (New Ways to Work with Workouts), 217 (Siri Shortcuts on the Siri Watch Face), 706 (Accessing Health Records with HealthKit), 239 (Designing Web Content for watchOS)

## Headline

watchOS 5 is the **third-party-app release**: background audio playback for any app (not just workout apps), a redesigned `HKWorkoutSession` + `HKLiveWorkoutBuilder` API with automatic crash recovery, Siri Shortcuts on the Siri watch face (and they execute on iPhone if you don't have a watch app), and a new `HKCumulativeQuantitySeriesSample` for high-frequency data ingestion. Plus interactive notifications with custom buttons, switches, and gesture recognizers right inside the notification interface.

## Background Audio for Any App (504, 206)

- Pre-watchOS 5: only workout apps could keep audio playing in the background. The hack was widespread; many "music" apps were registered as workout apps.
- watchOS 5: **`UIBackgroundModes = ["audio"]`**-equivalent capability is available to any app via the new "audio" background mode.
- Direct AVFoundation APIs: `AVAudioPlayer`, `AVAudioEngine`. Same code as iOS. Move shared playback logic to a framework and reuse.
- Bluetooth headphone routing is built into session activation. Set `route sharing policy = .longForm` and `activate(options:completionHandler:)` will:
  - Auto-connect to AirPods or W1/H1-chip Beats if active.
  - Show a route picker for other Bluetooth devices.
- `MPNowPlayingInfoCenter` and `MPRemoteCommandCenter` are exposed on watchOS; what's playing in your app shows in the Now Playing complication and on the lock screen of paired iPhone.
- New `WKInterfaceVolumeControl` view in Interface Builder — wires to the digital crown automatically with the standard system color treatment.

## New Workout API (707, 206)

The whole API got rewritten. Old `HKWorkout` was a one-shot create-and-save object; new model has separate _session_ and _builder_:

```swift
let session = try HKWorkoutSession(healthStore: store, configuration: config)
let builder = session.associatedWorkoutBuilder()
let dataSource = HKLiveWorkoutDataSource(healthStore: store, workoutConfiguration: config)
builder.dataSource = dataSource
session.startActivity(with: Date())
builder.beginCollection(withStart: Date()) { _, _ in }
```

- `HKLiveWorkoutDataSource` automatically collects samples relevant to the workout type (heart rate, active energy, distance walking/running for a run; add/remove types as needed).
- `builder.statistics(for: heartRateType)` returns `HKStatistics` with min/max/average/most-recent — bind to UI labels in the `workoutBuilderDidCollectData` delegate callback.
- `builder.elapsedTime` accounts for pause/resume automatically — anchor your `WKInterfaceTimer` to `Date(timeIntervalSinceNow: -builder.elapsedTime)`.

## Workout States (707)

`notStarted → prepared → running ⇄ paused → stopped → ended`

- `prepared` is new and important: puts the system in Session Mode (extended runtime + sensors warmed up) **before** the user actually starts working out. Use it during a 3-second countdown so heart-rate sensor is ready when activity actually starts.
- `stopped` keeps Session Mode active, giving you time to save the workout. The session only fully exits Session Mode at `ended`.

## Workout Crash Recovery (707, 206)

**HIDDEN GEM**: if your workout app crashes during an active session, watchOS automatically relaunches it and calls a new delegate method:

```swift
func handleActiveWorkoutRecovery() {
  let store = HKHealthStore()
  store.recoverActiveWorkoutSession { session, error in
    self.session = session
    self.builder = session?.associatedWorkoutBuilder()
    // do NOT call startActivity or beginCollection; they're already running
  }
}
```

- The session and builder come back in their previous state. The user's marathon isn't lost because your app crashed at mile 14.
- You _do_ need to re-attach a `HKLiveWorkoutDataSource` if you were using one.

## HKCumulativeQuantitySeriesSample (707)

- New sample type for high-frequency data (e.g., a soccer app tracking sprint distance every 100 ms).
- Pre-watchOS 5: each tiny distance was a separate `HKQuantitySample`. Storage overhead was per-sample, queries returned thousands of objects.
- New: a single `HKCumulativeQuantitySeriesSample` represents the cumulative total, backed by individually-queryable quantities via `HKQuantitySeriesSampleQuery`.
- For visualizations use the existing `HKStatisticsCollectionQuery` — automatically benefits from the new storage. For deep analysis use `HKQuantitySeriesSampleQuery`. To create new series use `HKQuantitySeriesSampleBuilder`.

## Siri Shortcuts on the Siri Watch Face (217, 206)

- `INRelevantShortcut` (introduced for watchOS 5) wraps an `INShortcut` (`NSUserActivity` or `INIntent`) plus relevance providers (`INDateRelevanceProvider`, `INLocationRelevanceProvider`, `INDailyRoutineRelevanceProvider`).
- **HIDDEN GEM**: relevant shortcuts work _without_ a Watch app. As long as the underlying intent is background-executable and doesn't need encrypted data, watchOS 5 executes it on iPhone via the watch's connection.
- `WKRelevantShortcutRefreshBackgroundTask` lets your watch app push fresh relevant shortcuts in the background (e.g., a glanceable weather platter that should always show current data).
- `WKIntentDidRunRefreshBackgroundTask` runs after a background intent fires — refresh complications and snapshots that may now be stale.

## Interactive Notifications on Watch (206)

- watchOS notifications now run dynamic content from Notification Center too (used to fall back to static).
- New "interactive" interface controllers in IB — opt in via "Has Interactive Interface" checkbox. Your notification UI can have buttons, switches, gesture recognizers.
- `WKExtensionDelegate.handleActiveWorkoutRecovery` from notification (above) plus `performNotificationDefaultAction()` and `performDismissAction()` for programmatic launch / dismiss.

## Walkie-Talkie (206 mention, ships in OS)

- New first-party app. Uses FaceTime Audio + a custom invitation/permission flow.
- No third-party API at WWDC 2018 — pure system feature. Notable as a sign of where peer-to-peer voice is heading.

## Web Content on the Watch (239)

- `WKWebView` works on watchOS now (limited form). Useful for showing Web pages from links inside Mail, Messages, etc.
- Apple's recommendation: design specifically for the small screen. Vertical scrolling, large tap targets, no JavaScript-heavy interactions.

## Always-on Wi-Fi Joining (206 mention)

- Series 3 / 4 with cellular don't need an iPhone for many tasks. watchOS 5 can join Wi-Fi networks _directly_ from watch, opening the door to truly independent watch use.

## HealthKit Records (706)

- Patients can pull medical records from supported health systems (Allergies, Conditions, Immunizations, Lab Results, Medications, Procedures, Vitals) into Apple Health on iPhone.
- Apps can read these records with explicit user permission. Powerful for research and personal-health apps.
- Privacy: per-record granularity in HealthKit's authorization sheet.

## Cross-references

- Siri Shortcuts core API: 211, 214 (iOS sessions).
- Background tasks lifecycle: see also 707 in 2019 (Background Tasks framework — a related but different API).
- AV Audio APIs: 504 covers the Bluetooth route handling in much more detail than 206.
