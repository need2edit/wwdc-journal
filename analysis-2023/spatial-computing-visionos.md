# WWDC 2023 — Spatial Computing & visionOS

WWDC 2023 introduced visionOS, Apple's first new platform in nearly a decade. This analysis covers the foundational sessions for building spatial apps.

## Sessions Analyzed
- 10260 — Get started with building apps for spatial computing (gateway)
- 10203 — Develop your first immersive app
- 10082 — Meet ARKit for spatial computing
- 10080 — Build spatial experiences with RealityKit
- 10081 — Enhance your spatial computing app with RealityKit
- 10091 — Evolve your ARKit app for spatial experiences
- 10083 — Meet Reality Composer Pro
- 10202 — Explore materials in Reality Composer Pro
- 10273 — Work with Reality Composer Pro content in Xcode
- 10191 — Meet Object Capture for iOS
- 10192 — Explore enhancements to RoomPlan
- 10087 — Build spatial SharePlay experiences
- 10095 — Explore rendering for spatial computing
- 10085 — Discover Quick Look for spatial computing
- 10274 — Create 3D models for Quick Look spatial experiences
- 10094 — Enhance your iPad and iPhone apps for the Shared Space
- 10090 — Run your iPad and iPhone apps in the Shared Space
- 10109 — Meet SwiftUI for spatial computing
- 111215 — Meet UIKit for spatial computing
- 10110 — Elevate your windowed app for spatial computing
- 10111 — Go beyond the window with SwiftUI
- 10113 — Take SwiftUI to the next dimension
- 10146 — Meet Core Location for spatial computing
- 10100 — Optimize app power and performance for spatial computing
- 10099 — Meet RealityKit Trace
- 10089 — Discover Metal for immersive apps
- 10096 — Build great games for spatial computing
- 10088 — Create immersive Unity apps
- 10093 — Bring your Unity VR app to a fully immersive space
- 10279 — Meet Safari for spatial computing
- 10071 — Deliver video content for spatial experiences
- 10070 — Create a great spatial playback experience

## The Three Element Model

Apple defined visionOS apps via three primitives:

1. **Windows** — `WindowGroup` SwiftUI scenes, 2D-by-default with depth-aware controls. Resizable, repositionable.
2. **Volumes** — `WindowGroup` with `.windowStyle(.volumetric)`. Bounded 3D containers with `defaultSize(width:height:depth:)` (in points or meters). Designed for the Shared Space; content must remain within bounds.
3. **Spaces** — `ImmersiveSpace` scene type. App takes over the whole field of view; supports `.mixed`, `.progressive`, `.full` immersion styles. Default is `.mixed`. Progressive style lets the user dial immersion via the Digital Crown.

This is a SPECTRUM. Apps should flex between modes during a single session — start in shared, dial up to immersive when the user opts in.

## Privacy-First Sensor Architecture

The system never hands raw sensor data to your app. Instead:
- Eye position is converted to focus/hover events; you never know where someone is LOOKING.
- Hand position is converted to standard gesture events.
- Hover effects render OUT-OF-PROCESS so apps can't infer gaze.
- Skeletal hand tracking, plane data, scene understanding all require **explicit user permission**.

This is critical: many "obvious" tracking features simply aren't possible. Build for events, not raw data.

## Input Model

- Default: gaze + pinch (look at a button, tap fingers).
- Direct touch: physical reach.
- Skeletal Hand Tracking (ARKit) for custom interactions like bowling, sign language, drumming.
- Wireless keyboards/trackpads/game controllers all work natively.

To make a RealityKit entity respond to input, it MUST have BOTH:
- `InputTargetComponent`
- `CollisionComponent`

Missing either will silently disable hit testing on that entity. This is a frequent gotcha.

## RealityKit's ECS Architecture

Entity-Component-System. An entity does nothing without components. Built-in components include:
- `ModelComponent` — mesh + materials
- `TransformComponent` — position/rotation/scale (every entity has one)
- `CollisionComponent` — for hit testing & physics
- `InputTargetComponent` — to receive gestures
- `HoverEffectComponent` — visual reaction when gazed at (privacy-safe)
- `SpatialAudioComponent`, `AmbientAudioComponent`, `ChannelAudioComponent` — three audio types
- `PortalComponent` — see into another world (10081)
- `ParticleEmitterComponent` — sparks/clouds/rain

You can register **custom components** (conform to `Component` & `Codable`) and they appear in Reality Composer Pro for designer use. Custom **systems** run code on entities matching an `EntityQuery` either every frame (`.rendering`) or on a timer.

## RealityView vs Model3D

- `Model3D(named:)` — image-equivalent for static USDs. Use when displaying a single model.
- `RealityView { content in ... }` — full ECS access. Use when adding gestures, animations, physics, custom systems, or attachments.

`RealityView` provides:
- Async `make` closure for initial scene setup
- `update` closure that re-runs when @State changes
- `attachments:` ViewBuilder for embedding SwiftUI views in 3D space (tagged then placed via `RealityViewAttachments`)
- Coordinate conversion functions (RealityKit uses meters, y-up, z-toward-viewer; SwiftUI uses points)

## Coordinate Conversion Pitfall

Drag gesture values are in SwiftUI points; entity positions are in meters. ALWAYS convert via `content.convert(value.location3D, from: .local, to: .scene)` or you'll get comically wrong positions.

## Reality Composer Pro

A new dedicated app for authoring 3D scenes. Key workflows:
- Reference USD files non-destructively (asset stays unchanged; you create a layer of overrides).
- Add custom components from your Swift package by conforming to `Component & Codable`.
- Author MaterialX shader graphs via node UI — no code.
- Author particle emitters (clouds, rain, sparks).
- Preview spatial audio with scene-aware reverb.
- Send scenes directly to device for in-headset preview without rebuilding the app.

USD asset packages are SEPARATE Swift packages from your app target — this is the recommended structure.

## ARKit on visionOS

Major API rewrite vs iOS ARKit. Key data providers:
- `WorldTrackingProvider` — device pose
- `HandTrackingProvider` — full skeletal hand joints
- `SceneReconstructionProvider` — mesh of the room
- `PlaneDetectionProvider` — flat surfaces with semantic labels (floor, wall, table)
- `ImageTrackingProvider` — anchor on known images

Anchors are streamed as `AnchorUpdate` events. ARKit ONLY runs in a Full ImmersiveSpace — not in Shared Space windows or volumes (privacy).

## iPad/iPhone Apps in the Shared Space

Existing apps run "as is" with NO recompile. iPad-version is preferred over iPhone-only when both exist. They render with light styling against the dark visionOS environment, materials translate automatically. Recompiling for visionOS gives native spacing, hover effects, 3D-aware materials.

## Performance Tools

**RealityKit Trace** (Instruments 15 template) is the new performance tool. It shows:
- Frame budget breakdown (CPU, GPU, system reserved)
- Triangle counts, entity counts
- Render passes
- Causes of dropped frames

Frame budget on visionOS is tighter than iOS due to stereo rendering. Aim for 90fps consistently. Use `UInt32` for instance count caps where possible.

## Spatial Audio is Default

In RealityKit, ALL audio is spatial unless you opt out. Use `SpatialAudioComponent.directivity` (0.0 = omnidirectional, 1.0 = laser-focused beam) to shape the sound cone. `AmbientAudioComponent` is for multichannel ambient beds (fixed-direction channels). `ChannelAudioComponent` skips spatialization entirely (background music).

## Cross-References / Pathways

- **First-time path**: 10260 → 10203 → 10080 → 10082 → 10083
- **Reality Composer Pro deep dive**: 10083 → 10202 → 10273
- **Existing iPad app porting**: 10090 → 10094 → 10110
- **SwiftUI-centric**: 10109 → 10113 → 10111
- **UIKit-centric**: 111215
- **Performance**: 10099 → 10100 → 10095
- **SharePlay**: 10075 (design) → 10087
- **Quick Look**: 10085 → 10274
- **Unity**: 10088 → 10093

## Hidden Gems

- Volumes are **bounded** to declared dimensions — content outside the bounds is clipped. They're meant for the Shared Space.
- `Model3D` loads asynchronously; always provide a `placeholder:` ProgressView.
- `HoverEffectComponent` runs in a separate process and never tells the app where the user is looking. Never try to infer gaze.
- The simulator includes three scenes (kitchen, museum, garden) with day/night lighting variants.
- ARKit data providers must be added to an `ARKitSession` and then `run()` — they don't auto-start.
- Custom shaders for spatial use **MaterialX** node graphs in Reality Composer Pro, not Metal directly.
- For SharePlay on visionOS, the system manages **shared context** so participants gesturing at the same virtual object see it in the same world position.
