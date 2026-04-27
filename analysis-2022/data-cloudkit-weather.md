# Data, Core Data, CloudKit & WeatherKit (2022)

WWDC22's data story includes the introduction of WeatherKit (Apple Weather replacing the soon-deprecated Dark Sky), continued evolution of NSPersistentCloudKitContainer, schema migration tooling, and major background-asset and background-task improvements.

## Sessions covered
- WWDC22-10003 — Meet WeatherKit
- WWDC22-10119 — Optimize your use of Core Data and CloudKit
- WWDC22-10120 — Evolve your Core Data schema
- WWDC22-10115 — What's new in CloudKit Console
- WWDC22-110339 — Build device-to-device interactions with Network Framework
- WWDC22-110403 — Meet Background Assets
- WWDC22-10142 — Efficiency awaits: Background tasks in SwiftUI
- WWDC22-10094 — Add Shared with You to your app
- WWDC22-10006 — Meet Apple Maps Server APIs
- WWDC22-10035 — What's new in MapKit

## WeatherKit (10003)

Apple's replacement for Dark Sky (which Apple acquired and is sunsetting on March 31, 2023). Powered by the new "Apple Weather Service" using high-resolution models and ML for hyperlocal forecasts.

### Two APIs
- **Native Swift framework** — `import WeatherKit` and call `weatherService.weather(for: location)`. Concise, async/await-based.
- **REST API** — works on any platform. Auth via JWT signed with a private key from Developer Portal.

### Available data sets
| Data set | Notes |
|----------|-------|
| Current weather | Single point-in-time conditions: UV, temperature, wind. |
| Minute forecast | Minute-by-minute precipitation for next hour (where available). |
| Hourly forecast | Up to 240 hours. |
| Daily forecast | Up to 10 days. |
| Weather alerts | Severe weather warnings. **Country code required.** |
| Historical | Specify start/end date with hourly or daily request. |

### Privacy commitment
Location is used solely to compute weather and not associated with any personally identifying information. Not shared, not sold.

### Required attribution
You MUST display:
1. The Apple Weather attribution mark (light/dark variants in the framework).
2. A link to the legal attribution page (`attribution.legalPageURL`).
3. For weather alerts, a link to the event page provided in each alert response.

### Capabilities setup
1. Enable WeatherKit in your App ID in the Developer Portal.
2. Add the WeatherKit capability in Xcode.
3. For the REST API: also create a key in the Keys section.

## Core Data schema migration (10120)

### Lightweight migration is the preferred path
Core Data analyzes the difference between source and destination managed-object models and infers a mapping. Operations supported:
- Add/remove/rename attributes (renaming via the `renamingIdentifier` in the property inspector).
- Make optional/non-optional, change defaults.
- Add/remove/rename relationships, change cardinality.
- Add/remove/rename entities, move attributes up/down hierarchy.

### What's NOT supported
Merging entity hierarchies that don't share a common parent in the source.

### Setup
- `NSPersistentContainer` and `NSPersistentStoreDescription` set the lightweight-migration options automatically.
- Manual: pass `[NSMigratePersistentStoresAutomaticallyOption: true, NSInferMappingModelAutomaticallyOption: true]` to `addPersistentStore`.

### Decompose complex migrations
For changes that exceed lightweight migration capability (e.g., external→internal binary storage), bridge through intermediate model versions where each step *is* lightweight-eligible. Apple's example: A → A' (add temp attribute, import data) → A'' (rename, delete old). Build an event loop that iterates through unprocessed model versions in order. **App-specific logic between migrations must be restartable** in case the migration is interrupted.

### CloudKit-specific constraints
After promoting CloudKit schema to Production, **record types and fields are immutable**. Plan for this:
- Don't define unique constraints (unsupported in CloudKit).
- All relationships must be optional with inverses.
- No deny deletion rule.
- Three migration strategies for CloudKit:
  1. Incrementally add new fields to existing record types (older app versions still see all records).
  2. Add a `version` attribute to records and filter by app version (older versions hide newer records).
  3. Create a completely new container for major migrations (uploads can take long with large data).

## CloudKit observability (10119)

### Data generators for testable applications
Pattern: extract data setup into a class with a clear method (`generateData`), use it from tests, command-line args, and UI buttons. Reusable, testable, and lets you reproduce real-world data shapes.

### XCTestExpectations for sync events
NSPersistentCloudKitContainer fires `eventChangedNotification` for export/import events. Build expectation helpers that wait on `endDate != nil` for specific event types per store. **This converts async sync into deterministic test verifications.**

### Memory-aware verifiers
Naive iteration over fetched objects keeps the entire result set in the managed-object context. Pattern shown:
1. Fetch only `objectIDs` (not whole objects).
2. Use `objectWithID(_:)` to fetch each object on demand.
3. Reset the context periodically (e.g., every 10 objects).

This dropped a verifier's memory usage from 10GB+ to a constant low ceiling.

### Observability via system logs
Four predicates to follow a sync end-to-end:
- App process: `process == "YourAppName"`
- CloudKit: `process == "cloudd"` filtered by container ID
- Push: `process == "apsd"` filtered by container ID
- Scheduling: `process == "dasd"` filtered by store-specific activity prefix

Use Console.app or `log stream` (Mac) / `log show` (sysdiagnose).

### Diagnostic collection from devices
1. Install **CloudKit logging profile** from the Apple Developer portal.
2. Reproduce the issue on the device.
3. Trigger sysdiagnose via the keychord (volume buttons + side button on iPhone).
4. Find sysdiagnose in `Settings → Privacy & Security → Analytics & Improvements → Analytics Data`.
5. AirDrop to your Mac.
6. From Xcode Devices Organizer, download the app's container files.

## Background Assets (110403)
A new framework for downloading large assets (game packs, ML models, etc.) before/after first launch:
- **Pre-launch downloads** triggered automatically when the user installs your app.
- **Periodic background updates** scheduled by the system.
- Download requests survive between sessions.
- Replaces On-Demand Resources for many use cases.

## Background tasks in SwiftUI (10142)
Already covered in the watchOS analysis but worth noting cross-cuts:
- New `backgroundTask(.appRefresh:)` and `backgroundTask(.urlSession:)` scene modifiers for SwiftUI apps across iOS, watchOS, tvOS, Mac Catalyst.
- Built on Swift Concurrency. Use `withTaskCancellationHandler` to gracefully promote in-flight requests to background URLSession tasks when runtime expires.

## Network framework (110339)
Build device-to-device peer interactions with Network framework primitives — TLS, QUIC, peer-to-peer connectivity over Bonjour. Use cases: collaborative apps, multi-device games, custom Continuity-style features.

## Best practices
- **BEST PRACTICE**: Always use `NSPersistentContainer` or `NSPersistentStoreDescription` for new code — they enable lightweight migration by default.
- **BEST PRACTICE**: For CloudKit-backed Core Data, design your schema with future-proofing in mind. Production schema is immutable.
- **BEST PRACTICE**: Display the WeatherKit attribution + Apple Weather mark + event page link if you want to ship to the App Store.
- **BEST PRACTICE**: When verifying large CloudKit sync operations in tests, use `objectIDs` + `objectWithID(_:)` + periodic context reset to bound memory.
- **HIDDEN GEM**: NSPersistentCloudKitContainer's `eventChangedNotification` lets you write tests that wait deterministically for sync events instead of polling.
- **HIDDEN GEM**: Set `com.apple.CoreData.SQLDebug` and `com.apple.CoreData.MigrationDebug` env vars to log every Core Data step including migration.
- **HIDDEN GEM**: WeatherKit Swift framework is async/await-only; use the REST API on Linux/Windows servers via JWT.
- **DEPRECATION**: Dark Sky API sunset on March 31, 2023 — migrate to WeatherKit.

## Cross-references
- WeatherKit pairs with location frameworks and CoreLocation patterns.
- Background tasks (10142) is foundational for any app that needs to refresh data periodically.
- CloudKit Console (10115) updates are the operational counterpart to NSPersistentCloudKitContainer development.
