# Metal Graphics Debut — WWDC 2014 Analysis

**Sessions covered:** 603 (Working with Metal: Overview), 604 (Working with Metal: Fundamentals), 605 (Working with Metal: Advanced), 601 (Harnessing the Power of the Mac Pro with OpenGL and OpenCL), 419 (Advanced Graphics and Animations for iOS Apps)

## Headline

Metal is iOS 8's **low-overhead, A7-optimized GPU programming API** that delivers **up to 10× more draw calls per frame** versus OpenGL ES. Apple designed it from a clean sheet to eliminate the CPU bottleneck of legacy graphics APIs, taking advantage of A7's unified memory architecture and tile-based deferred-mode rendering.

## The Core Mental Model (session 603)

- **Move expensive work out of the per-frame hot path**:
  - **App build time**: shader compilation. Your `.metal` source files are compiled to GPU bytecode by Xcode at build time, then compiled to device-specific code at content-load time. **NO draw-time compilation.** (603)
  - **Content load time**: pipeline state validation. Combine shaders + blend state + framebuffer descriptors into immutable `MTLRenderPipelineState` objects once.
  - **Draw call time**: just submit work. No state translation, no validation — those have already happened.
- **CPU savings → more draw calls**: the 10× number isn't a GPU improvement, it's a CPU-side overhead reduction. Each draw call in OpenGL ES requires the driver to validate state, recompile shaders if needed, encode commands. Metal does all that ahead of time, so each draw call is a tiny commit (603).
- **You explicitly control GPU work submission** — no implicit "the driver might do anything behind your back" assumptions. The clarity is a major selling point for game engine developers (603).

## The Object Graph (session 603)

- **`MTLDevice`** — the GPU. Get one with `MTLCreateSystemDefaultDevice()`. iOS 8: A7+ devices (iPhone 5s, iPad Air, iPad mini Retina).
- **`MTLCommandQueue`** — submit ordering. One per app typically.
- **`MTLCommandBuffer`** — a batch of GPU work. Lightweight; create one per frame (or more) and dispose.
- **`MTLCommandEncoder`** — translates API calls to GPU machine code. Three flavors:
  - **`MTLRenderCommandEncoder`** — graphics rendering pass.
  - **`MTLComputeCommandEncoder`** — general-purpose compute (replaces OpenCL on iOS).
  - **`MTLBlitCommandEncoder`** — async data copies between resources.
- **`MTLRenderPipelineState`** — immutable bundle of shaders + blend + vertex format + framebuffer attachments. Built from a `MTLRenderPipelineDescriptor` once; reused per draw.
- **`MTLBuffer`** / **`MTLTexture`** — memory. Buffers are unformatted; textures are formatted images.

## A7 Unified Memory (session 603)

- CPU and GPU share physical memory. **No implicit copies**, no "upload to GPU" step. You allocate a `MTLBuffer`, get a CPU pointer, write data, the GPU sees the same memory.
- HIDDEN GEM: `MTLBuffer.contents()` returns a raw `void *` you can write to with no `glMapBuffer`-style locking. **You** are responsible for not writing while the GPU reads — schedule work to avoid concurrent access (603).
- **No cache coherency management** — Apple handles it. No `glFlush`, no `glFinish` between the write and the GPU read.
- HIDDEN GEM: a `MTLBuffer` and a `MTLTexture` can share underlying storage — interpret the same bytes as either a buffer or a texture. **Reinterpret pixel formats without copying** by creating a second texture aliased to the first's storage (603).

## Render Passes and the Tile Cache (session 603)

- A7's GPU is a **tile-based deferred-mode renderer (TBDR)**. The framebuffer is divided into tiles; each tile is rendered in fast on-chip memory, then committed to main memory.
- **Load and store actions** on `MTLRenderPassAttachmentDescriptor`:
  - `loadAction`: `.clear`, `.load`, or `.dontCare` — what to do at the start of a pass.
  - `storeAction`: `.store`, `.dontCare`, or `.multisampleResolve` — what to do at the end.
- HIDDEN GEM (PERFORMANCE): use `.dontCare` for any attachment you don't need at end of pass. Skipping the store of a depth buffer saves significant memory bandwidth on every frame (603).
- The 603 talk shows a 4-read-4-write before-Metal flow becoming a 1-read-1-write after-Metal flow on the same scene by using `.clear`/`.dontCare` correctly. **This is one of the biggest Metal-only optimizations** because OpenGL ES had no equivalent control (603).

## Multi-threaded Command Encoding (session 603)

- Multiple threads can encode into separate `MTLCommandBuffer`s in parallel. **No locks, no atomics in the Metal implementation** — each command buffer is a thread-private builder.
- You commit them to the queue in your desired execution order; the queue serializes execution while the encoding parallelism saved CPU time.
- BEST PRACTICE: split a frame's draw calls across cores by render pass or scene region. The 603 talk demonstrates 4× speedup on a 4-core CPU encoding into 4 command buffers in parallel.

## The Metal Shading Language (session 603, 604)

- **C++11 subset** with attribute syntax for hardware bindings. If you know C++, you know MSL.
- **Unified for graphics AND compute** — same language, same source files for both vertex shaders, fragment shaders, compute kernels.
- **Argument tables** map shader parameters to API resources. `[[buffer(0)]]`, `[[texture(1)]]`, `[[sampler(2)]]` attributes on function parameters tell Metal which slot in the encoder's argument table to read from. The host code does `encoder.setVertexBuffer(myBuffer, offset: 0, index: 0)` to populate slot 0; the shader function declared `device float4 *vertices [[buffer(0)]]` reads from it.
- **Compiled offline by default**: `.metal` files in your Xcode project are compiled to a `.metallib` archive that ships in your app bundle. Load with `device.makeDefaultLibrary()`.
- **Runtime compilation supported** for dynamically-generated shader sources (`device.makeLibrary(source: ..., options: ...)`) — useful for custom effects from user content. Slower; avoid in performance-critical paths (603).

## Compute (Sessions 603, 605)

- General-purpose data-parallel work on the GPU. Same `MTLDevice`, same `MTLBuffer`/`MTLTexture` resources as graphics — interleave compute and render in the same command buffer.
- Replaces **OpenCL on iOS** (which never shipped publicly) and OpenGL compute shaders. On Mac, OpenCL stays around but Metal Compute is recommended for new work.
- BEST PRACTICE: use compute for image processing, particle simulation, neural network inference (this years before Core ML). The Crytek demo in 603 uses Metal Compute for character physics on the GPU.

## Blits — Async Resource Updates (session 603)

- `MTLBlitCommandEncoder` for async copies between buffers and textures, mipmap generation, buffer fills with constant values.
- Run in parallel with render and compute passes — useful for streaming texture updates without stalling rendering.

## Dev Tools — Xcode Integration (session 603)

- **Metal Frame Capture**: take a snapshot of a frame's GPU work; inspect every draw call, every state object, every resource (texture contents, buffer contents).
- **Per-line GPU time profiling** in your shader source. The 603 talk demonstrates clicking on a specific shader line and seeing its millisecond cost (603).
- **Metal Performance Report** in the Xcode debug navigator — frame rate, GPU usage, expensive shaders ranked.
- HIDDEN GEM: shader compile errors and warnings appear at **app build time** — same red-and-yellow you get for Swift/Obj-C code. Catch shader bugs before your customers do (603).

## Best Practices

- **Build shaders offline**. Use the runtime compiler only for genuinely dynamic content.
- **Configure load/store actions explicitly**. The default may store more than you need; explicit `.dontCare` saves bandwidth on every frame.
- **Compose immutable state into pipelines**. Don't mutate `MTLRenderPipelineState`s; build a finite set at content load and bind by index (603).
- **Use `.shared` storage on iOS** (the unified-memory mode) for resources you write from CPU each frame. Use `.private` for GPU-only resources (e.g. depth buffers, intermediate render targets) (603).
- **Multi-thread your encoding** at scenes with thousands of draw calls. Single-thread encoding is a CPU bottleneck even with Metal's reduced overhead.

## Hidden Gems

- HIDDEN GEM: **the Crytek "Collectables" demo at WWDC 2014** rendered 4,000 draw calls per frame on iPad Air using Metal — geometry-cached destruction physics that simply wasn't possible on OpenGL ES. **10× draw call increase enables qualitatively new content** (603).
- HIDDEN GEM: Metal Compute can run alongside graphics in the same command buffer. Image post-processing (bloom, DOF) compute kernels interleaved with render passes — efficient pipeline (605).
- PERFORMANCE: framebuffer tile cache locality matters. Sub-pass dependencies declared via `MTLRenderPassDescriptor` let Metal keep intermediate render targets in tile cache, never round-tripping to main memory. The 603 example is the deferred-shading G-buffer staying entirely on-chip.
- WARNING: A7-only on iOS at launch (iPhone 5s, iPad Air, iPad mini Retina). Apps targeting older devices need an OpenGL ES fallback path. Plan for two render backends until A6 support is dropped.

## Cross-references

- **SpriteKit (606, 608)** can render via Metal under the hood (still presented as the same SpriteKit API to your code) — adopt SpriteKit for 2D and you get Metal performance for free.
- **SceneKit (609, 610)** similarly — high-level 3D API on top of Metal/OpenGL.
- **Core Image (514, 515)** can use Metal as its rendering backend for filter chains.
- **Core Animation (419)** uses Metal under the hood for CALayer compositing on A7.
- **OpenGL ES** is **not deprecated in 2014** but Apple is clearly steering new development toward Metal. The OpenGL ES deprecation announcement comes 4 years later in WWDC 2018.

## Migration Guidance

- **2D games** — adopt **SpriteKit** if you can; it's already Metal-backed where appropriate. Don't write Metal directly unless you have specific control needs.
- **3D games** — choose **SceneKit** for high-level scene graph + animation; choose **Metal** directly if you have a custom engine and need maximum performance.
- **Existing OpenGL ES games** — keep them. Metal porting is a major undertaking (typically 2-6 months for a real engine). Plan it for your next major release if 10× draw call headroom would unlock new content.
- **General-purpose compute** — start migrating from OpenCL to Metal Compute on iOS for new work; OpenCL remains available on Mac.
