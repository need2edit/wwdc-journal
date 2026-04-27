# Core Data, CloudKit & Storage — WWDC 2019 Analysis

**Sessions covered:** 202 (Using Core Data With CloudKit), 230 (Making Apps with Core Data), 710 (What's New in Apple File Systems), 719 (What's New in File Management and Quick Look), 718 (Introducing Accelerate for Swift)

## Headline

Core Data + CloudKit integration is the marquee feature: `NSPersistentCloudKitContainer` does end-to-end iCloud sync with as little as one line of code change. APFS becomes the default file system across all Apple platforms. Quick Look gets a modern, extensible API.

## NSPersistentCloudKitContainer (202)

**The pitch**: change one class name and your existing Core Data app gets transparent iCloud sync.

```swift
// Before
container = NSPersistentContainer(name: "Model")
// After
container = NSPersistentCloudKitContainer(name: "Model")
```

What you must add:
1. iCloud capability with CloudKit checked.
2. Background Modes capability with Remote notifications.
3. Wrap your model entities in a Configuration named "Cloud" (Xcode model editor).

What it gives you for free:
- Local replica of the entire user's CloudKit private database.
- Automatic scheduling and back-off for cloud operations.
- Robust error recovery.
- Bidirectional NSManagedObject ↔ CKRecord transformation.
- A custom CloudKit zone managed for you.
- Push-driven sync (when your app is in the foreground or via background pushes when registered).

## Multi-Store Strategies (202)

**HIDDEN GEM**: use multiple Configurations to keep some entities **local-only** and others **synced**:

1. In the Xcode model editor, click `+` on Configurations. Create "Cloud" with synced entities and "Local" with local-only entities.
2. Create two `NSPersistentStoreDescription`s pointing at separate `.sqlite` files, assign different configurations.
3. Add both descriptions to `container.persistentStoreDescriptions`.

Common use cases:
- High-frequency telemetry → local store, coalesce, then write summaries to cloud store.
- User input validation that should never sync.
- Cached server responses that don't need cross-device sync.

## Schema Initialization (202)

```swift
try container.initializeCloudKitSchema()
```

Call once during DEV (not in production!) to upload the CloudKit schema based on your `NSManagedObjectModel`. Use the CloudKit Dashboard to migrate that schema to Production when you ship.

## Working with Core Data Effectively (230)

- **`NSFetchedResultsController`** — diff-based UI updates. Modern apps should use it for any list view backed by Core Data. Pairs perfectly with diffable data sources (220) — `NSFetchedResultsController` now has a `snapshot()` method that returns an `NSDiffableDataSourceSnapshot`. **HIDDEN GEM**.
- **Query Generations** (`NSPersistentStoreCoordinator.setQueryGenerationFrom:`) — pin your context to a snapshot of the store. Background sync writes don't perturb the UI mid-render.
- **History Tracking** (`NSPersistentHistoryTransaction`) — when sync writes happen in the background, query history to find what changed and update only relevant UI.
- **Constraint validation** — uniqueness constraints on entity attributes prevent duplicates from sync conflicts.
- **Derived attributes** (new in iOS 13) — Core Data computes derived properties (counts, sums, concatenations) at save time. Indexes them for fast queries. **HIDDEN GEM**: replaces the manual `willSave`/`didSave` denormalization pattern.

## APFS Across Platforms (710)

- APFS is now the default for iOS, iPadOS, tvOS, watchOS, and macOS.
- **Cloning** — `FileManager.default.copyItem(at:to:)` is O(1) and uses zero extra disk on APFS. Use it freely for snapshots, backups, A/B file comparisons.
- **Sparse files** — large files with mostly zero blocks consume only the non-zero space.
- **Snapshots** — Time Machine on Catalina uses APFS snapshots for instant local snapshots.
- **Encryption** — file-system-level encryption on by default.

## Quick Look Modernization (719)

- New `QLPreviewSceneActivationConfiguration` for opening previews from your scenes.
- New `QLPreviewingController` extension API for adding custom Quick Look previewers.
- Quick Look now supports rich annotations, markup, and editing built-in.

## Accelerate for Swift (718)

- The whole Accelerate framework gets a Swift-friendly overlay this year.
- vDSP, vForce, BNNS, BLAS, LAPACK, vImage all wrapped in idiomatic Swift APIs with named labels and value types.
- **PERFORMANCE**: vectorized math operations are 2-10x faster than scalar Swift, especially on Apple Silicon.
- New `vDSP.fft(...)`, `vDSP.convolve(...)` functions.

## File Provider Improvements (Catalina, mentioned in various sessions)

- Replaces "Sync Anywhere" architecture used by Dropbox, Google Drive, OneDrive.
- Cloud storage providers no longer need a kernel extension on macOS.
- File Provider extension runs in user space.

## Cross-references

- Diffable data sources for Core Data: 220 (the snapshot bridge).
- Background tasks for sync: 707.
- Sign In with Apple as the iCloud account model: 706.
