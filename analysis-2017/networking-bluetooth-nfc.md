# Networking, Bluetooth, NFC, CarPlay & HomeKit — WWDC 2017 Analysis

**Sessions covered:** 707 (Advances in Networking, Part 1), 709 (Advances in Networking, Part 2), 706 (Modernizing Grand Central Dispatch Usage), 712 (What's New in Core Bluetooth), 713 (What's New in Location Technologies), 714 (What's New in Apple Pay & Wallet), 717 (Developing Wireless CarPlay Systems), 718 (Introducing Core NFC), 719 (Enabling Your App for CarPlay), 705 (What's New in HomeKit), 701 (Your Apps and Evolving Network Security Standards), 708 (Best Practices and What's New in User Notifications)

## Headline

iOS 11 brings two major framework debuts — **Core NFC** (read NDEF-formatted NFC tags from iPhone 7+) and **L2CAP channels for Core Bluetooth** (high-throughput streaming peripherals like medical devices) — alongside upgrades to URLSession (multipath TCP, mobility-aware connections), location (visit monitoring revamp), HomeKit (Apple-certified accessory test for makers), and CarPlay (3rd-party navigation apps).

## Core NFC (718)

iPhone 7 / 7 Plus / 8 / 8 Plus / X gain a **read-only NDEF tag reader** API.

```swift
let session = NFCNDEFReaderSession(delegate: self,
                                   queue: nil,
                                   invalidateAfterFirstRead: true)
session.alertMessage = "Hold your iPhone near a tag."
session.begin()

// Delegate
func readerSession(_ session: NFCNDEFReaderSession,
                   didDetectNDEFs messages: [NFCNDEFMessage]) { … }
```

- Read-only in 2017 (write support is several years out).
- iOS 11 requires the user to have the app open and tap "Scan" — there's NO background tag detection (Apple ships that in iOS 13).
- Supports the four NDEF record types (Text, URI, Smart Poster, External). No raw ISO 7816 / Felica access in this release.
- **WARNING**: requires entitlement `com.apple.developer.nfc.readersession.formats` and `NFCReaderUsageDescription` in Info.plist. Forgetting either crashes immediately on `begin()`.
- **HIDDEN GEM**: even though the user has to launch your app, the app DOES NOT need to be foreground when the tag arrives — `begin()` works from a notification action handler, allowing scan-from-lock-screen flows.

## Core Bluetooth Enhancements (712)

- **L2CAP channels** — high-throughput, low-latency byte streams over BLE (Bluetooth 4.1+). Existing GATT characteristic-based transfer caps at ~10 kbps; L2CAP comfortably hits 100+ kbps. Critical for medical devices, audio streaming sensors, file transfer.

```swift
peripheral.openL2CAPChannel(0x80)
// Delegate
func peripheral(_ peripheral: CBPeripheral, didOpen channel: CBL2CAPChannel?, error: Error?) {
    guard let channel = channel else { return }
    let stream = channel.outputStream  // CFWriteStream
    stream.open()
    stream.write(data, maxLength: data.count)
}
```

- **watchOS support for Core Bluetooth**: the Apple Watch Series 3 (LTE/non-LTE) can now talk Bluetooth LE directly to peripherals, enabling independent watch-to-sensor flows without iPhone proxying.
- New CBPeripheralManager state restoration: peripheral mode persists across app suspension. Subscribed centrals don't drop reconnect.
- **PERFORMANCE**: `CBManagerStateUnauthorized` is now distinguished from `unsupported`. Show better UX based on whether the user denied or the device truly lacks BLE.

## URLSession Mobility (707, 709)

iOS 11 introduces **multipath TCP** for `URLSession`:

- `URLSessionConfiguration.multipathServiceType = .handover | .interactive | .aggregate`
- `.handover`: keeps a connection alive across Wi-Fi → cellular → Wi-Fi handoffs without a connection drop. Voice/video apps love this.
- `.interactive`: keeps latency low using whichever network is best.
- `.aggregate`: bonds Wi-Fi + cellular bandwidth (Apple internal use only initially; needs server-side cooperation).

**HIDDEN GEM**: streaming audio sessions can use `.handover` to survive elevator-and-back transitions seamlessly. Server must support the MPTCP RFC 6824 protocol (no transparent fallback proxy as of 2017).

## TLS 1.2 Mandatory (701)

- App Transport Security (ATS) defaulting to TLS 1.2 has been in effect since iOS 9 with exceptions allowed.
- iOS 11 **deprecates** several `NSAllowsArbitraryLoads` style escape hatches for App Store submissions; you must justify them in App Review notes.
- New evolution: forward secrecy via ECDHE cipher suites is now required for hosts you don't list in `NSExceptionDomains`.
- **PERFORMANCE**: HTTP/2 server push is honored by `URLSession` automatically. Hint your CDN to push CSS/JS for faster first-contentful-paint on hybrid apps.

## Modernizing Grand Central Dispatch (706)

The session reframes GCD usage for the modern multi-core (and Apple-Watch single-core) world:

- **Use queue hierarchies, not concurrent queues for everything.** Each level of concurrency adds thread allocation cost. Many apps unnecessarily hop between independent concurrent queues.
- **`DispatchQoS`** matters: `.userInteractive`, `.userInitiated`, `.utility`, `.background`. iOS will scale clock speed and core allocation accordingly. Picking the wrong QoS hurts battery on the low end and responsiveness on the high end.
- **WARNING**: `dispatch_once_t` / `DispatchOnce` MUST be in static or global storage. Never put it in an instance variable or heap memory — re-use of memory addresses can cause the once block to run twice. The static analyzer (Xcode 9) now warns on this.
- **HIDDEN GEM**: `DispatchWorkItem(qos:flags:block:)` with `.enforceQoS` flag prevents priority inversion when a high-priority work item is enqueued behind low-priority items.

## Notifications (708)

- Provisional authorization (`UNAuthorizationOptions.provisional`) — silent push to Notification Center for apps the user hasn't allowed yet, no permission alert. Lets users discover your notifications gradually.
- Notification grouping — set `threadIdentifier` on each `UNMutableNotificationContent`; iOS visually groups them in lock screen and Notification Center.
- **`UNUserNotificationCenter.removeDeliveredNotifications(withIdentifiers:)`** lets you clear notifications when the user has read them in-app — manage badge counts cleanly.
- **HIDDEN GEM**: critical alert sounds (medical/safety) require special entitlement (`com.apple.developer.usernotifications.critical-alerts`) and override Do Not Disturb. Apple reviews this entitlement carefully.

## Location Improvements (713)

- Visit monitoring (`CLLocationManager.startMonitoringVisits()`) re-architected for power efficiency. iOS 11 fuses Wi-Fi, motion, and prior visit history — visit detection now wakes apps with much higher precision.
- `requestWhenInUseAuthorization` now MUST be called BEFORE accessing any location API; calls before authorization silently no-op rather than implicitly prompting.
- New: `CLLocationManager.activityType = .otherNavigation | .automotiveNavigation | .fitness | .other | .airborne` — added `.airborne` for drone / aviation apps. The location stack tunes filter aggressiveness based on activity.

## HomeKit (705)

- **`HMAccessoryProtocol` for makers**: Apple-defined HAP over IP. Hobbyist hardware can self-certify with a less expensive certification process and still ship to consumers.
- New characteristic types: power management (notifications when accessory is offline), water leak sensor, smoke sensor, occupancy sensor.
- **HIDDEN GEM**: HomePod (announced WWDC 2017, ships fall 2017) is a HomeKit hub natively. No Apple TV / iPad-as-hub required for a household with a HomePod.

## Apple Pay & Wallet (714)

- **Pay messaging** — peer-to-peer payments via iMessage become a Wallet domain.
- Web payments adopted by Safari with `ApplePaySession.canMakePayments()` JS API.
- **Business Chat** (separate session 240) integrates Apple Pay for in-conversation purchases.

## CarPlay 3rd-Party Apps (719, 717)

- iOS 11 opens CarPlay to **third-party navigation apps** (limited initially to a handful of vendors with formal partnership; broadly opened in iOS 12).
- Wireless CarPlay support across more head units. Pairing flow: Bluetooth handshake → Wi-Fi data transfer.
- App templates for audio, messaging, voice-over-cellular, and now navigation.
- **WARNING**: CarPlay app interface is template-driven (CarPlay UI is rendered by the head unit, not your app). You provide a list of cells, the system renders. No custom drawing is allowed — by design, for safety.

## Cross-references

- See `swift4-language-codable.md` — `Codable` is ideal for HomeKit characteristic JSON.
- See `arkit-debut.md` — Core Bluetooth + ARKit can build location-tagged AR experiences with BLE beacons.
