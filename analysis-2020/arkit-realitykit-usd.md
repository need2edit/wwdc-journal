# WWDC 2020 — ARKit 4, RealityKit, USD

WWDC 2020's AR story is anchored by **the LiDAR scanner** (introduced on iPad Pro that spring) and **location anchors** (place AR content at GPS coordinates with map-data-derived precision). RealityKit got video materials, scene understanding, and improved debugging.

## Sessions Analyzed
- 10611 — Explore ARKit 4 (gateway)
- 10612 — What's new in RealityKit
- 10613 — What's new in USD
- 10601 — The artist's AR toolkit
- 10604 — Shop online with AR Quick Look

## ARKit 4: Three Major Additions

### Location Anchors

Place AR content at **real-world GPS coordinates** — and have it appear precisely positioned for everyone using the app at that location. This is "global-scale AR." API:

```swift
let config = ARGeoTrackingConfiguration()
ARGeoTrackingConfiguration.isSupported  // device check (A12+, GPS)
ARGeoTrackingConfiguration.checkAvailability(at:completionHandler:)  // location data check
arView.session.run(config)

let anchor = ARGeoAnchor(coordinate: CLLocationCoordinate2D(latitude: ..., longitude: ...))
arView.session.add(anchor: anchor)
```

How it works under the hood: ARKit downloads **localization map** data from Apple Maps for your area — feature points of buildings visible from the street. Combined with your camera images, machine learning runs on-device to determine your precise device pose. **No data leaves the device.**

Coverage at launch: SF Bay Area, NYC, LA, Chicago, Miami, with more cities through summer.

#### Geo Anchor Coordinate System
- X axis: always east
- Z axis: always south
- Y axis: up (positive)

Geo anchors are **immutable** — to position content above the ground or rotated, transform from the geo anchor entity in your render code.

#### Key Tracking States
ARGeoTrackingState transitions: `Initializing` → `Localizing` → `Localized` (or → `NotAvailable` if location isn't supported). Always monitor `ARGeoTrackingStatus`:
- Display Localizing UI hints to the user — "raise the device", "point at buildings", "geoDataNotLoaded — check your network"
- Only place content after the state is `Localized` and `accuracy` is acceptable
- States can regress; always handle going back to Localizing

### Scene Geometry / Depth API

The LiDAR scanner gives ARKit a **dense 3D depth map** at 60Hz. New `ARFrame.sceneDepth` property delivers `ARDepthData` containing:
- A depth map (`CVPixelBuffer`, smaller than the captured image but same aspect ratio, depth in meters)
- A confidence map (low/medium/high) — filter based on your app's tolerance for inaccuracy

```swift
let config = ARWorldTrackingConfiguration()
config.frameSemantics = [.sceneDepth]
arView.session.run(config)

// In didUpdateFrame
let depthMap = frame.sceneDepth?.depthMap
let confidenceMap = frame.sceneDepth?.confidenceMap
```

Apps using **People Occlusion** (`personSegmentationWithDepth`) automatically get scene depth on supported devices with no extra power cost.

### Improved Object Placement

`ARRaycastQuery` is now strongly recommended over `hitTest` (which is deprecated for object placement). On LiDAR devices, raycasting:
- Is more precise and faster
- Works on **featureless surfaces like white walls** thanks to scene depth
- Returns multiple types of intersection (existingPlanes, infinitePlanes, estimatedPlanes)

```swift
let query = arView.makeRaycastQuery(from: screenPoint, allowing: .estimatedPlane, alignment: .any)
let results = arView.session.raycast(query)
```

Two raycast types: single-shot and tracked (continuous updates as ARKit's scene understanding improves).

### Face Tracking on More Devices

Face tracking is now supported on devices with **A12 or later, even without TrueDepth camera** (iPhone SE 2020). Face anchors, geometry, and blend shapes work everywhere. Captured depth is still TrueDepth-only.

## RealityKit Additions

### Video Materials

Use a video as a texture (with looping, sequencing, HLS streaming) AND as a spatialized audio source, all from a single material:

```swift
let player = AVPlayer(url: videoURL)
let material = VideoMaterial(avPlayer: player)
bugEntity.model?.materials = [material]
player.play()
```

Built on AVPlayer — leverage AVQueuePlayer for sequencing, AVPlayerLooper for loops, even HLS streaming. The entity becomes a spatialized audio source (audio appears to come from the entity's position).

### Scene Understanding (LiDAR)

The new `arView.environment.sceneUnderstanding.options` set unlocks four interactions between virtual and real-world content:

- **`.occlusion`** — virtual objects are occluded by real-world geometry (the bug hides behind the tree).
- **`.receivesLighting`** — virtual objects cast shadows on real surfaces (auto-enables `.occlusion`).
- **`.physics`** — virtual objects physically interact with real surfaces (auto-enables `.collision`).
- **`.collision`** — collision events fire when virtual objects hit real-world entities; raycast against the real world works.

Important caveats:
- Real-world objects are **static, infinite mass** (you can't push them).
- Meshes are constantly updating; objects on non-planar surfaces may shift slightly.
- Mesh is limited to scanned regions — design your experience to encourage scanning before action.
- Mesh is an approximation; edges of stairs/etc. won't be crisp.
- **Physics is incompatible with collaborative sessions** (other scene understanding options work fine in collaborative mode).

#### Scene Understanding Entities

Real-world objects in your scene get represented as **scene understanding entities** with `SceneUnderstandingComponent`. Identify them with the `HasSceneUnderstanding` trait:

```swift
arView.scene.raycast(...).filter { $0.entity is HasSceneUnderstanding }
```

These entities are read-only — RealityKit creates and manages them. Don't modify their components.

#### Filtering Out Real-World Collisions

Use the new `CollisionGroup.sceneUnderstanding` to include or exclude real-world objects from collision filters.

#### Debug Visualization

`arView.debugOptions.insert(.showSceneUnderstanding)` shows the raw mesh, color-coded by distance (gradient from camera → 5m+ all white).

### Improved Rendering Debugging

The new `DebugModelComponent` lets you visualize 16 properties per entity: vertex attributes (normals, texture coords), material parameters (base color, roughness), PBR-related outputs (diffuse lighting received, specular lighting received). Excellent for diagnosing whether a downloaded model loaded correctly or whether your material parameters are doing what you think.

```swift
entity.components[DebugModelComponent.self] = DebugModelComponent(shaderDebugMode: .baseColor)
```

Apply per-entity (children don't inherit). For USDZ files with hierarchies, attach to each entity you want to inspect.

### Location Anchor Integration

Just create an `AnchorEntity` from an `ARGeoAnchor`:

```swift
let anchor = AnchorEntity(anchor: arGeoAnchor)
```

Note: location anchors require an `ARGeoTrackingConfiguration`, not `ARWorldTrackingConfiguration`, so scene understanding (which requires world tracking) is unavailable when using geo tracking.

## What's New in USD (10613)

USD is Pixar's universal 3D scene format, increasingly the standard for AR Quick Look and RealityKit content. 2020 additions:
- Better Reality Composer support for USDZ import/export.
- Material editing improvements for PBR workflows.
- Animation/rigging refinements.

## AR Quick Look — Shop Online with AR (10604)

Web pages can present AR Quick Look experiences for products. New in 2020: built-in support for in-app purchases via Apple Pay during AR Quick Look — users can preview a product in their space and buy it without leaving the AR view.

## The Artist's AR Toolkit (10601)

Reality Composer (Apple's no-code AR authoring app) gained physics simulation improvements, reactive triggers, and better behavior chaining. Useful for designers prototyping AR without writing code.

## Cross-References
- [ml-vision-coreml.md](ml-vision-coreml.md) — Vision body/hand pose pairs naturally with AR content placement.
- [metal-graphics-pro.md](metal-graphics-pro.md) — RealityKit and ARKit performance improvements lean on Metal.
- [apple-silicon-mac-transition.md](apple-silicon-mac-transition.md) — TBDR architecture (Apple Silicon Mac) is the same architecture that powers AR's GPU work on iOS.

## Adoption Checklist
- [ ] If your AR app has location-based experiences, audit cities supported and adopt `ARGeoAnchor`.
- [ ] Always check `ARGeoTrackingConfiguration.isSupported` AND `checkAvailability(at:)` before starting.
- [ ] Monitor `ARGeoTrackingStatus` and surface friendly UI for the localizing process.
- [ ] If you target LiDAR devices, evaluate `sceneDepth` for richer interactions.
- [ ] Migrate from `hitTest` to raycasting for object placement.
- [ ] If you support older iPhones, take advantage of face tracking on A12+ without TrueDepth.
- [ ] If using RealityKit, evaluate scene understanding options for occlusion/shadows/physics.
- [ ] Adopt video materials for animated textures and spatialized audio.
- [ ] Use `DebugModelComponent` when iterating on shading/materials.
