# PhotoKit Migration — WWDC 2014 Analysis

**Sessions covered:** 511 (Introducing the Photos Frameworks)

## Headline

iOS 8 introduces **PhotoKit** — two frameworks (Photos and PhotosUI) that supersede `ALAssetsLibrary`. The Photos framework grants apps **read/write/edit access to the system photo library** (the same library the built-in Photos app uses). The PhotosUI framework hosts **Photo Editing Extensions** that plug into the system Photos app for non-destructive editing.

## Why ALAssetsLibrary Had to Die (session 511)

- ALAssetsLibrary was sandboxed to its own framework's view of the library — couldn't see albums the user created elsewhere, couldn't see moments, couldn't see iCloud Photo Library.
- Read-only mostly. Writing was painful. Editing existing assets was impossible.
- No notification mechanism for external changes (other apps modifying the library).
- The 511 session is unusually direct: when the speaker says "ALAssetsLibrary doesn't provide much of the functionality and features that you'll get with the Photos Framework," the audience APPLAUDS (511).

## The Mental Model — Read-only Models, Change Requests (session 511)

- **All model objects are immutable and thread-safe**: `PHAsset`, `PHAssetCollection`, `PHCollectionList`, `PHFetchResult`. Pass them between threads without locking (511).
- **Mutations go through `PHAssetChangeRequest`, `PHAssetCollectionChangeRequest`, `PHCollectionListChangeRequest`** inside a `PHPhotoLibrary.shared().performChanges { ... }` block. The library applies changes asynchronously, out-of-process (511).
- HIDDEN GEM: this model is shared by HealthKit (`HKHealthStore.save(_:withCompletion:)`) — Apple's privacy framework reuses the same architectural pattern across both frameworks designed in 2014 (511).

## The Asset Hierarchy (session 511)

- **`PHAsset`** = a photo or video. Properties: creationDate, location, mediaType (`.image`/`.video`), favorite, hidden, pixelWidth/pixelHeight, duration (videos).
- **`PHAssetCollection`** = an ordered group of assets. Subtypes:
  - User albums (created by user or app)
  - Smart albums (Recently Added, Favorites, Selfies, Screenshots, etc.)
  - **Moments** (auto-grouped by time + location)
- **`PHCollectionList`** = a list of asset collections. Subtypes: Folder (user folder containing albums), Moment Year, Moment Cluster (groups of moments).
- HIDDEN GEM: the moments hierarchy IS exposed to apps — you can build your own "year in review" UI by enumerating moment-year collection lists, then their moments, then their assets (511).

## Fetching (session 511)

- **Class methods** on the model classes: `PHAsset.fetchAssets(with: PHFetchOptions())`, `PHAssetCollection.fetchMoments(with:)`, `PHAsset.fetchAssets(in: someAlbum, options:)`.
- Returns **`PHFetchResult`** — array-like, conforms to NSFastEnumeration, has `count` and subscript access, but **lazy**. Backing storage is a list of lightweight asset IDs; full `PHAsset` objects are realized in batches as you access them (511).
- HIDDEN GEM (PERFORMANCE): a fetch result of 100,000 assets does NOT load 100,000 objects. Only the assets you actually touch are realized. iCloud Photo Library can have hundreds of thousands of items; PhotoKit handles it gracefully (511).

## Transient Collections (session 511)

- **`PHAssetCollection.transientAssetCollection(with: [assets])`** creates an in-memory asset collection that doesn't exist in the library. Use cases: a search result, a user multi-selection, a temporary "share these" group.
- HIDDEN GEM: transient collections are interchangeable with library-backed collections — same API. Reuse your "show me a list of assets" view controller for both real albums and search results (511).

## Change Notifications (session 511)

- Register an observer (any object conforming to `PHPhotoLibraryChangeObserver`). Receive `PHChange` objects on a background queue when ANYTHING in the library changes — your app, the Photos app, iCloud Photo Stream, photo sharing, all of it.
- **`PHChange.changeDetails(for: someFetchResult)`** returns `PHFetchResultChangeDetails` with:
  - `removedIndexes`, `insertedIndexes`, `changedIndexes` — IndexSet ready for UICollectionView batch updates.
  - `hasMoves`, `enumerateMoves(_:)` — for assets that changed position.
  - `fetchResultAfterChanges` — the new state of the fetch result (USE THIS, don't keep the old one around).
- Pattern from 511's sample code:
```objc
- (void)photoLibraryDidChange:(PHChange *)change {
    dispatch_async(dispatch_get_main_queue(), ^{
        PHFetchResultChangeDetails *details = [change changeDetailsForFetchResult:self.assets];
        if (details) {
            self.assets = details.fetchResultAfterChanges;
            [self.collectionView performBatchUpdates:^{
                if (details.removedIndexes) [self.collectionView deleteItemsAtIndexPaths:...];
                if (details.insertedIndexes) [self.collectionView insertItemsAtIndexPaths:...];
                if (details.changedIndexes) [self.collectionView reloadItemsAtIndexPaths:...];
            } completion:nil];
        }
    });
}
```
- HIDDEN GEM: change notifications fire even for **secondary effects** of your own changes. Unfavoriting an asset triggers a removal from the Favorites smart album — you didn't request that explicitly, but the change comes through with full detail (511).

## Image and Video Loading (session 511)

- **`PHImageManager.default()`** abstracts the per-asset cached resolutions Photos maintains. Don't request "the original" unless you need to — request a target size and content mode, get back the most appropriate cached representation.
- **`requestImage(for: asset, targetSize: CGSize(160, 160), contentMode: .aspectFill, options: nil) { image, info in ... }`**.
- HIDDEN GEM: the result handler may be called **multiple times**. First with a fast low-res thumbnail (so the UI shows something), THEN with the full-quality result. Check `info[PHImageResultIsDegradedKey]` to know which (511).
- HIDDEN GEM: with iCloud Photo Library, the asset may not be local. Set `options.networkAccessAllowed = true` to authorize network fetch; provide `options.progressHandler` to surface download progress (511).
- For videos: `requestPlayerItem(for:options:resultHandler:)` for AVPlayer playback, or `requestExportSession(for:options:resultHandler:)` for re-encoding/sharing.

## PHCachingImageManager — Scrollable Grids (session 511)

- For grids of thumbnails, manually managing per-cell `PHImageManager` requests doesn't scale. **`PHCachingImageManager`** does it for you.
- Tell it `startCachingImages(for: assets, targetSize:, contentMode:, options:)` for the assets near the visible region; `stopCachingImages(for:)` for assets that scrolled away. The manager pre-fetches in the background and serves cached results synchronously when you eventually request them (511).
- BEST PRACTICE: one `PHCachingImageManager` per scrolling view controller. Different views have different cache windows (511).

## Editing — Non-Destructive (session 511)

- **`PHAsset.requestContentEditingInput(with:options:completionHandler:)`** returns a `PHContentEditingInput` containing:
  - `fullSizeImageURL` (or `audiovisualAsset` for videos)
  - `displaySizeImage` (a smaller representation for editing UI)
  - **`adjustmentData`** — opaque data describing previous edits, if any, by an editor that supports the same `formatIdentifier`.
- Build a `PHContentEditingOutput` from the input. Set:
  - `renderedContentURL` — write your final rendered JPEG here.
  - `adjustmentData = PHAdjustmentData(formatIdentifier: ..., formatVersion: ..., data: ...)` — your edit description (filter parameters, crop rect, adjustment values).
- Save via a change request:
```objc
[[PHPhotoLibrary sharedPhotoLibrary] performChanges:^{
    PHAssetChangeRequest *request = [PHAssetChangeRequest changeRequestForAsset:asset];
    request.contentEditingOutput = output;
} completionHandler:^(BOOL success, NSError *error) { ... }];
```

## The Adjustment Data Roundtrip (session 511)

- When the user re-opens an asset for editing, `requestContentEditingInput` calls back to your `PHContentEditingController.canHandle(_ adjustmentData:)`.
- If you return `true` (you understand this format identifier and version), you receive the **base image + adjustment data** — you can show the user editing parameters as if they hadn't left the editor. They can change a crop, undo a filter, anything (511).
- If you return `false` (you don't recognize the format — perhaps from a different vendor), you receive **the rendered image** plus an empty adjustment chain. The user can still edit, but the previous edit becomes baked-in; they can't go back without reverting to original.
- HIDDEN GEM: multiple vendors can agree on a shared `formatIdentifier` (e.g., "com.adobe.lightroom.adjustments-v1") — users can edit in Lightroom on iPhone, switch to Lightroom Mobile on iPad, and the adjustment chain travels (511).

## Photo Editing Extensions (session 511)

- A **photo editing extension** is invoked from inside the system Photos app — user taps Edit, then taps the extensions icon, picks your extension. Your extension VC slides up; user edits; user taps Done.
- Subclass `UIViewController` and conform to **`PHContentEditingController`**:
  - `canHandle(adjustmentData:)` — return whether you understand a previous edit's data.
  - `startContentEditing(with:placeholderImage:)` — the input has arrived; show your UI.
  - `finishContentEditing(completionHandler:)` — user tapped Done; produce your `PHContentEditingOutput` and call the handler.
  - `cancelContentEditing()` — user tapped Cancel; clean up.
- HIDDEN GEM: changes saved via the extension are visible system-wide AND across iCloud Photo Library devices. Edit a photo on iPhone, see the new version on iPad and Mac (511).

## Authorization (session 511)

- **`PHPhotoLibrary.requestAuthorization(_:)`** is the standard prompt. Returns `.authorized`, `.denied`, `.restricted`, `.notDetermined`.
- BEST PRACTICE: check authorization status before calling fetch APIs; if denied, show informative UI explaining why your app needs photos access. Don't crash or show empty UI silently.
- The 715 (User Privacy) session reinforces this — check `authorizationStatus()`, request only when you have a clear use, and configure a Privacy Policy URL.

## Best Practices

- **One `PHCachingImageManager` per scrolling view controller** (511).
- **Always observe library changes** if your app shows a fetched result over time — otherwise stale UI.
- **Use the smaller of `targetSize` and your displayed size** — wasting pixels burns RAM and CPU on JPEG decode (511).
- **Handle the `info[PHImageResultIsDegradedKey] == 1` case** — your handler will fire twice; don't allocate a heavy data structure twice (511).
- **Prefer transient collections for ephemeral selections** — don't pollute the library with throwaway albums.
- **Use `formatIdentifier` versioning aggressively** — rev the version when your adjustment data changes shape, even subtly. Old versions can fall back to "I can't handle this" gracefully (511).

## Hidden Gems

- HIDDEN GEM: deletes through PhotoKit prompt the user for confirmation OUT OF PROCESS — you don't write the alert, the system does. The app can't fake or skip the confirmation. **Privacy-by-default**: even your trusted app can't accidentally erase a memory (511).
- HIDDEN GEM: `PHAsset.canPerform(.properties)`, `.canPerform(.content)`, `.canPerform(.delete)` etc. let you check edit capability before requesting. iCloud Photo Stream items are non-editable; check first (511).
- HIDDEN GEM: `PHAssetChangeRequest.placeholderForCreatedAsset` returns a placeholder you can immediately add to a new collection in the same change block. Out-of-process the asset doesn't exist yet, but the framework wires up the relationships once it's saved (511).
- WARNING: never assume your fetch result is current. The library is shared with the built-in Photos app, iCloud Photo Stream, photo sharing, and other apps. Re-fetch or use change observers (511).
- PERFORMANCE: PhotoKit fetch results are O(1) creation regardless of library size. The 511 talk demonstrates 100,000+ asset fetches that don't block (511).

## Cross-references

- **App Extensions (205, 217)** — Photo Editing Extensions are an extension type; the architecture overlaps.
- **HealthKit (203)** — same read-only-model + change-request pattern, designed in parallel.
- **Camera Capture: Manual Controls (508)** — capturing photos to feed into PhotoKit; manual exposure/focus is new in iOS 8.
- **Privacy (715)** — PhotoKit-using apps must handle the photos privacy prompt and ideally configure a Privacy Policy URL.
- **iCloud Photo Library** — the cloud-synced photo storage that PhotoKit transparently surfaces. Apps don't have to know whether data is local or remote.

## Migration Guidance

- **From `ALAssetsLibrary`**: this is a major rewrite. The mental models differ substantially. Plan a 2-4 week migration for a non-trivial app. Strategy:
  1. Replace asset enumeration with `PHAsset.fetchAssets(with:)` returning a `PHFetchResult`.
  2. Replace per-asset thumbnail loading with `PHImageManager` requests (single asset) or `PHCachingImageManager` (scroll view).
  3. Adopt `PHPhotoLibraryChangeObserver` immediately — without it, your app's view of the library becomes stale invisibly.
  4. Migrate any "save edited image" code to the change request + adjustment data pattern. Non-destructive editing is now the standard; users will notice if your app is destructive when alternatives aren't.
- **For Photo Editing Extension developers**: this is brand-new territory. Read 511's sample code carefully. Get the format-identifier+version contract right — your users will edit, abandon the edit, return weeks later, and expect to resume.
