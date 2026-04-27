# Core Data & Persistence — WWDC 2014 Analysis

**Sessions covered:** 225 (What's New in Core Data), 234 (Building a Document-based App)

## Headline

Core Data in iOS 8 / Yosemite picks up two long-requested features: **Batch Updates** (mass attribute changes that bypass the managed object context) and **Asynchronous Fetching** (non-blocking fetches with progress reporting and cancellation). Plus full **Swift support** with `@NSManaged` properties. **`NSConfinementConcurrencyType` is officially obsolete** — adopt `MainQueueConcurrencyType` or `PrivateQueueConcurrencyType`.

## Batch Updates (session 225)

- **`NSBatchUpdateRequest`** — update many rows in the persistent store WITHOUT loading them into a managed object context.
- The classic problem: marking 200,000 messages as read used to require loading each one into the MOC, setting the flag, and saving. Either you ran out of memory (loading all 200K) or showed a long progress indicator (loading in batches).
- With batch updates, the SQL `UPDATE messages SET read = 1 WHERE mailbox = ?` runs directly against the store. **Sub-second instead of multi-second** (225).
- API:
```objc
NSBatchUpdateRequest *request = [NSBatchUpdateRequest batchUpdateRequestWithEntityName:@"Message"];
request.predicate = [NSPredicate predicateWithFormat:@"mailbox == %@", mailbox];
request.propertiesToUpdate = @{@"read": @YES};
request.resultType = NSUpdatedObjectIDsResultType;
NSBatchUpdateResult *result = [moc executeRequest:request error:&error];
NSArray *changedIDs = result.result;
[changedIDs enumerateObjectsUsingBlock:^(NSManagedObjectID *objectID, ...) {
    [moc refreshObject:[moc objectWithID:objectID] mergeChanges:NO];
}];
```
- WARNING: validation rules **are not run** for batch updates. You can write invalid data to the store (225).
- WARNING: the optimistic-locking version IS bumped per row, so contexts that have those objects loaded WILL see merge conflicts on save. **Set a merge policy** before using batch updates: `moc.mergePolicy = NSMergeByPropertyStoreTrumpMergePolicy` (225).

## Asynchronous Fetching (session 225)

- **`NSAsynchronousFetchRequest`** — wrap an `NSFetchRequest` with a completion block; the fetch runs without blocking the context.
- Returns a `NSAsynchronousFetchResult` immediately (a future). The fetch happens on a private queue inside the persistent store coordinator; the completion block is called on the context's queue with the fully-populated array.
- **Progress reporting** via `NSProgress`: create one on the calling thread before calling `executeRequest:`, set its unit count to 1, become current. Core Data sets up a child NSProgress that reports as the fetch proceeds. Observe the parent's `fractionCompleted` for UI updates (225).
- **Cancellation**: cancel the `NSProgress`. The fetch is interrupted and returns `NSUserCancelledError`.
- WARNING: only works with `MainQueueConcurrencyType` and `PrivateQueueConcurrencyType` contexts. NOT `ConfinementConcurrencyType` (225).

## Concurrency Story — The Definitive Answer (session 225)

- The historical concurrency story for Core Data is messy. Apple uses 225 to formally clarify (225):
  - **`ThreadConfinement` and `NSConfinementConcurrencyType` are obsolete**. Don't use in new code.
  - Use **`MainQueueConcurrencyType`** for the UI context (you can call methods directly when on the main queue).
  - Use **`PrivateQueueConcurrencyType`** for background contexts (always wrap access in `performBlock:` or `performBlockAndWait:`).
- New on `NSPersistentStoreCoordinator`: `performBlock:` and `performBlockAndWait:`. Subclassers should use these; default Core Data already uses them internally (225).
- **Concurrency debugging now built in**: launch your app with `-com.apple.CoreData.ConcurrencyDebug 1` argument. Core Data immediately asserts (with a useful message) when you access a context from the wrong queue. **Available on iOS for the first time in iOS 8** (225).
- HIDDEN GEM: set `NSManagedObjectContext.name` and `NSPersistentStoreCoordinator.name` (any string). Names appear in the LLDB debugger inspector AND in queue-trace output for thread-context debugging (225).

## Custom Persistent Store Requests (session 225)

- The new `NSPersistentStoreRequest` base class for `NSFetchRequest`, `NSSaveChangesRequest`, `NSBatchUpdateRequest`, AND your own subclasses.
- HIDDEN GEM: if you've written an `NSIncrementalStore` subclass (rare but real), you can now define your own request types — useful for batched server APIs that don't fit standard CRUD. Examples: a launch-time request that fetches multiple disjoint object types in one server round trip (225).

## Core Data + Swift (session 225)

- Define managed object subclasses in Swift just like any other class. Use `@NSManaged` instead of `@dynamic`:
```swift
class Message: NSManagedObject {
    @NSManaged var subject: String
    @NSManaged var read: Bool
    @NSManaged var date: Date
    @NSManaged var mailbox: Mailbox
}
```
- HIDDEN GEM: **the data model's "Class" field MUST be the fully-qualified class name** (`MyApp.Message`, not just `Message`). Swift namespaces classes per module; Core Data needs the fully-qualified name to instantiate them (225).
- BEST PRACTICE: define your own typed managed object subclasses. Without them, Swift's type system can't help you — everything is `NSManagedObject` and you key-value-code at runtime. The strict-typing wins are massive (225).

## Document-Based Apps (session 234)

- `UIDocument` (iOS) and `NSDocument` (Mac) get tighter iCloud Drive integration in iOS 8 / Yosemite.
- **NSDocument on Mac** can now move documents in and out of iCloud during their lifetime — KVO-observe `userActivity` on NSDocument to detect the transition.
- **Document Provider Extensions** (covered in App Extensions analysis) plug new file-storage backends — Dropbox, Box, Google Drive — into `UIDocumentPickerViewController`. Document apps that adopt the picker get cloud-storage support for free (234).
- HIDDEN GEM: `UIDocumentPickerViewController(documentTypes: [...], in: .open)` opens a "pick a document from any provider" sheet. Your app receives a security-scoped URL — call `startAccessingSecurityScopedResource()` before reading, `stopAccessingSecurityScopedResource()` when done. The user has explicitly authorized this read; iOS scopes it precisely (234).

## Best Practices

- **Use batch updates for mass attribute changes** — instant performance win; just remember to refresh affected objects (225).
- **Use async fetching for fetches that might be slow** (large datasets, network-backed stores) — UI stays responsive; users get progress; cancellation works (225).
- **Adopt `MainQueueConcurrencyType` for the UI context, `PrivateQueueConcurrencyType` for background work** — confinement is dead (225).
- **Run with `-com.apple.CoreData.ConcurrencyDebug 1` in Debug builds** — catches every cross-queue access at the moment it happens (225).
- **Set `name` on contexts and coordinators** for debuggable queue traces (225).
- **In Swift, write typed `NSManagedObject` subclasses** — type-safety wins back the Swift advantages (225).

## Hidden Gems

- HIDDEN GEM: `NSAsynchronousFetchRequest` enables **fetch-while-the-user-types** patterns. Cancel the previous fetch as the user keystrokes; start a new one. Old approach was custom queues + manual cancellation logic (225).
- HIDDEN GEM: batch updates can use `NSExpression`-based property updates: `request.propertiesToUpdate = @{@"viewCount": [NSExpression expressionWithFormat:@"viewCount + 1"]}` increments without read-modify-write (225).
- HIDDEN GEM: `NSManagedObjectContext.refresh(_:mergeChanges:)` re-faults a managed object — combine with batch updates' returned object IDs to keep your in-memory graph consistent without dropping unrelated cached data (225).
- WARNING: **iCloud Core Data is not deprecated in 2014, but Apple is moving to CloudKit**. New apps should evaluate CloudKit (208) before iCloud Core Data. Existing iCloud Core Data apps continue working but the long-term direction is clear (225).

## Cross-references

- **CloudKit (208)** — the alternative to iCloud Core Data for new apps. Different mental model, different tradeoffs.
- **Swift (402)** + **Swift interop (406)** — Core Data + Swift class definitions; the Bridging Header story applies.
- **Document-Based Apps + Document Provider Extensions (234, 217)** — same iCloud Drive ecosystem.

## Migration Guidance

- **Apps using `NSConfinementConcurrencyType`**: migrate to `MainQueueConcurrencyType` or `PrivateQueueConcurrencyType`. Confinement is dead. The `Asynchronous` and `Batch` features ONLY work on the new types (225).
- **Apps with mass-update operations** (mark all read, mark all favorited, recompute aggregate counts): rewrite using `NSBatchUpdateRequest` for instant perf win. Easy migration; high impact (225).
- **Apps with slow fetches**: rewrite UI-blocking fetches using `NSAsynchronousFetchRequest`. UX win, modest code change (225).
- **Apps using iCloud Core Data**: monitor Apple's direction. Consider CloudKit for new schemas; iCloud Core Data continues working for now but isn't the future (225).
- **Apps with `NSManagedObject` subclasses generated from the data model in Obj-C**: regenerate with Xcode 6's "Create NSManagedObject Subclass" — Swift output is supported (225).
