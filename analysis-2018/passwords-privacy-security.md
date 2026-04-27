# Passwords, Privacy & Security — WWDC 2018 Analysis

**Sessions covered:** 204 (Automatic Strong Passwords and Security Code AutoFill), 222 (Data You Can Trust), 718 (Better Apps through Better Privacy), 721 (Implementing AutoFill Credential Provider Extensions), 702 (Your Apps and the Future of macOS Security), 703-mac (Notarization), 207 (Strategies for Securing Web Content), 102 (Platforms State of the Union §Security)

## Headline

WWDC 2018 made strong passwords _automatic_ — iOS 12 generates a 20-character random password right inside your signup field, suggests usernames from existing iCloud Keychain credentials, autofills SMS verification codes from the QuickType bar, and lets third-party password managers act as autofill providers. On the security side: macOS Mojave gates camera/microphone access, introduces app **Notarization** as a stepping stone toward mandatory cloud-scanned distribution, and `NSKeyedArchiver` finally has secure-by-default APIs that return errors instead of throwing exceptions.

## Automatic Strong Passwords (204, 102)

The whole signup flow becomes ~3 taps:

1. User taps username field → QuickType suggests `chelsea@example.com` (pulled from existing iCloud Keychain entries on their device).
2. User taps password field → 20-character random password autofilled, format `ABc-d3F-gHij-klmn-OPQR`.
3. User taps "Sign Up." iCloud Keychain has stored the credential; it syncs to all their devices.

For your app to participate, three things:

```swift
// 1. Email field
emailField.textContentType = .username
emailField.keyboardType = .emailAddress

// 2. Password field
passwordField.textContentType = .newPassword   // .password for sign-in screens
passwordField.isSecureTextEntry = true

// 3. (optional) Custom password rules if your service has constraints
passwordField.passwordRules = UITextInputPasswordRules(
  descriptor: "required: upper; required: lower; required: digit; required: [$]; allowed: [-];"
)
```

That's it. Plus you need an associated domain (the `apple-app-site-association` file you already serve for Universal Links).

**HIDDEN GEM**: Apple maintains a **Password Rules Validation Tool** at developer.apple.com that lets you experiment with the rules language and download generated passwords for backend testing. Copy the rules straight into your `passwordRules` property.

## SMS Code Autofill (204)

- New text content type `.oneTimeCode`. Tag your 2FA / OTP fields with it.
- iOS scans incoming messages for code-like patterns (digit run + a word like "code" / "passcode" / "verification" / language-localized variants).
- The detected code appears _in the QuickType bar_ — single-tap fill.
- Works in iOS apps and Safari (`<input autocomplete="one-time-code">`).
- macOS Mojave: text-message forwarding pushes the code to Mac too — Safari autofill on desktop without leaving the page.
- **URGENT**: do not build your own keyboard for OTP entry. iOS needs the system keyboard to inject the code. Custom input views break the flow and accessibility.
- Test by texting yourself; if the code is underlined and "Copy Code" appears in the long-press menu, you're golden.

## Saving Passwords on Login (204)

- iOS 12 now offers to save credentials when the user logs in successfully — same prompt as Safari for years.
- Triggered when iOS detects a sign-in: form fields removed from the view hierarchy after submission, with non-empty values.
- **GOTCHA**: clear field text **after** removing the view from the hierarchy, not before. iOS reads the values when fields disappear.
- If iOS picks the wrong domain to save to, override with `WebCredentials Associated Domains` service in your Entitlements.

## Federated Sign-In: ASWebAuthenticationSession (204)

- Replaces `SFAuthenticationSession` for "Sign in with Google/Facebook/Twitter/etc." flows.
- New AuthenticationServices framework. Block-based API:
```swift
let session = ASWebAuthenticationSession(url: oauthURL, callbackURLScheme: "myapp") { url, error in ... }
session.start()
```
- Shares cookies with Safari (with explicit user consent prompt), so if the user is already signed in to the federated provider in Safari, the in-app flow may complete with a single tap.
- Holds a strong reference yourself; cancel via `session.cancel()` if needed.

## Third-Party Password Manager Extensions (721)

- New extension point: `Credential Provider`. Apps like 1Password and Dashlane can vend credentials into the QuickType bar alongside iCloud Keychain.
- All your work to support iCloud Keychain autofill (associated domains + content types) automatically helps third-party managers too. **HIDDEN GEM**: nothing extra to do.

## Notarization for Mac Apps (102, 702)

- New step in the macOS distribution pipeline outside the Mac App Store.
- After codesigning with your Developer ID, submit the app to Apple's **Notary Service** (`xcrun altool --notarize-app ...`). Apple scans for malware, returns a stapled ticket attached to your bundle.
- Mojave checks the ticket on first launch via Gatekeeper; missing or revoked → blocked.
- Crucially, revocation is now per-version, not per-developer-certificate. Apple can ban a single bad release without nuking your signing identity.
- **URGENT**: not yet mandatory for Mojave but a future macOS release will require it. Start now. Notarization is _not_ App Review — there are no content guidelines, only security scanning.

## Hardened Runtime (102, 702)

- Opt-in security baseline: block code injection (DYLD_INSERT_LIBRARIES), disable debugger attachment by other processes, prevent unsigned executable memory, restrict access to user data unless properly entitled.
- Required for notarization in the long run. Backwards compatible — your app keeps running without it, but enabling unlocks future security guarantees.

## Mojave Privacy Permissions (102, 702)

- New consent prompts for: Camera, Microphone, Mail history, Contacts, Calendars, Reminders, Photos, Safari/Chrome data, Time Machine backups, iTunes backups, system cookies, screen recording, automation (sending Apple Events to other apps).
- **URGENT**: handle the rejection gracefully. A camera-using app should display an "enable camera in Settings" UI when permission is denied, not crash.
- Provide good `NSCameraUsageDescription` etc. purpose strings — App Review is reading them more closely. Generic "needed for app functionality" gets rejected.

## Better Privacy Storytelling (718)

- Apple's overall framing: privacy is built on data minimization, on-device intelligence, transparency + control, security.
- Examples Apple cited:
  - Maps uses rotating random identifiers, never tied to Apple ID.
  - Photos uses on-device intelligence for Search and Memories — your photo collection isn't analyzed in the cloud.
  - Face ID data is encrypted on the Secure Enclave and never leaves the device.

**BEST PRACTICE**: when you write purpose strings, be specific about what features they enable. "Used to find your friends nearby" is better than "Used for various app features."

## Secure Coding Defaults (222, 209)

- Old: `NSKeyedArchiver` and `NSKeyedUnarchiver` could be used insecurely; secure coding was opt-in via `requiresSecureCoding` and would throw exceptions on failure.
- New: `NSKeyedUnarchiver.unarchivedObject(ofClass: SomeClass.self, from: data)` is **secure by default** + returns errors instead of exceptions.
- The non-secure APIs are deprecated immediately (no formal soft-deprecation period — Apple wants you off them now).
- New value transformer: `NSValueTransformerName.secureUnarchiveFromDataTransformerName` for Cocoa bindings / Core Data attribute transformers.
- All AppKit and Foundation classes that participate in archiving have adopted `NSSecureCoding`.

## Web Content Security (207)

- WKWebView now supports `URLSchemeHandler` for custom schemes — finally able to intercept `myapp://...` URLs without manual JS injection.
- Content Security Policy support is more complete; CSP nonce/hash directives validated.
- WebSockets in `WKWebView` work natively. Service Workers shipping in Safari 12.

## Cross-references

- For background-app authentication and biometric prompts: outside this set but `LocalAuthentication` framework matured.
- Apple's HealthKit data is treated as the most sensitive data on the platform: see 707 (workouts) and 706 (health records) for the privacy model.
- Sign In with Apple is one year away (WWDC 2019 — session 706).
