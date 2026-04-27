# Apple Pay on the Web + Extensions + watchOS — WWDC 2016 Analysis

**Sessions covered:** 703 (Apple Pay on the Web), 704 (What's New with Wallet and Apple Pay)

## Headline

Apple Pay leaves the iOS app silo and gets **everywhere**:
- **Safari on iOS 10 and macOS Sierra** — JavaScript API for any merchant website. Confirm payments on iPhone or Apple Watch via Continuity.
- **iMessage extensions, SiriKit intents, Maps ride-sharing extensions** — all support Apple Pay via the new `PKPaymentAuthorizationController`.
- **WatchKit apps** — same `PKPaymentAuthorizationController`, simplified UI, double-side-button confirmation.

Plus a **Sandbox testing environment** so developers can finally end-to-end test Apple Pay with real-data flow on real devices using fake test cards.

## Apple Pay on the Web — the architecture

The web flow is mostly identical to the in-app PassKit flow with one extra step: **merchant validation**.

```
User taps Buy with Apple Pay button
   ↓
JavaScript creates ApplePaySession(version: 1, paymentRequest)
   ↓
session.begin()  → System shows Apple Pay sheet (loading state)
   ↓
session.onvalidatemerchant(event)
   ↓ event.validationURL
Server: POST validationURL with your session certificate
   ↓ JSON merchant session
session.completeMerchantValidation(session)
   ↓
User authorizes (Touch ID on iPhone, double-tap on Watch)
   ↓
session.onpaymentauthorized(event)
   ↓ event.payment.token (encrypted card data)
Server: forward token to payment processor (Stripe, Braintree, …)
   ↓
session.completePayment(STATUS_SUCCESS)
```

## The merchant validation step (NEW concept)

In an iOS app, Apple Pay's security ties to your signed binary's entitlements. The web has no entitlements, so each Apple Pay session requires a fresh `merchant session` token issued per-payment, scoped to your registered domain.

Setup once:
1. At developer.apple.com, create a Merchant ID + Merchant Certificate.
2. Register your fully-qualified domain (e.g. `store.example.com`); Apple validates by requesting a known file path.
3. Receive an Apple Pay Session Certificate (TLS cert) tied to that domain.

Per payment:
1. Browser → your JS calls `session.begin()`.
2. Browser fires `onvalidatemerchant(event)` with `event.validationURL`.
3. Your JS sends `event.validationURL` to your server (don't validate from the client — your session cert must stay secret).
4. Server makes a TLS-mutual-auth POST to that URL using your session certificate.
5. Apple returns an opaque session token JSON.
6. Server returns it to the browser; JS calls `session.completeMerchantValidation(merchantSession)`.

**HIDDEN GEM:** The validation URL varies by region (Apple servers are geo-distributed). Always read the URL from the event — do not hardcode. If your firewall blocks outbound traffic, request the IP allowlist from developer.apple.com.

## ApplePaySession JS API

```javascript
const request = {
    countryCode: 'US',
    currencyCode: 'USD',
    supportedNetworks: ['visa', 'masterCard', 'amex'],
    merchantCapabilities: ['supports3DS'],
    total: { label: 'Acme Corp', amount: '99.99' },
    requiredShippingContactFields: ['postalAddress', 'name', 'phone', 'email']
};

const session = new ApplePaySession(1, request);

session.onvalidatemerchant = async event => {
    const ms = await fetch('/apple-pay/validate', {
        method: 'POST', body: JSON.stringify({ validationURL: event.validationURL })
    }).then(r => r.json());
    session.completeMerchantValidation(ms);
};

session.onpaymentauthorized = async event => {
    const result = await chargeProcessor(event.payment.token);
    session.completePayment(result.success
        ? ApplePaySession.STATUS_SUCCESS
        : ApplePaySession.STATUS_FAILURE);
};

session.begin();
```

## Detection — show the button only when payable

```javascript
if (window.ApplePaySession) {
    if (ApplePaySession.canMakePayments()) {
        // Device supports Apple Pay (has Secure Element, or watch/phone for Mac)
        showApplePayButton();
    }
    ApplePaySession.canMakePaymentsWithActiveCard(merchantId).then(can => {
        if (can) preferApplePayInCheckout();
    });
}
```

`canMakePayments()` is sync, only checks hardware. `canMakePaymentsWithActiveCard()` is async, validates against your merchant ID AND checks the user has a card provisioned.

## Browser security restrictions (HIDDEN GEM)

Several validations happen at `new ApplePaySession()` and `.begin()` time. They throw JavaScript exceptions:
- **Page must be HTTPS.** Period. No data: URLs, no localhost (unless using web inspector).
- **`begin()` must be called from a user-gesture event handler.** No timers, no async cascades.
- **Only one sheet can be active at a time.**
- **Property names must match the spec exactly** — typos throw. Use the Web Inspector Error Console to debug.

Use **`<link rel="apple-touch-icon">`** in your HTML — this is the icon that appears at the top of the iPhone Apple Pay sheet when paying from a Mac via Continuity. Spec sizes: 180px and 120px.

## Web design recommendations

- Place the **Apple Pay button on product pages** — not just the cart. Conversion rates increase dramatically when Apple Pay is the early-checkout option (StubHub, Warby Parker, Lululemon are case studies).
- Use the new `-webkit-named-image(apple-pay-logo-black)` CSS for the button — system-rendered, will get future visual updates automatically.
- **Don't suppress the Apple Pay button** in countries/regions where Apple Pay works — it's a guideline violation.
- After a successful payment, leverage the Apple Pay-collected email to **offer optional account creation** (pre-fill the field). Don't block guest checkout.

## Apple Pay in extensions (NEW for iOS 10)

Previously, Apple Pay needed a presenting `UIViewController`. The new **`PKPaymentAuthorizationController`** (note: not -ViewController) is non-UI-tied — works in any extension context: iMessage extensions, SiriKit intents extensions, Maps ride-sharing extensions, even watchOS apps.

Same API on watchOS and iOS — share your payment-handling code. Apple's sample app `Emporium` demonstrates the pattern with a single payment model class consumed by phone, watch, and extensions.

## Wallet PassKit updates

- **App icons can be placed on passes** (since iOS 9.3). Tap → deep link into your app for top-up, flight rebook, etc. Add `appLaunchURL` and `associatedStoreIdentifiers` to the pass.
- **Value-added services passes** (NFC tap-to-redeem loyalty cards) — sign with a special VAS certificate (request via developer.apple.com/contact/passkit). Supported by Verifone, Ingenico terminals.
- **In-app card provisioning** — `PKPassLibrary.signData(_:withSecureElementPass:completion:)` lets card-issuing apps add cards to Apple Pay without leaving the app or opening Wallet. Discover was the launch partner.
- **In-store experience promotion** — present your stored Apple Pay card directly from your retail/coupon app via `PKPassLibrary.openPaymentSetup()`. Pair with a coupon redemption for a single-tap pay flow.
- **`PKPaymentButton` styles** — use `.inStore`, `.donate` (NEW), `.book`, `.subscribe`, etc. for consistent branding.

## Dynamic networks (HIDDEN GEM — fixes a 2-year pain point)

Previously, your app had to hardcode supported card networks. Adding Discover required a re-shipped binary.

```swift
// New in iOS 10:
PKPaymentRequest.availableNetworks()  // dynamic list of all networks supported on this device

// New: payment processor proxies
request.supportedNetworks = paymentProcessor.supportedNetworks  // your processor's list
```

Some payment processor SDKs participate in this dynamic-network mechanism. New networks (e.g. bank cards added to Apple Pay later) automatically work without re-shipping your app.

## Apple Pay Sandbox (URGENT new test capability)

A separate Apple Pay environment for end-to-end testing on real devices.

Setup:
1. Create a sandbox iCloud account at iTunes Connect (you may already have one for IAP testing).
2. Sign into iCloud with that account on a real iOS device.
3. If your account region doesn't support Apple Pay (e.g. you're outside the US/UK/CA/etc.), change the account region to a supported one.
4. Add test cards published at developer.apple.com to Wallet — they look like real provisioning.
5. Pay with these test cards in your apps and websites — you get **real-format payment data** flowing through your stack, not the simulator's dummy values.

The environment switch is implicit on iCloud login (no developer toggle). Apple Pay on the web initially works ONLY in the Sandbox.

The Sandbox supports Visa, MasterCard, American Express. China UnionPay and others coming.

## Best practices summary

- **Always validate merchants on the server** — never embed your session certificate in client JS.
- **Never start charging until `completePayment(STATUS_SUCCESS)`** — only then is the user committed.
- **Do not suppress the Apple Pay button.** Place it next to other payment methods.
- **Pre-validate with `canMakePaymentsWithActiveCard`** before showing the button on a product page — graceful degradation.
- **For account creation**, leverage the email-from-Apple-Pay to create accounts post-purchase — don't block guest checkout.

## Hidden gems summary

- Validation URL is region-specific — read from the event, never hardcode.
- `canMakePaymentsWithActiveCard` does a real network round-trip against your merchant ID — cache the result for the session.
- `<link rel="apple-touch-icon">` shows your icon on the iPhone Apple Pay confirmation sheet (Continuity).
- The new `PKPaymentAuthorizationController` is non-UIViewController — works in iMessage extensions, SiriKit, Maps, watchOS, anywhere.
- Dynamic supported networks via processor proxy fixes the year-of-Discover-rollout pain.
- Sandbox cards live alongside production cards on the same device — region change is the toggle.
- Apple Pay buttons on product pages outperform cart-only placements for conversion (Lululemon/StubHub data).

## Cross-references

- iMessage extension Apple Pay → analysis-2016/imessage-apps-stickers.md
- SiriKit ride-sharing intent + Apple Pay → analysis-2016/sirikit-debut.md
- Wallet pass updates → cross-reference for PassKit improvements (also covered above)
