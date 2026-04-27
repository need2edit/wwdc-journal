# MapKit, Core Spotlight & Search — WWDC 2017 Analysis

**Sessions covered:** 237 (What's New in MapKit), 231 (What's New in Core Spotlight for iOS and macOS), 247 (Extend Your App's Presence With Sharing), 250 (Extend Your App's Presence with Deep Linking), 246 (Deep Linking on tvOS), 251 (Now Playing and Remote Commands on tvOS)

## Headline

MapKit gains **clustering** (collapse overlapping markers automatically), **customizable map markers** (replacing pin annotations as the iOS 11 default), **improved compass and scale views**, and **indoor maps for venues** that registered with Apple's Indoor Maps Program. Core Spotlight ships **continuation user activities** that bridge search results back into apps — the foundation for the Files app showing your documents in search.

## Map Markers Replace Pins (237)

`MKMarkerAnnotationView` is the new default annotation view — colorful, flexible, accessible.

```swift
let marker = MKMarkerAnnotationView(annotation: annotation, reuseIdentifier: "park")
marker.markerTintColor = .systemGreen
marker.glyphImage = UIImage(systemName: "tree.fill")
// or
marker.glyphText = "🌳"
marker.displayPriority = .defaultHigh   // controls clustering visibility
```

- **HIDDEN GEM**: `displayPriority` (`.required`, `.defaultHigh`, `.defaultLow`) replaces the old "z-index" hack. Markers with higher priority survive when MapKit collides annotations during clustering or zoom-out.

## Annotation Clustering (237)

Built-in:

```swift
let marker = MKMarkerAnnotationView(annotation: annotation, reuseIdentifier: "park")
marker.clusteringIdentifier = "parks"   // any non-nil string opts in
```

Annotations with the same `clusteringIdentifier` are auto-collapsed into a single annotation view at low zoom levels. The cluster annotation gets passed to `mapView(_:viewFor: clusterAnnotation)` — return your own `MKAnnotationView` (typically displaying the count).

- **PERFORMANCE**: clustering happens on a background queue. Re-clustering on pan/zoom no longer locks the main thread (a perennial complaint about MKAnnotation rendering).

## Custom Compass & Scale (237)

- `mapView.compassView` is now a `UIView` you can detach from the map and place anywhere. Required for full-screen maps where the default top-right position is hidden by the safe area.
- `MKScaleView(mapView:)` — drag-and-droppable scale indicator. Style: `.adaptive` (light/dark per map appearance), `.dark`, `.light`.
- **HIDDEN GEM**: detach the compass from the map, place it in a safe-area-respecting position, and rotate the map freely without losing the user's bearing reference.

## Indoor Maps Program (237)

Venues (airports, malls, museums) can now publish floor plans to Apple Maps via the **Indoor Maps Program** (apply at maps.apple.com/business). Once enrolled, MapKit automatically:

- Shows floor plan tiles when the user is inside the venue.
- Floor switcher UI (1F, 2F, etc.) appears in the map.
- Apps that show points of interest get accurate indoor positioning if the venue has installed BLE beacons.

For 2017, the API is invitation-only — Apple wants the data quality high before opening it broadly.

## MapKit JS (mentioned in 237 keynote)

Apple Maps now ships a JavaScript SDK for web embeds. Same look as native MapKit; identical annotation API. Auth via short-lived JWT tokens generated server-side from a developer key.

## Core Spotlight: Continuation Activities (231)

iOS 11 introduces `CSSearchableItem.compact` and `CSCustomAttributeKey` properties for richer search-result rendering, plus continuation user activities:

```swift
let attributes = CSSearchableItemAttributeSet(itemContentType: kUTTypeImage as String)
attributes.title = photo.title
attributes.contentDescription = photo.caption
attributes.thumbnailData = photo.thumbnail.pngData()

let item = CSSearchableItem(uniqueIdentifier: photo.id.uuidString,
                            domainIdentifier: "com.example.photos",
                            attributeSet: attributes)
CSSearchableIndex.default().indexSearchableItems([item])
```

When the user taps a result:

```swift
func application(_ app: UIApplication, continue userActivity: NSUserActivity,
                 restorationHandler: @escaping ([UIUserActivityRestoring]?) -> Void) -> Bool {
    if userActivity.activityType == CSSearchableItemActionType,
       let id = userActivity.userInfo?[CSSearchableItemActivityIdentifier] as? String {
        showPhoto(id: id)
        return true
    }
    return false
}
```

- **HIDDEN GEM**: Spotlight queries can be **continued via `CSQueryContinuationActionType`** — when the user types more in Spotlight after seeing a partial match, the system can re-launch your app with the full query for in-app search. Avoids the "tap result, see app, then re-type query" loop.

## Files-App Spotlight Integration (231)

Adopting `UIDocumentBrowserViewController` (see `files-document-browser.md`) auto-indexes your documents' metadata. To customize:

- Set `CSSearchableItem.contentURL` to the document's location — DBVC uses this to deduplicate entries.
- Index document body text via `attributes.textContent` (up to ~10 MB per item before truncation).
- Spotlight in iOS 11 surfaces results inside Files app search bar in addition to the home-screen Spotlight.

## Sharing Extensions (247)

- `UIActivityItemProvider` and `UIActivityItemSource` let you customize what gets shared per destination. Provide a different payload for Mail (full URL + summary) vs Twitter (just URL).
- New: `UIActivity.ActivityType.openInIBooks` and `.markupAsPDF` for richer integrations.
- **HIDDEN GEM**: `UIActivityItemSource.activityViewController(_:thumbnailImageForActivityType:suggestedSize:)` lets you provide a custom thumbnail per share destination — used by Photos for the share-sheet preview.

## Universal Links Best Practices (250)

- Apple-App-Site-Association file MUST be served over HTTPS at `https://yourdomain.com/.well-known/apple-app-site-association` with `Content-Type: application/json`.
- No comments allowed in the JSON. No `Content-Encoding: gzip` (unless your server transparently inflates).
- Validate with `swcutil dl -d yourdomain.com` from Terminal.
- iOS 11 caches AASA aggressively — debug by uninstalling and reinstalling the app, or use `Settings → Developer → Universal Links` to view the latest cache state.
- **HIDDEN GEM**: prefer `applinks` over `webcredentials` if you only need link routing. Each section has separate caching and entitlement implications.

## tvOS Now Playing & Remote Commands (251)

- `MPNowPlayingInfoCenter.default()` populates the system Now Playing info, the Apple TV remote, and Control Center on iPhone.
- `MPRemoteCommandCenter.shared()` exposes pause/play/skip/seek hooks. Wire each command's `.addTarget { … }` and return `.success`.
- **HIDDEN GEM**: setting `MPNowPlayingInfoPropertyPlaybackRate = 0` while keeping the now-playing info populated keeps your audio session active for lock-screen playback controls — useful for apps with cached audio that pauses without losing the lock-screen UI.

## Cross-references

- See `files-document-browser.md` — Spotlight indexing of documents flows from DBVC adoption.
- See `sirikit-business-chat-imessage.md` — Universal Links pair with iMessage app deep links.
