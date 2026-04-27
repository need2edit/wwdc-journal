# HealthKit Debut — WWDC 2014 Analysis

**Sessions covered:** 203 (Introducing HealthKit)

## Headline

HealthKit is iOS 8's centralized, secure, system-wide store for health and fitness data. Apps that previously each held their own siloed data (steps, weight, blood sugar, sleep, heart rate) now share through a common database backed by privacy-by-design APIs and a system Health app.

## The Mental Model (session 203)

- **HKHealthStore** is the database handle. Long-lived; create one, hold onto it, share it across your app (203).
- **All data is immutable** once written. To "edit" a weight reading, you delete the old sample and add a new one (203).
- **Read-only model objects, write-via-request-objects** (a pattern HealthKit shares with PhotoKit, by design — both designed in 2014 with the same Apple privacy framework). All `HKObject` subclasses are read-only; mutations go through change requests applied asynchronously by `HKHealthStore`.
- **Per-type read/write permissions**: the user grants access to "step count read" separately from "step count write" separately from "blood sugar read" — granular by every individual data type (203).

## Type System (session 203)

- **`HKObjectType`** abstract base. Subclasses: `HKCharacteristicType` (immutable user traits — date of birth, blood type), `HKQuantityType` (numeric measurements — weight, blood sugar, heart rate), `HKCategoryType` (enumerated states — sleep analysis, menstrual flow).
- **Identifier strings encode their subclass**: `HKQuantityTypeIdentifierHeartRate`, `HKCategoryTypeIdentifierSleepAnalysis`. Mismatching subclass and identifier returns nil from the constructor — a safety mechanism (203).
- **`HKQuantity`** wraps a `Double` value with an `HKUnit`. The unit system handles conversion automatically: `quantity.doubleValue(for: HKUnit.gram())` and `quantity.doubleValue(for: HKUnit.kilogram())` give the same data in different units (203).
- HIDDEN GEM: `HKUnit` supports compound units via strings: `HKUnit(from: "mg/dL")` parses to `mg per deciliter`. Saves writing the verbose `gram.divided(by: liter.unitDivided(by: 10))` (203).
- WARNING: asking a quantity for its value in an incompatible unit (mass-as-volume) **throws an exception**. Guard with `quantity.is(compatibleWith: someUnit)` first (203).

## Data Hierarchy (session 203)

- `HKObject` (UUID, source, metadata) → `HKSample` (start/end date, sample type) → `HKQuantitySample` / `HKCategorySample` / `HKWorkout`.
- **Every sample has BOTH start and end date**. For instantaneous readings (weight) they're equal. For interval readings (heart rate during a 30-second window) they differ — and the data type tells consumers what makes sense (203).
- **`source`** is automatically stamped: app or paired hardware (Bluetooth heart rate monitor). Users can see in the Health app exactly which app or device wrote each data point (203).
- **`metadata`** is a free-form `[String: NSString | NSNumber | NSDate]` dictionary on every object. Apple defines some keys (`HKMetadataKeyBodyTemperatureSensorLocation`) but you can add your own. **HIDDEN GEM: this is how you attach app-specific provenance to clinical data without bloating the schema** (203).

## Querying (session 203)

- **Characteristics** (DOB, biological sex, blood type, Fitzpatrick skin type) are synchronous: `healthStore.dateOfBirth()` returns immediately. They don't change.
- **Sample queries** for everything else. `HKSampleQuery(sampleType: ..., predicate: ..., limit: ..., sortDescriptors: [...]) { query, results, error in ... }`.
- **Predicates use `NSPredicate`** with HealthKit-provided constants (`HKPredicateKeyPathStartDate`, etc.) AND convenience constructors (`HKQuery.predicateForSamples(withStart: end: options:)`). Same predicate, two ways to write (203).
- **`HKObserverQuery`**: long-running, fires `updateHandler` whenever any sample of the watched type is saved or removed. Replaces polling. Pair with **background delivery** (`enableBackgroundDelivery(for:frequency:withCompletion:)`) and your app gets woken to fetch new readings without the user opening it.
- **`HKAnchoredObjectQuery`**: incremental sync. Pass an opaque `anchor` token; get back all samples added since that token, plus a new token. Stash the token, use it next time. Perfect for one-way syncing data from HealthKit to a server (203).
- **`HKStatisticsQuery`** + **`HKStatisticsCollectionQuery`**: server-side aggregation. Don't pull 7,000 step samples to sum them — ask HealthKit for the sum directly. Statistics collection bins by `NSDateComponents` interval (1 day, 1 week) starting from an `anchorDate` (203).

## Discrete vs Cumulative (session 203)

- **Discrete** types (weight, blood pressure): `min`, `max`, `average` make sense. Summing weight readings is meaningless.
- **Cumulative** types (steps, calories burned, distance): `sum` makes sense. Min/max of steps is meaningless.
- `HKQuantityType.aggregationStyle` returns `.discrete` or `.cumulative` so you can branch your stats UI correctly. Asking a cumulative type for `.discreteAverage` throws an exception (203).

## Source Merging — the "two pedometers" problem (session 203)

- Two apps both writing step samples at the same time would normally double-count. The user picks a "preferred source" per data type in the Health app; HealthKit's automatic statistics queries de-duplicate accordingly.
- HIDDEN GEM: `HKStatisticsOptions.separateBySource` lets you receive per-source statistics and apply your own merge strategy if Apple's preferred-source approach doesn't fit your domain (203).

## Permissions Model (session 203)

- **Request all permissions you'll need at once**: `requestAuthorization(toShare: Set<HKSampleType>, read: Set<HKObjectType>, completion:)` shows a single sheet listing every requested type. Asking incrementally creates a death-by-a-thousand-prompts UX.
- **You can check write authorization, NOT read authorization**. `authorizationStatus(for:)` reveals share status but read status is privileged information — knowing the user denied "blood sugar read" leaks medical info (a denied diabetic). Apple documents this asymmetry as deliberate (203).
- WARNING: **HealthKit is unavailable on iPad in iOS 8** — `HKHealthStore.isHealthDataAvailable()` returns false. Plan accordingly (203).

## Localization (session 203)

- New `NSMassFormatter`, `NSLengthFormatter`, `NSEnergyFormatter` ship in Foundation alongside HealthKit. They localize values to the user's locale (kg vs lb, km vs mi, kcal vs kJ).
- **`NSMassFormatter.isForPersonMassUse = true`** — important because some locales use stones for body mass but kg for object mass. The formatter respects this distinction (203).
- BEST PRACTICE: pass the value in a fixed canonical unit (kilograms) to the formatter; receive the localized display string AND optionally the unit that was selected, via the out-pointer overload (203).

## Best Practices

- **Long-lived `HKHealthStore`**: create once, share. Don't allocate per-screen.
- **Use `HKAnchoredObjectQuery` for sync to a server** — never iterate all samples to find what's new.
- **Use `HKStatisticsQuery` for "today's total steps"** — never fetch all samples and sum.
- **Request permissions as a batch upfront** — one sheet, all types.
- **Never assume a permission you didn't request** — and always check `isHealthDataAvailable` first (no-op on iPad).
- **Persist your `HKQueryAnchor` between launches** — that's the whole point of the anchored query.

## Hidden Gems

- HIDDEN GEM: `HKWorkout` is its own subclass that bundles a workout type, total energy burned, total distance, and start/end dates — tied to its own samples via metadata (203).
- HIDDEN GEM: HealthKit metadata can store custom keys. A diabetic-management app can stamp `["mealContext": "before_breakfast"]` on every blood sugar reading and query for them later (203).
- HIDDEN GEM: the synchronous `HKHealthStore.dateOfBirth()` blocks the main thread to read keychain-protected biometrics. Treat it like file I/O — call from a background queue if you must, or cache the result.
- PERFORMANCE: `HKStatisticsCollectionQuery` returns a `HKStatisticsCollection` that lazily realizes individual `HKStatistics` objects. Iterating with `enumerateStatistics(from:to:)` only materializes the bins you actually visit (203).

## Cross-references

- **HomeKit (213)** is the sibling debut for the home (smart-home accessories). Different domain, similar privacy story.
- **Touch ID (711)** lets you protect Health-tied secrets in the keychain with biometric authentication (in this device-only mode); a paired pattern for HealthKit-aware apps.
- **App Extensions (205)** can read HealthKit if you configure shared entitlements — useful for a today widget showing today's step count.
- **Privacy (715)** session is mandatory reading for HealthKit adopters: HealthKit-linked apps **must** ship a Privacy Policy URL via iTunes Connect.

## Migration Guidance

- For pedometer/step apps that previously wrote to a private file/database: **migrate writes to HealthKit** so other apps benefit. Then rebuild your reads from HealthKit too — instant interoperability with Apple Watch (announced for spring 2015), other fitness trackers, and the Health app.
- For diabetes apps with manual blood-sugar log entries: store as `HKQuantitySample` with `HKQuantityTypeIdentifierBloodGlucose`. Even if you keep your own visualization, contributing data to HealthKit means the user can see it in the Health app and physicians can pull a coherent record.
- For sleep apps: `HKCategoryTypeIdentifierSleepAnalysis` with `HKCategoryValueSleepAnalysis.inBed` / `.asleep`. Each `HKCategorySample` covers a contiguous interval; multiple samples for one night.
