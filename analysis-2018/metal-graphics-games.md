# Metal, Graphics & Games — WWDC 2018 Analysis

**Sessions covered:** 604 (Metal for OpenGL Developers), 606 (Metal for Ray Tracing Acceleration), 607 (Metal for Game Developers), 608 (Metal Shader Debugging and Profiling), 609 (Metal for Accelerating Machine Learning), 611 (Metal for VR), 612 (Metal Game Performance Optimization), 219 (Image and Graphics Best Practices), 605 (Inside SwiftShot), 102 (Platforms State of the Union §Metal)

## Headline

OpenGL is officially deprecated on every Apple platform — Metal is now the only forward-looking GPU API. WWDC 2018 piles on three big new Metal features: GPU-driven command encoding (drastically more parallelism, especially on the A11 Bionic with the new Apple-designed GPU), the new MPS Ray-Triangle Intersector (10× faster ray-triangle tests, scales linearly across multi-GPU on macOS), and MPS training kernels (full ML training on the local GPU, plus a Google partnership bringing Metal acceleration to TensorFlow). And Xcode 10's new visual GPU shader debugger lets you step through shader code at the pixel level.

## OpenGL/OpenCL Deprecated (604, 102)

- OpenGL ES on iOS, OpenGL/OpenCL on macOS, OpenGL on tvOS — all deprecated in 2018.
- They keep working but get no new features. Apple's recommendation: move to Metal, MPS, or MetalKit.
- Reasons cited: OpenGL doesn't expose new GPU features (tile shading, image blocks on A11+), debugging story is poor, and the legacy abstractions don't model modern GPUs well.
- 604 is the migration session: walks through state objects, command buffers, draw calls, shaders.

## GPU-Driven Command Encoding (612)

- Old: CPU encodes a list of GPU commands, GPU consumes them, then waits for the next list.
- New: a Metal compute shader running on the GPU itself can _encode the next set of commands_. The synchronization barrier between CPU and GPU disappears.
- Use case: massively-parallel scene traversal (thousands of objects culled from cone-of-vision, sorted by material, encoded into draw calls on the GPU).
- A11 Bionic Apple GPU added explicit support; works on Metal 2 across the line with varying degrees of efficiency.

## Ray Tracing Acceleration (606)

The flagship Metal feature for 2018:

- New `MPSRayIntersector` API does ray-triangle intersection on the GPU. Up to **10× faster** than CPU on iMac Pro for the same scene.
- Build an `MPSTriangleAccelerationStructure` from your vertex buffer once; reuse it for every frame.
- API works in two intersection modes: `.nearest` (find closest hit) and `.any` (early-out at first hit — perfect for shadow rays).
- Custom ray data can be appended to the standard ray struct (origin + direction + min/max distance) so you can carry your own per-ray state through the intersector.

### The Path-Tracing Algorithm in 200 Lines (606)

A complete path tracer demonstrated in the session:
1. Generate primary rays from camera through pixels.
2. Intersect with scene; shade hit points.
3. Cast shadow rays toward lights (use `.any` intersection mode).
4. Cast secondary rays in random directions for indirect lighting.
5. Loop step 2–4 for additional bounces.
6. Average across many frames to reduce noise.

- 30 fps at full resolution on iPad Pro 12.9" with the Amazon Lumberyard Bistro scene (~1M triangles, 20M rays/sec including primary, shadow, and secondary).
- Multi-GPU scaling on macOS: split frame between internal GPU + eGPUs. Adaptive load balancing measures per-GPU completion time and reassigns regions for the next frame. Live demo on iMac Pro hit ~30× CPU performance using internal GPU + RX 580 + Vega 64 simultaneously.

### Multi-GPU Best Practices (606)

- Use `MTLEvent` (new this year) for cross-GPU synchronization. Wait on event A from GPU B before reading buffers GPU A wrote.
- Buffer copies between GPUs: create paired `MTLBuffer`s wrapping the same memory via the new `noCopy` API. System memory backs both, so one GPU's writes are visible to the other's reads.
- Adaptive split: measure per-GPU time via command buffer completion handlers; resize render regions for the next frame based on relative speed.

## Metal Performance Shaders for ML Training (609, 102)

- Inference was supported pre-2018. Training kernels are new in 2018.
- An order-of-magnitude faster training on macOS than the prior MPSCNN inference graph would suggest.
- Apple + Google partnership: TensorFlow on macOS gets Metal acceleration. Early benchmarks: 20× faster than the previous OpenCL/OpenGL backend.
- Use case: on-device fine-tuning of large models. Combined with Core ML 2's quantization and custom layers, you can ship a custom-trainable model that adapts on the user's device with no cloud round-trip.

## Xcode 10 Metal Tools (608, 102)

- **Dependency Viewer** — visualize render passes as a graph. Critical for understanding multi-pass rendering in Unity / Unreal style engines (100+ passes per frame).
- **Visual GPU Shader Debugger** — pick a pixel, see the shader source executed for it, see the value of each variable as the line of code runs, see the execution mask (which threads in the warp executed each line). Catches shader bugs that profilers can't (e.g., "the lens flare is too green because line 47 used vector length instead of vector color").
- Update shaders live: edit a shader, hit "update shaders," recompile and reload — no app restart.

## Game Performance (612)

- Game Performance template combines System Trace + Metal System Trace + Frame Time + GPU/CPU utilization in one Instruments profile.
- Spot frame drops by frame ID; correlate to specific GPU command buffers or CPU stalls.
- A11 Bionic on iPhone 8 / X delivers ~2× GPU performance per watt vs. A10. Tile-based deferred renderer plus _tile shading_ and _image blocks_ enable techniques (e.g., subpasses with attached buffers as input to the next subpass) that were impossible on PowerVR-style GPUs.

## Image and Graphics Best Practices (219)

- The 590 KB JPEG → 10 MB in RAM gotcha (covered in `ios-12-performance.md`).
- Replace `UIGraphicsBeginImageContextWithOptions` with `UIGraphicsImageRenderer` — automatic format selection (Alpha 8 for grayscale, sRGB for color, Display P3 for wide).
- For thumbnails: `CGImageSourceCreateThumbnailAtIndex` from ImageIO — streaming, much less memory, ~50% faster than draw-into-smaller-rect.
- For HDR + Display P3 capture (iPhone 7+): request `extendedSRGB` color space; iOS converts automatically for non-wide displays.

## Inside SwiftShot (605)

- Apple's open-source multi-user AR game.
- Architecture lessons:
  - GameplayKit `GKEntity`/`GKComponent` model on top of ARKit anchors.
  - Deterministic physics ensure replays match across peers.
  - Networking: MultipeerConnectivity for the world map handoff, then UDP-style game state streaming.
  - Audio uses positional sound via `AVAudioEnvironmentNode` — slingshot fires sound localized to the launch position.
- Worth reading even for non-game-developers; the networking + state synchronization patterns generalize to multi-device collaboration apps.

## Cross-references

- Core Image / Python prototyping for filter chains: 719.
- Vision framework on Metal: 716, 717.
- Image and asset compression at the App Store level: 227.
- iPhone X / XS GPU specifics: see also Apple's hardware briefing materials referenced in 102.
