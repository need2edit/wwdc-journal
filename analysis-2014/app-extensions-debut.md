# App Extensions Debut — WWDC 2014 Analysis

**Sessions covered:** 205 (Creating Extensions for iOS and OS X, Part 1), 217 (Creating Extensions for iOS and OS X, Part 2)

## Headline

iOS 8 introduces **App Extensions** — a way for apps to extend the system and other apps. Six initial extension points: **Today widgets, Share, Action, Photo editing, Document Provider, Custom Keyboard, Finder Sync** (Mac). This is iOS's biggest IPC story ever — but with strict constraints that prevent the historical mess of inter-app communication.

## The Mental Model (sessions 205, 217)

- An extension is a **separate purpose-built binary** inside your app's bundle. NOT a special mode of your app, NOT a piece of your app's code running in your app's process — a literally different executable with its own code signature, its own entitlements, and its own container (205).
- Extensions are **delivered with apps** — never installed independently. The "Extension Container" (your .ipa) carries any number of extensions. Users install your app; they get all your extensions for free.
- An **extension point** is an Apple-defined attachment surface: Notification Center widget, share sheet, action sheet, photo editor pane, etc. Third parties cannot define new extension points (205).
- Extensions are **bound 1-to-1 with their hosting app at runtime**: if your share extension is invoked from Safari, a process spins up to serve Safari. If invoked from Mail simultaneously, a SECOND process spins up. They never share an address space (205).
- HIDDEN GEM: this 1-to-1 process binding means a wild pointer in your extension cannot bring down the user's other extension instances. Pure isolation by design (205).

## The Six Extension Points

### Today (Notification Center) Widget — session 205

- A `UIViewController` (or `NSViewController` on Mac) shown inside Notification Center's Today view.
- **Performance is the #1 concern**: load cached data immediately in `viewWillAppear`, kick off network fetches in the background, never block the user (205).
- **Sizing**: use Auto Layout constraints OR call `setPreferredContentSize(...)` on the controller. The Notification Center owns the frame; you describe your desired height (205).
- Implement `widgetPerformUpdateWithCompletionHandler:` and call back with `NCUpdateResultNewData`/`NoData`/`Failed`. The system uses this to refresh widgets in the background.
- Tap-to-launch-app: use `extensionContext.openURL(...)` with a custom URL scheme shared with your app. The widget can hand off to the full app smoothly.

### Share Extension — session 205

- Use case: post to a social network or photo blog from anywhere — Photos, Safari, Mail.
- Subclass `SLComposeServiceViewController` for the standard system look (free post button, character counter, preview, attached audience picker). Or subclass `UIViewController`/`NSViewController` for full custom UI.
- BEST PRACTICE: do the heavy lifting (downsampling images, processing video) in `presentationAnimationDidFinish` — NOT before the sheet has slid up. Otherwise the present animation stutters (205).
- **Activation rules** (Info.plist `NSExtensionActivationRule`): predicate string OR a condensed dictionary like `{NSExtensionActivationSupportsImageWithMaxCount: 1, NSExtensionActivationSupportsWebPageWithMaxCount: 1}`. Only matching contexts show your share extension in the activity sheet (205).
- **Mandatory background NSURLSession upload**: when the user taps Post, you have only seconds before your extension is suspended. Create a background `NSURLSession`, hand it the upload task, then call `extensionContext.completeRequestReturningItems(...)`. The system finishes the upload after your extension is dead (205).
- HIDDEN GEM: `CFBundleDisplayName` in your share extension's Info.plist controls what name the user sees — your app might bundle multiple share extensions with different names ("Photo Blog", "Set Header Photo") (205).

### Custom Action Extension — session 217

- Use case: edit/markup an image, translate text, annotate, run OCR, etc.
- Two flavors: **viewer** (no UI, just transforms data and returns) and **editor** (presents a UI). The Bing Translate demo from the keynote was a viewer extension — non-modal.
- Same `NSExtensionContext` model as share extensions: `inputItems` is an array of `NSExtensionItem`, each carrying `NSItemProvider` attachments.
- BEST PRACTICE: `loadItemForTypeIdentifier(kUTTypeImage, options: nil) { ... }` — Item Provider does **automatic type coercion**. Specify the desired return type (NSData, NSURL, UIImage, NSAttributedString) in your block signature; the framework picks the right transformer (217).
- HIDDEN GEM: action extensions can run in **Safari over live web content**. Your extension provides a JavaScript file (`ExtensionPreprocessing JavaScript` global with `run(arguments)` and `finalize(arguments)` methods) that reads the DOM and returns data to your native extension, and replaces DOM nodes with the edited result. Look at the TinySketch demo in 217 — annotates images directly inside Safari pages and writes the edited image back as a data URL (217).

### Photo Editing Extension — session 511 (Photos Frameworks)

- Subclass `PHContentEditingController` and conform to its protocol. Four methods: `canHandle(adjustmentData:)`, `startContentEditing(with:placeholderImage:)`, `finishContentEditing(completionHandler:)`, `cancelContentEditing()`.
- Edits are **non-destructive** and roundtrip through `PHAdjustmentData` so a later edit can resume from the original + adjustments (NOT the rasterized result). See PhotoKit Migration analysis for details.

### Document Provider Extension — keynote / session 205

- First time iOS apps can vend a file storage provider — Dropbox, iCloud Drive, Box, Google Drive — usable from any app's `UIDocumentPickerViewController`. The decade-old "no shared filesystem" wall is partially down (205).

### Custom Keyboard Extension — session 205

- Replace the system keyboard with your own. Most invasive extension type — has its own privacy considerations (network access requires user opt-in inside Settings).

## Code Sharing: Embedded Frameworks Debut — session 217

- iOS 8 finally allows **embedded frameworks** in your `.ipa` — like macOS has had since 2001. Your app and all its extensions can share the same framework (217).
- These frameworks are **encrypted with your app's same encryption** — the same anti-piracy protection wraps them.
- IMPORTANT: embedded frameworks are NOT a general code-sharing mechanism between apps. Each app's framework copies are isolated. They exist purely so an app and its own extensions can share code (217).
- If your app links the framework, the app's minimum deployment target is forced to **iOS 8**. If only an extension links it, the app's target is unaffected — but the extension's functionality won't be available below iOS 8 (217).
- BEST PRACTICE: refactor your model layer and any shared view controllers into a framework. Leave platform-specific UI in the app and extension targets respectively. The MVC split pays off massively here (217).

## API Restrictions in Extensions — session 217

- Most APIs are available, but some are explicitly forbidden. Marked with the new `NS_EXTENSION_UNAVAILABLE("...")` macro.
- **`UIApplication.sharedApplication()` is unavailable in extensions**. The error message recommends a "view controller-based solution" instead (217).
- No general multitasking in extensions: no VoIP, no long-running background tasks, no background fetch. You get a short task-completion window to flush dirty state to disk before suspension/kill (217).
- BEST PRACTICE: extensions should be lean. "Get in, do the job, get out." Treat them like an `NSOperation`, not an app (217).

## Data Sharing Between App and Extensions — session 217

- **App Groups** (capability in Xcode): a shared container directory accessible to your app and all extensions in the group. Configure in Apple Developer portal, enable in Capabilities (217).
- Use `NSFileCoordination` for raw file reads/writes — your app and extension can run simultaneously (217).
- **`NSUserDefaults(suiteName: "group.com.example.MyApp")`** — opens a shared defaults domain. The framework handles read/write coordination automatically (217).
- **Shared keychain**: configure an access group in your entitlements; both targets share keychain items. NOTE: in seed 1, this was team-ID-based; will be App-Group-based by GM (217).
- Core Data and SQLite both work for cross-process databases (Core Data with the right backing store, SQLite via WAL mode).
- HIDDEN GEM: Privacy permissions (Photos, Contacts, Camera) granted to your app **also cover all its extensions** — the user grants once for the whole app bundle (217).

## Communication Pattern: NSExtensionContext

- Every extension receives an `extensionContext` from its principal view controller (`self.extensionContext`).
- **Pull data IN** via `extensionContext.inputItems` — array of `NSExtensionItem`, each with `attachments` (array of `NSItemProvider`).
- **Send results OUT** via `completeRequestReturningItems([...], completionHandler:)` — returns modified items for editor extensions, or just dismisses for viewer extensions.
- **Cancel** via `cancelRequestWithError(...)`.
- **Open the host app** via `extensionContext.openURL(...)` (Today widgets only; restricted elsewhere).

## Best Practices

- **Be lean. Be fast. Be stateless.** The system kills extensions aggressively (217).
- **Defer expensive work** until after the present animation finishes (`presentationAnimationDidFinish` for `SLComposeServiceViewController` subclasses) (205).
- **Use background NSURLSession for any network I/O** in share extensions — the system completes the upload after your extension dies (205).
- **Cache frequently** in shared containers — your extension is a one-shot process. Don't recompute what your app already knows.
- **Test extensions when host apps are NOT in foreground** — your extension can launch into a freshly-spun-up process without your app's state.

## Hidden Gems

- HIDDEN GEM: extensions don't have an `application:didFinishLaunching:` lifecycle. The principal view controller's `viewDidLoad` IS the launch. There's no `AppDelegate` (205).
- HIDDEN GEM: today widgets can implement `viewWillTransitionToSize:withTransitionCoordinator:` to animate alongside their own preferred-size changes — coordinated with Notification Center's resize animation (205).
- HIDDEN GEM: `NSItemProvider`'s `loadItemForTypeIdentifier` does **automatic type coercion**. Ask for `NSData` and you get bytes; ask for `UIImage` and you get a decoded image; ask for `NSURL` from an image and you get a file URL — all from the same item provider (217).
- HIDDEN GEM: the JavaScript preprocessing for Safari action extensions is full DOM-aware JavaScript that runs in the page's context. You can scrape, modify, and replace any element. The TinySketch annotation demo replaces an `<img>` `src` with a base64 data URL of the edited image (217).
- WARNING: extensions on iOS get killed quickly. If your share extension uploads via foreground NSURLSession, the upload will be cancelled when the extension dies. ALWAYS use background sessions (205).

## Cross-references

- **CloudKit (208)** is a natural backend for share extensions writing to the public database.
- **PhotoKit (511)** is the framework for photo-editing extensions; the model objects (`PHAsset`, etc.) are designed to be shared between an app and its photo extension.
- **Embedded frameworks** (Building Modern Frameworks, session 416) is the recommended code-sharing mechanism that makes large extension projects manageable.
- **Touch ID (711)** integrates with extensions via shared keychain access groups — if your app has authenticated, your extension's queries against the shared keychain inherit that authentication.

## Migration Guidance

- **Reconsider your URL-scheme app-to-app workflows** — many of them are now better expressed as custom action extensions (205). The Bing Translate keynote demo would historically have been "open Bing Translate, paste text, copy result, return to Safari" — now it's a single tap.
- **Refactor your app's model into a framework FIRST** before adding extensions. The cleanup pays off forever.
- **For share/action extensions, audit your code for `[UIApplication sharedApplication]` calls** — they will fail to compile in the extension target. Move that work into the app, or use `UIResponder` chain alternatives.
