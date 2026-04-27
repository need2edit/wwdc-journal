# Metal, Graphics, Games & Media — WWDC 2019 Analysis

**Sessions covered:** 601 (Modern Rendering with Metal), 606 (Delivering Optimized Metal Apps and Games), 608 (Metal Enhancements for A13 Bionic), 611 (Bringing OpenGL Apps to Metal), 613 (Ray Tracing with Metal), 614 (Metal for Machine Learning), 615 (Game Center Player Identifiers), 616 (Supporting New Game Controllers), 510 (What's New in AVAudioEngine), 502 (Introducing Low-Latency HLS), 503 (Delivering Intuitive Media Playback with AVKit), 501 (Reaching the Big Screen with AirPlay 2), 249 (Introducing Multi-Camera Capture for iOS), 225 (Advances in Camera Capture & Photo Segmentation)

## Headline

OpenGL/OpenCL are officially **deprecated**. Metal becomes the only forward-looking GPU API on Apple platforms. Metal gets ray tracing, A13 Bionic optimizations (variable rasterization rate, indirect command buffers), and improved ML acceleration. Xbox One and PS4 controllers are now supported. Multi-camera capture (front+back simultaneously) ships for iOS.

## OpenGL/OpenCL Deprecation (611)

**URGENT** — already announced at WWDC 2018, hammered home this year:
- OpenGL ES on iOS: deprecated since iOS 12.
- OpenGL on macOS: deprecated since macOS Mojave.
- OpenCL on macOS: deprecated since Mojave.
- All still work in Catalina but Apple is clear: no new features, eventual removal.
- Migration path: Metal for graphics, Metal Performance Shaders for compute, MetalKit for utilities.

## Modern Metal (601)

- **Argument Buffers (Tier 2)** — pack thousands of textures and buffers into a single GPU-side struct. Bind once, then index. Replaces the per-draw bind-this-bind-that pattern.
- **Indirect Command Buffers (ICBs)** — generate draw commands ON the GPU. CPU just submits "execute the GPU-generated commands." Massive parallelism for things like terrain LOD or instance grids.
- **Resource heaps** — batch allocate and lifetime-manage buffers/textures.

## A13 Bionic Metal (608)

- **Variable Rasterization Rate** — render at lower resolution in peripheral regions of foveated VR/AR displays.
- **Sparse textures** — only the mip levels you sample get allocated.
- **HDR rendering pipeline** — full P3 wide gamut, EDR display support.
- **Persistent memoryless attachments** — render-target memory that never round-trips to system memory. Major bandwidth savings.
- **Tile-based shader features** — programmable blend, lossy compression hints.

## Ray Tracing with Metal (613)

- New `MPSRayIntersector` and Metal Performance Shaders ray tracing primitives.
- Build acceleration structures, trace rays, get hit info.
- Hardware-accelerated only on later GPUs (Apple Silicon, AMD Navi+). Software fallback elsewhere.
- **HIDDEN GEM**: Metal's ray tracing API was designed to be portable to mobile when hardware caught up — the same code runs on M1/M2 GPUs years later.

## Metal Performance Shaders (614)

- New CNN layers: GroupNormalization, RNN, GRU, LSTM.
- Improved fp16 throughput.
- Pre-built `MPSGraph` foundation that becomes more prominent in 2020+.

## Multi-Camera Capture (249)

- iOS 13 / iPhone XS+/XR allows simultaneous capture from front + back cameras (or two back cameras).
- New `AVCaptureMultiCamSession`. Use cases: picture-in-picture video calls, dual-perspective videos, simultaneous selfie + scene capture.
- Power-hungry; lower frame rates than single-cam.
- **URGENT**: iPhone X and earlier (A11) do NOT support multi-cam.

## Camera Capture Refinements (225)

- **Semantic segmentation mattes** for hair, skin, teeth (in addition to person matte).
- Captured into HEIF photos as auxiliary images.
- Use `AVCapturePhotoOutput.enabledSemanticSegmentationMatteTypes` to enable.
- Useful for advanced compositing in your camera/photo apps.

## Game Controllers (616)

- **Xbox One Wireless and PlayStation 4 DualShock controllers** now natively supported via Bluetooth on iOS, iPadOS, macOS, tvOS.
- Use the existing `GCController` framework — no app changes needed for basic mapping.
- New: `GCExtendedGamepad` exposes triggers, thumbsticks with deadzones, and touchpad on DualShock.

## Game Center 2.0 (615)

- New `GKLocalPlayer.gamePlayerID` and `teamPlayerID` — stable identifiers scoped to your app/team. Replaces the deprecated `playerID`.
- Older `playerID` values must be migrated using the new `fetchItems` server-side call.
- **URGENT**: `playerID` deprecation means you have a migration deadline (Apple gave a 2-year grace period at the time).

## AVAudioEngine What's New (510)

- New `AVAudioPlayerNode.scheduleSegment(at:length:)` for sample-accurate timeline scheduling.
- Voice processing tap with echo cancellation built in (`installTap(onBus:bufferSize:format:block:)` with new VP modes).
- AVAudioConverter now supports more sample rate / format conversions.

## Low-Latency HLS (502)

- New CMAF chunked-encoded HLS reduces latency from 30s to ~3s.
- Maintains DRM, ABR, and live-stream-rewind compatibility.
- Apple Music and Apple TV+ both use this protocol.

## AirPlay 2 (501)

- Multi-room, multi-device audio sync.
- Use `MPVolumeView` (deprecated way) or `AVRoutePickerView` (preferred) to surface AirPlay routes.
- Stereo-pair HomePods, TVs, and AirPlay 2 receivers all addressable.

## Intuitive Media Playback (503)

- **AVPlayerViewController** on iOS gets new chapter navigation, audio/subtitle pickers built in.
- **`AVPictureInPictureController`** extended for arbitrary media (not just AVPlayer).
- Universal "Now Playing" integration via `MPNowPlayingInfoCenter`.

## Cross-references

- ARKit 3 + RealityKit are the highest-level Metal consumers: 603, 604, 605.
- Metal for ML feeds CoreML 3 inference: 614, 704.
- Camera capture connects to Vision: 222, 225, 234.
