# SwiftUI Debut — WWDC 2019 Analysis

**Sessions covered:** 204 (Introducing SwiftUI: Building Your First App), 216 (SwiftUI Essentials), 226 (Data Flow Through SwiftUI), 231 (Integrating SwiftUI), 237 (Building Custom Views with SwiftUI), 238 (Accessibility in SwiftUI), 219 (SwiftUI on watchOS), 240 (SwiftUI On All Devices), 233 (Mastering Xcode Previews)

## Headline

WWDC 2019 introduced SwiftUI — a declarative, cross-platform UI framework built on top of Swift 5.1's new property wrappers, function builders (later @resultBuilder), and opaque return types (`some View`). It is the biggest shift in Apple UI development since UIKit launched in 2008.

## The Core Mental Model (sessions 216, 226)

- A view is a `struct` that conforms to `View`. It has one requirement: a computed `body` property of `some View`.
- Views are **lightweight value types** allocated on the stack — "extracting a subview has virtually no runtime overhead." Compose freely.
- SwiftUI is **declarative**: you describe what you want, not how to build it. The framework collapses the tree into an efficient internal data structure for rendering.
- Views are a **function of state**, not a sequence of events. There is exactly one entry point: `body`. UIKit's exponential ordering complexity (12 events ≈ 12! orderings) collapses to a single deterministic invocation. (Kyle Macomber's pivotal slide in 204.)

## Data Flow Tools (session 226)

| Tool | When to use |
|---|---|
| Plain `let` property | Read-only data passed in by parent |
| `@State private var` | Local source of truth owned by the view; framework allocates persistent storage |
| `@Binding` | Two-way reference to state owned elsewhere; no initial value, no source of truth |
| `BindableObject` (later renamed `ObservableObject`) + `@ObjectBinding` (later `@ObservedObject`) | External reference-type model with a `didChange` Combine publisher |
| `@EnvironmentObject` | Inject shared model down a subtree |
| `@Environment(\.someKeyPath)` | Read environment values like `colorScheme`, `sizeCategory`, `layoutDirection`, `isEnabled`, `locale` |

**Best practice:** "Lift state up into a common ancestor and let children have a binding to it" — duplicated source of truth is the #1 SwiftUI bug source.

**Best practice:** Always mark `@State` properties `private` to enforce that state is owned by that view alone.

## Conditional Views: Two Patterns (216)

- Use `if`/`else` in a ViewBuilder when you genuinely want to add/remove views from the hierarchy. Default animation is a crossfade.
- For style toggles (e.g., rotation, color), put the condition **inside the modifier** (`rotationEffect(flipped ? .degrees(180) : .zero)`). SwiftUI then animates between the two states correctly. **HIDDEN GEM**: pushing conditions into modifiers gives you better animations for free.

## Lists, ForEach, Identifiable (204)

- `List(rooms) { room in ... }` — no data sources, no delegates.
- Mixing static and dynamic content: wrap dynamic content in `ForEach`, put static elements alongside.
- `.onDelete { offsets in ... }` and `.onMove { src, dst in ... }` modifiers added directly on `ForEach`.
- Make types `Identifiable` and `ForEach` automatically synthesizes correct insert/delete/move animations — **no more `NSInternalInconsistencyException` from data source / view mismatch.**

## Bindings as Animations (226)

`Binding` has an `animation()` modifier: `Toggle(isOn: $isPlaying.animation())` will animate the resulting body diff. The framework computes the correct final state regardless of interruption.

## Localization Comes For Free (204)

- Text with a string literal is automatically localizable (compiler treats literal as `LocalizedStringKey`).
- `Text(roomName)` (string variable) is treated as already-localized content — passes through unchanged.
- String interpolation with `Text("\(count) rooms")` produces a properly formatted, localized format string. **HIDDEN GEM**: no more manual `NSLocalizedString(...)` wrapping for static UI strings.

## Accessibility Free Out of the Box (238)

- SwiftUI generates an Accessibility element for every primitive view (Text, Image, Button, Toggle, etc.) with appropriate label, role/traits, and default action — **with zero accessibility-specific code**.
- **HIDDEN GEM**: SwiftUI sends Accessibility notifications automatically when state changes. You no longer need to call `UIAccessibility.post(notification:)` — even for custom controls.
- Customize with `.accessibility(label:)`, `.accessibility(value:)`, `.accessibility(hint:)`, `.accessibilityAction(named:)`.

## Integrating SwiftUI With Existing Code (231)

- `UIHostingController(rootView: SwiftUIView())` embeds SwiftUI inside UIKit/AppKit.
- `UIViewRepresentable` / `UIViewControllerRepresentable` (and AppKit equivalents) wrap UIKit/AppKit views inside SwiftUI. Implement `makeUIView`, `updateUIView`, and an optional `Coordinator` for delegates.
- Adoption is incremental — bring SwiftUI in one screen at a time.

## Cross-platform Story (240)

- "Learn once, apply anywhere" — not "write once, run anywhere."
- Same `Toggle`, `Picker`, `Button`, `List`, `NavigationView`, `TabbedView` (later `TabView`) APIs render appropriately per platform.
- Picker on iPhone in a Form auto-becomes a navigation row → push to a list of options. No code change.
- Set `accentColor`, `disabled(true)`, environment values once at the top — they cascade down via the environment.

## Xcode Previews (233)

- Previews are **real running code**, not a renderer's guess. Custom assets, runtime config, and your code paths all work.
- Previews leverage Swift dynamic replacement: literal-only changes inject without recompile (instant feedback). Larger changes compile only the affected file.
- `PreviewProvider` returns `some View` — usually a `Group` of multiple configurations (devices, color schemes, content size categories, locales).
- **HIDDEN GEM:** the **Development Assets** group lets you ship preview-only assets that are stripped from the App Store build.
- Pin previews to compare alongside other devices/configurations. Use `previewLayout(.sizeThatFits)` for cells and small components.

## SwiftUI on watchOS (219)

- SwiftUI is the **only** way to build watchOS 6 complications and full Apple Watch UIs going forward beyond what WatchKit offers.
- Independent watch apps (no iPhone counterpart required) ship in watchOS 6 — see also session 208 (Creating Independent Watch Apps).

## URGENT / Migration Notes

- SwiftUI requires iOS 13 / macOS 10.15 / watchOS 6 / tvOS 13. There is no backport to earlier OSes. Apps targeting older OSes must keep UIKit/AppKit.
- Many WWDC 2019 SwiftUI APIs were renamed by 2020/2021: `BindableObject` → `ObservableObject`, `@ObjectBinding` → `@ObservedObject`, `TabbedView` → `TabView`, `NavigationButton` → `NavigationLink`, `PresentationLink` removed. Code from this session won't compile in a modern Xcode without updates.

## Cross-references

- Combine framework: 721, 722 (data flow plumbing under SwiftUI).
- Property wrappers, function builders, opaque return types: 402 (What's New in Swift), 415 (Modern Swift API Design).
- Modernizing UI for iOS 13: 224 (UIKit context for what SwiftUI replaces).
