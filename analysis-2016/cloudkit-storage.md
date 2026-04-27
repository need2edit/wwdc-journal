# CloudKit & Storage — WWDC 2016 Analysis

**Sessions covered:** 226 (What's New with CloudKit), 231 (CloudKit Best Practices), 242 (What's New in Core Data)

## Headline

CloudKit gets a major year — **CKShare** introduces user-to-user record sharing with proper permission model. **Database-level subscriptions** (`CKDatabaseSubscription`) replace ad-hoc per-record-type subscription collections. Server change tokens become the canonical sync mechanism. CloudKit on watchOS 3 ships at parity with iOS.

Core Data gains **concurrent-context support** (no more "must run on this context's queue") and CloudKit-friendly persistent history tracking — laying groundwork for the iOS 13 NSPersistentCloudKitContainer.

## CloudKit conceptual refresher

```
Container (≈ one per app, e.g. iCloud.com.example.notes)
├── Public Database         (all users see same content — news feeds, leaderboards)
├── Private Database        (single user's data, syncs across their devices)
│   └── Default Zone + Custom Zones
└── Shared Database (NEW)   (proxies to other users' shared zones)
    └── Shared Zones
        └── CKRecords
```

Custom zones in private DB enable atomic multi-record changes, server change tokens, and sharing. Default zones do not.

## CKShare — sharing records (HIDDEN GEM)

`CKShare` is a CKRecord subtype representing a sharing relationship over a hierarchy of records.

```swift
// Owner: create a share for a record
let share = CKShare(rootRecord: documentRecord)
share[CKShare.SystemFieldKey.title] = "Q3 Roadmap" as CKRecordValue
share.publicPermission = .none      // .none / .readOnly / .readWrite
share.addParticipant(participant)   // added via CKUserIdentity

let op = CKModifyRecordsOperation(recordsToSave: [documentRecord, share], recordIDsToDelete: nil)
op.modifyRecordsCompletionBlock = { saved, _, error in
    // share.url contains the shareable iCloud link
    let shareURL = share.url!
    // share via UIActivityViewController, Mail, Messages, etc.
}
privateDB.add(op)

// Recipient: open the URL via Universal Link or system handler
func application(_ app: UIApplication, userDidAcceptCloudKitShareWith metadata: CKShare.Metadata) {
    let op = CKAcceptSharesOperation(shareMetadatas: [metadata])
    op.acceptSharesCompletionBlock = { _ in /* refresh shared DB */ }
    container.add(op)
}
```

After acceptance, the recipient sees the shared zone in their **shared database**. They have read or read/write access depending on the share configuration.

`UICloudSharingController` provides built-in UI for share creation, link copying, participant management, and revocation.

## Database subscriptions (NEW pattern)

The recommended sync workflow in iOS 10:

```swift
// Subscribe ONCE per device (idempotent — check a UserDefaults flag)
let subscription = CKDatabaseSubscription(subscriptionID: "shared-changes")
let notificationInfo = CKSubscription.NotificationInfo()
notificationInfo.shouldSendContentAvailable = true   // SILENT push — no user permission needed
subscription.notificationInfo = notificationInfo

let op = CKModifySubscriptionsOperation(subscriptionsToSave: [subscription],
                                         subscriptionIDsToDelete: nil)
op.modifySubscriptionsCompletionBlock = { _, _, error in
    if error == nil { UserDefaults.standard.set(true, forKey: "didSubscribeShared") }
}
op.qualityOfService = .utility
sharedDB.add(op)
```

**HIDDEN GEM:** Silent pushes (`shouldSendContentAvailable = true` only, no alert/badge/sound) **don't require user permission** — they bypass the "Allow notifications?" prompt. Use these for sync, not UI alerts. Then if the user has denied UI notifications, your sync still works.

**HIDDEN GEM (URGENT):** Push delivery is **best-effort with coalescing**. APNs may drop pushes under low battery / bad network, **but guarantees at least one push will arrive eventually.** Treat pushes as "something changed" notifications, not "this changed." Always go fetch.

## Server change tokens — the canonical sync mechanism

CloudKit hands you opaque tokens that mark "where in history" your local cache is. Two-level fetch when handling a push:

```swift
// 1. Fetch zone changes in the database
let dbOp = CKFetchDatabaseChangesOperation(previousServerChangeToken: previousDBToken)
dbOp.fetchAllChanges = true
dbOp.recordZoneWithIDChangedBlock = { changedZones.append($0) }
dbOp.changeTokenUpdatedBlock = { newToken in saveToken(newToken) }
dbOp.fetchDatabaseChangesCompletionBlock = { newToken, _, error in
    saveToken(newToken)
    fetchRecordChanges(in: changedZones)
}

// 2. Fetch record changes in each zone
func fetchRecordChanges(in zones: [CKRecordZone.ID]) {
    let configurations = [zoneID: CKFetchRecordZoneChangesOperation.ZoneConfiguration(
        previousServerChangeToken: tokenForZone(zoneID),
        resultsLimit: nil, desiredKeys: nil
    )]
    let op = CKFetchRecordZoneChangesOperation(recordZoneIDs: zones,
                                                configurationsByRecordZoneID: configurations)
    op.recordChangedBlock = { record in /* store */ }
    op.recordWithIDWasDeletedBlock = { id, _ in /* delete */ }
    op.recordZoneFetchCompletionBlock = { zoneID, newToken, _, _, _ in saveToken(newToken, for: zoneID) }
    sharedDB.add(op)
}
```

Tokens advance only on **fetches** — writes don't advance them. So a device that just wrote and didn't fetch will see its own changes again on the next fetch (the server can't know which devices got the write). **Don't be surprised by this** — check IDs to dedupe.

## CloudKit on watchOS 3

Watch apps gain full CloudKit access including CKShare. Critically, CloudKit operations use NSURLSession underneath, so they **work without iPhone reachability** as long as the watch can reach a known Wi-Fi network. Standalone watch apps can sync directly.

## Pitfalls and best practices

- **Always use operations** (`CKModify…Operation`, `CKFetch…Operation`) over the convenience methods (`fetch`, `save`). Operations support batching, QoS, and cancellation.
- **Set `qualityOfService`** appropriately — `.utility` for sync, `.userInitiated` for user-action-triggered fetches, `.userInteractive` for foreground UI.
- **Set `database.add(op)` rather than `op.start()`** — lets the system manage scheduling and retries.
- **Handle errors carefully**:
  - `CKError.serverRecordChanged` — your client record is stale. Fetch the server's, merge, retry.
  - `CKError.networkFailure` / `CKError.networkUnavailable` — retry with exponential backoff using `userInfo[CKErrorRetryAfterKey]`.
  - `CKError.zoneBusy` / `CKError.requestRateLimited` — wait for `CKErrorRetryAfterKey` seconds.
  - `CKError.partialFailure` — examine `CKErrorPartialErrorsByItemIDKey` for per-record statuses.
  - `CKError.changeTokenExpired` — your token is too old; reset to nil and full-resync.
- **Cache subscription creation** in UserDefaults so you don't re-create on every launch.
- **Use silent pushes** (`shouldSendContentAvailable = true`) for sync — no permission required.

## Core Data with CloudKit (preview of the iOS 13 future)

iOS 10 Core Data lays groundwork:
- **Concurrent contexts** — `NSManagedObjectContext` no longer requires you to be on its queue for read-only operations. `perform`/`performAndWait` for writes.
- **Persistent History Tracking** — opt in via store option `NSPersistentHistoryTrackingKey`. Each context records its writes; other contexts can fetch history and merge.
- **Query generations** — `setQueryGenerationFrom(_:)` pins a context to a snapshot for stable iteration.
- **NSFetchedResultsController.snapshot()** (preview) — bridges to NSDiffableDataSourceSnapshot in iOS 13.

Use the new APIs to begin building syncable Core Data stores; the seamless CloudKit integration arrives in iOS 13's NSPersistentCloudKitContainer.

## Best practices summary

- Subscribe once, idempotent. Check a flag in UserDefaults.
- Use silent pushes for sync — no user permission needed.
- Treat pushes as "something changed" — always fetch with server change token.
- Use operations, not convenience methods.
- Set `qualityOfService` per operation purpose.
- Handle `serverRecordChanged` with merge-and-retry; honor `CKErrorRetryAfterKey`.
- For sharing: use `CKShare`, surface `UICloudSharingController` for UI.
- Adopt persistent history tracking in Core Data now — sets you up for CloudKit integration later.

## Hidden gems summary

- Silent pushes bypass user permission — sync without "Allow Notifications" prompt.
- Push coalescing means pushes are "fire-and-forget signals" — always fetch on receipt.
- `CKShare` URLs are short, shareable iCloud.com links; recipients can accept via tap on iOS or Mac.
- watchOS 3 CloudKit works without iPhone if the watch is on Wi-Fi.
- Server change tokens advance only on fetches — write-only devices will see their own changes back next fetch.
- `CKErrorRetryAfterKey` in error.userInfo is the canonical backoff hint.

## Cross-references

- Notification permission flow → analysis-2016/ios10-notifications.md
- iCloud + Developer ID Mac apps → analysis-2016/cocoa-modern-mac.md (Gatekeeper section, session 706)
