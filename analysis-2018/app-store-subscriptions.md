# App Store, Subscriptions & In-App Purchases — WWDC 2018 Analysis

**Sessions covered:** 301 (What's New in App Store Connect), 302 (What's New in Managing Apple Devices), 303 (Automating App Store Connect), 304 (What's New in Search Ads), 704 (Best Practices and What's New with In-App Purchases), 705 (Engineering Subscriptions), 232 (Getting Ready for Business Chat), 720 (Wallet and Apple Pay)

## Headline

WWDC 2018 doubled down on the subscription business model. Free trials are now possible for **non-subscription apps** (via paid in-app purchase + free unlock pattern), introductory pricing got better APIs, server-to-server notifications expanded, and Apple's billing-retry service automatically recovered **12 million subscriptions** in its first year. Plus a separate Sandbox account in iOS 12 (no more signing in and out of production accounts to test purchases) and the new App Store Connect API for full automation.

## Free Trials for Non-Subscription Apps (704)

A new pattern, not a new API:
1. Make your app **free** in the App Store.
2. Add a non-consumable IAP at price tier matching your old paid price ("Full Unlock — $9.99").
3. Add a second non-consumable IAP at price tier 0 ("14-Day Free Trial").
4. Before the trial begins, clearly show the trial duration, the cost after, and what features expire.

```swift
// Look for the trial-start non-consumable in the receipt's type 17 dictionary
if let trialStart = receipt.type17.first(where: { $0.productID == "com.app.trial" }) {
  let purchaseDate = trialStart.purchaseDate  // type 1704
  // Compare to a trusted clock (server time, DeviceCheck) — not local clock
}
```

- **HIDDEN GEM**: use `DeviceCheck` API to detect "this device already used the free trial" — survives reinstalls. The clock check is unreliable on its own (users can change device time).

## Introductory Pricing API Maturity (704, 705)

- `SKProduct.introductoryPrice` (`SKProductDiscount`) — exists if the user is eligible.
- Three modes: `payAsYouGo` (renewing introductory rate), `payUpFront` (one-time discounted period), `freeTrial` (3 days to 1 year).
- `subscriptionPeriod`: `unit` (.day/.week/.month/.year) + `numberOfUnits`.
- `numberOfPeriods` on the introductory discount: how many billing cycles at the discount price (e.g., 2 cycles of 3-month at $1.99 each, then standard $9.99/3 months).
- Eligibility is **per subscription group**, not per product. Track it server-side using receipt parsing of `is_trial_period` and `is_in_intro_offer_period`.
- New `SKProduct.subscriptionGroupIdentifier` so you can compute eligibility server-side without re-fetching products.

## App Store Receipt Best Practices (704)

- **NEVER** send the receipt directly from device to `verifyReceipt`. You don't control either end of the connection — vulnerable to MitM and to spoofed device-side validation results.
- Always send device → your trusted server → `verifyReceipt`.
- For utility apps with no networking, on-device validation is the fallback. Be paranoid: build OpenSSL as a static library, hardcode the bundle ID + version (don't read from Info.plist — too easy to swap), validate against the Apple Root CA but don't check certificate expiry (check transaction dates).
- Receipt `type 5` = SHA-1 hash of (bundleID + device ID + opaque value type 4). Validate to prove the receipt is for _this_ app on _this_ device.

## Server-to-Server Notifications (705)

- Set a notifications URL in App Store Connect; Apple POSTs renewal events.
- Notification types you'll receive: INITIAL_BUY, CANCEL, RENEWAL, INTERACTIVE_RENEWAL, DID_CHANGE_RENEWAL_PREF, DID_CHANGE_RENEWAL_STATUS, DID_FAIL_TO_RENEW, DID_RECOVER, RENEWAL_FROM_BILLING_RETRY.
- **HIDDEN GEM**: `DID_RECOVER` fires when a billing-retry succeeds — close the loop on involuntary churn instantly without the user re-launching your app.
- Combine with status polling for the cases where the user accesses your service via web (no app launch to refresh receipt).

## The Billing Retry Service (705)

- Apple now auto-retries failed renewals for **up to 60 days** (was 24 hours). 12M subscriptions recovered in year one.
- Receipt fields: `is_in_billing_retry_period`, `expiration_intent` (1 = voluntary cancel, 2 = billing issue, etc.).
- **BEST PRACTICE**: implement a **grace period**. If the receipt shows `is_in_billing_retry_period = 1` and `expires_date` is past, give the user up to 7 days of continued access while Apple retries. Combine with in-app messaging: "There's a billing issue with your subscription — update payment to continue."

## Voluntary Churn Reduction (705)

- Status-poll once per subscription period (start or end) to catch `auto_renew_status = 0` early.
- When you detect "user will churn next period," show an in-app save offer: cross-grade to a different tier, offer a discount, link to subscription management.
- New direct deep-links to App Store sheets: payment-method update and subscription-management URLs (announced for shortly after WWDC).

## Sandbox Improvements (704)

- iOS 12 separates the **Sandbox account** from the production iTunes/App Store account. No more sign-out-and-back-in dance to test purchases.
- Switch in Settings → iTunes & App Store → Sandbox Account.
- Auto-renew acceleration in Sandbox: 1 year-real = 1 hour-Sandbox; monthly = 5 minutes; etc.
- Sandbox limits to 5 auto-renews then stops (simulates "user disabled subscription").

## Ratings & Reviews (704)

- `SKStoreReviewController.requestReview()` continues to be rate-limited by the system (≤3 prompts per 365 days).
- New: `requestReview()` is now available on **macOS** (Mojave), aligned with iOS API.
- Deep-link with `action=write-review` URL parameter to land users directly on the App Store's "Write a Review" sheet (ideal for app menu items where the user has explicitly asked).

## App Store Connect API (303)

- New REST API replacing iTunes Connect. Full automation of:
  - App metadata, localizations, build management, TestFlight, in-app purchase setup.
  - Sales/Trends data export — daily JSON for ingestion into your own warehouses.
  - Subscription analytics (Billing Retry monitoring, retention dashboards).
- Authentication via JWT signed with App Store Connect API keys.

## Search Ads (304)

- Search Ads Basic (introduced 2017) is the no-budget-required entry point.
- Cost-per-install bidding; max 50/day install caps.
- Performance reporting integrated with App Store Connect API in 2018.

## Business Chat (232)

- Customer-service chat between consumers and businesses inside Messages.
- iMessage Apps + Apple Pay for transactions in-thread.
- Apple-curated business directory; suggested-response and intent-classification by Apple's NLP.
- Use case: scheduling, support, retail returns. Shipping with Marriott, Discover, Hilton, T-Mobile at launch.

## Wallet & Apple Pay (720)

- New PKAddPassButton styles.
- Multi-installment summary items in `PKPaymentRequest`.
- Maestro added as a `PKPaymentNetwork` for European market.
- Apple Pay for the Web continues to expand; in-store contactless transit cards on iPhone in more cities.

## Cross-references

- Notification settings deep links: 710.
- Core Data + iCloud sync (background renewal of subscription state across devices): see also 224 for general best practices.
- App Thinning + on-demand resources for the now-larger 200 MB cellular limit: 227.
