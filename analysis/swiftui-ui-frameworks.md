# SwiftUI, UI Frameworks, and Design System -- WWDC 2025 Deep Analysis

> Analysis of 16 sessions covering Liquid Glass adoption, SwiftUI new APIs, UIKit modernization, spatial layout, widgets, and the new design system.

---

## 1. Liquid Glass: The New Design Foundation

### Core Design Principles (WWDC25-219, WWDC25-356)

Liquid Glass is not simply a visual effect -- it is a meta-material system that defines a new **functional layer** in the UI hierarchy. Key principles:

- **Lensing over blurring**: Unlike previous materials that scattered light, Liquid Glass dynamically bends, shapes, and concentrates light in real time (WWDC25-219).
- **Two variants only**: Regular (adaptive, versatile, use everywhere) and Clear (permanently transparent, only for media-rich backgrounds with bold content on top). Never mix them (WWDC25-219).
- **Never stack glass on glass**: "Avoid glass on glass. Stacking Liquid Glass elements on top of each other can quickly make the interface feel cluttered and confusing." When elements must sit on glass, use fills, transparency, and vibrancy instead (WWDC25-219).
- **Tinting is semantic, not decorative**: Use tint only to convey meaning -- a call to action or next step -- not for visual effect. "When every element is tinted, nothing stands out" (WWDC25-219, WWDC25-323).
- **Materialize/dematerialize, never fade**: Glass elements should animate in/out by setting the effect property, not alpha. "Always prefer setting the effect property over the alpha to ensure that the glass dematerializes or materializes with the appropriate animation" (WWDC25-284).

### Concentricity -- The Quiet Geometry (WWDC25-356, WWDC25-310)

A button positioned at the bottom of a sheet should share the same corner center with the corners of the sheet. Three shape types build concentric layouts:

- **Fixed shapes**: constant corner radius
- **Capsules**: radius = half the height
- **Concentric shapes**: radius = parent radius minus padding

**Best practice**: Use `concentricRectangle` shape with `containerConcentric` configuration in SwiftUI to automatically match container corners (WWDC25-323). In AppKit, use `.containerRelative()` cornerConfiguration (WWDC25-310).

**Hidden gem**: "Here's a neat trick for managing components that need to work both inside a container and on their own: use a concentricShape with a fallback radius. The concentric value adapts when nested, and the fallback kicks in when the component stands alone" (WWDC25-356).

### Scroll Edge Effects (WWDC25-219, WWDC25-356, WWDC25-284)

- Two styles: **Soft** (default, subtle blur/fade, preferred on iOS/iPadOS) and **Hard** (opaque boundary, preferred on macOS, for dense UIs with pinned headers).
- "Scroll edge effects are not decorative. They don't block or darken like overlays. They simply clarify where UI and content meet, and shouldn't be used where there aren't any floating UI elements" (WWDC25-356).
- Apply one scroll edge effect per view. In split view layouts, each pane can have its own.
- **Never mix or stack** soft and hard styles together.
- Custom containers can adopt edge effects via `ScrollEdgeElementContainerInteraction` in UIKit (WWDC25-284) or `scrollEdgeEffectStyle` in SwiftUI (WWDC25-323).

### Migration Checklist for Liquid Glass

1. Build your app with Xcode 26 -- most updates are automatic (WWDC25-323, WWDC25-284, WWDC25-310).
2. **Remove** custom background colors behind sheets (`presentationBackground`) -- let the new material shine (WWDC25-323).
3. **Remove** extra backgrounds or darkening effects behind bar items -- these interfere with the scroll edge effect (WWDC25-323).
4. **Remove** `UIBarAppearance` or `backgroundColor` customization from navigation and toolbars -- these interfere with glass appearance (WWDC25-284).
5. **Remove** `NSVisualEffectView` from sidebar content views -- the legacy sidebar material prevents glass from showing through (WWDC25-310).
6. **Audit** every screen for corners that feel "pinched or flared" -- they break concentricity (WWDC25-356).
7. Icons should use **monochrome rendering** in toolbars -- "The monochrome palette reduces visual noise, emphasizes your app's content, and maintains legibility" (WWDC25-323).

---

## 2. SwiftUI New APIs and Patterns

### Performance Improvements (WWDC25-256)

Major wins announced:
- **Lists on macOS**: Over 100,000 items now load **6x faster** and update up to **16x faster**.
- **Scrolling**: Dropped frames during scroll are significantly reduced. SwiftUI now does preparatory work before visible, reducing the amount of work done during the frame deadline.
- **New SwiftUI Performance Instrument** in Xcode with lanes for long view body updates, platform view updates, etc. See "Optimize SwiftUI performance with Instruments" (WWDC25-306).

### New @Animatable Macro (WWDC25-256)

Replaces the manual `animatableData` property on `Shape` conformances:

```swift
@Animatable
struct LoadingArc: Shape {
    var center: CGPoint
    var radius: CGFloat
    var startAngle: Angle
    var endAngle: Angle
    @AnimatableIgnored var drawPathClockwise: Bool
    // No need for manual animatableData anymore
}
```

**Best practice**: Use `@AnimatableIgnored` to exclude properties you don't want to animate.

### Toolbar APIs (WWDC25-256, WWDC25-323)

- **`ToolbarSpacer(.fixed)`**: Separates toolbar items into distinct glass groups to show relatedness.
- **`ToolbarSpacer(.flexible)`**: Creates expanding space between items (e.g., Mail's leading filter + trailing search/compose).
- **`sharedBackgroundVisibility`**: Separate an item into its own group without a shared glass background.
- **`badge` modifier** on toolbar items: One-line badge indicators.
- **Tinting**: Apply `.borderedProminent` button style with `.tint(.pink)` to toolbar items for emphasis.

### Tab Bar Enhancements (WWDC25-323, WWDC25-284)

- **`tabBarMinimizeBehavior(.onScrollDown)`**: Tab bar collapses on scroll, re-expands on reverse scroll.
- **`tabViewBottomAccessory`**: Place persistent views (e.g., mini player) above the tab bar. Read `tabViewBottomAccessoryPlacement` from environment to adjust content when it collapses.
- **Search tab role**: `Tab(role: .search)` makes a dedicated search tab that morphs into a search field.
- **`searchToolbarBehavior`**: Explicitly opt into minimized search field behavior.

### Search Improvements (WWDC25-323, WWDC25-284)

- Search is now **bottom-aligned on iPhone** -- more ergonomic to reach. No code changes needed when `.searchable` is on `NavigationSplitView`.
- On iPad: search appears in **top-trailing corner**.
- Tab-based search: `Tab(role: .search)` on a TabView replaces the tab bar with a search field.
- UIKit: `searchBarPlacementAllowsExternalIntegration = true` for trailing-edge search on iPad.
- UIKit: `searchBarPlacementBarButtonItem` for toolbar-integrated search.

### Glass Effect for Custom Views (WWDC25-323, WWDC25-284, WWDC25-310)

**SwiftUI:**
```swift
.glassEffect()                          // Default capsule shape
.glassEffect(.interactive)              // Adds scale/bounce/shimmer on touch (iOS)
.glassEffect(in: .rect(cornerRadius: 12)) // Custom shape
```

**Critical**: Use `GlassEffectContainer` to group multiple glass elements. "Glass cannot sample other glass, so having nearby glass elements in different containers will result in inconsistent behavior" (WWDC25-323).

**Fluid morphing** between glass elements: Use `glassEffectID` modifier with a local namespace.

**UIKit:**
```swift
let effectView = UIVisualEffectView()
let glassEffect = UIGlassEffect()
UIView.animate { effectView.effect = glassEffect }
```
- `UIGlassContainerEffect` for grouping.
- `cornerConfiguration = .containerRelative()` for automatic concentricity.
- `glassEffect.isInteractive = true` for tap reactions.

**AppKit:**
- `NSGlassEffectView` with `contentView` property. "Set each one's contentView property to the desired view. The glass effect view ties its geometry to the contentView using Auto Layout" (WWDC25-310).
- `NSGlassEffectContainerView` for grouping -- also improves performance since it "only needs one sampling pass for the entire group" (WWDC25-310).

### Background Extension Effect (WWDC25-323, WWDC25-284, WWDC25-310)

Allows content to extend behind floating sidebars without clipping:

**SwiftUI**: `.backgroundExtensionEffect()` modifier -- mirrors and blurs content outside safe area.

**UIKit**: `UIBackgroundExtensionView` with `contentView` property. Set `automaticallyPlacesContentView = false` for manual layout control.

**AppKit**: `NSBackgroundExtensionView` -- "Assign it a content view, which it positions in the safe area, avoiding the floating sidebar."

### Rich Text Editing with AttributedString (WWDC25-280)

Major new capability -- `TextEditor` now supports `AttributedString`:

```swift
@Binding var text: AttributedString
TextEditor(text: $text)
```

**Supported attributes**: bold, italic, underline, strikethrough, custom fonts, point size, foreground/background colors, kerning, tracking, baseline offset, Genmoji, paragraph styling (line height, text alignment, base writing direction).

**Key patterns:**
- `AttributedTextSelection` for tracking selection (uses `RangeSet`, not single `Range`, to support bidirectional text).
- `AttributedTextFormattingDefinition` protocol to constrain which attributes your editor supports.
- `AttributedTextValueConstraint` protocol to enforce attribute value rules (e.g., ingredients always green).
- `transform(updating: &selection)` to safely mutate text without invalidating selection indices.
- `inheritedByAddedText = false` on custom AttributedStringKeys to prevent attribute expansion.
- `invalidationConditions: [.textChanged]` to remove attribute when text is modified.

**Hidden gem**: "Any mutation to an AttributedString invalidates all of its indices, even those not within the bounds of the mutation" (WWDC25-280). Always use `transform(updating:)`.

### Window and Scene APIs (WWDC25-256, WWDC25-290)

- **`.windowResizeAnchor(.top)`**: Controls where window resize animation originates on macOS.
- **`.commands { TextEditingCommands() }`**: Menu bar commands now work on iPad too (swipe down from top).
- **`UIRequiresFullscreen` is deprecated** in iPadOS 26 -- migrate off this.
- macOS window resizing now synchronizes animation between content and window frame.

### Drag and Drop Enhancements (WWDC25-256)

- **`draggable(containerItemID:)`** + **`dragContainer(for:selection:)`**: Multi-item drag from grid/list with lazy item transfer.
- **`DragConfiguration(allowMove: false, allowDelete: true)`**: Customize supported operations.
- **`onDragSessionUpdated`**: Observe drag events including `.ended(.delete)`.
- **`dragPreviewsFormation(.stack)`**: Control how drag previews look.

### WebView for SwiftUI (WWDC25-256)

New `WebView` and `WebPage` types:
```swift
WebView(url: myURL)
// Or with full control:
@State private var page = WebPage()
WebView(page)
```
`WebPage` is an observable model supporting programmatic navigation, page property access, JavaScript execution, custom URL schemes, and user agent customization.

---

## 3. UIKit Modernization

### Mandatory UIScene Lifecycle (WWDC25-243, WWDC25-282)

**Critical deadline**: "In the release following iOS 26, any UIKit app built with the latest SDK will be required to use the UIScene life cycle, otherwise it will not launch" (WWDC25-243).

Action items:
- Adopt scene-based lifecycle now using tech note TN3187.
- Legacy `UIApplicationDelegate` callbacks and `UIApplicationLaunchOptionKeys` are deprecated.
- Only the `init(windowScene:)` initializer for `UIWindow` remains.
- Remove `UIRequiresFullscreen` -- deprecated and will be ignored in a future release (WWDC25-282).

### Automatic Observation Tracking (WWDC25-243)

UIKit now integrates Swift `@Observable` at its core:

- In update methods like `layoutSubviews`, UIKit automatically tracks any Observable you reference and invalidates views.
- **Back-deployable to iOS 18** via `UIObservationTrackingEnabled` Info.plist key. Enabled by default on iOS 26.
- Works in `configurationUpdateHandler` closures for collection view cells.

### New `updateProperties()` Method (WWDC25-243)

- Runs just before `layoutSubviews` but is independent -- invalidate properties without forcing layout.
- Use for populating content, applying styling, configuring behaviors.
- Automatically tracks any Observable you read.
- Manual trigger: `setNeedsUpdateProperties()`.
- **Performance tip**: "By using updateProperties to configure the view instead of layoutSubviews, I avoid re-running the code on unrelated events, like resizing, cutting unnecessary work" (WWDC25-243).

### Animation Improvements (WWDC25-243)

- **`UIView.animate(options: .flushUpdates)`**: Automatically animates changes to Observable properties and Auto Layout constraints without calling `layoutIfNeeded()`.

### Scene Bridging: SwiftUI Scenes in UIKit Apps (WWDC25-243, WWDC25-290)

```swift
class MyDelegate: NSObject, UIHostingSceneDelegate {
    static var rootScene: some Scene {
        WindowGroup(id: "my-volume") { ContentView() }
            .windowStyle(.volumetric)
    }
}
```
- Enables UIKit apps to add volumes and immersive spaces on visionOS.
- Request scenes via `UISceneSessionActivationRequest(hostingDelegateClass:id:)`.
- Also available for AppKit via matching API.

### iPad Menu Bar (WWDC25-243)

- Swipe from top reveals full menu bar on iPad.
- `UIMainMenuSystem.Configuration` for declaring supported commands.
- `UIMenuBuilder` upgraded with better convenience methods, faster performance.
- **Important**: Menu bars defined in storyboards are **no longer supported** -- must implement programmatically.
- `UIKeyCommand.repeatBehavior = .nonRepeatable` for destructive actions.
- Focus-based `UIDeferredMenuElement` for dynamic menu content.

### UISplitViewController Improvements (WWDC25-282, WWDC25-243)

- **Interactive column resizing** by dragging separators.
- **Inspector column** support -- first-class, presents as sheet when collapsed.
- New `splitViewControllerLayoutEnvironment` trait to detect expanded/collapsed state.
- Customizable min/max/preferred column widths.

### Navigation Transitions (WWDC25-284)

- Navigation slide transitions are now **always-interactive and interruptible** (like zoom transitions from iOS 18).
- **Content backswipe**: Can now swipe back anywhere in the content area, not just the leading edge.
- Custom gestures needing priority: set failure requirements on `interactiveContentPopGestureRecognizer`.

### Slider Enhancements (UIKit) (WWDC25-284)

- **Tick marks**: `slider.trackConfiguration = .init(allowsTickValuesOnly: true, numberOfTicks: 5)`
- **Neutral value**: `slider.trackConfiguration.neutralValue = 0.2` -- anchors fill at arbitrary position
- **Thumbless style**: `slider.sliderStyle = .thumbless` -- great for media playback progress bars

### HDR Color Support (WWDC25-243)

- `UIColor(red:green:blue:alpha:linearExposure:)` -- HDR colors with adjustable brightness.
- `UIColorPickerViewController.maximumLinearExposure` for HDR color picking.
- `UITraitHDRHeadroomUsageLimit` trait to monitor when to fall back to SDR.

---

## 4. Spatial Layout and visionOS

### SwiftUI 3D Layout System (WWDC25-273)

All SwiftUI views are now truly 3D on visionOS with width, height, **depth**, and Z position:

- **`scaledToFit3D()`**: Maintains 3D aspect ratio while scaling to available space.
- **Depth Alignments**: `.depthAlignment(.front)`, `.center`, `.back` on any Layout type. Create custom depth alignments via `DepthAlignmentID` protocol.
- **`rotation3DLayout`**: New modifier that **modifies the layout frame** (unlike `rotation3DEffect` which is visual-only). "The layout system won't adjust the size or placement of views due to visual effects" (WWDC25-273).
- **`SpatialContainer`**: Place multiple views in the same 3D space with 3D alignment.
- **`spatialOverlay`**: Overlay a single view in the same 3D space as another.

**Hidden gem**: Existing 2D custom `Layout` types work in 3D on visionOS with sensible default depth behaviors -- no changes needed.

### SwiftUI + RealityKit Integration (WWDC25-274)

**Model3D Enhancements:**
- `Model3DAsset` for loading and controlling animations.
- `AnimationPlaybackController` is now `@Observable` -- drive UI from animation state.
- `ConfigurationCatalog` support for switching model representations.

**Transitioning Model3D to RealityView:**
- `.realityViewLayoutBehavior(.fixedSize)` makes RealityView tightly wrap model bounds like Model3D.
- Other options: `.flexible` (default, fills available space), `.centered` (centers contents).

**New Components in visionOS 26:**
- `ViewAttachmentComponent` -- add SwiftUI views directly to entities.
- `GestureComponent` -- add gestures to entities with values in entity coordinate space.
- `PresentationComponent` -- present popovers/sheets from within RealityKit scenes.
- `ManipulationComponent` -- one-line object manipulation (move, rotate, scale with hands).

**Observable Entities**: Entities are now `@Observable`. Read `entity.observable.position` etc. to drive SwiftUI updates.

**Avoiding infinite loops**: "Don't modify your observed state within your update closure" in RealityView. Split large views into smaller ones. Prefer modifying entities in gesture closures or custom Systems, not the update closure (WWDC25-274).

**SwiftUI-driven RealityKit animations**: `entity.animate(.bouncy) { entity.position = newPosition }` -- implicit animation of Transform and other components.

**Unified Coordinate Conversion**: `CoordinateSpace3D` protocol bridges SwiftUI and RealityKit coordinate spaces. `GeometryProxy3D.coordinateSpace3D()` provides the SwiftUI side.

### visionOS Scene Management (WWDC25-290)

- **Window locking**: Windows/volumes can be locked to physical rooms for persistence.
- **`.restorationBehavior(.disabled)`**: Opt transient windows out of restoration.
- **`.defaultLaunchBehavior(.suppressed)`**: Prevent secondary windows from returning on relaunch.
- **`Window` (not `WindowGroup`)**: Unique windows that cannot be duplicated.
- **Surface snapping**: Volumes/windows snap to physical surfaces. `SurfaceSnappingInfo` environment value with `.classification` (requires world sensing permission).
- **Clipping margins**: `preferredWindowClippingMargins` renders non-interactive visual flourish outside scene bounds.
- **Presentations in volumes**: All presentation types (menus, tooltips, popovers, sheets, alerts) now work in volumes, ornaments, and RealityView attachments.
- **`presentationBreakthroughEffect`**: `.subtle`, `.prominent`, or `.none` for 3D content occlusion.
- **RemoteImmersiveSpace**: Stream immersive content from Mac to Vision Pro.
- **CompositorContent**: New builder type giving CompositorLayer access to SwiftUI environment variables and modifiers.
- **Progressive immersion**: New `.portrait` aspect ratio option for vertical experiences.
- **`.immersiveEnvironmentBehavior(.coexist)`**: Mixed immersive spaces can coexist with system environments.

---

## 5. Swift Charts 3D (WWDC25-313)

New `Chart3D` view for 3D data visualization on iOS, macOS, and visionOS:

- `PointMark`, `RuleMark`, `RectangleMark` all updated for 3D.
- **`SurfacePlot`**: 3D extension of `LinePlot` for mathematical surfaces.
- **`Chart3DPose`**: Control initial viewing angle with azimuth and inclination.
- **Camera projection**: `.orthographic` (default, no perspective distortion) and `.perspective` (depth perception with convergence).
- **Surface styles**: `.heightBased` and `.normalBased` foreground styles, plus gradients.
- **Best practice**: "3D charts work great when the shape of the data is more important than the exact values. Interactivity is key to understanding 3D datasets, so only consider 3D charts if requiring interaction enhances the experience" (WWDC25-313).

---

## 6. Widgets and Live Activities (WWDC25-278, WWDC25-334)

### New Platforms

- **visionOS**: Widgets can be pinned to surfaces. Elevated or recessed mounting styles. Glass or paper textures. New `systemExtraLargePortrait` family. `levelOfDetail` environment value for distance-based simplification.
- **CarPlay**: Widgets render in StandBy style. Live Activities via `supplementalActivityFamilies([.small])`.
- **macOS**: Live Activities from paired iPhone appear in menu bar.
- **watchOS 26**: Controls in Control Center, Smart Stack, and Action button.

### Accented Rendering Mode (WWDC25-278)

Use `widgetRenderingMode` environment variable to conditionally display content for glass/accented modes. `widgetAccentedRenderingMode` modifier options: `nil` (primary), `.accented`, `.desaturated`, `.accentedDesaturated`, `.fullColor`.

### Relevance Widgets (WWDC25-278, WWDC25-334)

New `RelevanceConfiguration` with `RelevanceEntriesProvider` -- widgets appear in Smart Stack only when relevant. Uses `WidgetRelevanceAttribute` with context types like `.date(interval:kind:)` and `.location(category:)`.

**Hidden gem**: Use `associatedKind` modifier to prevent duplication when you have both a timeline widget and a relevance widget for the same content (WWDC25-334).

### Push Widget Updates (WWDC25-278)

Server-sent push notifications can trigger widget timeline reloads:
- Implement `WidgetPushHandler` protocol.
- Add `.pushHandler(MyHandler.self)` to widget configuration.
- Add Push Notification entitlement to widget extension.
- Send HTTPS POST to APNs with `.push-type.widgets` topic suffix.

### watchOS 26 Specifics (WWDC25-334)

- **ARM64 architecture**: Apple Watch Series 9+ now uses arm64 on watchOS 26. Use Standard Architectures build setting. Be aware of type differences (Float, Int, pointer math).
- **Configurable widgets on watch**: Return empty array from `recommendations()` to enable in-place configuration.
- **Controls on Apple Watch**: Built with WidgetKit. iPhone controls can appear on Apple Watch even without a Watch app. Tap executes action on companion iPhone.
- When to build what: Control = perform action, Widget = display info throughout day, Live Activity = events with clear start/end.

---

## 7. SF Symbols 7 (WWDC25-337)

### Draw Animation System

- **Draw On/Draw Off**: New animation presets that imitate handwritten stroke paths.
- Three playback options, previewed in SF Symbols app.
- **Variable Draw**: Renders path at specific percentage for progress/strength visualization.
- Draw Off has a "reverse" switch to control direction.

### Magic Replace Enhancements

- Draw Off for outgoing symbol + Draw On for incoming symbol.
- Enclosure matching preserves shared enclosures during transitions.

### Gradients

- New color rendering mode: `.gradient` -- auto-generated linear gradient from single source color.
- Available across all rendering modes, custom and system symbols.
- "Gradients render great at all scales and sizes, but really stand out in larger instances" (WWDC25-337).

### Custom Symbol Annotation

- Annotate regular weight first (base annotation), system interpolates to ultralight and black.
- Minimum 2 guide points (start + end) per draw path.
- Corner guide points for sharp bends.
- Adaptive end caps via context menu on start points.
- Subpath selection in layer list for overlapping paths.
- Guide points must be in same order across weight templates.

### API Integration

**SwiftUI:**
```swift
Image(systemName: "pencil")
    .symbolEffect(.drawOn)              // Draw animation
    .symbolRenderingMode(.gradient)     // Gradient rendering
```

**UIKit:**
```swift
button.configuration?.symbolContentTransition = UISymbolContentTransition(.replace)
```

---

## 8. AppKit Design Adoption (WWDC25-310)

### Key AppKit-Specific APIs

- **`NSToolbarItem.isBordered = false`**: Remove glass from non-interactive items (status indicators, informational text).
- **`NSToolbarItem.style = .prominent`**: Tint glass with accent color.
- **`NSToolbarItem.backgroundTintColor`**: Custom glass tint color.
- **`NSItemBadge`**: `.count(4)`, `.text("New")`, `.indicator` for toolbar item badges.
- **`NSSplitViewItem.automaticallyAdjustsSafeAreaInsets = true`**: Allow content to extend under floating sidebar.
- **`NSView.LayoutRegion`** with corner adaptation for avoiding window corners.
- **Split item accessories**: `NSSplitViewItemAccessoryViewController` for top/bottom-aligned accessories within split views.
- **`prefersCompactControlSizeMetrics`**: Revert to pre-Tahoe control sizing for dense layouts.
- **`NSButton.borderShape`**: Override shape (capsule/roundedRect) for concentricity.
- **`NSButton.bezelStyle = .glass`**: Liquid Glass material for floating buttons.
- **`tintProminence`**: Four levels (automatic, none, secondary, primary) for controlling button visual weight.

### Window Corner Radius Changes

- Windows with toolbars use a larger corner radius wrapping concentrically around glass toolbar elements.
- Titlebar-only windows retain a smaller radius.
- Use `NSView.LayoutRegion` API with `.safeArea(cornerAdaptation: .horizontal)` to avoid corner clipping.

---

## 9. Cross-Session References and Learning Paths

### Liquid Glass Adoption Path
1. "Meet Liquid Glass" (WWDC25-219) -- design principles
2. "Get to know the new design system" (WWDC25-356) -- best practices
3. Platform-specific: WWDC25-323 (SwiftUI), WWDC25-284 (UIKit), WWDC25-310 (AppKit)

### Performance Path
- "Optimize SwiftUI performance with Instruments" (WWDC25-306)
- "Explore concurrency in SwiftUI" (WWDC25-266)
- "Embracing Swift concurrency" (WWDC25-268)

### Spatial/visionOS Path
- "Meet SwiftUI spatial layout" (WWDC25-273)
- "Better together: SwiftUI and RealityKit" (WWDC25-274)
- "Set the scene with SwiftUI in visionOS" (WWDC25-290)
- "Bring Swift Charts to the third dimension" (WWDC25-313)

### UIKit Modernization Path
- "What's new in UIKit" (WWDC25-243)
- "Build a UIKit app with the new design" (WWDC25-284)
- "Make your UIKit app more flexible" (WWDC25-282)
- "Elevate the design of your iPad app" (WWDC25-208)

### Widget Path
- "What's new in widgets" (WWDC25-278)
- "What's new in watchOS 26" (WWDC25-334)
- "Design widgets for visionOS" (WWDC25-255)

---

## 10. Critical Action Items Summary

| Priority | Action | Source |
|----------|--------|--------|
| **Urgent** | Adopt UIScene lifecycle -- will be **required** in the release following iOS 26 | WWDC25-243 |
| **Urgent** | Remove `UIRequiresFullscreen` -- deprecated, will be ignored | WWDC25-282 |
| **High** | Remove custom bar backgrounds, presentation backgrounds, and NSVisualEffectView from sidebars | WWDC25-323/284/310 |
| **High** | Remove storyboard-defined menu bars (UIKit) -- no longer supported | WWDC25-243 |
| **High** | Build for arm64 on watchOS 26, test type differences | WWDC25-334 |
| **Medium** | Adopt `updateProperties()` instead of `layoutSubviews` for property updates | WWDC25-243 |
| **Medium** | Use `GlassEffectContainer`/`UIGlassContainerEffect`/`NSGlassEffectContainerView` when grouping glass elements | WWDC25-323/284/310 |
| **Medium** | Add symbols to menu items across platforms | WWDC25-356/310 |
| **Medium** | Consider `RelevanceConfiguration` for watchOS widgets | WWDC25-334 |
| **Low** | Adopt push widget updates for cross-device sync | WWDC25-278 |
| **Low** | Add `supplementalActivityFamilies([.small])` for CarPlay/Watch Live Activities | WWDC25-278 |
