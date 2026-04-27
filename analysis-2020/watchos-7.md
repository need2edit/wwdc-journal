# WWDC 2020 — watchOS 7: Sleep, Family Setup, Multiple Complications, Mobility Metrics

watchOS 7 was a major release: sleep tracking, Family Setup (kids and seniors without their own iPhone), face sharing, multiple complications per app, SwiftUI-in-complications, and a new category of HealthKit "mobility metrics" that bring lab-grade gait analysis into everyday wear.

## Sessions Analyzed
- 10026 — Lists in UICollectionView (covered in iPad analysis; relevant for catalyst)
- 10046 — Create complications for Apple Watch (gateway)
- 10048 — Build complications in SwiftUI
- 10049 — Keep your complications up to date
- 10100 — Meet Watch Face Sharing
- 10171 — What's new in watchOS design
- 10083 — Integrate your app with Wind Down
- 10184 — Synchronize health data with HealthKit
- 10656 — Beyond counting steps
- 10182 — What's new in HealthKit
- 10190 — Create quick interactions with Shortcuts on watchOS
- 10636 — What's new in streaming audio for Apple Watch

## ClockKit: Multiple Complications Per App

Pre-watchOS 7, each app supplied **one** complication. Now an app can supply many — distinct kinds for different watch face slots, all from a single extension.

### CLKComplicationDescriptor

```swift
let descriptor = CLKComplicationDescriptor(
  identifier: "station.\(stationID)",
  displayName: "Whale Sightings — \(name)",
  supportedFamilies: [.graphicCircular, .graphicCorner, .graphicRectangular],
  userInfo: ["stationID": stationID]
)
```

Implement `getComplicationDescriptors(handler:)` on your `CLKComplicationDataSource` to return the list. Call `CLKComplicationServer.sharedInstance().reloadComplicationDescriptors()` if the user changes which complications they want exposed (e.g., favorite stations changed in your app).

### Sample Templates Are Cached

`getLocalizableSampleTemplate(for:withHandler:)` is called **once per complication and cached**. Use placeholder/sample data, not user data — these appear in face-editing and the Apple Watch app on iPhone.

### The Default Complication Identifier

A user with a complication on their face from an older version of your app, or who shared a face containing your complication and chose to remove the data, will be queried for `CLKComplicationDescriptor` with the **`CLKDefaultComplicationIdentifier`**. **Always handle it** — don't return nothing or your users get a broken-looking complication on their face. Sensible defaults: most popular item, app icon as a brand placeholder, or your previously-shipped pre-watchOS-7 complication's content.

## SwiftUI in Complications

All `CLKFullColorImageProvider`-based templates have SwiftUI alternatives. Reuse view code from your main app. The "Build complications in SwiftUI" session walks through it; the data flow is the same as for widgets — return a SwiftUI view from your TimelineProvider.

## Watch Face Sharing (10100) — A New Distribution Channel

Faces share via Messages, Mail, websites, NFC tags, QR codes. iOS 14 / watchOS 7 add `CLKWatchFaceLibrary.addWatchFace(at:completionHandler:)` so apps can prompt users to install a face — including your branded complication.

### Watch Face File Anatomy

Includes complete configuration: photos, color/style, complications, and **a sample timeline entry from your complication so it previews even without your app installed**. Critical: provide good sample data!

User-info dictionary contents are bundled — useful for "this complication shows the surf at this beach" via shared identifier — but **be careful not to leak personal data** in shared files. Mark the user-info content carefully when calling Share via Mail.

### Best Practices
- App must be published to the App Store before shipping a face that references your complication (the App Store Connect ID needs to be embedded).
- Use `WCSession` to detect a paired watch before offering the face-share UI in your iOS app.
- Provide a **fallback face** for Apple Watch Series 3 (some new faces aren't compatible — Modular Compact is one).
- Email yourself a face from the Watch app on iOS to extract the preview image. That preview is what you should display next to the "Add to Apple Watch" button in your UI.
- For website hosting: serve files with the Apple-defined watch-face MIME type so Safari recognizes them.

## watchOS 7 Design Overhaul (10171)

The principle: **kill all gesture-based contextual menus**. Force every action to be discoverable. Three goals:
1. Discoverable & predictable interactions.
2. Relevant actions visible.
3. No gesture menus without losing functionality.

Patterns introduced:
- **Sort/filter buttons** at the top of long lists. SwiftUI: nest a `Picker` in a `List`.
- **Swipe actions** in lists — `onDelete` modifier for the standard "remove" action.
- **More button** — circular ellipsis glyph, bottom-right, for secondary actions in non-scrolling glanceable views (Maps).
- **Action buttons at the bottom of detail views** — most discoverable for delete/share actions. Red text for destructive; require confirmation if not retrievable.
- **Toolbar button** — new SwiftUI API, tucked beneath the navigation bar, only appears in scrolling views (scrolling makes it discoverable). Use sparingly for not-quite-primary actions like "Compose new message".
- **Hierarchical navigation** — apps remember the destination across launches (Mail's "All Inboxes" pattern).

The More button's design: white circular container at 85% opacity with a 1pt black outer glow at 50% opacity for legibility on any background. Refer to HIG hit-region recommendations and add transparent padding to reach the recommended size.

## Sleep Tracking & Wind Down (10083)

watchOS 7's sleep feature includes a **Wind Down** routine that runs leading up to sleep. Apps in supported categories (mindfulness, journaling, music) can be featured in Wind Down setup if they donate Siri Shortcuts marked with the new API:

```swift
shortcut.shortcutAvailability = .sleepGoodForSleep
```

(Or `INShortcutAvailabilityOptions` in Objective-C.)

This is a significant App Store discoverability path for relevant apps.

## HealthKit: Mobility Metrics — The Lab on Your Wrist (10656)

A new category of HealthKit metrics that turn iPhone + Apple Watch into a continuous gait-analysis platform. **Eight new metrics**:

iPhone (collected on the motion coprocessor when phone is in pocket/hip, walking on flat ground in continuous segments):
- **Walking speed** (HKQuantityType `.walkingSpeed`) — sensitive to slow walking, accurate without GPS calibration.
- **Step length** — long confident strides vs. short cautious steps.
- **Double-support time** — % of walking with both feet on the ground (lower is better, indicates stability).
- **Walking asymmetry** — % of time one foot's steps are differently-paced from the other.

Apple Watch:
- **Stair speed up** / **stair speed down** — not just count but velocity.
- **Six-minute walk distance (predicted)** — synthesizes a week of activity into an estimate of the standardized clinical test result.
- **VO₂ max** — improved, now accurate at slower walking speeds (no longer requires running effort).

### Why These Matter

Traditional walking tests require 30m of clear hallway, specialized motion-capture equipment, or rare clinical visits. These metrics passively gather data during everyday wear, enabling apps for:
- Recovery from musculoskeletal injury (the session's worked example).
- Aging-with-independence monitoring.
- Cardiopulmonary fitness tracking.
- Vascular surgery follow-up (Society for Vascular Surgery is using these for peripheral vascular disease patients).
- Pre/post knee-replacement (Zimmer Biomet's mymobility app).

### How to Query

```swift
let type = HKQuantityType.quantityType(forIdentifier: .walkingSpeed)!
let predicate = HKQuery.predicateForSamples(withStart: start, end: end)
let query = HKSampleQuery(sampleType: type, predicate: predicate, limit: HKObjectQueryNoLimit, sortDescriptors: ...) { ... }
healthStore.execute(query)
```

Walking-speed samples have **start/end times for each walking bout**, allowing per-bout filtering. Aggregate intelligently — Apple's example uses 95th percentile per day with a 7-day rolling average, reset around the date of injury, to filter out noise (slow walks with a partner, dog walks).

### Combining With Other Sources

Six-minute-walk samples can come from Apple Watch (predicted) or be manually entered by the user (in-clinic test). Filter by `sourceRevision.bundleIdentifier == apple-known-bundle` and check `metadata[HKMetadataKeyWasUserEntered]` to distinguish.

### Caveats

- Mobility metrics require **specific conditions** to be recorded — phone in pocket/hip, walking on flat ground in a continuous segment.
- Six-minute walk distance requires a week of Apple Watch wear.
- Don't expect every day to have a value; the API returns optionals across enumerated days.

## Synchronize Health Data (10184)

Improvements to HealthKit sync between iPhone and Apple Watch. Apps that record on the watch (workouts, water intake) now sync more reliably. The session covers `HKAnchoredObjectQuery` patterns for incremental sync.

## Family Setup (Implicitly Across Sessions)

Family Setup lets parents configure an Apple Watch for kids/seniors who don't have an iPhone. Implications for app developers:
- Some Apple ID features may be restricted on managed accounts.
- Family Sharing controls (in-app purchases — see [app-services-storekit-store.md](app-services-storekit-store.md)) handle the parental approval flow.

## Streaming Audio for Apple Watch (10636)

watchOS 7 added cellular streaming directly to the watch — apps can now stream music/podcasts without a paired iPhone present. New `WKAudioFilePlayer` improvements; CarPlay-style background audio sessions on the watch.

## Cross-References
- [widgets-and-widgetkit.md](widgets-and-widgetkit.md) — complications and widgets share the timeline mental model.
- [healthkit-research.md](healthkit-research.md) — broader HealthKit changes (CareKit, ResearchKit, FHIR).
- [siri-intents-shortcuts.md](siri-intents-shortcuts.md) — Wind Down integration via Shortcuts donations.

## Adoption Checklist
- [ ] If you have a complication, audit for `CLKDefaultComplicationIdentifier` handling.
- [ ] If multiple complications per app makes sense for you, refactor into descriptors.
- [ ] Consider migrating one complication to SwiftUI for richer visuals.
- [ ] Add `addWatchFace` flow to your iOS app; ship a curated face with your complication.
- [ ] Audit your watchOS UI for hidden gesture menus — surface those actions visibly.
- [ ] Adopt the toolbar button for occasionally-needed actions in scrolling views.
- [ ] If your app touches sleep/mindfulness, add the Wind Down availability flag to your Shortcuts.
- [ ] If health-related, evaluate which mobility metrics enrich your insights.
