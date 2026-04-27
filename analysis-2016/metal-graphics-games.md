# Metal, Graphics & Games — WWDC 2016 Analysis

**Sessions covered:** 602 (Adopting Metal Part 1), 603 (Adopting Metal Part 2), 604 (What's New in Metal Part 1), 605 (What's New in Metal Part 2), 606 (Advanced Metal Shader Optimization), 608 (What's New in GameplayKit), 609 (Advances in SceneKit Rendering), 610 (What's New in SpriteKit), 611 (What's New in Game Center), 612 (Game Technologies for Apple Watch), 715 (Neural Networks and Accelerate)

## Headline

Metal gets a major upgrade with **tessellation**, **resource heaps and texture argument buffers (preview)**, **wide-color textures**, **function specialization**, and **Metal Performance Shaders** (MPS) image processing primitives. **Metal CNN** debuts inside MPS — Apple ships convolutional neural network primitives for inference on the GPU. SceneKit gains a new physically-based rendering pipeline; SpriteKit is now on Apple Watch.

## Metal Performance Shaders (MPS) — Image processing + neural nets

MPS is Apple's library of GPU-optimized building blocks. Image filters (`MPSImageGaussianBlur`, `MPSImageBox`, `MPSImageHistogram`, `MPSImageIntegral`, etc.) replace hand-written shaders for common operations.

NEW in 2016: **Convolutional Neural Network primitives** (`MPSCNNConvolution`, `MPSCNNFullyConnected`, `MPSCNNPoolingMax`, `MPSCNNPoolingAverage`, `MPSCNNNeuronReLU`, `MPSCNNSoftMax`, more). Run pre-trained CNN models for inference on the GPU. Apple's example: image classification at 60fps on iPhone 6s.

```swift
let device = MTLCreateSystemDefaultDevice()!
let commandQueue = device.makeCommandQueue()!

// Define convolutional layer
let convDescriptor = MPSCNNConvolutionDescriptor(kernelWidth: 3, kernelHeight: 3,
                                                  inputFeatureChannels: 64, outputFeatureChannels: 128)
let conv = MPSCNNConvolution(device: device, convolutionDescriptor: convDescriptor,
                              kernelWeights: weights, biasTerms: biases, flags: .none)

// Run inference
let commandBuffer = commandQueue.makeCommandBuffer()!
conv.encode(commandBuffer: commandBuffer, sourceImage: inputImage, destinationImage: outputImage)
commandBuffer.commit()
```

This is **the precursor to Core ML** — Apple shipping the bricks that get bundled into the Core ML facade in iOS 11.

## Metal core engine improvements

### Tessellation (NEW)

Hardware-accelerated dynamic geometry detail. The GPU subdivides primitives at runtime — terrain LOD, character muscle deformation, displacement mapping all become practical. iOS-class GPUs gain feature parity with desktop here.

### Function specialization

Compile a generic shader, specialize at runtime with constants:

```swift
let constants = MTLFunctionConstantValues()
constants.setConstantValue(&useHDR, type: .bool, withName: "useHDR")
let specializedFunction = try library.makeFunction(name: "myShader", constantValues: constants)
```

Replaces shader permutation explosion (compile 64 variants of a shader). One source, many specializations.

### Wide color textures

`MTLPixelFormat.bgr10a2Unorm`, `bgra8Unorm_srgb`, plus extended-range half-float formats let games render to Display P3 textures directly. Critical for the new iPad Pro 9.7 wide-color path.

### Resource heaps + textures argument buffers (preview)

Massive memory-management upgrade — bind hundreds of textures with a single argument buffer, share heap memory across resources, drop bind-call overhead by orders of magnitude. (Goes mainstream in Metal 2 / iOS 11.)

### Tile shaders & threadgroup memory

Compute shaders gain shared threadgroup memory for inter-thread cooperation; tile shaders run on tile-render hardware (A-series GPUs are tile-based deferred renderers). Big perf wins for image filters that previously required multi-pass.

## SceneKit (session 609)

- **Physically-based rendering** — `SCNMaterial.lightingModel = .physicallyBased`. Materials are described by metalness, roughness, normal, emission. Energy-conserving lighting model matches modern game engines (Unreal/Unity).
- **HDR rendering pipeline** — render in floating-point precision; tonemap at the end. `SCNCamera.wantsHDR = true`.
- **Cascaded shadow maps**, **screen-space ambient occlusion**, **bloom** all built in.
- **Tessellation** for dynamic terrain.
- **Animation events** for synchronized audio/visual triggers.

## SpriteKit (session 610)

- **GameplayKit integration** — pathfinding, state machines, AI behavior trees.
- **Tile maps** with `SKTileMapNode` — finally first-class tile-based games.
- **Camera nodes** — `SKCameraNode` simplifies side-scrolling camera management.
- **Shader uniforms** — pass dynamic values into fragment shaders via `SKAttributeValue`.
- **Now on Apple Watch** (watchOS 3) — short interaction games, complications backgrounds, animated elements in long-look notifications.

## GameplayKit (session 608)

- **Procedural noise generation** — Perlin, Voronoi, billow, ridged-multi for terrain/cloud generation.
- **Decision trees** for AI behavior with weighted edges.
- **Path generation** improvements — obstacle avoidance, GKMeshGraph for polygon-based pathfinding.

## Game Center & Game Controllers

- **Player identifiers** are now per-game, opaque tokens (privacy improvement). Old `playerID` is deprecated; use `gamePlayerID` and `teamPlayerID`.
- **GKLocalPlayer.fetchItems** for sharing achievements/leaderboard scores via UIActivityViewController.
- **Turn-based game controllers** on Apple Watch — start/play/end turns from the wrist.

## Apple Watch games (session 612)

watchOS 3 enables real game development on the watch:
- SpriteKit + SceneKit available.
- AVFoundation for audio playback.
- GameKit for turn-based games.
- Crown raw events + gesture recognizers + gyroscope for input.
- Inline video playback (auto-play in dock).

Apple's example: **Fish Time by WoGa** — fishing game using crown depth control, swipe-to-cast, tap-to-bite. The watch is now a viable platform for short-interaction games.

## Neural Networks and Accelerate (session 715)

For developers without Metal expertise, Accelerate's `vImage`, `vDSP`, and the new **`BNNS` (Basic Neural Network Subroutines)** library provide CPU-side neural network primitives. Cross-architecture (iPhone, iPad, Mac, Apple Watch) — especially valuable for the watch where Metal isn't an option. Same conceptual layers (convolution, pooling, fully-connected, ReLU, soft-max).

Combine with MPS CNN: Train on Mac in TensorFlow/Caffe, deploy on iOS using BNNS for CPU or MPS CNN for GPU. (Core ML in iOS 11 unifies this.)

## Best practices summary

- Use MPS for image filters — hand-written shaders rarely beat them.
- Use MPSCNN for inference of pre-trained models on iOS — ~60fps on iPhone 6s.
- Adopt function specialization for shader variants instead of permutation source.
- Use SCNMaterial physically-based lighting for modern game/visualization look.
- For Apple Watch games, target short interactions — 30 seconds of gameplay max.
- Use BNNS for CPU-only neural nets (especially on watchOS).

## Hidden gems summary

- MPSCNN at 60fps on iPhone 6s makes real-time image classification practical.
- Tessellation closes the iOS-vs-desktop GPU feature gap for dynamic geometry.
- Function specialization eliminates shader permutation explosion.
- SpriteKit on Apple Watch enables a new short-game category.
- BNNS gives watchOS apps neural-network inference without GPU.

## Cross-references

- Wide color textures → analysis-2016/wide-color-display.md
- watchOS 3 inline video + games → analysis-2016/watchos3-redesign.md
- Camera + image processing → analysis-2016/photos-camera-media.md
