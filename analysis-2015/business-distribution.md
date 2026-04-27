# App Store, Distribution, Enterprise & Privacy — WWDC 2015 Analysis

**Sessions covered:** 303 (Getting the Most out of App Analytics), 302 (What's New in iTunes Connect), 304 (iTunes Connect: Development to Distribution), 301 (What's New in Managing Apple Devices), 306 (Supporting the Enterprise with OS X Automation), 703 (Privacy and Your App), 706 (Security and Your Apps), 717 (What's New in Network Extension and VPN), 719 (Your App and Next Generation Networks), 706 (Security and Your Apps), 702 (Apple Pay Within Apps), 701 (Wallet)

## Headline

App Analytics launches in iTunes Connect — first-party, free, opt-in user telemetry that respects privacy. App Transport Security (ATS) becomes default-on, enforcing TLS 1.2 + forward secrecy. Apple Pay expands inside apps via PKPaymentRequest. Wallet rebrands from Passbook. The privacy story tightens: `canOpenURL` whitelist, MAC address randomization expansion, sandbox restrictions on `kern.proc`.

## App Analytics (303)

iTunes Connect's first first-party analytics product.

- Opt-in by user (Settings → Privacy → Diagnostics & Usage → Share With App Developers).
- Aggregated across all opted-in users; thresholds prevent de-anonymization.
- **Engagement**: sessions, app launches, time spent.
- **Sales & trends**: real-time downloads, pre-orders, in-app purchases.
- **App store performance**: page views, source attribution (which Universal Link / Smart App Banner / direct App Store visit drove the install).
- Custom NSUserActivity events surface in App Analytics if you mark them `eligibleForPublicIndexing` AND they meet engagement thresholds.

**HIDDEN GEM**: zero code changes required. Just check the box in iTunes Connect.

## iTunes Connect Improvements (302, 304)

- **TestFlight expansion**: external testers (up to 2,000 people via email) plus internal team. 60-day testing windows.
- iTunes Connect API for partial automation of metadata and binary submission.
- Bug-fix-only resubmission while previous version is still in review.
- Phased release control (gradual rollout over 7 days for automatic-update users).
- App Analytics in the same workspace.

## Privacy (703)

A landmark privacy session.

### Identifier strategy

- Always ask: do you NEED an identifier, or can you increment a server-side counter via API call?
- Choose the right scope: session ID, user ID, device install ID. Each carries different privacy implications.
- Rotate identifiers on a schedule appropriate to the use (e.g., 15-min rotation in search to break long-term correlation).
- iOS provides identifierForVendor (IDFV) — resets when all apps from your team are uninstalled. And advertisingIdentifier (IDFA) — user-resettable, with a `Limit Ad Tracking` flag the user can set.
- **CRITICAL**: ALWAYS check `ASIdentifierManager.shared().isAdvertisingTrackingEnabled` BEFORE reading IDFA. Always re-fetch IDFA fresh; never cache.

### Reporting

To respect privacy when reporting to third parties:
1. **Report insights, not data** — "X% of users are frequent users" instead of the raw events.
2. **Aggregate** — "12,000 frequent users" instead of "user 123, user 456...".
3. **Threshold** — never report a group with 1 or 2 users; that's identification, not reporting.

### Background changes

- iOS 9 expands MAC address randomization to more Wi-Fi scan types. **DOCS MISS THIS**: hardware-pairing apps that relied on the device's true MAC must test on iOS 9.
- `canOpenURL:` now requires a whitelist (`LSApplicationQueriesSchemes` in Info.plist; max 50 schemes for legacy apps; undeclared schemes always return false). See `search-and-deep-linking.md`.
- `kern.proc`, `kern.procargs`, `kern.procargs2` sysctls are sandbox-blocked. Apps can no longer enumerate other processes' info.
- App-installed-detection via custom URL schemes is dead. Move to extensions and Universal Links.

### Just-in-time prompts and purpose strings

- Required `Info.plist` purpose strings for every protected data class (`NSCameraUsageDescription`, `NSLocationWhenInUseUsageDescription`, `NSPhotoLibraryUsageDescription`, etc.). Without them, the prompt won't even appear.
- The watch shares iOS's authorization decisions. A user grants location once → both apps have it.
- Watch prompts can be dismissed without yes/no — your app must handle the unset state gracefully.

### Data Protection Classes (703)

Applied per file:
- `noProtection` — never use this. Default for older apps was effectively this.
- `protectedUntilFirstAuthentication` (iOS 7+ default for third-party data) — not accessible at boot, accessible after first unlock, accessible while locked.
- `protectedUnlessOpen` — for write-anytime, read-only-while-unlocked. Mail uses this for new incoming messages.
- `complete` — accessible only while device is unlocked. Use for sensitive data (HealthKit, financial, passwords).

**HIDDEN GEM**: test with data protection enabled (Settings → Touch ID & Passcode shows whether DP is on). Apps that work fine on a developer-passcode-less device may crash with permission errors on real users.

## App Transport Security (711, 703)

iOS 9 default-on. All higher-level network APIs (NSURLSession, NSURLConnection, WebKit-loaded resources) require:
- HTTPS
- TLS 1.2 minimum
- Forward secrecy ciphers
- Certificate must be SHA-256+

Exceptions go in `NSAppTransportSecurity` in Info.plist:
- `NSAllowsArbitraryLoads` (avoid! all-or-nothing).
- `NSExceptionDomains` (per-domain exceptions for legacy partners).
- Per-domain: `NSExceptionAllowsInsecureHTTPLoads`, `NSIncludesSubdomains`, `NSExceptionMinimumTLSVersion`.

**BEST PRACTICE**: per-domain exceptions are the safe path. Never blanket-disable.

## Security (706)

- Keychain enhancements: shared groups via entitlements (cross-app credential sharing within your team).
- `kSecAttrAccessGroup` for the access group identifier.
- Touch ID for sensitive Keychain items: `kSecAccessControlTouchIDAny`, `kSecAccessControlTouchIDCurrentSet`.
- CryptoKit not yet — but `CommonCrypto` and Security framework gain Swift-friendliness.

## Apple Pay In-App (702, 701)

- Wallet (renamed from Passbook) hosts Apple Pay credit/debit cards, store cards, transit cards, boarding passes.
- `PKPaymentRequest` for in-app payments — supports Apple Pay, no need to handle card numbers yourself.
- Bank app entitlement for provisioning cards directly into Wallet (no manual card-image scanning).
- NFC contactless transactions can present a rewards card encrypted via the new `nfc` dictionary in pass.json — see `business-distribution.md`.
- Apple Pay can be suppressed via API for apps showing barcodes near NFC terminals.

## Network Extension & VPN (717)

iOS 9 introduces three new VPN extension points:

- **PacketTunnelProvider**: implement custom VPN tunneling protocols.
- **AppProxyProvider**: client side of custom transparent network proxies.
- **FilterControlProvider / FilterDataProvider**: dynamic on-device content filtering (parental controls, enterprise filtering).

This is the foundation for full enterprise VPN apps without a custom hardware appliance.

## Enterprise Mobile Device Management (301, 306)

- New MDM payloads for app management, restrictions, single sign-on configuration.
- Apple Configurator improvements for iOS provisioning at scale.
- OS X automation: AppleScript, Automator, and shell scripts updates for Yosemite/El Capitan.

## Cross-references

- App Analytics (303) plus NSUserActivity public indexing (709) plus engagement signals are tightly intertwined.
- Privacy (703) is the unifying thread across canOpenURL (107), MAC randomization, sandbox restrictions, search APIs (709).
- ATS (711) plus Sign in with Apple ID via Web Services (704) plus Safari View Controller (504) form a coherent secure-by-default story.
- Apple Pay (702) plus Wallet (701) plus Watch (105) plus rewards-card NFC encryption are the in-store commerce arc.
