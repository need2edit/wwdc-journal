# App Store, StoreKit & Business (2022)

WWDC22 brought App Analytics peer-group benchmarking, in-app events, custom product pages, family sharing for IAP, more StoreKit 2 features, and Swift Playgrounds 4 enabling app development directly on iPad.

## Sessions covered
- WWDC22-10007 — What's new with in-app purchase
- WWDC22-10039 — What's new in StoreKit testing
- WWDC22-10040 — Explore in-app purchase integration and migration
- WWDC22-10043 — What's new in App Store Connect
- WWDC22-10044 — Discover Benchmarks in App Analytics
- WWDC22-110404 — Implement proactive in-app purchase restore
- WWDC22-110345 — Explore Family Sharing for in-app purchases
- WWDC22-110347 — Get started with in-app events
- WWDC22-110350 — Manage auto-renewable subscription pricing in App Store Connect
- WWDC22-110352 — Do more with less data
- WWDC22-110353 — Meet high-performance MapKit JS
- WWDC22-110335 — Explore Apple Business Essentials
- WWDC22-110348 — Build your first app in Swift Playgrounds
- WWDC22-110349 — Create engaging content for Swift Playgrounds
- WWDC22-10002 — Create macOS or Linux virtual machines
- WWDC22-10046 — Adopt declarative device management
- WWDC22-10045 — What's new in managing Apple devices
- WWDC22-10053 — Discover Sign in with Apple at Work & School
- WWDC22-10143 — Discover Managed Device Attestation

## App Analytics Benchmarking (10044)

The headline feature: **peer-group benchmarking** for App Store apps.

### What you get
For every key metric, see your app's percentile within a peer group of similar apps:
- **Conversion rate** — how often App Store viewers download.
- **Day 1, Day 7, Day 28 retention** — how engaging your app is.
- **Crash rate** — relative reliability.
- **Average proceeds per paying user** — monetization efficiency.

The dashboard shows your app's position alongside the 25th, 50th, and 75th percentiles of your peer group — so you know whether you have growth opportunity or whether you're already crushing it.

### Privacy: differential privacy
Apple uses differential privacy to compute these benchmarks. Each data point in the peer-group aggregate has small noise added, and peer groups are large enough that membership cannot be inferred. **This means individual app performance is never revealed** — Apple guarantees aggregate insights without competitive exposure.

### Peer group composition
Apple groups apps by:
- **App Store category** (e.g., Travel).
- **Monetization type** (Free, Freemium, Paid, Paidmium, Subscription).

Each attribute is tested for meaningful comparison stability over time.

### Action paths
Use benchmarks to inform App Store optimizations:
- **Low conversion** → Product Page Optimization (A/B test icons/screenshots/previews), Custom Product Pages.
- **Low retention** → In-App Events (timely promotions in the App Store), App Clips for low-friction trial.
- **Low monetization** → New pricing tiers, Promoted In-App Purchases.

## StoreKit 2 advances (10007, 10039, 10040, 110404)

- **Server-to-server notifications V2** — richer payloads, deduplicated events.
- **Promotional offers** with signed metadata for verification.
- **`Transaction.currentEntitlements`** — atomic snapshot of all current paid entitlements.
- **`Transaction.unfinished`** — work through pending transactions.
- **`AppStore.sync()`** — manually trigger a refresh from the App Store.
- **`Subscription.subscriptionRenewalInfo`** — full lifecycle visibility (signed JWS).
- **Proactive restore** (110404) — detect entitlements before the user explicitly asks. Greatly reduces "Where did my purchase go?" support tickets.

### StoreKit testing
- **Configure subscription pricing in `.storekit` files.**
- **Local-only subscription scenarios** — test renewals, expirations, billing retries.
- **Test grace periods** without waiting in real time.

## Family Sharing for IAP (110345)
- **Non-consumable** purchases and **non-renewing subscriptions** can now be shared with Family Sharing members.
- Use `Transaction.ownershipType` to detect family-shared vs. originally-purchased entitlements.
- Display family-share badge in your UI for transparency.
- Family Sharing is not available for consumable IAPs.

## In-App Events (110347)
A new App Store surface — promote timely events (game competitions, livestreams, premieres) directly on your product page. Up to 10 events per app, each with images/videos, scheduled times, and deep links into your app.

## Custom Product Pages (110343, 10043)
Multiple App Store product pages for the same app, each with custom icons/screenshots/previews. Use them for:
- Different audiences (e.g., kids vs. adults).
- Different feature emphasis (e.g., a feature tied to a campaign).
- Localization-specific layouts beyond just translated text.

Tied to URLs you can use in your marketing — each visit attributes to that custom page.

## App Store Connect API (10043)
- **REST API for IAP management**, app submissions, TestFlight management.
- **Power and Performance API** for fetching aggregated metrics programmatically.
- Use in CI/CD to automate releases and monitor crashes/hangs.

## Swift Playgrounds 4 (110348, 110349)
- Build complete iOS apps directly on iPad.
- Submit to App Store from iPad.
- New project templates and SwiftUI integration.
- For educators: 110349 covers building learning content.

## Virtual machines on macOS (10002)
The new `Virtualization` framework lets you spin up macOS or Linux VMs from your Mac app:
- macOS guest support (Apple silicon Macs only) since macOS Monterey, expanded in Ventura.
- Linux guests (any Mac).
- GPU acceleration via virtio-gpu.
- Networking, shared folders, clipboard.

Used by ParaVirtual, by CI services, and by tools like Tart for ephemeral build environments.

## Device management (10045, 10046, 10143)
- **Declarative Device Management** continues maturing — devices push state changes to MDM servers proactively rather than being polled.
- **Managed Device Attestation** — cryptographically prove device identity and integrity to MDM and SSO.
- **Sign in with Apple at Work & School** — managed accounts.

## Best practices
- **BEST PRACTICE**: Use App Store benchmarks to focus optimization effort — knowing whether your conversion rate is bottom-quartile vs. top-quartile completely changes priorities.
- **BEST PRACTICE**: Implement proactive in-app purchase restore (110404) — dramatically cuts support ticket volume.
- **BEST PRACTICE**: Use `Transaction.ownershipType` to display family-share badges so users understand their access.
- **BEST PRACTICE**: Custom Product Pages let you target different audiences without forking your app — combine with deep-link campaigns.
- **HIDDEN GEM**: Differential privacy in benchmarks means you can't infer competitor performance — Apple guarantees this mathematically. Other platforms reveal much more.
- **HIDDEN GEM**: In-App Events show on your App Store product page even when the user hasn't installed the app — great for re-engagement and discovery.
- **HIDDEN GEM**: Swift Playgrounds 4 can build and submit complete iOS apps from iPad — the iPad is now a real development platform.
- **HIDDEN GEM**: Virtualization framework on Apple silicon supports macOS guest VMs — perfect for CI build environments without Docker.
- **DEPRECATION**: Older StoreKit 1 patterns (PaymentTransactionObserver) should be migrated to StoreKit 2's async/await API.

## Cross-references
- App Analytics benchmarks pair with the Hangs report in the Xcode Organizer (10082) for full quality+monetization picture.
- StoreKit 2 builds on Swift Concurrency (110354).
- Custom Product Pages tie into App Clips (10097) and deep linking.
