# Spatial Computing, visionOS, RealityKit, and Immersive Media -- WWDC25 Deep Analysis

> Analysis of 12 WWDC25 sessions covering visionOS 26, RealityKit updates, Metal rendering for immersive apps, immersive video playback, spatial accessories, shared experiences, environment optimization, hover design, and widget design.

**Sessions analyzed:** 317, 287, 288, 289, 294, 296, 304, 305, 318, 403, 303, 255

---

## Table of Contents

1. [visionOS 26 Platform Overview](#1-visionos-26-platform-overview)
2. [RealityKit: New APIs and Architecture](#2-realitykit-new-apis-and-architecture)
3. [SceneKit to RealityKit Migration](#3-scenekit-to-realitykit-migration)
4. [Metal Rendering for Immersive Apps](#4-metal-rendering-for-immersive-apps)
5. [Immersive Video Ecosystem](#5-immersive-video-ecosystem)
6. [Apple Immersive Video Technologies](#6-apple-immersive-video-technologies)
7. [Spatial Accessories](#7-spatial-accessories)
8. [Shared Experiences and Nearby Sharing](#8-shared-experiences-and-nearby-sharing)
9. [Environment Optimization](#9-environment-optimization)
10. [Hover Interaction Design](#10-hover-interaction-design)
11. [Widget Design for visionOS](#11-widget-design-for-visionos)
12. [Cross-Session References](#12-cross-session-references)

---

## 1. visionOS 26 Platform Overview

*Source: WWDC25-317 -- What's new in visionOS 26*

### Key Platform Additions

- **Depth alignments for SwiftUI layouts**: Existing layout types (VStack, HStack) now support `.depthAlignment(.front)` for 3D spatial positioning.
- **`rotation3DLayout` modifier**: Enables layout-aware rotations in 3D space using any axis or angle.
- **`preferredWindowClippingMargins`**: Allows content to "peek" outside volume bounds without changing the volume's size -- enhancing immersiveness without requiring a full immersive space.
- **`realityViewSizingBehavior`**: New view modifier controlling how RealityView sizes itself relative to its 3D content.
- **Scene persistence**: Windows, scenes, and Quick Look content now persist and reappear in the same physical location, even after device restart.
- **`restorationBehavior(.disabled)` and `defaultLaunchBehavior(.suppressed)`**: New scene modifiers for controlling window restoration and auto-launch behavior.

### Best Practices

- Use `Model3D` with `.manipulable()` for drag-and-rotate interactions on SwiftUI 3D models, or `ManipulationComponent.configureEntity()` for RealityKit entities. (WWDC25-317)
- Use `ViewAttachmentComponent` to attach any SwiftUI view to a RealityKit entity -- replaces the old attachments closure pattern. (WWDC25-317)
- `GestureComponent` allows attaching SwiftUI gestures directly to RealityKit entities. (WWDC25-317)
- `QuickLook3DView` via `PreviewApplication.open(urls:)` enables viewing multiple 3D models simultaneously with built-in manipulation. (WWDC25-317)

### Hidden Gems

- **Environment Occlusion**: `EnvironmentBlendingComponent` automatically occludes virtual objects behind real-world static objects -- applied by default to pinned widgets and Quick Look 3D models. (WWDC25-317)
- **ImagePresentationComponent**: Uses on-device generative AI to convert monoscopic or spatial stereo content into 3D spatial scenes with motion parallax. (WWDC25-317)
- **Increased memory limits**: High-end iPad games can now be brought to Vision Pro via App Store Connect with little to no code changes. (WWDC25-317)
- **"Look to Scroll"**: Eyes-only scrolling enabled via `.scrollInputBehavior(.enabled, for: .look)` in SwiftUI or `lookToScrollAxes` in UIKit. (WWDC25-317)
- **Dynamic render quality in Compositor Services**: Control the resolution of rendered frames to balance fidelity vs. performance. Higher quality = larger textures = more memory. (WWDC25-317)
- **macOS spatial rendering**: Use `RemoteImmersiveSpace` to render immersive content on Mac and stream to Vision Pro. Uses same Compositor Services and ARKit frameworks. (WWDC25-317)
- **RealityKit now on tvOS**: A new platform for RealityKit content. (WWDC25-288)

### Enterprise APIs

- **Camera access in shared space**: Enterprise apps can now access the main camera concurrently with other spatial apps.
- **CameraRegionProvider (ARKit)**: Provides stabilized video feed of a select region of interest.
- **Protected Content API**: New API for protecting sensitive data.
- **Return to Service**: MDM-managed device sharing between team members with automatic data erasure.
- **SharedCoordinateSpaceProvider**: Enterprise entitlement enabling co-location without FaceTime/SharePlay.

---

## 2. RealityKit: New APIs and Architecture

*Source: WWDC25-287 -- What's new in RealityKit*

### New Components and APIs

#### ARKitAnchorComponent
Direct access to ARKit anchor data (transforms, extents) from RealityKit entities. Cast to specific anchor types like `PlaneAnchor` for surface dimensions.

```swift
guard let anchorComponent = event.entity.components[ARKitAnchorComponent.self] else { return }
guard let planeAnchor = anchorComponent.anchor as? PlaneAnchor else { return }
let worldSpaceFromExtent = planeAnchor.originFromAnchorTransform * planeAnchor.geometry.extent.anchorFromExtentTransform
```

#### AnchorStateEvents
Subscribe to `DidAnchor`, `WillUnanchor`, or `FailedToAnchor` events for reactive anchor lifecycle management:
```swift
content.subscribe(to: AnchorStateEvents.DidAnchor.self) { event in ... }
```

#### ManipulationComponent
Single-call setup for grab-and-rotate interactions:
```swift
ManipulationComponent.configureEntity(entity, collisionShapes: [shapes])
```
This automatically adds InputTarget, Collision, HoverEffect, and Manipulation components. Set `releaseBehavior = .stay` to prevent objects snapping back.

**ManipulationEvents**: `WillBegin`, `WillEnd`, `WillRelease`, `DidUpdateTransform`, `DidHandOff` -- use to coordinate physics mode changes during manipulation. (WWDC25-287)

#### EnvironmentBlendingComponent
Occludes virtual entities behind static real-world objects:
```swift
entity.components.set(EnvironmentBlendingComponent(preferredBlendingMode: .occluded(by: .surroundings)))
```
**Important**: Dynamic objects (people, pets) do NOT occlude. Only static environment features. (WWDC25-287)

#### MeshInstancesComponent
Draw a mesh multiple times with a single entity using only a list of transforms. Reduces GPU memory by sending model/material data only once:
```swift
let instances = try LowLevelInstanceData(instanceCount: 20)
meshInstancesComponent[partIndex: 0] = instances
instances.withMutableTransforms { transforms in ... }
```
On iOS/iPadOS/macOS/tvOS: Use `LowLevelBuffer` with `CustomMaterial` to make each instance visually unique. (WWDC25-287)

#### ImagePresentationComponent
Three presentation modes:
1. **2D photos**: `ImagePresentationComponent(contentsOf: url)` -- async initializer
2. **Spatial photos**: Set `desiredViewingMode = .spatialStereo` or `.spatialStereoImmersive`
3. **Spatial scenes (AI-generated 3D)**: Create `Spatial3DImage`, call `generate()`, then set `desiredViewingMode = .spatial3D`

The generation shows the same progress animation as the Photos app. (WWDC25-287)

#### Entity Loading from Data
```swift
let entity = try await Entity(from: data)
```
Load RealityKit scenes or USDs from network sources. Supports same formats as existing initializers. (WWDC25-287)

#### Entity Attach to Pins
`entity.attach(to:pin:)` -- attach entities to skeleton joint pins without manual alignment or expensive hierarchical transform updates. (WWDC25-287)

### Performance Tips

- **AVIF texture support**: Quality similar to JPEG with 10-bit color and significantly smaller file sizes. Export via Preview app or `usdcrush` CLI. (WWDC25-287)
- **MeshInstancesComponent** reduces draw calls significantly for repeated geometry. (WWDC25-287)
- **Scene understanding mesh**: Set `sceneUnderstanding: [.collision, .physics]` on `SpatialTrackingSession.Configuration` to enable virtual-to-real collisions. (WWDC25-287)

### Hidden Gems

- **HoverEffectComponent GroupIDs**: Override hierarchical hover effect propagation. Entities sharing a GroupID share activations regardless of hierarchy. Entities with GroupIDs do NOT propagate effects to children. (WWDC25-287)
- **Post-processing effects in RealityView**: `customPostProcessing` API for bloom, CIFilters, or custom Metal shaders. Supported on iOS, iPadOS, macOS, and tvOS (NOT visionOS). (WWDC25-287)
- **GestureComponent**: Attach SwiftUI gestures directly to entities. Each entity can have its own gesture with independent state via `@GestureState`. (WWDC25-317)

---

## 3. SceneKit to RealityKit Migration

*Source: WWDC25-288 -- Bring your SceneKit project to RealityKit*

### Key Takeaways

- **SceneKit is officially deprecated** across all platforms. This is a **soft deprecation** -- existing apps continue to work. No plan for hard deprecation yet. Apple will give ample notice if this changes. (WWDC25-288)
- SceneKit enters maintenance mode: only critical bug fixes, no new features.
- **RealityKit is the recommended path forward** for all new projects.

### Architecture Comparison

| Concept | SceneKit | RealityKit |
|---------|----------|------------|
| Object model | Node-based (properties on nodes) | Entity Component System (ECS) |
| Coordinate system | Same (X-right, Y-up, Z-toward-camera) | Same |
| Asset format | SCN files (proprietary) | USD (open standard) |
| View | SCNView / SceneView / ARSCNView | RealityView (single view for all platforms) |
| Scene editor | SceneKit Editor (Xcode) | Reality Composer Pro |

### Asset Conversion Best Practices

1. **Prefer original DCC files** (Blender, Maya) and export directly to USD. (WWDC25-288)
2. **Xcode export**: Select SCN asset > File > Export > Universal Scene Description Package. (WWDC25-288)
3. **`xcrun scntool`** (updated in Xcode 26): Convert SCN to USDZ with animation appending:
   ```bash
   xcrun scntool --convert max.scn --format usdz --append-animation max_spin.scn
   ```
4. SCN particle files cannot be directly converted -- recreate in Reality Composer Pro. (WWDC25-288)

### Animation Migration

- SceneKit: Load separate animation SCN files, traverse to find `SCNAnimationPlayer`, add to node.
- RealityKit: Animations stored in `AnimationLibraryComponent`, accessed by name:
  ```swift
  let library = entity.components[AnimationLibraryComponent.self]
  let anim = library.animations["spin"]
  entity.playAnimation(anim)
  ```

### Audio Migration

- Use `AudioLibraryComponent` (similar to `AnimationLibraryComponent`).
- Configure streaming, looping, and ambient vs. spatial directly in Reality Composer Pro.
- Alternative: Use `PlayAudioAction` entity action for minimal code.

### Post-Processing (New)

- RealityKit adds post-processing API on iOS, iPadOS, macOS, tvOS.
- Use `PostProcessEffect` protocol with Metal Performance Shaders:
  ```swift
  content.renderingEffects.customPostProcessing = .effect(BloomPostProcess())
  ```
- **Not available on visionOS** -- by design for performance reasons.

---

## 4. Metal Rendering for Immersive Apps

*Source: WWDC25-294 -- What's new in Metal rendering for immersive apps*

### New Render Loop: queryDrawables()

- Replaces `queryDrawable()` (singular). Returns an array of drawables. Usually 1, but 2 during high-quality Reality Composer Pro recording (`.builtIn` + `.capture`). (WWDC25-294)

### Hover Effects in Metal

- **Tracking areas texture**: New `.r8Uint` texture supporting up to 255 concurrent interactive objects.
- Register tracking areas per-object with unique identifiers. Add `.automatic` hover effect attribute.
- Write tracking area render values in fragment shader at `color(1)`.
- **MSAA consideration**: Tracking areas texture does not support MSAA resolve -- must handle manually. (WWDC25-294)
- `SpatialEventCollection.Event` now includes `trackingAreaIdentifier` for easier input handling.

### Dynamic Render Quality

- Set `maxRenderQuality` at configuration time, adjust at runtime via `layerRenderer.renderQuality`.
- **Only works with foveation enabled**.
- Recommended: 0.8 for menus/text, 0.6 for complex 3D scenes.
- Transitions between quality levels are smooth (not instant). (WWDC25-294)
- **Performance tip**: "Profile your app with your most complex scenes to make sure it has enough time to render its frames at a steady pace." (WWDC25-294)

### Progressive Immersion for Metal

- Progressive immersion style requires the **layered layout**.
- Uses a system-computed stencil buffer to mask content outside the portal.
- Portal fading is applied by the system as the last step on your command buffer.
- **Performance optimization**: Skip rendering pixels outside the portal stencil. (WWDC25-294)

### macOS Spatial Rendering

- **`RemoteImmersiveSpace`**: New SwiftUI scene type for Mac apps to render and stream to Vision Pro.
- `ARKitSession(device: remoteDeviceIdentifier)` connects Mac ARKit to Vision Pro sensors.
- Supports keyboard, mouse, gamepad, and pinch events via `onSpatialEvent`.
- `supportsRemoteScenes` environment variable for capability checking.
- All Compositor Services APIs have C equivalents (`cp_` prefix). (WWDC25-294)
- Only progressive and full immersion styles supported on Mac.

### Hidden Gems

- **Xcode template**: New visionOS app template with "Metal 4" option for immersive space renderer. Metal 3 still fully supported. (WWDC25-294)
- Can add SwiftUI scenes from AppKit/UIKit apps for immersive experiences. (WWDC25-294)

---

## 5. Immersive Video Ecosystem

*Source: WWDC25-296 -- Support immersive video playback in visionOS apps; WWDC25-304 -- Explore video experiences for visionOS*

### Video Profile Hierarchy (visionOS 26)

1. **2D video** -- flat rectilinear, all frameworks
2. **3D stereoscopic video** -- requires expanded experience for stereo
3. **Spatial video** -- stereo with spatial metadata, new immersive rendering in visionOS 26
4. **180/360/Wide FOV (APMP)** -- new in visionOS 26
5. **Apple Immersive Video** -- highest fidelity, now available to developers

### Apple Projected Media Profile (APMP)

- Metadata-based profile for 180, 360, and wide FOV content.
- Uses parametric immersive projection to model diverse lens profiles (focal length, skew, distortion).
- Automatic conversion for select third-party cameras (GoPro HERO13, Insta360 Ace Pro 2, Canon EOS VR, GoPro MAX, Insta360 X5).
- `avconvert` CLI updated for APMP conversion on macOS. (WWDC25-304)
- High motion detection automatically enabled for all APMP profiles. (WWDC25-304)

### New Dynamic Mask

- 2D and 3D videos can specify per-frame dynamic mask to animate frame size/aspect ratio during playback -- no letterboxing needed. (WWDC25-304)

### VideoPlayerComponent in RealityKit

Three immersive viewing modes:
- **Portal**: Windowed presentation. Mesh height = 1 meter by default. Scale X/Y uniformly.
- **Progressive** (NEW): Digital Crown controls immersion level. Requires `ImmersiveSpace` with `.progressive` ImmersionStyle.
- **Full**: 100% immersion.

**Critical rule**: Always match `desiredImmersiveViewingMode` with `ImmersionStyle` when rendering in a RealityView. (WWDC25-296)

### Spatial Video in RealityKit

- `desiredSpatialVideoMode = .spatial` enables spatial styling.
- Immersive spatial video uses `.full` viewing mode (not progressive).
- Use `mixed` ImmersionStyle with `.immersiveEnvironmentBehavior(.coexist)` for spatial video in system environments.
- Position immersive spatial video entities explicitly (e.g., `[0, 1.5, -1]`). Use head anchor for robust positioning. (WWDC25-296)

### Comfort Mitigation

- `VideoComfortMitigationDidOccur` event signals when system reduces immersion due to high camera motion.
- Three mitigation types: `.reduceImmersion` (progressive only), `.play`, `.pause`.
- **Best practice**: Use progressive viewing mode for APMP content to enable `reduceImmersion` mitigation. (WWDC25-296)

### SwiftUI Integration Tips

- Use `GeometryReader3D` to scale video portals to fit window size.
- Add `ModelSortGroupComponent` with `.planarUIPlacement` category to resolve co-planar sorting with UI. (WWDC25-296)
- Use `ImmersiveViewingModeWillTransition`/`DidTransition` events to toggle UI visibility during mode changes. (WWDC25-296)

### Framework Selection Guide

| Need | Framework |
|------|-----------|
| Quick preview of any media | Quick Look |
| Familiar video controls | AVKit |
| Custom immersive UI (games, etc.) | RealityKit |
| Browser playback | WebKit/Safari |

---

## 6. Apple Immersive Video Technologies

*Source: WWDC25-403 -- Learn about Apple Immersive Video technologies*

### AIVU File Format

- Apple Immersive Video Universal (`.aivu`) -- container with video + `PresentationDescriptor` metadata + `VenueDescriptor`.
- Playable via Files app / Quick Look on visionOS.
- `AIVUValidator.validate(url:)` to verify file correctness. (WWDC25-403)

### ImmersiveMediaSupport Framework (NEW)

- Available on macOS and visionOS 26.
- **VenueDescriptor**: Describes camera combinations (multi-camera setups). Contains `ImmersiveCamera` references with calibration, edge blend masks, origin positions, and custom backdrop environments.
- **PresentationDescriptor**: Per-frame dynamic metadata. Commands include camera selection, shot flops (auto-handles stereoscopic eye swap). (WWDC25-403)
- **ImmersiveMediaRemotePreviewSender/Receiver**: Send low-bitrate Apple Immersive Video frames from Mac to Vision Pro for live editorial preview. (WWDC25-403)

### Apple Spatial Audio Format (ASAF) and APAC

- ASAF: Production format for spatial audio creation.
- APAC (Apple Positional Audio Codec): Delivery encoding of ASAF for streaming.
- Tooling: Pro Tools plugins (per-user license) or DaVinci Resolve Studio. (WWDC25-403)

### Recommended Specs

- Resolution: 4320x4320 per eye
- Frame rate: 90 fps
- Color space: P3-D65-PQ
- Audio: Apple Spatial Audio
- Delivery: HLS with MV-HEVC encoding (WWDC25-403)

### Hidden Gems

- Every URSA Cine Immersive lens is individually factory-calibrated. Calibration data travels with every video file. (WWDC25-403)
- APMP content is NOT supported for inline embedded playback -- only expanded and immersive. (WWDC25-304)
- MV-HEVC encodes stereo by compressing one eye relative to the other, significantly reducing file size for streaming. (WWDC25-304)

---

## 7. Spatial Accessories

*Source: WWDC25-289 -- Explore spatial accessory input on visionOS*

### Supported Accessories

- **PlayStation VR2 Sense controller**: Buttons, joystick, trigger. Great for gaming. Can navigate system via standard gestures.
- **Logitech Muse**: Force sensors with variable input on tip and side button. Haptic feedback. Precision for productivity/creativity. (WWDC25-289)

### Integration Architecture

1. **GameController framework**: Discover and connect (`GCController` / `GCStylus`).
2. **RealityKit**: Anchor virtual content to accessories. Create `AnchorEntity(.accessory(...))`.
3. **ARKit**: `AccessoryAnchor` for handedness, relative motion, tracking state.

### Key APIs

```swift
// Check spatial accessory support
controller.productCategory == GCProductCategorySpatialController
stylus.productCategory == "Spatial Stylus"

// Anchor to accessory
let source = try await AnchoringComponent.AccessoryAnchoringSource(device: device)
let entity = AnchorEntity(.accessory(from: source, location: location), trackingMode: .predicted)

// SpatialTrackingSession now supports .accessory
let config = SpatialTrackingSession.Configuration(tracking: [.accessory])
```

### Tracking Modes

- **Predicted**: Low latency, may overshoot on jerky movements. Best for rendering.
- **Continuous**: Higher accuracy, higher latency. Best for precise measurements. (WWDC25-289)

### ARKit AccessoryAnchor Properties

- `heldChirality`: Which hand holds the accessory (left/right/none).
- Relative motion and rotational movement.
- Tracking quality state.
- Get ARKit anchor from RealityKit: `entity.components[ARKitAnchorComponent.self]` then cast to `AccessoryAnchor`. (WWDC25-289)

### Design Considerations

- Support both gestures AND controllers: Use `.receivesEventsInView` modifier alongside game controller input. (WWDC25-289)
- For full space apps: Use `.persistentSystemOverlays` to hide home indicator and `.upperLimbVisibility` to hide limbs/accessories. (WWDC25-289)
- **Always offer adaptive support for hands and accessories.** (WWDC25-289)
- ARKit natively tracks hands even faster this year. (WWDC25-289)
- App Store badges: "Spatial game controller support" or "Spatial game controller required". (WWDC25-289)

---

## 8. Shared Experiences and Nearby Sharing

*Source: WWDC25-318 -- Share visionOS experiences with nearby people*

### Nearby Window Sharing

- Windows appear for everyone at the exact same location in the room with a green window bar.
- Anyone can move/resize shared windows -- changes are reflected for all.
- Digital crown recenter moves window to a good position for everyone.
- Content fades when someone points at or moves hand over shared window. (WWDC25-318)

### SharePlay Integration

- Existing SharePlay apps work with nearby sharing -- no code changes needed.
- New `ShareLink` with hidden modifier exposes GroupActivity to Share menu:
  ```swift
  ShareLink(item: BoardGameActivity(), preview: SharePreview("Play Together")).hidden()
  ```
- Calling `activate()` on an activity now auto-prompts the Share menu outside FaceTime. (WWDC25-318)

### Key New APIs

- **`isNearbyWithLocalParticipant`**: Property on ParticipantState to distinguish nearby vs. remote participants.
- **`pose` on ParticipantState**: Location of participant relative to ImmersiveSpace scene. Updates after key events (sharing start, recenter). NOT real-time tracking.
- **`.groupActivityAssociation(.primary("id"))`**: View modifier to designate which WindowGroup is the shared window when multiple are open.

### Shared World Anchors (ARKit)

```swift
let anchor = WorldAnchor(originFromAnchorTransform: transform, sharedWithNearbyParticipants: true)
try await provider.addAnchor(anchor)
```
- Only available during active SharePlay session.
- Only shared with nearby participants.
- Do NOT persist after sharing ends (unlike regular world anchors).
- Check availability via `provider.worldAnchorSharingAvailability`. (WWDC25-318)

### Design Best Practices

- Offer a non-immersive mode for sharing from the Share menu, then transition to immersive after everyone joins. (WWDC25-318)
- Use participant poses (not seat poses) for placing content where people already are. (WWDC25-318)
- Use `AVPlaybackCoordinator` for precisely synchronized media playback with no echo or delay. (WWDC25-318)
- Spatial Personas are now out of beta with expanded customization. (WWDC25-317)

---

## 9. Environment Optimization

*Source: WWDC25-305 -- Optimize your custom environments for visionOS*

### Optimization Pipeline (Houdini-based)

Apple provides a downloadable Houdini toolkit with custom HDAs (Houdini Digital Assets):

1. **Boundary Camera HDA**: Visualize content from actual viewer perspectives within the Immersive Boundary.
2. **Boundary Samples HDA**: Generate sample points inside the Immersive Boundary for multi-viewpoint analysis.
3. **Adaptive Reduce HDA**: Distance-weighted polygon reduction preserving silhouettes. Uses sample points to evaluate geometry from all viewing angles.
4. **Vista Billboard HDA**: Convert distant geometry (>1km) to flat panoramic strips -- millions of polygons to thousands.
5. **Remove Backfaces HDA**: Dot-product culling of always-away-facing polygons.
6. **Occlusion Culling HDA**: Ray-cast visibility testing from sample positions.
7. **Mesh Partition HDA**: Split mesh into minimal UV islands for multi-angle projection.
8. **Multi-Projection HDA**: Project UVs from optimal viewpoint per partition.

### Performance Targets

From the Moon environment case study:
- Source: 100 million polygons, dozens of GB of textures
- Optimized: **180,000 triangles**, <200 MB textures
- Entity count: under 200 assets
- Draw calls per frame: typically fewer than 100 (WWDC25-305)

### Key Optimization Techniques

- **Adaptive mesh reduction**: Preserve density near viewer, reduce organically with distance. Use silhouette parameter to control triangle spend on edge features. (WWDC25-305)
- **Geometry billboards**: Replace distant 3D geometry with flat projected strips. (WWDC25-305)
- **Occlusion + backface culling combined**: ~50% triangle reduction on already-optimized geometry. (WWDC25-305)
- **Screen-space UV mapping**: For content outside the Immersive Boundary, use spherical projection UVs instead of surface-area UVs. Texel density scales with viewer perception, not physical surface area.
- **Two-texture approach**: One texture for inside boundary (area-based UVs), one for everything beyond (screen-space UVs). Same texture size despite vastly different physical coverage. (WWDC25-305)

### USD Setup for Runtime

- Structure USD to enable **frustum culling**: System automatically unloads entities outside view. Proper entity granularity is critical. (WWDC25-305)
- Merge and bake assets into consistent mesh partitions regardless of original object count. (WWDC25-305)

### Hidden Gems

- Texel density only matters from the Immersive Boundary -- don't waste resolution on surfaces the viewer cannot approach. (WWDC25-305)
- For portal experiences: Modify occlusion culling to only preserve triangles visible through portal extents. (WWDC25-305)
- Multiple Immersive Boundaries can share optimizations using multiple sets of sample points. (WWDC25-305)

---

## 10. Hover Interaction Design

*Source: WWDC25-303 -- Design hover interactions for visionOS*

### Fundamentals

- Hover effects are applied outside app process for privacy -- app never knows where user is looking.
- Views define two states (standard + hovered). System animates between them.
- Custom effects cannot trigger app actions -- only drive animations. (WWDC25-303)

### Animation Types

1. **Instant**: Start immediately on look (e.g., showing an arrow icon). Best for small, contextual info.
2. **Delayed**: Show content after a short delay (e.g., tooltips). Allows quick taps without triggering the effect.
3. **Ramp**: Slow ease-in then spring pop. Best for content expansion (e.g., environment icons in Home View). Provides hint of upcoming action without being distracting. (WWDC25-303)

**Recommended ramp curve**: "Slow ease-in, then pops to completion with a quick spring." (WWDC25-303)

### Design Guidelines

- **Provide anchoring elements**: Keep part of the view static during hover (especially text). Prevents reading disruption.
- **Start from visible elements**: Never reveal content from invisible triggers. Show controls when looking at something visible nearby.
- **Apply effects carefully**: Avoid effects on high-usage views (toolbar buttons, table cells) -- stick with standard highlight.
- **Keep effects small**: Avoid large-view effects that cause excessive motion.
- **For imagery**: Use highlight that fades to show true colors. Works for photos and 3D objects.
- **Avoid unexpected motion**: Example: Don't show/hide close buttons on hover -- users' eyes jump to them causing accidental closes. Instead: fade in slowly at 50% then fully on direct look. (WWDC25-303)
- **Test on device**: "It's impossible to experience them by watching a video since they react to where you look." Simulator is not a replacement. (WWDC25-303)

### Sizing for 3D

- Interactive elements: minimum **60 points** of space.
- For fixed-scale 3D objects: 60pt ~ **2.5 degrees angular size** ~ **4.4 cm at 1 meter distance**. (WWDC25-303)
- Prefer rounded shapes (circles, pills, rounded rectangles) -- easier to look at, drawing eyes to center. (WWDC25-303)

### Look to Scroll

- Not enabled by default -- opt in per scroll view.
- Best for reading/browsing content (articles, media). NOT for UI control lists (Settings-like views).
- Scroll views should ideally be full width/height of window. If inset, provide clear boundaries.
- Consider disabling for views with parallax or custom scroll animations. (WWDC25-303)

### Persistent Controls

- Auto-hiding media controls now support persistence on hover.
- Standard video player gets this for free.
- Custom video controls need explicit opt-in.
- Also works for non-video (FaceTime call controls, Mindfulness session controls). (WWDC25-303)

---

## 11. Widget Design for visionOS

*Source: WWDC25-255 -- Design widgets for visionOS*

### Core Principles

1. **Persistence**: Widgets anchor to physical locations, persist across sessions even across rooms and restarts.
2. **Fixed size**: Real-world scale. Template sizes available (including extra-large for poster-like widgets). Resizable 75%-125% via corner affordance.
3. **Customizable**: Paper vs. Glass styles, color palettes, mounting styles, frame widths.

### Styles

- **Paper**: Print-like, responds to ambient lighting. Components: frame + content + reflective coating. Best for artwork/photos that should feel like real objects.
- **Glass**: Layered depth. Foreground elements in full color (unaffected by lighting). Components: frame + background/backplate + UI duplicate layer (shadow) + UI layer (crisp text) + coating layer. Best for information-rich widgets. (WWDC25-255)

### Mounting Styles

- **Elevated** (default): On wall surface like a picture frame. Works on horizontal and vertical surfaces.
- **Recessed**: Cutout illusion in wall. Only available on vertical surfaces. Fixed frame width. Best for immersive/ambient content (weather, editorial visuals). (WWDC25-255)

### Proximity Awareness

- Two thresholds: **Default** (close-up detail) and **Simplified** (distance view).
- Like responsive design but for angular size, not screen size.
- Maintain shared elements across thresholds for continuity.
- Ensure interactive areas are targetable at all distances.
- Not every widget needs proximity awareness, but it improves clarity for information-dense widgets. (WWDC25-255)

### Design Guidelines

- Design with room context in mind -- widgets live in kitchens, offices, living rooms.
- Test across all system color palettes (7 light + 7 dark).
- Widget frame always receives tinting and cannot be excluded.
- Use high-resolution assets since widgets can be resized and viewed up close.
- Tap on non-interactive widgets launches the app nearby. (WWDC25-255)

---

## 12. Cross-Session References

### Sessions Referenced by Multiple Talks

| Session | Referenced By |
|---------|-------------|
| "Better together: SwiftUI and RealityKit" (WWDC25-274) | 287, 317 |
| "Support immersive video playback in visionOS apps" (WWDC25-296) | 287, 304, 317, 403 |
| "Explore video experiences for visionOS" (WWDC25-304) | 296, 317, 403 |
| "Learn about Apple Immersive Video technologies" (WWDC25-403) | 296, 304, 317 |
| "Learn about the Apple Projected Media Profile" (WWDC25-297) | 296, 304, 317, 403 |
| "What's new for the spatial web" (WWDC25-237) | 296, 304, 317, 403 |
| "What's new in RealityKit" (WWDC25-287) | 288, 289, 304, 317 |
| "Explore spatial accessory input on visionOS" (WWDC25-289) | 287, 294, 317 |
| "Set the scene with SwiftUI in visionOS" (WWDC25-290) | 294, 317 |
| "Meet SwiftUI spatial layout" (WWDC25-273) | 317 |
| "What's new in Metal rendering for immersive apps" (WWDC25-294) | 317 |
| "Share visionOS experiences with nearby people" (WWDC25-318) | 317 |
| "Design for spatial input" (WWDC23) | 303 |
| "Customize spatial Persona templates in SharePlay" (WWDC24-10201) | 318 |
| "Build a Spatial Drawing App with RealityKit" (WWDC24-10104) | 289 |
| "Discover Metal 4" (WWDC25-205) | 294 |

### Prerequisite Sessions (Watch First)

- Before WWDC25-296: Watch WWDC25-304 (Explore video experiences)
- Before WWDC25-403: Watch WWDC25-304 (Explore video experiences)
- Before WWDC25-294: Familiarize with Compositor Services and Metal rendering (WWDC23-10089, WWDC24-10092)
- Before WWDC25-318: Watch WWDC21-10187 (Build custom experiences with Group Activities)

### Sample Projects Worth Downloading

- **Canyon Crosser**: Volumetric hike-planning app demonstrating new SwiftUI + RealityKit APIs (WWDC25-317)
- **Petite Asteroids**: Volumetric visionOS game (WWDC25-317)
- **PyroPanda (SceneKit to RealityKit)**: Full migration sample with animations, audio, particles, post-processing (WWDC25-288)
- **Tracking accessories in volumetric windows**: ARKit accessory tracking sample (WWDC25-289)
- **Playing immersive media with AVKit**: AVExperienceController delegate methods (WWDC25-296)
- **Playing immersive media with RealityKit**: Video scaling, portal transitions (WWDC25-296)
- **Presenting images in RealityKit**: ImagePresentationComponent usage (WWDC25-287)
- **Building a guessing game for visionOS**: SharePlay nearby sharing (WWDC25-318)
- **Immersive environment optimization toolkit for Houdini**: HDAs for optimization pipeline (WWDC25-305)
- **Authoring Apple Immersive Video**: AVAssetWriter for AIVU files (WWDC25-403)
- **Destination Video**: Video docking in custom environments (WWDC25-304)
- **Construct an immersive environment for visionOS**: Environment building guide (WWDC25-305)
