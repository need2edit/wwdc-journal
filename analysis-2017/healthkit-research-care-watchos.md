# HealthKit, ResearchKit, CareKit & watchOS — WWDC 2017 Analysis

**Sessions covered:** 221 (What's New in Health), 232 (What's New in CareKit and ResearchKit), 239 (Connecting CareKit to the Cloud), 216 (The Life of a watchOS App), 205 (What's New in watchOS), 802 (Essential Design Principles), 808 (Planning a Great Apple Watch Experience)

## Headline

HealthKit gains **insulin delivery and blood glucose** types (the foundation for closed-loop diabetes apps), **wheelchair-aware activity metrics**, and a **modernized BeatsPerMinute / HeartRateVariability story**. ResearchKit and CareKit both move to a **cloud-sync ready architecture** with new sample code (CareKit's Cloud Sync sample uses CloudKit). Apple Watch Series 3 introduces cellular-aware app design.

## HealthKit Quantity Types (221)

New in iOS 11:

- **Insulin delivery** (`HKQuantityTypeIdentifier.insulinDelivery`) — units and basal/bolus reasons.
- **Blood glucose** (`HKQuantityTypeIdentifier.bloodGlucose`) — mg/dL or mmol/L.
- **Wheelchair-specific metrics** — `pushCount`, `wheelchairWorkout` workout type, energy-burn formulas.
- **Resting heart rate** (`restingHeartRate`) — daily-average derived metric.
- **Walking heart rate average** — separates active from at-rest.

**HIDDEN GEM**: HKWorkoutSession on watchOS now supports `WorkoutActivityType.wheelchairRunPace` and `.wheelchairWalkPace`. Apps targeting wheelchair users can ditch the misleading "walk" metaphor.

## CareKit + Cloud (232, 239)

CareKit's care plan / care activities / contacts model historically lived in local SQLite. Apple ships a **CloudKit sync sample** showing:

- Patient device → CloudKit private database (PHI lives in user's iCloud, not third-party servers).
- Caregiver device → CloudKit shared database with patient consent.
- Bidirectional CKShare invitations gated by the patient.

**HIDDEN GEM**: this architecture means a clinic can review a patient's care plan compliance without ever hosting their PHI on the clinic's servers — a major HIPAA simplification. The clinic just stores their own CloudKit container references.

## ResearchKit Refresh (232)

- **Trail-making test** — common cognitive assessment for dementia screening, now built-in.
- **Speech-in-noise** — measures speech recognition in noise, used for hearing studies.
- **Spatial-span memory** — visual sequence recall for cognitive tracking.
- New consent flow templates with stronger localization and accessibility.

## watchOS App Lifecycle (216)

- Watch apps run as **extensions of an iPhone app's bundle** (true independence is 2 years away in WWDC 2019).
- Lifecycle: foreground (active), background (frontmost while user lowers wrist), suspended (after a few seconds).
- **PERFORMANCE**: keep launch under 1 second. The user lifts their wrist and expects content NOW. Aggressively lazy-init non-critical state.
- `WKExtension.shared().registerForRemoteNotifications()` — push to Watch independently of phone (in some configurations, Watch even gets pushes when phone is off).

## Apple Watch Series 3 (205)

- LTE cellular variant. Network reachability via `NSURLSession` works on cellular without phone.
- **HIDDEN GEM**: cellular sessions are EXPENSIVE in battery. Use `URLSessionConfiguration.allowsCellularAccess = false` on opportunistic transfers (analytics, prefetch) and let the system route over Bluetooth-to-phone instead.
- Series 3 and Watch OS 4 add Siri faces — your `INIntent` responses can populate complications-style cards on the Siri face. Use Relevant Shortcuts (iOS 12) for the full pattern.

## HealthKit Background Delivery (221)

- `HKHealthStore.enableBackgroundDelivery(for: type, frequency:)` — system wakes your app when new samples for a type arrive.
- Frequencies: `.immediate` (heart rate, with rate limiting), `.hourly`, `.daily`, `.weekly`.
- **WARNING**: if your background handler does substantial work, request a `BGProcessingTask` (iOS 13+ pattern) — for 2017, use a `URLSessionConfiguration.background` upload to push samples to your server while the system maintains the wake.

## Designing Apple Watch Experiences (808)

- **Modular face is the design canvas**. Optimize for "one number, glanceable in 1 second".
- Long-form information lives in the iPhone app, not Watch. Watch is for the latest, most-relevant atom.
- **HIDDEN GEM**: use `UNNotificationContentExtension` on the Watch (`WKInterfaceController` on Watch displays the equivalent rich notification) to show full incident detail without launching a heavyweight app.
- Complication update budget: ~50 timeline updates per day total. Don't try to update every minute — the system will silently drop excess updates.

## Cross-references

- See `accessibility-everywhere.md` — wheelchair metrics tie into accessibility design philosophy.
- See `networking-bluetooth-nfc.md` — Bluetooth LE accessory pattern critical for medical sensors.
