# Search APIs & Spotlight — WWDC 2016 Analysis

**Sessions covered:** 223 (Making the Most of Search APIs)

## Headline

Spotlight in iOS 10 becomes the universal search interface — accessible from Notification Center, the Lock Screen, plus the home screen swipe. Three Search APIs (Core Spotlight, NSUserActivity, Universal Links + web markup) unify with new features: **Continue Search in App** for handing off to your custom search UI, **Core Spotlight Search API** so apps can use the same on-device index they already feed for in-app search, **Differential-privacy-driven deep-link popularity** for ranking, and **app-icon promotion** via search continuation.

## The three Search APIs (refresher)

| API | Where data lives | Use for |
|-----|-----------------|---------|
| **Core Spotlight** | On-device, file-protected | Private user data, favorites, downloaded content, anything you don't want to expose publicly |
| **NSUserActivity** (eligible-for-search) | On-device app-history index | "Things the user has actually viewed in your app" — recall pattern |
| **Universal Links + Web Markup** | Apple's server-side index | Public web content with an in-app counterpart — discovery for users who don't have your app yet |

Use all three together. Set `relatedUniqueIdentifier` on `NSUserActivity` to point to the matching CSSearchableItem; set both to use the same `URL` as the matching web page. Spotlight de-duplicates and aggregates ranking signals across the three.

## NEW: Continue Search in App (HIDDEN GEM)

When your app returns enough search results for a query, Spotlight shows a "Search in [Your App]" affordance. Tapping launches your app with the query — perfect for apps with their own customized search UI.

Adoption — two steps:

1. Add a key to Info.plist:
```xml
<key>CoreSpotlightContinuation</key>
<true/>
```

2. Handle a new activity type in `application(_:continue:restorationHandler:)`:
```swift
if userActivity.activityType == CSQueryContinuationActionType {
    let query = userActivity.userInfo?[CSSearchQueryString] as? String
    presentSearchUI(with: query ?? "")
    return true
}
```

**BEST PRACTICE:** Make your search behavior consistent with Spotlight's prefix-match style — users learn one search behavior across iOS. If you can't, take them to a completion UI rather than zero-results.

## NEW: Core Spotlight Search API

The same index you've been feeding (via `CSSearchableIndex`) is now a fully-queryable corpus for use **inside your app**. No need to maintain a separate search index. Apple's Mail, Messages, Notes apps use this internally.

```swift
let escapedQuery = query.replacingOccurrences(of: "\"", with: "\\\"")
let queryString = "**=\"\(escapedQuery)*\"cdwt"   // case-insensitive, diacritic-insensitive, word-match, tokenized
let csQuery = CSSearchQuery(queryString: queryString,
                            attributes: ["displayName", "contentDescription"])
csQuery.foundItemsHandler = { items in
    // batch of CSSearchableItem with requested attributes pre-populated
}
csQuery.completionHandler = { error in
    // called once
}
csQuery.start()
```

Query syntax:
- `**` matches across content + metadata.
- Comparators `==`, `!=`, `<`, `>`, `<=`, `>=`.
- Boolean: AND, OR, NOT.
- Flags after the closing quote: **`c`** case-insensitive, **`d`** diacritic-insensitive, **`w`** word-match, **`t`** tokenize the query into separate words.

**HIDDEN GEM:** Because the index is shared, you store data **once** and use it for both system search AND in-app search. Mail's full-text search for emails uses exactly this.

**HIDDEN GEM:** Wrap CSSearchableItem in a "lazy picture" pattern that uses the query-returned attributes when present and falls back to your DB only when needed — minimizes database load during search.

## Indexing best practices

### CSSearchableIndex with batching

```swift
let index = CSSearchableIndex(name: "userMessages")
index.beginBatch()
index.indexSearchableItems(items, completionHandler: nil)  // ignore in batch mode
index.endBatch(withClientState: stateData) { error in
    // saved with the batch
}
```

Use **client state** (an opaque `Data` token you store with the batch) to track indexing progress without your own DB transactions. On next launch, fetch the client state back, compare against your DB, and replay only the deltas needed:

```swift
index.fetchLastClientState { state, error in
    let lastSeq = decodeSequence(state)
    let pendingItems = myDB.itemsWithSequenceGreater(than: lastSeq)
    indexBatchAndAdvance(pendingItems)
}
```

### Implement a CSSearchableIndexDelegate

Implement `searchableIndex(_:reindexAllSearchableItemsWithAcknowledgementHandler:)` and `searchableIndex(_:reindexSearchableItemsWithIdentifiers:acknowledgementHandler:)`. Spotlight reaches out when:
- App reinstalled, restored from backup, content needs re-indexing.
- Items hit their `expirationDate` — Spotlight pings you to refresh.

**Always call the acknowledgmentHandler** ONLY after your last indexing completion fires. Premature calls = you don't get re-pinged later. Late calls = Spotlight stays out of sync.

### CSSearchableIndexExtension (NEW)

A separate non-UI extension that can index even when your app isn't running. Same protocol as the in-app delegate. Critical for apps that need to recover index state after a backup restore without forcing a launch.

### Performance

- Always run indexing on a background queue.
- Batch items (10+ items per call reduces IPC overhead by 10×).
- Use expiration dates to prune stale items automatically.
- Use background fetch / silent remote notifications to refresh the index without UI.

## NSUserActivity for app history

Add `eligibleForSearch = true` and `eligibleForPublicIndexing = true` (if the activity represents public content) to make activities searchable.

NEW in iOS 10:
- **`weakRelatedUniqueIdentifier`** lets you bind the activity to a CSSearchableItem **that doesn't exist yet** — useful when the user might later mark something as favorite. The strong `relatedUniqueIdentifier` insists the searchable item exists at write-time and would delete the activity otherwise.
- **`domainIdentifier`** on NSUserActivity (and CSSearchableItemAttributeSet) lets you bulk-delete activities like you can searchable items.

## Universal Links + web markup (server-side index)

Apple's web crawler (Applebot) walks your website (after you allow it via robots.txt) and indexes content. Universal Links you've configured for your app + Schema.org/Open Graph markup on those pages = the Spotlight server-side index for your domain.

NEW in 2016: the validation tool at `search.developer.apple.com` now **visualizes** your indexed result — title, description, thumbnail, action buttons — exactly as it'll appear in Spotlight. Helps catch missing/wrong markup.

Supported Schema.org types: Article, Book, Restaurant, Movie, Recipe, Event, Person, Product, Organization, Place, plus more. **Always set `interactionCount` and `aggregateRating`** — they're powerful ranking signals.

## Ranking signals (HIDDEN GEM)

Spotlight ranks results by:

1. **Engagement ratio (3 flavors):**
   - Per-device engagement (your app's results that THIS user has selected before)
   - Per-query engagement (across all users who saw your result for that query, who clicked)
   - Global engagement (across all users for your app)

2. **Content popularity:**
   - For Universal Links: Apple's web-graph reputation
   - For NSUserActivity: how often the user views this item personally
   - For NSUserActivity + Universal Links + public-indexing-eligible: **differential-privacy-derived global popularity** of the deep link across the iOS user base

**You don't get penalized** if your results never appear (under the keyboard, never seen). Don't keyword-stuff to game appearance — it tanks engagement ratios and Spotlight ranks you lower.

## Best practices summary

- Use all three Search APIs together; link items via `relatedUniqueIdentifier` / shared URL / shared `domainIdentifier`.
- Continue-Search-in-App is one Info.plist key + one delegate method. Add it.
- Use Core Spotlight Search API for in-app search — single index, no duplication.
- Provide great thumbnails, titles, descriptions, ratings — they directly improve ranking.
- Set `expirationDate` on time-bound content (event tickets, reservations) — auto-cleans the index.
- Deep-link directly into content; no interstitials between Spotlight and the destination.
- Always call the index delegate's acknowledgmentHandler exactly when you finish.

## Hidden gems summary

- The Core Spotlight on-device index is a fully-featured query engine — single source of truth for in-app search too.
- Differential-privacy-derived deep-link popularity is a free ranking boost for popular content in your app.
- Schema.org markup on your website auto-populates Spotlight on iOS — no app code needed.
- The `weakRelatedUniqueIdentifier` lets you pre-index activities for content not yet created.
- Spotlight Search API supports complex predicates (range, AND/OR/NOT) — usable as a general query engine.
- `CSSearchableIndexExtension` indexes even when your app isn't running — disaster recovery.

## Cross-references

- Differential privacy → analysis-2016/privacy-differential.md
- NSUserActivity for proactive surfaces → analysis-2016/maps-transit-extensions.md
- Schema.org for Maps location promotion → analysis-2016/maps-transit-extensions.md
