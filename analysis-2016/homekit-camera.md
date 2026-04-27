# HomeKit Cameras & Home App — WWDC 2016 Analysis

**Sessions covered:** 710 (What's New in HomeKit)

## Headline

HomeKit gets the **dedicated Home app** (built in for iOS 10), expanded **accessory categories** (cameras, doorbells, air conditioners/heaters, humidifiers, air purifiers), automation execution moved to the **Apple TV / iPad** as remote-access gateways, and a new **HomeKit framework on tvOS 10**. Setup of new accessories is collapsed to a single API call.

## What's new at the platform level

### Home app

Apple's first first-party HomeKit app. Available on iPhone, iPad, Apple Watch (watchOS 3). Surfaces accessory control, scenes, and automations. HomeKit Control Center widget brings accessory toggles to the lockscreen and Notification Center on iOS.

### Remote access + automation now run on Apple TV (and iPad)

In tvOS 10, the Apple TV is a HomeKit hub:
- Runs all user automations from the cloud / locally.
- Provides remote-access gateway (was on Apple TV but limited).
- Can serve administrative shared-user permissions.

iPad gains the same role. Multiple hubs in the same home auto-coordinate the HomeKit network. Picks the optimal path automatically — no user configuration.

### HomeKit on tvOS

Brand new framework for tvOS apps to view, control, and execute scenes. Siri remote integration: "Turn off the lights" works through the Apple TV's microphone.

## New accessory categories

| Category | Can do |
|----------|--------|
| Air conditioner / heater | Target temp, current temp, fan mode, swing mode |
| Air purifier | Target/current state, filter life, rotation speed |
| Humidifier / dehumidifier | Target humidity, current, water level |
| **Camera** | Live video stream, snapshots, all settings (night vision, tilt, zoom, mirror), microphone & speaker |
| **Doorbell** | Press event + chime volume + visual indicator |
| **Doorbell + camera combo** | Auto-snapshots on press, rich notification UI |

## Camera API — `HMCameraProfile`

Cameras are complex (many services and characteristics), so HomeKit wraps them in a high-level **`HMCameraProfile`** object exposed via `accessory.cameraProfiles[i]`.

```swift
guard let profile = accessory.cameraProfiles?.first else { return }

// Live stream
profile.streamControl?.startStream()
// in delegate cameraStreamControl(_:didStartStream:):
let view = HMCameraView()
view.cameraSource = profile.streamControl?.cameraStream
self.view.addSubview(view)

// Snapshot
profile.snapshotControl?.takeSnapshot()
// in delegate cameraSnapshotControl(_:didTake snapshot:):
imageView.cameraSource = snapshot

// Settings (any may be nil if unsupported)
profile.settingsControl?.nightVision?.writeValue(true) { _ in }
profile.settingsControl?.opticalZoom?.writeValue(2.0) { _ in }

// Audio
profile.microphoneControl?.mute?.writeValue(false) { _ in }
profile.speakerControl?.volume?.writeValue(0.5) { _ in }
```

`HMCameraView` (iOS, tvOS) and `HMWKInterfaceCamera` (watchOS) accept either a `HMCameraStream` (live) or `HMCameraSnapshot` (still). Same `cameraSource` property.

## Doorbell + camera combination — rich notifications (HIDDEN GEM)

When a user has a doorbell + camera + door lock all assigned to the same Room (e.g. "Entryway"), HomeKit **automatically associates** them. When the doorbell rings:
- A rich notification fires with a snapshot from the camera.
- Notification actions: Intercom (open audio), Unlock, View Live (full live video stream).
- All happen without your app code; HomeKit links the services if they share a Room.

Same notification works on Apple Watch — tapping the snapshot starts a live stream to the wrist.

## New API improvements (small but powerful)

### Primary service

`HMService.isPrimaryService` — for accessories with multiple services (a fan-with-light), the accessory tells you which is the primary. Show context-appropriate UI: a "fan with light" vs a "light with fan" surfaces differently.

### Linked services

A switch with three outlets links to all three: `service.linkedServices` returns the related services. Now your switch UI can show "all three outlet states are off" because they're linked.

### Valid values for characteristics

`HMCharacteristicMetadata.validValues` — when an accessory only supports a subset of an Apple-defined enumeration (e.g. an AC that doesn't support heating omits the `.heat` and `.auto` values from `targetHeatingCoolingState`), the accessory advertises which values are valid. UI shows only the supported options.

## Single-API setup flow (BEST PRACTICE)

Accessory setup used to require multiple steps — discovery, optional Wi-Fi configuration via External Accessory framework, scan QR/HomeKit code, name, choose room, mark as favorite.

iOS 10 collapses this into one method:

```swift
home.addAndSetupAccessories(in: primaryHome) { error in
    // Apple's full setup UI runs to completion
}
```

The system UI handles network onboarding, code scanning, naming, room assignment, associated-service selection (e.g. "this outlet controls a fan"), favorites toggle. **Use this** — it gives every HomeKit app the same predictable user experience.

## Sharing model improvements

- **Administrative shared users** — granted by the home owner, can change configuration (add/remove accessories, invite more users).
- **Per-user remote-access** control — the owner can grant or deny remote access per shared user.

## Best practices summary

- Always use `addAndSetupAccessories` — don't roll your own setup flow.
- Check `isPrimaryService` and `linkedServices` to render context-aware UI.
- Honor `validValues` — never offer values the accessory rejected.
- For cameras, use `HMCameraView` / `HMWKInterfaceCamera` — they handle source-type switching for you.
- Use `HMHomeManagerDelegate` to react when remote access changes (the user might revoke it).

## Hidden gems

- Doorbell-camera-lock auto-association by Room means no code is needed for the rich-notification + intercom + unlock pattern.
- `HMCameraSettingsControl` characteristics may be nil — always optional-chain (`profile.settingsControl?.nightVision?`).
- The Home app on Apple Watch supports live camera streaming with one tap — your watch UI can leverage `HMWKInterfaceCamera` similarly.
- HomeKit on tvOS means a TV remote can become a smart-home controller via Siri.

## Cross-references

- Notifications + rich UI for doorbell → analysis-2016/ios10-notifications.md
- Home app accessibility and design → analysis-2016/accessibility-design.md
- IoT security model → analysis-2016/security-network.md
