# Platform Services, Media, Games & Cross-Cutting -- WWDC24 Deep Analysis

Comprehensive analysis of the WWDC 2024 sessions on StoreKit, controls, lock-screen camera capture, passkey upgrades, watchOS 11, HealthKit, MapKit, weather, AdAttributionKit, the Apple Games app, and other platform-level capabilities.

Sessions analyzed: 10061 (StoreKit), 10062 (App Store server APIs), 10063 (App Store Connect), 10110 (Implement App Store Offers), 111386 (Subscriber retention), 10157 (Custom controls), 10204 (Lock screen capture), 10125 (Passkey upgrades), 10123 (What's new in privacy), 10203 (AccessorySetupKit), 10205 (watchOS 11), 10068 (Live Activities watch), 10069 (Broadcast updates), 10070 (TipKit), 10083 (HealthKit on visionOS), 10084 (Workout swimming), 10109 (Wellbeing APIs), 10067 (WeatherKit), 10097 (MapKit), 10212 (Location authorization), 10060 (AdAttributionKit), 10164 (DockKit), 10162 (HDR colors), 10177 (HDR images), 10215 (Apple Games app), 111378 (Network conditions), 10131 (Spotlight semantic search), 10185 (Multilingual), 10089 (Game porting), 10093 (iOS to visionOS), 10091 (TabletopKit), 10117 (Translation), 2023 (FinanceKit), 10220 (Genmoji).

---

## 1. StoreKit 2 + Subscription Improvements (WWDC24-10061, 10110, 111386)

### 1.1 Finished Consumables in Transaction History

iOS 18 adds **finished consumables** to `Transaction.all` (opt-in via `SKIncludeConsumableInAppPurchaseHistory` Info.plist key). Previously you had to track these manually. Now the framework remembers them for you.

### 1.2 Transaction.currency + Transaction.price (NEW)

Server-side reconciliation gets easier -- you no longer need to look up the price your customer actually paid in their currency:

```swift
let tx = await Transaction.latest(for: productID)
print(tx.currency, tx.price)  // e.g., "USD", 9.99
```

Available even on **older OS versions back to iOS 15** when built with Xcode 16.

### 1.3 RenewalInfo.renewalPrice + .currency (NEW)

Tells you what the user will be charged at next renewal. **Critical for "your price is going up" notifications** -- show users their next bill in advance.

### 1.4 Win-Back Offers (NEW)

A new offer type for re-engaging churned subscribers. Eligibility rules in App Store Connect. **No code required** -- the StoreKit Message API merchandises them automatically. Apple's editorial team can promote them on Today/Games/Apps tabs.

### 1.5 Subscription Store View -- The Big SwiftUI API Expansion

Three new picker control styles in iOS 18:
- `.compactPicker` -- horizontal shelf, 2-3 plans best
- `.pagedPicker` -- horizontal paging
- `.pagedProminentPicker` -- selected option scaled up

Plus **placement** API (`.bottomBar`, `.leading`, `.trailing`, `.bottom` on tvOS) and **subscription option groups** (tab-organized plan tiers like Premium vs. Basic with separate marketing content per tab).

### 1.6 Custom Subscription Store Controls

You can now write your own `SubscriptionStoreControlStyle` conformance using `SubscriptionPicker` + `SubscribeButton` primitives. **Get StoreKit's tx-handling for free with full design control.**

### 1.7 Xcode 16 StoreKit Testing Improvements

- Test **App Policies** (privacy + license) locally
- Localize subscription group display names
- Test win-back offers
- New **Image** field for in-app purchase products
- **Disable system dialogs** for UI tests
- Send purchase intents directly from the transaction manager
- Test billing-issue messages with the new "billing retry" toggle

---

## 2. Custom Controls (WWDC24-10157)

### 2.1 The Architecture

Controls are a new kind of widget powered by `WidgetKit + AppIntents`. Two types:
- `ControlWidgetButton` -- discrete action
- `ControlWidgetToggle` -- boolean state

```swift
struct TimerToggle: ControlWidget {
    var body: some ControlWidgetConfiguration {
        StaticControlConfiguration(kind: "...") {
            ControlWidgetToggle("Timer", isOn: TimerManager().isRunning, action: ToggleTimerIntent()) { isOn in
                Label(isOn ? "Running" : "Stopped", systemImage: isOn ? "hourglass.flowing" : "hourglass")
            }
        }
        .tint(.purple)
    }
}
```

### 2.2 The Three Reload Triggers

A control reloads when:
1. Its action's `perform()` returns
2. Your app calls `ControlCenter.shared.reloadControls(ofKind:)`
3. A push notification invalidates it

### 2.3 The `AppIntentControlValueProvider` Pattern (configurable controls)

```swift
struct TimerProvider: AppIntentControlValueProvider {
    func currentValue(configuration: SelectTimerIntent) async throws -> TimerState { ... }
    var previewValue: TimerState { .stopped }
}
```

This makes a control **user-configurable** (e.g., choose which timer this control controls). Each user can put two of your controls in Control Center, each configured for a different timer.

### 2.4 The `promptsForUserConfiguration()` Modifier

If your control requires configuration to be functional, this modifier auto-prompts on add. Better than failing silently.

### 2.5 Action Hint and Status Customization

```swift
.controlWidgetActionHint("Start", offString: "Stop")  // Action button shows "Hold to Start"
.controlWidgetStatus("3:24 remaining")                // momentary Control Center status
```

### 2.6 Display Name & Description

Default control display name is your app name -- always override:

```swift
.displayName("Productivity Timer")
.description("Start or stop your productivity timer.")
```

---

## 3. Lock Screen Camera Capture (WWDC24-10204)

### 3.1 LockedCameraCapture Framework

A new app extension type (`LockedCameraCaptureExtension`) that runs **from the Lock Screen** without unlocking. Strict requirements:
- MUST show a viewfinder immediately at launch (or get terminated)
- MUST use `AVCaptureEventInteraction` for hardware buttons
- NO network access
- NO shared group container access
- NO shared preferences access

### 3.2 The CameraCaptureIntent Trio

A `CameraCaptureIntent` must be included in **all three targets**:
1. Your widget extension (the control)
2. Your capture extension
3. Your main app

The intent defines an `appContext` (small payload) shared between extension and app -- e.g., user preferences. Updated via `intent.updateAppContext(...)`.

### 3.3 Persistence Workflow

The capture extension cannot write to your shared container. Instead:
- Write to `session.sessionContentURL` (provided per-launch)
- When the extension dismisses, the session directory is **migrated to your app's container**
- Your app reads via `LockedCameraCaptureManager.shared.sessionContentURLs` and `.sessionContentUpdates` (an AsyncSequence)
- Your app calls `.invalidate(_:)` when done -- this deletes the session

### 3.4 The Photos Library Trick

PhotoKit works in the extension. When the device is locked, **only photos written during the current session are readable** -- privacy-by-default. When unlocked, full access (per existing permissions).

### 3.5 Transitioning Extension → App

```swift
let activity = NSUserActivity(activityType: NSUserActivityTypeLockedCameraCapture)
activity.userInfo = ["action": "share"]
try await session.openApplication(for: activity)
```

Triggers user authentication, then opens the app with the activity for seamless continuation.

---

## 4. Passkey Upgrades & Authentication (WWDC24-10125)

### 4.1 Automatic Passkey Upgrades -- The Headline

After an existing password sign-in, your app calls a `.conditional` request style. If the system + credential manager think it makes sense, a passkey is **silently created** and a notification is shown. **No upsell screen, no interruption.**

```swift
let request = ASAuthorizationPlatformPublicKeyCredentialProvider(
    relyingPartyIdentifier: "example.com")
    .createCredentialRegistrationRequest(challenge: challenge,
                                         name: username,
                                         userID: userID)
request.requestStyle = .conditional  // KEY: makes it an upgrade attempt
```

If conditions aren't met, you get an error -- no UI shown. Show your existing upsell as a fallback or just try again next time.

### 4.2 Web Equivalent

```javascript
const cred = await navigator.credentials.create({ ..., mediation: "conditional" })
```

Check `getClientCapabilities()` first to ensure the browser supports it.

### 4.3 The Phishing Endgame

> "It's time to start thinking about what it would take to eliminate all phishable factors as sign-in options from accounts." (WWDC24-10125)

Adding passkeys is step 1. The destination is **removing passwords entirely** for accounts that no longer use them.

### 4.4 Credential Manager Improvements

3rd-party credential managers can now:
- Participate in automatic passkey upgrades
- Fill time-based verification codes (`otpauth:` links)
- Fill any text field (not just username/password)

Users can pick **up to three** apps for AutoFill.

### 4.5 The New Passwords App

Adopt the **OpenGraph** standard (`og:site_name`, `og:image`) so your service appears with the right name and icon. Use `.well-known/change-password` URL so the Passwords app's Change Password button works.

### 4.6 One-Tap Verification Code Setup

Provide an `otpauth://` link alongside your QR code. This opens the system default verification-code app with one tap.

---

## 5. WeatherKit + MapKit + Location (WWDC24-10067, 10097, 10212)

### 5.1 WeatherKit -- New Datasets

- **Cloud cover by altitude**
- **Maximum wind speed**
- **Precipitation by type** (rain vs. snow vs. sleet)
- **Historical comparisons** -- compare today vs. last year same date
- **Significant change summaries** for the next 24 hours

### 5.2 Summarize Weather by Time of Day

```swift
let summary = try await weatherService.summary(for: location, parts: [.morning, .afternoon, .evening])
```

### 5.3 MapKit -- Places API

`MKMapItem` now exposes structured Place data: hours, ratings, photos, accessibility info. Combined with the new selectable POI annotations, much richer than before.

### 5.4 Cycling Directions (NEW)

```swift
let request = MKDirections.Request()
request.transportType = .cycling  // NEW
```

### 5.5 Location Authorization Modernization (WWDC24-10212)

`CLServiceSession` is the new way to request location. Tied to a session lifetime instead of a long-living delegate. Better for apps that need location only during a specific user task.

```swift
let session = CLServiceSession(authorization: .whenInUse)
for try await update in session.updates {
    // process
}
// ends when session deallocates
```

---

## 6. AdAttributionKit (WWDC24-10060)

Replaces SKAdNetwork for ad attribution. Cross-platform, supports re-engagement attribution, server callbacks. The migration story for the post-IDFA era is now solidified.

---

## 7. Privacy in iOS 18 (WWDC24-10123)

### 7.1 Contact Access Button (WWDC24-10121)

Lets users selectively grant access to specific contacts without granting full address book access. **Recommended pattern for new apps**:

```swift
ContactAccessButton(queryString: searchText) { contacts in
    selectedContacts.append(contentsOf: contacts)
}
```

### 7.2 Limited Library Access for Photos

Now also covers Live Photos and selected metadata -- previously the limited subset excluded these.

### 7.3 New Privacy Manifests Audit Tools

Xcode 16 surfaces missing or inconsistent privacy manifests in your app + dependencies. Run the Privacy Report from Build Settings → Privacy.

---

## 8. AccessorySetupKit (WWDC24-10203)

A new framework for in-app accessory pairing without exposing all Bluetooth devices. Display only YOUR accessories with their photos/branding for a clean pairing UX. **Works for both Bluetooth and Wi-Fi accessories.**

---

## 9. watchOS 11 (WWDC24-10205)

### 9.1 Live Activities Auto-Inheritance

Any iOS Live Activity automatically appears on Apple Watch.

### 9.2 Vitals App Integration

A new HealthKit-driven Vitals app aggregates morning baseline (heart rate, HRV, body temp, blood oxygen). Apps can read and write the new `vitalsBaseline` HealthKit type.

### 9.3 Training Load API

A computed score combining recent workouts + heart rate effort over time. Apps can read this for "fatigue" analysis features.

### 9.4 Smart Stack on the Watch

Time-relevant widgets surface based on context (calendar, location, time-of-day). Configure via `RelevantContext` in your Widget configuration.

### 9.5 Pause/Resume Workouts (WWDC24-10084)

WorkoutKit now supports custom pause/resume triggers, custom workout types (e.g., custom swim drills), and exposing them via App Intents to Siri.

---

## 10. HealthKit (WWDC24-10083, 10084, 10109)

### 10.1 HealthKit on visionOS (WWDC24-10083)

Vision Pro now has HealthKit (read-only by default). Apps can build immersive data visualizations. Note: Vision Pro doesn't capture biometric data itself -- it reads from connected iPhone/Apple Watch.

### 10.2 Wellbeing APIs (WWDC24-10109)

New mental-health data types:
- **Mood logs** (anxiety, joy, sadness, etc. on a scale)
- **Sleep apnea** (data from Apple Watch screening)

Requires the new "wellbeing" entitlement and special user consent flow.

### 10.3 Custom Swimming Workouts (WWDC24-10084)

Build pool-aware swim workouts with stroke types, lap counts, and structured intervals.

---

## 11. TipKit Improvements (WWDC24-10070)

### 11.1 Custom Feature Discovery

Beyond the "see this for the first time" pattern, you can now define:
- **Frequency rules** -- "Show this tip at most once per week"
- **Cross-tip relationships** -- "Don't show Tip B if Tip A was dismissed in the last 24h"
- **Custom event triggers** -- arbitrary events from your app code

### 11.2 New Tip Styles

Inline tips, popover tips, and adapted styles for each platform.

---

## 12. The Apple Games App (WWDC24-10215)

A new dedicated games hub app. Adopt:
- **Game Center achievements** -- power the Challenges tab
- **Game saves to iCloud** -- enable continue-anywhere
- **Trophy room support**
- **Apple Arcade integration** if applicable

---

## 13. HDR Images (WWDC24-10177, 10162)

### 13.1 The HDR Image Format

iOS 18 supports **gain-map HDR**, where images carry both an SDR base + HDR boost layer. Single file works on SDR and HDR displays.

### 13.2 Color Consistency Across Captures (WWDC24-10162)

`AVCaptureDevice` now exposes manual white-balance + color-matrix controls for cross-photo consistency. Critical for product photography apps.

### 13.3 Display HDR in Your App

```swift
Image("photo")
    .allowedDynamicRange(.high)  // SwiftUI
```

UIImageView and CALayer have equivalent flags.

---

## 14. DockKit (WWDC24-10164)

DockKit accessories (motorized phone mounts) get new APIs:
- Custom subject tracking (not just face/body)
- Manual control overlays
- Multi-camera coordination

---

## 15. Network Adaptation (WWDC24-111378)

### 15.1 NWPathMonitor + URLSession Integration

```swift
NWPathMonitor.publisher
    .sink { path in
        if path.isExpensive {
            // throttle uploads
        }
    }
```

### 15.2 Background Network Latency Telemetry

The system now tracks per-request latency and surfaces it via Instruments' Network instrument. Spot regressions quickly.

---

## 16. Spotlight Semantic Search (WWDC24-10131)

### 16.1 The IndexedEntity Bridge

Already covered in the App Intents cluster. Key insight: indexing your AppEntity into Spotlight enables **semantic search** -- search "pets" finds entities tagged with cats/dogs/snakes.

### 16.2 Custom Attribute Sets

```swift
extension TrailEntity: IndexedEntity {
    var attributeSet: CSSearchableItemAttributeSet {
        let set = CSSearchableItemAttributeSet(contentType: .item)
        set.city = location.city
        set.stateOrProvince = location.state
        set.keywords = activities
        return set
    }
}
```

---

## 17. FinanceKit (WWDC24-2023)

A new framework giving apps read-only access to a user's Apple Cash, Apple Card, and Apple Pay transactions (with explicit user consent). Use cases: budgeting apps, expense reports, personal finance dashboards.

---

## 18. CarPlay Architecture (WWDC24-10111)

Companion to the design session (WWDC24-10112). The technical reference for automakers implementing the next-gen CarPlay system. App developers don't need new code -- the system surfaces existing CarPlay app data automatically.

---

## 19. Cross-References

For monetization:
1. **WWDC24-10061** (StoreKit) -- core APIs
2. **WWDC24-10110** (App Store Offers) -- win-back, intro pricing
3. **WWDC24-111386** (Subscriber retention)

For lock-screen / camera capture:
1. **WWDC24-10204** (Lock Screen capture)
2. **WWDC24-10157** (Custom controls)

For authentication:
1. **WWDC24-10125** (Passkey upgrades)
2. **WWDC24-10123** (Privacy)

For watch + health:
1. **WWDC24-10205** (watchOS 11)
2. **WWDC24-10084** (Workout customization)
3. **WWDC24-10109** (Wellbeing APIs)
