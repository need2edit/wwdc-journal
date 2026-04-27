# StoreKit 2 & App Services (WWDC 2021)

The biggest in-app purchase API rewrite ever, plus iCloud Private Relay, Wallet/Apple Pay, and App Clip light-build improvements.

## Sessions covered
- WWDC21-10114 — Meet StoreKit 2
- WWDC21-10174 — Manage in-app purchases on your server
- WWDC21-10175 — Support customers and handle refunds
- WWDC21-10171 — Meet in-app events on the App Store
- WWDC21-10115 — What's new in App Analytics
- WWDC21-10033 — Meet privacy-preserving ad attribution
- WWDC21-10092 — What's new in Wallet and Apple Pay
- WWDC21-10012 — What's new in App Clips
- WWDC21-10013 — Build light and fast App Clips
- WWDC21-10027 — Explore Safari Web Extension improvements
- WWDC21-10168 — Build Mail app extensions
- WWDC21-10231 — Donate intents and expand your app's presence
- WWDC21-10232 — Meet Shortcuts for macOS
- WWDC21-10084 — Explore UWB-based car keys

## Best practices

- **`Transaction.updates` is an `AsyncSequence` you must subscribe to at app launch** — it surfaces deferred Ask-to-Buy approvals, family-shared purchases that arrive on this device, and cross-device sync (WWDC21-10114).
- **Always call `transaction.finish()` after delivering content** — un-finished transactions re-deliver on every launch (WWDC21-10114).
- **Use `appAccountToken` (UUID)** to tie purchases to your in-app account system. Survives across devices, deletions, family sharing — your server can correlate without the App Store account (WWDC21-10114, WWDC21-10174).
- **`Transaction.currentEntitlements`** is the single API that returns what the user owns RIGHT NOW (active subs + non-consumables). No more receipt parsing for the common case (WWDC21-10114).

## Hidden gems

- StoreKit 2 transactions are **JSON Web Signatures (JWS)** — a web standard. Server-side verification works with any JWS library; you don't need an Apple-specific receipt validator (WWDC21-10114).
- StoreKit 2 **automatically verifies** the JWS for you on-device. The `VerificationResult` enum has `.verified(T)` and `.unverified(T, VerificationError)` — you choose how strict to be (WWDC21-10114).
- Restore purchases is essentially obsolete: `currentEntitlements` returns everything automatically. Only call `AppStore.sync()` in response to a "Restore" button if a user reports something missing (WWDC21-10114).
- The new App Store Server API (`/inApps/v1/transactions/{transactionId}`) returns server-fetched transactions in the same JWS format — your server and client speak the same language now (WWDC21-10174).
- **In-App Events** — discoverable promotional content (movie premieres, in-game tournaments, live streams) that can appear directly on your App Store product page and in Search/Today (WWDC21-10171).
- **iCloud Private Relay** is opt-in for iCloud+ subscribers and rewrites all Safari traffic + non-HTTPS app traffic through two relays. Apps using HTTPS APIs are unaffected; non-HTTPS connections may break (WWDC21-10096).
- App Clips: 10MB binary cap (was 10MB) but new **App Clip Codes** (NFC + visual code combo) enable in-physical-world launches (WWDC21-10012, WWDC21-10013).
- Mail extensions on macOS Monterey: signed, sandboxed, replace the unsigned Mail bundles. Ship through the App Store (WWDC21-10168).
- Safari Web Extensions are now also on **iOS and iPadOS** in Safari 15 — same WebExtension manifest as desktop Safari/Chrome/Firefox (WWDC21-10104, WWDC21-10027).
- UWB-based car keys: passive entry/start using the U1 chip. Three-packet ranging protocol with cryptographic time-bounded scrambled timestamps prevents relay attacks (WWDC21-10084).

## Performance

- StoreKit 2 product fetch is one async call instead of an SKProductsRequest delegate dance: `try await Product.products(for: identifiers)` (WWDC21-10114).

## Migration guidance

- Old StoreKit and StoreKit 2 share the same underlying transaction store — purchases made with one are visible to the other. You can incrementally migrate (WWDC21-10114).
- Existing receipt-based servers continue to work; switch to the App Store Server API when convenient (WWDC21-10174).

## Cross-references

- The App Store Server Notifications V2 (covered in WWDC21-10174) also use JWS — server-to-server consistency.
- For child-account "Ask to Buy", the deferred result is the new `.pending` `PurchaseResult` case — handle via the `Transaction.updates` listener (WWDC21-10114).
