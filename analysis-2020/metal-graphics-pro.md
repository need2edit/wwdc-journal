# WWDC 2020 — Metal, GPU, Pro Display, HDR

The Metal story in 2020 is dominated by **Metal coming to Apple Silicon Mac** with a unified iOS+macOS feature set, plus Metal 2 deep-dives on Pro Display XDR, HDR video pipelines, and ray tracing. The "Apple GPU" tile-based deferred renderer architecture became a first-class Mac graphics target.

## Sessions Analyzed
- 10602 — Harness Apple GPUs with Metal (gateway)
- 10631 — Bring your Metal app to Apple silicon Macs (covered in apple-silicon analysis)
- 10632 — Optimize Metal Performance for Apple silicon Macs
- 10615 — Build GPU binaries with Metal
- 10616 — Debug GPU-side errors in Metal
- 10605 — Gain insights into your Metal app with Xcode 12
- 10603 — Optimize Metal apps and games with GPU counters
- 10001 — Explore Live GPU Profiling with Metal Counters
- 10012 — Discover ray tracing with Metal
- 10013 — Get to know Metal function pointers
- 10089 — Discover Core Image debugging techniques
- 10021 — Build Metal-based Core Image kernels with Xcode
- 10008 — Optimize the Core Image pipeline for your video app
- 10023 — Support Apple Pro Display XDR in your apps
- 10090 — Decode ProRes with AVFoundation and VideoToolbox
- 10010 — Export HDR media in your app with AVFoundation
- 10009 — Edit and play back HDR video with AVFoundation
- 10621 — Support performance-intensive apps and games

## TBDR (Tile-Based Deferred Renderer) — The Mac's New GPU Architecture

Apple Silicon Macs use the **same TBDR architecture as iPhone/iPad**, dramatically different from Intel/AMD/Nvidia immediate-mode renderers. Two phases:

1. **Tiling phase** — process all geometry, transform vertices, bin primitives into screen-space tiles via the **Tiled Vertex Buffer**.
2. **Rendering phase** — for each tile: load action → rasterize → Hidden Surface Removal → fragment shading → store action.

### What Makes TBDR Fast

- **Hidden Surface Removal (HSR)** — pixel-perfect, submission-order-independent culling. The GPU keeps the frontmost visible primitive ID per pixel and shades only the visible ones. **No overdraw on opaque geometry**, regardless of submission order.
- **Tile memory** — alpha blending happens entirely in registers; no fixed-function blending unit, no roundtrip to system memory.
- **Memoryless render targets** — `storageMode = .memoryless` for textures used only within a single render pass. Zero VRAM cost.
- **MSAA in tile memory** — samples live on-chip and resolve before flush. The multisample texture itself can be `.memoryless`. MSAA + deferred rendering is finally cheap.

### HSR Submission Order Tips

To maximize HSR efficiency:
1. **Render opaque geometry first** (any order is fine).
2. Then **alpha-tested / discard / depth-feedback** geometry.
3. Then **translucent meshes** (back-to-front).

**Don't interleave** opaque and non-opaque meshes. Don't interleave opaque meshes with different write masks. Translucent primitives force HSR to flush pixels — pixels that may then get occluded by later opaque meshes, costing you re-shading.

### Load and Store Actions: Critical Discipline

Under TBDR these aren't optimization hints — they directly control on-chip tile memory state:

- `loadAction = .load` only when previous content is needed (partial-frame draws on top of prior content).
- `loadAction = .clear` when starting fresh.
- `loadAction = .dontCare` only when you draw the entire frame buffer.
- `storeAction = .store` only when a later pass consumes the result.
- `storeAction = .dontCare` for transient buffers.

The "Bring your Metal app to Apple silicon Macs" session details how Metal applies **automatic compatibility workarounds** (only for apps built against Catalina or earlier SDK) for three common bugs that only manifest on TBDR:
1. `.dontCare` load action where `.load` was needed (artifacts on partial frames)
2. **Position invariance** missing — different vertex shaders compute positions slightly differently due to compiler optimizations; depth-compare `.equal` then fails (fix: pass `preserveInvariance` to compiler + mark `[[invariant]]` in MSL)
3. Sampling the current depth/stencil attachment in the same render pass (undefined behavior)

Apps built against Big Sur lose these workarounds — your code must be correct.

## Modern Apple GPU Features (A11+, Apple Silicon Mac)

Beyond TBDR fundamentals, modern Apple GPUs add programmable stages that let you do more on-chip:

### Imageblock

A 2D data structure in tile memory accessible from both fragment and compute kernels. Width × height × pixel-depth. Atomic load/store of image data (vs. pixel-by-pixel into threadgroup memory).

### Tile Shaders

Compute kernels you can dispatch **mid-render-pass** that access the imageblock. Dispatches interleave with draw calls; the GPU barriers automatically against earlier and later draws.

This enables, for example, **tiled deferred rendering**: G-buffer pass → tile compute (light culling per-tile) → lighting pass — **all merged into a single render pass** with no intermediate textures spilling to VRAM.

### Imageblock Sample Coverage Control

Programmatic resolve of MSAA samples per-pixel from a tile shader. Lets you implement custom per-target resolve (e.g., HDR linear color resolves differently from linear depth) and route blending decisions based on per-pixel sample uniformity.

### SIMD Group Size = 32 on Apple GPUs

The most subtle correctness pitfall. AMD desktop GPUs typically have SIMD = 64. Compute shaders that "got lucky" assuming SIMD == threadgroup size produce visual artifacts on Apple. **Always**:
- Query `threads_per_simdgroup` (in shader) or `threadExecutionWidth` (Metal API).
- Use `simdgroup_barrier` for single-SIMD-group threadgroups; `threadgroup_barrier` only when crossing groups (it's expensive on Apple).
- Best perf: rewrite shaders for 32-thread SIMD groups to skip threadgroup barriers entirely.

## Feature Detection: Stop Querying GPU Names

In 2020, query `supportsFamily(_:)` (returns whether a device supports a Metal feature family like `.apple7`, `.mac2`) and individual feature properties. Stop:
- Branching on `device.name` strings (breaks across new GPUs)
- Assuming Apple GPU features aren't available on macOS (they are now)
- Assuming `isLowPower == true` means integrated/treat-as-discrete — Apple GPUs return `false` from `isLowPower` and should be treated like discrete GPUs for tier decisions

## Ray Tracing with Metal (10012, 10013)

Metal 2.4 introduces ray tracing acceleration:
- `MTLAccelerationStructure` — bounding-volume hierarchies for your scene
- Ray tracing in compute kernels via the `metal_raytracing` shader header
- **Function pointers** — call shader functions indirectly via pointers stored in buffers, enabling per-material shading without recompilation. Critical for ray-traced rendering where each ray-mesh intersection runs a different shader.

The ray tracing API in 2020 is **compute-pipeline-based** (full hardware RT acceleration came later years). Build acceleration structures once, intersect rays per-frame.

## Metal Tooling Improvements

### Build GPU Binaries (10615)

Pre-compile Metal shaders to GPU machine code at app build time, embedded in your binary. Eliminates the runtime shader compilation pause on first launch. Apple Silicon Macs can compile multi-architecture binaries (Intel GPU + Apple GPU).

### Debug GPU-Side Errors (10616)

Xcode 12 surfaces shader-side errors with backtraces, including command-encoder validation failures, out-of-bounds buffer reads, etc. Setting up Metal API validation in the scheme catches mistakes earlier.

### Xcode 12 Metal Insights (10605)

The Metal Frame Capture window adds:
- Memory bandwidth visualization per render pass
- Tile memory usage heatmap
- Detailed GPU counters integrated with the captured frame

### GPU Counters & Live Profiling (10001, 10603)

`MTLCounterSet` API gives you real-time GPU performance counters during execution: ALU utilization, texture sample rates, fragment overdraw, memory bandwidth. Use these to drive an in-app perf-overlay or to log telemetry.

## Core Image Pipeline (10008, 10021, 10089)

### Build Metal-based CI Kernels (10021)

Core Image kernels are now written in **Metal Shading Language** (replacing the older CIKernel Language). Compiled at build time via Xcode → faster startup, full Metal Compiler optimizations.

### Optimize CI for Video (10008)

Specific optimizations for video frame pipelines:
- Use `CIRenderDestination` with explicit format/colorspace for fewer color conversions
- Combine multiple filters into a single render pass to maximize tile-memory benefits
- Avoid roundtripping through `CIImage` after every filter — chain them

### CI Debugging (10089)

Use the CI Image debug overlay to visualize the filter graph, identify redundant transforms and intermediate buffers.

## Pro Display XDR & HDR (10023, 10009, 10010)

### Pro Display XDR Support (10023)

To support the Pro Display XDR (and other reference displays):
- **Reference modes** — query `NSScreen.preferredReferenceModes` for the display's certified color/luminance presets
- Use `EDR (Extended Dynamic Range)` rendering — request EDR-capable layers, write floats above 1.0 for highlights
- Color-manage with explicit `NSColorSpace` / `CGColorSpace` everywhere; never assume sRGB

### HDR Video Editing & Playback (10009, 10010)

- AVFoundation now supports HDR (HDR10, HLG, Dolby Vision) editing pipelines
- Use `AVPlayer` + `AVPlayerLayer` with `wantsExtendedDynamicRangeContent = true` for EDR playback
- Export with `AVAssetExportSession` and HDR-specific presets to preserve metadata

### ProRes Decoding (10090)

VideoToolbox now exposes ProRes decode acceleration. Useful for video apps targeting professional workflows.

## Audio Workgroups (10224 — Cross-cutting)

Joining your realtime audio threads to the audio device's `os_workgroup` makes the kernel scheduler aware that those threads have a deadline. **Critical** on Apple Silicon Macs with their asymmetric P/E core architecture — without this signal, audio threads may be scheduled on E cores and cause glitches.

```swift
let workgroup = audioUnit.osWorkgroup  // From AURemoteIO/AUHAL property
os_workgroup_join(workgroup, &joinToken)
// ... realtime work ...
os_workgroup_leave(workgroup, &joinToken)
```

For **Audio Units that create their own threads**, implement the new `AURenderContextObserver` block. It receives the workgroup before each render call (it can change between renders) — join your auxiliary threads to it.

For asynchronous worker threads with a different deadline than the device, create your own workgroup with `AudioWorkIntervalCreate`.

`os_workgroup_max_parallel_threads()` recommends thread count.

## Cross-References
- [apple-silicon-mac-transition.md](apple-silicon-mac-transition.md) — TBDR fundamentals, position invariance, SIMD size pitfalls.
- [arkit-realitykit-usd.md](arkit-realitykit-usd.md) — RealityKit performance heavily depends on these patterns.
- [media-hls-audio.md](media-hls-audio.md) — HLS and audio pipelines complement the HDR video story.

## Adoption Checklist
- [ ] Adopt `supportsFamily(_:)` everywhere — eliminate device-name string queries.
- [ ] Audit load/store actions across all render passes; use `.dontCare` aggressively where safe.
- [ ] Make intermediate textures `.memoryless` where they never leave a single render pass.
- [ ] If you write compute shaders, query `threadExecutionWidth` and write 32-SIMD-friendly variants.
- [ ] Verify position invariance enabled on shaders that participate in multi-pass depth-equal rendering.
- [ ] If you produce realtime audio, join `os_workgroup`s.
- [ ] Pre-compile Metal shaders to GPU binaries (10615) for faster startup.
- [ ] If a video/photo app, evaluate Metal-based CI kernels for hot filter paths.
- [ ] If you produce/consume HDR content, audit AVFoundation pipeline for EDR support.
