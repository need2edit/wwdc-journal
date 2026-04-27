# Audio, Video & Media (WWDC 2021)

26 sessions in 2021's Audio & Video topic — the largest category. Covers Spatial Audio, ShazamKit, HLS Content Steering, low-latency video encoding, EDR/HDR rendering, Apple Music API, MusicKit for Swift.

## Sessions covered
- WWDC21-10146 — What's new in AVFoundation
- WWDC21-10265 — Immerse your app in Spatial Audio
- WWDC21-10044, 10045 — ShazamKit
- WWDC21-10079 — Discover geometry-aware audio with PHASE
- WWDC21-10036 — Discover built-in sound classification in SoundAnalysis
- WWDC21-10101 — Discover rolling clips with ReplayKit
- WWDC21-10140 — HLS dynamic pre-rolls and mid-rolls
- WWDC21-10141 — HLS Content Steering
- WWDC21-10142 — Transition media gaplessly with HLS
- WWDC21-10143 — Explore HLS variants in AVFoundation
- WWDC21-10145 — Advanced Video Quality Tool
- WWDC21-10158 — Low-latency video encoding with VideoToolbox
- WWDC21-10159 — Core Image kernel improvements
- WWDC21-10161 — HDR rendering with EDR
- WWDC21-10190 — Audio drivers with DriverKit
- WWDC21-10191 — Deliver a great playback experience on tvOS
- WWDC21-10278 — Practice audio haptic design
- WWDC21-10290 — What's new in AVKit
- WWDC21-10291, 10293, 10294 — Apple Music API & MusicKit for Swift

## Best practices

- **Migrate to async `AVAsset.load(.duration, .tracks, …)`** — the old `loadValuesAsynchronously(forKeys:)` API is deprecation-bound in Swift. Multi-property loading is batched and faster than serial property reads (WWDC21-10146).
- **Use Spatial Audio for any 3D-positioned sound**: set `AudioBufferResource.inputMode = .spatial` in RealityKit, or use `AVAudioPlayer` with HRTF positioning. Falls back gracefully on speakers without head-tracking (WWDC21-10265).
- **For HLS**: Adopt **Content Steering** to switch between CDNs based on availability/cost. The manifest stays simple; the steering server returns ordered CDN preferences (WWDC21-10141).
- **For HLS dynamic ads**: use HLS Interstitials (`#EXT-X-DATERANGE` with `X-ASSET-URI`) instead of stitching MP4 ads into the main playlist. AVKit handles ad rendering, scrubbing, and DRM separation (WWDC21-10140).

## Hidden gems

- **EDR (Extended Dynamic Range)** is always-on whenever video HDR is supported. The naming is confusing: `videoHDREnabled` actually controls EDR. **10-bit HDR video** is the genuinely-new full HDR thing in iOS 15 / iPhone 12+ (WWDC21-10047).
- **AVFoundation auto-inserts per-frame Dolby Vision metadata** when capturing 10-bit HDR — your `.mov` plays correctly on Dolby Vision TVs without any additional work (WWDC21-10047).
- **PHASE** (Physical Audio Spatialization Engine) — RealityKit-shaped audio engine that simulates room acoustics, geometry occlusion, and material absorption. Works alongside ARKit room mesh (WWDC21-10079).
- **`SNClassifySoundRequest`** ships with a built-in classifier covering ~300 everyday sounds (alarms, animals, instruments). No model file required — it's in the OS (WWDC21-10036).
- **ReplayKit rolling clips**: `RPScreenRecorder.startClipBuffering()` — the system continuously records a 15-second rolling buffer; call `exportClip(to:duration:)` retroactively to save the last N seconds when something cool happens (WWDC21-10101).
- `AVPlayer` low-latency video encode in VideoToolbox: `kVTCompressionPropertyKey_PrioritizeEncodingSpeedOverQuality` plus `kVTVideoEncoderSpecification_RequireHardwareAcceleratedVideoEncoder=true` (WWDC21-10158).
- **EDR rendering** for HDR images in your own Metal layer: `CAMetalLayer.wantsExtendedDynamicRangeContent=true` plus an HDR-capable color space — your render targets can exceed 1.0 white-point luminance (WWDC21-10161).
- AVKit on tvOS gets a redesigned playback UI with **interstitial ad markers** and per-section navigation (WWDC21-10191).
- **MusicKit for Swift** brings the full Apple Music catalog query API (formerly REST-only) into native Swift — `MusicCatalogResourceRequest`, `MusicSubscription` for entitlement checks (WWDC21-10294).

## Performance

- HLS Content Steering reduces failed playback by ~10x in regions with multi-CDN setups (Apple internal data, WWDC21-10141).
- Low-latency video encoding at 1080p60 hits sub-50ms encode latency on Apple Silicon (WWDC21-10158).

## Migration guidance

- For caption authoring on macOS: new `AVCaption`, `AVAssetWriterInputCaptionAdaptor`, `AVCaptionConversionValidator` produce iTunes Timed Text (.itt) and Scenarist Closed Captions (.scc). Replaces hand-rolled subtitle authoring (WWDC21-10146).
- AVAudioEngine for spatial audio routes through the new spatializer node — you can pre-render spatial mixes for offline export (WWDC21-10265).

## Cross-references

- Group Activities + AVPlayer = sub-second time-synced playback across continents (WWDC21-10183, WWDC21-10225).
- Cinematic mode is a 2022 feature; 2021's "Use video formats for high-quality photos" (WWDC21-10247) hints at the underlying capture pipeline.
