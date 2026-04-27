# watchOS 2 Native Apps — WWDC 2015 Analysis

**Sessions covered:** 105 (Introducing WatchKit for watchOS 2), 207 (WatchKit In-Depth, Part 1), 208 (WatchKit In-Depth, Part 2), 209 (Creating Complications with ClockKit), 216 (Layout and Animation Techniques for WatchKit), 228 (WatchKit Tips and Tricks), 713 (Introducing Watch Connectivity), 204 (Apple Watch Accessibility), 802 (Designing for Apple Watch), 803 (Designing with Animation), 805 (Apple Watch Design Tips and Tricks)

## Headline

In watchOS 1, your "Apple Watch app" was a slim Storyboard living on the watch driven by an extension running on the iPhone. Every interaction made a roundtrip across the Bluetooth link. **watchOS 2 moves your extension code natively onto the watch.** Lower latency, standalone operation when the iPhone isn't around, plus brand-new frameworks: ClockKit (complications), Watch Connectivity (iPhone↔Watch), and access to native sensors (Core Motion, Core Location, HealthKit, HomeKit, MapKit, Contacts, EventKit, PassKit, AVFoundation, NSURLSession with tetherless Wi-Fi).

## Architectural Shift (105, 207)

watchOS 1: WK extension runs on iPhone (iOS SDK).
watchOS 2: WK extension runs natively on the watch (watchOS 2 SDK), bundled into the watch app installed alongside (and inside) the iPhone app's bundle.

- Both side bundles are bundled into the user's iPhone app at build time. When paired with the watch, the watch portion gets copied across.
- A WatchKit-2 extension is a separate target with its own subset of frameworks. Cannot share code with the iPhone target by linking; you must add files to BOTH targets, OR use a shared dynamic framework that ships in both.
- watchOS 1 image caching APIs (`addCachedImage`) are gone — use `setImage:` directly with `UIImage` data, or use Watch Connectivity to push assets ahead of time.
- `openParentApplication` is gone — use Watch Connectivity instead.

## Watch Connectivity (713, 207)

The new WCSession framework on BOTH iOS and watchOS for paired-device messaging.

Three transport modes, each tuned for different needs:

| Mode | Direction | Wakes counterpart? | Use case |
|---|---|---|---|
| `updateApplicationContext(_:)` | Bi-directional dictionary | No | Keep latest known state available next time the other side runs |
| `transferFile(_:)` / `transferUserInfo(_:)` | Bi-directional, queued, in-order | No | Larger background transfers; system schedules at power-friendly time |
| `sendMessage(_:replyHandler:)` | Bi-directional immediate | Watch→iPhone wakes the iPhone in background. iPhone→Watch ONLY if the watch app is running. | Live interactive request/response |

- **HIDDEN GEM**: `applicationContext` always overwrites the previous value — the receiver always gets the latest, never a backlog. Perfect for "here's the current weather" semantics.
- **HIDDEN GEM**: messages from Watch can wake the iPhone app silently in the background — perfect for "kick off a long-running iPhone task from the watch."
- The asymmetry (iPhone cannot wake the watch in background) is deliberate: the watch is energy-constrained.

## ClockKit & Complications (209, 105)

Complications are the small data tiles on the watch face.

- You implement a `CLKComplicationDataSource`. The system asks for a **timeline** of data (past + present + future), not a single value.
- The system pre-fetches your timeline so when the user raises their wrist, the data is already current — no code runs.
- **Time travel** (digital crown to see past/future) just consults the timeline you already provided. Zero extra code.
- Templates per family: `circularSmall`, `modularSmall`, `modularLarge`, `utilitarianSmall`, `utilitarianLarge`. Each template has slots (line text, ring fill, image).
- Budget: complications get a tight CPU/network budget per day. Use the timeline to give the system everything it needs ahead of time.
- For background updates: `requestedUpdateDidBegin` / `requestedUpdateBudgetExhausted` callbacks. Schedule next update with `scheduledUpdateAlignmentInterval`.

## Layout & Animation (216)

WatchKit doesn't have Auto Layout. Layout is done in Interface Builder using groups (horizontal/vertical), with size and spacing per-element.

- **All properties settable in IB are now settable programmatically in watchOS 2** — fixes a watchOS 1 frustration.
- New `animate(withDuration:animations:)` API for state changes inside a block — UIKit-style. Supported animatable properties: alpha, height, width, color, position-via-group offset.
- **HIDDEN GEM**: Coordinated images. Set an animated image (a sequence of frames) on a group's background, then bind a `WKInterfacePicker` to it via `setCoordinatedAnimations`. As the user scrolls the digital crown, the animation frame index tracks the picker position. Used for ring-fill UIs (timer, intensity, minute selector).

## Digital Crown via WKInterfacePicker (105)

Three styles:
- `list` (familiar from complication configuration)
- `stack` (image transitions stack-fade between frames)
- `imageSequence` (raw frame-to-frame, for natural animations like clock hands)

Optional focus outline and caption above. Optional scroll indicator (use when the count isn't obvious from content; skip when content makes count clear, e.g., 24 hours).

## Hardware Access (105)

- **Taptic engine**: `WKInterfaceDevice.current().play(_:)` with named haptic styles (`notification`, `directionUp`, `success`, `failure`, `retry`, `start`, `stop`, `click`). Users learn the meaning of each — use them consistently.
- **Microphone**: `presentTextInputController(...)` brings up the dictation/audio sheet; you choose the action button name ("Send" vs "Save"). On Force Touch in the input UI, language switcher appears.
- **Speaker**: `WKInterfaceMovie` for short content; for longer audio (podcasts), use AVFoundation — system can play in background while your extension is suspended. Now Playing glance controls work.
- **Long-form audio playback** doesn't keep your extension alive — file is handed to the system.
- **Maps**: subset of MapKit available. `openMaps(...)` and turn-by-turn deep links.
- **PassKit**: full pass library access on watch; can add new passes from your watch app. Synced via iCloud.

## Open System URLs (207)

`openSystemURL(_:)` from `WKExtension` handles `tel:`, `sms:`, `mailto:`, `passkit:` URLs by calling out to system UI on the watch (in-call screen overlays your app, tap-to-end returns to your app).

## Notifications (207, 208)

- Local notifications must originate from the iPhone (use Watch Connectivity to ask the iPhone). Same routing logic decides phone-vs-watch.
- iOS 9 supports inline text reply on the watch (third-party): set `behavior = .textInput` on a `UIUserNotificationAction`, optionally provide `suggestionsForResponseToActionWithIdentifier`.
- **HIDDEN GEM**: Force Touch in any text input UI brings up an on-the-fly language switcher (showing every keyboard you have on iPhone) — works inside notifications too.
- When app is **active**, the user notification interface controller is NOT shown over your app — instead `WKExtensionDelegate.didReceive...Notification` is called and YOUR app is responsible for surfacing the alert (e.g., append to chat transcript).

## Data Storage (207)

- `documents` — persistent, NOT restored from backup
- `caches` — purgeable
- Sharing between iPhone and watch needs `NSFileManager.containerURL(forSecurityApplicationGroupIdentifier:)` with App Groups capability, OR Watch Connectivity for transfer.

## Networking (105, 207)

- `NSURLSession` works on watch including with tetherless Wi-Fi (network without iPhone present).
- Background download sessions work — IMPORTANT to grab the file IMMEDIATELY in the delegate callback because it's removed from temp shortly after.
- Re-attach to outstanding URL sessions in `applicationDidFinishLaunching` since your extension may have been killed mid-download.

## Security (105)

- Keychain is on the watch.
- **HIDDEN GEM**: Watch Keychain inherits the watch's wrist-detection lock. Wrist on = unlocked = your stored credential is accessible. Wrist off = locked = inaccessible. Best place to stash credentials for an auto-login experience.

## Authorization (105, 703)

- Location, contacts, calendar, HealthKit, etc. — authorization is **shared** between iPhone app and watch app. User answers once.
- Watch can prompt; the prompt is **delivered to the iPhone** for the user to answer (limited screen real estate on watch). Until answered, your watch app may operate without that data — design for the unset state.

## HealthKit on Watch (105)

- Direct sensor access — heart rate is recorded much more frequently while a workout session is active.
- `HKWorkoutSession` keeps your watch app foreground each wrist-raise during the session. Between wrist-raises, your app is suspended but HealthKit continues recording.

## Migration Tips (207)

- watchOS 2 SDK isn't a 100% iOS framework subset. Audit imports.
- Re-test all images at watch-appropriate sizes (38mm and 42mm).
- Move all logic out of `openParentApplication` into your extension.
- WK extension delegate is new — implement lifecycle methods (`applicationDidFinishLaunching`, `applicationDidBecomeActive`, `applicationWillResignActive`).

## Modal Alerts (207)

`presentAlert(title:message:preferredStyle:actions:)` brings up:
- `.alert` (notification of fact)
- `.sideBySideButtonsAlert` (either/or)
- `.actionSheet` (up to 4 actions + cancel)

Actions can be `.destructive` (rendered red).

## Cross-references

- Watch Connectivity (713) is the foundation for ClockKit (209) data refresh.
- HealthKit on watch (105) connects to all-day battery work (707) — high-frequency HR sampling is power-expensive.
- Layout and Animation (216) builds on UIKit dynamics-style mental models without literal `UIKitDynamics`.
