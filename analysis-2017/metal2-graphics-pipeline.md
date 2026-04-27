# Metal 2 & Graphics Pipeline — WWDC 2017 Analysis

**Sessions covered:** 601 (Introducing Metal 2), 603 (VR with Metal 2), 607 (Metal 2 Optimization and Debugging), 608 (Using Metal 2 for Compute), 604 (SceneKit: What's New), 605 (SceneKit in Swift Playgrounds), 609 (Going Beyond 2D with SpriteKit), 610 (From Art to Engine with Model I/O), 821 (Get Started with Display P3)

## Headline

Metal 2 lands on macOS High Sierra and iOS 11, with a massive boost on the new **A11 Bionic** chip's TBDR (tile-based deferred renderer) GPU. The headline features: **argument buffers** (massively reduce CPU draw-call overhead), **MPS for ML** (Metal Performance Shaders for neural networks), the A11-exclusive **imageblocks**, **tile shading**, **raster order groups**, and **imageblock sample coverage control** — pipelining tricks that let high-end mobile graphics engines run techniques that previously required desktop-class hardware. macOS High Sierra adds **VR support via Metal 2** for the first time.

## Argument Buffers (601)

Replace dozens of `setVertexBuffer:offset:atIndex:` / `setTexture:atIndex:` calls per draw with a single buffer of references.

```metal
struct Material {
    texture2d<float> diffuse  [[id(0)]];
    texture2d<float> normal   [[id(1)]];
    sampler          samp     [[id(2)]];
    float3           tint     [[id(3)]];
};

fragment float4 frag(Material material [[buffer(0)]]) { … }
```

Then on the CPU:

```swift
let encoder = device.makeArgumentEncoder(arguments: [/* MTLArgumentDescriptors */])!
let buf = device.makeBuffer(length: encoder.encodedLength)!
encoder.setArgumentBuffer(buf, offset: 0)
encoder.setTexture(diffuse, index: 0)
encoder.setTexture(normal,  index: 1)
encoder.setSamplerState(samp, index: 2)
// Reuse `buf` across many draws - bind once, use many times.
```

- **PERFORMANCE**: a scene with 5,000 draws on iOS that took ~200 ms of CPU encoding per frame drops to ~40 ms with argument buffers. CPU-bound scenes scale 5-10x.
- **HIDDEN GEM**: argument buffers can hold POINTERS to other argument buffers (Tier-2 only on A11+/macOS High Sierra) — build a single "scene description" buffer and let the GPU traverse it. This unlocks GPU-driven rendering pipelines.

## A11 GPU Architecture (601)

The A11 GPU is Apple's first in-house GPU for iOS. Key TBDR enhancements:

- **Imageblocks** — per-tile, programmable on-chip memory accessible from fragment shaders.
- **Tile shading** — kernels that run per-tile in the middle of the render pass without a full memory round-trip.
- **Raster order groups** — fine-grained ordering guarantees for overlapping fragment work.
- **Imageblock sample coverage control** — programmatic control over which sample slots get written for MSAA workloads.

These features collectively let you implement order-independent transparency, deferred shading, tile-based light culling, and screen-space AO **without a single intermediate render target store/load**, on a phone.

## Imageblocks (601, 607)

Tile-local memory, declared and accessed in MSL like a structured array:

```metal
struct GBuffer {
    half4 color;
    half3 normal;
    half2 motionVector;
};

fragment GBuffer geometryPass(/* ... */ imageblock<GBuffer, imageblock_layout_explicit> gbuf) {
    GBuffer pixel;
    pixel.color = …;
    pixel.normal = …;
    return pixel;
}

fragment half4 lightingPass(imageblock<GBuffer, imageblock_layout_explicit> gbuf,
                            uint2 tid [[thread_position_in_quadgroup]]) {
    GBuffer pixel = gbuf.read(tid);   // never touched DRAM
    return shade(pixel);
}
```

- **PERFORMANCE**: deferred shading on A11 keeps the entire G-buffer on-chip — bandwidth savings 5-10x vs traditional store-then-sample.
- Imageblocks are declared per-render-pass via `MTLTileRenderPipelineDescriptor`.

## Tile Shading (601, 607)

Run a compute-style kernel between two render passes WITHOUT exiting the tile. Lets you do:

- Tile-based light culling (find which lights intersect this 32×32 tile).
- Local tone mapping (compute average luminance per tile, apply curve in second pass).
- Screen-space ambient occlusion using on-chip depth + normals.

```metal
kernel void tileLightCull(imageblock<GBuffer> gbuf, … ) { /* compute */ }
```

Encode with `renderEncoder.dispatchThreadsPerTile(_:)` between draw calls.

## Raster Order Groups (601, 607)

The classic order-independent transparency problem: multiple fragments target the same pixel; fragment shader executions reorder for parallelism. Raster order groups force serialization for the SAME pixel within a group:

```metal
[[fragment]] void blend(/* ... */, imageblock<TransparentBuffer, ...> ib,
                        ushort2 tid [[thread_position_in_quadgroup]]) {
    [[raster_order_group(0)]] auto& slot = ib.read(tid);
    // exclusive access to `slot` for this fragment, ordered by primitive submission
    slot.color = blend(slot.color, fragment.color);
}
```

- **HIDDEN GEM**: this is the on-iOS equivalent of Direct3D's Rasterizer-Ordered Views. It enables correct order-independent transparency on mobile for the first time.

## Imageblock Sample Coverage Control (607)

For MSAA, decide programmatically which sample slots within a pixel to write — useful for techniques like adaptive sample shading where edge pixels get more samples than interior pixels.

## VR with Metal 2 (603)

macOS High Sierra adds full VR rendering pipeline support — HTC Vive and Oculus Rift SDK integration via the new `MTKView` external display path. Apple's Pro reference workstations (the new iMac Pro) and external GPU enclosures are positioned as creative-pro VR development platforms.

- Stereo render-target arrays cut per-eye render cost via instanced draw calls.
- 90 Hz frame rate target — Metal 2 frame capture has a "VR" filter to highlight per-frame consistency.

## Metal 2 Compute (608)

`MTLComputePipelineState` gains:

- Indirect dispatch (`dispatchThreadgroups(indirectBuffer:indirectBufferOffset:threadsPerThreadgroup:)`) — GPU-driven compute.
- Heap-based resources for multi-pass compute pipelines (textures and buffers reused without reallocation).
- Shared events for CPU/GPU + GPU/GPU sync without command buffer fences.

## MPS for ML (608)

Metal Performance Shaders Neural Network kernels (`MPSCNN*`) provide GPU-accelerated convolution, pooling, fully-connected, normalization, and activation layers. **This is the engine under Core ML's GPU code path.** If Core ML's high-level API doesn't suit a custom architecture, drop down to MPSCNN to compose layers directly.

```swift
let conv = MPSCNNConvolution(device: device, weights: dataSource)
conv.encode(commandBuffer: cb, sourceImage: input, destinationImage: output)
```

- **PERFORMANCE**: MPSCNN on A11 hits real-time inference rates for ResNet-50 (~10 ms/frame) at 640×480 input.

## SpriteKit + ARKit (609)

`ARSKView` projects 3D anchor positions to 2D screen and renders sprites as billboards. The `SKView` integration means existing SpriteKit content (physics, particles, scenes) drops onto AR scenes for free — placing animated 2D characters in the camera feed is a few lines.

**HIDDEN GEM**: `SKVideoNode` works inside `ARSKView` — pin a video to a wall by attaching to a horizontal-plane anchor (you'll need to rotate it 90°).

## Model I/O — USDZ Hint (610)

Model I/O is the cross-engine asset loader (Metal/SceneKit/SpriteKit/ARKit). 2017 enhancements:

- USD/USDC (Pixar's Universal Scene Description) is supported — sets the stage for USDZ to ship in iOS 12.
- Vertex descriptors auto-derive from imported geometry; you can plug into Metal's vertex stage with no manual layout work.
- PBR materials (base color, metallic, roughness, normal, AO) auto-translate from glTF/OBJ/USD and bind to the appropriate texture/sampler slots.

## SceneKit: What's New (604, 605)

- New PBR shading model and physically-based animations.
- Camera grain matching for AR scenes.
- SceneKit-in-Swift-Playgrounds (605) — interactive 3D in iPad coding lessons.
- New `SCNCameraController` for input-handling boilerplate elimination.

## Best Practices Summary (601, 607)

- **PERFORMANCE**: use the new Metal Frame Capture in Xcode 9 — it visualizes argument buffers, GPU performance counters, shader compiler diagnostics, and per-encoder bandwidth. Worth running on every commit.
- **PERFORMANCE**: `MTLDevice.recommendedMaxWorkingSetSize` on macOS reports the largest amount of resident GPU memory you should allocate. Exceed it and the system pages — drop frame rate immediately.
- **DEPRECATION**: OpenGL ES is officially **deprecated** on iOS in iOS 12 (announced as legacy in 2017). Migrate now; OpenGL is in maintenance mode.

## Cross-references

- See `arkit-debut.md` — Metal template renderer for ARKit.
- See `coreml-vision-nlp.md` — MPSCNN powers Core ML's GPU path.
- See `heif-hevc-photos.md` — HEVC encode/decode on A11 hardware.
