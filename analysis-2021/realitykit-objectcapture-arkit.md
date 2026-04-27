# RealityKit 2, Object Capture, and ARKit 5 (WWDC 2021)

## Sessions covered
- WWDC21-10074 — Dive into RealityKit 2
- WWDC21-10075 — Explore advanced rendering with RealityKit 2
- WWDC21-10076 — Create 3D models with Object Capture
- WWDC21-10078 — AR Quick Look, meet Object Capture
- WWDC21-10077 — Create 3D workflows with USD
- WWDC21-10073 — Explore ARKit 5
- WWDC21-10245 — Design for spatial interaction
- WWDC21-10039 — Classify hand poses and actions with Create ML

## Best practices

- **Components store data, systems hold logic, entities are just IDs** — RealityKit 2 moves toward a pure ECS model. Don't subclass `Entity`; add components instead so behaviors can be added/removed at runtime without re-allocating (WWDC21-10074).
- **Mark codable components for network sync** in multiplayer — RealityKit auto-syncs codable components but does NOT sync system state. Keep all multiplayer-relevant data in components (WWDC21-10074).
- **Specify `System` dependencies** with `.before(MotionSystem.self)` / `.after(...)`. Without explicit ordering, systems run in registration order, which is fragile (WWDC21-10074).
- **Always declare `EntityQuery` as `static let`** so the query isn't rebuilt every frame (WWDC21-10074).

## Hidden gems

- `TransientComponent` — components conforming to it are NOT inherited when the entity is cloned, but DO sync over the network if also `Codable`. Perfect for "fish-has-seen-the-octopus" runtime fear flags (WWDC21-10074).
- `subscription.storeWhileEntityActive(entity)` — replaces manual cancellable bookkeeping for entity event subscriptions (WWDC21-10074).
- `PhysicallyBasedMaterial` is a USD-shaped material superset of `SimpleMaterial`. Roughness, metallic, normal map, AO, **clearcoat**, opacityThreshold (alpha-test cutoff) — all configurable per-property (WWDC21-10074).
- `CustomMaterial` with surface shader + geometry modifier (Metal) — custom vertex/fragment effects (WWDC21-10074, WWDC21-10075).
- `CharacterControllerComponent` — capsule-shaped physical controller that interacts with LiDAR-generated room mesh. `move(to:)` honors obstacles; `teleport(to:)` ignores them (WWDC21-10074).
- `BlendLayer` for animation cross-fade — play Walk on top of Idle, smoothly modulate `blendFactor` to interpolate. Replaces snapping between clips (WWDC21-10074).
- Object Capture takes ~20–200 photos and produces a USDZ at four detail levels (Reduced/Medium/Full/Raw). The HelloPhotogrammetry CLI sample lets you try it before writing any code (WWDC21-10076).
- iPhone 12 Pro/Pro Max images embed depth+gravity automatically — Object Capture uses these to recover real-world scale and to orient the model right-side-up (WWDC21-10076).
- `PhotogrammetrySession` outputs are an `AsyncSequence` — `for try await output in session.outputs { … }` rather than KVO/delegate (WWDC21-10076).
- The interactive Object Capture workflow: request a `.preview` model + `.bounds`, edit the bounding box in your UI to clip out the pedestal/turntable, then request `.full` — the cropped final reconstruction is optimized away from wasted geometry (WWDC21-10076).
- ARKit 5 adds **Location Anchors** support beyond the original five US cities (WWDC21-10073).
- `AR Quick Look` accepts USDZs from Object Capture directly, plus Reality Composer behaviors. You can swap models on tap with no code (WWDC21-10078).

## Performance

- **Reduced detail level** is the default recommendation for AR Quick Look on the web — fastest download, fewest triangles, three PBR channels (Diffuse/Normal/AO) (WWDC21-10076, WWDC21-10078).
- **Medium** when you have one hero asset and download time isn't the bottleneck (e.g., bundled in-app). **Full** for offline pro/film workflows (Diffuse/Normal/AO/Roughness/Displacement). **Raw** for in-house pipelines that bake their own materials (WWDC21-10076).
- Request multiple detail levels in a single `process` call so the engine shares computation between them — much faster than sequential calls (WWDC21-10076).

## Migration guidance

- If you previously used `subscribe(to: SceneEvents.update)` closures on a Game Manager, move that logic to a `System` and register it at app launch. Cleaner separation, easier ordering, parallelism-ready (WWDC21-10074).

## Cross-references

- Spatial design (WWDC21-10245) introduces gaze + tap, world-space anchored UI, and direct-touch interactions — the concepts return in 2023 visionOS sessions.
- Object Capture pairs with `RoomPlan` (introduced 2022) for full room → 3D scene workflows.
- For underlying USD authoring, see WWDC21-10077 ("Create 3D workflows with USD").
