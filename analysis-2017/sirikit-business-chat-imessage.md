# SiriKit, Business Chat & iMessage Apps — WWDC 2017 Analysis

**Sessions covered:** 214 (What's New in SiriKit), 228 (Making Great SiriKit Experiences), 240 (Introducing Business Chat), 234 (What's New in iMessage Apps), 250 (Extend Your App's Presence with Deep Linking), 247 (Extend Your App's Presence With Sharing), 249 (Filtering Unwanted Messages with Identity Lookup), 246 (Deep Linking on tvOS)

## Headline

SiriKit gains **Lists & Notes**, **Visual Codes**, expanded Payments (accounts), and a new **per-parameter Intent UI customization** model that finally gives apps full control over how Siri renders their content. Business Chat debuts — a structured conversational flow letting customers contact businesses through iMessage. iMessage apps get a new compact-vs-expanded mode and tighter Hot Chat integration.

## SiriKit New Domains (214)

- **Lists & Notes** — `INCreateNoteIntent`, `INAppendToNoteIntent`, `INSearchForNotebookItemIntent`, `INCreateTaskListIntent`, `INAddTasksIntent`, `INSetTaskAttributeIntent`. Reminders are tasks with location or date triggers.
- **Visual Codes** — `INGetVisualCodeIntent` covers QR-code-based contact, payment, and request payment flows. The user says "Show my UnicornChat code" and your handler returns a `UIImage`.
- **Payments — Accounts** — `INTransferMoneyIntent` (account-to-account) and `INSearchForAccountsIntent` (balance lookups, including reward miles and points).

## Per-Parameter Intent UI Customization (214)

Previously, your `INUIHostedViewController` got one big chunk of the Siri view to customize. iOS 11 introduces **`configureView(for parameters:of interaction:context:completion:)`** which is called multiple times with different parameter subsets:

```swift
func configureView(for parameters: Set<INParameter>,
                   of interaction: INInteraction,
                   context: INUIHostedViewContext,
                   completion: @escaping (Bool, Set<INParameter>, CGSize) -> Void) {
    // Empty parameter set - first call. Add custom header.
    if parameters.isEmpty {
        completion(true, [], CGSize(width: 0, height: 60))
        return
    }
    // Specific parameter we want to handle:
    let pickup = INParameter(for: INRequestRideIntent.self, keyPath: \.pickupLocation)
    if parameters == [pickup] {
        let value = interaction.parameterValue(for: pickup) as? CLPlacemark
        configurePickupView(with: value)
        completion(true, [pickup], pickupViewSize)
        return
    }
    completion(false, [], .zero)  // Let Siri draw default
}
```

- Return `false` to fall back to Siri's default for any parameter set.
- Return multiple parameters to create a single combined custom view.
- **HIDDEN GEM**: this fixes the duplicate-info bug from iOS 10 SiriKit where ride-sharing apps showed Siri's pickup-location card AND their own custom pickup info redundantly.

## Background Workout Handling (214)

Workout intents (start, pause, resume, end) can now run **without launching your app to the foreground**:

```swift
class WorkoutHandler: INStartWorkoutIntentHandling {
    func handle(intent: INStartWorkoutIntent,
                completion: @escaping (INStartWorkoutIntentResponse) -> Void) {
        completion(INStartWorkoutIntentResponse(code: .handleInApp, userActivity: nil))
        // System calls UIApplicationDelegate.application(_:handle:completionHandler:)
        // in the background - no UI shown.
    }
}
```

- App is launched in the BACKGROUND (`.handleInApp` response code).
- Your app delegate's new `application(_:handle:completionHandler:)` runs to perform the action and call back.
- **HIDDEN GEM**: this means users can pause workouts while their phone is locked in their pocket — voice → background launch → action → done, screen never lights up.

## Alternative App Names (214)

Add to Info.plist:

```xml
<key>INAlternativeAppNames</key>
<array>
  <dict>
    <key>INAlternativeAppName</key>
    <string>UnicornPay</string>
    <key>INAlternativeAppNamePronunciationHint</key>
    <string>You-NEE-corn pay</string>
  </dict>
</array>
```

Siri now understands "Pay Bob with Unicorn" / "Pay Bob with CornPay" both as your app. Pronunciation hints help non-English users find apps with English names.

## SiriKit Best Practices (228)

- Implement `resolve…` methods for every parameter — that's how Siri disambiguates ambiguous user input. Returning `.disambiguation(with:)` makes Siri prompt "Did you mean Bob Smith or Bob Jones?".
- Implement `confirm…` methods to present a "Are you sure?" step for destructive operations. `confirm` returns a "Ready" response if you have authority, "RequiresAuthentication" if you need Touch ID, etc.
- Use `INVocabulary.shared.setVocabulary(_:of:)` to register user-specific terms (account nicknames, contact aliases, custom workout names). Update on app launch and after the user changes data.
- **WARNING**: Vocabulary is per-user-per-device. Re-register after app reinstall. Don't bulk-load 10,000 terms — keep relevant set under 1,000 for speed.

## Business Chat (240)

A new conversational endpoint accessible from Apple Maps, Spotlight, Siri, and the web — not from a generic "Messages → New" search.

```
Customer taps a "Message" button in Maps for "Apple Park"
  → Conversation begins in iMessage with the business
  → Business CSP (chat services platform) routes to a human or a bot
  → Business can ask for structured input via interactive messages:
     - List Picker (single/multi-select from a menu)
     - Time Picker (calendar UI)
     - Apple Pay (in-conversation purchase)
     - Custom payload (deep-link into your iMessage app)
```

- The business is identified by a `business-id` registered with Apple. Server-to-business webhooks deliver customer messages.
- Customers can mute / leave anytime; conversations are end-to-end encrypted via iMessage.
- **HIDDEN GEM**: Apple Pay inside Business Chat doesn't require a card-on-file — the customer authorizes via Touch ID right in the message. No checkout page, no redirect.

## iMessage Apps Refresh (234)

- New "compact / expanded" presentation. Compact (44 pt tall) hosts a button strip; expanded is full sheet.
- Sticker packs added to Xcode templates — drop PNGs in the asset catalog, no code, ship to App Store.
- **HIDDEN GEM**: `MSMessage.layout = MSMessageTemplateLayout()` with `image`, `imageTitle`, `imageSubtitle`, `caption`, `subcaption` produces a stable rich card across every iOS version. Don't reinvent.
- iMessage apps can now drive **Apple Pay** inline via the Business Chat extension flow.

## Deep Linking (250, 246)

- Universal Links remain the recommended deep-link surface.
- iOS 11: Universal Link prompts the user once per domain — "Open in App?" — then remembers. Apps can show a banner from Safari for re-engagement.
- **WARNING**: the `apple-app-site-association` file format is strict. Use `swcutil` to validate. Files served with the wrong MIME type or with comments in the JSON silently fail association.
- tvOS 11 (246) gets full Universal Links — search results in TV.app deep-link into your app at the right detail screen.

## Identity Lookup — SMS / MMS Filtering (249)

iOS 11 lets third-party apps filter incoming SMS / MMS:

- `ILMessageFilterExtension` runs out-of-process when an iMessage / SMS arrives.
- Returns `ILMessageFilterAction.allow`, `.filter` (silent), `.junk` (Junk folder).
- **PRIVACY**: extension can't read other messages or send any data. The system blocks all network access by default. To consult a server (with user consent), declare a server endpoint in Info.plist; the system makes the request opaquely on your behalf.

## Cross-references

- See `swift4-language-codable.md` — Codable for INVocabulary content.
- See `accessibility-everywhere.md` — Type to Siri pairs with these intent flows.
