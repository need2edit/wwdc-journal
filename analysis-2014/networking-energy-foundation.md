# Networking, Energy & Foundation — WWDC 2014 Analysis

**Sessions covered:** 707 (What's New in Foundation Networking), 710 (Writing Energy Efficient Code, Part 1), 712 (Writing Energy Efficient Code, Part 2), 716 (Power, Performance and Diagnostics: GCD and XPC), 714 (Fix Bugs Faster using Activity Tracing), 706 (What's New in Core Location), 708 (Taking Core Location Indoors), 709 (Cross Platform Nearby Networking), 713 (What's New in iOS Notifications), 718 (Adopting AirPrint), 703 (What's New in the Accelerate Framework)

## Headline

iOS 8 introduces **SPDY** (the precursor to HTTP/2) transparently in `NSURLSession`, **background NSURLSession** for out-of-process uploads/downloads that survive your app dying, **NSBackgroundActivityScheduler** on Mac for energy-aware deferred work, and **`requestWhenInUseAuthorization`** vs `requestAlwaysAuthorization` granular Location permissions.

## SPDY in NSURLSession (session 707)

- **SPDY is now a transparent NSURLSession protocol** in iOS 8 / Yosemite. No code changes required — if your server supports SPDY, NSURLSession negotiates it via TLS ALPN, otherwise falls back to HTTP/1.1.
- **One long-lived TCP connection** per server, multiplexed across many simultaneous requests. Eliminates **head-of-line blocking** that HTTP/1.1 (even with pipelining) suffers from.
- HIDDEN GEM: SPDY uses **request priorities** to interleave high-priority small responses (CSS, JS) with low-priority large responses (images). On a slow connection, your stylesheet finishes downloading before the giant hero image, so the page renders sooner (707).
- Requires HTTPS (SPDY mandates encryption).
- Apple measured **up to 25% faster** end-to-end vs HTTP/1.1 for typical workloads (many small requests). Big-file downloads see less benefit (single large transfer doesn't multiplex).
- BEST PRACTICE: **un-shard your hostnames**. The classic optimization of splitting content across `images.example.com` + `static.example.com` + `api.example.com` to get more parallel HTTP/1.1 connections is **counter-productive with SPDY** — defeats connection reuse (707).
- BEST PRACTICE: **enqueue all your requests at once**. SPDY multiplexing makes them parallel; you no longer need to manually serialize to avoid head-of-line blocking (707).

## Background NSURLSession (session 707)

- Create with `URLSessionConfiguration.background(withIdentifier:)`. Tasks (uploads/downloads) run in a system daemon, not your app.
- Your app can crash, be killed, be suspended — uploads/downloads continue. iOS relaunches your app in the background to deliver completion handlers.
- **`application(_:handleEventsForBackgroundURLSession:completionHandler:)`** is the AppDelegate hook. Re-create the URLSession with the same identifier; the daemon delivers pending events.
- WARNING: background sessions only support **file-based uploads** (`uploadTask(with:fromFile:)`, NOT `fromData:`) and downloads. The framework needs a stable file source/destination since your app might be terminated (707).
- HIDDEN GEM: **`isDiscretionary = true`** on a background config means "schedule when system conditions are good" — defer to Wi-Fi when on cellular, defer when battery is low. Apple's photo upload uses this (707).
- HIDDEN GEM: NSURLSession monitors network reachability automatically inside background sessions. Stepping out of Wi-Fi mid-download triggers a transparent retry when reachable again — **you don't have to use SCNetworkReachability anymore** for these tasks (707).

## Energy-Efficient Code (sessions 710, 712)

- **CPU power has wide dynamic range**. Use a little, costs little; use a lot, costs a lot. **A small task that runs occasionally can cost more energy than a big task that runs once** because of fixed wakeup cost. (710)
- **Aggregate small sporadic work**. The fixed cost (waking the CPU, scheduling, getting data into cache) dominates for tiny work units. Batching many small operations into one big operation cuts energy substantially (710).
- **Energy = power × time. Faster execution often means less energy** even at higher instantaneous power. Multi-threading a single-threaded job: dynamic cost stays the same; fixed cost drops because the job finishes sooner (710).
- HIDDEN GEM: **iOS 8 / Mavericks Battery Settings now show per-app energy usage**. Users can see who's draining the battery. Inefficient apps lose users (710).

## NSBackgroundActivityScheduler (Mac, session 710)

- Tell the system "I have work to do; here's the time window." Yosemite picks the best moment based on power state, network type, user activity.
- `init(identifier: "com.example.MyApp.refresh")`, set `interval`, `tolerance`, `repeats`. Call `schedule { completion in ... completion(.finished) }`.
- HIDDEN GEM: poll `activity.shouldDefer` inside long-running work. If the system's power state changed during your task, gracefully pause and call `completion(.deferred)` to resume later (710).
- Use cases: periodic content fetch, garbage collection, log uploads, automatic backups. **Anything that's "soon, but not now"** (710).

## Core Location Granular Permissions (session 706)

- Two new permission tiers replacing iOS 7's blanket `startUpdatingLocation`-triggers-prompt:
  - **`requestWhenInUseAuthorization`** — only foreground location access. No region monitoring, no significant location changes, no Visits API.
  - **`requestAlwaysAuthorization`** — all of the above PLUS background access.
- Both require Info.plist purpose strings: `NSLocationWhenInUseUsageDescription` / `NSLocationAlwaysUsageDescription`.
- HIDDEN GEM: **request the lower permission first** if it satisfies your needs. Users prefer "When in Use" — explicit foreground-only is reassuring. Apps that demand "Always" without justification get denied (706).
- WARNING: you cannot upgrade from "When in Use" to "Always" with a second prompt. The user must go to Settings to change. Plan your initial request carefully (706).

## Visits API (session 706)

- New in iOS 8: `CLLocationManager.startMonitoringVisits()` delivers `CLVisit` objects to your delegate when the system detects the user has arrived at or departed from a "visit" location (home, work, regularly-visited places).
- More energy-efficient than continuous location monitoring; more semantically meaningful than significant-location-change.
- HIDDEN GEM: doesn't require GPS — uses Wi-Fi + cell tower fingerprinting. Battery cost is minimal (706).

## Indoor Maps + iBeacon (sessions 706, 708)

- Apple Indoor Maps Program: registered venues (airports, malls) provide indoor maps; Core Location returns indoor positions inside them.
- iBeacon (introduced 2013) gets refined: `CLBeaconRegion` with `notifyEntryStateOnDisplay = true` gives a notification just as the user looks at their lock screen, useful for retail (706).

## Multipeer Connectivity Framework — Cross-Platform (session 709)

- Re-introduced from iOS 7 with macOS support in Yosemite.
- Peer-to-peer Wi-Fi and Bluetooth networking. No server needed. Discovery via Bonjour-style advertising.
- Use cases: collaborative editing, multiplayer games over local network, file sharing.

## Activity Tracing (session 714)

- New API in `os/activity.h`: `os_activity_t`, `os_activity_initiate(...)`, etc. Wraps a high-level user-meaningful activity (e.g. "loading user profile") around lower-level work (network, parsing, layout).
- HIDDEN GEM: in Console + Instruments + crash reports, the activity tags propagate. A crash report shows "this crash happened during 'loading user profile'" — narrows debugging dramatically (714).
- Also exposes the **activity tree** in `sample`, `spindump`, and process introspection tools.

## Foundation Other Improvements (session 707)

- **`NSStream getStreamsToHostWithName:port:inputStream:outputStream:`** — finally back. Was missing for years. Direct TCP stream to a host (707).
- **`NSURLSession` delegate queue can be concurrent now** — in iOS 7 it was effectively serial. Big throughput win when many tasks complete simultaneously (707).
- **`NSURLSessionTaskAdditions`** category — protocol implementations get the `URLSessionTask` along with the URL, enabling task-aware cookie/credential storage subclasses (707).

## Push Notifications iOS 8 (session 713)

- **Interactive notifications** — define `UIUserNotificationAction`s with title, identifier, and authentication requirements. Group into `UIUserNotificationCategory` (e.g., "INVITE" with Accept/Decline actions). System shows actions when user 3D-touches or pulls down the notification.
- HIDDEN GEM: actions can be **background** (handled by your app without launching to foreground) or **foreground** (launches your app to handle). For background actions, `application(_:handleActionWithIdentifier:for:completionHandler:)` is called with limited time (713).
- **Permissions overhaul**: `registerUserNotificationSettings(_:)` with `UIUserNotificationSettings(types: .alert | .badge | .sound, categories: [...])`. Replaces the deprecated `registerForRemoteNotificationTypes(_:)` (713).

## AirPrint Adoption (session 718)

- Print without configuring printers. iOS detects nearby AirPrint-enabled printers via Bonjour.
- `UIPrintInteractionController` for printing from app. Customize via `UIPrintPaperList`, `UIPrintInfo`, custom page renderers.
- BEST PRACTICE: support AirPrint in any app that displays content — articles, photos, receipts, tickets. Trivial to add; users expect it (718).

## Accelerate Framework (session 703)

- vDSP / vForce / BLAS / LAPACK: SIMD-accelerated math.
- New in iOS 8 / Yosemite: image processing routines (vImage), supports new pixel formats including HDR.
- BEST PRACTICE: when you find yourself writing a loop with floating-point math (DSP, image filtering, signal processing), check Accelerate first — chances are Apple has a vector-optimized version (703).

## Best Practices

- **Use background NSURLSession for any user-perceivable upload or download** — the user can switch apps, lock the device, even crash your app, and the transfer continues (707).
- **Set Discretionary on background sessions** for non-urgent transfers — saves battery and respects cellular metering (707).
- **Use `requestWhenInUseAuthorization` if you only need foreground location** — more likely to be granted (706).
- **Use NSBackgroundActivityScheduler on Mac for periodic work** instead of NSTimer — system-coordinated scheduling is far more energy-efficient (710).
- **Implement `applicationDidResignActive` and stop animations/timers** — pointless rendering when not visible drains battery (710).
- **Adopt activity tracing** for high-level user actions — your crash reports get better immediately (714).

## Hidden Gems

- HIDDEN GEM: NSURLSession's SPDY support means **switching to HTTPS gets you not just security but performance** if your server supports SPDY. The "HTTPS is slow" excuse is gone (707).
- HIDDEN GEM: app extensions can use background NSURLSession too. Your share extension hands off the upload to the daemon and dies; the upload completes; the daemon wakes your CONTAINING APP (not the extension) to deliver the completion (707, 217).
- HIDDEN GEM: `URLSessionConfiguration.shouldUseExtendedBackgroundIdleMode = true` allows TCP connections to stay open longer when iOS is in background — useful for chat apps that want to receive pushes via long-poll (707).
- HIDDEN GEM: `UIApplication.openSettingsURLString` deep-links the user to YOUR app's settings page in Settings.app — useful in "permissions denied — please enable in Settings" UI (715).
- WARNING: **iOS 8 push notifications require explicit user permission via `registerUserNotificationSettings` BEFORE `registerForRemoteNotifications`**. iOS 7 code that just calls `registerForRemoteNotificationTypes:` is broken in iOS 8 (713).

## Cross-references

- **App Extensions (205, 217)** — extensions REQUIRE background NSURLSession for any upload/download. Direct dependency.
- **CloudKit (208)** — built on top of NSURLSession internally; benefits from SPDY automatically.
- **Privacy (715)** — Location's new tier system is part of the broader purpose-strings initiative.
- **HealthKit (203)** + **HomeKit (213)** — privacy considerations applied to new domains.

## Migration Guidance

- **Apps with foreground NSURLSession uploads**: switch to background NSURLSession with file-based upload sources. The user-perceived reliability improvement is dramatic.
- **Apps using `registerForRemoteNotificationTypes:`**: must switch to the new `registerUserNotificationSettings:` API in iOS 8. Existing code path is broken (713).
- **Apps using `startUpdatingLocation` to trigger location prompts**: must explicitly call `requestWhenInUseAuthorization` or `requestAlwaysAuthorization` AND add the matching purpose strings to Info.plist. Existing code silently fails to ever start updates (706).
- **Apps using NSTimer for periodic background work on Mac**: migrate to NSBackgroundActivityScheduler. The system can defer your work to better times.
- **Server operators**: deploy SPDY support (or wait for HTTP/2 — same multiplexing gains, IETF-standardized). Apple's metric of 25% faster is conservative for many workloads.
