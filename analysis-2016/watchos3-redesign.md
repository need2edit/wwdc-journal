# watchOS 3 Redesign — WWDC 2016 Analysis

**Sessions covered:** 208 (What's New in watchOS 3), 211 (Quick Interaction Techniques for watchOS), 218 (Keeping Your Watch App Up to Date), 227 (Architecting for Performance on watchOS 3), 235 (Building Great Workout Apps), 612 (Game Technologies for Apple Watch), 804 (Designing Great Apple Watch Experiences)

## Headline

watchOS 3 is **Apple's reset of the entire interaction model**. Instant launch, the Dock, glanceable design, background app refresh, and a brand-new SDK posture: gone are glances; native apps run faster because favorited apps are kept in memory; complications get a guaranteed budget of 50 push updates per day.

The mantra Apple repeats across every watchOS session: **glanceable, actionable, responsive**. The 2-second rule (every interaction should complete in under 2 seconds) is the design north star.

## The new interaction surfaces

| Surface | When it shows | Code behavior |
|---------|--------------|---------------|
| **Watch face complication** | Always, on the active face | App is kept in memory; instant resume |
| **Dock** (side-button press) | Quick scrub through 10 favorites | App suspended-but-resident; resumes on focus |
| **Notification long look** | Scheduled or remote notification | Custom UI via NotificationController |
| **Full app** | Tap from Dock or home screen | Resume (was launch) |

Glances are gone — that functionality merged into the Dock. Migrate any glance UI into your app's primary `WKInterfaceController`.

## Background app refresh — the major new SDK addition

In watchOS 3, your watch app can run code in the background to keep its data, snapshot, and complication current.

Three task types, all delivered through `WKExtensionDelegate.handle(_:)`:

1. **`WKApplicationRefreshBackgroundTask`** — periodic wakeup. Use to fetch fresh data, then schedule the next one with `scheduleBackgroundRefresh(withPreferredDate:userInfo:scheduledCompletion:)`. Minimum: once per hour guaranteed. More frequent if you're a Dock favorite or the dock is partly empty.

2. **`WKSnapshotRefreshBackgroundTask`** — scheduled by the system after notifications dismiss / app backgrounds, OR by you via `scheduleSnapshotRefresh`. Update your UI for the snapshot the user will see in the Dock. The flag `returnToDefaultState` means "the dock will reset me — show my home view, not whatever drilled-in detail I was last on."

3. **`WKURLSessionRefreshBackgroundTask`** — system handed an NSURLSession completing in the background. Used in tandem with background-configuration NSURLSessions for NW fetches that finish while you're suspended.

```swift
func handle(_ backgroundTasks: Set<WKRefreshBackgroundTask>) {
    for task in backgroundTasks {
        switch task {
        case let appRefresh as WKApplicationRefreshBackgroundTask:
            scheduleNextDataUpdate()
            scheduleNextRefresh()
            appRefresh.setTaskCompleted()
        case let snapshot as WKSnapshotRefreshBackgroundTask:
            updateUIForSnapshot()
            snapshot.setTaskCompleted(restoredDefaultState: false,
                estimatedSnapshotExpiration: .distantFuture, userInfo: nil)
        case let urlTask as WKURLSessionRefreshBackgroundTask:
            // store and fulfil after URL session completes
            self.pendingURLTask = urlTask
        default: task.setTaskCompleted()
        }
    }
}
```

## Complication push budget — guaranteed 50/day

In watchOS 2, push updates to complications were unguaranteed and inconsistent. In watchOS 3, **each app on the active watch face is guaranteed 50 silent push updates per day** to refresh its complication.

**BEST PRACTICE:** Don't naively spread them every 28 minutes. Use what you know about the user (sleeping window) and the data (market hours, gym hours, school day) to cluster updates when they matter:
- 50/day naive = 1 update / ~30min
- Skipping midnight–6am = 1 update / ~20min
- Stocks-only-during-NYSE-hours = 1 update / 8min

**HIDDEN GEM:** Complication pushes can also be initiated from the iPhone app via Watch Connectivity (`WCSession.transferCurrentComplicationUserInfo(_:)`). Useful when your Mac/iPhone has fresh data and the watch needs to be pushed without involving your server.

## App resume vs launch — new lifecycle

Favorited apps (in Dock or on watch face complications) are **kept in memory and resumed**, not launched. Lifecycle events get called repeatedly as the user scrubs the dock:

```
willActivate → didAppear → willDisappear → didDeactivate → willActivate → didAppear → …
```

**BEST PRACTICE (URGENT):** Optimize `willActivate` and `didAppear` for resume speed. Heavy work belongs in `applicationDidFinishLaunching` (called once, ever) or dispatched to a background queue. Long-running tasks triggered from `willActivate` will run multiple times as the user dock-scrubs through your app.

**Memory cap:** 30 MB per WatchKit extension. Exceed it and the system **terminates abruptly with no chance to clean up** (so your snapshot won't update). Use small images, narrow data sets, separate watch-specific endpoints if your iPhone API is too verbose.

## WKInterfaceTable performance traps (HIDDEN GEM)

Unlike `UITableView`, `WKInterfaceTable`:
- **Eagerly creates all row controllers up front** — no cell reuse.
- **Cost is linear** in row count.
- **Reload is expensive** — avoid `setNumberOfRows(_:withRowType:)` in favor of `insertRows(at:withRowType:)` / `removeRows(at:)`.

Apple's guidance: **cap watch tables around 20 rows**. The watch is not a phone.

## WKInterface object updates are IPC

Setting any property on a `WKInterface*` object (label, image, group color) **sends an IPC message** from your extension process to the app process. Average latency ~200ms; worst case (Stocks profiling) up to 1.4s on launch.

**BEST PRACTICE:** Cache values in your row controller and only send when the value changes:
```swift
if cachedTitle != newTitle {
    titleLabel.setText(newTitle)
    cachedTitle = newTitle
}
```

Don't blindly set every property on resume.

## New navigation: vertical detail paging

Previously navigating between detail views required tap-back-tap-tap (slow). watchOS 3 adds a paging mode where detail controllers scroll vertically with the digital crown — you scrub through the list of detail views without going back to master.

To opt in:
1. Use a segue from a `WKInterfaceTable` row to your detail interface controller.
2. On the table, set `tableSegueStyle = .detailPaging` (storyboard) or the equivalent code property.
3. **Critical:** detail views must fit on a single screen (no internal scrolling) — internal scrolling takes precedence over outer paging.

The system pre-instantiates neighbors and calls full lifecycle (`awakeWithContext` + `willActivate` + `didDeactivate`) on them. **Don't kick off heavy CPU/network in `willActivate`** for every neighbor — use `didAppear` to start work and cancel in `willDisappear` for the previous controller.

## Workout apps — background-running breakthrough

**Workout-processing background mode** (declared in extension Info.plist) lets your workout app run continuously in the background for the entire workout duration. You receive heart-rate samples, accelerometer, motion changes, and can schedule haptics — all while the user's wrist is down.

Sensor data delivery upgraded to **continuous values** (was batched). Heart rate streams sample-by-sample.

**BEST PRACTICE:** Keep average background CPU below the threshold Xcode shows in the CPU report (red dotted line). Exceed it and watchOS suspends your app to preserve battery. Use Time Profiler in Instruments + the in-Xcode CPU report.

The HKWorkoutSession API can also now be **started from iPhone** (`HKHealthStore.startWatchApp(toHandle:completion:)` with a workout configuration) — useful when the user begins a run by tapping their phone before getting to the watch. The watch app launches in the background already in workout state.

## Frameworks now on watchOS 3

| Framework | New on watch? | Notes |
|-----------|---------------|-------|
| UserNotifications | NEW | Local scheduling on watch |
| CloudKit | NEW | Including CKShare |
| GameKit | NEW | Turn-based games, achievements |
| SpriteKit | NEW | 2D scenes |
| SceneKit | NEW | 3D scenes |
| Apple Pay (in-app) | NEW | Pay for physical goods inside watch app |
| AVFoundation video playback (inline) | NEW | Was full-screen only |
| Audio playback (`AVAudioPlayerNode`) | NEW | Speaker output |
| Crown raw events | NEW | Was scroll/picker only |
| Gesture recognizers | NEW | tap/swipe/pan/long-press on any interface element |
| Gyroscope | NEW | Motion frameworks |

## Discoverability — getting users to find your watch app

The new **Watch Face Gallery** in the iOS Apple Watch app shows pre-built faces. Apps with complications appear here in their own section — a major install funnel.

To appear in the gallery:
1. Implement `getLocalizableSampleTemplate(for:withHandler:)` on your `CLKComplicationDataSource` (returns a localization-key-bearing template).
2. Build a complication bundle in the simulator.
3. Include the bundle in your iPhone app — the iOS Apple Watch app uses it to show a static rendering even before the watch app is installed.

The new face configuration UI lives in the iPhone Apple Watch app. With Quick Watch Face Switching, users will have many faces — your complication has more chances to appear.

The Dock auto-shows the **most recent app** with a "Keep in Dock" button beneath it — easy discovery for users who don't know they can pin apps.

## Apple Pay on watch (in-app)

Use the new `PKPaymentAuthorizationController` (NOT view controller — controller). Same API on watchOS and iOS. Sheet auto-shows on the watch with a simplified UI: only total + merchant name, with double-side-button confirmation.

```swift
let request = PKPaymentRequest()
request.merchantIdentifier = "merchant.com.example.coffee"
request.countryCode = "US"
request.currencyCode = "USD"
request.supportedNetworks = [.visa, .masterCard, .amex]
request.merchantCapabilities = .capability3DS
request.paymentSummaryItems = [PKPaymentSummaryItem(label: "Espresso", amount: 4.50)]

let controller = PKPaymentAuthorizationController(paymentRequest: request)
controller.delegate = self
controller.present(completion: nil)
```

## Best practices summary

- Plan for **2-second tasks** as your design unit.
- Use Background App Refresh for any data that's not always-current.
- Snapshot your UI for the dock — even a slightly different "summary" view if your full UI is too detailed.
- Cap tables at ~20 rows.
- Cache `WKInterface*` properties — don't re-set unchanged values.
- Use the iPhone app + Watch Connectivity to seed a workout instead of asking the user to start it on the watch.
- Always implement a complication, even if you only have a launcher icon — drives Watch Face Gallery placement.

## Hidden gems summary

- 50 guaranteed complication push updates per day per app on the active watch face.
- Apps in the dock can have **inline video autoplay** — even before the user taps in.
- Complication push updates can be initiated from the iPhone app (not just server) via Watch Connectivity.
- The user-default 8-minute "return to last app on wrist raise" enables long-tail interaction patterns (cooking with a recipe, shopping with a list).
- Workout sessions can be started from iPhone — the watch wakes to background-running workout mode automatically.
- Complication pushes don't count against UI alert badge/sound budgets — they're silent updates that never alert.

## Cross-references

- Notifications on watch → analysis-2016/ios10-notifications.md
- HealthKit + workouts → analysis-2016/health-fitness.md
- Performance optimization techniques → analysis-2016/performance-instruments.md
