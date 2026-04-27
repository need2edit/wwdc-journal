# CloudKit Debut — WWDC 2014 Analysis

**Sessions covered:** 208 (Introducing CloudKit), 231 (Advanced CloudKit)

## Headline

CloudKit is iOS 8 / OS X Yosemite's **direct API to Apple's iCloud servers** — a Backend-as-a-Service Apple already uses internally for iCloud Drive and iCloud Photo Library. Public + private databases, structured records + bulk asset storage, push subscriptions, query support, free quota that scales with your app's user base. NO local persistence — CloudKit is purely a transport.

## The Mental Model (sessions 208, 231)

- **`CKContainer`** — your app's silo on iCloud. Default 1:1 with your app, but many-to-many is supported (one app talks to multiple containers; one container shared across multiple apps from your team) (208).
- **Two databases per container**: **public** (one shared dataset for all users of your app) and **private** (per-user — your view shows only the currently-logged-in iCloud user's database) (208).
- **You as the developer have NO access to anyone's private database** — not even your own users'. Apple enforces this at the iCloud server. Private data is private (208).
- **`CKRecord`** — a key-value bag with a record type (string), record ID, change tag, creation/modification metadata. Supported value types: `NSString`, `NSNumber`, `NSData`, `NSDate`, `CLLocation`, `CKReference`, `CKAsset`, and homogeneous arrays of any of the above (208).
- **Just-in-time schema** in development. Save a record with new fields; the server creates schema entries automatically. **Promote dev → prod in iCloud Dashboard before shipping** to lock the schema (231).
- **`CKReference`** — a typed pointer to another record, with optional `referenceAction = .deleteSelf` for cascading deletes. **Prefer back references** (child points to parent) to avoid update-bottleneck on a single records that holds an array of children (231).
- **`CKAsset`** — opaque large-file storage tied to a record. You hand a `fileURL`; the framework handles efficient diff upload/download. Server garbage-collects assets when their owning record is deleted (208).

## The API Levels — Convenience vs Operation (sessions 208, 231)

**Convenience API**: simple, single-record at a time. `database.fetch(withRecordID:completionHandler:)`, `database.save(record:completionHandler:)`. Use to get started; covers most simple cases.

**Operation API**: batch, fine-grained control, NSOperation-based. `CKFetchRecordsOperation`, `CKModifyRecordsOperation`, `CKQueryOperation`, `CKModifySubscriptionsOperation`, etc.

- HIDDEN GEM: operations support **NSOperation dependencies** — chain a fetch → modify → save and let GCD plumb the data flow. But use operation-specific completion blocks (e.g. `fetchRecordsCompletionBlock`), NOT `NSOperation.completionBlock`, because those fire asynchronously and lose the dependency ordering (231).
- HIDDEN GEM: `desiredKeys` on fetch/query operations lets you pull a partial record — only the keys you care about. Save bandwidth on big records (231).

## Custom Zones (session 231)

- The **default zone** in any database is fine for most use cases. Custom zones unlock advanced features:
  - **Atomic commits** — a batch save in a custom zone is all-or-nothing (only in private database; public can't lock).
  - **Delta downloads** — `CKFetchRecordChangesOperation` returns only what changed since your stored `CKServerChangeToken`. Implements offline cache cleanly.
  - **Zone subscriptions** — push notification fires whenever ANYTHING in the zone changes. Perfect trigger to do a delta download.
- **Constraint**: you cannot move records between zones (copy-and-delete required), no cross-zone delete-self references (231).

## Querying (session 208)

- `CKQuery` = recordType + `NSPredicate` + optional sort descriptors.
- Supported predicates: equality, ordering, `CKLocationSortDescriptor` for distance from a `CLLocation`, **token-based search** (e.g. `"selfTokens CONTAINS 'wwdc'"`), and `AND` compounds.
- Queries run server-side and return live `CKRecord` instances you can mutate and save back.
- WARNING: queries are POLLS. They're appropriate for one-shot "show top-10 nearest parties on launch" but TERRIBLE for "keep this list current" — that's what subscriptions are for (208).

## Subscriptions and Push (sessions 208, 231)

- **`CKSubscription`** = recordType + predicate + `CKNotificationInfo` (alert string, sound, badge). Save it to the server; server runs the query after every record save and pushes when matches change.
- Pushes flow via APNs and look like normal push notifications. Parse with `CKNotification(fromRemoteNotificationDictionary:)` to extract the affected record ID, change type, etc. (208).
- WARNING: APNs **only stores ONE pending push per client per app**. If your phone is offline and 10 subscription matches happen, you get only the most recent push — the others are lost (231).
- **THE FIX: notification collection.** Every push the server sends is also recorded in a notification collection. Whenever your app receives a push, **also fetch from the notification collection** to recover anything you missed: `CKFetchNotificationChangesOperation` with your stored `CKServerChangeToken` (231).
- HIDDEN GEM: notifications can be **marked read** via `CKMarkNotificationsReadOperation`. After the user has dealt with a subscription firing on one device, the next push on another device tells the other clients to tear down their UI for that notification (231).

## Locked vs Unlocked Saves (session 231)

- **Locked save (default, `CKRecordSaveIfServerRecordUnchanged`)**: includes the record's change tag. Server rejects with `CKErrorServerRecordChanged` if the version on the server has changed since you fetched.
- **Unlocked saves (`CKRecordSaveChangedKeys`, `CKRecordSaveAllKeys`)**: force the change. SaveChangedKeys writes only modified keys; SaveAllKeys writes everything in the record.
- **Conflict handling**: `CKErrorServerRecordChanged` returns three records in `userInfo`: the client record, the original record (the version you started from), and the server record (the latest). **Apply your local changes to the server record, then retry the save** (231).
- BEST PRACTICE: use the default locked save unless you have highly contentious updates in the public database where conflicts would dominate. Unlocked saves can corrupt records by combining changes from clients that don't know about each other's edits (231).
- HIDDEN GEM: **partial records work for saves too**. Fetch only the keys you'll modify (`desiredKeys: ["score"]`), update them, save back. The locked save still verifies the change tag is current — your one-key save is safe even if the server has other unrelated changes you didn't fetch (231).

## User Identity (session 208)

- **`CKContainer.fetchUserRecordID(completionHandler:)`** returns a stable, container-scoped record ID for the logged-in iCloud user. Same ID every time your app runs, on any device. Different ID for different apps (privacy boundary) (208).
- **The user record** is automatically created in the public database for every user. It's a regular `CKRecord` of type `CKRecordTypeUserRecord` — you can attach key-value metadata to it (favorite color, last-seen-version) and read it back from any device (208).
- **You cannot query user records** — too easy to abuse (find all users named John). Discovery happens through explicit channels.
- **`CKContainer.discoverAllContactUserInfos(completionHandler:)`**: returns user info (record ID, first/last name) for every user in the device's address book who has both your app installed AND opted-in to discoverability — WITHOUT requiring address book access. The CloudKit framework hashes the address book locally and asks the server for matches; only the matched users are returned, only if they opted in. **PRIVACY-PRESERVING SOCIAL DISCOVERY** (208).
- HIDDEN GEM: you can also discover by email (`discoverUserInfo(withEmailAddress:completionHandler:)`) or by record ID. All require the target user to have opted in (208).

## iCloud Dashboard (session 231)

- Web app for managing your CloudKit container: view records, edit schema, set up roles for public-database access control, and **promote dev schema to production**.
- HIDDEN GEM: define **roles** in the dashboard to restrict who can create records of a given type in the public database. Default lets any authenticated user create; you can restrict create-permissions to a "PartyAdmin" role and add specific user record IDs to that role (231).
- WARNING: in dev, the server creates indexes on every key automatically (so you can query freely). In prod, **drop unused indexes** to reclaim storage — your app's database scales with your user count, and unnecessary indexes get expensive (231).

## Best Practices

- **Handle errors EVERYWHERE**. CloudKit talks over the network; anything can fail. Apple repeats this multiple times in 208 and 231: "the difference between a working app and a non-working app, not the difference between a good app and a great app." (208, 231)
- **Retry on `CKErrorServiceUnavailable` after `userInfo[CKErrorRetryAfterKey]` seconds**. Don't spin (231).
- **Use back references (child → parent) instead of forward references (parent → array of children)** — avoids contention on the parent record (231).
- **Map CKRecords to your own model objects** — don't subclass `CKRecord`. CloudKit is transport, not your model (231).
- **Always check the notification collection on push receipt** — pushes can be coalesced or dropped (231).

## Hidden Gems

- HIDDEN GEM: `CKModifyRecordsOperation` with `savePolicy = .ifServerRecordUnchanged` AND `atomic = true` (in custom zones, private database) gives you transactional semantics — all records save or none do (231).
- HIDDEN GEM: assets are **content-addressed** — if you upload a file you've previously uploaded, the server reuses the existing blob. Saves bandwidth on duplicate user uploads automatically (231).
- HIDDEN GEM: the `CKReference.referenceAction = .deleteSelf` cascade is one-direction — only deletes the record holding the reference when the target is deleted, not the other way. Build your relationship arrows accordingly (231).
- PERFORMANCE: CloudKit pushes have CloudKit-specific data attached (record ID, change type) parsed by `CKNotification(fromRemoteNotificationDictionary:)` — don't roll your own parsing (208).
- WARNING: the public database default permissions are **world-readable, creator-writable**. If your app stores anything sensitive in the public database, configure roles in iCloud Dashboard. Otherwise it leaks (231).

## Cross-references

- **HealthKit (203)** uses an internal data store (NOT CloudKit). Health data is too sensitive even for the iCloud private database. iCloud Health sync arrives later.
- **App Extensions (205)** can use CloudKit — your share extension can write to your container's public database directly.
- **iCloud Drive** and **iCloud Photo Library** are built ON CloudKit — Apple ate its own dogfood (208).
- **Core Data (225)** can be paired with CloudKit, but the integration in 2014 is manual (you write the bridge). NSPersistentCloudKitContainer is years away (2019).

## Migration Guidance

- **From iCloud Documents**: if you were using `NSFileManager` URLs in iCloud, CloudKit's not a drop-in replacement — different mental model. iCloud Documents is for replacement-semantics document storage; CloudKit is for merge-semantics structured data.
- **From iCloud Core Data**: CloudKit replaces iCloud Core Data for many cases. Apple deprecates iCloud Core Data over the next few years. If you started a Core Data + iCloud sync in 2013, plan a CloudKit migration.
- **From parse.com / Firebase / your own server**: if you don't need cross-platform reach, CloudKit's free tier is generous and the integration is much simpler. Apple-only apps targeting iOS 8+ have a strong case for CloudKit.
