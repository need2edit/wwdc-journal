# WWDC 2020 — Privacy, Security & Networking

WWDC 2020 was a privacy-defining year. **App Tracking Transparency**, **Limited Photos Library**, **approximate location**, **local network privacy prompts**, **clipboard transparency**, **camera/mic indicators**, **encrypted DNS** — all landed together, plus the new **App Store privacy labels** ("nutrition labels"). And the security side added **Sign in with Apple upgrades**, **Web Authentication (FIDO2)** in Safari, and **endpoint security** APIs.

## Sessions Analyzed
- 10676 — Build trust through better privacy (gateway)
- 10162 — Design for location privacy
- 10641 — Handle the Limited Photos Library in your app
- 10652 — Meet the new Photos picker
- 10110 — Support local network privacy in your app
- 10047 — Enable encrypted DNS
- 10111 — Boost performance and security with modern networking
- 10173 — Get the most out of Sign in with Apple
- 10666 — One-tap account security upgrades
- 10670 — Meet Face ID and Touch ID for the web
- 10665 — Meet Safari Web Extensions
- 10189 — Secure your app: threat modeling and anti-patterns
- 10159 — Build an Endpoint Security app
- 10668 — Meet Nearby Interaction
- 10006 — Introducing Car Keys
- 10209 — What's new in Core NFC

## Apple's Four Privacy Pillars (10676)

The framing repeated across many sessions:
1. **On-device processing** — keep data on the device whenever possible. Federated learning, on-device dictation, on-device HomeKit face recognition, Core ML.
2. **Data minimization** — request only the data you actually need; ask only when you need it.
3. **Security protections** — encryption (DNS, TLS SNI), private Wi-Fi address randomization.
4. **Transparency and control** — visible indicators for camera/mic, App Store privacy labels, settings to revoke at any time.

## App Tracking Transparency (ATT)

The most policy-impactful change. Apps must now **prompt before tracking users across apps and websites owned by other companies** for purposes like targeted advertising, ad measurement, or sharing with data brokers.

```swift
import AppTrackingTransparency
ATTrackingManager.requestTrackingAuthorization { status in ... }
```

NSUserTrackingUsageDescription in Info.plist required.

**What counts as tracking**:
- Linking user data with other apps' or websites' data (even via fingerprinting / probabilistic IDs)
- Sharing data with data brokers
- Targeted advertising / ad measurement

**Doesn't count**:
- Linking entirely on the user's device (data never leaves the device tied to user identity)
- Sharing with data brokers for fraud/security only

If user denies tracking (or has the system-wide "Ask App Not to Track" toggle on), `ASIdentifierManager.advertisingIdentifier` returns all zeros. The IDFA was previously gated only by the "Limit Ad Tracking" switch; now it's gated by ATT permission.

### SKAdNetwork Improvements

Apple's privacy-friendly ad attribution framework got significant upgrades to give ad networks the data they need (campaign success, source app) without identifying users. Conversion data is aggregated by Apple (k-anonymity check via threshold of identical conversions) before being delivered. Major addition: ad networks now receive postback values without requiring user-level tracking, making this a credible alternative to the old IDFA flow.

## Limited Photos Library (10641, 10652)

Users can now grant apps **access to a subset** of their Photos library, not all-or-nothing. Three changes:

### 1. The New PHPicker Replaces UIImagePickerController (10652)

For most apps that just need to pick photos to share, **don't request library access at all**. Use `PHPicker` — it runs **out-of-process**, your app cannot inspect it or screenshot it, and only what the user selects is returned. **No prompt needed.**

```swift
var config = PHPickerConfiguration()
config.selectionLimit = 1  // 0 = unlimited
config.filter = .images
let picker = PHPickerViewController(configuration: config)
```

### 2. Limited Library APIs (10641)

For apps that genuinely need PhotoKit access (browsers, editors, backup):

```swift
PHPhotoLibrary.authorizationStatus(for: .readWrite) // returns .limited if user picked subset
PHPhotoLibrary.requestAuthorization(for: .readWrite) { status in ... }
```

The new `.limited` status. Old APIs return `.authorized` even when the user granted limited access — back-compat. New APIs surface `.limited` distinctly.

### 3. Native Selection Management UI

Trigger from your own UI:
```swift
PHPhotoLibrary.shared().presentLimitedLibraryPicker(from: viewController)
```

Set `PHPhotoLibraryPreventAutomaticLimitedAccessAlert = YES` in Info.plist to suppress the system's first-time prompt and present the picker on your own schedule.

When in limited mode, fetched assets are filtered to the user's selection. App-created assets are auto-included. **User albums cannot be fetched or created**; cloud-shared assets are not visible.

## Approximate Location (10162)

Users can now grant **approximate** location instead of precise. Set `NSLocationDefaultAccuracyReduced = YES` in Info.plist to default new requests to approximate. For specific operations needing precision (turn-by-turn navigation), request a temporary precise upgrade:

```swift
locationManager.requestTemporaryFullAccuracyAuthorization(withPurposeKey: "Navigation")
```

Apple's design guidance: respect the user — if approximate is enough for your feature, ask only for that.

## Local Network Privacy (10110)

iOS 14 prompts for permission the **first time an app accesses the local network** (Bonjour browse/advertise, multicast, custom protocols). Once allowed, all local network traffic from your app is enabled.

Required Info.plist entries:
- `NSLocalNetworkUsageDescription` — clear reason text
- `NSBonjourServices` — list of Bonjour service types you'll browse/advertise

If you need raw multicast or to enumerate all Bonjour service types: request the multicast networking entitlement via the developer portal.

Best practices:
- **Don't browse on launch** — wait for a user action that requires it. The prompt feels less invasive when timed to a "Find Devices" tap.
- Set `URLSession.waitsForConnectivity = true` so URL session tasks complete after permission is granted.
- Prefer system services that don't need local network access: AirPrint, AirPlay, AirDrop, HomeKit.

NoAuth errors mean you've forgotten to add the Bonjour services or usage description.

## Encrypted DNS (10047)

iOS 14 / macOS Big Sur natively support **DNS over HTTPS (DoH)** and **DNS over TLS (DoT)**. Two enable paths:

### System-wide DNS Settings

Apps that provide a public DNS service can ship a NetworkExtension app that calls:
```swift
let manager = NEDNSSettingsManager.shared()
let settings = NWDNSOverHTTPSSettings(servers: [...], serverURL: URL(string: "https://...")!)
manager.dnsSettings = settings
manager.saveToPreferences { ... }
```

Plus Network Rules for compatibility with private enterprise networks (specific Wi-Fi SSIDs that need exceptions for `enterprise.example.net`-style private domains, or to disable on cellular).

MDM profiles can configure DNS settings for managed devices.

### Per-App via PrivacyContext

For apps that just want their own connections to use encrypted DNS:
```swift
let privacyContext = NWParameters.PrivacyContext(description: "MyApp")
privacyContext.requireEncryptedNameResolution(true, fallbackResolver: .https(url, ...))
let parameters = NWParameters.tcp
parameters.setPrivacyContext(privacyContext)
```

Verify which DNS protocol was used via `NWConnection`'s `EstablishmentReport`.

## Camera, Mic, Clipboard Transparency

iOS 14 always shows an **indicator in the status bar** when an app uses the camera or microphone. Control Center shows which app is currently or recently using them.

For pasteboard, a banner notification appears when an app reads the pasteboard programmatically. Be careful with auto-paste features — they look suspicious without user-initiated context. The session recommends pre-warming patterns (request access only at the moment the user signals intent).

## Private Wi-Fi Address

iOS 14 randomizes the device's MAC address per Wi-Fi network, regenerated every 24 hours. This blocks cross-network user tracking. Users can disable per-network in Wi-Fi settings.

## Sign in with Apple Improvements (10173)

### State and Nonce — Critical Security Practices

Always set both on the request:
```swift
request.nonce = UUID().uuidString  // Send to server, verify embedded in identityToken
request.state = UUID().uuidString  // Returned in credential, verify locally
```

Server validates the JWT identityToken: signature with Apple's public key, nonce matches, expiration valid, audience is your bundle ID. Exchange `authorizationCode` with Apple's servers for refresh + access tokens; verify refresh once a day.

### Server-to-Server Notifications

Register a webhook URL in the developer portal. Apple sends signed JWTs for events:
- `email-disabled` / `email-enabled` — user opted in/out of relay
- `consent-revoked` — treat as sign-out
- `account-delete` — userIdentifier no longer valid

### Transferred Credential State

When an app is transferred between developer teams, userIdentifiers must be regenerated. The new `.transferred` `ASAuthorizationAppleIDProviderCredentialState` triggers a silent re-authorization on the next launch — call the same Sign in with Apple API with the existing userIdentifier; you get back a new one matching the new team.

### SwiftUI Button

```swift
SignInWithAppleButton(.signIn,
  onRequest: { req in req.nonce = ... },
  onCompletion: { result in ... })
```

### Online Button Generator

`appleid.apple.com/signinwithapple/button` — customize label/size/style, download assets.

## Upgrade to Sign in with Apple (10666)

Account Authentication Modification Extension lets users **upgrade existing username/password credentials** to Sign in with Apple. Surfaces in:
1. Password Manager security recommendations (weak credential)
2. Password AutoFill picking a weak credential
3. Custom invocation from your app via Authentication Services

Two-stage flow: try non-interactive upgrade first (fast for already-authenticated users); if user verification needed (2FA), present step-up UI in your extension.

## Face ID & Touch ID for the Web (10670)

Safari supports **Web Authentication (WebAuthn)** with Face ID/Touch ID as the platform authenticator. For web developers:

```js
// Onboarding
navigator.credentials.create({ publicKey: { rp, user, pubKeyCredParams, challenge,
  authenticatorSelection: { authenticatorAttachment: 'platform' } } })

// Sign in
navigator.credentials.get({ publicKey: { challenge, allowCredentials: [...] } })
```

Authenticator is the iPhone (something you have) + biometric (something you are) = multi-factor in one tap. Private keys never leave the Secure Enclave. Apple's **Anonymous Attestation** generates a unique cert per credential to prevent cross-site tracking.

Best practice: **don't make this the only sign-in method** — users can lose devices.

## App Store Privacy Labels

Starting fall 2020, every App Store submission must complete a privacy questionnaire describing data collection and usage. The information appears prominently on the product page across all App Stores.

You're responsible for **third-party SDKs** in your app too — they share your app's data access. Reach out to SDK vendors for documentation.

## Build Trust Through Threat Modeling (10189)

Practical security session covering:
- **Threat modeling** — STRIDE-style enumeration of trust boundaries.
- **Anti-patterns** — hard-coded secrets, ignoring TLS errors, untrusted deserialization, IDOR (insecure direct object references).
- **Storage hygiene** — Keychain for secrets (with the right access class), encrypted Core Data store options, file protection classes.
- **App-to-app communication** — XPC, App Groups, Universal Links — and the trust boundaries each implies.

## Endpoint Security (10159)

For Mac app developers building security tools (EDR, antivirus, monitoring), **Endpoint Security framework** replaces Kernel Authorization (KAuth) and other deprecated mechanisms. User-space framework that subscribes to system events (process exec, file access, network connection) with both notification and authorization-decision modes.

## Nearby Interaction (10668)

A new framework for the **U1 chip's ultra-wideband** ranging. Get distance and direction information between two devices in real-time for peer-to-peer apps:

```swift
let session = NISession()
session.delegate = self
let token = session.discoveryToken  // Send to peer via your transport (network, BLE)
session.run(NINearbyPeerConfiguration(peerToken: peerToken))
// session(_:didUpdate:) callbacks with distance + direction
```

No Bluetooth permission prompt — session-based access only while in foreground.

Use cases: precise device-to-device awareness for games, AirDrop-style targeting, social distance measurements.

## Car Keys & Core NFC (10006, 10209)

### Car Keys

iOS 13.6 / 14 supports digital car keys via U1/NFC. Apps integrate with Apple Wallet to issue and manage keys. BMW was the launch partner.

### Core NFC

iOS 14 Core NFC adds:
- Read **vCard / contact** records from NFC tags
- Read **NDEF Wi-Fi configuration** records
- Improved background NFC reading on iPhone XS+ (no app launch required for many tag types)

## Cross-References
- [app-clips.md](app-clips.md) — App Clips have specific privacy designs (location confirmation, no HealthKit).
- [siri-intents-shortcuts.md](siri-intents-shortcuts.md) — Suggested actions are an alternative to data collection.
- [ml-vision-coreml.md](ml-vision-coreml.md) — On-device ML is the privacy-friendly alternative.

## Adoption Checklist
- [ ] Audit your app for tracking that requires the ATT prompt; implement `requestTrackingAuthorization`.
- [ ] Replace `UIImagePickerController` with `PHPicker` where you don't need full library access.
- [ ] Handle the new `.limited` PhotoKit authorization status if you must access the library.
- [ ] Adopt approximate location where precise isn't needed; use `NSLocationDefaultAccuracyReduced`.
- [ ] Add `NSLocalNetworkUsageDescription` and `NSBonjourServices` to Info.plist.
- [ ] Time local-network access prompts to user-initiated actions.
- [ ] Add nonce + state to all Sign in with Apple requests; validate server-side.
- [ ] Register a server-to-server notification webhook with Apple if you persist users long-term.
- [ ] Complete the App Store privacy questionnaire; audit your third-party SDKs.
- [ ] Replace `print` with `os.Logger` for security-relevant events.
- [ ] If a Mac app for security/monitoring, migrate to Endpoint Security framework.
