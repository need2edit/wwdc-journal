# RealityKit, Reality Composer & ARKit 3 — WWDC 2019 Analysis

**Sessions covered:** 603 (Introducing RealityKit and Reality Composer), 605 (Building Apps with RealityKit), 604 (Introducing ARKit 3), 607 (Bringing People into AR), 609 (Advanced Scene Understanding in AR), 610 (Building Collaborative AR Experiences), 612 (Advances in AR Quick Look), 602 (Working with USD)

## Headline

RealityKit is the brand-new AR-first Swift framework that sits **above** ARKit and SceneKit, providing physically-based rendering, ECS-based content modeling, networked sync, spatial audio, and a high-level scene system. Reality Composer ships as both a Mac app and an iOS app for creating AR content visually. ARKit 3 brings people occlusion and motion capture.

## RealityKit Design Pillars (603)

- **AR-first**: built from scratch for AR rendering. PBR shading with realistic lighting, shadows, motion blur, depth of field, and camera grain — all matched to the live camera feed automatically.
- **Swift-only public API**: no Objective-C bridge layer like SceneKit had. Generic, type-safe, value-oriented.
- **ECS architecture (Entity Component System)**: composition over inheritance. An `Entity` is just an ID; you attach `Component`s (`ModelComponent`, `Transform`, `CollisionComponent`, `PhysicsBodyComponent`, `AnchoringComponent`) to give it behavior. **HIDDEN GEM**: even custom components automatically network-sync across devices via multipeer.
- **Built on Metal**: multi-threaded rendering, takes advantage of every GPU feature on Apple Silicon.

## Six Core Subsystems (603)

1. **Rendering** — physically-based shading, motion blur, depth of field, grain to match camera.
2. **Animation** — skeletal + transform, imported from USDZ. Procedural animation via ARKit motion capture.
3. **Physics** — rigid body dynamics, collisions (box/sphere/compound), mass, friction, restitution.
4. **Networking** — built on MultipeerConnectivity. Entire scene state syncs to all peers, including custom components.
5. **Audio** — 3D-positional spatial audio attached to entities. Distance attenuation automatic.
6. **ARView** — the entry-point view with full gesture support, all camera effects, and a built-in coaching overlay.

## Camera Effects in ARView (603)

ARView gives you the SAME quality as AR Quick Look out of the box:

- **Grounding shadows** (drop or HBAO/contact-area). Without shadows, virtual content "floats." Two performance tiers.
- **Motion blur** matched to the camera's exposure time (read from ARKit).
- **Depth of field** matching the camera's current focus distance.
- **Camera grain** — virtual content gets the same noise as the camera image, especially in low light. **HIDDEN GEM**: this is what sells the illusion.

## The Reality File Format (603)

- New `.reality` file: pre-optimized scene container with meshes, materials, physics, audio, and animations.
- **PERFORMANCE**: Reality files load dramatically faster than USDZ at runtime.
- Export from Reality Composer.
- ARView still loads USDZ directly for AR Quick Look style use cases.

## Anchor System (603)

- Anchors are first-class. Entire entity hierarchies are children of an `AnchorEntity`.
- Hierarchies are **inactive** until ARKit detects a matching anchor in the world. So content doesn't "float" — it appears only when an actual surface/face/image is found.
- Anchor types: horizontal/vertical plane, image, face, body, camera, world (specific transform).

## ARKit 3 Highlights (604)

- **People occlusion**: ARKit produces a per-frame depth segmentation matte for humans. Virtual objects can correctly pass behind real people. Requires A12 Bionic+. **HIDDEN GEM**: works without lidar (lidar arrived in 2020 iPad Pro).
- **Motion capture**: real-time skeleton tracking from a single back camera. Drive an animated character with a real person's motion. `ARBodyTrackingConfiguration`.
- **Simultaneous front+back camera**: face tracking with the front camera while world tracking with the back. Power-hungry; A12+.
- **Multiple face tracking**: up to 3 faces simultaneously (also A12+).
- **Collaborative sessions**: `ARWorldTrackingConfiguration.isCollaborationEnabled = true` shares world maps continuously between peers (not the one-shot `ARWorldMap` flow from 2018).
- **Coaching overlay** — system-provided UI that guides the user to find a surface (`ARCoachingOverlayView`).
- **HIDDEN GEM**: `ARView` automatically integrates the coaching overlay; UIKit/SceneKit hosts must add it manually.

## RealityKit Networking (610)

- One line: `arView.scene.synchronizationService = try MultipeerConnectivityService(session:)`.
- Every entity in the scene syncs to all peers automatically. Each peer "owns" certain entities and broadcasts changes.
- `entity.synchronization.ownership = .clientAuthoritative` to transfer ownership.
- Custom components conform to `Codable & Component` and sync for free.

## Reality Composer (603, 605)

- Available on iPadOS, iOS, and Mac.
- Drag-and-drop scene assembly. Triggers and actions for behavior without code.
- **HIDDEN GEM**: edit your scene directly in AR — point at a surface, lay out objects in your real room.
- Exports `.reality` files that your app can load with one line: `try Entity.loadAsync(named: "myScene")`.
- Includes a library of Apple-curated assets.

## USD Workflow (602)

- USDZ is now the recommended interchange format. Apple ships `usdzconvert` (Python script) for FBX/OBJ → USDZ conversion.
- USD layered scene composition (sublayers, references, instances) is supported.
- Use `usdtree` and `usdcat` from the Pixar reference impl for inspecting files.

## Migration / Deprecation Notes

- **DEPRECATION**: SceneKit is not officially deprecated in 2019, but RealityKit is positioned as the path forward for AR. SceneKit gets minor updates this year and very few thereafter. By 2025 it's effectively deprecated.
- **DEPRECATION**: OpenGL ES is deprecated as of iOS 12 / macOS Catalina (see 611 Bringing OpenGL Apps to Metal).

## Cross-references

- Bringing People into AR (607) — people occlusion deep dive.
- Advanced Scene Understanding (609) — plane classification, mesh reconstruction.
- AR Quick Look (612) — preview USDZ in Safari, Mail, Messages with no app needed.
- Working with USD (602) — file format internals.
