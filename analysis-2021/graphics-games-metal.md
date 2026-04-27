# Graphics, Games & Metal (WWDC 2021)

Bindless rendering, ray tracing, MetalFX precursors, variable refresh rate displays, on-screen virtual game controllers.

## Sessions covered
- WWDC21-10148 — Optimize high-end games for Apple GPUs
- WWDC21-10149 — Enhance your app with Metal ray tracing
- WWDC21-10150 — Explore hybrid rendering with Metal ray tracing
- WWDC21-10152 — Accelerate machine learning with Metal Performance Shaders Graph
- WWDC21-10153 — Create image processing apps powered by Apple silicon
- WWDC21-10157 — Discover Metal debugging, profiling, and asset creation tools
- WWDC21-10229 — Discover compilation workflows in Metal
- WWDC21-10286 — Explore bindless rendering in Metal
- WWDC21-10147 — Optimize for variable refresh rate displays
- WWDC21-10081 — Tap into virtual and physical game controllers
- WWDC21-10067 — Bring Recurring Leaderboards to your game
- WWDC21-10066 — What's new in Game Center

## Best practices

- **Bindless rendering**: replace per-draw-call `setVertexBuffer`/`setFragmentTexture` calls with a single argument buffer holding a heap of resources. Cuts CPU overhead by 10-50% for scenes with hundreds of materials (WWDC21-10286).
- **Hybrid ray tracing**: don't ray-trace everything. Use the rasterizer for primary rays, ray-trace only for reflections/shadows/AO (WWDC21-10149, WWDC21-10150).
- **Variable refresh rate**: declare your preferred frame rate via `CADisplayLink.preferredFrameRateRange` so ProMotion displays don't waste battery rendering at 120Hz when your app updates at 60 (WWDC21-10147).

## Hidden gems

- **`GCVirtualController`** — Apple-vended on-screen joystick UI that appears to your code as a regular `GCController`. Customizable button shapes via Bezier paths. Replaces hand-rolled touch overlays (WWDC21-10081).
- DualSense **adaptive trigger** API: `GCDualSenseAdaptiveTrigger.setModeFeedback(...)` for resistance, `setModeVibration(...)` for force-vibration. Works on all Apple platforms (WWDC21-10081).
- **Game Controller `.sfSymbolsName`** returns the right glyph honoring the user's system-wide button remap. Always show the user-correct glyph in tutorials/UIs (WWDC21-10081).
- ReplayKit + Game Controller integration: the share button on a controller starts/stops a ReplayKit clip, including the new 15-second rolling buffer mode (WWDC21-10081, WWDC21-10101).
- MPSGraph (Metal Performance Shaders Graph) gains Stable Diffusion-style ML compute primitives — runs neural networks directly on GPU with Apple Silicon-optimized kernels (WWDC21-10152).
- Metal asset creation tools added geometry shaders, mesh shaders precursors (WWDC21-10157).

## Performance

- Bindless rendering wins more than 50% CPU on heavy-draw-call scenes (Apple internal benchmarks for AAA ports).
- ProMotion variable rate at 24Hz uses ~30% less power than locked-60 for the same content (WWDC21-10147).

## Migration guidance

- For older games using individual texture binding: gradually migrate to argument buffers — no need for an all-at-once rewrite. Start with material textures, then geometry buffers (WWDC21-10286).

## Cross-references

- Metal ray tracing (WWDC21-10149) is the API foundation for Game Porting Toolkit which ships in 2023 (WWDC23-10123).
- Game Controller framework on iPad/iPhone now supports Sony DualSense and Xbox Series X controllers system-wide (WWDC21-10081).
