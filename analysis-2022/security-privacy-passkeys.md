# Security, Privacy & Passkeys (2022)

WWDC22 was the year passkeys went mainstream. Apple shipped the FIDO Alliance / WebAuthn-based replacement for passwords across all platforms, with sync via iCloud Keychain, AirDrop sharing, and cross-device sign-in via QR codes. Beyond passkeys, the lineup includes Private Access Tokens, Web Push for Safari, Passkey-aware Sign in with Apple, and developer-mode hardening.

## Sessions covered
- WWDC22-10092 — Meet passkeys
- WWDC22-10122 — Enhance your Sign in with Apple experience
- WWDC22-10077 — Replace CAPTCHAs with Private Access Tokens
- WWDC22-10079 — Improve DNS security for apps and servers
- WWDC22-10096 — What's new in privacy
- WWDC22-10108 — Streamline local authorization flows
- WWDC22-10109 — What's new in notarization for Mac apps
- WWDC22-10167 — Create your Privacy Nutrition Label
- WWDC22-110344 — Get to know Developer Mode
- WWDC22-10166 — Explore App Tracking Transparency
- WWDC22-110341 — Explore SMS message filters

## Passkeys (10092)

### What they are
Replacements for passwords built on WebAuthn / FIDO. Each "passkey" is a public-private keypair generated per-account by your device. The server only ever sees the public key. Your private key never leaves the device (or, on Apple devices, never leaves your iCloud Keychain — synced end-to-end-encrypted across your devices).

### Why this matters
- **No more credential leaks.** Even if the server is breached, attackers can't sign in — they only have public keys.
- **No more phishing.** The cryptographic challenge-response is bound to the actual domain. Fake sites can't trick you.
- **No more password reuse problem.** Every passkey is unique by construction.
- **No more "is the SMS code factor secure enough?"** A single passkey beats password+SMS on every relevant security axis.

### User experience
- **One-tap sign-in via QuickType bar.** When you focus a username field with a saved passkey, it appears in the QuickType bar. Tap → biometric → signed in.
- **AirDrop sharing.** Right-click a passkey in Settings → Share → AirDrop to a partner's device.
- **Cross-device sign-in via QR code.** When signing in on a friend's PC, scan a QR code with your iPhone. The phone and browser perform local key agreement, prove physical proximity (via Bluetooth advertisement), then connect through a server-relayed end-to-end encrypted channel.

### iOS adoption (in your app)
The API is `ASAuthorization*` in AuthenticationServices. Two key calls:

#### AutoFill-assisted (the recommended primary path)
```swift
let provider = ASAuthorizationPlatformPublicKey CredentialProvider(relyingPartyIdentifier: domain)
let request = provider.createCredentialAssertionRequest(challenge: challenge)
let controller = ASAuthorizationController(authorizationRequests: [request])
controller.delegate = self
controller.presentationContextProvider = self
controller.performAutoFillAssistedRequests()
```

The passkey appears in the QuickType bar above the keyboard. **Start this request EARLY in view lifetime** before the user focuses the field — otherwise the suggestion won't be ready when the keyboard appears.

#### Modal sign-in
Same code, but call `controller.performRequests()` instead. Used when the user typed a username instead of accepting the AutoFill suggestion.

### Critical UI guidelines
- "Passkey" is a common noun — lowercase, like "password," same pluralization.
- Use the new SF Symbol `person.key.badge` (and `.fill`) for iconography.
- Make sure your `webcredentials` associated domain is set up so the system knows which passkeys to suggest in your app.

### Server adoption
- Adopt **WebAuthn** on your backend (any standard implementation works).
- Apple platforms always require user verification (biometrics) when biometrics are available.
- Use `userVerification: "preferred"` in WebAuthn requests — never specify `"required"` (creates bad UX on devices without biometrics).

### Web adoption
On the web, annotate the username field with both `username` and `webauthn` autocomplete tokens:
```html
<input name="username" autocomplete="username webauthn">
```
Use WebAuthn JavaScript API with `mediation: "conditional"` for AutoFill-assisted requests. Without `conditional`, you get a modal request — user-gesture-driven, like a button click.

### Allow lists
For modal sign-in after a username is typed, fetch the user's credential IDs from your backend and pass them as an allow list to the request. Only matching passkeys appear in the picker.

### `preferImmediatelyAvailableCredentials`
By default, a modal request with no local passkeys shows a QR code immediately. Set this option to silently fall back instead — useful for "try passkey, else show password form" patterns. You'll receive an `ASAuthorizationError.canceled` if no credentials are available.

### Combined credential requests
You can pass passkey + password + Sign in with Apple requests to the same `ASAuthorizationController`. The picker shows whichever credentials are actually available, so single-credential users don't see options they don't have.

## Sign in with Apple (10122)
- **AutoFill flow improvements** — Sign in with Apple now appears in the QuickType bar.
- **Hide My Email forwarding** — control which sender addresses can email a user's relay address; new private-key-signed messages.
- **Refresh tokens** — refresh validity changed; check the docs.
- **App Transfer support** — keep user signatures stable across app ownership transfers.

## Private Access Tokens (10077)
A privacy-preserving CAPTCHA replacement. The browser/OS proves "this is a real device, not a bot" via cryptographic attestation, without sharing the user's identity with the server. Apple's iCloud Private Relay attestation issuer is supported. Adopt on your server via the `WWW-Authenticate: PrivateToken` challenge.

## Privacy nutrition labels (10167)
Self-service in App Store Connect. **You're responsible for accuracy.** Apple now provides a downloadable template/printable description. Categories: Data Used to Track You, Data Linked to You, Data Not Linked to You.

## Privacy hardening in iOS 16 (10096)
- **Pasteboard access prompts.** Programmatic pasteboard reads now show an alert (used to be a banner). Use the new `UIPasteControl` (looks like a filled `UIButton`) for one-tap paste with system trust.
- **`UIDevice.name`** returns the model name, not the user's custom name. Custom name requires entitlement.
- **App Tracking Transparency** clarifications and stricter enforcement.
- **System Photos picker** improvements — apps don't need full photo-library access for the new picker.

## Developer Mode (110344)
**Required in iOS 16 for development-signed and TestFlight builds.** Enable via `Settings → Privacy & Security → Developer Mode`. Reboots the device. After reboot, you can install dev-signed apps. This was a security hardening — production users can't be tricked into running random dev builds.

## Local authorization (10108)
- **`ASAuthorization` for password sign-in** got first-class support — even non-passkey password sign-ins should go through this API for consistent UX.
- **LocalAuthentication** improvements for biometric prompts in flows.

## Best practices
- **BEST PRACTICE**: Use AutoFill-assisted passkey requests as your primary path. Start them EARLY in view lifetime.
- **BEST PRACTICE**: Combine passkey + password + Sign in with Apple in a single `ASAuthorizationController` — single-credential users see only what they have.
- **BEST PRACTICE**: Always use `userVerification: "preferred"` (the WebAuthn default), never `"required"`.
- **BEST PRACTICE**: Annotate web username fields with `autocomplete="username webauthn"` for both passkey and password suggestions.
- **HIDDEN GEM**: Passkey cross-device sign-in is end-to-end encrypted via server relay — it's not just a QR code, it includes Bluetooth proximity proof so remote attackers can't replay the QR.
- **HIDDEN GEM**: `preferImmediatelyAvailableCredentials` lets you silently fall back to your password form when no local passkeys exist.
- **HIDDEN GEM**: Apple-provided platform authenticator credentials created before iOS 16 still work but stay device-bound. New ones become passkeys (synced via iCloud Keychain). Differentiate during registration: passkeys don't provide an attestation statement.
- **URGENT**: Developer Mode must be enabled in iOS 16 to install development-signed builds. Existing TestFlight users may need to enable it on first launch.
- **DEPRECATION**: `UIDevice.name` no longer returns user-set name without entitlement.

## Cross-references
- Pairs with the new `ASAuthorization` patterns in `Streamline local authorization flows` (10108).
- Sign in with Apple (10122) integrates with the same picker.
- Privacy nutrition labels (10167) inform users about the data your passkey-using app handles.
