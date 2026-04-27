# Core Data, CloudKit & Storage — WWDC 2015 Analysis

**Sessions covered:** 220 (What's New in Core Data), 704 (What's New in CloudKit), 710 (CloudKit JS and Web Services), 715 (CloudKit Tips and Tricks), 223 (Introducing the Contacts Framework for iOS and OS X), 234 (Building Document Based Apps), 224 (App Extension Best Practices)

## Headline

Core Data gets unique constraints (finally — no more dedup), batch deletes (operate directly on the store), and model caching (no more "couldn't find source model"). CloudKit launches **Web Services**: Apple-hosted Sign in with Apple ID, full JSON+HTTPS API, JS library, web-only iCloud accounts (1GB free). The Contacts framework replaces 30-year-old AddressBook.

## Core Data (220)

### Unique constraints

Mark one or more entity attributes as **unique** in the model editor. Core Data enforces uniqueness across all instances at the persistence layer.

- Replaces hand-written "find or create" logic that's racy across multiple ingestion sources.
- For inheritance: subentities inherit parent's unique constraints AND can add their own.
- Best for values that don't change after creation (UUID, email, part number).
- Conflicting saves throw merge conflicts that you resolve via merge policies.

**HIDDEN GEM**: combine with `NSManagedObjectContext.mergePolicy = NSMergeByPropertyObjectTrumpMergePolicy` to make ingestion idempotent. Re-ingesting the same data updates rather than duplicates.

### NSBatchDeleteRequest

Operate on the persistent store directly. No object materialization, no memory pressure, blazing fast.

- Configure result type: `.resultTypeStatusOnly`, `.resultTypeCount`, `.resultTypeObjectIDs`.
- **WARNING**: changes are NOT reflected in your context. No validation runs. No object notifications fire. You must manually merge the deleted IDs into your context (`NSManagedObjectContext.mergeChanges(fromRemoteContextSave:into:)`) or refresh objects.
- Relationships are nullified or cascade-deleted as your model specifies.

### Other improvements

- `NSManagedObject.hasPersistentChangedValues` — true only if differs from persistent store (vs. `hasChanges` which is just a dirty flag).
- `objectIDs(forRelationshipNamed:)` — get IDs without materializing, then batch-fetch in chunks.
- `NSManagedObjectContext.refreshAllObjects()` — refresh while preserving unsaved changes; fixes retain cycles from bidirectional traversals.
- `NSManagedObjectContext.shouldDeleteInaccessibleFaults = true` — mark unloadable faults as deleted instead of crashing with the dreaded "Could not load fault" exception. **HIDDEN GEM**: this single property prevents one of the top Core Data crash categories.
- `mergeChanges(fromRemoteContextSave:into:)` — propagate save notifications across multiple coordinators.

### Persistent store management

- `NSPersistentStoreCoordinator.destroyPersistentStore(at:)` — properly closes and deletes a store, honoring locking. **DOCS MISS THIS**: prior to iOS 9, developers bypassed Core Data and `rm`-ed the SQLite file directly, leaving stale file descriptors open.
- `replacePersistentStore(at:withPersistentStoreFrom:)` — atomic replace.

### Model caching

- The MOM is cached into the SQLite store on creation/migration. Lightweight migrations can find the source model from the cache when you forgot to copy the previous .xcdatamodel into the bundle. **HIDDEN GEM**: ends the "I forgot to ship my old model" deployment disaster.
- SQLite stores only. Heavyweight migrations still need explicit source model.

### Subclass generation changes

- Xcode 7 generates a separate **extension/category** file containing the Core Data declarations, alongside YOUR header+implementation. Update model → only the extension file regenerates. Your code is untouched.
- Generated subclasses use generics (`NSSet<Person>`) and `nullability` annotations.

### Concurrency

- `confinementConcurrencyType` (formerly the default) is **deprecated**. `init()` is also deprecated.
- Always use `init(concurrencyType: .privateQueueConcurrencyType)` or `.mainQueueConcurrencyType` and `perform`/`performAndWait` blocks.

### Performance audit (220)

Three patterns to look for in Core Data Instruments:

1. **Relationship faults** — Use `relationshipKeyPathsForPrefetching` on your `NSFetchRequest`. Saved 9 queries down to 1 in the Recipes demo.
2. **Slow fetches** — set `fetchBatchSize` so objects are paged in lazily as cells become visible. 30,000 rows that won't even launch reduces to scrollable.
3. **SQL profiling** — pass `-com.apple.CoreData.SQLDebug 1` to print queries. Use `EXPLAIN QUERY PLAN` to find scans, then add a compound index in the model. **HIDDEN GEM**: indices come from the model's property inspector — don't roll your own.

## CloudKit (704)

### Pricing model

Public database is the developer's storage; private database comes from the user's iCloud quota.

Free tier scales with users:
- **Asset storage**: 10GB + 250MB per active user, up to 1PB.
- **Database storage**: 100MB + 2.5MB per user, up to 10TB.
- **Data transfer**: 2GB + 50MB per user per month, up to 200TB/month.
- **Database requests/second**: 40 + 10 per 100K users, up to 400/sec.
- Push notifications: free, no limit.

Beyond free: $0.03/GB-month asset storage, $3/GB-month database, $0.10/GB transfer, $100/10 RPS extra.

The 2015 demo went to 4 million users — still free if your per-user usage stays at the average. Above that, charges apply.

### CloudKit Dashboard

New Usage tab on developer.apple.com/cloudkit. Daily and monthly rollups for users, RPS, asset storage, database storage. Red line shows free quota; yellow line shows actual usage. Forecasts for the current month based on prior trend.

## CloudKit JS / Web Services (704, 710)

A first-class JavaScript SDK for the same CloudKit container that backs your iOS/macOS app.

- Same record model (records, references, assets, queries, subscriptions, push).
- Web Sign-in with Apple ID (sandboxed iframe, Apple-hosted, dev never sees credentials).
- iCloud "web-only" accounts: 1GB private storage. Upgrades to 5GB the moment the user pairs with iOS/macOS.
- Same public storage budget across all clients.
- A native iOS/macOS app must exist in App Store Connect to enable web access — Web Services extend an iOS app to web, not stand-alone.
- Subscriptions push notifications to the web app via JavaScript callbacks (no need for the user to refresh).

**HIDDEN GEM**: the Notes web app at icloud.com is the canonical CloudKit JS demo — Apple uses CloudKit JS in production for their own apps.

## CloudKit Tips and Tricks (715)

- **Use `CKQueryOperation` rather than `perform(_:inZoneWith:completionHandler:)`** — the convenience method is a wrapper that uses the operation under the hood; the operation lets you set the result limit, desired keys, and chain via cursor.
- For sync of large data: use **custom zones** with `CKFetchRecordChangesOperation`. Custom zones support atomic commits across records.
- Subscriptions are cheaper than polling. CKSubscription with a predicate fires push notifications when matching records change.
- **HIDDEN GEM**: the new `init(zoneID:options:)` includes options like `.fireOnRecordCreation` — combine subscription types to reduce push load.
- Asset uploads/downloads should use `CKModifyRecordsOperation.perRecordProgressBlock` and `perRecordCompletionBlock` for cancellable progress UI.

## Contacts Framework (223)

The 30-year-old C-based AddressBook is replaced by **Contacts.framework** (CN-prefixed, Swift- and Objective-C-friendly).

- `CNContact`, `CNContactStore`, `CNContactFetchRequest`, `CNMutableContact`.
- Predicate-based fetching: `CNContact.predicateForContacts(matchingName:)`.
- New picker UI: `CNContactPickerViewController` and view UI: `CNContactViewController`.
- Authorization model is the same as before (`CNContactStore.requestAccess(for:)`).
- Available on **all** Apple platforms, including watchOS — and the authorization is shared between iPhone app and watch app.

**HIDDEN GEM**: Contacts framework lets you display formatted contact attribution easily — `CNContactFormatter.string(from:style:)` handles all locale-specific name formats.

## Best Practices for Progress Reporting (232)

- `NSProgress` is a tree of progress objects. A parent progress's `fractionCompleted` is computed from its children.
- Implicit binding: `parent.becomeCurrent(withPendingUnitCount: N); doWork(); parent.resignCurrent()` — any progress created during `doWork` becomes a child of the parent.
- Used by `NSBundleResourceRequest`, `NSURLSession` tasks, document save/load.
- Cancel/pause/resume cascade through the tree.
- Localized description: `progress.localizedDescription` returns "5 of 10" formatted per locale.

## App Extension Best Practices (224)

App extensions need to share data with their containing app. Patterns:

### Shared data via App Groups
- Settings → Capabilities → App Groups (extension AND containing app).
- `UserDefaults(suiteName: "group.com.example.app")` — note: this is NOT your standard defaults. The containing app must also use `init(suiteName:)`.
- For Core Data: store the SQLite in `FileManager.default.containerURL(forSecurityApplicationGroupIdentifier:)`.
- For Keychain: shared Keychain access groups via the entitlement; access from anywhere with `kSecAttrAccessGroup`.

### Background URL sessions for extensions
- Extensions are killed aggressively. Background URL sessions survive — the system continues the network task and delivers events to your CONTAINING APP via `application(_:handleEventsForBackgroundURLSession:completionHandler:)`.
- Set `sessionConfiguration.sharedContainerIdentifier` so the system knows where to write the downloaded file.

### Task assertions
- `ProcessInfo.processInfo.performExpiringActivity(withReason:using:)` — ask the system for a brief grace period to do critical work (file save, lock release).
- The completion block is called twice: with `expired = false` initially (do your work), then with `expired = true` when the system needs you to stop.
- If acquired, holds for the duration of your block scope. **WARNING**: don't dispatch_async to another queue inside — execution leaves your block scope. Use `dispatch_sync` to wait synchronously.

### Darwin Notifications
- `CFNotificationCenter.darwinNotifyCenter` — system-wide pubsub between processes (containing app ↔ extension). No payload, just notification names.
- Use to **hint** an extension to refresh its data when the containing app changed something. Not for synchronization (extensions may not be running to receive).

### Today widgets (224)

- `NCWidgetProviding` protocol's `widgetPerformUpdate` is called opportunistically by the system.
- Pass `.newData` to the completion handler if you have new content; `.noData` if not. **HIDDEN GEM**: lying and always returning `.newData` causes the system to wake you more often, hurting battery — be honest.

## Cross-references

- Core Data unique constraints (220) plus CloudKit (704) make idempotent ingestion patterns possible across multiple devices.
- Contacts framework (223) plus Privacy (703) plus watchOS authorization sharing (105) is the new contacts-on-Apple-Watch story.
- App Extension best practices (224) tie together Today widgets, Action/Share extensions, and the new content blocker (511) and shared links (511) extension types.
