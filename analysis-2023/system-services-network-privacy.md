# WWDC 2023 — System Services, Networking, Privacy & Security

The "infrastructure" tier — Network framework with L4S, CKSyncEngine, Virtualization, Calendar/EventKit, privacy manifests, code signing for SDKs, passkeys at work.

## Sessions Analyzed
- 10004 — Reduce network delays with L4S
- 10002 — Ready, set, relay: Protect app traffic with network relays
- 10006 — Build robust and resumable file transfers
- 10188 — Sync to iCloud with CKSyncEngine
- 10186 — What's new in Core Data
- 10052 — Discover Calendar and EventKit
- 10007 — Create seamless experiences with Virtualization
- 10150 — Optimize CarPlay for vehicle systems
- 10146 — Meet Core Location for spatial computing
- 10147 — Meet Core Location Monitor
- 10180 — Discover streamlined location updates
- 10060 — Get started with privacy manifests
- 10061 — Verify app dependencies with digital signatures
- 10053 — What's new in privacy
- 10266 — Protect your Mac app with environment constraints
- 10263 — Deploy passkeys at work
- 10040 — What's new in managing Apple devices
- 10041 — Explore advances in declarative device management
- 10039 — Meet device management for Apple Watch
- 10254 — Do more with Managed Apple IDs

## L4S: Sub-Millisecond Network Latency (10004)

**L4S (Low Latency, Low Loss, Scalable Throughput)** is a new IETF standard. iOS 17 supports it in Network framework and URLSession.

The problem: traditional TCP creates "bufferbloat" when reaching capacity — packets queue, latency spikes from 10ms to hundreds of ms.

L4S uses ECN (Explicit Congestion Notification) marking at routers to signal congestion BEFORE buffers fill. Senders react instantly, keeping latency low.

Result: video calls, gaming, Live Activities can stay in single-digit milliseconds even under network load.

How to opt in:
```swift
var options = NWProtocolTCP.Options()
options.enableL4S = true
```

URLSession opts in by default for HTTP/3. L4S requires server + path support — limited deployment in 2023, expanding throughout 2024.

## Network Relays (10002)

iOS 17 adds support for OHTTP-based relays. Apps can route traffic through privacy-preserving relays:

```swift
let relay = NWRelay.Source(...)
let configuration = NWParameters.tls
configuration.setRelaySource(relay)
```

Use cases:
- Apps with sensitive traffic.
- Enterprise apps that must traverse a known proxy.
- Privacy-preserving telemetry.

Apple's iCloud Private Relay uses a similar architecture.

## Resumable File Transfers (10006)

`URLSession.bytes(for:)` has had streaming reads. Now downloads support EXPLICIT RESUMABILITY across app launches:

```swift
let task = URLSession.shared.downloadTask(with: url) { ... }
task.resume()
// later, on relaunch:
let resumeData = task.cancel(byProducingResumeData:)
let newTask = URLSession.shared.downloadTask(withResumeData: resumeData)
```

Background sessions get smarter retry; partial transfers persist across reboot. Critical for game asset downloads, podcast apps, document sync.

## CKSyncEngine (10188)

Brand-new HIGH-LEVEL API for CloudKit sync. Replaces the old `CKDatabaseSubscription` + manual change-token bookkeeping.

```swift
let engine = CKSyncEngine(configuration: .init(database: db, stateSerialization: nil, delegate: self))
try await engine.sendChanges()
try await engine.fetchChanges()
```

`CKSyncEngineDelegate` callbacks:
- `nextRecordZoneChangeBatch(_:syncEngine:)` — what to upload next.
- `handleEvent(_:syncEngine:)` — fetch results, conflicts, account changes.

The engine handles:
- Change token persistence
- Retry/backoff
- Push notification subscription setup
- Conflict resolution (with your delegate input)

Migration from the lower-level CloudKit APIs is recommended for new development.

## Core Data Updates (10186)

Core Data still ships and gets improvements:
- Composite attributes (group multiple values under one logical attribute).
- Stage-based progressive loading.
- Better integration with SwiftData (you can read/write the same store).
- Performance improvements for predicates and fetch batches.

## EventKit (10052)

iOS 17 changes the calendar permission model:
- New "write-only" access level — your app can ADD events without seeing existing events. Privacy win.
- Permission prompt updated to reflect this.
- `EKEventStore.requestWriteOnlyAccessToEvents()` for the new level.
- Events your app added are visible; everything else is hidden.

If you only need to add events (a flight booking app, an Eventbrite import), use write-only.

## Virtualization Framework (10007)

macOS Sonoma adds:
- Linux trusted-platform-module (TPM) emulation.
- Networking namespaces (NAT-based isolated networks).
- Snapshots / rollback.
- Rosetta-in-Linux passthrough — run x86_64 Linux binaries inside an arm64 Linux VM.

`VZVirtualMachine` API gains methods for managing these. Used by the new Mac Containerization story (which expanded in 2025).

## Streamlined Location Updates (10180)

The `CLLocationUpdate.liveUpdates` async stream replaces `CLLocationManager` delegates for many use cases:

```swift
for try await update in CLLocationUpdate.liveUpdates() {
  let location = update.location
}
```

- Built on Swift Concurrency.
- Backgrounded automatically when scope task ends.
- Less boilerplate than the delegate model.

Use the delegate API only when you need monitoring (region exit/entry) or significant change handling.

## Privacy Manifests (10060)

A new REQUIRED file (`PrivacyInfo.xcprivacy`) for SDKs and apps that declares:
- What data types are collected
- What "tracking domains" are contacted
- Required reasons for using certain APIs (e.g., `UserDefaults`, file timestamps, disk space)

Apple's API Categories:
- File Timestamp APIs
- System Boot Time APIs
- Disk Space APIs
- Active Keyboard APIs
- User Defaults APIs

Every SDK author MUST include `NSPrivacyAccessedAPITypes` and provide an approved reason for each.

This was previously soft guidance; in 2024 it became a hard App Store submission requirement. Audit your dependencies now.

## SDK Code Signing (10061)

XCFrameworks can now be SIGNED by the author. Xcode 15 verifies the signature at integration time. If a new version of a framework is signed by a DIFFERENT identity, Xcode warns prominently — defending against supply-chain attacks.

```bash
codesign --sign "..." MyFramework.xcframework
```

Apple is leaning on major SDK authors (Firebase, AWS, etc.) to adopt. Privacy manifest and signature are SEPARATE but complementary.

## Environment Constraints (10266)

Mac apps can declare LAUNCH ENVIRONMENT CONSTRAINTS in their entitlements: "must be launched from /Applications", "must be launched by signed parent process X", "must run inside parent bundle Y".

The OS enforces these at exec time. Defends against:
- Helper tools being copied out and run standalone.
- Malware re-launching legitimate binaries from different paths.

Use case: your menu bar app's helper that should ONLY ever be launched by the main app.

## Passkeys at Work (10263)

Passkeys (built on WebAuthn) can now be:
- Provisioned by MDM (Managed Apple ID accounts).
- Synced through enterprise iCloud accounts (no personal Apple ID needed).
- Audited by IT (revocation lists, usage logs).

Combined with Web Apps, this enables "passwordless workplace" deployments. Companies like Canva, GitHub, Salesforce shipped passkey support throughout 2023–2024.

## Device Management (10040, 10041)

Declarative Device Management gets:
- Management properties for iCloud Drive, Apple Pay, AirDrop visibility.
- Status reports — devices push status to MDM proactively (less polling).
- Software update declarations — IT specifies "iOS 17.x by Date Y"; device complies autonomously.
- Apple Watch is now manageable separately from iPhone (10039).

## Pathways

- **Network performance**: 10004 → 10006
- **Privacy & SDK posture**: 10060 → 10061 → 10053
- **iCloud sync**: 10188 → 10186
- **Mac security hardening**: 10266 → 10061
- **MDM admin**: 10040 → 10041 → 10039 → 10254 → 10263

## Hidden Gems

- L4S can drop latency from ~100ms to ~5ms on congested networks WITHOUT throughput loss — but only if every router on the path supports it. Test in real conditions.
- Network Relays use OHTTP (Oblivious HTTP) — the relay sees source IP but not request content; the destination sees content but not source.
- CKSyncEngine PERSISTS its state across app launches via the `stateSerialization` data you provide back to it. Save it to disk after every sync.
- EventKit's write-only mode lets a one-shot booking flow ADD events without ever seeing the user's calendar — major privacy win you can advertise.
- Privacy manifests are PARSED by App Store Connect and shown in the privacy nutrition label automatically. No more manual entry.
- Environment constraints block "helper.app run by Terminal" attack patterns that have been bypassed for years.
- `CLLocationUpdate.liveUpdates` returns nil locations when the user revokes permission mid-stream — handle that case.
- Managed Apple IDs can now own software (App Store purchases, paid apps) — previously they couldn't, blocking enterprise rollouts.
- Declarative Device Management replaces hundreds of MDM commands with a few "declarations" the device interprets — much more robust than imperative commands.
