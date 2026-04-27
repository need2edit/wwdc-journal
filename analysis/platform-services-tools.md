# WWDC25 Analysis: Platform Services, Privacy, Security, Developer Tools, System Services

Deep analysis of 27 WWDC25 sessions covering developer tools, security, privacy, web technologies, system services, payments, localization, and new platform frameworks.

---

## 1. Developer Tools & Xcode

### What's new in Xcode (WWDC25-247)

**Performance Optimizations**
- Xcode 26 download is **smaller than Xcode 6 from 2014** after removing default Intel support from Simulator runtimes and conditional Metal toolchain downloads (24% smaller)
- Typing latency improved by **up to 50%** in complex expressions
- Workspace loading is **40% faster**, significant for large projects

**Best Practices: Playgrounds**
- New `#Playground` macro lets you add inline playgrounds directly in source files -- results appear in a canvas tab
- `import Playgrounds` gives access to the `#Playground` macro
- The macro is being **open-sourced** for cross-platform Swift developers
- Playgrounds support Quick Look visualizations for types like regex match results and CLLocation

**Hidden Gem: Multiple Words Search**
- New search mode uses "search engine techniques" to find clusters of words in proximity across documents, sorted by relevance -- great for exploring unfamiliar codebases

**AI/LLM Integration**
- Xcode supports ChatGPT out of the box, plus Anthropic (Claude 4 Opus/Sonnet) via API key, and local models via Ollama/LM Studio
- Use `@` to reference symbols directly when chatting with the model
- Modification history lets you scrub back/forth through AI-generated changes
- Coding tools menu provides quick actions on selected code (fix errors, deprecation warnings)

**Security: Enhanced Security Capability**
- New "Enhanced Security" capability provides the same protections used in Apple's own apps, including **pointer authentication**
- Enable via Signing and Capabilities editor
- Recommended for apps with significant attack surface: "social media, messaging, image viewing, and browsing" (WWDC25-247)

**Builds**
- **Explicitly Built Modules enabled by default** -- improves build efficiency, reliability, and debugging speed
- **Swift Build** is open-sourced and being integrated into Swift Package Manager for Linux, Windows, Android support
- Preview with `--build-system` option in the Swift CLI

**Testing**
- New `XCTHitchMetric` for measuring scrolling animation performance (Hitch Time Ratio)
- Runtime API Checks now surface in tests, including **Thread Performance Checker** for priority inversions and non-UI work on main thread
- Power Profiler instrument for diagnosing energy impact
- Processor Trace instrument provides exact CPU instruction traces (not sampling-based)

**Cross-references:** WWDC25-344, WWDC25-225, WWDC25-361, WWDC25-308, WWDC25-306, WWDC25-226, WWDC25-245, WWDC25-256

---

### Record, replay, and review: UI automation with Xcode (WWDC25-344)

**Best Practices: Accessibility Identifiers**
- "Accessibility identifiers are the best way to uniquely identify any element in your app for automation" (WWDC25-344)
- Good identifiers are: **unique within entire app, descriptive, and static** (not reacting to content changes)
- Use `accessibilityIdentifier("LandmarkImage-\(landmark.id)")` pattern for instance-specific identifiers
- The accessibility identifier is **not read by VoiceOver** and not exposed to users -- purely for automation

**Hidden Gem: AI-assisted accessibility**
- You can ask Xcode's coding assistant to "Add accessibility identifiers to the relevant parts of this view" and it will intelligently add them

**API Details: XCUIAutomation**
- `waitForExistence(timeout:)` -- wait for element to appear
- `wait(for:toEqual:timeout:)` -- validate any property on XCUIElement
- `XCUIDevice.shared.orientation`, `.appearance`, `.location` -- set device state in setUp()
- `app.open(customURL)` -- test custom URL schemes
- `try app.performAccessibilityAudit()` -- run accessibility audit during UI test

**Best Practices: Query Selection**
- For localized strings: prefer accessibility identifier over string matching
- For deeply nested views: choose the **shortest possible query**
- For dynamic content: use generic queries like `.staticTexts.firstMatch` or accessibility identifiers
- Worst: `XCUIApplication().staticTexts["Max's Australian Adventure"]`
- Better: `XCUIApplication().staticTexts["Collection-1"]`

**Test Plans**
- Configure multiple locale configurations (especially German for longer strings, Arabic/Hebrew for RTL)
- Video/screenshot capture settings: default keeps only for failing runs; use "On, and keep all" for documentation/marketing purposes
- Test plans work identically in Xcode Cloud

**Cross-references:** WWDC24-10179, WWDC23-10036, WWDC23-10278, WWDC23-10175, WWDC22-110361, WWDC21-10119

---

### Meet Containerization (WWDC25-346)

**Architecture: One VM per Container**
- Unlike traditional Docker-on-Mac (one large VM hosting all containers), Containerization runs **each container in its own lightweight VM** with sub-second start times
- Each container gets a **dedicated IP address** -- no port mapping needed
- Directory sharing is per-container (not shared across containers) for better privacy
- Zero resource allocation when no containers are running

**Hidden Gem: vminitd is Built in Swift**
- The init system (`vminitd`) runs as PID 1 inside each VM, compiled as a **static executable** using Swift's Static Linux SDK with musl libc
- The VM filesystem has **no core utilities, no dynamic libraries, no libc** -- reducing attack surface
- Cross-compiled from Mac to Linux

**API Details**
- `container image pull alpine:latest` -- pull images
- `container run -t -i alpine:latest sh` -- run interactive shell (sub-second startup)
- EXT4 filesystem support via a Swift package for formatting block devices

**Open Source**
- Framework: github.com/apple/containerization
- CLI tool: github.com/apple/container

**Cross-references:** None explicitly mentioned

---

## 2. Security & Cryptography

### Get ahead with quantum-secure cryptography (WWDC25-314)

**Critical Urgency: Harvest Now, Decrypt Later**
- "Attackers can already be harvesting network traffic right now" (WWDC25-314)
- Any app sending sensitive data over the network is vulnerable to future quantum decryption
- Apple already addressed this for iMessage with PQ3 in iOS 17.4

**Migration Priority**
1. **Network data first** (highest priority -- harvest now, decrypt later is happening now)
2. **Custom protocols second** (if using direct cryptography APIs)
3. **Signatures third** (future threat, requires active quantum computer)

**Best Practice: Quantum-Secure TLS**
- Starting in **iOS 26, quantum-secure encryption in TLS is enabled by default** for URLSession and Network.framework
- **Migrate away from legacy networking APIs** (Secure Transport) -- they will NOT support quantum-secure TLS
- Server-side: most hosting providers already support it; check configuration
- System services (CloudKit, APNs, iCloud Private Relay) are enabling it

**API Details: CryptoKit Quantum-Secure APIs**
```swift
let ciphersuite = HPKE.Ciphersuite.XWingMLKEM768X25519_SHA256_AES_GCM_256
let privateKey = try XWingMLKEM768X25519.PrivateKey.generate()
var sender = try HPKE.Sender(recipientKey: publicKey, ciphersuite: ciphersuite, info: info)
let ciphertext = try sender.seal(userData, authenticating: metadata)
```
- Post-quantum HPKE for encryption (X-Wing KEM)
- ML-DSA for signatures
- Both have **Secure Enclave support** and **formally verified** implementations
- If migrating from classical HPKE, it's "just a change of ciphersuite and key type"

**Best Practice: Symmetric Key Upgrade**
- Upgrade 128-bit keys to 256-bit (e.g., AES-128 to AES-256)
- Quantum computers only achieve a "small, constant factor reduction" for symmetric crypto

**Server Interoperability**
- Use **Swift Crypto** on the server for API compatibility with CryptoKit
- All quantum-secure APIs available in both CryptoKit and Swift Crypto

**Cross-references:** Apple Security Blog (iMessage PQ3)

---

### What's new in passkeys (WWDC25-279)

**Industry Momentum**
- 69% of people surveyed have at least one passkey (FIDO Alliance, 2025)
- Google: passkey users are **4x more successful** signing in than password users
- TikTok: **97% sign-in success rate** with passkeys

**New: Account Creation API**
- `ASAuthorizationAccountCreationProvider` -- streamlined sign-up with prefilled name/email and passkey in one step
- System presents a sheet with editable fields, no multi-step form needed
- Handle `ASAuthorizationError.preferSignInWithApple` to redirect to existing SIWA accounts
- Handle `ASAuthorizationError.deviceNotConfiguredForPasskeyCreation` to fall back to password form

**Best Practice: Offer credentials at launch**
- Use combined sign-in request with `preferImmediatelyAvailableCredentials` -- if credentials exist, they're offered; if not, no UI shown

**New: Signal APIs for Credential Managers**
- `ASCredentialUpdater().reportPublicKeyCredentialUpdate(...)` -- notify when username changes
- `ASCredentialUpdater().reportAllAcceptedPublicKeyCredentials(...)` -- notify when passkeys are revoked
- `ASCredentialUpdater().reportUnusedPasswordCredential(...)` -- signal password-free account
- Web equivalents: `PublicKeyCredential.signalCurrentUserDetails()`, `.signalAllAcceptedCredentials()`

**Automatic Passkey Upgrades**
- After password sign-in, silently create a passkey with `requestStyle: .conditional`
- System shows notification but **no interruption** -- "attempt the upgrade on every password sign-in"
- Password remains valid

**Well-Known URL for Passkey Management**
- Serve JSON at `/.well-known/passkey-endpoints` with `enroll` and `manage` URLs
- Must return 200 OK directly (no redirect), content-type `application/json`
- Ensure pages handle unauthenticated users (authenticate, then redirect back)
- Serve to all user agents (not just browsers -- credential managers request too)

**Passkey Import/Export**
- Secure transfer between credential manager apps via FIDO Alliance data schema
- No insecure files on disk; secured by Face ID
- Apps/websites don't need changes

**Cross-references:** WWDC24-10125, WWDC22-10092

---

### Verify identity documents on the web (WWDC25-232)

**Digital Credentials API**
- Websites can request identity information from IDs in Apple Wallet
- Uses the W3C Digital Credentials API (`navigator.identity.get()`)
- New **IdentityDocumentServices** framework lets apps provide their own identity documents for web verification
- Based on ISO/IEC 18013-5 (mdoc) and ISO/IEC 18013-7 (OID4VP) standards
- Business verification through Apple Business Connect integration

**Privacy Design**
- User explicitly consents to each data element shared
- Selective disclosure: only requested fields are shared
- Verifier must be registered and verified

**Cross-references:** Apple Business Connect

---

## 3. Privacy & Child Safety

### Integrate privacy into your development process (WWDC25-246)

**Privacy Assurances Framework**
- Define high-level privacy statements during **planning phase** -- these inform engineering requirements
- Use Apple's four pillars: data minimization, on-device processing, transparency & control, security protections

**Best Practice: Privacy by Design**
- "Privacy should be part of development from the very beginning. As with security or localization, privacy is much more challenging to retrofit later on." (WWDC25-246)
- Use PhotosPicker instead of requesting full photo library access
- Use LocationButton for one-tap location sharing without permission prompt (after first confirmation)
- Use UIPasteControl, contacts picker for minimal-access UI elements

**Hidden Gem: CloudKit End-to-End Encryption**
```swift
myRecord.encryptedValues["encryptedStringField"] = "Sensitive value"
```
- Use `encryptedValues` API for automatic E2E encryption when Advanced Data Protection is enabled
- No infrastructure changes needed, no key management
- Caveat: CloudKit doesn't support indexes on encrypted fields

**Hidden Gem: Homomorphic Encryption & PIR**
- Private Information Retrieval (PIR) lets you query server databases without revealing the query or result
- Swift Homomorphic Encryption library available on GitHub
- Already used in production features on Apple platforms

**Privacy Testing**
- Build tests to confirm privacy assurances (unit, integration, UI tests)
- App Privacy Report (iOS 15.2+) -- review data access, sensor access, and network activity
- UI test changing privacy settings to confirm data flow updates

**Deployment Requirements**
- Privacy nutrition labels in App Store Connect
- Generate Privacy Report from archive context menu in Xcode
- Privacy policy required
- Privacy manifests for app and all third-party SDKs
- Purpose strings for all permission prompts

**macOS Specific**
- macOS Tahoe will detect if spawned processes (fork/exec/POSIX spawn) continue running after app quit, prompting users
- App group containers protect data from other apps without user permission

**Cross-references:** WWDC25-221, WWDC24-10159, WWDC24-10161, WWDC24-10060, WWDC24-10123, WWDC23-10107, WWDC23-10060, WWDC22-10167, WWDC22-10077, WWDC21-10102, WWDC21-10244, WWDC21-10086

---

### Enhance child safety with PermissionKit (WWDC25-293)

**New Framework: PermissionKit**
- Children can ask parents for permission to communicate with someone new, via Messages
- Leverages Family Sharing groups
- Available on iOS, iPadOS, and macOS 26

**API Pattern**
```swift
// Check known handles
let knownHandles = await CommunicationLimits.current.knownHandles(in: conversation.participants)

// Create permission question
var question = PermissionQuestion(communicationTopic: topic)

// SwiftUI: Present button
CommunicationLimitsButton(question: question) { Label("Ask Permission", systemImage: "paperplane") }

// Listen for responses
for await update in CommunicationLimits.current.updates { /* handle response */ }
```

**Best Practice**
- Hide content from unknown senders for children (message previews, profile pictures)
- Provide maximum metadata in `PersonInformation` to help parents make informed decisions
- Specify actions (`.message`, `.call`, `.video`) for appropriate system verbiage
- App is launched in background when parent responds -- iterate over `CommunicationLimits.current.updates` on a background task

**Cross-references:** WWDC25-299

---

### Deliver age-appropriate experiences in your app (WWDC25-299)

**New: Declared Age Range API**
- Privacy-preserving: returns age **ranges** (not birth dates)
- Up to 3 age gates per request, producing 4 ranges (each at least 2 years)
- Regional max age automatically set to age of majority

**Privacy Protections**
- Caching: by default, only re-prompts on the **anniversary** of original response
- Three settings: Always Share, Ask First, Never Share
- Users can force cache clear in Settings to get updated access sooner

**API Pattern**
```swift
@Environment(\.requestAgeRange) var requestAgeRange
let ageRangeResponse = try await requestAgeRange(ageGates: 16)
switch ageRangeResponse {
case let .sharing(range):
    if let lowerBound = range.lowerBound, lowerBound >= 16 { /* enable feature */ }
case .declinedSharing: /* handle decline */
}
```

**Hidden Gem: Parental Controls Detection**
- If upper bound is below age of majority, API returns `activeParentalControls` set
- Check `range.activeParentalControls.contains(.communicationLimits)` to integrate with PermissionKit

**App Store Changes**
- Global age ratings now have 5 categories: 4+, 9+, 13+, 16+, 18+
- Add "Declared Age Range" capability in Signing and Capabilities

**Cross-references:** WWDC25-293

---

## 4. Networking & Connectivity

### Supercharge device connectivity with Wi-Fi Aware (WWDC25-228)

**New Framework: Wi-Fi Aware**
- Direct peer-to-peer communication without routers/servers
- Operates **alongside** regular Wi-Fi (devices stay connected to internet)
- Wi-Fi Alliance global standard, cross-platform and interoperable
- Connections are authenticated and encrypted at the Wi-Fi layer

**Architecture: Services Model**
- Services declared in Info.plist under `WiFiAwareServices` key
- Publisher (server) + Subscriber (client) roles; app can be both
- Service names: max 15 chars, letters/numbers/dashes, register with IANA to prevent collisions
- Two-part name format: `_file-service._tcp`

**Pairing: Two Frameworks**
- **DeviceDiscoveryUI** -- for app-to-app pairing (Apple + third-party devices)
- **AccessorySetupKit** -- for hardware accessory pairing; supports multi-transport (Bluetooth + Wi-Fi Aware simultaneous setup)

**Performance Tuning**
- **Bulk mode** (default): energy-efficient, higher latency, best effort
- **Real-time mode**: lower latency, more power consumption
- Traffic service classes: best effort, interactive video/voice, background
- Performance reports available: signal strength, throughput, latency
- "Before you decide to use real time mode, consider carefully if it's required" (WWDC25-228)

**Best Practice: Resource Conservation**
- Stop listener and browser once all required connections are made
- Limit listening/browsing to the duration necessary for use case

**Cross-references:** WWDC24-10203

---

### Filter and tunnel network traffic with NetworkExtension (WWDC25-234)

**New: URL Filter API (iOS 26)**
- System-wide HTTP/HTTPS filtering based on **full URL** (not just hostname)
- Privacy-preserving: app never sees URLs; all database queries anonymized
- Uses four technologies: Bloom filters, PIR, Privacy Pass, Oblivious HTTP Relay

**Architecture**
1. On-device Bloom filter for quick negative matches (no false negatives)
2. If Bloom filter positive: encrypted PIR query to your server
3. Server performs lookup on encrypted data, returns encrypted result
4. Only device can decrypt the result

**Oblivious HTTP Relay**
- Apple hosts the relay (capability must be applied for)
- Your app hosts the Gateway (Oblivious HTTP)
- Development-signed builds exempt from approval requirement

**Best Practice: VPN Development**
- "Network Extension is the supported API to build a VPN app. Building a VPN app with anything else is highly discouraged." (WWDC25-234)
- Avoid Packet Filter or direct routing table modification on Mac
- Use NEPacketTunnelProvider **only** for IP traffic tunneling -- not for DNS proxying or content filtering
- Migrate to Network Extension ASAP if not already using it

**Migration Guidance: Relays vs VPN**
- Network relays (MASQUE protocol): for TCP/UDP to specific apps (cloud enterprise apps)
- IP-based VPN: for full network access (corporate network extension)
- Relays don't need a custom extension -- just configure with `NERelayManager`

**Non-WebKit App Participation**
```swift
let verdict = await NEURLFilter.verdict(for: url)
if verdict == .deny { /* fail request */ }
```

**Cross-references:** WWDC25-246, WWDC19-714

---

## 5. System Services & New Frameworks

### Optimize home electricity usage with EnergyKit (WWDC25-257)

**New Framework: EnergyKit**
- Integrates local electricity grid insights for residential apps
- Primary use cases: EV charging scheduling, smart thermostat control
- Two guidance actions: **Reduce** (thermostats) and **Shift** (EVs)
- Guidance values 0-1, where lower = cleaner/cheaper electricity

**Data Flow**
1. User opts in and selects an `EnergyVenue` (linked to Home app)
2. App fetches `ElectricityGuidance` as AsyncSequence
3. App creates charging schedule based on guidance
4. App submits `LoadEvents` as feedback for insight generation
5. App retrieves `ElectricityInsightRecord` for user-facing summaries

**Best Practice: Event Submission**
- One event every 15 minutes during steady charging
- Create events for significant state changes (pause, schedule change, rapid power change)
- Batch submit events for performance
- Don't submit events between charging sessions
- Events stored with E2E encryption on-device and backed up to CloudKit

**Cross-references:** WWDC25-266, WWDC25-227

---

### Discover Apple-Hosted Background Assets (WWDC25-325)

**On-Demand Resources is Deprecated**
- "On-Demand Resources is a legacy technology, and it will be deprecated" (WWDC25-325)
- Migrate to Background Assets

**Managed Background Assets**
- Three download policies: **Essential** (integrated into install), **Prefetch** (continues in background), **On-Demand**
- Essential can be restricted to `firstInstallation` only (skip on updates)
- System provides a fully-featured downloader extension with zero custom code
- **200GB Apple hosting** included in Developer Program membership

**API Pattern**
```swift
try await AssetPackManager.shared.ensureLocalAvailability(of: assetPack)
let videoData = try AssetPackManager.shared.contents(at: "Videos/Introduction.m4v")
try await AssetPackManager.shared.remove(assetPackWithID: "Tutorial")
```

**Hidden Gem: Shared Namespace**
- System merges all asset packs into a shared namespace reconstructing your source repository
- No need to track which asset pack contains a particular file

**Asset Pack Versioning**
- Asset pack versions are independent of app builds
- One version can be live per context (App Store, external beta, internal beta)
- Updating a live asset pack **affects all installed app versions** -- ensure backward compatibility

**Testing**
- New `ba-serve` mock server for macOS, Linux, Windows
- Requires SSL certificate setup for HTTPS
- Development Overrides in Developer Settings for device configuration

**Info.plist Keys**
- `BAAppGroupID` -- shared app group
- `BAHasManagedAssetPacks` -- enable managed asset packs
- `BAUsesAppleHosting` -- enable Apple hosting

**Cross-references:** WWDC25-324, WWDC25-328, WWDC23-10108

---

### Wake up to the AlarmKit API (WWDC25-230)

**New Framework: AlarmKit**
- Prominent alerts that break through silent mode and focus
- Supports Lock Screen, Dynamic Island, StandBy, Apple Watch
- Two schedule types: **Fixed** (absolute date) and **Relative** (time + weekly recurrence with timezone support)

**Integration with ActivityKit**
- Countdown UI is implemented as a Live Activity (required for countdown support)
- Uses `AlarmAttributes` with custom `AlarmMetadata` protocol conforming type
- System provides fallback countdown presentation for pre-unlock scenarios

**Custom Actions via App Intents**
- Secondary button can execute a `LiveActivityIntent`
- Set `secondaryButtonBehavior` to `.custom` for intent execution or `.countdown` for timer repeat

**Best Practice**
- "Alarms are not a replacement for other prominent notifications, like critical alerts or time-sensitive notifications" (WWDC25-230)
- Use for countdowns with specific intervals or recurring scheduled alerts
- Include remaining duration, dismiss button, and pause/resume in Live Activity

**Authorization**
- Add `NSAlarmKitUsageDescription` to Info.plist
- Authorization requested automatically on first alarm or manually via `AlarmManager.requestAuthorization()`

**Cross-references:** WWDC25-244, WWDC23-10184

---

### Turbocharge your app for CarPlay (WWDC25-216)

**Widgets in CarPlay**
- Support `systemSmall` widget family -- that's all that's needed
- Use `disfavoredLocations([.carPlay])` for widgets not suited for driving
- Disfavor if: widget is a game, requires extensive interaction, relies on data protection classes A/B, or primarily launches non-CarPlay apps

**Live Activities in CarPlay**
- Uses `activityFamily` small size class (same as watchOS Smart Stack)
- Falls back to compact leading/trailing views if small not implemented
- Non-interactive in CarPlay

**Navigation Metadata**
- 54 maneuver types for instrument cluster/HUD display
- "Focus on the semantic meaning of the type, as the car defines how it looks" (WWDC25-216)
- Provide maneuvers up-front to `CPNavigationSession` when route guidance starts
- Multitouch gestures now supported (pinch, pitch, rotate)

**Performance**
- Observe thermal levels and reduce map detail or switch to overview mode
- CADisplayLink frame rates may auto-adapt to device conditions
- Center console and instrument cluster views don't need to show same content

**Cross-references:** WWDC25-308, WWDC25-278, WWDC24-10111, WWDC24-10112, WWDC22-10016

---

## 6. Payments, Commerce & Wallet

### What's new in Apple Pay (WWDC25-201)

**Liquid Glass Pay Button**
- New Apple Pay button treatment adopted automatically by SwiftUI/UIKit apps
- View modifier available to revert to previous style if needed

**Preauthorized Payments**
- Unified view in Wallet app for all preauthorized payments
- Merchants can provide: icon (via Apple Business Connect), custom name, description, images
- Merchant Token Usage Information endpoint returns encrypted zip (max 5MB) with logo, product images, localization

**Automatic Order Tracking**
- Wallet now ingests order information from emails automatically
- Detects merchant name, delivery window, tracking numbers
- For best results: adopt Order Tracking API directly for full features (emailless updates, receipts, returns)

**FinanceKit Background Delivery**
- New extension type: background delivery extension
- Notified when finance store data changes (accounts, balances, transactions)
- Three update frequencies: hourly, daily, weekly
- Limited time window for execution; `willTerminate` callback for graceful shutdown
- Authorization from main app inherited by extension
- FinanceKit now available in UK via Connected Cards (Open Banking)

**Cross-references:** WWDC25-202, WWDC24-2023, WWDC23-10114, WWDC22-10041

---

### What's new in Wallet (WWDC25-202)

**Multi-Event Tickets**
- Tickets can now contain upcoming events for a series
- Enhanced boarding pass design with new visual treatment

**Automatic Pass Addition**
- New APIs for seamlessly adding passes to Wallet programmatically

**Cross-references:** WWDC25-201

---

### What's new in StoreKit and In-App Purchase (WWDC25-241)

**New Fields**
- `appTransactionID` on AppTransaction, Transaction, and RenewalInfo (back-deployed to iOS 15)
- `originalPlatform` (iOS 18.4) -- identifies platform where app was originally purchased
- `offerPeriod` (iOS 18.4) -- subscription period for redeemed offers
- `advancedCommerceInfo` -- for Advanced Commerce API users
- `appAccountToken` on RenewalInfo

**Offer Codes Expanded**
- Now available for consumables, non-consumables, and non-renewing subscriptions
- Redeemable back to iOS 16.3

**JWS-Signed Purchase Requests**
- New `introductoryOfferEligibility` and `promotionalOffer` purchase options require compact JWS
- App Store Server Library (Java, Python, Node.js, Swift) simplifies signing

**New: SubscriptionOfferView**
- Merchandises individual subscription plans with `visibleRelationship` parameter
- Five relationships: upgrade, downgrade, crossgrade, current, all
- `subscriptionOfferViewDetailAction` modifier for directing traffic to subscription store

**UI Context for Purchases (iOS 18.2+)**
- Purchase methods now require UI context (UIViewController on iOS, NSWindow on macOS)
- SwiftUI: use `@Environment(\.purchase)` for automatic context

**Cross-references:** WWDC25-328, WWDC24-10062, WWDC23-10013, WWDC21-10114

---

### What's new in AdAttributionKit (WWDC25-221)

**Overlapping Re-engagement Conversions (iOS 18.4)**
- Multiple active re-engagement conversion windows simultaneously
- Conversion tags act as bookmarks for specific conversions
- Extract tag from URL: `Postback.reengagementOpenURLParameter`

**Configurable Attribution Rules**
- Attribution window: per ad-network, per interaction type (view-through/click-through)
- Attribution cooldown: configurable delay before new conversions can override
- Both configured in Info.plist

**Geography Data in Postbacks**
- New `countryCode` field derived from App Store storefront
- For re-engagement: uses same location as original install

**Testing in iOS Settings**
- Create development postbacks directly in Settings > Developer > Development Postbacks
- Control data granularity per postback for server implementation testing
- Postbacks signed with different key (new `kid` value)

**Cross-references:** WWDC25-246, WWDC24-10060

---

## 7. Localization & Internationalization

### Enhance your app's multilingual experience (WWDC25-222)

**New: Language Discovery API**
- Discover user's preferred languages without exposing full list
- Privacy-preserving: app only learns which of its supported languages match

**Alternate Calendar Support**
- Better framework support for non-Gregorian calendars

**Bidirectional Text Improvements**
- **Natural Selection** for selecting multiple ranges in bidirectional text
- Better cursor movement and text handling in mixed LTR/RTL content

**Cross-references:** HIG: Right to left

---

### Code-along: Explore localization with Xcode (WWDC25-225)

**String Catalogs Enhancements**
- **Type-safe Swift symbols** for localized strings defined in String Catalog
- Symbols appear as auto-complete suggestions
- Define strings directly in String Catalog that produce Swift symbols accessible in code

**AI-Generated Translation Context**
- Xcode analyzes where/how localized strings are used and generates comments using on-device model
- Helps translators understand context without asking developers

**Best Practices for Translators**
- Export/import XLIFF files for external translators
- Use string catalog comments to provide context
- For large projects: organize strings across multiple catalogs, use namespacing

**Cross-references:** WWDC25-247

---

## 8. Web Technologies

### Meet WebKit for SwiftUI (WWDC25-231)

**New: Native SwiftUI WebView**
- `WebView(url:)` for basic web content display
- `WebView(html:)` for inline HTML
- Full navigation control, JavaScript communication, and content customization

**Communication with Pages**
- `@WebPage` property wrapper for page state observation
- JavaScript message handlers for bidirectional communication
- `userContentController` for injecting scripts

**Cross-references:** WWDC25-236

---

### What's new in Safari and WebKit (WWDC25-233)

**CSS Animations**
- Scroll-driven animations now fully supported
- Cross-document view transitions
- Anchor positioning for popovers and tooltips

**Layout**
- Masonry layout support in CSS
- Container queries

**Visual Effects**
- Backdrop filter improvements
- New color functions

**Media**
- Web Speech API support
- HEIC/HEIF image support in web
- SVG favicon support

**Cross-references:** Safari Technology Preview, caniuse.com

---

### Learn more about Declarative Web Push (WWDC25-235)

**Declarative Web Push**
- Alternative to traditional Web Push that's "more efficient and transparent by design"
- Server sends structured JSON notification payload directly
- Backward compatible with original Web Push
- Service Worker support for hybrid approaches
- No JavaScript execution needed for notification display

**Cross-references:** webkit.org blog

---

### Unlock GPU computing with WebGPU (WWDC25-236)

**WebGPU Now Available**
- Safe GPU access for graphics and general-purpose computation
- WGSL shading language for GPU programs
- Works with three.js, babylon.js, Transformers.js (Hugging Face)

**Performance Best Practices**
- Minimize GPU pipeline state changes
- Use buffer binding offsets instead of creating new buffers
- Test on both desktop and mobile for power efficiency

**Cross-references:** Metal Performance Shaders

---

### What's new for the spatial web (WWDC25-237)

**HTML `<model>` Element**
- Inline 3D models on web pages (USDZ format)
- Model lighting, interactions, and animations
- No JavaScript required for basic display

**Immersive Media on Web**
- 360-degree video embedding
- Apple Immersive Video support
- Custom environments for web pages (preview)

**Cross-references:** Reality Composer, QuickLook

---

### Meet PaperKit (WWDC25-285)

**New Framework: PaperKit**
- Integrates PencilKit drawing with markup features (shapes, images, text)
- Available on iOS, iPadOS, macOS, and visionOS
- Customizable toolbar and feature set
- Forward compatibility best practices for document format

**Cross-references:** WWDC24-10214

---

## 9. Cross-Cutting Themes

### Privacy as a Platform Principle
Multiple sessions reinforce privacy at every layer:
- **Quantum-secure TLS** enabled by default (WWDC25-314)
- **URL filtering** uses PIR and Oblivious HTTP to prevent even Apple from seeing queries (WWDC25-234)
- **Declared Age Range** reveals ranges, not birth dates (WWDC25-299)
- **PermissionKit** keeps parent-child communication in Messages (WWDC25-293)
- **AdAttributionKit** measures campaigns without user tracking (WWDC25-221)
- **EnergyKit** events stored with E2E encryption (WWDC25-257)
- **Wi-Fi Aware** connections encrypted at the Wi-Fi layer (WWDC25-228)

### Deprecation Watch
- **On-Demand Resources**: deprecated, migrate to Background Assets (WWDC25-325)
- **Secure Transport**: will not support quantum-secure TLS (WWDC25-314)
- **Legacy networking APIs**: migrate to URLSession/Network.framework (WWDC25-314)
- **Non-Network Extension VPN implementations**: "highly discouraged" (WWDC25-234)

### Action Items for iOS Developers
1. **Enable quantum-secure TLS** on your servers (client-side automatic in iOS 26)
2. **Adopt passkey account creation API** for new user onboarding
3. **Add automatic passkey upgrades** on every password sign-in
4. **Migrate from On-Demand Resources** to Background Assets
5. **Add Declared Age Range** if your app serves minors
6. **Enable Enhanced Security** capability for apps with significant attack surface
7. **Adopt StoreKit 2** with new SubscriptionOfferView for subscription merchandising
8. **Add accessibility identifiers** comprehensively for UI automation
9. **Serve well-known passkey-endpoints** JSON from your website
10. **Review privacy manifests** and nutrition labels before deployment
