# WWDC 2023 — Graphics, Games, Metal, & USD

WWDC 2023's gaming push: Metal 3 ray tracing, the "Bring your game to Mac" trilogy (Game Porting Toolkit), Unity for visionOS, ScreenCaptureKit, USD ecosystem.

## Sessions Analyzed
- 10123 — Bring your game to Mac, Part 1: Make a game plan
- 10124 — Bring your game to Mac, Part 2: Compile your shaders
- 10125 — Bring your game to Mac, Part 3: Render with Metal
- 10128 — Your guide to Metal ray tracing
- 10127 — Optimize GPU renderers with Metal
- 10089 — Discover Metal for immersive apps
- 10086 — Explore the USD ecosystem
- 10096 — Build great games for spatial computing
- 10093 — Bring your Unity VR app to a fully immersive space
- 10088 — Create immersive Unity apps
- 10136 — What's new in ScreenCaptureKit

## Game Porting Toolkit (10123–10125)

The most consequential game-development announcement of the year. Apple shipped a TOOLKIT that lets Windows games run on Mac for EVALUATION purposes BEFORE you've ported them.

The trilogy of sessions walks through the actual port:
1. **Make a game plan (10123)** — evaluate your game with the toolkit, scope the work.
2. **Compile your shaders (10124)** — translate HLSL to Metal Shading Language using the new tools.
3. **Render with Metal (10125)** — port the rendering layer, integrate Apple Silicon-specific features.

Game Porting Toolkit components:
- A wine/CrossOver-derived runtime that translates DirectX 12 to Metal 3 in real time.
- `metal-shaderconverter` CLI: converts DXIL (compiled HLSL) to Metal-compatible IR.
- New profiler views in Xcode Metal debugger for game workloads.

This isn't shipping product — it's a developer evaluation tool. After evaluation, you do the actual port using the converted shaders + native Metal rendering.

Result: Death Stranding, RE Village, Cyberpunk-class games can run on Apple Silicon Macs with reasonable perf.

## Metal Ray Tracing (10128)

Metal 3 ray tracing API receives major updates:
- `MTLAccelerationStructure` build performance significantly improved (faster BVH builds).
- `MTLIntersectionFunctionTable` for custom intersection logic (great for procedural geometry, hair, foliage).
- Motion blur ray tracing — sample over time for motion-blurred reflections.
- Compaction of acceleration structures to reduce memory.

Patterns:
```metal
ray r = ray(origin, direction);
intersector<triangle_data> intersector;
auto result = intersector.intersect(r, accelerationStructure, mask);
```

Recommended for: dynamic global illumination, accurate reflections in transparent surfaces, hair rendering, ambient occlusion in dynamic scenes.

## Optimize GPU Renderers (10127)

Best practices for Apple Silicon:
- Use TILE shading where possible — keep work in tile memory.
- Minimize render pass changes — each transition costs.
- Use `MTLHeap` for transient resources — alloc/free is essentially free within a frame.
- Programmable blending in fragment shaders (Apple Silicon exclusive, very fast).
- Use indirect command buffers (ICBs) to record draw calls on GPU.
- Argument buffers > individual binding slots — higher arg counts, lower CPU cost.

GPU counters in Xcode now show:
- Tile memory usage per pass
- Threadgroup occupancy
- Bandwidth read/write per resource

## Discover Metal for Immersive Apps (10089)

For visionOS, you can use Metal directly inside a `CompositorServices` layer for fully custom rendering (e.g., your own engine instead of RealityKit).

Key differences vs iOS Metal:
- STEREO RENDERING: render two views per frame (left/right eye).
- FOVEATED RENDERING: shaders write higher detail in the fovea region; the system upscales the periphery.
- VIEWPORT ARRAYS: render to two viewports in one draw call.
- Reproject for the late-stage warp — submit a frame with predicted head pose; the system warps it to the actual head pose at scanout.

Frame budget: 90fps stereo = 11.1ms per frame for two eyes. Tight.

## USD Ecosystem (10086)

Universal Scene Description (USD) is Apple's chosen 3D interchange format across:
- visionOS (RealityKit)
- macOS (Quick Look, SceneKit)
- Reality Composer Pro

Key tools:
- `usdz` is the binary archive format (single file, drag-and-drop friendly).
- `usda` is ASCII (readable, version-controllable).
- `usdc` is binary (efficient).
- `usdzip` packs a folder of USD + textures into `.usdz`.

USD lets you:
- LAYER: an asset can override another non-destructively. (Reality Composer Pro uses this.)
- VARIANT: multiple looks/configurations in one asset (color variants of a chair).
- INSTANCE: multiple copies of the same prim with shared geometry — for forests, particles.

Pixar maintains the open-source `OpenUSD` repo; Apple ships an SDK (`Foundation USD`).

USDZ ASSET PIPELINE for visionOS apps:
1. Author in Blender / Maya / Cinema 4D.
2. Export to USDZ.
3. Drag into Reality Composer Pro for component setup.
4. Reference from RealityKit code.

## ScreenCaptureKit Updates (10136)

ScreenCaptureKit (introduced 2022 as the modern macOS capture API) gains:
- Microphone capture in the same stream.
- Improved performance for game capture (no compositor overhead).
- Mouse cursor visibility control.
- Window-specific capture even when window is offscreen.
- Application-only capture (mute one app's audio in a system-wide capture).

Replaces the deprecated `CGWindowList` + `AVCaptureScreenInput` APIs entirely. New macOS apps MUST use ScreenCaptureKit.

## Unity for visionOS (10088, 10093)

Unity (with Apple's collaboration) supports visionOS as a target. Two paths:
1. **VR (fully immersive)**: existing Unity VR projects port to visionOS with minimal changes.
2. **Mixed reality / shared space**: Unity's PolySpatial framework renders Unity content into a RealityKit scene. Shaders are converted via shader graph → MaterialX.

PolySpatial is the bridge: Unity scene tree → RealityKit entity tree, kept in sync. Most Unity features work; some (custom shaders, certain post-processing) require shader conversion.

## Pathways

- **Game porting**: 10123 → 10124 → 10125 → 10127
- **Modern Metal renderer**: 10128 → 10127
- **visionOS rendering (custom)**: 10089 → 10128
- **3D asset pipeline**: 10086 → 10202 → 10273
- **Unity for visionOS**: 10088 → 10093

## Hidden Gems

- The Game Porting Toolkit is a DEVELOPER tool — it's not for end users to play Windows games on Mac. After evaluation, you do a native port.
- Metal 3 ray tracing performance on M2 Max is competitive with mid-range desktop GPUs for offline-quality scenes.
- USD layer composition lets you have a "base" asset that artists update, while engineers add components in a separate layer — no merge conflicts.
- ScreenCaptureKit can record OFFSCREEN windows — useful for capturing minimized windows for thumbnail generation.
- Foveated rendering on visionOS is automatic if you use RealityKit; with raw Metal, you opt in via a layer configuration.
- The DXIL → Metal IR converter handles most DirectX 12 shaders, but compute shaders with explicit wave intrinsics need manual conversion.
- USDZ files can include AUDIO (USD has audio prims) — let your 3D assets include sound design out of the box.
- Indirect command buffers (ICBs) let you record millions of draw calls on GPU; CPU is often the bottleneck for very large scenes, and ICBs eliminate it.
- ScreenCaptureKit requires user permission via System Settings; first call shows a permission prompt with a thumbnail of what would be captured.
