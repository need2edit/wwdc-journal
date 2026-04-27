# App Thinning, Bitcode, On-Demand Resources — WWDC 2015 Analysis

**Sessions covered:** 404 (App Thinning in Xcode), 214 (Introducing On Demand Resources), 102 (Platforms State of the Union — Bitcode introduction), 107 (What's New in Cocoa Touch — slicing, ODR overview)

## Headline

A unified strategy to ship smaller apps and ship them more flexibly. Three pillars:

1. **App Slicing** — App Store generates per-device variants of your IPA, delivering only the architecture, asset scale, and graphics-tier resources that device needs.
2. **Bitcode** — your app uploads as LLVM intermediate representation. Apple can re-optimize and re-compile in the future without you resubmitting.
3. **On-Demand Resources (ODR)** — assets tagged for staged download, hosted by the App Store, paged in/out on demand.

The headline number from the demo: a 74MB universal app sliced down to 16-29MB per device, plus reclaimable ODR space.

## App Slicing (404)

- All resources must live in **asset catalogs** to be sliced — loose files are not thinned. (Exception: name-data assets, see below.)
- Device traits used for slicing: scale (1x/2x/3x), idiom (iPhone/iPad/Watch/TV), graphics capability (Metal generations), and memory class (low/high).
- Slicing happens on Apple's servers from your single uploaded universal IPA. Per-device variants are generated and delivered.
- **NEW asset class**: NSDataAsset stores arbitrary files in an asset catalog with the same trait markup. Use `NSDataAsset(name:)` to retrieve. This makes anything that isn't an image slice-able.
- **NEW asset class**: SpriteKit Atlas — group images via the asset catalog, build-time atlas generation produces sliced texture atlases retrievable as `SKTextureAtlas`.
- **HIDDEN GEM**: Build & Run thins for the active run destination only. New build setting `Enable On Demand Resources` and "Build Active Resources Only" make iterative builds substantially faster on content-heavy apps.
- Asset Catalog source format documented as **XCAssets** — JSON-based contents.json + arbitrary file naming. Designers can run a tool chain (the talk's example: PhotoShop CC generator) that emits XCAssets directly without launching Xcode. Xcode will descend the folder tree and find image sets and data sets at any depth.

## Bitcode

- Compiled into all iOS 9 SDK builds by default; opt-out exists.
- Apple servers can re-compile your bitcode-enabled IPA to take advantage of future CPU optimizations or chip generations.
- **DOCS MISS THIS** (subtle): bitcode means the binary the user installs is NOT byte-identical to what you uploaded. Crash reports continue to symbolicate via dSYM, but you must download the App-Store-provided dSYM (they re-build, they re-symbol) — your build's dSYM is for YOUR copy, not the shipped binary. App Store Connect provides the rebuilt dSYM for download.
- Watch and tvOS apps require bitcode (no opt-out).

## On-Demand Resources (214)

The user model:
- Initial install includes a designated subset (the "Initial Install Tags").
- Other resources download on demand, intelligently cached, evicted when system runs low.
- Total IPA size in App Store: up to 20GB (was 4GB).
- The app's own `.app` bundle: max 2GB.
- Initial + pre-fetched ODR content: max 2GB.
- Maximum ODR in use at any one time by a single app: 2GB.
- Maximum size of one asset pack: 512MB.

Adoption:
1. Add **tag strings** to assets in Xcode. Files can have multiple tags; Xcode creates an asset pack per unique tag combination.
2. In code, `NSBundleResourceRequest(tags: [...])` then `beginAccessingResources(completionHandler:)`.
3. After the completion handler reports success, use the SAME APIs you always have — `UIImage(named:)`, `NSBundle.url(forResource:)`, `NSData(contentsOfURL:)` — they just work because the resources are now on disk.
4. Call `endAccessingResources()` (or let the request object dealloc) to tell the system you're done.

**HIDDEN GEM**: Decoupled request-from-use design means existing resource APIs don't change. You add a request guard and that's it.

**HIDDEN GEM**: `conditionallyBeginAccessingResources(completionHandler:)` returns a Bool indicating whether the resources are already cached on device. Use to opportunistically read content without triggering a download.

**HIDDEN GEM**: `loadingPriority` (0–1, with `loadingPriorityUrgent` constant) hints the system about within-app ordering. `setPreservationPriority(_:forTags:)` per-tag tells the system which content to keep when purging.

**HIDDEN GEM**: There's a new debug gauge in Xcode showing per-tag size and current state (`in use`, `downloaded`, etc.). Watch the state flip when your `endAccessingResources` call lands.

**HIDDEN GEM**: ODR content is hosted by Xcode itself during dev (no need to deploy to TestFlight to test). For ad-hoc/enterprise hosting, ODR content can be served from your own web server, including behind authentication. Xcode Server hosts ODR content automatically for CI builds.

### Three usage patterns (214)

| Pattern | Strategy |
|---|---|
| Random access (browse-anywhere, e.g., travel guide) | Many small tags, request progressively, show progress UI immediately |
| Limited prediction (open-world game) | Many small tags, request as the player approaches; release when they leave |
| Linear progression (level-based game) | Sequential tags, prefetch the next one well ahead of time |

### Performance gotchas (214)

- ODR is network-based. Always test with **Network Link Conditioner** (in Settings → Developer on a tethered device) — your tethered USB connection is unrealistically fast.
- Initial install + prefetched ODR counts toward the 100MB cellular download cap. If you blow past it, your app won't install over cellular.
- Asset pack > 512MB → Xcode warns at build time, App Store rejects at submission.
- When the system needs to purge, it picks based on (1) last-used date, (2) preservation priority you set, (3) running state. Don't tag everything 1.0 — that defeats prioritization.

### Errors to handle (214)

- No network when an asset pack is needed.
- Resource unavailable (server moved/removed for ad-hoc hosting).
- 2GB-in-use limit hit.
- Low local disk space.

## Cellular Data (214)

ODR follows the same per-app cellular toggle. Bandwidth used counts against your app's cellular usage as displayed to the user — minimize.

## Cross-references

- App Slicing depends on asset catalog discipline (404), which connects to Cocoa Touch best practices (231) and design systems.
- ODR's tag system is designed to work alongside slicing — every asset pack is itself sliced for its target device.
- Memory pressure handling (212) becomes more important when multiple apps + ODR caches contend.
