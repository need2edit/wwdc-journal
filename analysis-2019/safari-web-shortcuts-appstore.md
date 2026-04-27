# Safari, Web, Shortcuts & App Store — WWDC 2019 Analysis

**Sessions covered:** 515 (What's New in Safari), 518 (What's New for Web Developers), 720 (What's New in Safari Extensions), 511 (Supporting Dark Mode in Web Content), 513 (Understanding CPU Usage with Web Inspector), 514 (Auditing Web Content with Web Inspector), 213 (Introducing Parameters for Shortcuts), 243 (Integrating with Siri Event Suggestions), 805 (Building Great Shortcuts), 806 (Designing Great Shortcuts), 207 (Introducing SiriKit Media Intents), 302 (In-App Purchases & S2S Notifications), 305 (Subscription Offers Best Practices), 304 (App Distribution), 716 (Universal Links)

## Headline

Safari 13 brings desktop-class browsing to iPad and adopts CSS dark mode. Shortcuts becomes a system-shipping app with **parameters** that let intents accept user-configured input at runtime. SiriKit gains a **Media intent** so any music/podcast/audio app can be invoked via "Hey Siri play X on Y."

## Safari 13 Highlights (515, 518)

- **iPadOS Desktop class browsing**: WKWebView requests desktop sites by default. Sites built mobile-only need their breakpoints rechecked.
- **Form validation API** — `<input pattern>` actually works.
- **Pointer events** spec fully shipped — unified mouse/touch/pen events on web.
- **Resource Timing Level 2**, **Server-Timing** headers in dev tools.
- **Visual Viewport API** — accurate viewport metrics during pinch-zoom.
- **CSS Scroll Snap**, **CSS Position: sticky** widely supported.

## Web Dark Mode (511)

```css
@media (prefers-color-scheme: dark) {
  body { background: black; color: white; }
}
```

Plus `<meta name="color-scheme" content="light dark">` to opt your site in. **HIDDEN GEM**: native form controls (input, select) automatically adapt to the user's color scheme.

## Safari App Extensions (720)

- macOS Safari extensions ported away from the legacy Safari Extension format and into native App Extensions (App Store distributable).
- **URGENT**: legacy `.safariextz` extensions deprecated. Existing developers must migrate.
- Native extensions can read DOM via Content Scripts, modify the page, communicate with a containing macOS app.
- Communicate with web pages via `safari.application.dispatchMessage(...)`.

## Web Inspector Improvements (513, 514)

- **CPU profiling** with sampled call stacks and flame graphs.
- **Audit panel** — write JavaScript audits for accessibility, performance, web standards. Export, share, and re-run.
- Built-in audits ship: poor color contrast, missing alt text, large image hot spots.

## Shortcuts: Parameters (213, 805, 806)

The biggest change to App Intents this year.

- Old SiriKit intents had hardcoded parameters. The new **Custom Intents with Parameters** let your app define its own intent class with typed inputs.
- User builds shortcuts visually in the Shortcuts app, picks parameters per step.
- Voice phrase: "Order [coffee size] from [shop]" with `coffee size` and `shop` as parameters Siri prompts the user for.

### Implementation
1. Add an Intent Definition File to your project.
2. Define your intent class with parameter declarations.
3. Implement `INIntentHandler` in an Intents extension.
4. Donate completed instances of the intent (`INInteraction(intent:response:).donate()`).

### Suggested phrases
- Implement `INIntentHandlerProviding` so Siri can suggest your intent in the Shortcuts gallery and on the lock screen.
- Provide rich UI via `IntentResponse.userActivity` and a custom Intent UI extension.

## Siri Event Suggestions (243)

- Donate `INReservation` and similar to surface your bookings/events as Siri suggestions and on the lock screen.
- Maps shows directions, Calendar pre-creates events, lock screen offers a tap to open.

## Media Intents (207)

- "Hey Siri, play [song] on [your app]" works for third-party music/podcast apps via `INPlayMediaIntent`.
- Resolve which song the user meant via `IntentHandler`. Return a `MPMusicPlayerController`-equivalent for Siri to operate.

## In-App Purchases & Subscriptions (302, 305)

- **App Store Server Notifications** (S2S) — Apple posts JSON to your server for subscription state changes. Replaces the old polling pattern. Includes purchase, renewal, cancel, billing retry, refund.
- **Subscription Offers** — promotional offers (free trials, discounted intro periods) can be targeted at specific users via signed offer objects.
- **Family Sharing for In-App Purchases** — opt in by setting `IsFamilyShareable=true` for non-consumables. **HIDDEN GEM**: makes premium content much more attractive — buy once, share with up to 5 family members.
- **App Store Connect API** — programmatic access to your TestFlight builds, sales reports, certificates, profiles.

## App Distribution (304)

- Ad Hoc, Enterprise, Developer ID, App Store, TestFlight — overview session.
- **URGENT**: Apple Enterprise Program more strictly enforced — companies caught distributing public-facing apps via Enterprise certs are banned.
- Notarization (703) becomes effectively mandatory for Mac apps distributed outside the App Store starting Catalina.

## Notarization (703)

- Required for ALL Mac software distributed outside the App Store starting macOS 10.15 (Catalina, Oct 2019). Hardened Runtime + Notarization checks malware via Apple's Gatekeeper.
- Submit via `xcrun altool --notarize-app` or Xcode's Organizer.
- Must enable Hardened Runtime and pass Apple's malware scan; ticket is stapled to your app.
- **URGENT**: not just Mac App Store apps — every direct download, every internal tool, every CI artifact you let users grab.

## Cross-references

- SiriKit Media Intents replaced custom playback hacks: 207, 805.
- Notarization + Gatekeeper hardening: 701 (Advances in macOS Security), 703.
- Sign In with Apple as a payment-account proxy: 706, 302.
