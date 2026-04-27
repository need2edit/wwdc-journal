# Spatial Computing & visionOS 2 -- WWDC24 Deep Analysis

Comprehensive analysis of WWDC24 sessions covering visionOS 2's maturity wave: ARKit object/room tracking, RealityKit cross-platform expansion, mixed-immersion Metal rendering, spatial photo/video, custom hover effects, and the volume/immersive-space SwiftUI APIs.

Sessions analyzed: 10100 (ARKit enhanced), 10101 (Object tracking), 10102 (Reality Composer Pro), 10103 (RealityKit cross-platform), 10104 (Spatial drawing), 10105 (Quick Look), 10106 (USD/MaterialX), 10107 (Object Capture area mode), 10166 (Spatial photo/video), 10186 (Optimize 3D assets), 10092 (Metal passthrough), 10091 (TabletopKit), 10093 (iOS games to visionOS), 10094 (Game input), 10115 (Custom environments), 10116 (Multiview video), 10152 (Custom hover effects), 10172 (RealityKit debugger), 111801 (Spatial audio).

---

## 1. ARKit on visionOS 2 -- The Object Tracking Era (WWDC24-10100, 10101)

### 1.1 Object Tracking -- The Headline Feature

For the first time, ARKit can track **specific real-world objects** as anchors. This unlocks "instructional manual on the appliance," "interactive globe," and "collectible toy comes to life" use cases.

**Workflow:**
1. Get a USDZ 3D model of the object (use Object Capture if you don't have one)
2. Train a `ReferenceObject` with the new Create ML **Spatial > Object Tracking** template
3. Use the `.referenceObject` anchor type at runtime

```swift
let referenceObject = try await ReferenceObject(from: url)
let provider = ObjectTrackingProvider(referenceObjects: [referenceObject])
try await session.run([provider])
for await anchor in provider.anchorUpdates {
    // anchor.boundingBox, anchor.referenceObject
}
```

### 1.2 Object Tracking Quality Constraints (WWDC24-10101)

> "It works best for objects that are mostly stationary in the surrounding. Also, aim for objects that have a rigid appearance in both shape and texture. Lastly, your objects should be non-symmetrical."

**Best practices:**
- Photorealistic 3D model required -- use Object Capture
- Multi-material USDZ for glossy/transparent parts
- Choose viewing angle hint: `.allAngles`, `.upright`, `.front` -- this dramatically affects training quality
- Training takes hours and is **only supported on Apple Silicon Macs**

### 1.3 Coaching UI Pattern (WWDC24-10101)

When the object isn't yet tracked, display a 50%-opacity preview of the target. When tracking begins, animate the preview toward the actual object position. This is the *recommended UX pattern* for object-tracking apps.

```swift
// Get the 3D model from the ReferenceObject:
let url = referenceObject.usdzPath
let preview = try await Entity(contentsOf: url)
preview.components.set(OpacityComponent(opacity: 0.5))
```

### 1.4 Room Tracking (WWDC24-10100)

ARKit can now identify **room boundaries** and detect transitions between rooms. Use cases:
- "Virtual pet greets me when I enter the bedroom"
- Per-room virtual content
- Wall-aligned virtual portals

```swift
let provider = RoomTrackingProvider()
for await update in provider.anchorUpdates {
    if update.anchor.isCurrentRoom {
        // The room you're standing in
        let geometry = update.anchor.geometry
        // also: walls/floor as disjoint geometries, plane/mesh anchor IDs
    }
}
```

**Hidden gem:** RoomAnchor exposes the room's associated plane/mesh anchor IDs. **Use these to skip expensive operations on planes outside the current room.**

### 1.5 Slanted Plane Detection

A new `.slanted` alignment value joins `.horizontal` and `.vertical`. Slanted surfaces (ramps, sloped walls) are now detectable -- one-line opt-in.

### 1.6 World Tracking Limited Mode (WWDC24-10100)

When lighting is bad, ARKit now **falls back to orientation-only tracking** rather than losing tracking entirely. Apps detect this via:

```swift
@Environment(\.worldTrackingLimitations) var limitations
// SwiftUI environment value, or:
deviceAnchor.trackingState  // .normal vs .limited
```

When tracking is limited, persisted `WorldAnchor` objects are marked "not tracked" -- gracefully rearrange your content.

### 1.7 Hand Tracking Improvements (WWDC24-10100)

Two new modes:
- **Display rate updates** -- HandAnchor stream now matches display refresh (smoother)
- **Future predictions** -- `provider.predictedHandAnchor(at: time)` predicts where the hand will be at a target timestamp

For RealityKit AnchorEntities you can choose `.continuous` or `.predicted`. **Trade-off:** predicted is lower latency but slightly less accurate. Use predicted for "object stuck to hand" experiences; use continuous for drawing/gesture detection.

---

## 2. RealityKit -- The Cross-Platform Expansion (WWDC24-10103)

The single biggest message of WWDC 2024 RealityKit: **most visionOS RealityKit features now work on iOS, iPadOS, and macOS too.**

### 2.1 What's Cross-Platform

- RealityView with new camera mode controls (e.g., `.cameraMode(.worldTracking)` for AR)
- ShaderGraph materials
- Particle emitters
- Portals
- Hover effects (custom)
- Text entities
- Force effects, joints, dynamic lights, shadows
- Spatial Tracking Session (with platform-appropriate authorizations)

### 2.2 The Three Hover Effect Styles (WWDC24-10103)

```swift
HoverEffectComponent(.spotlight)     // default visionOS
HoverEffectComponent(.highlight(...))  // uniform tint
HoverEffectComponent(.shader)        // shader graph driven
```

The shader style integrates with a `HoverState` node in Reality Composer Pro -- intensity animates 0→1 when looked at. Use it for "lights up the spaceship window when you look at it" effects.

### 2.3 Force Effects and Physics Joints (WWDC24-10103)

Four built-in force effect types:
- **`ConstantRadialForceEffect`** -- pulls toward a center
- **`VortexForceEffect`** -- circulates around an axis
- **`DragForceEffect`** -- proportional to velocity
- **`TurbulenceForceEffect`** -- random perturbations

For custom physics (e.g., 1/r² gravity), conform to `ForceEffectProtocol` with `parameterTypes`, `forceMode`, and an `update(parameters:)` function. **Hidden gem:** Use `spatialFalloff` and `mask` to scope which physics bodies are affected.

Five built-in joint types: fixed, spherical, revolute (1-axis rotation), prismatic (1-axis slide), distance. Use `CustomJoint` to constrain angular motion per-axis (e.g., trailer that wobbles slightly).

### 2.4 Dynamic Lights & Shadows (NEW on visionOS 2)

```swift
SpotLightComponent(color: .yellow, intensity: 10000, attenuationRadius: 6)
DirectionalLightComponent(...)
PointLightComponent(...)
```

Only spotlights and directional lights cast shadows. **Performance warning:** Dynamic lights and shadows can be expensive -- profile with RealityKit Trace. Disable shadows on individual entities with `DynamicLightShadowComponent(castsShadow: false)`.

### 2.5 Portal Crossing -- The Coolest New Feature (WWDC24-10103)

In visionOS 1, an entity was either fully inside or fully outside a portal. In visionOS 2, entities can **smoothly cross the portal surface**:

```swift
portalComponent.crossingMode = .plane(.positiveZ)
portalComponent.clippingPlane = .positiveZ

shipEntity.components.set(PortalCrossingComponent())
```

**Lighting trick:** Use `EnvironmentLightingConfigurationComponent` with a weight 0...1 to smoothly transition the entity's lighting from outside-portal IBL to inside-portal IBL as it approaches the surface. Avoids the harsh light cutoff at the portal plane.

### 2.6 New RealityView Camera Modes for iOS/macOS

```swift
RealityView(...) { ... }
    .realityViewCameraControls(.world)       // AR
    .realityViewCameraControls(.orbit)        // 3D viewer
```

### 2.7 Other RealityKit Goodies

- **`LowLevelMesh` and `LowLevelTexture`** -- direct, low-level construction of resources
- **Animation timelines** authored in Reality Composer Pro
- **`BillboardComponent`** -- privacy-preserving "always face the user"
- **PixelCast** -- pixel-perfect entity hit testing via rendering
- **Subdivision surfaces** -- smooth surfaces without dense meshes

---

## 3. Spatial Audio in RealityKit (WWDC24-111801)

Spatial audio is now a first-class RealityKit feature with reverb, occlusion, and directionality. **Best practices:**
- Use `SpatialAudioComponent` for sound that should appear to come from an entity's location
- Use `AmbientAudioComponent` for general scene atmosphere
- Reverb tied to room geometry from RoomTrackingProvider

---

## 4. Mixed Immersion with Metal (WWDC24-10092)

This is a major new capability for custom rendering engines (Unity, custom Metal-based). Previously Metal was full-immersion only.

### 4.1 The Five Critical Steps

1. **Set the immersion style:** `.mixed`. Add `UIImmersionStyleMixed` to scene manifest if launching mixed.
2. **Clear color texture to all zeros** (NOT (0,0,0,1) like in full immersion)
3. **Use pre-multiplied alpha + P3 color space**
4. **Use ARKit scene understanding** to anchor and occlude content
5. **Choose upper-limb visibility:** `.visible`, `.hidden`, or `.automatic` (recommended -- depth-aware)

### 4.2 The Scene-Aware Projection Matrix (REQUIRED for Mixed)

> "If an application requests mixed immersion style through Compositor Services, it must use this new API." (WWDC24-10092)

The new `cp_view_compute_projection` API combines camera intrinsics + per-frame scene understanding for accurate placement against real-world objects.

### 4.3 The Trackable Anchor Time vs. Presentation Time Distinction

> "For trackable anchor prediction, use the trackable anchor time. For device anchor prediction, use the presentation time." (WWDC24-10092)

The frame timeline exposes **four** timings:
1. Optimal Input Time -- finish non-critical work
2. Rendering Deadline -- CPU + GPU done
3. **Trackable Anchor Time** -- when the cameras actually saw the surroundings (use for hand prediction)
4. **Presentation Time** -- when the frame displays (use for device pose prediction)

**Hidden gem:** Acquire pose data TWICE per frame -- first for non-critical simulation, then again right before render submission. Prediction accuracy improves the closer the query time is to the presentation time.

### 4.4 Reverse-Z Depth Convention

Compositor Services expects depth in **reverse-Z** convention. Pixels with alpha=0 should also have depth=0 -- this avoids parallax artifacts and improves system performance.

---

## 5. SwiftUI for Volumes & Immersive Spaces (WWDC24-10153)

(Detailed in the SwiftUI cluster analysis -- see `swiftui-ui-frameworks.md` Section 8.)

Key takeaways:
- Volumes have baseplate by default in visionOS 2 -- disable for content that fills bounds
- Volumes inherit min/max size from content frames -- use `.frame(minWidth:...)` to enable resize
- Toolbars and ornaments **automatically follow the side** the user stands on
- `onVolumeViewpointChange` + `supportedVolumeViewpoints` -- react to and constrain user position
- Custom immersion levels with progressive style: `.progressive(0.20...1.0, initialAmount: 0.8)`
- `preferredSurroundingsEffect(.colorMultiply(.purple))` -- tint passthrough for mood

---

## 6. Spatial Media -- Photo, Video & Apple Immersive (WWDC24-10166)

### 6.1 The Three Stereoscopic Tiers

| Format | Capture | Best For |
|---|---|---|
| 3D video | n/a (curated) | Movies docked into environments |
| Spatial video | iPhone 15 Pro, Vision Pro | Personal moments, point-and-shoot |
| Apple Immersive Video | Pro production | 180° 8K cinematic, fully immersive |

### 6.2 Recording Spatial Video on iPhone 15 Pro (NEW)

Three lines of code change a normal AVFoundation capture into spatial:
1. Set device to `.builtInDualWideCamera`
2. Pick a format with `isSpatialVideoCaptureSupported`
3. Set `output.isSpatialVideoCaptureEnabled = true`

### 6.3 Discomfort Detection API (WWDC24-10166)

```swift
captureDevice.publisher(for: \.spatialCaptureDiscomfortReasons)
    .sink { reasons in
        // .subjectTooClose or .notEnoughLight
    }
```

The two cameras have different minimum focus distances and light gathering. The Camera app surfaces these warnings -- you should too. **The iPhone preview is monocular, so users can't see the issue until it's too late.**

### 6.4 Recommended Stabilization Mode

> "To get the best quality stabilization, set the preferredVideoStabilizationMode to cinematicExtendedEnhanced." (WWDC24-10166)

Especially important on visionOS where screen sizes can be enormous.

### 6.5 Detection + Loading

- `PhotosPicker` matching: `.spatialMedia`
- PhotoKit predicate: `PHAssetMediaSubtype.spatialMedia`
- `AVAssetPlaybackAssistant.playbackConfigurationOptions` -- works for assets outside the Photo Library

### 6.6 Presentation Choices

| API | Spatial Mode? | Use case |
|---|---|---|
| `PreviewApplication` (QuickLook) | YES, full spatial | Best for spatial photos + videos |
| Element Fullscreen API (JS) | YES | Web-loaded spatial photos |
| `AVPlayerViewController` | NO -- displays as 3D video | Mixed 2D/3D content with consistent UI |

**Critical:** `AVPlayerViewController` plays spatial videos as **3D videos**, not in the full spatial portal presentation. Use `PreviewApplication` if you want the spatial portal experience.

### 6.7 Spatial Metadata Deep Dive

Spatial photos = stereo HEIC + metadata. Spatial videos = MV-HEVC + metadata.

Required metadata:
- **Projection** -- always rectilinear
- **Baseline** (~64mm = human-eye-distance is the default; smaller for close-up; larger gives miniaturization)
- **Field of view** (≤90° recommended)
- **Disparity adjustment** -- horizontal offset as % of image width; controls the 3D depth in windowed presentation

Required image characteristics (NOT enforced but critical):
- Stereo rectified (parallel optical axes)
- Optical axis alignment (don't crop or shift!)
- No vertical disparity (feature points must lie on horizontal lines between left/right)

> "A shift of even a couple percentage points is enough to dramatically alter the perception of the image, so make sure to test in Vision Pro, when picking a value for the disparity adjustment."

---

## 7. 3D Asset Optimization (WWDC24-10186)

### 7.1 Polygon Budget

> "We recommend no more than 500 thousand triangles for an immersive scene, with 250 thousand for applications in the shared space."

Visible triangles at any moment: aim for ~100K. **Split large objects (terrain) into chunks** so off-camera pieces can be culled.

### 7.2 The "Texture Packing" Technique

Single-channel grayscale textures (roughness, metallic, AO) **don't get compressed**. Combine them into a single RGB texture to enable compression:
- R = roughness, G = metallic, B = AO

Up to **40% asset size reduction** for PBR materials.

### 7.3 Color Space Pitfalls

Reality Composer Pro shows color spaces as `Transfer Function - Gamut`:
- Perceptual textures (base color): **sRGB - Display P3**
- Data textures (normal, packed RGB): use `vector3` type, no transformation
- HDR images (IBL): **Linear**

### 7.4 Normal Map Gotchas

- RealityKit expects **OpenGL** format. DirectX format has the green channel inverted.
- Range must be -1...1, not 0...1. Use the **`NormalMapDecode`** node (NOT `NormalMap`, which doesn't transform range).

### 7.5 Material Instances

Promote textures to inputs, then `Create Instance` for variants. Saves shader compilation cost AND your authoring time.

### 7.6 Skybox vs. IBL

| | Skybox | IBL |
|---|---|---|
| Resolution | 8K+ | 512px is often enough |
| Format | LDR | **HDR** |
| Material | Unlit | Image-Based Light + Receiver components |

### 7.7 The EnvironmentRadiance Node

When you want some specular reflection without the cost of a full PBR shader, use `EnvironmentRadiance` in an unlit graph. Cheaper than PBR but more expressive than pure unlit.

### 7.8 Avoid Transparency Overdraw

Transparent pixels are computed once per layer. **Trade more triangles for fewer transparent pixels** (e.g., grass blades as geometry vs. alpha-cut planes).

---

## 8. Game Input on visionOS (WWDC24-10094)

### 8.1 Decision Tree

| Need | Use |
|---|---|
| Standard interaction | System gestures (`SpatialTapGesture`, `SpatialEventGesture`, `RotateGesture3D`) |
| Multi-action simultaneously | `SimultaneousGesture` combinations |
| Anything else | Custom hand tracking via ARKit (Full Space only) |

**Critical constraint:** Custom gestures via ARKit hand tracking **only work in Full Spaces** -- shared/volume scenes don't get hand tracking access.

### 8.2 Direct vs. Indirect Input

- **Direct** = reach out and touch. High-energy, satisfying. Add visual + audio feedback heavily.
- **Indirect** = look + pinch-and-drag. Comfortable for long sessions. Players can sit back.

> "Indirect input lets players make small hand movements that are amplified into big actions."

### 8.3 Game Controller + Trackpad Support

Same `GameController` framework as iOS/macOS. **New in visionOS 2:** Add the `gameControllerInteraction()` modifier to your RealityView so input is routed to your game.

### 8.4 The "Always Have a Fallback" Rule

> "It's really important to think about these types of accessibility use cases and build in some input fallbacks for your players."

Synth Riders' one-handed mode is the example. If your game requires both hands, give an option for one. Use the native Accessibility frameworks via RealityKit.

---

## 9. RealityKit Debugger (WWDC24-10172)

A new debugger in Xcode 16. Capture a snapshot of your running app's entity hierarchy with one click. Browse entities and their components in 3D, including custom components. Far more productive than `print(entity.components)` debugging.

Companion: **RealityKit Trace** for profiling rendering performance.

---

## 10. TabletopKit (WWDC24-10091)

A new high-level framework specifically for **tabletop board game** experiences on visionOS. Handles common patterns:
- Card decks, dice, pawns, hands
- Multiplayer turn order
- Drag-to-place + snap-to-grid
- Player vs. shared visibility

If you're building a tabletop game, you almost certainly want TabletopKit instead of building scene management from scratch on RealityKit.

---

## 11. Bringing iOS Games to visionOS (WWDC24-10093)

### 11.1 The Three-Tier Adaptation Path

1. **Compatible** -- your iPad app runs as-is in a window
2. **Enhanced** -- adopt visionOS APIs for hover, pinch-tap on UI, lighting
3. **Native** -- volumetric or fully immersive experience

### 11.2 Quick Wins for Existing Games

- Add hover effects to interactive UI elements
- Enable `gameControllerInteraction()` on your RealityView
- Use spatial audio for in-world sounds
- Adapt UI density (visionOS targets are larger)

---

## 12. Quick Look for visionOS (WWDC24-10105)

`PreviewApplication` API spawns a new QuickLook scene from your app -- supporting USDZ, spatial photos, spatial videos. Full spatial presentation with automatic immersive view button.

This is the **simplest** way to add a "view spatial content" feature without building your own scene.

---

## 13. Custom Environments (WWDC24-10115, 10087)

Custom immersive environments can now be authored in Reality Composer Pro AND optimized to support media playback. Use cases: a virtual movie theater for your video player; a serene environment for meditation app.

---

## 14. Cross-References & Watch Order

For visionOS app developers:
1. **WWDC24-10153** (Volumes + Immersive Spaces) -- foundational
2. **WWDC24-10103** (RealityKit cross-platform) -- everything new in RealityKit
3. **WWDC24-10101** (Object tracking) + **10100** (ARKit) -- if you want anchored experiences
4. **WWDC24-10186** (3D asset optimization) -- if you have models

For Metal-based engines:
1. **WWDC24-10092** (Metal passthrough)
2. **WWDC24-10100** (ARKit) for anchors and hand tracking

For media apps:
1. **WWDC24-10166** (Spatial photo/video)
2. **WWDC24-10115** (Custom environments for video)

For game developers:
1. **WWDC24-10094** (Game input)
2. **WWDC24-10093** (Bring iOS games)
3. **WWDC24-10091** (TabletopKit if applicable)
