# Sign In with Apple, Authentication & Privacy — WWDC 2019 Analysis

**Sessions covered:** 706 (Introducing Sign In with Apple), 516 (What's New in Authentication), 708 (Designing for Privacy), 709 (Cryptography and Your Apps), 701 (Advances in macOS Security), 717 (What's New in Universal Links)

## Headline

Sign In with Apple is the biggest auth/identity launch of the year. Two-factor by default, no password to forget, hidden-email relay, real-user indicator for fraud detection, and cross-platform via JavaScript SDK. Combined with CryptoKit, the new Network framework crypto, and the `AuthenticationServices` framework, this is Apple's privacy-first stack.

## Sign In with Apple — The Four Steps (706)

1. **Add the button**: `ASAuthorizationAppleIDButton` (one line).
2. **Configure & perform request**: `ASAuthorizationAppleIDProvider().createRequest()`, set `requestedScopes = [.fullName, .email]`, hand to `ASAuthorizationController`, call `performRequests()`.
3. **Handle the result** in `authorizationController(_:didCompleteWith:)`: cast `authorization.credential` to `ASAuthorizationAppleIDCredential`. You get:
   - `user` — stable, team-scoped unique identifier (this is your primary key).
   - `identityToken` + `authorizationCode` — for server-side verification with Apple.
   - `fullName`, `email` (only if requested AND user shared).
   - `realUserStatus` — `.likelyReal`, `.unknown`, or `.unsupported`.
4. **Handle credential state changes**: call `provider.getCredentialState(forUserID:)` at app launch. States: `.authorized`, `.revoked`, `.notFound`. Subscribe to `ASAuthorizationAppleIDProvider.credentialRevokedNotification`.

## The Quick Sign-In Flow (706)

**HIDDEN GEM** — call this on app launch when you have no local session:

```swift
let requests = [ASAuthorizationAppleIDProvider().createRequest(),
                ASAuthorizationPasswordProvider().createRequest()]
let controller = ASAuthorizationController(authorizationRequests: requests)
controller.performRequests()
```

This combined call returns the user's **existing iCloud Keychain password OR existing Apple ID credential** in one tap, preventing duplicate accounts. If neither exists, you immediately get an error and show your normal login flow.

## Hide My Email Relay (706)

- When the user picks "Hide My Email", you receive a routing address `xyz@privaterelay.appleid.com`.
- Apple forwards real user emails to and from that address. Two-way email works.
- **BEST PRACTICE**: Configure your domain and email senders in the developer portal at developer.apple.com so your transactional emails don't get rejected.

## Real User Indicator (706)

- `realUserStatus` combines on-device intelligence + Apple ID account history into a single bit: `.likelyReal` or `.unknown`.
- **BEST PRACTICE**: Treat `.likelyReal` users like trusted accounts (skip captcha, fast-track verification). Treat `.unknown` like any other new account.

## Cross-Platform via JavaScript (706)

- Drop in Apple's JS SDK on any web platform (Windows, Android, web).
- On Safari, the button transforms into a native Apple Pay-style sheet with TouchID. **HIDDEN GEM**: huge UX win for web users on Apple devices.
- On other platforms it's a redirect-based OAuth-like flow.

## App Store Mandate (706, App Store Guidelines update)

If your app uses any third-party social sign-in (Facebook Login, Google Sign-In, etc.), you **must** also offer Sign In with Apple. **URGENT** — this rule went into effect April 2020 with all new app submissions.

## CryptoKit (709)

A brand-new Swift-native crypto framework. Replaces direct `CommonCrypto` usage for most apps.

- `SHA256`, `SHA384`, `SHA512`, `SHA1` (legacy), `MD5` (legacy).
- `SymmetricKey`, `AES.GCM.seal(_:using:)` / `.open(_:using:)` — authenticated encryption with one line.
- `ChaChaPoly` — alternative AEAD.
- `HMAC<H>`.
- `Curve25519.KeyAgreement.PrivateKey` — modern elliptic curves with X25519.
- `P256`, `P384`, `P521` ECC for FIPS use cases.
- `SecureEnclave.P256.Signing.PrivateKey` — keys generated and used inside the Secure Enclave never leave the chip. **HIDDEN GEM**.
- All keys conform to value-type semantics. No more `SecKeyRef` / Keychain dance for ephemeral keys.

## Universal Links Improvements (717)

- New `apple-app-site-association` syntax with components, query parameters, exclusions.
- Universal Links now work in SafariViewController and SFAuthenticationSession redirects.
- **HIDDEN GEM**: you can use `appLinks` patterns with wildcards now (`/products/*`, `/users/*/posts`).

## Designing for Privacy (708)

Five themes that became the foundation for App Tracking Transparency in 2020/iOS 14:

1. **Use the minimum data necessary** — request only the fields you actually need.
2. **On-device processing wherever possible** — Vision, Speech (now on-device), CoreML, Create ML all run locally.
3. **Just-in-time permission requests** — ask when the feature is invoked, not at launch.
4. **Clearly explain why** — usage description strings should describe the user benefit, not the technical reason.
5. **Approximate location is often enough** — iOS 14 added precise/approximate, but the seeds were planted here.

## Network Privacy (701, 712)

- New "Find My" cross-broadcast protocol (mentioned but full details came later).
- Random MAC address per-network on iOS 14 (foreshadowed in this year's Wi-Fi privacy talks).

## Cross-references

- Authentication services framework details: 516 (What's New in Authentication).
- Backend verification of identityToken: server-side JWT validation against `https://appleid.apple.com/auth/keys`.
- Replaces: Facebook Login mandate driver, OAuth flows in many apps.
