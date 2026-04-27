# Touch ID & Keychain — WWDC 2014 Analysis

**Sessions covered:** 711 (Keychain and Authentication with Touch ID), 715 (User Privacy in iOS and OS X)

## Headline

iOS 8 opens up **Touch ID to third-party developers** for the first time. Two integration paths: **Keychain Item Access Control Lists** that biometrically gate keychain reads, and the new **`LocalAuthentication`** framework for app-level biometric auth. All Touch ID processing remains in the **Secure Enclave**; fingerprint images are never accessible to the kernel, let alone your app.

## The Mental Model — Secure Enclave Trust (session 711)

- The **Secure Enclave** is a separate security coprocessor on the A7. It owns:
  - Touch ID matching (registered fingerprints + the matching algorithm)
  - Data Protection cryptographic keys (per-class and per-passcode)
  - The user's passcode (never sent to the application processor)
- **Even the iOS kernel cannot access registered fingerprints or fingerprint images.** This isn't a software boundary; it's a hardware boundary (711).
- Touch ID match results are passed from the Secure Enclave to **`securityd`** (the Keychain daemon). `securityd` uses the result to authorize keychain decryption operations — without your app or any other component ever seeing the actual fingerprint data (711).
- **`LocalAuthentication`** (the new framework) gives apps the same yes/no biometric result for app-level authentication, without requiring that the secret being protected live in the keychain (711).

## Keychain Item ACLs (session 711)

- A new keychain item attribute `kSecAttrAccessControl` carries a **`SecAccessControl`** object describing accessibility + authentication policy.
- **Accessibility** (already familiar): `WhenUnlocked`, `AfterFirstUnlock`, `WhenPasscodeSet`, plus `ThisDeviceOnly` variants. Determines WHEN the item can be decrypted at all (lock state).
- **Authentication policy** (new): `kSecAccessControlUserPresence` requires user-presence authentication (Touch ID OR passcode fallback) before the item can be read.
- Combined: an item with `WhenUnlocked` + `UserPresence` requires (a) device unlocked AND (b) Touch ID/passcode authentication before each read.
- HIDDEN GEM: the `WhenPasscodeSet` accessibility class is brand new in iOS 8. Items in this class **are wiped from the device if the user removes their passcode** — cryptographically destroyed in the Secure Enclave. Perfect for highly sensitive secrets that should never exist on a device without a passcode (711).
- `WhenPasscodeSet` items also do **not** sync via iCloud Keychain and do **not** go into encrypted backups. Device-only by design (711).

## The User-Presence Policy in Practice (session 711)

Three scenarios, three behaviors:

1. **Device with no passcode**: `kSecAccessControlUserPresence` items are inaccessible. Reads always fail. Adding such items also fails — the policy can't be satisfied.
2. **Device with passcode but no Touch ID enrolled** (e.g., iPad without Touch ID): the user is prompted for the device passcode each time the keychain item is accessed. Secure but inconvenient (711).
3. **Device with passcode AND Touch ID enrolled**: the system shows the standard Touch ID sheet. The user touches; if the match succeeds, the item is decrypted and returned. If they cancel or the matcher disables itself after multiple failures, **passcode entry is the fallback** (711).

## Sample Code Pattern (session 711)

```objc
// Adding a keychain item with biometric ACL:
CFErrorRef error = NULL;
SecAccessControlRef acl = SecAccessControlCreateWithFlags(
    kCFAllocatorDefault,
    kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly,
    kSecAccessControlUserPresence,
    &error);

NSDictionary *attrs = @{
    (__bridge id)kSecClass: (__bridge id)kSecClassGenericPassword,
    (__bridge id)kSecAttrService: @"MyApp",
    (__bridge id)kSecValueData: [@"my secret" dataUsingEncoding:NSUTF8StringEncoding],
    (__bridge id)kSecAttrAccessControl: (__bridge id)acl
};
SecItemAdd((__bridge CFDictionaryRef)attrs, NULL);

// Reading: the system shows Touch ID UI automatically
NSDictionary *query = @{
    (__bridge id)kSecClass: (__bridge id)kSecClassGenericPassword,
    (__bridge id)kSecAttrService: @"MyApp",
    (__bridge id)kSecReturnData: @YES,
    (__bridge id)kSecUseOperationPrompt: @"Authenticate to access your secret"
};
CFTypeRef result = NULL;
OSStatus status = SecItemCopyMatching((__bridge CFDictionaryRef)query, &result);
```

- HIDDEN GEM: `kSecUseOperationPrompt` puts your custom message in the Touch ID sheet ("Authenticate to access your secret"). Strongly recommended — otherwise the user sees only the app name + "Authenticate" (711).
- WARNING: **`SecItemCopyMatching` for ACL items is BLOCKING**. It blocks the calling thread until the user authenticates or cancels. **Always wrap in `dispatch_async` to a background queue** (711).

## The LocalAuthentication Framework (session 711)

- For app-level authentication that doesn't necessarily protect a keychain item: prompt for biometric, get yes/no.
- **`LAContext`** is the entry point.
- **`canEvaluatePolicy(_:error:)`** — non-blocking check. "Can I do biometric auth on this device right now?" Returns false if no fingerprints enrolled, no Touch ID hardware, or hardware locked.
- **`evaluatePolicy(_:localizedReason:reply:)`** — async biometric check. Shows the UI; calls back with success or error.

```swift
let context = LAContext()
var error: NSError?
if context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) {
    context.evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics,
                            localizedReason: "Authenticate to view your account") { success, error in
        if success {
            // unlock the app
        } else if (error as? LAError)?.code == .userFallback {
            // user tapped "Enter Password" — show YOUR fallback UI
        }
    }
}
```

- HIDDEN GEM: in iOS 8, `LocalAuthentication`'s policy `.deviceOwnerAuthenticationWithBiometrics` does NOT fall back to passcode. If Touch ID fails or is unavailable, the user sees an "Enter Password" button that dismisses the prompt — and YOUR app must show YOUR fallback UI (711). (The `.deviceOwnerAuthentication` policy that includes passcode fallback ships in iOS 9.)
- HIDDEN GEM: `localizedReason` is **mandatory** — pass nil or empty and the call fails. Apple wants the user to know WHY they're being prompted (711).

## Best Practices

- **Use Keychain ACLs over LocalAuthentication when the secret is in the keychain.** ACLs give you Secure Enclave-level trust; LocalAuthentication only gives you OS-level trust (711).
- **Always wrap `SecItemCopyMatching` for ACL items in `dispatch_async`** — the call blocks for user interaction (711).
- **Provide your own password fallback UI** — `LocalAuthentication`'s biometric-only policy in iOS 8 doesn't fall back to passcode automatically; your app must (711).
- **Use `WhenPasscodeSet` for highly sensitive secrets** — they're wiped if the user removes their passcode, but they don't sync. Tradeoff worth making for medical/financial secrets (711).
- **Default to broader queries failing if any item requires authentication** — e.g., `SecItemCopyMatching` with a broad predicate may match an ACL-protected item and trigger the Touch ID prompt unexpectedly. Use `kSecUseAuthenticationUI = kSecUseAuthenticationUISkip` to suppress UI and just check whether auth would be required (711).
- **Don't try to detect "is a passcode set?"** — Apple's intentional design is that you cannot. Use `WhenPasscodeSet` accessibility class and check the error returned from `SecItemAdd` (711).

## Hidden Gems

- HIDDEN GEM: the Secure Enclave **counts failed Touch ID attempts**. After 5 failed matches, Touch ID is **disabled for the device** until the next successful passcode entry. Your app gets the disabled state via the LAError code (711).
- HIDDEN GEM: `SecItemCopyMatching` returns `errSecItemNotFound` when an authentication-protected item exists but the user denied auth — same error as if the item didn't exist. **Privacy by design**: a "this app was denied access" error would leak the existence of the item to other apps (711).
- HIDDEN GEM: keychain access groups for App Groups (configured in your entitlements) work transparently with Touch ID ACLs — your share extension can read a Touch ID-protected secret if the user authenticates inside the extension's UI (711).
- WARNING: `LAContext` can be reused, but each `evaluatePolicy` call shows a new prompt. To reuse a single authentication across multiple keychain reads in the same flow, pass the LAContext via `kSecUseAuthenticationContext` to `SecItemCopyMatching` — same auth, multiple operations.

## User Privacy Best Practices (session 715)

- **Just-in-time prompts** — request permission AT the moment the user tries to do the thing that needs it, not at app launch (715).
- **Purpose strings are mandatory** for all data-isolated APIs in iOS 8: `NSLocationWhenInUseUsageDescription`, `NSLocationAlwaysUsageDescription`, `NSCameraUsageDescription`, `NSMicrophoneUsageDescription`, `NSPhotoLibraryUsageDescription`, `NSContactsUsageDescription`, `NSCalendarsUsageDescription`, `NSRemindersUsageDescription`, `NSMotionUsageDescription`, `NSHealthShareUsageDescription`, `NSHealthUpdateUsageDescription`. Without them, calling the API fails (715).
- **Privacy Policy URL is mandatory** for apps that link HealthKit, HomeKit, third-party keyboards, or appear in the Kids section of the App Store (715).
- HIDDEN GEM: in iOS 8, you can deep-link the user to your app's privacy settings: `UIApplication.shared.open(URL(string: UIApplication.openSettingsURLString)!)`. Useful in your "Permission denied — please enable in Settings" UI (715).
- **Family Sharing impact**: more children on the platform means more apps will encounter restricted users. Test with restrictions enabled (715).
- HIDDEN GEM: in iOS 8, `ABPeoplePickerNavigationController` can be presented WITHOUT requesting Contacts access. The user picks a contact; you receive only that contact, with no read/write access to the rest of the address book (715).

## Cross-references

- **CloudKit (208)** — CloudKit identity uses the same iCloud account; user discovery is privacy-preserving by design.
- **HealthKit (203)** + **HomeKit (213)** — both REQUIRE a Privacy Policy URL in iTunes Connect (715).
- **Continuity / Shared Web Credentials (506)** — Touch ID can gate the credential-picker UI for shared web credentials.
- **App Extensions (217)** — extensions can share keychain items via App Groups; ACLs propagate consistently.

## Migration Guidance

- **Apps storing passwords in `NSUserDefaults`**: STOP. Move to keychain immediately. Add ACL with user-presence for high-value credentials (banking, password managers).
- **Apps with their own PIN/password gates**: consider switching to `LocalAuthentication.evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, ...)`. Keep your existing PIN UI as the fallback (the framework doesn't fall back automatically in iOS 8).
- **Health/finance apps**: adopt `kSecAttrAccessibleWhenPasscodeSetThisDeviceOnly` for the most sensitive secrets. The "wiped if passcode removed" guarantee is a major safeguard.
- **Audit your Info.plist** in iOS 8 — every privacy-sensitive API needs its purpose string. Apps that linked privacy frameworks pre-iOS-8 will silently fail until the strings are added.
