# WWDC 2020 — SwiftUI 2.0: Apps, Scenes, Lists, Toolbars, Animation

SwiftUI's second major release. The big change: **you can write your entire app in SwiftUI** — no more UIKit/AppKit/WatchKit shells. New scene architecture, document-based apps, list/grid/outline support, toolbar API, scene storage, and a richer data-flow story.

## Sessions Analyzed
- 10037 — App essentials in SwiftUI (gateway)
- 10040 — Data Essentials in SwiftUI
- 10041 — What's new in SwiftUI
- 10119 — Introduction to SwiftUI
- 10031 — Stacks, Grids, and Outlines in SwiftUI
- 10039 — Build document-based apps in SwiftUI
- 10052 — Build with iOS pickers, menus and actions
- 10148 — Inspect, modify, and construct PencilKit drawings (uses SwiftUI patterns)
- 10149 — Structure your app for SwiftUI previews
- 10185 — Visually edit SwiftUI views
- 10643 — Build a SwiftUI view in Swift Playgrounds

## The New App / Scene / View Hierarchy

Three protocols, three responsibilities:

```swift
@main
struct BookClubApp: App {
  @StateObject private var store = BookStore()
  
  var body: some Scene {
    WindowGroup {
      ReadingListViewer().environmentObject(store)
    }
    Settings { SettingsView() }  // macOS-only
  }
}
```

- **`App`** — top of the tree, owned by the runtime, returns a `Scene`.
- **`Scene`** — a piece of UI that the platform manages independently (a window, a tab in a tabbed window, a document). Scenes can be composed.
- **`View`** — content within a scene.

`@main` (new in Swift 5.3) replaces the need for a `main.swift`. Apps can hold `@StateObject`, `@State`, and other source-of-truth properties just like views.

### Scene Types

- **`WindowGroup`** — the primary multi-platform scene. Manages a single full-screen window on iOS/watchOS/tvOS; multiple windows on iPadOS/macOS via standard Cmd-N. SwiftUI auto-adds the New Window menu on Mac.
- **`DocumentGroup`** — automatic open/edit/save flow for document-based apps. iOS shows a document browser; Mac opens new windows per document; menu commands are added automatically.
- **`Settings`** — macOS-only, sets up the standard preferences window with the right styling and Cmd-, shortcut.

### Scenes Have Independent State

Each instance of a scene from a `WindowGroup` gets its **own** copy of the views' state. This is why two iPad app windows can be at different books in the same app.

### Commands API — Menu Bar and Keyboard Shortcuts

```swift
WindowGroup { ContentView() }
  .commands {
    CommandMenu("Shape") {
      Button("Circle") { ... }.keyboardShortcut("c")
    }
  }
```

Custom command types (conforming to `Commands`) for organizing. The framework auto-targets actions based on user focus (similar to AppKit responder chain). On Mac you get a real `NSMenuItem`; on iPad you get the keyboard shortcut.

### Launch Screen

For SwiftUI apps without a storyboard, a new **Launch Screen** Info.plist key declares standard components (default images, background colors, empty top/bottom bars) instead of a separate launch storyboard. Existing storyboards still work.

## Data Flow: The Decision Matrix

The single most-asked SwiftUI question: which property wrapper for what? The 2020 answer:

| Wrapper | Purpose | Lifetime | Source of Truth? |
|---|---|---|---|
| `@State` | View-local mutable value | View lifetime, persisted by SwiftUI | YES (creates one) |
| `@Binding` | Read-write reference to someone else's source of truth | Lives with the source | NO |
| `@StateObject` | View-owned ObservableObject | View lifetime, instantiated once before first body | YES (creates one) |
| `@ObservedObject` | Externally-owned ObservableObject | Caller controls; do NOT init in body | NO |
| `@EnvironmentObject` | Inherited ObservableObject | Set by ancestor's `.environmentObject(_:)` | NO (shares) |
| `@SceneStorage` | Persisted scene-local value (auto-restored) | Scene + restoration | YES |
| `@AppStorage` | Persisted via UserDefaults | App-wide, persistent | YES |

### `@StateObject` Solves a Real Bug

Before iOS 14, `@ObservedObject var store = MyStore()` in a view's property would **re-allocate** the store every time the parent re-rendered, losing data and burning heap. `@StateObject` is the fix: SwiftUI instantiates the object **once** before the first `body` call and keeps it alive for the view's lifetime.

Rule: if you create the object inside the view, use `@StateObject`. If the object is passed in from outside, use `@ObservedObject`.

### `@SceneStorage` and `@AppStorage` (New Persistence)

`@State` is process-lifetime — gone if the app is killed. The new wrappers solve UI state restoration:

```swift
@SceneStorage("selection") var selectedID: String?    // per-scene
@AppStorage("darkMode") var darkMode: Bool = false   // app-wide via UserDefaults
```

SceneStorage is per-scene (each iPad window restores its own selection independently), AppStorage is app-wide. Both are sources of truth — you can derive `Binding`s from them. Don't store everything; persistence isn't free.

### Update Lifecycle

User event → mutate source of truth → SwiftUI invalidates dependent views → fresh body executions → diff vs. previous render → minimal UI changes. Body should be a **pure function**:
- No side effects.
- Don't dispatch work.
- Don't make assumptions about how often body is called.

For side effects, use the new event modifiers:
- `.onChange(of:perform:)` — react to value changes
- `.onAppear` / `.onDisappear`
- `.onReceive(_:perform:)` — Combine publisher
- `.onOpenURL(perform:)`
- `.onContinueUserActivity(_:perform:)`

These run on the main thread; dispatch to background for expensive work.

## Lists, Grids, Outlines

### Lists with Hierarchy

`List(items, children: \.children) { item in Row(item) }` recursively renders an outline. macOS gets the proper outline disclosure styling; iOS/iPadOS get expandable rows. Apple's pitch: **reduce push-pop navigation by using outlines for content browsing**.

### `LazyVStack`, `LazyHStack`, `LazyVGrid`, `LazyHGrid`

The lazy variants only instantiate views as they scroll into view. Combined with `ScrollView`, they make smooth infinite-feeling galleries:

```swift
LazyVGrid(columns: [GridItem(.adaptive(minimum: 80))]) {
  ForEach(photos) { Photo($0) }
}
```

Three column-sizing modes:
- `.adaptive(minimum:)` — fits as many fit
- `.flexible(minimum:maximum:)` — equal-share with bounds
- `.fixed(_:)` — exact width

### `ForEach` Inside Lists (Mixed Static/Dynamic Content)

`List` supports mixing static and dynamic rows by using `ForEach` for the dynamic part:

```swift
List {
  ForEach(items) { Row($0) }
  HStack { Spacer(); Text("\(items.count) items"); Spacer() }
    .foregroundColor(.secondary)
}
```

`onMove(perform:)` and `onDelete(perform:)` modifiers on the `ForEach` give you reordering and swipe-to-delete with no further code.

## Toolbars (New, Multi-Platform)

```swift
.toolbar {
  ToolbarItem(placement: .primaryAction) { Button("Add", action: add) }
  ToolbarItem(placement: .cancellationAction) { Button("Cancel", action: cancel) }
}
```

Placements are **semantic** — `.primaryAction`, `.confirmationAction`, `.cancellationAction`, `.principal`, plus positional ones (`.bottomBar`, `.navigation`). SwiftUI puts each item in the idiomatic location for the platform: navigation bar on iOS, real Mac toolbar on macOS, watchOS toolbar.

Pair with `keyboardShortcut(_:)` modifier. Cancel/default actions use Esc/Return shortcuts respectively.

## The `Label` View

A new combined title-and-icon view used everywhere — toolbars, menus, lists:

```swift
Label("Edit", systemImage: "pencil")
```

Auto-adapts to context:
- In a toolbar: icon-only with title used for accessibility.
- In a list: icon and title aligned consistently.
- At larger Dynamic Type sizes: text wraps around the icon to maximize legibility.
- At accessibility text sizes: icon shrinks proportionally.

## Visual Effects

### `matchedGeometryEffect`

This is genuinely magical. Two views in different parts of the hierarchy can share an identifier in a namespace, and SwiftUI animates the transition between them as if it's a single physical view:

```swift
@Namespace var ns
// View A
Image(album).matchedGeometryEffect(id: album.id, in: ns)
// View B (somewhere else)
Image(album).matchedGeometryEffect(id: album.id, in: ns)
```

When one disappears and the other appears, SwiftUI interpolates the frames as a single transition. Used heavily in macOS Big Sur Control Center. This eliminates the entire class of "hero" / "shared element" transition code.

### `ContainerRelativeShape`

Adopts the shape and corner radius of the nearest container. Critical for widgets and any views in containers with platform-controlled corner radii.

### Scaled Metrics

`@ScaledMetric var iconSize: CGFloat = 24` automatically scales with Dynamic Type. Custom fonts scale automatically too. Images embedded in `Text` size with the surrounding text.

### Custom Accent Color

Assets catalog → Accent Color (auto-created in new projects) → set per-platform colors. Cyber/sidebar icons follow this color via `listItemTint(_:)` modifier. Switch fills, button tints, etc. all customizable per-control via style modifiers.

## System Integration

### Link & openURL

```swift
Link("Open News", destination: URL(string: "https://...")!)
@Environment(\.openURL) var openURL
Button("Open") { openURL(url, completion: { _ in }) }
```

Universal links open directly into other apps. Links work in widgets too.

### Drag and Drop with UTI

Built on the new Uniform Type Identifiers framework — strongly typed:

```swift
.onDrop(of: [.image], isTargeted: nil) { providers in ... }
```

### Sign In With Apple Button (SwiftUI-Native)

```swift
SignInWithAppleButton(.signIn,
  onRequest: { req in req.requestedScopes = [.fullName, .email] },
  onCompletion: { result in ... })
```

Just import `AuthenticationServices` and `SwiftUI` together; the button is provided. Same pattern for video players (AVKit), maps (MapKit), AppClip overlay (StoreKit).

## Previews — Aggressively Useful

`PreviewProvider` previews can cover Dark Mode, Dynamic Type sizes, locales, layout direction, and device idioms. The flow Apple recommends:
- Build views entirely in the canvas. Don't run the simulator until you want to feel the real responsiveness.
- Add multiple previews to test light/dark + small/XXL Dynamic Type + RTL/LTR + Mac/iPad idioms simultaneously.
- Use a "preview asset catalog" for sample data so previews never reach the network.
- Build views to use `Constant(_:)` bindings for previewing (`@Binding` views can preview by passing `.constant(false)`).

The "Visually Edit SwiftUI Views" session (10185) drives this home: command-click → "Embed in HStack/Group/etc.", control-option-click → in-canvas inspector to avoid the side panel, library has both views and modifiers searchable, drag-and-drop into the canvas updates the source.

## Document-Based Apps in SwiftUI

```swift
DocumentGroup(newDocument: ShapeDocument()) { file in
  ContentView(document: file.$document)
}
```

`ShapeDocument` conforms to `FileDocument` (or `ReferenceFileDocument`) — declare which UTIs you read/write, implement `init(configuration:)` and `fileWrapper(configuration:)`. iOS gets the document browser; Mac gets new-window-per-document and standard menus.

## Cross-References
- [widgets-and-widgetkit.md](widgets-and-widgetkit.md) — widgets are SwiftUI-only.
- [swift-5.3-language.md](swift-5.3-language.md) — multiple trailing closures, `@main`, builder inference all enable SwiftUI's syntax.
- [big-sur-design-system.md](big-sur-design-system.md) — toolbars, accent colors, SF Symbols all complement these APIs.
- [ipados-pointer-scribble.md](ipados-pointer-scribble.md) — the new pointer interactions are framework-agnostic but blend with SwiftUI views.

## Adoption Checklist
- [ ] Migrate from `@ObservedObject var store = Store()` to `@StateObject` for view-owned objects.
- [ ] Add `@SceneStorage` for per-scene UI state restoration.
- [ ] Add `@AppStorage` for app-wide preferences instead of UserDefaults plumbing.
- [ ] Replace iOS-specific NavigationView push/pop patterns with outline `List` where appropriate.
- [ ] Use `LazyVGrid` / `LazyHGrid` instead of `UICollectionViewCompositionalLayout` where feasible.
- [ ] Use `Label`, `Link`, and the toolbar API instead of bespoke title/icon combinations.
- [ ] Adopt `ContainerRelativeShape` in widgets and any container-aware views.
- [ ] Build a multi-preview setup that catches Dark Mode + Dynamic Type + RTL bugs early.
- [ ] If document-based, migrate to `DocumentGroup` + `FileDocument` instead of UIDocumentBrowserViewController plumbing.
