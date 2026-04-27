# New App Store, In-App Purchase & Distribution — WWDC 2017 Analysis

**Sessions covered:** 301 (Introducing the New App Store), 302 (What's New in iTunes Connect), 303 (What's New in StoreKit), 304 (What's New in Device Configuration, Deployment, and Management), 305 (Advanced StoreKit), 814 (Designing for Subscription Success), 816 (Love at First Launch)

## Headline

iOS 11 redesigns the App Store from the ground up: **Today, Games, Apps, Updates, Search** tabs replace the old taxonomy. Editorial **Stories** and **App of the Day** features curate; the "All-Time" rankings shrink in importance. **In-app rating prompts via `SKStoreReviewController`** become the official path; arbitrary rating prompts become risky. App Store Connect (newly renamed from iTunes Connect) gains **promo codes for in-app purchases**, **app analytics for IAP funnels**, and **price-tier scheduling**. Subscription apps are designated first-class citizens with tooling for free trials, intro pricing, and grace periods.

## The New Editorial Surface (301)

- **Today tab**: hand-curated stories featuring developers, apps, and games. Stories show the studio behind the app; the social angle is intentional.
- **Games tab**: separate from Apps — games are 80% of App Store downloads but had no dedicated home.
- **Apps tab**: organized by category and editorial collection.
- **Updates tab**: shows In-App Purchase changes and subscription status alongside app updates.

**HIDDEN GEM**: the App Preview videos can now be **autoplaying** in the Today and category feeds. Apps with strong videos see significantly higher conversion. Author 3 videos (one per orientation if relevant) — viewer screen size determines which plays.

## SKStoreReviewController (305)

```swift
SKStoreReviewController.requestReview()
```

The system shows the rating prompt **at most three times per 365-day rolling window** per user. App Store Review enforces this — custom rating prompts that bypass `SKStoreReviewController` are increasingly subject to rejection.

- **WARNING**: do not call from the app delegate's `applicationDidFinishLaunching` — reviewers have rejected apps for prompting before the user has used the app meaningfully.
- **BEST PRACTICE**: trigger after a successful, valuable user moment (completed onboarding, finished N-th task, won a level). Never after an error or churn-risk event.

## Subscription Improvements (305, 814)

- **Free trials and intro pricing**: configure in App Store Connect; StoreKit reports them via `SKProductDiscount`.
- **Subscription Groups**: organize tiers (Basic, Pro, Premium) so users see a single "switch tier" UI instead of multiple separate subscriptions.
- **Server-to-server notifications (S2S)**: configure a webhook URL to receive `INITIAL_BUY`, `RENEWAL`, `CANCEL`, `DID_FAIL_TO_RENEW`, `DID_RECOVER`, `INTERACTIVE_RENEWAL` events. Your server source-of-truth without polling.
- **Grace periods** (announced 2017, ships later): keep service active for 16 days after a billing failure to recover the user.
- **Subscription offer codes** (announced 2017, fully shipped 2020): distribute promotional codes for win-back.

**HIDDEN GEM**: introduce a 7-day free trial with intro price. Conversion rates from trial-to-paid double on average vs. cold-start subscription. Use App Store Connect's subscription analytics to see retention curves.

## In-App Purchase Promotions on App Store (305)

Promote up to 20 IAP items directly on your App Store product page:

- Each promoted IAP gets its own image + name + description + price.
- Tapping the IAP card on the App Store launches your app to the appropriate IAP view.
- Server-side code path: `SKPaymentTransactionObserver.paymentQueue(_:shouldAddStorePayment:for:in:)` — return `true` to forward the payment immediately, `false` to defer to your custom flow (e.g. require login first).

## Price Tier Changes (302)

- Schedule price changes in advance (e.g., "raise to $4.99 on 2018-01-01").
- Per-territory pricing with "auto-adjust" tracking the US tier.
- Currency conversions auto-update.

## Beta & TestFlight (303)

- 10,000 external beta tester slots (raised from 2,000 earlier).
- Internal testers can use Apple ID alone — no email invite required.
- Crash reports from TestFlight feed back into Xcode Organizer with symbolicated stacks.
- **HIDDEN GEM**: TestFlight builds expire after 90 days. Schedule beta uploads on a cadence — leaving testers without a fresh build for a quarter resets onboarding.

## Device Management (304)

- New MDM commands for shared iPad in education and business: `OSUpdate`, `RestrictionList`, `Lock`.
- `Setup Assistant` skip keys: pre-skip iCloud signin, Apple Pay setup, Siri permission for managed devices.
- DEP (Device Enrollment Program) and VPP (Volume Purchase Program) merged into Apple Business Manager / Apple School Manager.

## App Review Guidelines Refresh (301, 814)

- Subscription apps must justify recurring billing — pure content + sync no longer always qualifies. Include ongoing service, frequent content updates, or cloud features.
- "Free trial" UI must be clear about post-trial billing. Pre-Apple-mandated text is shown by StoreKit; don't paraphrase incorrectly.
- **WARNING**: rejecting a refund request from a customer is no longer your call — Apple will refund and possibly chargeback to you. Optimize for low refund rates by setting expectations clearly.

## Designing For Subscription Success (814)

- Show value FAST — the first launch must demonstrate why subscribing matters.
- Free tier should be valuable in itself; the upgrade should feel like an unlock, not a punishment.
- Onboarding sequence: **explain → demo → ask**. Asking for the subscription before the user has experienced value yields ~5% conversion; asking after a clear value moment yields 25-40%.
- Allow the user to use the app meaningfully without subscribing — "wall of paywall" experiences review poorly.

## First Launch Best Practices (816)

- Three-screen rule: orient → opt-in to permissions (notifications, location) → land in core flow.
- Permission prompts should be **just-in-time, not bulk-up-front**. Asking for location on launch alienates; asking when the user taps "Find nearby" succeeds.
- Defer authentication until necessary. Many apps lose 60% of users on a sign-up wall.
- **HIDDEN GEM**: pre-warm Sign In with Apple (one tap, biometric) reduces sign-up friction near-zero — but Sign In with Apple ships in 2019. For 2017, leverage iCloud Keychain auto-fill of saved passwords (iOS 11 introduces the QuickType bar credential row).

## Cross-references

- See `swift4-language-codable.md` — Codable for App Store receipt parsing.
- See `accessibility-everywhere.md` — TestFlight reviews include accessibility passes for many large studios.
