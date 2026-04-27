# Health, Research & Workouts — WWDC 2018 Analysis

**Sessions covered:** 205 (Advances in Research and Care Frameworks), 706 (Accessing Health Records with HealthKit), 707 (New Ways to Work with Workouts), 503 (Creating Photo and Video Effects Using Depth)

## Headline

WWDC 2018 made HealthKit the access point for **medical records** (Allergies, Conditions, Immunizations, Lab Results, Medications, Procedures, Vitals) from supported health systems, rewrote the **workout API** with crash recovery and automatic data collection, and gave us `HKCumulativeQuantitySeriesSample` for high-frequency data. ResearchKit and CareKit got framework refreshes that align them with the modern Swift API style.

## Health Records in HealthKit (706)

- Patients pull medical records from supported health systems (initially: Cedars-Sinai, Stanford, Penn Medicine, Geisinger — many more added since) into the Health app on iPhone.
- Apps with explicit user permission can read these records via new HealthKit object types:
  - `HKClinicalRecord` — base type with `clinicalType`, `displayName`, `fhirResource`.
  - Subtypes: AllergyRecord, ConditionRecord, ImmunizationRecord, LabResultRecord, MedicationRecord, ProcedureRecord, VitalSignRecord.
- Format: FHIR (Fast Healthcare Interoperability Resources) — the same standard used by hospital EMRs.
- **HIDDEN GEM**: per-record-type granularity in HealthKit's authorization sheet. Users can grant your app immunization records but not lab results.

## Workout API Rewrite (707)

The whole API is new (covered in `watchos-5-workouts-audio.md`). Key wins:
- Separate `HKWorkoutSession` (state machine) and `HKLiveWorkoutBuilder` (data collector).
- `HKLiveWorkoutDataSource` automatically collects samples relevant to the workout type.
- `HKLiveWorkoutBuilder.statistics(for:)` returns min/max/average/most-recent — bind directly to UI labels.
- Pause/resume handled automatically; elapsed time accounts for paused intervals.
- Workout crash recovery: app relaunches, gets `handleActiveWorkoutRecovery()`, calls `recoverActiveWorkoutSession()`, session and builder come back in their previous state.

## Quantity Series for High-Frequency Data (707)

- Old: per-distance HKQuantitySamples; thousands of separate objects for a soccer game.
- New: one `HKCumulativeQuantitySeriesSample` backed by individually-queryable quantities.
- Use `HKStatisticsCollectionQuery` (existing API, automatically benefits) for visualization.
- Use `HKQuantitySeriesSampleQuery` for deep analysis of individual data points.
- Use `HKQuantitySeriesSampleBuilder` to create new series. Add quantities at whatever cadence you want; call `finish` to commit.

## ResearchKit + CareKit (205)

- ResearchKit 2.0: Swift-friendly task and result types, accessibility improvements in survey UI, new visual consent flows.
- CareKit 2.0 split into multiple modular pods (Care Plan, Symptom Tracking, Insights, Connect). Easier to adopt parts.
- Both frameworks now consume HealthKit's clinical records as input for tracking + analysis.

## Photo/Video Effects with Depth (503)

- iPhone 7+ Plus, X, etc. dual cameras and TrueDepth front camera capture depth maps.
- New `AVDepthData` API exposes the depth map at capture time.
- Vision framework's `VNDetectFaceLandmarksRequest` produces high-precision landmark positions when combined with depth.
- Use cases beyond Portrait Mode: AR mask alignment, custom bokeh, hair-style preview apps, fitness body-measurement apps.

## Cross-references

- Workout-related background audio: 504, 206.
- Privacy framing for sensitive data (HealthKit data is the most sensitive): 718.
- Vision + Core ML combined (e.g., training a model on depth-derived data): 717.
