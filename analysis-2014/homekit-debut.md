# HomeKit Debut — WWDC 2014 Analysis

**Sessions covered:** 213 (Introducing HomeKit)

## Headline

HomeKit is iOS 8's framework for **smart home device control with end-to-end encryption, system-wide consistency, and Siri natural-language integration**. Apps from different vendors now talk to home accessories through a common database, so the user's home setup persists across apps. The HomeKit Accessory Protocol (HAP) and the MFi program let manufacturers ship certified accessories.

## The Mental Model (session 213)

- **One Common Database in iOS** — every accessory, room, zone, action set, and trigger is stored centrally. Multiple apps see and edit the same data. The user configures their kitchen lights once; every HomeKit-aware app sees them (213).
- **Siri integration** — homes, rooms, accessories, services, service types, zones, action sets, and triggers are ALL recognized by Siri by name. "Turn off the lights in the living room" works with no per-app effort (213).
- **End-to-end encryption** between iOS and the accessory. The accessory protocol assumes the network might be untrusted; the iOS-accessory channel is authenticated and encrypted in both directions (213).
- **iCloud-mediated remote access** for free — no extra code from your app. When the user is away, an Apple TV at home (or later, HomePod) bridges the connection (213).
- **HomeKit APIs only work in foreground** — no background polling, no surprise device manipulation. The user always knows when an app is talking to their home (213).

## The Object Hierarchy (session 213)

```
HMHomeManager
└── HMHome (multiple homes per user, e.g. main + cabin)
    ├── HMRoom (Living Room, Kitchen, Bedroom...)
    ├── HMAccessory (Garage Door Opener, Thermostat, Lock...)
    │   └── HMService (Garage Door, Light Bulb, Thermostat...)
    │       └── HMCharacteristic (PowerState, Temperature, LockState...)
    ├── HMZone (arbitrary groupings: Upstairs, Downstairs, Bedrooms)
    ├── HMServiceGroup (cross-accessory groupings: All Nightlights)
    ├── HMActionSet (a "scene": Goodnight, Movie Mode)
    │   └── HMCharacteristicWriteAction
    └── HMTimerTrigger (fires Action Sets at scheduled times)
```

## Setup Flow — first-time user (session 213)

1. Create `HMHomeManager`, set delegate, wait for `homeManagerDidUpdateHomes:` (data may be loading).
2. If no homes exist, prompt for a home name and call `addHomeWithName:completionHandler:`.
3. User adds rooms via your UI; you call `home.addRoomWithName:completionHandler:`.
4. Use `HMAccessoryBrowser` to discover unconfigured accessories on the local network. Implement `accessoryBrowser:didFindNewAccessory:` and `:didRemoveNewAccessory:`.
5. User picks an accessory; you call `home.addAccessory:completionHandler:`. iOS prompts the user for the accessory's setup code (printed on the device, shown on its display, or scanable HomeKit pairing code) (213).
6. User assigns the accessory to a room and gives it a name. **Names must be unique within a home**. Siri uses these names directly.

## Working With Accessories (session 213)

- **Reachability** can change at any moment — accessories drop off Wi-Fi, get powered down, lose Bluetooth range. Implement `accessoryDidUpdateReachability:` to update your UI.
- **Services** are functional groupings of characteristics. A garage door opener accessory exposes:
  - `HMServiceTypeAccessoryInformation` (always present, gives manufacturer/model/serial)
  - `HMServiceTypeGarageDoorOpener` (the motor)
  - `HMServiceTypeLightbulb` (the light on the opener)
- **Unnamed services are operational** (firmware update, configuration) — don't show them in your user-facing UI. **Named services are user-facing** — light bulbs the user wants to address by name (213).
- HIDDEN GEM: services have **Apple-defined types** (`HMServiceTypeLightbulb`, `HMServiceTypeThermostat`, etc.). Siri understands these types semantically, so "Hey Siri, turn off the lights" works across vendors without per-vendor mapping (213).
- **Characteristics**: read-only (`CurrentTemperature`), write-only (`Identify`), or read-write (`TargetTemperature`). All access is asynchronous via completion handlers — accessories may be slow.
- **The `Identify` characteristic is special and required on every accessory**. Sending it makes the accessory blink/beep/flash to help the user pick it out from a pile of identical-looking devices during setup (213).

## Bridges (session 213)

- A **Bridge** is an accessory that proxies for non-HomeKit-native devices behind it (Zigbee bulbs behind a Hue hub, Z-Wave devices behind a Vera). The bridge speaks HAP to iOS; whatever protocol it wants behind it.
- HIDDEN GEM: from your app's perspective, **devices behind a bridge are just regular accessories**. You list, pair, and control them the same way. The protocol translation is the bridge's problem (213).
- The bridge itself appears as one accessory; each device behind it appears as additional accessories whose `bridgedAccessoryIdentifier` ties them to the bridge.

## Action Sets and Triggers (session 213)

- **`HMActionSet`** = a named scene composed of `HMCharacteristicWriteAction`s. "Goodnight" might lock the door, close the garage, set the thermostat to 68°, turn off all lights.
- **Order of execution within an Action Set is undefined** — they're treated as a parallel best-effort batch (213).
- **`HMTimerTrigger`** fires an Action Set at a scheduled date+time, with optional repetition. **iOS executes triggers in the background even when no app is running** — this is the only HomeKit code path that doesn't require foreground (213).
- Trigger names ARE NOT recognized by Siri (only homes/rooms/accessories/services/zones/action sets are). But Siri can fire an Action Set: "Hey Siri, goodnight" runs the Goodnight scene (213).

## Zones and Service Groups (session 213)

- **Zones** = arbitrary groupings of rooms. "Upstairs" might contain Bedroom + Bath + Office. "Downstairs" might contain Living + Kitchen + Dining. A room can be in any number of zones; this is association, not ownership.
- **Service Groups** = arbitrary groupings of services across accessories. "Nightlights" might bundle the bulb on the coffee maker, the bulb on the microwave, and a dedicated nightlight in the hallway — three different accessories' services, addressable as one. Siri recognizes service group names too.

## Testing Without Hardware: HomeKit Accessory Simulator (session 213)

- Apple ships a separate **HomeKit Accessory Simulator** (downloadable from developer.apple.com — separate from Xcode). Lets you create virtual accessories of any type, simulate firmware updates, simulate bridges with multiple downstream devices.
- HIDDEN GEM: develop your entire HomeKit app against the simulator before any real hardware exists. The simulator behaves identically to real accessories from your app's perspective (213).

## Best Practices

- **Implement EVERY delegate method**. The home is shared with other apps; data changes constantly out from under you. Missing a `homeDidUpdateName:` callback leaves your UI stale (213).
- **Listen for reachability** — the user is going to expect that when you say a light is on, it actually is. If you've lost the connection, dim/disable the controls (213).
- **Don't do anything destructive without confirmation** — turning off all lights is fine; deleting a room or accessory should always confirm.
- **Use the simulator from day one** — even when you have hardware. The simulator can fake failure modes (low battery, comms errors) more easily than real devices.

## Hidden Gems

- HIDDEN GEM: action sets execute via Siri command. "Hey Siri, movie time" runs the Movie Time action set. No glue code; Apple's NLU handles the mapping from spoken phrase to action set name (213).
- HIDDEN GEM: HomeKit characteristics are **self-describing** — they expose units, valid ranges, step values via `HMCharacteristic.metadata`. Build a generic UI that introspects characteristics and renders the right control (slider for percent dimming, segmented for thermostat mode, switch for power state) (213).
- HIDDEN GEM: **HomeKit Accessory Simulator can model any custom characteristic** an accessory manufacturer wants to invent — Apple deliberately allows custom characteristics so innovation isn't blocked. Your app receives them as `HMCharacteristic`s with custom UUIDs (213).
- WARNING: HomeKit network traffic is encrypted, but the local-network discovery (Bonjour) is not. Don't put PII in your Bonjour service names.

## Cross-references

- **App Extensions (205, 217)** — a Today widget showing the user's "Goodnight" button is a natural HomeKit + extension combo.
- **CloudKit (208)** is unrelated to HomeKit's iCloud-mediated remote access — they're separate iCloud services. HomeKit's remote access is internal to Apple.
- **Privacy (715)** — HomeKit-linked apps must ship a Privacy Policy URL.
- **Continuity / Handoff (219, 506)** — HomeKit isn't part of Continuity but the design philosophy (system-wide consistency) is shared.

## Migration Guidance

- **No migration story** — this is a brand new framework with no predecessor. Apps that were doing ad-hoc smart-home integration via the HTTP REST APIs of Hue, Nest, etc., should evaluate adopting HomeKit:
  - Pro: your app benefits from system-wide accessory database, Siri, secure remote access, MFi-certified hardware.
  - Con: your app is gated to MFi-certified accessories. Hue requires Apple's MFi certification on the bridge; Nest never went HomeKit. Apps that need to support specific non-MFi devices may have to keep a parallel non-HomeKit code path.
- For existing accessory manufacturers: HomeKit certification (MFi program, MFI HomeKit chip on the device) is required — the secure pairing relies on a hardware crypto chip Apple provides via MFi.
