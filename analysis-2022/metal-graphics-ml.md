# Metal 3, Graphics & Machine Learning (2022)

WWDC22 introduced Metal 3 — Apple's biggest graphics-API leap since the original Metal in 2014. The headline features (fast resource loading, MetalFX upscaling, mesh shaders, ray tracing performance, ML acceleration) target AAA games coming to Apple silicon, but the supporting ML and PyTorch story is even more important for non-game developers.

## Sessions covered
- WWDC22-10066 — Discover Metal 3
- WWDC22-10101 — Go bindless with Metal 3
- WWDC22-10102 — Target and optimize GPU binaries with Metal 3
- WWDC22-10103 — Boost performance with MetalFX Upscaling
- WWDC22-10104 — Load resources faster with Metal 3
- WWDC22-10105 — Maximize your Metal ray tracing performance
- WWDC22-10106 — Profile and optimize your game's memory
- WWDC22-10159 — Scale compute workloads across Apple GPUs
- WWDC22-10160 — Program Metal in C++ with metal-cpp
- WWDC22-10162 — Transform your geometry with Metal mesh shaders
- WWDC22-10063 — Accelerate machine learning with Metal
- WWDC22-10064 — Reach new players with Game Center dashboard
- WWDC22-10065 — Plug-in and play: Add Apple frameworks to your Unity game projects
- WWDC22-10027 — Optimize your Core ML usage
- WWDC22-10017 — Explore the machine learning development experience
- WWDC22-10019 — Get to know Create ML Components
- WWDC22-10020 — Compose advanced models with Create ML Components
- WWDC22-110332 — What's new in Create ML
- WWDC22-10024 — What's new in Vision
- WWDC22-10113 — Explore EDR on iOS
- WWDC22-10114 — Display EDR content with Core Image, Metal, and SwiftUI

## Metal 3 highlights (10066)

### Fast Resource Loading (10104)
Modern games stream textures from storage in many small reads, but the existing storage APIs (URLSession, NSData, etc.) are designed for large bulk reads. **Metal 3's fast resource loading** treats loads as Metal commands — multi-threaded, queueable, asynchronous, loading directly into Metal buffers/textures with no intermediate copy. Sync with Metal's existing fences/events.

This is essential for **sparse-texture streaming**: per-tile loads at 60+ fps. Fewer dropped tiles → less time spent rendering at low quality.

### Offline shader compilation (10102)
Pre-compile pipeline state objects at *project build time* into binary archives. Eliminates runtime shader generation:
- Reduces app load times.
- Eliminates frame stutters when a new pipeline is needed mid-frame (the dreaded "shader compilation hitch").

### MetalFX Upscaling (10103)
Apple's answer to Nvidia DLSS / AMD FSR. Renders the game at lower resolution and upscales to Retina with high quality. Two flavors:
- **Spatial** (single frame, faster).
- **Temporal** (multiple frames, higher quality, includes anti-aliasing).

Drop-in for any Metal-based renderer.

### Mesh shaders (10162)
A new geometry pipeline that replaces the traditional vertex stage with two compute-like stages (Object stage + Mesh stage) running inline in the render pipeline. Enables:
- GPU-driven culling without intermediate device-memory writes.
- Procedural geometry generation.
- LOD selection per object based on screen-space size.

### Ray tracing improvements
- Acceleration structure builds are dramatically faster.
- New Indirect Command Buffer support for ray tracing → push culling onto the GPU.
- Direct primitive data access in intersection/shading.

### Hardware support
Metal 3 requires:
- iPhone/iPad with **A13 Bionic or M1 chip or newer**.
- All Apple silicon Macs.
- Mac systems with **recent AMD/Intel GPUs** (specific list in docs).

Use `device.supportsFamily(.metal3)` to feature-detect.

## ML on the GPU (10063)

### PyTorch on Apple silicon
Apple contributed an MPS backend to PyTorch 1.12. **One-line change:** `model.to('mps')`. Result: up to 20× speedup on M1 Ultra vs CPU, average 8.3× across PyTorch benchmarks.

```python
import torch
device = torch.device('mps' if torch.backends.mps.is_available() else 'cpu')
model = torch.load(...).to(device)
```

The MPS backend is fully open source and merged into the official PyTorch GitHub repo.

### TensorFlow improvements
- New ops on the Metal plug-in: `argMin`, `all`, `pack`, `adaDelta`, etc.
- **Custom ops API** — write your own GPU-accelerated TensorFlow ops via `TensorFlow_MetalStream` protocol.
- **Distributed training across multiple Macs.** Shown training across 4 Mac Studios connected via Thunderbolt with near-linear scaling: 200 → 400 → 800 images/sec for ResNet50.

### MPSGraph improvements
- **Shared events API** — synchronize work across multiple command queues, eliminating data races between compute graphs.
- **New ops**: LSTM/GRU/RNN as single ops (vs hand-built subgraphs), parallel random number generator (Philox, matches TensorFlow seeds), Hamming distance, expand/squeeze/split/stack/coordinate/range.
- Max-pooling now returns indices for backprop reuse — up to 6× faster training.

### Memory advantage on Apple silicon
Unified memory means you can train networks with batch sizes that exceed the GPU memory of a discrete card. Higher-quality gradient updates → better model convergence. Run on a single Mac Studio instead of a cloud cluster.

## Vision framework (10024)

### Text recognition revision 3
Powers Live Text. Now includes **Korean and Japanese** in addition to existing languages (use `supportedRecognitionLanguages` for the current list). New `automaticallyDetectsLanguage` for unknown-language inputs.

### Barcode detection revision 3
Switched from classical algorithms to ML under the hood:
- Multi-code detection in a single pass (faster for multi-code images).
- Better accuracy on linear codes (now returns full bounding boxes, not lines).
- Robust to curved surfaces, reflections.

### Optical flow revision 2
ML-based, replacing classical algorithms. Much better at object boundaries and small/fast motion. **Returns lower-resolution output by default that's bilinearly upsampled** — opt out with `keepNetworkOutput = true` if you have your own upsampler or don't need full resolution.

### Quick Look in the debugger
**Hover over a `VNObservation` in the debugger and click the eye icon to visualize the result on your input image.** Works in Xcode Playgrounds too. Removes the need to write visualization utility code.

**Critical caveat:** the `VNImageRequestHandler` must still be in scope; the image lives in the handler. If the handler is released, you'll see the overlay but not the source image.

### Spring cleaning
Vision removed revision-1 detector implementations to save space, but compatibility is preserved by satisfying revision-1 requests with revision-2 detectors (with revision-1 behaviors maintained, e.g. no upside-down faces). **Always specify revision explicitly** — don't rely on default behaviors.

## EDR on iOS (10113, 10114)
Extended Dynamic Range was Mac-only. Now on iOS 16. Use `view.window.windowScene.screen.currentEDRHeadroom` to query available headroom; render brighter-than-white pixels through Core Image, Metal, or SwiftUI's `Image(...).colorEffect(...)`.

## Core ML optimization (10027)
- **Compute Plan API** — get a profile of which compute units (CPU/GPU/Neural Engine) execute each layer. Diagnose unexpected fallbacks.
- **`MLModelAsset`** — async model loading with priority. Cancel and reload mid-flight.
- **Async model evaluation** — `let prediction = try await model.prediction(from: input)`.
- **Stateful models** — for recurrent/streaming inference.

## Create ML Components (10019, 10020, 110332)
A new low-level API for ML pipelines. Compose feature extractors, transformers, and estimators. Use cases:
- Train pipelines that don't fit Create ML's built-in templates (e.g. custom hand-pose classifier).
- Run feature extraction on-device, train on Mac.

## Best practices
- **BEST PRACTICE**: Always specify Vision revision explicitly. Defaults change over time.
- **BEST PRACTICE**: Pre-compile Metal pipelines offline (Metal 3 binary archives) to eliminate runtime shader generation hitches.
- **BEST PRACTICE**: For PyTorch on Apple silicon, just call `.to('mps')` — no other API changes needed.
- **PERFORMANCE**: MetalFX upscaling lets you render at lower resolution and upscale, doubling or tripling frame rates with minimal quality loss.
- **PERFORMANCE**: Mesh shaders eliminate intermediate device-memory roundtrips for GPU-driven culling and procedural geometry.
- **HIDDEN GEM**: PyTorch on Apple silicon delivers up to 20× speedup vs CPU; the entire MPS backend is open source.
- **HIDDEN GEM**: Vision Quick Look in debugger lets you visualize observations with one click — but the request handler must still be in scope.
- **HIDDEN GEM**: TensorFlow on Apple silicon distributes across multiple Mac Studios via Thunderbolt with near-linear scaling.
- **DEPRECATION**: Vision revision-1 face/landmark detector implementations removed from the OS — code still works (revision-2 satisfies revision-1 requests with revision-1 behaviors).

## Cross-references
- Pairs with Camera & Vision integrations: WWDC22-10025 (DataScannerViewController in VisionKit), WWDC22-10026 (Add Live Text interaction).
- Game Center / Apple Games App: WWDC22-10064.
- USDZ / RoomPlan / ARKit 6: WWDC22-10126, 10127, 10128, 10129, 10131, 10141.
- Performance comparison foundation: WWDC22-110363 (general runtime perf), WWDC22-10082 (hangs).
