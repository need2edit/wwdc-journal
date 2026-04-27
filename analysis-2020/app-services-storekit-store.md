# WWDC 2020 — App Store, StoreKit, Subscriptions, Distribution

WWDC 2020 brought significant additions to the App Store side: **StoreKit Testing in Xcode** (finally local IAP testing without sandbox accounts), **Family Sharing for in-app purchases**, **App Store Connect API** automation expansion, **subscription offer codes**, and **App Clip distribution paths**.

## Sessions Analyzed
- 10659 — Introducing StoreKit Testing in Xcode (gateway)
- 10661 — What's new with in-app purchase
- 10671 — Architecting for subscriptions
- 10869 — Family Sharing for in-app purchases
- 10868 — Subscription offer codes
- 10662 — What's new in Wallet and Apple Pay
- 10004 — Expanding automation with the App Store Connect API
- 10651 — What's new in App Store Connect
- 10639 — What's new in managing Apple devices
- 10145 — Design for Game Center

## StoreKit Testing in Xcode (10659)

The headline App Store improvement. Test in-app purchases **entirely locally** in Xcode without sandbox Apple IDs, without internet round-trips, without the App Store at all. This was a long-standing developer pain point.

### How It Works

1. Add a **StoreKit Configuration** file to your project.
2. Define products, subscription groups, introductory offers, etc. in the file.
3. Configure your scheme to use the StoreKit Configuration file.
4. Run — the app sees your products as if they came from the App Store.

The transaction manager in Xcode lets you:
- Approve / decline / interrupt purchases mid-flow
- Issue refunds
- Cancel subscriptions
- Time-shift the renewal date (compress months into seconds)
- Test failure scenarios

This **transforms** the developer workflow — testing a yearly subscription's auto-renew used to require waiting a year (or carefully manipulating sandbox accounts). Now you simulate it in seconds.

### Synchronizing Configuration

The StoreKit Configuration file can be synced to App Store Connect (one-way) so your test setup mirrors production product IDs.

## What's New in In-App Purchase (10661)

### App Store Promotional Offers

Existing subscribers can be offered a discounted re-engagement offer (e.g., "come back at 50% off for 3 months"). Apple validates the offer signature server-side before applying. Adopt via `SKPaymentDiscount`.

### App Store Server API

A new server-to-server REST API for managing transactions, subscriptions, and notifications. Pulls and pushes more than the older verifyReceipt endpoint:
- Look up transaction history
- Extend subscription renewal dates (e.g., apologize for a service outage)
- Receive App Store Server Notifications v2 with richer event types

### App Clip In-App Purchase Overlay (SKOverlay / appStoreOverlay)

After a successful App Clip experience, prompt the user to install the full app via:

```swift
// SwiftUI
.appStoreOverlay(isPresented: $showOverlay) {
  SKOverlay.AppClipConfiguration(position: .bottom)
}
```

The overlay slides up from the bottom; user can tap to install.

## Architecting for Subscriptions (10671)

Best practices session covering:
- **Server-side receipt validation** — never trust the client for entitlement decisions.
- **Receipt sharing across devices** — one Apple ID = subscription works on all the user's devices; don't require sign-in.
- **Group multiple subscriptions** in one subscription group when they're mutually exclusive (Basic vs. Premium tiers); `SKProductSubscriptionPeriod` and the group's renewal logic handles upgrades/downgrades.
- **Introductory offers** — strict eligibility rules (one per group per Apple ID per family); validate via `SKProductDiscount`.
- **Grace periods** — Apple gives users a 16-day grace period after billing failure to fix payment without losing service. Honor it.
- **Account hold** — billing failure can put accounts in "billing retry" status; show a "Manage Subscription" link rather than treating as expired.

## Family Sharing for In-App Purchases (10869)

Up to 6 family members can share access to non-consumable IAPs and subscriptions when the original purchaser enables sharing. Important details:
- The purchaser opts in **per product** in App Store Connect.
- For your code: receipt validation reveals shared transactions via `is_in_billing_retry_period` and family_shared fields.
- New transaction states for app to handle.

The Tech Talk (10869) — no transcript available — likely covers the receipt details.

## Subscription Offer Codes (10868)

Generate codes that users redeem for free or discounted access. Each code is single-use; eligible for one offer in a group. Generated in App Store Connect; presented to users via:

```swift
SKPaymentQueue.default().presentCodeRedemptionSheet()
```

(Tech Talk transcript not available; this is the broad pattern.)

## App Store Connect API Expansion (10004)

The REST API gained endpoints for:
- TestFlight beta tester management
- Provisioning profile management
- App availability / pricing
- Review submissions

This unlocks CI workflows for distribution that previously required clicking through the website.

## What's New in App Store Connect (10651)

UI / workflow updates:
- App Privacy questionnaire (new this year — mandatory by fall 2020)
- App Clip experience configuration
- More granular pricing tiers
- TestFlight improvements

## Wallet & Apple Pay (10662)

- **Apple Pay buttons in SwiftUI** — `PayWithApplePayButton` for direct integration
- **In-app card management** — issue store-credit cards, loyalty cards via PassKit improvements
- **Health & ID cards in Wallet** (gradual rollout)

## Managing Apple Devices (10639)

For enterprise/MDM:
- **Declarative device management** — devices can sync state declaratively rather than receive every command from MDM, improving reliability
- New configuration profiles for OS-level features
- Improved enrollment experiences

## Game Center: Major Redesign (10145)

Game Center got a full UI overhaul (the first in years):
- **Access point** — player avatar in a corner of the game UI provides one-tap access to the dashboard. Apple recommends top-left placement.
- **Dashboard** — transparent overlay on the game; shows profile, achievements, leaderboards.
- **Achievement cards** — collectible-card visual format. Up to 100 per game; reserve some for later updates.
- **Leaderboards** redesigned around friends.
- **Multiplayer lobby** — simplified UI, shows nearby players + friends + recent + contacts.
- **App Store integration** — friends' avatars appear on app icons; friends-playing surfaces on product pages.

For implementation: integrate access point via `GKAccessPoint.shared`; provide unique artwork per achievement and leaderboard; supports tvOS focus engine.

```swift
GKAccessPoint.shared.location = .topLeading
GKAccessPoint.shared.showHighlights = true
GKAccessPoint.shared.isActive = true
```

## Cross-References
- [app-clips.md](app-clips.md) — App Clip overlay invites users to install the full app.
- [privacy-security-network.md](privacy-security-network.md) — App Store privacy labels are part of this story.
- [game-controllers-center.md](game-controllers-center.md) — Game Center pairs with new game controller / xcloud-style features.

## Adoption Checklist
- [ ] Add a StoreKit Configuration file to your project for local IAP testing.
- [ ] Migrate to App Store Server API v2 for richer transaction and subscription events.
- [ ] Audit your subscription receipt validation server-side.
- [ ] Honor billing retry / grace periods in your entitlement logic.
- [ ] If supporting Family Sharing for IAP, audit receipt processing for shared transactions.
- [ ] Adopt `appStoreOverlay()` in App Clips to invite full app install.
- [ ] Complete the App Store privacy questionnaire by the fall deadline.
- [ ] If you're a game developer, integrate the new `GKAccessPoint`, design unique achievement/leaderboard artwork.
- [ ] If you have CI workflows touching App Store Connect, evaluate the API for automation.
