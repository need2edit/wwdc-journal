# Files App, Document Browser & File Provider — WWDC 2017 Analysis

**Sessions covered:** 229 (Building Great Document-based Apps in iOS 11), 243 (File Provider Enhancements), 241 (Introducing PDFKit on iOS), 231 (What's New in Core Spotlight)

## Headline

iOS 11 ships the **Files** app — the user-facing window onto a unified file system that includes iCloud Drive, on-device "On My iPad" storage, and any third-party cloud provider that adopts the new `FileProvider` extension. The Files app is itself a thin layer on top of the public `UIDocumentBrowserViewController` (DBVC), which any document-based app can adopt to get the same UX.

## What Apps Get For Free (229)

Adopting `UIDocumentBrowserViewController`:

- Unified browse/recents UI matching Files
- All third-party cloud providers (Box, Dropbox, etc.) appear automatically — no per-vendor SDK
- Tags (cross-provider, cross-device sync via iCloud)
- Long-press recents popover on the home-screen icon
- Full Spotlight indexing of document metadata
- Drag-and-drop in/out
- The `Open In Place` semantics — your app edits the original file, not a copy
- Built-in zoom-from-thumbnail transition via `UIDocumentBrowserTransitionController`

## DBVC Setup (229)

Required Info.plist keys:

- `UISupportsDocumentBrowser = YES` — declares the app as a DBVC app
- `CFBundleDocumentTypes` array — declared content types you handle
- `UTExportedTypeDeclarations` — for any custom UTI you own (with `UTTypeConformsTo` like `["public.data", "public.content"]` and a `UTTypeTagSpecification.public.filename-extension`)

**WARNING**: `UIDocumentBrowserViewController` MUST be the root view controller of your scene. It will not work embedded in a navigation controller, tab bar, or split view. This is a hard requirement.

## Open + Create + Import Flow (229)

Three delegate methods cover the full life cycle:

```swift
// Tap an existing document
func documentBrowser(_ controller: UIDocumentBrowserViewController,
                     didPickDocumentURLs urls: [URL])

// User taps "+" to create new
func documentBrowser(_ controller: UIDocumentBrowserViewController,
                     didRequestDocumentCreationWithHandler importHandler:
                     @escaping (URL?, UIDocumentBrowserViewController.ImportMode) -> Void)

// Import succeeded
func documentBrowser(_ controller: UIDocumentBrowserViewController,
                     didImportDocumentAt source: URL,
                     toDestinationURL destination: URL)

// Import failed
func documentBrowser(_ controller: UIDocumentBrowserViewController,
                     failedToImportDocumentAt url: URL, error: Error?)
```

**ImportMode** is `.copy` (template files in your bundle) or `.move` (a working file the user already created elsewhere). Always call `importHandler(nil, .none)` if the user cancels — without it, the create button hangs forever.

## Open-In-Place Is Mandatory (229)

Apps using DBVC MUST handle `application(_:open:options:)` and call `revealDocument(at:importIfNeeded:)` — that's how the Recents popover and other apps' "Open with…" flows reach you.

```swift
func application(_ app: UIApplication, open url: URL,
                 options: [UIApplication.OpenURLOptionsKey: Any]) -> Bool {
    guard url.isFileURL else { return false }
    documentBrowser.revealDocument(at: url, importIfNeeded: true) { revealedURL, error in
        if let error = error { /* present alert */; return }
        self.presentDocument(at: revealedURL!)
    }
    return true
}
```

## Security-Scoped URLs Trap (229)

Documents outside your app sandbox come as **security-scoped URLs**. You MUST `startAccessingSecurityScopedResource()` before reading and pair it with `stopAccessingSecurityScopedResource()`. **Forgetting the stop leaks a file system reservation.**

**HIDDEN GEM**: persisting a URL is wrong — instead, store its **bookmark data** (`url.bookmarkData(options: [.minimalBookmark], …)`) and resolve it later. Plain URL paths break across reboots, app reinstalls, and external storage moves.

## UIDocument Is Recommended (229)

`UIDocument` gives you:

- Auto-save (triggered by typing pauses, app backgrounding, etc.)
- File coordination (`NSFileCoordinator` and `NSFilePresenter`) — cooperate with sync engines and other apps
- Versioning conflicts surfaced as `documentStateChangedNotification`
- Security-scoped resource bracketing handled internally

Implement `contents(forType:) throws -> Any` and `load(fromContents:ofType:) throws`. Use `NSKeyedArchiver` for object graphs (Codable for Swift-native types — see `swift4-language-codable.md`).

## File Provider Extensions (243)

Cloud vendors no longer need to ship a Files-replacement app. A `NSFileProviderExtension` exposes the cloud as a folder under "Locations" in the Files sidebar. Apple's iCloud Drive itself runs as a file provider extension — third parties get the SAME API surface.

- **HIDDEN GEM**: `NSFileProviderItemIdentifier` lets you publish files lazily — return placeholders, fetch only on access. Ideal for huge cloud libraries.
- **PERFORMANCE**: implement `evictItem(identifier:)` to honor the system's storage pressure callbacks. Without it, your provider fills the device.
- **WARNING**: file providers run in a sandboxed extension process with strict memory limits. Stream large downloads; never `Data(contentsOf:)` an unknown-size file.

## Custom Actions, Bar Buttons, Activities (229)

Three ways to add UI to DBVC:

- `UIDocumentBrowserAction` (`.menu` long-press / `.navigationBar` selection-mode) — declarative, gets URLs the user selected
- `additionalLeadingNavigationBarButtonItems` / `additionalTrailingNavigationBarButtonItems` — plain `UIBarButtonItem`s
- `documentBrowser(_:applicationActivitiesForDocumentURLs:)` — extra `UIActivity` items in the Share sheet

**WARNING**: in custom actions, you only have access to the URLs UNTIL THE APP IS KILLED. Persist a bookmark immediately if you'll need it later.

## Custom Zoom Transition (229)

`transitionController(forDocumentURL:)` returns a `UIDocumentBrowserTransitionController` that drives the thumbnail-to-full-screen zoom. Set its `targetView` to your editor's hero view. Drive the loading progress with `transitionController.loadingProgress = …`. Vend it from your `UIViewControllerTransitioningDelegate`. **HIDDEN GEM**: this same transition can be a regular `UIPercentDrivenInteractiveTransition` for swipe-down-to-dismiss.

## Quick Look Thumbnail & Preview Extensions (229)

Two new system-wide extension points in iOS 11:

- **Thumbnail extension** (`QLThumbnailProvider`): your custom file types get rendered thumbnails everywhere in the system (Files, Mail attachments, Messages, Spotlight). Implement `provideThumbnail(for: QLFileThumbnailRequest, completionHandler:)`. Return either a `QLThumbnailReply(contextSize:drawingBlock:)` (you draw) or `QLThumbnailReply(imageFileURL:)` (Quick Look scales).
- **Preview extension** (`QLPreviewingController`): full-fidelity peek/quick-look of your custom types. Implement `preparePreviewOfFile(at: URL, completionHandler:)`. Pair with `QLSupportsSearchableItems = YES` to preview Spotlight results too.

**PERFORMANCE**: these extensions run in tight memory budgets. Don't link giant frameworks; check for leaks; never do background work after calling the completion handler.

## PDFKit Comes to iOS (241)

For the first time, **PDFKit ships on iOS in addition to macOS**. Same API surface (`PDFView`, `PDFDocument`, `PDFPage`, `PDFAnnotation`).

- `PDFView` is now a `UIView` on iOS / `NSView` on macOS.
- New iOS-only feature: `usePageViewController = true` for iBooks-style page swipes with a `PDFThumbnailView` scrubber strip.
- `PDFPage(image:)` initializer creates a P3-color-aware page from a UIImage — the easiest way to convert images to PDF.
- Thumbnail-on-demand: `pdfPage.thumbnail(of:size, for: displayBox)` returns a UIImage with proper aspect ratio, P3 color, and box-aware crop.

### PDF Form Widgets (241)

Three flavors via `widgetFieldType`: `text`, `button`, `choice`. Sub-flavors via `widgetControlType` (radio/checkbox/push) or `isListChoice`.

**HIDDEN GEM**: `hasComb = true` paired with `maximumLength = N` divides a text widget into N equal cells — perfect for date fields like `MM/DD/YYYY`. Two properties replace dozens of lines of custom rendering.

**HIDDEN GEM**: radio buttons are grouped by sharing the same `fieldName` and differentiated by `buttonWidgetStateString`. Group siblings with the same `fieldName` "Question1"; give each its own `buttonWidgetStateString` "yes"/"no".

`PDFActionResetForm` with `fieldsIncludedAreCleared = false` and an EMPTY field list **resets every widget in the document** — one line of code.

### Custom Page Drawing (241)

Subclass `PDFPage`, override `draw(with box: PDFDisplayBox, to context: CGContext)`. Set `PDFDocument.delegate` and return your subclass from `documentDidUnlock(_:) -> classForPage()`. **CRITICAL**: drawing must be thread-safe — PDFKit can render the main view and a thumbnail concurrently. Watermarks and "owned by user X" overlays are the canonical use case (transcript shows a session-long worked example).

## Core Spotlight Integration (231)

Adopting DBVC automatically indexes your documents' metadata in Spotlight. For richer search:

- `CSSearchableItem.contentURL` MUST point to the document so DBVC can deduplicate.
- New: `CSSearchableItem` results in iOS 11 surface inside the Files app search bar, not just system Spotlight.
- Continue user activity from Spotlight back into the document via `NSUserActivity` and `userActivity.referrerEntityIdentifier` for analytics.

## Cross-references

- See `drag-drop-ipad.md` — DBVC's Recents popover supports drag-and-drop import natively.
- See `swift4-language-codable.md` — `Codable` is the new go-to for `UIDocument.contents(forType:)` payloads.
