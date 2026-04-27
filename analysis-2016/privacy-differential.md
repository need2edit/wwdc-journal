# Privacy & Differential Privacy — WWDC 2016 Analysis

**Sessions covered:** 709 (Engineering Privacy for Your Users), 706 (What's New in Security)

## Headline

WWDC 2016 introduces **Differential Privacy** — Apple's mathematically-rigorous approach to learning from large user populations *without* collecting individually-identifiable data. iOS 10 uses it for emoji frequency, new word discovery, deep-link popularity, and lookup hints. Combined with privacy-friendly identifier APIs, expanded `Info.plist` permission requirements, and tighter widget data discipline, this is Apple's most aggressive privacy push in years.

## Differential privacy — the technique in plain terms

You want to learn the most popular emoji across millions of users. The naive approach: collect every user's emoji usage history. The privacy-preserving approach:

1. **On device**, hash the emoji into a fixed-length bit vector.
2. **Add noise** by randomly flipping some 1-bits to 0 and some 0-bits to 1, with a tunable probability that ones are slightly more likely to stay 1 and zeros to stay 0.
3. **Send only the noised vector** (no identifiers) to Apple servers.
4. The aggregator cannot recover any individual's contribution. But across millions of vectors, statistically-significant patterns (popular emoji) emerge from the noise.

A privacy budget restricts the number of contributions any one device can make in a time window — preventing the "single donor becomes their own aggregate" attack. No identifiers are stored. Raw measurements are deleted permanently after aggregation.

Only users opted into "Diagnostics & Usage" data sharing contribute. Always honor this opt-in.

## Apple's four iOS 10 use cases for differential privacy

1. **Emoji frequency** — reorder the keyboard to surface popular emoji.
2. **New words** — discover slang and proper nouns not in the dictionary, surface them as candidate completions.
3. **Deep links** — measure which links inside which apps users open. Used in Spotlight ranking (see Search APIs).
4. **Lookup hints** — Safari URL suggestions.

For app developers, the takeaway is the **mental model**: collect aggregate signal, not individual measurements. If you really need a metric, ask whether bucketing, sampling, or aggregation can give you the same answer with less risk.

## Privacy-friendly identifier APIs

| API | Lifetime | Use case |
|-----|----------|----------|
| `UUID()` | Per call | Generate a fresh random ID — sessions, transactions |
| `UIDevice.identifierForVendor` | Stable across your apps from the same vendor; reset on uninstall | Cross-app personalization within your own portfolio |
| `ASIdentifierManager.advertisingIdentifier` | User-resettable, can be zeroed by Limit Ad Tracking | Advertising attribution (and ONLY advertising) |
| `MKMapItem` ephemeral session ID, Spotlight rotating ID | Per session, system-managed | System rotation built in |

**URGENT (iOS 10):** When the user enables **Limit Ad Tracking**, `advertisingIdentifier` returns **all zeros** (`00000000-0000-0000-0000-000000000000`). Previously this was a signal you could ignore; in iOS 10 it's enforced in code. **Don't cache the ad identifier yourself** — it must be re-fetched (so resets propagate) and you must check for the zero-UUID every time.

If the user enables Limit Ad Tracking, you can still show **contextual ads** (based on the article they're reading, the search they're doing) — you just can't track them across apps via the IDFA.

## Mandatory `Info.plist` purpose strings — apps crash without them

iOS 8 began requiring purpose strings for Location. iOS 10 **extends this to every protected data class.** If your app accesses any of these, you must declare a purpose string in `Info.plist`. Otherwise, the app **terminates** with a console error pointing to the missing key.

Required keys (incomplete list — full list in Xcode):
- `NSCameraUsageDescription`
- `NSMicrophoneUsageDescription`
- `NSPhotoLibraryUsageDescription`
- `NSLocationAlwaysUsageDescription` / `NSLocationWhenInUseUsageDescription`
- `NSContactsUsageDescription`
- `NSCalendarsUsageDescription`
- `NSRemindersUsageDescription`
- `NSHealthShareUsageDescription`, `NSHealthUpdateUsageDescription`
- `NSHomeKitUsageDescription`
- `NSMotionUsageDescription`
- `NSBluetoothPeripheralUsageDescription`
- `NSAppleMusicUsageDescription` (NEW — Media Library reading)
- `NSSiriUsageDescription` (NEW — SiriKit registration)
- `NSSpeechRecognitionUsageDescription` (NEW — Speech framework)
- `NSVideoSubscriberAccountUsageDescription` (NEW — TV provider single sign-on)

**HIDDEN GEM:** Write CONCRETE, USEFUL strings ("Used to scan barcodes when you take a photo of a book") rather than legalese. Conversion-rate-on-permissions correlates strongly with how clearly the user understands what your app is doing.

You're also responsible for the third-party libraries you bundle. If a library accesses contacts and you didn't declare it, your app crashes.

## Pasteboard improvements (HIDDEN GEM)

`UIPasteboard` gained two key knobs:

```swift
UIPasteboard.general.setItems([
    [UIPasteboardTypeListString.first as String: "Hello"]
], options: [
    .expirationDate: Date(timeIntervalSinceNow: 120),  // auto-clear in 2min
    .localOnly: true                                    // exclude from Universal Clipboard
])
```

Use `.expirationDate` for sensitive data the user copies (passwords, OTPs, security codes). The clipboard self-cleans, even if the user forgets.

Use `.localOnly` for data you don't want syncing to other devices via Universal Clipboard.

**DEPRECATION:** Persistent named pasteboards trigger deprecation warnings. Find pasteboard items return empty. **Use App Groups** (shared containers) for cross-app data inside your team — pasteboards are user-facing only.

## Core Spotlight — privacy responsibilities

- Don't `eligibleForPublicIndexing = true` on items containing private user data.
- Don't index every tap as an `NSUserActivity` — the system gets flooded and the user can't find what they're actually looking for. Index things they'd want to come back to.

## Widget data discipline (NEW — widgets on lock screen)

iOS 10 widgets are visible on the lock screen by default. Apple's guidance:

- **Evaluate sensitivity of data you put in your widget.** If it's not appropriate for the lock screen (location of friends, account balances, medication schedules), use file protection class `.complete` so the data simply isn't available pre-unlock — show a "Unlock to view" placeholder instead.
- **Make the data consistent and predictable.** A user looking at your widget today should see something similar tomorrow — they should know what type of content lives there.
- **The Find My Friends widget** is the canonical example: pre-unlock it shows "Unlock to view location"; post-unlock it shows the actual locations. Mirror this pattern.

## App Sandbox enhancements (security session)

Apple deduplicated and gated some APIs that were being used for fingerprinting. Some `UIDevice` properties became sandbox-restricted; others were whitelisted as legitimate.

In iOS 8, Apple already started using **locally administered MAC addresses that rotate** during Wi-Fi scans — preventing third parties from passively tracking your device's MAC across networks. macOS Sierra extends this. If you're a Wi-Fi equipment vendor, test against rotating MACs.

## Network security (session 706 cont.)

- **App Transport Security** is enforced at App Store submission starting late 2016. Justification required for exceptions. New exception keys for arbitrary web content (`NSAllowsArbitraryLoadsInWebContent`) and streaming media.
- **TLS 1.2 with forward secrecy + SHA-2 + AES-128** is the new minimum.
- **RC4 disabled**, **SSLv3 disabled**, **3DES & SHA-1 deprecated** at the system level.
- **Certificate Transparency** — opt in via `NSRequiresCertificateTransparency` per domain. Validates that your server cert was logged in public CT logs.
- **OCSP stapling** is now fully supported across Apple platforms — flip it on at your server (Apache, Nginx) for cheap revocation checking without leaking client browsing patterns to the CA.

## Best practices summary

- Use the shortest-lived identifier that solves your problem. UUID for sessions; rotating system IDs for transient personalization.
- Declare all Info.plist purpose strings up front; revisit copy regularly.
- For pasteboard data, set expirationDate and localOnly when handling secrets.
- Audit widgets for lock-screen data exposure.
- Audit info you collect — could you bucket, sample, or aggregate instead of keeping raw events?
- Always honor Limit Ad Tracking — fetch the IDFA fresh each time, check for zeros.

## Hidden gems summary

- Differential privacy is opt-in (Diagnostics & Usage), uses no identifiers, deletes raw measurements.
- Pasteboard expiration date auto-clears sensitive copies.
- `UIPasteboard.localOnly` keeps copies off the Universal Clipboard.
- Limit Ad Tracking is enforced in the OS — IDFA returns all zeros, no longer a hint.
- Widget file-protection class `.complete` makes lock-screen widgets show placeholders for sensitive data.
- Certificate Transparency opt-in protects against rogue-CA attacks.

## Cross-references

- App Transport Security details → analysis-2016/security-network.md (session 706)
- Speech recognition's privacy posture → analysis-2016/speech-recognition.md
- SiriKit's authorization → analysis-2016/sirikit-debut.md
