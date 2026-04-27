# Catalyst (iPad Apps for Mac) & iPadOS — WWDC 2019 Analysis

**Sessions covered:** 205 (Introducing iPad Apps for Mac), 235 (Taking iPad Apps for Mac to the Next Level), 212 (Introducing Multiple Windows on iPad), 246 (Window Management in Your Multitasking App), 258 (Architecting Your App for Multiple Windows), 259 (Targeting Content with Multiple Windows), 215 (Advances in Collection View Layout), 220 (Advances in UI Data Sources), 224 (Modernizing Your UI for iOS 13), 203 (Introducing Desktop-class Browsing on iPad), 809 (Designing iPad Apps for Mac), 808 (What's New in iOS Design)

## Headline

iPadOS launched as a separate brand from iOS. Catalyst (then called "iPad Apps for Mac") brings UIKit to macOS Catalina natively. Multiple windows, full keyboard support, contextual menus, drag and drop everywhere, sidebars and toolbars come to iPad — and all of these unlock a great Mac translation for free.

## Catalyst Architecture (205)

- A single shared technology stack on macOS hosts both AppKit and UIKit apps. Lower-level frameworks (CoreGraphics, Foundation, libSystem) are unified — there is one copy.
- AppKit and UIKit remain distinct (NSView != UIView), and frameworks that depend on either remain separate (two MapKits, two SceneKits, two WebKits — the linker picks the right copy automatically).
- Enable in Xcode 11: Project → target → Deployment Info → check **Mac**. Xcode auto-rewrites the bundle identifier with a `maccatalyst.` prefix and adds entitlements derived from your `Info.plist` usage descriptions.
- Pre-compiled iOS Simulator binary frameworks are NOT compatible with Catalyst. You need either source frameworks or vendor-supplied XCFrameworks (see 416).

## What's "Free" on Mac (205)

- Default menu bar with cut/copy/paste/undo/redo/select all/Edit/View/Window/Help.
- Window resizing, full screen, split view, traffic light buttons.
- Dark Mode if you used semantic colors in iOS 13.
- Scroll bars and overlay scrollers.
- Touch Bar via `AVPlayerViewController` and `UITextView` automatically.
- `UIDocumentPickerViewController` becomes `NSOpenPanel`.
- iOS Settings Bundle becomes a Preferences pane via the Preferences menu item.
- Drag and drop, copy/paste, printing, multi-window — all carry over.

## API Differences You Must Handle (205)

- **Unavailable frameworks**: ARKit, ClassKit, HealthKit, HomeKit, Sticker Packs, Custom Keyboards, iMessage extensions, UIWebView. Migrate to WKWebView.
- **Different sensors**: CoreLocation works but Macs lack GPU; CoreMotion is irrelevant.
- **Data protection APIs (`.completeFileProtection`)** **silently no-op on Mac**. Don't assume sensitive files are encrypted at rest. Use Keychain or `AES.GCM` from CryptoKit instead. **URGENT** — this is a security pitfall.
- **Bundle layout** is deeper on Mac (proper `.app/Contents/...`). Use `Bundle.main.url(forResource:)`. Do not hardcode paths.
- **77% scaling**: UIKit content is automatically scaled to 77% to fit Mac density (17pt iOS body ≈ 13pt Mac body).
- Mouse left-button drags map to single synthesized touches → tap/pan/long-press recognizers fire. Custom multi-touch gestures (pinch to do something custom) need an alternate Mac path.
- New `UIHoverGestureRecognizer` for cursor hover.

## Refining the Mac Experience (235)

- **Better iPad apps are better Mac apps**: support keyboard shortcuts (`UIKeyCommand`), drag and drop, multi-window, dynamic type, dark mode.
- **`UICommand` / `UIMenu` / `UIMenuBuilder`**: take full control of the Mac menu bar in code. Same `UIKeyCommand`s show in iPad's command-key discoverability HUD.
- **`UIContextMenuInteraction`** — new in iOS 13, replaces 3D Touch peek/pop. On Mac it's the right-click context menu. Cross-platform with one API.
- **Sidebar style**: `splitVC.primaryBackgroundStyle = .sidebar` for a translucent macOS-style sidebar.
- **Toolbar via NSToolbar**: `windowScene.titlebar?.toolbar = NSToolbar(...)` — yes, you use the AppKit `NSToolbar` directly from your Catalyst app.
- **NSTouchBar** is exposed via UIResponder for Catalyst.

## Multiple Windows / Scenes (212, 246, 258, 259)

- **Concept change**: an app delegate can have multiple `UIScene`s, each with its own state and lifecycle. App lifecycle (`didFinishLaunching`) fires once per process; scene lifecycle (`scene(_:willConnectTo:options:)`, `sceneWillEnterForeground`, `sceneDidBecomeActive`, `sceneDidDisconnect`) fires per window.
- **Adoption**: declare `UIApplicationSceneManifest` in `Info.plist`. Your `UIApplicationDelegate` implements `application(_:configurationForConnecting:options:)`.
- **State restoration via `NSUserActivity`** is now the canonical pattern: `scene.userActivity = NSUserActivity(activityType:)` and rebuild your view controllers from it on reconnect.
- **Targeting content with `UIWindowSceneDelegate`**: spawn a new window programmatically via `UIApplication.shared.requestSceneSessionActivation(_:userActivity:options:errorHandler:)`.
- **PERFORMANCE**: iPad shows up to 2 windows from your app side-by-side. iPad on Mac → one window per scene.

## Compositional Layout & Diffable Data Sources (215, 220)

These two new APIs landed together and pair perfectly. Both come to iOS, tvOS, and macOS in 2019.

### Compositional Layout (215)
- New `UICollectionViewCompositionalLayout` replaces custom `UICollectionViewLayout` subclasses for the App Store-style heterogeneous grids.
- Composable hierarchy: **Item → Group → Section → Layout**. Groups can be horizontal, vertical, or custom (radial, generated).
- Sizing via `NSCollectionLayoutDimension`: `.fractionalWidth(0.5)`, `.fractionalHeight(0.3)`, `.absolute(200)`, `.estimated(200)`.
- Per-section closure: `UICollectionViewCompositionalLayout(sectionProvider:)` lets each section have a totally different layout.
- **HIDDEN GEM**: groups can be nested inside other groups → arbitrarily complex layouts from simple primitives.

### Diffable Data Sources (220)
- `UICollectionViewDiffableDataSource` and `UITableViewDiffableDataSource` (and `NSCollectionViewDiffableDataSource` on Mac).
- Build an `NSDiffableDataSourceSnapshot<SectionID, ItemID>`, populate it, call `apply(snapshot, animatingDifferences: true)`. Done.
- **No more `performBatchUpdates`** — all the index-path crashes go away. **URGENT BEST PRACTICE** — adopt this immediately if you do any `performBatchUpdates`.
- Uses identifiers (`Hashable`), not index paths. Index paths are ephemeral and fragile; identifiers are robust.
- Enums make great section identifiers (auto-Hashable in Swift).

## Modernizing UI for iOS 13 (224)

- **Launch images are dead**: by April 2020, App Store requires Launch Storyboards. Apps with only launch images will be rejected. **URGENT**.
- **Letterboxing is gone**: apps built against the iOS 13 SDK always render at native full-screen resolution. Make sure your layouts handle every size.
- **Sheets are the new default**: `.modalPresentationStyle = .automatic` — view controllers presented full-screen on iOS 12 now appear as a swipe-down sheet on iOS 13. To opt out (camera, fullscreen game), set `.fullScreen` explicitly.
- **`isModalInPresentation = true`** on a sheet view controller prevents pull-to-dismiss; combine with `presentationControllerDidAttemptToDismiss` delegate to prompt save/discard.
- **`UINavigationBarAppearance`, `UIToolbarAppearance`, `UITabBarAppearance`** — comprehensive new appearance configuration with `standardAppearance`, `compactAppearance`, `scrollEdgeAppearance`. Per-`UINavigationItem` overrides allow per-screen bar styling like the new Reminders app.
- **`UISearchTextField`** is now a public subclass of `UITextField`. **HIDDEN GEM**: tokens (`UISearchToken`) provide the Photos-style filter chips inside the search field — copy/paste/drag and drop included.
- **`UIContextMenuInteraction`** replaces `UIPreviewInteraction` and 3D Touch peek/pop.
- **`UITextInteraction`** — new `UIInteraction` you can attach to your custom text view to get system-quality selection, magnifier, and handles for free (3 lines of code).

## Desktop-class Browsing on iPad (203)

- WKWebView on iPadOS now requests **desktop sites by default**. Override per-site if you need mobile.
- New `WKWebpagePreferences` and `WKWebView.evaluateJavaScript(_:in:in:)` for cross-frame evaluation.

## Cross-references

- Sign In with Apple in Catalyst apps: 706 (works automatically across iOS/macOS/web).
- Dark Mode: 214 (the same APIs work in Catalyst).
- New Design: 808 (iOS 13 design language), 809 (designing iPad apps for Mac).
- Distribution: 304 (App Distribution from ad-hoc to enterprise).
