# Siri Shortcuts — WWDC 2018 Analysis

**Sessions covered:** 211 (Introduction to Siri Shortcuts), 214 (Building for Voice with Siri Shortcuts), 217 (Siri Shortcuts on the Siri Watch Face), 202 (What's New in Cocoa Touch §Shortcuts)

## Headline

WWDC 2018 introduced **Siri Shortcuts** — the next phase of SiriKit that lets every app expose its key actions to Siri without limiting itself to one of the 10 SiriKit domains. It's built on two layers: the lightweight `NSUserActivity` path (one line: `activity.isEligibleForPrediction = true`) and the deep `INIntent` path with a brand-new **Intent Definition File** in Xcode that lets you define your own custom intents. Apple also debuted the **Shortcuts app** (formerly Workflow), in which user-built workflows can chain together your custom intents.

## Two Adoption Paths (211)

| Need | API | Effort |
|---|---|---|
| Restore an in-app screen with parameters | `NSUserActivity` with `isEligibleForPrediction = true` | One line if you already have user activities for Spotlight/Handoff |
| Run inline in Siri / lock screen with custom UI and voice response | Custom intent (Intent Definition File + Intents Extension) | New target, but no app launch needed |
| Built-in domain (messaging, payments, lists, ride, workout, media, etc.) | Use the existing SiriKit intent | Same as 2017 |

**BEST PRACTICE**: only expose shortcuts that meaningfully _accelerate_ the user. A shortcut that just opens your app to its root screen is pointless and Siri will rarely surface it. Expose actions that are repeated, executable from any context, and offer real time savings.

## Custom Intent Definition File (211)

- New file template in Xcode 10. Visual editor for defining intents, parameters, response codes, response templates, and shortcut types.
- Each intent has a **Category** (Order, Create, Run, Do, Go, etc.) — the category controls Siri's confirmation phrasing ("Okay, I ordered it") and the look of the system buttons (e.g., the "Order" button color).
- Parameters support primitive types (string, number, boolean, person, location, date components, decimal, currency, length, mass, speed, temperature, energy, volume) plus a **Custom** type that maps to `INObject` (identifier + display string).
- **HIDDEN GEM**: prefer `INObject` (custom type) over two parallel string parameters for "id and display name." Two correlated parameters confuse the prediction engine because it treats them as independent. `INObject` keeps them bound.
- Each intent can have up to 16 **Shortcut Types**. Each type lists a subset of parameters that should be predicted together. Define many shortcut types — they let Siri find patterns at multiple levels of specificity. Three shortcut types (soup, soup+quantity, soup+quantity+options) lets Siri suggest "1 tomato soup" when it can, but fall back to "tomato soup" when the options aren't predictable.

## Intent Definition File Codegen Trap (211)

**URGENT**: when you check the Intent Definition File into multiple targets (app + intents extension + shared framework), Xcode generates intent classes _into each target_, causing duplicate-symbol issues. The fix:
- If you have a shared framework, set Target Membership to "intent classes" only on the framework target, and "no generated classes" on the app target and intents extension target.
- If you have no shared framework, generate in both app and extension; cleanup is automatic.

## Donation API (211)

- For an `NSUserActivity`: set `userActivity.isEligibleForPrediction = true` (it must also be `isEligibleForSearch`), then attach to a view controller as you would for Handoff.
- For a custom intent: build an `INInteraction(intent: orderSoupIntent, response: nil)` and call `.donate { ... }`. Donate **once per user action** that maps to that shortcut — not once per render.
- **HIDDEN GEM**: two new developer settings in Settings > Developer in iOS 12 — "Display Recent Shortcuts" and "Display Donations on Lock Screen" — show your donations in Search and on the Lock Screen instead of the system's normal Siri suggestions, so you can verify donation correctness without waiting for Siri to predict.

## Predictions: How Siri Picks (211)

- **For NSUserActivity**: Siri compares user activities using `requiredUserInfoKeys`. If you don't set these, _the entire userInfo dict is compared verbatim_, which means any one varying key (scroll position, last-viewed-at timestamp) destroys all matching. **CRITICAL**: always set `requiredUserInfoKeys` on prediction-eligible user activities.
- **For intents**: Siri compares the parameters listed in your Shortcut Types. Define a hierarchy of shortcut types from least-specific to most-specific.
- Prediction signals: time of day, day of week, location (if "Significant Locations" is enabled), recent app interactions.
- **BEST PRACTICE**: never include a timestamp in donated payloads. A shortcut for "Wednesday's appointments" becomes useless on Thursday. Use relative phrases ("tomorrow's appointments") that compute fresh at execution time.

## Custom Responses (Intent Definition File) (214)

- Four response types: **success**, **failure** (with multiple error codes), **confirmation** (preview before committing — "Are you ready to order?"), and **informational** (read-only data delivery, no transaction).
- Define response templates with placeholders. Codegen produces typed initializers: `OrderSoupIntentResponse.success(soup: soup, waitTime: "10 minutes")`.
- **HIDDEN GEM**: Siri's confirmation behavior depends on the intent's Category. "Order" category gets confirmation by default ("Are you ready to order?"); "Information" category does not. The "User Confirmation Required" checkbox lets you override. Critical for transactional intents like ordering, paying, sharing.
- Informational responses unlock entirely new app categories — transit schedules, ski reports, "what's the weather at my next meeting" — that previously had no way into Siri.

## Custom UI: Intents UI Extensions (214)

- Reuse the iOS 11 `MSMessagesAppViewController`-style approach: ship an Intents UI Extension target whose view controller renders a custom UI for your intent.
- The same custom UI shows up in Siri, Search, the Lock Screen, and the Shortcuts app.
- **HIDDEN GEM**: the order of parameters in the Intent Definition File determines image-attachment priority for sticker-style suggestions. List parameters from least-specific to most-specific so the most informative image (e.g., the soup, not the delivery location) wins when both are bound.

## Per-Parameter Images (214)

- Set `interaction.parameter(for: \.soup)?.setImage(soupImage, forParameterNamed: \.soup)`.
- For NSUserActivity, attach a `CSSearchableItemAttributeSet.thumbnailData = pngData` and assign as the `userActivity.contentAttributeSet`.

## Suggested Invocation Phrases (214)

- Both `NSUserActivity` and `INIntent` have a `suggestedInvocationPhrase` property (a String).
- **BEST PRACTICE**: 2–3 words, no "Hey Siri" prefix, easy to remember, localized. "Chowder time" not "Order one clam chowder to my office."
- Localize via `.stringsdict` for plurals — Apple ships an example with English, Hebrew, and Russian plural cases all handled automatically by `NSString(format:locale:)`.

## In-App "Add to Siri" Button (214)

- New `INUIAddVoiceShortcutViewController` and `INUIEditVoiceShortcutViewController` let you embed Apple's official "Add to Siri" UI right inside your app.
- `INVoiceShortcutCenter.shared.getAllVoiceShortcuts(...)` lets your app know which shortcuts the user has already added — so you can show a checkmark next to "Order my regular" if it's already wired up.
- `INVoiceShortcutCenter.shared.setShortcutSuggestions(_:)` lets you proactively seed suggestions even for things the user has never done (e.g., a music app suggesting "Play my Discover Weekly playlist" before they've manually played it).

## Privacy: Honoring Deletes (211)

- **URGENT**: when the user deletes content in your app, you _must_ delete the corresponding donations. Otherwise Siri keeps suggesting "play X" for a song the user deleted.
- For `NSUserActivity`: set `persistentIdentifier` before donating, then call `NSUserActivity.deleteSavedUserActivities(withPersistentIdentifiers:)` when the content is deleted, or `deleteAllSavedUserActivities()` on logout.
- If you also use Spotlight indexing, set `relatedUniqueIdentifier` to bind the activity to the searchable item — deleting from Spotlight then automatically deletes the donation.
- For intents: set `INInteraction.identifier` and/or `groupIdentifier` before donating. Then `INInteraction.delete(with: identifiers)` or `INInteraction.delete(with: groupIdentifier:)`.

## Watch Face Integration (217)

- `INRelevantShortcut` is the watch-specific wrapper. It contains an `INShortcut` (which wraps either an `NSUserActivity` or `INIntent`) plus an array of `INRelevanceProvider`.
- Relevance providers: `INDateRelevanceProvider`, `INLocationRelevanceProvider`, `INDailyRoutineRelevanceProvider` (`.morning`, `.commute`, `.evening`...).
- **HIDDEN GEM**: relevant shortcuts work _even if you don't have a Watch app_. As long as the shortcut is a background-executable intent and doesn't need APFS-encrypted data, it executes on iPhone via the watch's connection. iOS 12 watches with no companion watch app still surface the platter on the Siri face.
- The `WKRelevantShortcutRefreshBackgroundTask` lets your watch app update relevant shortcuts in the background — important for shortcuts whose platter shows real-time data ("72° and cloudy").
- The `WKIntentDidRunRefreshBackgroundTask` runs after a background intent fires, letting the main extension refresh complications and snapshots.

## Media Intent (211)

- New built-in `INPlayMediaIntent` works great with Shortcuts and shows up in the lock-screen now-playing controls when headphones connect.
- On HomePod: a play-media shortcut added on iPhone is invokable on HomePod by voice, with audio playing through HomePod from your iPhone. (HomePod doesn't run apps but can route intents.)

## Cross-references

- Watch background tasks: 206 (What's New in watchOS).
- New User Notifications interactions complement shortcuts: 710, 711.
- App Store discovery of shortcuts requires merchandising via NSUserActivity for Spotlight: see 2017's "Making the Most of Search APIs."
