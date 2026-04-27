# Search APIs & Universal Links — WWDC 2015 Analysis

**Sessions covered:** 709 (Introducing Search APIs), 509 (Seamless Linking to Your App), 504 (Introducing Safari View Controller), 511 (Safari Extensibility: Content Blocking and Shared Links), 107 (What's New in Cocoa Touch — Search, App Links overview)

## Headline

iOS 9 introduces **search of in-app content** for the first time. Three complementary APIs:

1. **NSUserActivity** (extended from iOS 8 Handoff) — index activities the user has done.
2. **Core Spotlight** — explicit, database-style indexing of items.
3. **Web markup** — Apple's AppleBot crawler indexes your website's deep links into a public cloud index.

Plus **Universal Links** — `https://` URLs that open your app instead of Safari, replacing custom URL schemes for the first time as Apple's preferred app-to-app navigation mechanism.

## NSUserActivity (709)

The same `NSUserActivity` you used for Handoff in iOS 8 now has search-relevant properties:

- `isEligibleForHandoff` (default true) — disable if not appropriate.
- `isEligibleForSearch` (default false) — opt-in for on-device indexing.
- `isEligibleForPublicIndexing` (default false) — opt-in for cloud aggregation.
- `expirationDate` — drop from the index after this date.
- `webpageURL` — if set, taps in Spotlight can open in Safari OR your app via Universal Links.
- `keywords` — additional search terms.
- `contentAttributeSet` — assign a `CSSearchableItemAttributeSet` for rich result rendering (thumbnail, description).

Mark the activity as the user's current state by calling `becomeCurrent()`. The system indexes it.

When the user taps the result, your app receives `application(_:continue:userActivity:restorationHandler:)` (same delegate method as Handoff) — the activity carries the userInfo dictionary you packed.

### Public Indexing — the privacy-preserving design (709, 703)

`isEligibleForPublicIndexing = true` does NOT immediately ship the activity to Apple. Instead:

1. Each device that engages with the result hashes the activity and sends only the hash.
2. Apple's cloud index counts hashes.
3. Only after a threshold of distinct devices have hashed identical activity contents does Apple fetch the actual content.

This is a **zero-knowledge proof** design: an activity accidentally marked public but with private content (e.g., one user's bank balance) never reaches Apple's servers because no two users would hash the same value.

## Core Spotlight (709)

Database-style API for explicit indexing of items. Used by built-in Mail, Notes, Messages, Calendar.

- `CSSearchableItem(uniqueIdentifier:domainIdentifier:attributeSet:)` — the unit of indexing.
- `CSSearchableItemAttributeSet(itemContentType:)` — describe the item with title, contentDescription, thumbnailData, contentURL, etc.
- `CSSearchableIndex.default().indexSearchableItems([item], completionHandler:)` — index.
- Update by re-indexing the same `uniqueIdentifier`.
- Delete: by identifier, by domain identifier, or all.

When the user taps a result, your app gets `continueUserActivity` with `activityType == CSSearchableItemActionType` and the unique identifier in `userInfo[CSSearchableItemActivityIdentifier]`.

**HIDDEN GEM**: Set the data protection class on the index to match the underlying data — this is derivative data and inherits the same sensitivity. Without this, you can leak protected data through the search index.

**HIDDEN GEM**: When the user deletes content in your app, you must explicitly remove it from the Core Spotlight index. The index is NOT automatically synchronized with your data store.

## Web Markup & AppleBot (709)

If your app mirrors content on a website, AppleBot crawls it.

- Use **Smart App Banner** (`<meta name="apple-itunes-app" content="app-id=...,app-argument=URL">`) to declare the deep link for each page. The most popular convention.
- Twitter Cards and Facebook App Links also supported.
- Add **structured data** (Open Graph, schema.org via microdata, RDFa, or JSON-LD) for rich results: AggregateRating, Offer/price, Recipe, ImageObject, Organization.
- Mark up Actions (telephone, address, audio playback) for actionable result buttons.

Crawled content can be returned in search results to users **who do not have your app installed**. Tapping a result opens Safari with a Smart App Banner inviting installation. **HIDDEN GEM**: this is a totally new app discovery channel.

## Ranking — what makes results bubble up (709)

Three signals:
1. URL popularity (web markup) — schema-described ratings, position in the link graph.
2. Frequency of views inside the app — captured ONLY through `NSUserActivity`. Even if you primarily use Core Spotlight, you should ALSO emit user activities so this signal gets recorded.
3. Engagement with search results (tap-throughs and dwell, plus "silent engagement" when the user reads the description and is satisfied).

Anti-spam: low engagement-to-shown ratio causes Apple to down-rank or suppress your results.

**HIDDEN GEM**: The system measures the time from tap-to-content-shown and uses it as a ranking factor. Don't put up loading screens or interstitials between the result tap and the destination view — go straight to the content. The "fast tap-through" wins ranking battles.

**BEST PRACTICE**: provide thumbnail, well-structured description, ratings (if applicable), and synonyms/abbreviations as keywords ("sf giants" should match "San Francisco Giants").

## Universal Links (509, 107)

Apple's replacement for custom URL schemes. An `https://yourdomain.com/path` URL can open your app directly when tapped from Mail, Messages, etc., without bouncing through Safari.

### Server side

1. Create `apple-app-site-association` JSON file:
```json
{
  "applinks": {
    "apps": [],
    "details": {
      "TEAMID.com.example.MyApp": {
        "paths": ["/articles/*", "/users/*", "NOT /admin/*"]
      }
    }
  }
}
```
2. Sign with `openssl smime` using your SSL certificate (iOS 8). **As of iOS 9 seed 2, signing is no longer required** — just upload the unsigned JSON. **HIDDEN GEM**: keep signing for iOS 8 backwards compat; iOS 9 doesn't care either way.
3. Host at `https://yourdomain.com/apple-app-site-association` over HTTPS.

Note: each domain (`example.com` vs `www.example.com`) needs its own file.

### Client side

1. Add `applinks:yourdomain.com` to the **Associated Domains** entitlement (Capabilities tab).
2. Implement `application(_:continue:userActivity:restorationHandler:)`.
3. Check `userActivity.activityType == NSUserActivityTypeBrowsingWeb`, get `webpageURL`, parse with `NSURLComponents`.
4. **CRITICAL BEST PRACTICE**: validate input. If you can't handle the URL, fall back to `UIApplication.shared.open(url)` — which will route to Safari since you've now declined the link. NEVER leave the user staring at a blank view controller.

### Why universal links beat custom URL schemes

- Custom URL schemes have no enforcement — two apps can claim the same scheme and the user gets the wrong one.
- Custom URL schemes have no fallback when the app isn't installed.
- Custom URL schemes can be used to detect installed apps (privacy leak) — see `canOpenURL` changes below.
- Universal links are universal: the same URL works in your app, in Safari, on Mac, on web.
- Universal links don't require a third-party redirector — no Branch.io–style intermediary needed.

## canOpenURL Whitelist (703, 107)

Apple's iOS 9 privacy change: `canOpenURL:` now requires you to declare schemes in `LSApplicationQueriesSchemes` in your Info.plist.

- Schemes you declare: `canOpenURL` returns true if any installed app handles them, false otherwise.
- Schemes you don't declare: `canOpenURL` ALWAYS returns false.
- Apps linked PRIOR to iOS 9 get a transition allowance of 50 distinct URL schemes; the 51st returns false. Not reset on reboot.

This is a **URGENT** change. Detection of installed apps via probing is now sandbox-blocked. Move to extensions and Universal Links instead.

## Safari View Controller (504)

Replaces the in-app browser. `SFSafariViewController(url:)`, set delegate, present.

- Runs **out of process** — your app cannot see the user's typing, passwords, cookies, or browsing.
- Shares cookies with Safari — if the user is logged into a site in Safari, they're logged in here too. **HIDDEN GEM**: this transforms the OAuth flow. The user often doesn't have to log in at all.
- Shares iCloud Keychain passwords for autofill — user names and passwords come for free.
- Includes Reader, Content Blockers, AutoFill of credit cards and contacts, and your custom share sheet activities.
- Customizable tint color (lets users see they're inside YOUR app).
- For OAuth flows: present `SFSafariViewController`, let the redirect URL hit your app via Universal Links (or your custom URL scheme), inspect the response in `application(_:open:options:)`, dismiss the controller. Replaces the entire in-app login web view pattern.

**BEST PRACTICE**: Stop building in-app web browsers. The "Don't write your own SFSafariViewController" mantra became Apple's official line for years to come.

## Content Blockers (511, 107)

iOS finally gets ad/content blocking — but in a privacy-respecting way.

- Content Blocker Extension is a new app extension type. It returns a JSON list of rules to Safari **once**, ahead of time. Safari compiles it into bytecode for fast evaluation.
- The extension never sees what URL the user visits — Safari evaluates the rules itself. Privacy-by-design.
- Rule format: array of `{action: {type, selector?}, trigger: {url-filter, resource-type, load-type, if-domain, unless-domain}}`.
- Action types: `block` (don't load resource), `block-cookies`, `css-display-none` (hide element via selector), `make-https`, `ignore-previous-rules`.
- Trigger filters: regex against URL, resource types (script, image, style-sheet, raw, svg-document, media, popup, font), load type (first-party, third-party).
- Apply to both Safari AND any app using SFSafariViewController. **DOCS MISS THIS**: a user with a content blocker installed will have it apply to your in-app web views automatically.
- `SFContentBlockerManager.reloadContentBlocker(withIdentifier:)` to recompile after your app updates the rules dynamically.

The same JSON list also works as the new Mac Safari extension content blocker (deprecating the old `canLoad` callback pattern, which had to consult JS for every load).

## Shared Links Extension (511)

A new extension type that injects content into Safari's Shared Links sidebar.

- Implement an extension that returns `NSExtensionItem` objects describing your shared content (title, description, image, URL).
- Each item must have a stable unique identifier across instantiations.
- Sandboxed by default — you must check Outgoing Connections in capabilities to fetch from the network.

## Cross-references

- All three search APIs work together — for the same content, give them all the SAME unique ID. The system will deduplicate AND consolidate ranking signals (709).
- Universal Links provide the fall-through for `webpageURL` set on a user activity.
- Privacy-preserving public indexing (709) is part of the broader privacy story (703).
