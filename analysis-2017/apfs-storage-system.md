# APFS, Storage & System Frameworks — WWDC 2017 Analysis

**Sessions covered:** 715 (What's New in Apple File System), 706 (Modernizing Grand Central Dispatch Usage), 238 (Writing Energy Efficient Apps), 218 (Choosing the Right Cocoa Container View), 236 (Cocoa Development Tips), 244 (Efficient Interactions with Frameworks), 204 (Updating Your App for iOS 11 — storage notes)

## Headline

**APFS becomes the default file system on the Mac** in High Sierra after shipping silently on every iOS device in iOS 10.3. Snapshots, atomic clones, native encryption, sparse files, and space sharing within a container land on macOS. iOS 11 leverages APFS for iCloud Backup snapshots that no longer fail when files are mid-write. Storage best practices, GCD modernization, and Cocoa container choices round out the operations track.

## APFS Highlights (715)

- **Cloning** — copy a 1 GB file in milliseconds. The new file shares storage with the original via copy-on-write. Modify either; only the changed blocks are duplicated.
- **Snapshots** — atomic, read-only point-in-time views of an entire volume. iCloud Backup uses this to grab a stable file system view without pausing apps.
- **Native encryption** — single-key, multi-key, or per-file. FileVault is now an APFS-native operation, not a CoreStorage layer.
- **Space sharing** — multiple volumes inside one container share free space. No more "Mac HD has 100 GB, MacOS Beta has 0 GB, can't install update" — both volumes draw from one pool.
- **Sparse files** — `seek` past EOF and write doesn't allocate the gap. Saves space and disk bandwidth.
- **PERFORMANCE**: directory enumeration on APFS is dramatically faster than HFS+ for large directories due to B-tree indexing.

## Migration & Compatibility (715)

- macOS High Sierra installer auto-converts the system volume on Solid State Macs. Fusion Drives are NOT auto-converted in 10.13.0 (later updates).
- Disk Utility → "Convert to APFS" lets you upgrade additional volumes manually. **WARNING**: a converted volume becomes its own container; it does NOT share space with other containers. To get space sharing, you must add the volume to an existing container and migrate data.
- **HIDDEN GEM**: cloning works only WITHIN a single APFS container. Files copied across containers (or to an external HFS+ drive) trigger a real copy.

## Unicode Normalization Trap (715)

- Pre-iOS 11, APFS stored filenames as **un-normalized UTF-8**. The Spanish `ñ` could be stored as the single Unicode codepoint U+00F1 OR as `n` + U+0303 (combining tilde) — and they were treated as DIFFERENT files. Cross-process file lookups failed unpredictably.
- iOS 11 introduces **runtime normalization**: the file system normalizes both candidate names and stored names before comparison, so `ñ` always finds the file regardless of source encoding.
- macOS High Sierra case-sensitive APFS volumes get **native** normalization (NFD-only stored, comparisons normalized).
- **WARNING**: if your app stored filenames pre-iOS 11 and later compares them with re-typed user input, you may see lookup misses. Normalize manually with `String.precomposedStringWithCanonicalMapping` before comparison if you're touching filenames you stored before iOS 11.

## iOS Storage Best Practices (204)
<!-- (Storage best practices were covered as part of the iOS 11 update session) -->


- **`FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)`** — for files the user actively created. Backed up.
- **`.applicationSupportDirectory`** — for app-managed data. Backed up.
- **`.cachesDirectory`** — purgeable. Don't store anything you can't re-download.
- **`.libraryDirectory/Caches/com.apple.nsurlsessiond/`** — system-managed download cache. Don't touch.
- **`tmp/`** — temporary scratch. May be purged any time.

iOS 11 storage features:

- `URLResourceKey.isUbiquitousItemKey`, `.ubiquitousItemDownloadingStatusKey`, `.ubiquitousItemDownloadingErrorKey` for iCloud Drive items.
- `URLResourceKey.documentIdentifierKey` provides a stable ID for a file across moves and renames — store this, not the URL, for long-lived references.
- **HIDDEN GEM**: APFS clones are exposed via `FileManager.copyItem(at:to:)` — on APFS, this is now a near-instant operation regardless of source size. Use it freely; you no longer pay the price you used to.

## "Optimize Storage" / Offloaded Apps (204)

- iOS 11 can offload unused apps automatically. The icon stays on the home screen with a cloud badge; tapping re-downloads.
- Your app's documents and data persist across offload. Be ready to find your files exactly where you left them after a re-download.
- App Slicing (iOS 9+) and On-Demand Resources (iOS 9+) ship distinct architectures and asset bundles per device, lowering download size.

## Energy Efficiency (238)

- Profile with **Energy Impact in Instruments** — combines CPU, GPU, network, location, and display brightness into a single energy score.
- **PERFORMANCE**: avoid wake-from-sleep frequency. The CPU costs of waking, doing 10 ms of work, and sleeping again are dominated by the wake transition. Batch work into longer, less-frequent bursts.
- Use `BGAppRefreshTask` (iOS 13 onward) — for 2017, the BackgroundTasks framework doesn't exist yet; use `UIApplication.beginBackgroundTask(_:expirationHandler:)` and `URLSessionConfiguration.background(withIdentifier:)` for bounded background work.
- **HIDDEN GEM**: `URLSession` background sessions hand off to the system — your app can be terminated and the upload/download completes anyway, with `application(_:handleEventsForBackgroundURLSession:completionHandler:)` re-launching to handle completion.
- Display: dim toward black on OLED devices saves real power. Animations: pre-render where possible; avoid Core Animation property animations on slow paths.

## GCD Modernization (706)

- **Use `DispatchQoS` consistently.** A user-interactive task on a utility queue gets utility-level CPU bandwidth. Match the QoS to user expectations.
- **Concurrency limits**: `DispatchQueue(label:, attributes: .concurrent)` is rarely the right answer. Most apps need a serial queue or a few category-specific serial queues, not one giant thread pool.
- **`DispatchSourceTimer`** beats `Timer` for non-UI scheduling — runs on a dispatch queue, no main run loop dependency.
- **Locks**: prefer `os_unfair_lock` (low-level) or `DispatchQueue.sync` (synchronization). Avoid `NSLock` for hot paths — the Objective-C call overhead is non-trivial.
- **WARNING**: `DispatchSemaphore` for synchronous behavior in async APIs is a recipe for priority inversion and deadlocks. Restructure to async/callback chains instead.

## Choosing The Right Container (218)

- **`UIScrollView`** — direct content. Use when you have a fixed layout that needs to scroll.
- **`UITableView`** — recyclable single-column lists. Use for any uniform-row-height list.
- **`UICollectionView`** — recyclable arbitrary layouts. Compositional Layout doesn't exist yet (2019), so layouts are flow-based or fully custom subclasses.
- **`UIStackView`** — auto-layout grouping. Use for static or near-static row layouts that may grow with Dynamic Type.
- **`UISplitViewController`** — primary/detail on iPad and iPhone Plus. iOS 11 finally makes split view collapse correctly with `displayMode = .allVisible | .primaryHidden | .primaryOverlay`.

**HIDDEN GEM**: a `UIStackView` of `UIStackView`s is often the right answer for forms and settings — far less code than per-cell `UITableView` and reflows naturally with Dynamic Type. Trade off: no recycling, so stay under ~100 rows.

## Foundation Performance (244)

- **`Date`, `URL`, `Data`** are value types — copy-on-write. Free to pass around without ARC overhead.
- `String` (Swift 4) is now `Collection` again and stored as UTF-8 — see `swift4-language-codable.md`.
- **HIDDEN GEM**: `JSONDecoder` is several times faster than `JSONSerialization` + manual mapping for typical Codable structs.
- **PERFORMANCE**: `Calendar.current` returns the SAME instance per call — cache it once at app launch in a global to skip the dispatch.
- `DispatchData` for IO buffers — zero-copy concatenation, mappable into `Data` without copying.

## Cocoa Development Tips (236)

- **Strong type your KVO**: use the new block-based `observe(_:options:changeHandler:)` (Swift 4) — see `swift4-language-codable.md`. Token deinit auto-removes the observation.
- **Don't subclass UIControl unnecessarily** — composing with gesture recognizers and child views is usually cleaner.
- **`NSUbiquitousKeyValueStore`** for tiny shared prefs across user's devices via iCloud. ~64 KB total budget — don't put images here.

## Cross-references

- See `swift4-language-codable.md` — `Codable` works hand-in-hand with the new APFS-aware archiving.
- See `files-document-browser.md` — `UIDocumentBrowserViewController` builds atop APFS clone-aware semantics.
