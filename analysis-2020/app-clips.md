# WWDC 2020 — App Clips

App Clips debuted at WWDC 2020: a new app category for **lightweight, on-demand app experiences** that launch from a URL, NFC tag, QR code, or App Clip Code without requiring a full install. Sub-10MB, focused, designed to evaporate after use.

## Sessions Analyzed
- 10174 — Explore App Clips (gateway)
- 10146 — Configure and link your App Clips
- 10172 — Design Great App Clips
- 10120 — Streamline your App Clip
- 10118 — Create App Clips for other businesses
- 10098 — What's new in Universal Links

## What an App Clip Actually Is

An App Clip is a **second app target** in Xcode that ships alongside your full app. It's a real iOS app binary subject to a strict size limit and several restrictions, intended to handle a specific URL-driven experience instantly.

Three terms to learn:
1. **App Clip Experience** — a URL that on iOS 14 is handled by the App Clip rather than Safari. Configured in **App Store Connect**, not via Apple-App-Site-Association files.
2. **App Clip** — the lightweight binary built from a separate Xcode target.
3. **Your App** — the full app. Always preferred when installed; the App Clip is downloaded only when no app exists.

When the user installs the full app, it takes over the URL handling. The App Clip and full app are mutually exclusive on a single device.

## Discovery Surfaces

App Clips can launch from:
- App Clip Codes (Apple-designed scannable codes that combine NFC + visual)
- Generic NFC tags
- QR codes
- Safari Smart App Banners
- Maps Place Cards
- Messages links
- iMessage app card via the new SKOverlay/`appStoreOverlay()` SwiftUI modifier (in your App Clip, you can prompt to install the full app)

App Clip Codes are the recommended path — visual familiarity, NFC convenience.

## Size Constraint: 10MB After Thinning

The App Clip must be under 10MB. To stay under:
- Share assets with the main app via a shared Asset Catalog (drag colors/icons/images from the main asset catalog to a shared one in Xcode and add it to both targets).
- Share Swift source with conditional compilation (define `APPCLIP` in Swift Compiler Custom Flags for the App Clip target; use `#if APPCLIP` to strip references to features the Clip doesn't need).
- Strip recipe-style features (e.g., the full Fruta app has Recipes; the App Clip strips them out).
- Download additional data on demand from your server.

## What Works Like a Normal App

- UIKit or the new SwiftUI app lifecycle
- Any iOS SDK API can be linked (no special "isAppClip" branching needed)
- StoreKit (in-app purchases work as in the main app)
- `ASAuthorizationController` for Sign In with Apple / federated sign-in
- Apple Pay (recommended way to take payment in an App Clip)
- Notifications (limited)
- Shared data containers between Clip and full app (new this year — see migration below)

## What's Restricted

- No access to **HealthKit** or sensitive health/fitness data — `HKHealthStore.isHealthDataAvailable` returns `false` in an App Clip; check before requesting.
- No **custom URL schemes**, **document types**, or **Universal Links** registration. If your federated sign-in callback uses a custom URL scheme, switch to `ASWebAuthenticationSession` which doesn't need scheme registration.
- No **bundled extensions** (no content blockers, share extensions, etc.).
- No iOS backups — the Clip is treated as ephemeral.

## Privacy Model

App Clips are designed to be **privacy-first**:
- Limited access to sensitive user data; HealthKit, Music, etc. are off-limits.
- A new **location confirmation** API replaces full Core Location for the common "is the user near this tag?" check. It returns success/failure without sharing precise location with your code, and there's no permission prompt — but a failed check is ambiguous (location could be off, denied, or genuinely not at the location). Always provide a fallback path for the user to complete the action.
- App Clips and their data containers are **deleted automatically by iOS** after a period of disuse. Treat the Clip's local storage like a cache.
- Frequently used Clips have their lifetime extended.
- When the user installs the full app, iOS auto-migrates camera/microphone/Bluetooth permissions.

## Data Migration: App Clip → Full App

A new **shared group container** is automatically available to both your App Clip and your full app. Store anything you want to migrate (cached order, preferences, partial sign-in state) in this container instead of the App Clip's standard container. When the user installs the full app, the standard container is deleted but the shared container survives — the full app gets a one-time chance to copy data out.

## Designing Linear Experiences

Apple is emphatic: **rethink your app's flow for App Clips, not just clip a piece off**. Your app likely has hierarchies (start page → tab bar → list → detail). For App Clips, this is wrong shape:

- Strip top-level navigation (tab bars, side menus) — use one URL per experience.
- Use deep-link URLs to skip configuration screens (which store, which product, which variant).
- Each experience should be a single user goal achieved in seconds.
- "Reward programs" or "create an account" should be **optional steps after** the user achieves their primary goal — not blockers up front.

Examples Apple shipped:
- Coffee shop: order a drink. URL identifies the store. No store-chooser required.
- Parking meter: pay for parking. URL identifies the meter. Skip the city-chooser.
- E-commerce checkout: complete purchase. URL identifies the product. Show full sign-up only after the order's done.

## Configure and Link (Session 10146)

Two new configuration steps:
1. **App Store Connect** — register the App Clip Experience URLs. The URLs become the public surface; no Apple-App-Site-Association edits needed for App Clip URLs.
2. **App Clip Codes** — generated from App Store Connect for your registered experiences. They embed the URL plus a visually unique pattern.

For multiple experiences in a single App Clip, your Clip receives an `NSUserActivity` with the launching URL — switch on the URL path to drive UI.

## Cross-References
- [swiftui-2-foundation.md](swiftui-2-foundation.md) — App Clips work great with SwiftUI's small reusable views.
- [privacy-security-network.md](privacy-security-network.md) — for AppTrackingTransparency, location privacy.
- [siri-intents-shortcuts.md](siri-intents-shortcuts.md) — Siri Suggestion can surface App Clip experiences.

## Adoption Checklist
- [ ] Decide whether your app has an App Clip-shaped use case (instant, focused, contextual).
- [ ] Add a new App Clip target in Xcode.
- [ ] Set up shared assets and source code with conditional compilation.
- [ ] Wire up App Clip Experiences in App Store Connect.
- [ ] Use shared group containers for any data that should survive an upgrade to the full app.
- [ ] Use the location confirmation API instead of full Core Location.
- [ ] Use `ASWebAuthenticationSession` instead of custom URL scheme callbacks.
- [ ] Add `appStoreOverlay()` to invite users to install the full app after a successful experience.
- [ ] Test the < 10MB size limit (thinned).
- [ ] Test under privacy-restricted modes — your Clip should degrade gracefully.
