# APFS — Apple File System Sneak Preview — WWDC 2016 Analysis

**Sessions covered:** 701 (Introducing Apple File System), 719 (Optimizing I/O for Performance and Battery Life)

## Headline

APFS is **the next-generation file system replacing HFS+ across every Apple platform** — Watch through Mac Pro. macOS Sierra ships it as a developer-preview technology (data volumes only), with default rollout planned for 2017. Designed from the ground up for SSDs, native encryption, atomic operations, and instantaneous file/directory cloning.

## Why now? HFS+ was 30 years old

HFS+ predates SSDs, predates mobile, predates the threading models we use today. Its B-trees take a single big lock; its records are fixed-format (every new field requires a backwards-incompatible volume bump); its encryption is bolted on as extended attributes (iOS) or via an external Core Storage layer (macOS). APFS unifies the encryption story, opens the data structures to flexible per-record fields, and adds modern features.

## Key APFS features

### Crash protection (copy-on-write metadata)

Every metadata write goes to a new location on disk. Combined with a transaction subsystem, you either see a consistent before-state or a consistent after-state — never partial. There is no fsck-style recovery needed for metadata.

### Space sharing — multiple volumes share free space

Containers hold multiple volumes; volumes share free space dynamically. No more "20GB free on disk0s2 but I'm out of room on disk0s3" — partitions stop being a planning problem.

**API impact (URGENT — DOCS MISS THIS):** The classic `total_size − used_size = free_size` formula **no longer works**. Other volumes in the same container also draw from free space. Use `URLResourceKey.volumeAvailableCapacityForImportantUsageKey` (new) or `volumeAvailableCapacityForOpportunisticUsageKey` to get accurate, intent-aware free-space estimates.

### Cloning files and directories — instant copies

`copyfile()` with the `COPYFILE_CLONE` flag, `clonefile()` system call, or just `FileManager.copyItem` — APFS writes only new metadata (refs to the same data blocks). Directory hierarchies clone atomically too — Document bundles (a directory!) become safe to atomic-replace.

```swift
// Foundation already detects APFS and clones automatically
try FileManager.default.copyItem(at: src, to: dst)
```

This is **transparent** — Foundation and `libcopyfile` detect the underlying file system. Your app picks up cloning behavior for free.

### Snapshots — read-only, mountable, point-in-time

Take a snapshot of the file system. You get an independently mountable read-only view. Modifications to live files don't affect the snapshot (until you delete the snapshot).

**Gotcha:** deleting a file that exists in any snapshot doesn't free its blocks. Snapshots can fill your disk if you don't prune them. Apple's expected primary use case: backups (Time Machine grabs a snapshot, copies from it, releases it).

### Atomic safe-save for directory bundles (HUGE WIN)

The `renamex_np()` syscall + `RENAME_SWAP` atomically swaps two filesystem entries. **Document bundles** (directories that contain assets — `.rtfd`, `.numbers`, `.pages`, photo libraries) finally get atomic save semantics — no more "move-old-aside, move-new-into-place, hope-power-doesn't-fail" dance.

Foundation's `replaceItem` and `URL.replacingItemAt(_:)` automatically use the new atomic primitive on APFS.

### Native multi-key encryption

Three modes:
- No encryption.
- Single-key per volume (full-disk-encryption equivalent).
- Multi-key per file AND per extent (region of a file). **No other file system in the industry supports per-extent encryption.** Combined with snapshots and clones it gives correct security boundaries through CoW operations.

iOS already does per-file encryption via HFS+ extended attributes; APFS makes it a first-class part of the file system.

### Fast directory sizing

Computing directory sizes (the "calculating size…" spinner in Get Info) is now an O(1)-ish lookup. APFS keeps the running size in a separate atomic record per directory rather than storing it on the directory itself (which would create lock-order violations).

### Fundamentals

- 64-bit inode numbers, 64-bit timestamps, nanosecond timestamp granularity.
- Sparse files (finally!).
- Optional fields per record — adding new attributes doesn't require a volume bump.
- Latency-optimized over throughput — apps and animations come up faster.

## Compatibility constraints (URGENT)

- Yosemite (10.10) and earlier **cannot read APFS volumes**. They prompt with an unhelpful "you need to initialize this disk" dialog. **Do not let users mount APFS on older OSes.**
- AFP (the legacy file-sharing protocol) does not support APFS volumes. Use SMB instead.
- Sierra developer preview only allows **data volumes** — no booting from APFS, no Time Machine source, no FileVault, no Fusion Drive (yet).
- Case-sensitive only (no insensitive variant in the preview). Test your apps on case-sensitive volumes!
- Cannot share over AFP — must use SMB.

## In-place upgrade

In 2017 macOS will upgrade users from HFS+ to APFS **in place** — user data stays where it is on disk; APFS metadata gets written into HFS+ free space. This is multi-second to multi-minute, fully crash-protected. Time Machine backup not required (though always recommended).

## I/O performance & battery (session 719)

- **Coalesce writes.** Writes to flash storage are far more expensive than reads. Use larger buffers, fewer syscalls.
- **Use `posix_fadvise()` / `madvise()`** to tell the kernel about your access pattern (sequential, random, willneed, dontneed). The system can prefetch or evict accordingly.
- **Don't `fsync()` casually.** Each `fsync` forces a flush through the I/O stack — drains the journal, drains the disk write cache. Use NSFileCoordinator + atomic write APIs at the Foundation layer.
- **Don't poll files for changes.** Use `DispatchSourceFileSystemObject` — kernel-driven, zero-CPU until something happens.
- **Memory-map (`mmap`) read-mostly files.** Page cache acts as your free LRU.

## Best practices for APFS-readiness

1. **Test your app on an APFS volume now.** Create a sparse-bundle disk image with `hdiutil create -fs APFS …` and copy your app's data there.
2. Stop computing free space yourself — use the URLResourceKey APIs.
3. Stop using `mvOnly` move/swap dances for safe-save — use `FileManager.replaceItem`.
4. If you have plug-ins or document bundles, prepare for atomic-replace semantics.
5. File bug reports against APFS issues now while it's still in preview.

## Hidden gems summary

- Foundation's `copyItem` + `replaceItem` automatically clone or atomic-rename on APFS — no opt-in needed.
- Multi-key per-extent encryption — unique to APFS in the industry.
- Atomic safe-save of document bundles via `renamex_np` (RENAME_SWAP) — finally fixes the long-standing 1980s bundle-save race.
- Snapshot + revert — file-system-level "global undo" for the whole volume.
- The new `URLResourceKey.volumeAvailableCapacityForImportantUsageKey` correctly accounts for purgeable iCloud Drive caches and other reclaim sources.

## Cross-references

- Foundation `URLResourceValues` modernization → analysis-2016/swift-3-migration.md
- Document model best practices → analysis-2016/cocoa-modern-mac.md
