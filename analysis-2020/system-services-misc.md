# WWDC 2020 — System Services: Background Execution, Notifications, Enterprise, Education, Misc

A grab-bag of important system-level frameworks and updates that don't fit neatly elsewhere: background execution mechanics, push notifications evolution, enterprise/MDM, education/ClassKit, CarPlay, and CareKit/Wallet.

## Sessions Analyzed
- 10063 — Background execution demystified (gateway)
- 10095 — The Push Notifications primer
- 10025 — Meet Push Notifications Console (companion to other notification sessions)
- 10222 — Create custom apps for employees
- 10204 — Create great enterprise apps: A chat with Box's Aaron Levie
- 10140 — Build location-aware enterprise apps
- 10142 — Build scalable enterprise app suites
- 10138 — Discover AppleSeed for IT and Managed Software Updates
- 10139 — Leverage enterprise identity and authentication
- 10223 — Deploy Apple devices using zero-touch
- 10667 — Custom app distribution with Apple Business Manager
- 10672 — What's new in ClassKit
- 10005 — What's new in assessment
- 10658 — What's new in education
- 10635 — Accelerate your app with CarPlay
- 10160 — Formatters: Make data human-friendly
- 10696 — Uniform Type Identifiers — a reintroduction
- 10650 — Sync a Core Data store with the CloudKit public database

## Background Execution Demystified (10063)

The single best framing of why background execution APIs behave the way they do. Apple's seven factors that determine whether your background work runs:

1. **Critically low battery** — system pauses discretionary work to ensure the user can reach a charger.
2. **Low Power Mode** — user-toggled. Listen for `NSProcessInfoPowerStateDidChange` notifications and proactively reduce work.
3. **App usage** — the system prefers to run apps the user actually opens. The on-device predictive engine learns when you typically launch your app.
4. **App Switcher presence** — swiping an app away from the App Switcher signals "don't run this in the background" for many modes.
5. **Background App Refresh switch** — applies to **all** the modes covered, not just App Refresh tasks.
6. **System budgets** — energy and cellular data budgets that the system replenishes throughout the day. Going over starves you.
7. **Rate-limiting** — system spaces out launches based on each mode's purpose and your usage patterns.

### The Modes

#### Background App Refresh Tasks
For periodic refresh (social feed, email, stocks). Distributed throughout the day; system learns when you typically use the app and schedules just before. Target: under 100KB cellular per launch. **Always call `setTaskCompleted(success:)`** to let the system suspend you immediately.

#### Background Pushes
Visible notification optional — push triggers app launch, you fetch new content. Critically: **rate-limited even with frequent pushes**. 14 incoming pushes in a window may produce 7 launches; system delays delivery to keep launches at ~15-minute intervals. Don't worry about delivery rate; focus on launch interval.

#### Background URLSessions
File downloads/uploads off-loaded to the system. **Discretionary** = system picks an optimal time (Wi-Fi + plugged in is ideal). **Non-discretionary** = ASAP. Apps in foreground default to non-discretionary; apps in background to discretionary. `sessionSendsLaunchEvents = YES` requests app re-launch when transfer completes.

#### Background Processing Tasks
Multi-minute work for maintenance/training. Runs while plugged in, when the user isn't actively using the device. Most of the seven factors don't apply (no battery/Low Power gate). User must have launched the app in the past couple of weeks. Daily plug-in = daily run for healthy users.

### Practical Levers

You have most influence over **system budgets**:
- Minimize energy: avoid bringing up GPS / accelerometer / camera unless needed
- Parallelize network I/O
- Limit cellular data usage; offload large transfers to discretionary background URL sessions
- Always call completion handlers immediately when work is done

## Push Notifications

Multiple sessions covered evolutionary improvements:
- **APNS API** — JSON payload with new fields for richer notification UIs
- **Notification grouping** — group by `thread-identifier` for stack-based presentation
- **Notification Service Extension** — modify content before delivery (decrypt E2E payloads, attach images)
- **Critical alerts** for medical/safety apps (entitlement required)
- **Push to Talk** infrastructure (debuted later but architecture forming)
- **Background pushes** for app refresh triggers (covered in 10063)

The Push Notifications Console (Tech Talk) gave Apple-hosted UI for sending test notifications without command-line `apnsd`.

## Enterprise & MDM

Apple Business Manager + MDM gained:
- **Custom app distribution** — sell privately to specific organizations (10667)
- **Zero-touch deployment** — devices auto-enroll on first activation (10223)
- **Declarative device management** (10138 / 10639) — devices sync state declaratively rather than receiving every command, dramatically improving reliability
- **AppleSeed for IT** — IT admins can test pre-release OS/MDM features
- **Managed Apple IDs** for school/work (with Family Sharing limits)

For enterprise app developers (10222): build apps tailored to your organization's workflows, distribute via Apple Business Manager Custom App, integrate with enterprise identity providers (Azure AD, Okta) via the new identity APIs (10139).

Aaron Levie of Box's chat (10204) is a high-level discussion of why enterprise apps should think mobile-first now that iPad is a credible computer.

Location-aware enterprise apps (10140) covers indoor positioning, region monitoring, and the privacy considerations specific to enterprise (employees may legitimately need their location tracked for their job, but the design should respect them).

## ClassKit & Education (10672, 10005, 10658)

ClassKit lets education apps integrate with **Schoolwork** — teachers assign activities, students complete them, progress flows back. 2020 additions:
- More activity types (assessments with auto-graded scoring)
- Better integration with Apple Books for reading assignments
- Improved progress reporting

Assessment Mode (10005) for testing apps — locks down device features during exams to prevent cheating. Critical for high-stakes testing.

Education broadly (10658) covers Schoolwork updates, Classroom updates, and education-specific MDM features.

## CarPlay (10635)

CarPlay app categories continue to expand. 2020 added:
- **Parking apps**
- **Charging station apps** (EV)
- **Quick food ordering**
- **Driving task apps** (e.g., truck logging)

App templates limit UI complexity for safe driving. For audio apps (already supported pre-2020), CarPlay session manages playback handoff between phone and car.

## Formatters: Make Data Human-Friendly (10160)

Foundation gained `Formatter` API improvements: easier-to-use date/number/measurement formatters, proper localization, locale-aware ordinals. The session covers practical patterns:
- `RelativeDateTimeFormatter` for "5 minutes ago" / "in 2 days"
- `ListFormatter` for "Alice, Bob, and Charlie"
- `MeasurementFormatter` for unit conversions
- `PersonNameComponentsFormatter` for proper name display across locales
- `DateIntervalFormatter` for "Mar 1 – Apr 5"

The pattern: **stop hand-rolling string concatenation for human-facing values** — Foundation has it covered.

## Uniform Type Identifiers — Reintroduction (10696)

UTIs got a **modern Swift API** with type-safe values: `UTType.image`, `UTType.json`, etc. Replaces the ad-hoc string CFStrings (`kUTTypeImage`). Used by the new SwiftUI drag-drop API, file pickers, and document types.

```swift
import UniformTypeIdentifiers
let type = UTType.png
type.conforms(to: .image)  // true
type.preferredFilenameExtension  // "png"
let custom = UTType("com.example.mytype")
```

## Core Data + CloudKit Public Database (10650)

`NSPersistentCloudKitContainer` (introduced WWDC 2019) now supports the **CloudKit public database** in addition to private. Use cases: shared content across all users (recipes, world data), with the same Core Data programming model.

Configuration:
```swift
let description = NSPersistentStoreDescription(...)
description.cloudKitContainerOptions?.databaseScope = .public
```

Caveats: public database has different conflict-resolution semantics; treat your local Core Data as a cache of the cloud-of-record.

## Wallet & Apple Pay (10662)

Covered briefly in [app-services-storekit-store.md](app-services-storekit-store.md). Highlights:
- SwiftUI `PayWithApplePayButton`
- Improved card management
- Health/ID cards (rolling out gradually)

## Cross-References
- [swiftui-2-foundation.md](swiftui-2-foundation.md) — UTI integration with SwiftUI drag-drop.
- [privacy-security-network.md](privacy-security-network.md) — Push notification privacy, MDM-deployed DNS settings.
- [app-services-storekit-store.md](app-services-storekit-store.md) — Wallet and managed devices.

## Adoption Checklist
- [ ] Audit your background-mode usage against the seven factors — make sure budgets aren't burning.
- [ ] Always call completion handlers immediately when background work is done.
- [ ] Migrate to typed `UTType` values from the old kUTTypeXxx strings.
- [ ] Replace hand-rolled date/list/name formatting with Foundation's `Formatter`s.
- [ ] If a CloudKit Core Data app, evaluate public database support.
- [ ] If an enterprise app, evaluate Apple Business Manager Custom Apps.
- [ ] If education, evaluate ClassKit and Schoolwork integration.
- [ ] If a CarPlay app, evaluate the new template categories.
- [ ] Monitor APNS topics + use `thread-identifier` for grouped notifications.
