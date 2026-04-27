# SiriKit Debut — WWDC 2016 Analysis

**Sessions covered:** 217 (Introducing SiriKit), 225 (Extending Your Apps with SiriKit), 240 (Increase Usage of Your App With Proactive Suggestions)

## Headline

SiriKit is the year's marquee debut. For the first time, third-party apps can plug into Siri's conversational engine via a closed set of intent **domains**: messaging, payments (sending/requesting), VoIP calling, ride booking, photo search, workouts, climate/audio for CarPlay. Apple deliberately ships a *limited* domain list — every domain has been hand-tuned by Apple's NLP team, with every recipient/amount/intent slot resolved by Siri before your code runs.

## Mental model

- A **domain** is a category Siri understands (Messaging, Payments, Workouts, Ride Booking, VoIP Calling, Photo Search, Climate/Radio for CarPlay, CarPlay).
- An **intent** is a specific action inside a domain (`INSendMessageIntent`, `INRequestPaymentIntent`, `INStartWorkoutIntent`, `INRequestRideIntent`).
- An intent has **parameters** (recipients, content, amount, payee, workout name…). Siri pre-resolves them via NLP before invoking your extension.
- An **intent response** carries result code + filled-in parameters back to Siri.
- Siri handles audio→text, language→intent, the multi-turn dialogue, AND localization. Your code never sees raw speech.

## The three-call lifecycle (resolve → confirm → handle)

For each parameter on an intent, your `IntentHandler` extension is asked, in order:

1. **`resolve…`** — one method *per parameter*, called potentially multiple times until Siri + user + your app agree on a value. Return a `ResolutionResult.success(with:)`, `.disambiguation(with: [options])` (5–10 max), `.confirmationRequired(with:)`, `.needsValue`, `.notRequired`, or `.unsupported`.
2. **`confirm…`** — preflight the entire intent. Check authentication, network reachability, sufficient balance for a payment, etc. Return an `IntentResponse` with code `.success`, `.failureRequiringAppLaunch`, etc.
3. **`handle…`** — actually perform the action. Return an `IntentResponse`. **You have ~2-3 seconds**; if longer, return `.inProgress` and finish in the background.

**HIDDEN GEM:** In `confirm`, return `.failureRequiringAppLaunch` when the user is logged out — Siri then offers to launch your app and your `NSUserActivity` carries custom error strings via `userInfo`.

## Two extensions, never one

Every SiriKit app builds **two** extensions:
- **Intents extension** — runs in the background while Siri is foreground. Handles resolve/confirm/handle. Subclass `INExtension`, conform to `INIntentHandlerProviding`.
- **Intents UI extension** (optional) — a `UIViewController` that conforms to `INUIHostedViewControlling`. Render your app's brand/identity inside Siri. **Non-interactive** (no controls work). Use `INUIHostedViewSiriProviding` to suppress Siri's default UI when you're already drawing the message bubble or map.

**BEST PRACTICE:** Move all business logic into an embedded framework (e.g. `UnicornCore`) shared between app, intents extension, and intents UI extension. Lets you write unit tests using mock `INIntent` objects with no live Siri needed.

**BEST PRACTICE:** Group naturally-related intents into the *same* extension to minimize process churn. Audio call + video call → one extension; messaging → another. Don't put all intents in one extension (bulky), don't put each in its own (memory pressure). Apple's guidance: "use what feels natural."

## Vocabulary — app vs. user

Two scopes. Both feed Siri's recognizer so your custom names get transcribed correctly.

- **App vocabulary** (`AppIntentVocabulary.plist` in main bundle): hero phrases ("Start a workout with UnicornFit"), custom workout/vehicle names, pronunciation hints (phonetic spelling), example usages. **LOCALIZE these.**
- **User vocabulary** (`INVocabulary.shared()` from main app at runtime): contact names, photo album names, workout names. Provide as an **ordered set** — most important (favorites) first, then recents, then the rest. The ordering teaches Siri your priority. If your app uses the system address book, you don't need to register contacts at all.

**URGENT:** Update vocabulary the instant data changes (new contact added → add to vocabulary on save tap). **Delete on the same tick** — users will be furious if Siri keeps recognizing a contact they deleted yesterday. Wipe vocabulary entirely on logout/reset.

**HIDDEN GEM:** Don't put phone numbers, emails, or anything users wouldn't expect Siri to verbally recognize into vocabulary. Just names.

## Maps integration is free

The new ride-booking intents are shared between Siri AND Apple Maps. If you adopt `INRequestRideIntent` for SiriKit, your app appears in the new ride-sharing UI in Apple Maps with **zero extra code**. Same extension serves both surfaces. Same is true for booking-from-Maps in CarPlay.

## Security

- Some intents (payments, photo search) are restricted while locked **by default**.
- To restrict more (e.g. "messages only when unlocked"), set `IntentsRestrictedWhileLocked` array in extension Info.plist.
- `LocalAuthentication` framework is available in the intents extension — TouchID/FaceID for additional confirmation even when device is unlocked.
- Apple Pay is fully usable inside intents extensions; PKPaymentAuthorizationController appears above Siri.

## Designing a Siri experience

- Siri **forces users to say the app name** (uses `CFBundleDisplayName`). Users will say it as a verb ("Unicorn Chat Celestra…"), at start, middle, or end. Siri handles all positions.
- **Hands-free mode** (Hey Siri, CarPlay) gives more verbal feedback, less visual. **Held-in-hand** (home button) gives more visual, less verbal. Test BOTH.
- Pick **good defaults** so you don't ask 20 questions. For an unspecified pickup location → user's current location. But avoid surprises (don't default to expensive Pegasus for the ride).
- Use **`disambiguation`** for short option lists (5–10 max). Users can tap, say the option, or say "the second one."
- **`confirmationRequired`** when you've made a smart guess — Siri asks "Did you mean Sir Buttercup?"
- Provide examples in your vocabulary plist. Users discover them by asking Siri "What can you do?" Localize them.

## NSUserActivity donation surfaces (session 240)

In iOS 10 the `INInteraction` class lets you **donate** outgoing communications to the system. Donate a `INSendMessageIntent` after sending, and the contact card surface elevates your app as a default communication channel for that contact. Three donation intents support this: `INSendMessageIntent`, `INStartAudioCallIntent`, `INStartVideoCallIntent`. This is how WhatsApp/Skype/etc. show up under the message/call buttons in the Contacts app.

## Hidden gems summary

- Mock `INIntent` objects in unit tests — no live Siri needed.
- The Maps integration is automatic for Ride Booking — adopt SiriKit and you get Maps for free.
- `failureRequiringAppLaunch` lets you push the user out to your app with custom `NSUserActivity.userInfo` payload.
- App vocabulary plist is localizable — add per-locale variants for international users.
- Donate `INInteraction` from a successful send to be promoted as the default channel for that contact.

## Cross-references

- For background runtime/ProactiveSuggestions integration: see analysis-2016/proactive-suggestions.md
- For CallKit + VoIP intents: see analysis-2016/callkit-voip.md
- For Apple Pay inside intents extensions: see analysis-2016/apple-pay-extensions.md
