# Apple Platform Modernization Guide

**A comprehensive playbook for bringing a dated Apple-platform project up to current best practices.**

Synthesized from 12 years of WWDC analysis (2014–2025). Use this as a checklist when inheriting an old codebase, modernizing a long-lived app, or auditing technical debt before a major release.

---

## How to Use This Guide

1. **Find your starting point.** When was the project last meaningfully modernized? Jump to the corresponding row in §15 (Chronological Reference Table) to see everything that has shipped since.
2. **Triage by urgency.** §1 lists items that will *break your app* if ignored. §2 lists changes that have already shipped that you've likely missed. Everything after that is opt-in modernization.
3. **Plan your phases.** §16 (The Modernization Recipe) describes a five-phase migration that minimizes risk and maximizes early wins.
4. **Use the checklist** in §17 as a printable audit form.

A blanket rule: **don't try to do everything at once.** Apple's APIs evolve in waves, and each wave has rough edges in its first year. Adopt one paradigm per release cycle.

---

## §1. Critical Issues — Fix or App Breaks

These items either prevent build, prevent App Store submission, prevent launch on current OS versions, or cause silent crashes. Order is roughly by deadline urgency.

### 1.1 UIScene lifecycle is mandatory (post-iOS 26)
- **Symptom:** App will not launch in the release following iOS 26.
- **Fix:** Adopt `UIScene` / `UIWindowSceneDelegate`. Move `UIApplicationDelegate` lifecycle methods (`applicationDidBecomeActive`, `applicationDidEnterBackground`, etc.) to the corresponding `UISceneDelegate` methods. Add `UIApplicationSceneManifest` to `Info.plist`.
- **Source:** WWDC25-243, TN3187.
- **Note:** Apple's official docs still describe scene support as "opt-in" — the WWDC25 transcripts are the only authoritative source on the upcoming mandatory deadline. This is the single most-missed urgent item across the entire 12-year corpus.

### 1.2 Privacy manifests required for SDKs
- **Symptom:** App Store rejection at submission. Required for any SDK using "Required Reason APIs" (file timestamps, system boot time, disk space, active keyboards, user defaults).
- **Fix:** Add `PrivacyInfo.xcprivacy` to every SDK and to your app, declaring tracking, tracking domains, collected data types, and reasons for using designated APIs.
- **Source:** WWDC23 / enforcement deadline May 2024.

### 1.3 App Tracking Transparency (ATT) prompt mandatory before tracking
- **Symptom:** App rejection if you access IDFA without prompting; opt-in rates ~15–25% of users.
- **Fix:** Call `ATTrackingManager.requestTrackingAuthorization` before reading IDFA or sending data to a tracking domain. Add `NSUserTrackingUsageDescription` to `Info.plist`.
- **Source:** WWDC20 / enforced in iOS 14.5 (April 2021).

### 1.4 Modal sheet behavior changed (iOS 13)
- **Symptom:** Auth flows, onboarding, and forms that assumed full-screen modals now appear as cards that users can swipe-dismiss — leading to broken state, lost input, "I tapped Sign Up but nothing happened" reports.
- **Fix:** Set `viewController.modalPresentationStyle = .fullScreen` explicitly where you need the old behavior, OR adopt the new dismissal model with `isModalInPresentation = true` to prevent accidental dismissal.
- **Source:** WWDC19 — "Modernizing Your UI for iOS 13".

### 1.5 macOS notarization & hardened runtime required
- **Symptom:** macOS Catalina+ refuses to launch unnotarized Developer ID apps. Hardened runtime entitlements required.
- **Fix:** Enable Hardened Runtime, declare entitlements (camera, microphone, JIT, allow-unsigned-executable-memory only if truly needed), notarize via `notarytool` or Xcode Organizer, staple the ticket.
- **Source:** WWDC19 — "All About Notarization".

### 1.6 32-bit code removed from macOS / iOS
- **Symptom:** Won't run on macOS Catalina+ or iOS 11+.
- **Fix:** Build for 64-bit only. Remove any 32-bit dependencies. For Apple Silicon, also build arm64 (Universal binary).
- **Source:** WWDC17 (iOS), WWDC18 (macOS warnings), WWDC19 (Catalina removal).

### 1.7 App Transport Security (HTTPS) mandatory
- **Symptom:** All HTTP requests fail unless you've added an exception.
- **Fix:** Migrate all endpoints to HTTPS with TLS 1.2+. Remove `NSAllowsArbitraryLoads` from `Info.plist` (and don't add it back). Use `NSExceptionDomains` only for legacy third-party APIs you don't control.
- **Source:** WWDC16, mandatory January 2017.

### 1.8 UIWebView removed
- **Symptom:** App Store rejection if any binary references `UIWebView`.
- **Fix:** Replace with `WKWebView` (or in 2025+, `WebView` from WebKit for SwiftUI). Audit every dependency — many SDKs still pulled it in 2019–2020.
- **Source:** WWDC14 (intro of WKWebView), Apple ban December 2020.

### 1.9 Mac Catalyst / unified Apple Silicon binaries
- **Symptom:** Slow launch, Rosetta 2 fallback, no native Apple Silicon performance.
- **Fix:** Build Universal binaries (arm64 + x86_64). Audit dependencies for arm64 compatibility. `mach_absolute_time` does NOT return nanoseconds on Apple Silicon — use `clock_gettime_nsec_np` or `ContinuousClock`.
- **Source:** WWDC20 (Apple Silicon transition).
- **Hidden gem:** WWDC20-10214 — `mach_absolute_time` ratio change is the single most common Apple Silicon porting bug, producing 40× slowdowns.

### 1.10 Bitcode removed
- **Symptom:** Xcode 14+ refuses to upload Bitcode-enabled apps.
- **Fix:** Remove Bitcode from build settings. Apple no longer requires it for any platform.
- **Source:** WWDC22, Bitcode officially removed in Xcode 14.

### 1.11 On-Demand Resources deprecated
- **Symptom:** Continues to work, but Apple stopped investing — you're locked into the old slow CDN with no path to 200GB hosting tier.
- **Fix:** Migrate to **Background Assets** (Apple-hosted, 200GB per app, integrates with App Store Connect).
- **Source:** WWDC25-325.

### 1.12 SceneKit officially soft-deprecated
- **Symptom:** Continues to work but no new investment. RealityKit is the path forward.
- **Fix:** Migrate via `xcrun scntool` to convert assets, then port nodes → entities, animations, particles.
- **Source:** WWDC25-288.

### 1.13 Combine quietly being eclipsed by Swift Concurrency
- **Symptom:** No deprecation, but Apple has clearly stopped investing. New Apple frameworks return `AsyncSequence`, not `Publisher`.
- **Fix:** For new code, prefer Swift Concurrency. Migrate hot Combine pipelines if they're causing maintenance pain. The `Observation` framework (2023) replaces `ObservableObject`/`@Published` for view models.
- **Source:** WWDC23 (Observation), WWDC21 (async/await debut).

---

## §2. Things That Already Shipped That You Probably Missed

These won't break your app, but adopting them yields significant wins. Listed in approximate order of bang-for-buck.

| Item | Year | Why it matters |
|---|---|---|
| **Codable** | 2017 | Replace 50+ lines of NSCoding/JSONSerialization boilerplate with auto-synthesized protocol conformance |
| **NSURLSession async/await** | 2021 | Replace completion-handler URL loading with `try await URLSession.shared.data(for:)` |
| **Result type built-in** | 2019 | Stop hand-rolling `Result<T, E>` |
| **Property wrappers** | 2019 | Underpin SwiftUI, replace boilerplate observers |
| **SF Symbols** | 2019 | Free, animated, weight-aware icons across all platforms — drop Glyphish & custom asset packs |
| **NSLayoutAnchor** | 2015 | If you're still writing `addConstraint(NSLayoutConstraint(item:..., toItem:..., multiplier:..., constant:))`, stop |
| **PHPickerViewController** | 2020 | Replace `UIImagePickerController` with the privacy-respecting picker that doesn't need Photos permission at all |
| **WKWebView** | 2014 | Out-of-process, faster, Nitro JS, no main-thread blocking |
| **Document Browser / Files** | 2017 | Modern document-based apps integrate with the Files app and iCloud Drive |
| **Sign In with Apple** | 2019 | Required if you offer third-party social sign-in (Google/Facebook), and a great primary auth option |
| **Swift Package Manager in Xcode** | 2019 | Dramatically simpler than CocoaPods for most use cases |
| **Background tasks (BGTaskScheduler)** | 2019 | Replaces deprecated background fetch / silent push patterns |
| **os_log → Logger** | 2016/2020 | Replace `print()` and `NSLog` — privacy-aware, structured, viewable in Console.app |
| **Combine → Observation framework** | 2023 | If you used `@ObservedObject`/`@Published` only for view-model observation, switch to `@Observable` macro for less boilerplate and better SwiftUI performance |
| **NavigationStack / NavigationSplitView** | 2022 | `NavigationView` is deprecated; `NavigationStack` enables programmatic navigation that actually works |
| **App Intents** | 2022 | Replaces NSUserActivity-based Siri Shortcuts donations + custom intents — required for Spotlight, Visual Intelligence, Apple Intelligence integration |
| **Swift Charts** | 2022 | If you have any custom charting code, delete most of it |
| **SwiftData** | 2023 | If you're starting new persistence work, skip Core Data |
| **Swift Macros** | 2023 | Replace boilerplate generators (Sourcery, GYB) |
| **Swift Testing** | 2024 | Modern replacement for XCTest with `@Test`, `#expect`, parameterized tests, tags |
| **Mergeable libraries** | 2023 | 1.5x–3x launch time improvement for apps with many frameworks (single build setting) |
| **Quantum-secure TLS (default)** | 2025 | Free post-quantum protection for URLSession/Network — no app changes needed |
| **Foundation Models** | 2025 | On-device LLM, zero cost, no API keys, offline. Use `@Generable` for typed output |

---

## §3. Language Modernization (Swift)

Swift has had multiple breaking versions. Each migration unlocks significant ergonomics.

### 3.1 Swift Version Upgrade Path

| From | To | Effort | Watch out for |
|---|---|---|---|
| **Swift 1 → 2** | Low | Error handling (do/try/catch), guard, defer |
| **Swift 2 → 3** | **HIGH** | API guidelines change — every Foundation/UIKit method renamed (snake_case → camelCase, prepositions reorganized, NS prefix dropped). Use Xcode's "Convert to Current Swift Syntax" assistant. |
| **Swift 3 → 4** | Medium | Codable adoption, String as Collection, `@objc` inference rules tightened (you may need to add explicit `@objc` annotations) |
| **Swift 4 → 5** | Low | Result type built in, ABI stability, raw strings |
| **Swift 5 → 5.5** | Medium | Concurrency: async/await, actors, `Sendable`. Mostly opt-in, but interop requires careful annotation |
| **Swift 5.5 → 6** | **HIGH** | Strict concurrency. Every `class` accessed across actors must conform to `Sendable`. Many third-party libs aren't ready. Enable in stages with `-strict-concurrency=minimal/targeted/complete` |
| **Swift 6 → 6.2** | Medium | "Approachable Concurrency" — main-actor-by-default for app targets (libraries should stay nonisolated). Async functions no longer eagerly offload. New `@concurrent` attribute opts into background execution |

### 3.2 Adopt These Patterns

- **`Codable`** instead of `NSCoding`, manual `init?(coder:)`, or `JSONSerialization` (Swift 4 / 2017)
- **`Result<Success, Failure>`** for callback APIs that pre-date async/await (Swift 5 / 2019)
- **Property wrappers** for cross-cutting concerns: `@Published`, `@AppStorage`, `@SceneStorage`, `@ScaledMetric`, custom validators (Swift 5.1 / 2019)
- **Result builders** for DSLs: SwiftUI's `@ViewBuilder`, regex builders, navigation paths (Swift 5.1 / 2019)
- **Macros** to replace code generation tools (Swift 5.9 / 2023)
- **Parameter packs** for variadic generics (Swift 5.9 / 2023) — replaces ugly `(A,B,C,...)` overloads
- **`@Observable`** macro instead of `ObservableObject` + `@Published` (Swift 5.9 / 2023)
- **Typed throws** — `throws(MyError)` for compile-time error type checking (Swift 6 / 2024)

### 3.3 Stop Using

- `println` (Swift 2 renamed to `print`)
- `dispatch_*` C-style GCD APIs (use `DispatchQueue.main.async {}` or, better, `await MainActor.run`)
- `dispatch_semaphore_wait` (causes priority inversion — use `dispatch_block_wait` or async/await — WWDC15-718)
- `NSError**` patterns (use `throws`)
- `var = NSNotFound` sentinels (use Optional)
- Manual `init?(coder:)` and `encode(with:)` (use `Codable`)
- `Data.dropFirst()` — it's O(n), not O(1). Use `Slice` or new `Span` types (WWDC25-312)

---

## §4. UI Framework Modernization

### 4.1 SwiftUI Adoption Strategy

If your app is pure UIKit, you don't have to rewrite — SwiftUI interoperates cleanly. Adoption ladder:

1. **Start with leaf screens.** Replace simple settings/about/onboarding screens with SwiftUI views in `UIHostingController`.
2. **Replace forms and lists.** SwiftUI Lists got 6× faster, ForEach 16× faster in 2025 — they often beat hand-tuned UITableView.
3. **Replace empty states and small subviews.** Use `UIHostingConfiguration` to put SwiftUI inside UITableViewCell/UICollectionViewCell.
4. **Replace navigation.** `NavigationStack` (2022) supports programmatic navigation properly.
5. **Replace whole flows.** Once your data layer is `@Observable` (or actor-based), this becomes trivial.

### 4.2 UIKit Modernization (if you stay on UIKit)

| Old pattern | Modern replacement | Year |
|---|---|---|
| `UIWebView` | `WKWebView` | 2014 |
| `UIAlertView` / `UIActionSheet` | `UIAlertController` | 2014 |
| `UISearchDisplayController` | `UISearchController` | 2014 |
| `UIImagePickerController` (full Photos access) | `PHPickerViewController` | 2020 |
| `UILocalNotification` | `UNUserNotificationCenter` | 2016 |
| `dataSource` / `delegate` for collections | `UICollectionViewDiffableDataSource` + `NSDiffableDataSourceSnapshot` | 2019 |
| Manual `NSLayoutConstraint` | `NSLayoutAnchor` | 2015 |
| Custom `UIView` containers | `UIStackView` | 2015 |
| `UIDocument` boilerplate | Document Browser API | 2017 |
| Manual cell self-sizing | `UITableView.automaticDimension` + `estimatedRowHeight` | 2014 |
| `setNeedsLayout()` / observer plumbing | `updateProperties()` + automatic observation tracking (UIKit 26) | 2025 |
| Manual scene management | UIScene + UIWindowSceneDelegate | 2019 (recommended) → 2026 (mandatory) |

### 4.3 Liquid Glass adoption (2025) — URGENT

Apps without Liquid Glass adoption will look conspicuously dated within 12 months of iOS 26 shipping.

- Add `.glassEffect()` modifier to interactive controls
- Use `GlassEffectContainer` to manage groups of glass elements
- Migrate custom toolbar appearances — many will conflict with glass
- Two variants: **Regular** (interactive) and **Clear** (decorative)
- Respect "concentricity": glass elements should be nested, not overlapping

### 4.4 Adopt These Universal UI Improvements

- **SF Symbols 7** (2025) — variable draw, gradients, Magic Replace. Replace any custom icon assets.
- **Dynamic Type** — every text view should support it. `UIFontMetrics` / SwiftUI auto-handles this.
- **Dark Mode** — adopt semantic colors (`.systemBackground`, `Color(.label)`, etc.). No more hardcoded `UIColor.white`.
- **Safe area insets** — handle the notch and Dynamic Island. Stop using `topLayoutGuide` / `bottomLayoutGuide`.
- **Size classes** (since 2014) — design for trait collections, not device families.
- **Layout protocol** (2022) — custom SwiftUI layout containers, replaces older `LayoutValueKey` hacks.
- **`@Animatable` macro** (2025) — replaces `AnimatableModifier` and manual `animatableData`.

### 4.5 Accessibility Audit

- VoiceOver labels on every interactive element
- `Button` instead of `onTapGesture` where semantically appropriate
- Dynamic Type support on every text view
- High Contrast colors
- Reduce Motion respect
- Reduce Transparency respect
- Voice Control labels
- **Accessibility Nutrition Labels** (2025) — declare your supported accessibility features in App Store Connect
- **Assistive Access scene type** (2025) — opt in if you have a simplified UI mode

---

## §5. Concurrency Overhaul (the Biggest Paradigm Shift)

This is the single most impactful modernization. Done well, it eliminates entire classes of bugs (data races, callback hell, leaked references). Done poorly, it introduces new ones.

### 5.1 The Concurrency Eras

| Era | Pattern | Year | Notes |
|---|---|---|---|
| GCD (Grand Central Dispatch) | `dispatch_async` / `dispatch_sync` | 2009 | Still works; use sparingly |
| NSOperation / OperationQueue | Cancellable, dependent operations | 2010 | Mostly superseded |
| Combine | `Publisher`, `Subscriber`, operators | 2019 | Quietly being eclipsed |
| Swift Concurrency | `async`/`await`, actors, structured concurrency | 2021 | **The path forward** |

### 5.2 Migration Recipe (GCD → Swift Concurrency)

```swift
// Old
func fetch(_ id: String, completion: @escaping (Result<User, Error>) -> Void) {
    URLSession.shared.dataTask(with: url(id)) { data, _, error in
        // ...
        DispatchQueue.main.async { completion(.success(user)) }
    }.resume()
}

// New
func fetch(_ id: String) async throws -> User {
    let (data, _) = try await URLSession.shared.data(from: url(id))
    return try JSONDecoder().decode(User.self, from: data)
}
```

Steps:
1. **Annotate UI types as `@MainActor`** (or enable main-actor-by-default in Swift 6.2 build settings).
2. **Replace completion handlers with `async throws`.** Many Apple APIs already have async overloads.
3. **Use `withCheckedThrowingContinuation`** to bridge legacy callback APIs.
4. **Replace `DispatchQueue.main.async {}` with `await MainActor.run { ... }`** or just call from a `@MainActor` context.
5. **Use `TaskGroup`** for parallel work that was previously a `dispatch_group`.
6. **Use `AsyncSequence`** for Combine pipelines (especially `URLSession.bytes`, `NotificationCenter.notifications`).

### 5.3 Key Insights from the Transcripts

- **Profile BEFORE adding concurrency.** Many perceived concurrency needs are algorithmic inefficiencies that should be fixed first (WWDC25-268, WWDC25-312).
- **Swift Concurrency's cooperative pool spawns only as many threads as CPU cores.** Thread explosion is impossible by construction. Compare to GCD which can spawn 64+ on contention (WWDC21-10254).
- **Actor hopping is NOT a thread switch when uncontended** — but `MainActor` hops *are* real switches, so batch them.
- **In Swift 6.2, async functions no longer eagerly offload.** A `nonisolated async` function called from `@MainActor` stays on the main actor unless you mark it `@concurrent`.
- **For libraries, prefer `nonisolated` over `@concurrent`** — let the caller decide.
- **SwiftUI's `visualEffect` modifier runs on background threads** — never access `@MainActor` state inside (WWDC25-266).

### 5.4 Sendable & Strict Concurrency

Swift 6 enforces `Sendable` on every value crossing actor boundaries. Strategies:

- **Make value types `Sendable` automatically** by using only `Sendable` properties (Bool, Int, String, Date, etc.).
- **Mark reference types `@unchecked Sendable`** only if you've manually proven thread safety.
- **Use actors** for mutable state shared across tasks.
- **Adopt `nonisolated(unsafe)` sparingly** for legitimate cases (like `static let` immutable globals).

---

## §6. Persistence Modernization

### 6.1 The Data Stack Evolution

| Era | Stack | Year | Status |
|---|---|---|---|
| Direct SQLite + FMDB | Manual schema | < 2010 | Legacy |
| Core Data | Object graph + SQLite store | 2009 | Mature, still supported |
| Realm | Third-party, popular | 2014–2020 | Less momentum now |
| **Codable** for simple persistence | JSON to file/UserDefaults | 2017 | Simple use cases |
| **SwiftData** | Modern Swift-first persistence | 2023 | **Recommended for new code** |

### 6.2 Migrate These

- **`NSCoding` + `NSKeyedArchiver`** → `Codable` + `JSONEncoder`/`PropertyListEncoder` (2017)
- **`ALAssetsLibrary`** → `PhotoKit` (2014, removed 2020)
- **`AddressBook` framework** → `Contacts` framework (2015, AB framework deprecated)
- **`SLSpeechRecognizer`** → `Speech` framework (2016)
- **`NSLinguisticTagger`** → `NaturalLanguage` framework (2018)
- **`NSUserDefaults` for structured data** → SwiftData / file-backed Codable
- **`FileWrapper` + `UIDocument`** → `DocumentGroup` in SwiftUI (2019+)

### 6.3 SwiftData Key Patterns

- **Class inheritance is supported** (2025) — Trip, BusinessTrip, PersonalTrip pattern
- **Deep vs shallow queries** matter: avoid fetching all subclasses if you only need one
- **Schema migration plans** — declare them in code, version explicitly
- **Cloud sync** via CloudKit integration

### 6.4 KVO → Observation Framework

- Drop `addObserver(_:forKeyPath:options:context:)` and `observeValue(forKeyPath:...)` boilerplate.
- Drop `ObservableObject` + `@Published` for view-model use.
- Add `@Observable` macro to your model class.
- Use `withObservationTracking` for fine-grained reactive updates.
- Use the new `Observations` AsyncSequence for transactional updates (WWDC25).

---

## §7. Networking Modernization

### 7.1 The HTTP Stack

| Old | New | Year |
|---|---|---|
| `NSURLConnection` | `URLSession` | 2013 (deprecated 2015) |
| `URLSession` with delegates | `URLSession` async/await | 2021 |
| `CFNetwork` low-level | `Network` framework (`NWConnection`, `NWListener`) | 2018 |
| `Secure Transport` | `Network` framework's TLS | 2018 (Secure Transport deprecated) |
| Custom WebSocket libs | `URLSessionWebSocketTask` | 2019 |
| Polling | Server-Sent Events via `URLSession.bytes` | 2021 |
| Background fetch / silent push | `BGTaskScheduler` (`BGAppRefreshTask`, `BGProcessingTask`) | 2019 |
| Custom CDN for asset packs | `Background Assets` (Apple-hosted, 200GB) | 2025 |

### 7.2 Adopt These

- **`URLSession.shared.data(for:)`** instead of completion-handler `dataTask`
- **`URLSession.shared.bytes(for:)`** for streaming JSON-Lines or SSE
- **`URL.lines`** and **`URL.bytes`** as AsyncSequence accessors (WWDC21-10058 — works for remote endpoints AND local files with no setup)
- **L4S (Low Latency, Low Loss, Scalable Throughput)** opt-in via `Network` framework — drops latency from 100ms → 5ms on congested networks WITHOUT throughput loss (WWDC23-10004)
- **Wi-Fi Aware** (2025) for direct peer-to-peer with encrypted connections — no Wi-Fi network needed
- **HTTP/3 (QUIC)** — automatic with `URLSession`, no code changes needed

### 7.3 VPN / Network Extensions

- **Old VPN apps using IKEv2 only:** Now must use NetworkExtension framework. Older `NEVPNManager` patterns still work but new VPN protocols require the modern path.
- **Content blockers / network filters:** Use `NEFilterDataProvider` / `NEFilterControlProvider`.

---

## §8. Privacy & Security

### 8.1 Mandatory Adoption

- **App Tracking Transparency** prompt (2020) — see §1.3
- **Privacy manifests** (2024) — see §1.2
- **Sign In with Apple** (2019) — required if offering social sign-in
- **Hardened Runtime + notarization** on macOS (2019) — see §1.5
- **App Transport Security** (2017) — see §1.7
- **Required Reason API declarations** (2024) — for file timestamps, system boot time, disk space, active keyboards, user defaults

### 8.2 Adopt These for Better Security UX

- **Passkeys** (2022) — phishing-resistant, no passwords to leak, syncs via iCloud Keychain
  - Account creation API (2025), automatic passkey upgrades
  - Credential signal APIs for relying parties
- **Biometric ACLs in Keychain** — items unlock only when Face ID/Touch ID succeeds
- **Sign In with Apple** for primary auth (privacy-preserving relay email)
- **App Attest** to prove your app instance is genuine (anti-fraud, anti-cheat)
- **CryptoKit** modern crypto APIs (replace CommonCrypto where possible) — 2019
- **Quantum-secure HPKE, ML-KEM, ML-DSA** in CryptoKit (2025) — for forward secrecy against future quantum attacks
- **Differential Privacy** (2016) for any analytics you ship — Apple's privacy-preserving aggregation
- **PIR (Private Information Retrieval)** patterns for lookups without revealing what you're looking up (2025)

### 8.3 Privacy-by-Design Patterns

- **`PHPickerViewController`** instead of `UIImagePickerController` — no Photos permission needed at all
- **Limited Photos access** — handle the case where the user grants access to *some* photos
- **Location: request "When in Use" before "Always"** — never start with Always
- **Contacts/Calendars per-event access** instead of full library
- **HealthKit per-object authorization** (2025) — user picks which specific medications/data to share, not all-or-nothing
- **`NSUserActivity.eligibleForPublicIndexing`** is privacy-preserving by default — only hashes ship to Apple, content stays local until enough independent devices vote (WWDC15-709)

### 8.4 Network Privacy

- **Hide your IP from trackers** (Mail Privacy Protection, iCloud Private Relay)
- **Encrypted Client Hello (ECH)** in TLS — automatic via `URLSession`
- **Declared Age Range API** (2025) — privacy-preserving age signals for child-safe content

---

## §9. Performance & Observability

### 9.1 Profile-First Mindset

Apple's consistent message across 12 years: **measure before optimizing.** Specific tools to learn:

- **Instruments** — Time Profiler, Allocations, Hangs, Animation Hitches
- **MetricKit** (2018) — receive on-device metrics from real users (battery, hangs, scroll hitches)
- **`XCTHitchMetric`** (2023) — automated hitch detection in tests
- **SwiftUI Instrument** (2025) — cause-and-effect graphs of state changes → view body evaluations
- **Foundation Models Instrument** (2025) — token consumption, asset loading, inference time
- **Swift Concurrency Instrument** — visualize task scheduling, actor contention
- **Power Profiler** — battery impact attribution

### 9.2 Logging Modernization

```swift
// Old
NSLog("User %@ logged in", user.email)
print("Debug: \(user)")

// New (Logger, 2020)
import os
let log = Logger(subsystem: "com.example.app", category: "auth")
log.info("User \(user.email, privacy: .private) logged in")
log.debug("Full user: \(user, privacy: .private)")
```

Benefits: privacy-aware (sensitive data redacted in production logs), structured, viewable in Console.app, lower overhead than `NSLog`.

### 9.3 Performance Wins You Get for Free

- **Auto Layout went from O(n²) to O(n)** in iOS 12 — apps with deep view hierarchies get massive scrolling/launch wins from JUST relinking against iOS 12 (WWDC18-220).
- **Mergeable libraries** (2023) — 1.5x–3x launch time improvement, single build setting (WWDC23-10268).
- **SwiftUI List 6× / ForEach 16× faster** in 2025 — automatic, no code changes.
- **APFS clones** make `FileManager.copyItem(at:to:)` essentially free regardless of file size (2017).
- **HEIF/HEVC** ~50% smaller files than JPEG/H.264 with same quality (2017).

### 9.4 Memory & Algorithmic Gotchas

- **`Data.dropFirst()` is O(n)** — use `Slice` or new `Span` types (WWDC25-312)
- **Eytzinger layout** for cache-friendly binary search (WWDC25-312)
- **`InlineArray` and `Span`** for stack-allocated, non-escapable buffers (Swift 6.2 / 2025)
- **Don't pre-scale images for Vision** — framework rescales internally, pre-scaling burns work twice (WWDC17)
- **Don't hold many `ARFrame.capturedImage` references** — they're AVFoundation-vended and stall capture (WWDC17)

---

## §10. ML / AI — Capabilities You Can Add for Free

If you skipped Apple's ML stack, you're leaving major user-facing features on the table.

### 10.1 The ML Stack

| Capability | Framework | Year | Cost |
|---|---|---|---|
| Text/face/barcode/QR detection | `Vision` | 2017 | Free, on-device |
| OCR (live & batch) | `Vision.VNRecognizeTextRequest` | 2018 | Free, on-device, 30+ languages |
| Document understanding | `VNDocumentObservation` | 2025 | Free, on-device |
| Barcode scanning | `Vision.VNDetectBarcodesRequest` | 2017 | Free |
| Speech recognition | `Speech` framework | 2016 | Free, on-device since iOS 13 |
| Advanced speech-to-text | `SpeechAnalyzer` | 2025 | Free, real-time, multiple speakers |
| Translation | `Translation` framework | 2024 | Free, on-device |
| Natural Language | `NaturalLanguage` framework | 2018 | Free, replaces NSLinguisticTagger |
| Custom on-device ML models | `CoreML` | 2017 | Free runtime, train via `CreateML` |
| Generative text / structured output | `FoundationModels` | 2025 | Free, on-device LLM |
| Generative images | Image Playground integration | 2024 | Free for users with Apple Intelligence |
| Custom LLM fine-tuning | `MLX` framework | 2023 | Free, runs on Apple Silicon |
| GPU compute (ML in shaders) | `Metal` + `MPSGraph` / `Metal 4 ML` | 2017 → 2025 | Free |

### 10.2 App Intents Integration (2022, mature 2025)

This is the single biggest "free distribution" opportunity for any app:

- **Spotlight surfaces your app's actions** without extra work
- **Siri can invoke your intents** — voice integration without speech-to-text plumbing
- **Shortcuts app** lets users build automations
- **Visual Intelligence** integration (2025) — point camera at thing, your app appears
- **"Use Model" Shortcut action** (2025) — users can pipe your data through an LLM
- **Apple Intelligence integration** — your app participates in system-wide AI features
- **Interactive snippets** (2025) — rich response UI

If you only adopt one new framework from the past 5 years, make it App Intents.

### 10.3 Foundation Models Best Practices (2025)

- **`@Generable`** for typed structured output via constrained decoding
- **Property declaration order matters** for streaming UX AND output quality — put summaries LAST (transcript-only insight)
- **`includeSchemaInPrompt: false`** saves hundreds of tokens once you've provided examples
- **`session.prewarm()`** eliminates asset loading latency — call when user navigates to a screen that will use AI
- **`Tool` protocol** for runtime data fetching (RAG patterns)
- **Model size ~3B parameters**, on-device, zero cost, no API keys, offline

---

## §11. Build, Signing, Distribution

### 11.1 Modernize Your Build Pipeline

- **Bitcode** — added 2015, **removed in Xcode 14 (2022)**. Disable in build settings.
- **App Thinning** (2015) — automatic for App Store distribution
- **Universal binaries** (2020) — must include arm64 for Apple Silicon
- **Mergeable libraries** (2023) — single build setting, 1.5x–3x launch wins
- **Privacy manifests** (2024) — required for SDKs and apps using "Required Reason APIs"
- **Hardened runtime + notarization** (2019) — required for macOS Developer ID distribution

### 11.2 Signing & Distribution

- **Manual provisioning profiles** → Automatic signing (2016+) — let Xcode manage
- **iTunes Connect** → **App Store Connect** (renamed 2018)
- **App Store Connect API** (2018, mature 2025) — webhooks for build state, feedback, app version changes (replaces polling)
- **TestFlight Mac** (2021) — distribute Mac builds to testers
- **Xcode Cloud** (2021) — Apple-hosted CI/CD
- **`notarytool`** (replaced `altool` in Xcode 13)

### 11.3 New Capabilities & Entitlements to Audit

- **Background modes**: location, audio, VoIP, fetch, push, processing, refresh — declare only what you use
- **App Transport Security exceptions** — minimize and document
- **CarPlay**, **HealthKit**, **HomeKit**, **iCloud**, **Network Extensions**, **WeatherKit**, **WidgetKit**, **ActivityKit** — each requires explicit capability
- **EnergyKit entitlement** (2025) — required for home electricity APIs
- **AlarmKit** requires `NSAlarmKitUsageDescription` (2025)

### 11.4 Modern Asset Delivery

- **On-Demand Resources** (2015) — deprecated, migrate to Background Assets
- **Background Assets** (2025) — Apple-hosted, 200GB per app, integrates with App Store Connect
- **App Thinning** — automatic, just provide multi-resolution assets

---

## §12. Testing Modernization

### 12.1 XCTest → Swift Testing

```swift
// Old (XCTest)
class UserTests: XCTestCase {
    func testEmailValidation() {
        XCTAssertTrue(User(email: "a@b.c").isValid)
        XCTAssertEqual(User(email: "x").errors.count, 1)
    }
}

// New (Swift Testing, 2024)
import Testing

@Test func emailValidation() {
    #expect(User(email: "a@b.c").isValid)
    #expect(User(email: "x").errors.count == 1)
}

@Test(arguments: ["a@b.c", "test+1@example.org"])
func validEmails(_ email: String) {
    #expect(User(email: email).isValid)
}
```

Benefits:
- Macros provide much better failure messages
- Parameterized tests are first-class
- Tags for filtering test runs
- Async-native (no `XCTestExpectation` boilerplate)
- Tests aren't methods on a class — better composition

### 12.2 UI Testing

- **`XCUIApplication`** for UI testing (still current)
- **Record, replay, review** workflow (2025) — record manual interaction, edit the script
- **Hitch testing** with `XCTHitchMetric` (2023) — automate scroll smoothness checks

### 12.3 Snapshot Testing

- Apple doesn't ship a first-party snapshot framework
- pointfree.co's `swift-snapshot-testing` is the de-facto standard
- For SwiftUI specifically, use Xcode Previews + `RenderPreview` MCP for AI-driven verification

### 12.4 Performance Testing

- `measure {}` blocks in XCTest
- `XCTOSSignpostMetric` for custom signposts
- `XCTHitchMetric` for animation hitches
- Test against multiple device classes (especially older devices)

---

## §13. Platform-Specific Modernization

### 13.1 watchOS

| Era | Pattern |
|---|---|
| watchOS 1 (2014) | All UI logic in iPhone extension, slow |
| watchOS 2 (2015) | Native apps on watch, ClockKit complications |
| watchOS 3 (2016) | Dock model, instant launching, glance dropped |
| watchOS 6 (2019) | Independent watch apps (no iPhone required) |
| watchOS 9+ | Health features, sleep stages, complications redesign |
| watchOS 10 (2023) | Major UI redesign — vertical scrolling, new design language |
| watchOS 11 (2024) | Translation, smart stack improvements |
| watchOS 26 (2025) | Liquid Glass, smart stack widgets |

**Things to fix in old watchOS code:**
- WatchKit IPC was ~200ms per UI property set on watchOS 1–2 — it's not anymore on native apps
- `WKInterfaceTable` had no cell reuse — use modern SwiftUI Lists
- Background URL sessions — they actually work now
- Use `ClockKit` for complications (CLKComplicationDataSource)

### 13.2 tvOS

- Debuted 2015 with TVMLKit (HTML/JS-based) — long deprecated
- Modern path: SwiftUI + Focus engine
- Subscription / streaming app review process is strict — use TV provider sign-in, not custom auth
- Top Shelf extension for promoted content

### 13.3 Mac Catalyst

- Sneak preview as "Marzipan" 2018, shipped 2019
- Maturity: 2020 (Big Sur) — proper Mac idioms supported
- 2022+: Catalyst can opt into AppKit-style toolbars, sidebars, menus
- 2025: Liquid Glass for Catalyst apps
- **Catalyst silent gotcha**: `.completeFileProtection` no-ops on Mac — your sensitive iOS files are NOT encrypted at rest. Use Keychain or CryptoKit AES.GCM. (WWDC19-205)

### 13.4 visionOS (debut 2023, mature 2025)

If your iPad app is well-architected, it runs on visionOS as a "Compatible" app. To take real advantage:
- **Volumes** for 3D content alongside windows
- **Immersive spaces** for fully immersive experiences
- **RealityKit + SwiftUI** integration (2024 — `RealityView`)
- **Spatial layout** in SwiftUI (2025) — `rotation3DLayout`, `SpatialContainer`, depth alignments
- **Shared experiences** via SharePlay + spatial personas
- **Apple Immersive Video** format support
- **Spatial accessory input** (PS VR2 Sense, Logitech Muse, 2025)

---

## §14. Comprehensive Deprecation Reference

### 14.1 Frameworks (replaced or removed)

| Old | Replacement | Removed/Deprecated |
|---|---|---|
| `UIWebView` | `WKWebView` (then `WebView` SwiftUI in 2025) | Submission banned Dec 2020 |
| `ALAssetsLibrary` | `PhotoKit` | Removed iOS 9 |
| `AddressBook` (and `AddressBookUI`) | `Contacts` (and `ContactsUI`) | Deprecated iOS 9 |
| `EventKitUI.EKEventEditViewController` | Same, but per-event auth | Auth model changed iOS 17 |
| `NSLinguisticTagger` | `NaturalLanguage` | Deprecated 2018 |
| `SLSpeechRecognizer` | `Speech` framework | Deprecated 2016 |
| `Secure Transport` | `Network` framework | Deprecated 2018 |
| `OpenGL ES` | `Metal` | Deprecated 2018 |
| `SceneKit` | `RealityKit` | Soft-deprecated 2025 |
| `On-Demand Resources` | `Background Assets` | Soft-deprecated 2025 |
| `NSURLConnection` | `URLSession` | Deprecated iOS 9 |
| `dispatch_*` C APIs | Swift `DispatchQueue` / async-await | Convention since Swift 3 |
| `UILocalNotification` | `UNUserNotificationCenter` | Deprecated iOS 10 |
| `UIAlertView` / `UIActionSheet` | `UIAlertController` | Deprecated iOS 8 |
| `UIImagePickerController` (default behavior) | `PHPickerViewController` | Recommended iOS 14+ |
| `NSCoding` (manual) | `Codable` | Convention since Swift 4 |
| `NSKeyedUnarchiver.unarchiveObject(with:)` | `NSKeyedUnarchiver.unarchivedObject(ofClass:from:)` | Deprecated iOS 12 (security) |
| `UISearchDisplayController` | `UISearchController` | Deprecated iOS 8 |
| `UIWindow.rootViewController` (sole) | `UIWindowScene` | Mandatory post-iOS 26 |
| `XCTest` (assertions) | `Swift Testing` | Recommended 2024+ |
| `Combine` (`ObservableObject`) | `Observation` (`@Observable`) | Recommended 2023+ |
| `NavigationView` | `NavigationStack` / `NavigationSplitView` | Deprecated 2022 |
| `Bitcode` | (none — removed) | Removed Xcode 14 (2022) |
| `Reachability` | `NWPathMonitor` | Convention since 2018 |
| `NSURLSession` background events via `application(_:handleEventsForBackgroundURLSession:)` | Same, but per-scene now | iOS 13+ |
| `UIScreen.main` | `view.window?.windowScene?.screen` | Deprecated iOS 16 |
| `application(_:open:options:)` (without scenes) | Per-scene callbacks | iOS 13+ |
| `notify_register_dispatch` (Darwin notifications) | `NSNotification` / `NotificationCenter` | Avoid for new code |

### 14.2 APIs that didn't deprecate but quietly stopped being investment

- `CommonCrypto` — use `CryptoKit` for new code
- `NSOperation` — use Swift Concurrency
- `Combine` — use Swift Concurrency + Observation
- `Core Data` — use SwiftData for new persistence
- `Storyboards` — use SwiftUI Previews
- `AppDelegate`-only lifecycle — use Scenes + SwiftUI App
- `XCTest` — use Swift Testing

---

## §15. Chronological Reference Table

Find the year of your project's last meaningful refresh. Everything in subsequent rows is potentially relevant.

| Year | Major debuts | Critical deprecations | Headline frameworks |
|---|---|---|---|
| **2014** | Swift 1, App Extensions, HealthKit, HomeKit, CloudKit, Metal, WKWebView, PhotoKit, Touch ID API, Adaptive UI/Size Classes, Continuity/Handoff, SceneKit on iOS, WatchKit preview | ALAssetsLibrary, UIWebView (later) | iOS 8, OS X Yosemite |
| **2015** | Swift 2, Protocol-Oriented Programming, iPad multitasking, watchOS 2 native, tvOS, App Thinning, Bitcode, GameplayKit, ContactsKit, NSLayoutAnchor, Search APIs (Core Spotlight, NSUserActivity), UIStackView, Content Blockers | NSURLConnection, AddressBook | iOS 9, watchOS 2, tvOS, El Capitan |
| **2016** | Swift 3 (huge breaking renames), SiriKit, iMessage Apps, CallKit, watchOS 3 redesign, APFS sneak, Speech framework, Differential Privacy, Universal Clipboard, UNUserNotifications | UILocalNotification, dispatch C APIs (in Swift), SLSpeechRecognizer | iOS 10, macOS Sierra |
| **2017** | ARKit, Core ML, Vision framework, Drag and Drop, Files app, iOS 11 design refresh, Swift 4 + Codable, Metal 2, HEIF/HEVC, PDFKit cross-platform, MapKit clustering | NSCoding (in favor of Codable), default UIImagePickerController in many cases | iOS 11, High Sierra |
| **2018** | iOS 12 PERFORMANCE, Siri Shortcuts API + Shortcuts app, ARKit 2, USDZ, Create ML, Core ML 2, NaturalLanguage, Network framework, Marzipan preview, watchOS 5, Mojave Dark Mode, Memoji | NSLinguisticTagger, OpenGL ES, Secure Transport (in favor of Network framework) | iOS 12, macOS Mojave |
| **2019** | SwiftUI, Combine, Catalyst, iPadOS, Sign In with Apple, Dark Mode, Swift 5.1 (property wrappers, function builders, opaque return types), RealityKit, SF Symbols, Swift Package Manager in Xcode, BGTaskScheduler, CryptoKit, macOS notarization | UIWebView (banned 2020), 32-bit on macOS Catalina, UIApplicationDelegate-only lifecycle (recommendation) | iOS 13, iPadOS, macOS Catalina, watchOS 6 |
| **2020** | Apple Silicon transition, macOS Big Sur design, Widgets + WidgetKit, App Clips, Swift 5.3, watchOS 7 sleep tracking, App Tracking Transparency, ClockKit complications redesign, Logger (`os.Logger`), PHPickerViewController, ARKit 4 (location anchors) | UIWebView (December 2020 ban), legacy AppKit patterns | iOS 14, macOS Big Sur, watchOS 7 |
| **2021** | Swift Concurrency (async/await, actors, structured concurrency), SharePlay, Object Capture, RealityKit 2, Xcode Cloud, DocC, Focus modes, Live Text, Swift Playgrounds 4, TestFlight Mac, GroupActivities | None major; Combine begins to wane | iOS 15, macOS Monterey, watchOS 8 |
| **2022** | SwiftUI Charts, NavigationStack/SplitView, App Intents, Lock Screen widgets, Live Activities, Layout protocol, Swift 5.7 (regex, generic constraints), watchOS 9 | NavigationView (deprecated), Bitcode (removed), `setNeedsStatusBarAppearanceUpdate` patterns | iOS 16, macOS Ventura, watchOS 9 |
| **2023** | visionOS reveal, SwiftData, Observation framework, Swift macros (5.9), parameter packs, interactive widgets, mergeable libraries, watchOS 10 redesign, L4S networking, StoreKit 2 maturity, Reality Composer Pro, RealityKit on macOS | None forced, but Combine `ObservableObject` pattern phases out | iOS 17, macOS Sonoma, visionOS 1, watchOS 10 |
| **2024** | Apple Intelligence (Writing Tools, Genmoji, Image Playground), Swift 6 strict concurrency, Swift Testing, visionOS 2, Translation framework, Privacy manifest enforcement, WidgetKit interactivity (full), watchOS 11 | XCTest (in favor of Swift Testing), pre-Swift-6 unchecked concurrency | iOS 18, macOS Sequoia, visionOS 2, watchOS 11 |
| **2025** | Liquid Glass, Foundation Models, Swift 6.2 main-actor-by-default, visionOS 26, immersive video pipeline, AlarmKit, EnergyKit, PaperKit, PermissionKit, SpeechAnalyzer, Background Assets (replaces ODR), Wi-Fi Aware, App Intents + LLM integration, quantum-secure TLS default | UIScene becomes mandatory next year, SceneKit soft-deprecated, On-Demand Resources soft-deprecated | iOS 26, macOS 26, visionOS 26, watchOS 26 |

---

## §16. The Modernization Recipe

A five-phase migration that minimizes risk while delivering early wins.

### Phase 1: Stop the Bleeding (1–2 weeks)

Get the app building, signing, and submittable on current Xcode without breaking changes for users.

- [ ] Build with current Xcode + current SDK
- [ ] Fix compiler errors and Swift migration warnings
- [ ] Add or update `PrivacyInfo.xcprivacy` (privacy manifest)
- [ ] Add ATT prompt if you read IDFA or ship to tracking domains
- [ ] Audit Required Reason API declarations
- [ ] Remove Bitcode from build settings (if still on)
- [ ] Remove any `UIWebView` references (audit dependencies)
- [ ] Verify HTTPS for all endpoints; remove `NSAllowsArbitraryLoads`
- [ ] Test on current simulators: iPhone Air (latest), iPad Pro, Vision Pro, Apple Watch
- [ ] macOS only: enable Hardened Runtime, run `notarytool` end-to-end

**Exit criteria:** App builds, signs, runs on current OS, passes App Store validation.

### Phase 2: Modernize the Foundation (3–4 weeks)

Take the painful but mechanical changes that unlock everything else.

- [ ] Migrate Swift to current major version (incrementally — one breaking change at a time)
- [ ] Replace `NSCoding` with `Codable` everywhere reasonable
- [ ] Replace `NSURLConnection` and completion-handler `URLSession` with async/await
- [ ] Adopt UIScene + UIWindowSceneDelegate (or SwiftUI App lifecycle)
- [ ] Replace `print`/`NSLog` with `Logger`
- [ ] Replace `dispatch_*` C APIs with Swift `DispatchQueue` (or skip ahead to async/await)
- [ ] Adopt `os.allocator` / Swift's `withUnsafePointer` patterns where you have raw pointer code
- [ ] Add `Sendable` annotations to your value types (mostly trivial)
- [ ] Replace any `UIImagePickerController` usage with `PHPickerViewController`

**Exit criteria:** Foundation is current; no compiler warnings about deprecated APIs in your code.

### Phase 3: Adopt High-Impact Paradigms (4–8 weeks)

The big wins. Pick based on which gives your app the most leverage.

- [ ] **Swift Concurrency** — convert callback-based APIs to async/throws; replace `DispatchQueue.main.async` with `@MainActor`; use `TaskGroup` where you previously used `dispatch_group`
- [ ] **SwiftUI** — replace leaf screens, then forms, then navigation, then full flows
- [ ] **SwiftData** (if persistence is in scope) — for new models; keep Core Data for existing schema until cost-justified
- [ ] **Observation framework** — replace `ObservableObject`/`@Published` view models with `@Observable`
- [ ] **App Intents** — expose your app's primary actions to Siri/Spotlight/Shortcuts/Visual Intelligence
- [ ] **Vision / NaturalLanguage / Speech** — add OCR, scanning, transcription if relevant
- [ ] **Background Assets** if you have large content downloads
- [ ] **Network framework** if you have custom networking
- [ ] **CryptoKit** to replace `CommonCrypto` where present

**Exit criteria:** App now feels like a modern Apple-platform app. New features ship faster.

### Phase 4: Polish (2–4 weeks)

Visible improvements that delight users.

- [ ] **Liquid Glass** adoption (2025) — add `.glassEffect()` to controls
- [ ] **Icon Composer** for app icon refresh (2025)
- [ ] **SF Symbols 7** — replace any custom icon assets
- [ ] **Dynamic Type** audit — every text view scales
- [ ] **Dark Mode** audit — every color is semantic
- [ ] **VoiceOver** + **Voice Control** labels everywhere
- [ ] **Accessibility Nutrition Labels** in App Store Connect
- [ ] **Widgets** + **Live Activities** if applicable
- [ ] **Foundation Models** integration (on-device LLM features) where it adds genuine value
- [ ] **Passkeys** for authentication
- [ ] **Sign In with Apple** if you offer social sign-in

**Exit criteria:** App is genuinely competitive with new apps shipping today.

### Phase 5: Forward Discipline (ongoing)

Don't let it rot again.

- [ ] **Each WWDC**: schedule a half-day to review What's New in Swift, What's New in SwiftUI/UIKit, What's New in Xcode
- [ ] **Adopt Swift 6 strict concurrency** as soon as your dependencies support it
- [ ] **Adopt new iOS major-version SDK on day 1** of public beta — find breaking changes before users do
- [ ] **Run `XCTHitchMetric` in CI** — catch performance regressions
- [ ] **Subscribe to Apple Developer News** — privacy and review-process changes hit there first
- [ ] **Annual deprecation audit** — `Build > Build For > Profile` and check for new deprecation warnings
- [ ] **Run on the oldest device class you support** quarterly — performance issues hide on M2 iPads

---

## §17. Self-Assessment Checklist

Quick scorecard. Score each item: ✓ done / ⚠ partial / ✗ not done. <2/3 = significant tech debt.

### Critical (must-do)
- [ ] Privacy manifest present and accurate
- [ ] ATT prompt in place if tracking
- [ ] HTTPS-only (no ATS exceptions for first-party endpoints)
- [ ] No `UIWebView` anywhere (incl. dependencies)
- [ ] Hardened runtime + notarization (macOS)
- [ ] Universal binary (arm64 + x86_64)
- [ ] No Bitcode
- [ ] UIScene lifecycle adopted (urgent)

### Foundation
- [ ] Current Swift major version
- [ ] `Codable` for serialization
- [ ] `URLSession.data(for:)` async APIs
- [ ] `Logger` instead of `print`/`NSLog`
- [ ] `PHPickerViewController` instead of `UIImagePickerController` for media access
- [ ] `Network` framework or modern `URLSession` instead of `CFNetwork`/`NSURLConnection`

### Paradigms
- [ ] Swift Concurrency adopted in new code
- [ ] SwiftUI in at least some screens
- [ ] `@Observable` instead of `ObservableObject`
- [ ] App Intents exposing primary actions
- [ ] `NavigationStack` instead of `NavigationView`

### Polish
- [ ] Liquid Glass adoption
- [ ] SF Symbols throughout
- [ ] Dynamic Type works on every screen
- [ ] Dark Mode works on every screen
- [ ] VoiceOver labels on every interactive element
- [ ] Accessibility Nutrition Labels filed
- [ ] Sign In with Apple offered
- [ ] Passkeys supported
- [ ] Widgets and/or Live Activities (if applicable)

### AI/ML opportunities (any user-facing)
- [ ] Vision for OCR / barcode / document scanning
- [ ] Speech for voice input
- [ ] Translation for any user-facing text
- [ ] Foundation Models for content generation / structured extraction
- [ ] App Intents + "Use Model" exposure

### Hygiene
- [ ] Swift Testing for new tests
- [ ] `XCTHitchMetric` in CI
- [ ] MetricKit integration
- [ ] Mergeable libraries enabled (if many frameworks)
- [ ] Background Assets if you have downloadable content
- [ ] CryptoKit instead of CommonCrypto

---

## Appendix A: "Surprising" Hidden Gems Across All 12 Years

Cross-cutting findings that don't fit a category but are too valuable to omit. Each is sourced to a specific WWDC session.

- **`mach_absolute_time` is NOT nanoseconds on Apple Silicon** — most common porting bug, 40× slowdowns (WWDC20-10214)
- **`Data.dropFirst()` is O(n)**, not O(1) — use `Slice` or `Span` (WWDC25-312)
- **`Optional` is just an enum** modeled in Swift itself: `enum Optional<T> { case none; case some(T) }` (WWDC14-403)
- **APFS clones make `FileManager.copyItem` essentially free** regardless of file size (WWDC17 / 2017)
- **`URL.lines` and `URL.bytes` are AsyncSequence** — stream a remote JSON-Lines endpoint or a local file with no setup (WWDC21-10058)
- **GroupSession messaging is end-to-end encrypted, even from Apple** — free private cross-device channel for any custom multi-device experience (WWDC21-10183)
- **Catalyst silently no-ops file data protection** — `.completeFileProtection` does nothing on Mac. Use Keychain or CryptoKit (WWDC19-205)
- **Personal Voice runs entirely on-device** and your app can use it via `AVSpeechSynthesisVoice.personalVoice` (WWDC23-10033)
- **Core Data + SwiftData can share the SAME underlying store** — incremental migration screen-by-screen (WWDC23-10189)
- **L4S networking** can drop latency from 100ms → 5ms WITHOUT throughput loss — opt in via one Network framework flag (WWDC23-10004)
- **Mergeable libraries** can shrink launch time 1.5x–3x — single build setting, no code changes (WWDC23-10268)
- **iOS 12 made Auto Layout linear-complexity** — apps with deep view hierarchies got massive wins from JUST relinking against iOS 12 (WWDC18-220)
- **Network.framework's user-space TCP/UDP stack** lives in your app's address space — ~30% less CPU on packet-heavy workloads (WWDC18-715)
- **Custom keyboards BLOCK SMS code autofill** — iOS needs the system keyboard to inject the OTP (WWDC18-204)
- **Watch Keychain inherits wrist-detection lock** — credentials become inaccessible the moment the user takes off the watch (WWDC15-105)
- **Photoshop's value-type undo stack pattern**: append to `[Diagram]` for free undo via copy-on-write (WWDC15-414)
- **`dispatch_semaphore_wait` blocks priority inversion resolution** — semaphores have no ownership, so the system can't raise the worker's QoS. Use `dispatch_block_wait` (WWDC15-718)
- **`PDFActionResetForm`** with empty field list resets every widget — one-line full-form reset (WWDC17)
- **NEVER pre-scale images for Vision** — framework rescales internally, pre-scaling burns work twice (WWDC17)
- **Workout SiriKit intents with `.handleInApp`** run the app in the **background** — pause workouts via voice with phone locked (WWDC17)
- **Property declaration order in `@Generable`** affects Foundation Models output quality — put summaries LAST (WWDC25-301, transcript-only)
- **`session.prewarm()`** eliminates Foundation Models asset loading latency — call when user navigates to a screen that will use AI (WWDC25-301)
- **`includeSchemaInPrompt = false`** saves hundreds of tokens once you've provided examples in instructions (WWDC25-301)
- **Quantum-secure TLS is enabled by DEFAULT in iOS 26** — your app gets post-quantum protection automatically (WWDC25-314)
- **Background pushes are silently rate-limited** — 14 pushes may produce only 7 launches (WWDC20-10063)
- **Audio threads on Apple Silicon MUST join `os_workgroup`** or they may be scheduled on E-cores and glitch (WWDC20-10224)
- **Apple GPU SIMD group size is 32, not 64** — compute shaders that assumed otherwise produce visual artifacts on Apple GPUs (WWDC20-10602)
- **Eytzinger layout** for cache-friendly binary search — dramatically faster than sorted arrays (WWDC25-312)
- **SwiftUI's `visualEffect` modifier runs on background threads** — never access `@MainActor` state inside (WWDC25-266)

---

## Appendix B: How This Guide Was Built

This guide is synthesized from analysis of **1,751 WWDC session transcripts across 12 years (2014–2025)**, indexed at 1,895 total sessions, surfacing 166 curated learning pathways and several hundred best practices, hidden gems, performance tips, and migration warnings. Each item above traces back to a specific session — see the per-year dashboards (`index-{YEAR}.html`) for full context.

When in doubt, prefer reading the actual session transcript over reading this guide. The WWDC sessions consistently contain context, motivation, and hidden recommendations that don't make it into Apple's official documentation.

---

*Last updated: 2026-04-26*
