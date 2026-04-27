# WWDC 2020 — HealthKit, ResearchKit, CareKit, FHIR

WWDC 2020 was a significant year for the **Health stack**: mobility metrics in HealthKit (covered in detail in watchos-7.md), continued evolution of CareKit and ResearchKit, **FHIR support** for clinical health records, and the addition of **handling FHIR without getting burned**.

## Sessions Analyzed
- 10182 — What's new in HealthKit
- 10184 — Synchronize health data with HealthKit
- 10656 — Beyond counting steps (covered in detail in watchos-7.md)
- 10664 — Getting started with HealthKit
- 10669 — Handling FHIR without getting burned
- 10151 — What's new in CareKit
- 10216 — What's new in ResearchKit

## Mobility Metrics — Recap

Eight new HealthKit data types capture lab-grade gait analysis from passive iPhone + Apple Watch wear. Detailed coverage is in [watchos-7.md](watchos-7.md). Briefly:
- **iPhone**: walking speed, step length, double-support time, walking asymmetry
- **Apple Watch**: stair speed up/down, predicted six-minute walk distance, improved VO₂ max

These transform health-app categories like injury recovery, cardiopulmonary monitoring, and aging-with-independence.

## What's New in HealthKit (10182)

Beyond mobility metrics:
- **Symptom tracking** as a first-class data type
- **Sleep stages** (REM, core, deep) — apps can read/write
- **Electrocardiogram (ECG)** — newer Apple Watch models record; HealthKit exposes the waveform
- **Hearing health** — environmental sound levels, headphone audio levels
- **Mobility-related types** beyond gait (stand hours, exercise minutes refinements)
- **Period tracking** improvements

### `HKAnchoredObjectQuery` for Sync

For long-running apps that observe health data changes, use `HKAnchoredObjectQuery` with a saved anchor (token) to fetch only what's changed since last sync. Robust to deletes, modifications, and out-of-order events. Use the `updateHandler` for live observation.

## Sync Strategies (10184)

Cross-device HealthKit sync got more reliable for:
- Apps that record on Apple Watch and need consistent state on iPhone
- Background updates for observers
- Conflict resolution when two devices write simultaneously

Best practice: don't poll; use observer queries with background delivery (`enableBackgroundDelivery(for:frequency:withCompletion:)`).

## FHIR — Clinical Health Records (10669)

FHIR (Fast Healthcare Interoperability Resources) is HL7's standard for clinical health record exchange. Apple Health on iPhone can now connect to participating health systems and pull the user's clinical records (diagnoses, immunizations, lab results, medications). HealthKit exposes these to apps via:

```swift
// Request authorization for clinical record types
healthStore.requestAuthorization(toShare: nil, read: [HKClinicalType.allergyRecordType()]) { ... }

// Query for clinical records
let query = HKSampleQuery(sampleType: ..., predicate: ..., limit: ...) { ... }
```

### Why "Without Getting Burned"

FHIR data is messy. The session covers:
- **Variable schema** — different EHR systems output FHIR slightly differently. Don't assume any field is present.
- **Multiple resource versions** — DSTU2, STU3, R4. Apple normalizes to specific versions but parse defensively.
- **Privacy posture** — clinical data is highly sensitive. Don't send to your server unless absolutely necessary; never log it.
- **Patient identity context** — your app sees data for the currently signed-in iCloud-Health user; treat the source as the patient.

Use cases:
- Surface vaccine records in an immunization-tracking app
- Cross-reference medications a user takes for safe dosage advice
- Display lab results in patient-facing apps

## CareKit (10151)

CareKit is Apple's open-source framework for patient care/management apps. 2020 additions:
- **Synchronization with cloud-based CareKit stores** (via the `CareKitStore` protocol abstraction)
- **Time-windowed task definitions** for medications and activities
- **Updated Charting** views for health trends visualization
- **Better contact integration** for care teams

CareKit is open-source; you can subclass and replace components freely. Used by clinical research and patient-engagement apps.

## ResearchKit (10216)

ResearchKit is Apple's open-source framework for **clinical research surveys, consent flows, and active task collection** (e.g., reaction-time tests, hearing tests). 2020 additions:
- New active tasks (e.g., the **9-Hole Peg Test** for fine motor function)
- Improved survey UI (modernized looks)
- Better integration with HealthKit for combining survey responses with sensor data
- Improved consent flow templates

The "Action Classification" + "Body Pose" Vision additions (covered in [ml-vision-coreml.md](ml-vision-coreml.md)) compose well with ResearchKit for in-clinic-style movement assessments at home.

## HealthKit Authorization & Privacy

Critical reminders:
- HealthKit authorization is **per-data-type, per-direction** (read vs. share). Request only what you need.
- Apps can never see what data the user hasn't shared. There's no way to detect denial vs. no-data.
- For clinical records (FHIR), the user grants access per-record-type per-app.
- Any HealthKit data sent off-device must comply with HIPAA/relevant regulations in your jurisdiction.

## Cross-References
- [watchos-7.md](watchos-7.md) — Mobility metrics in detail.
- [privacy-security-network.md](privacy-security-network.md) — Privacy considerations for sensitive health data.
- [ml-vision-coreml.md](ml-vision-coreml.md) — Vision body pose pairs with health/fitness use cases.

## Adoption Checklist
- [ ] If a fitness/health app, evaluate which of the eight mobility metrics enrich your insights.
- [ ] Use `HKAnchoredObjectQuery` instead of polling for sync.
- [ ] Enable background delivery for observer queries to keep data fresh.
- [ ] If your app handles patient records, evaluate HealthKit clinical record types.
- [ ] When parsing FHIR, code defensively for missing/extra fields.
- [ ] Never log clinical data; minimize off-device transmission.
- [ ] If a research app, check ResearchKit's active tasks for ones suited to your study.
- [ ] If a care-management app, evaluate CareKit's framework primitives.
