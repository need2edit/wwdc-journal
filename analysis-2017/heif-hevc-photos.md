# HEIF, HEVC & Photos — WWDC 2017 Analysis

**Sessions covered:** 503 (Introducing HEIF and HEVC), 511 (Working with HEIF and HEVC), 513 (High Efficiency Image File Format), 504 (Advances in HTTP Live Streaming), 514 (Error Handling Best Practices for HTTP Live Streaming), 515 (HLS Authoring Update), 505 (What's New in Photos APIs), 507 (Capturing Depth in iPhone Photography), 508 (Image Editing with Depth), 510 (Advances in Core Image), 501 (What's New in Audio), 502 (Introducing MusicKit), 821 (Get Started with Display P3)

## Headline

iOS 11 / High Sierra adopt the **HEVC** (H.265) video codec and **HEIF** (High Efficiency Image File Format) container — Apple's commitment to halve photo and video file sizes at equal or better quality vs JPEG / H.264. New depth-aware photography APIs, native multi-image HEIF (live photos, bursts, depth maps in one file), and HDR video support across HLS round out a media-heavy year.

## HEVC: Why and How (503, 511)

H.264 has hit its compression ceiling. HEVC delivers ~40% smaller files at equal subjective quality, plus support for:

- **4K and larger frame sizes** at reasonable bitrate.
- **10-bit color depth** (HDR-ready).
- **Wider color gamuts** (Rec. 2020).

Apple's HEVC encode/decode is hardware-accelerated on A9 and later for **8-bit Main Profile** decode and on A10 Fusion and later for full 10-bit Main10 decode/encode. macOS High Sierra requires a sixth-generation Intel CPU for hardware decode (Sky Lake+); older Macs fall back to software decode.

### AVFoundation Encoding (511)

```swift
let writer = try AVAssetWriter(outputURL: url, fileType: .mov)
let settings: [String: Any] = [
    AVVideoCodecKey: AVVideoCodecType.hevc,
    AVVideoWidthKey: 1920,
    AVVideoHeightKey: 1080
]
let input = AVAssetWriterInput(mediaType: .video, outputSettings: settings)
```

- **HIDDEN GEM**: query `AVAssetExportSession.allExportPresets()` — the new `AVAssetExportPresetHEVCHighestQuality` and `…3840x2160` presets ship in iOS 11. Old apps using `AVAssetExportPresetHighestQuality` keep generating H.264 for backward compatibility — switch explicitly to opt into HEVC.
- **WARNING**: not every device supports hardware HEVC encode. Check `AVAssetExportSession.exportPresets(compatibleWith:)` for a given source asset before applying a preset; degrade gracefully on older devices.

### HEVC in HLS (504, 514, 515)

- **HLS now requires fragmented MP4 (fMP4) for HEVC streams.** TS segments are H.264-only. Plan tooling: ffmpeg / mediafilesegmenter / Bento4 all updated.
- **DEPRECATION**: `mediastreamvalidator` rejects HLS playlists that don't include both an H.264 fallback and a HEVC primary as of iOS 11. Author both.
- HLS can now signal HDR (HDR10 / Dolby Vision) with new `EXT-X-MEDIA` and `VIDEO-RANGE` attributes.

## HEIF Container (503, 513)

HEIF is a multi-image, metadata-rich container based on the ISO Base Media File Format (same family as MP4):

- **Multi-image**: a single `.heic` can contain a primary image, alternate representations (preview thumbnail), burst sequences, live photos (image + paired video), depth/disparity maps, image sequences (animated HEIF — like animated GIF, but HEVC).
- **Metadata everywhere**: EXIF, XMP, color profiles per item.
- **HEVC compressed inside**: a still HEIC is one HEVC I-frame.
- **PERFORMANCE**: ~50% smaller than equivalent-quality JPEG.

### Reading HEIF (511, 513)

`UIImage(named:)`, `UIImage(contentsOfFile:)`, `Image I/O`'s `CGImageSourceCreateWithURL`, all read HEIF transparently. **No code change required for read**.

For multi-image content, use Image I/O directly:

```swift
let source = CGImageSourceCreateWithURL(url as CFURL, nil)!
let count = CGImageSourceGetCount(source)            // > 1 for live photos / bursts
for i in 0..<count {
    let image = CGImageSourceCreateImageAtIndex(source, i, nil)
}
```

### Writing HEIF (511, 513)

```swift
let dest = CGImageDestinationCreateWithURL(url as CFURL,
                                           AVFileType.heic as CFString, 1, nil)!
CGImageDestinationAddImage(dest, cgImage, [
    kCGImageDestinationLossyCompressionQuality as String: 0.8
] as CFDictionary)
CGImageDestinationFinalize(dest)
```

- **WARNING**: hardware HEIF encode requires A10 Fusion. On A9 devices, Image I/O writes JPEG silently for stills if HEVC encode isn't available. Check `CGImageDestinationCopyTypeIdentifiers()` to confirm `public.heic` is in the list before assuming HEIF will be written.

### Backward Compatibility (511, 513)

- The Photos picker / `PHImageManager` returns JPEG-encoded data by default for compatibility. Pass `PHImageRequestOptions.version = .original` and `deliveryMode = .highQualityFormat` for the original HEIF.
- Sharing through `UIActivityViewController` / Mail / iMessage transcodes to JPEG/H.264 automatically on the way OUT to non-Apple recipients (see Settings → Photos → Transfer to Mac/PC: "Automatic" vs "Keep Originals").
- **HIDDEN GEM**: AirDrop preserves HEIF/HEVC between Apple devices natively — no quality loss in the share chain.

## Capturing Depth (507)

The dual-camera iPhone 7 Plus / 8 Plus and the front-facing TrueDepth camera (iPhone X) now expose **disparity** and **depth** maps as first-class data:

- `AVCapturePhotoOutput.isDepthDataDeliveryEnabled = true` (dual cam) or use `AVCaptureDevice.DeviceType.builtInTrueDepthCamera`.
- The capture delivers an `AVDepthData` along with the `AVCapturePhoto`. The photo embeds the depth map as an auxiliary image in the HEIF.
- `AVDepthData.depthDataMap` is a `CVPixelBuffer` of type `kCVPixelFormatType_DepthFloat32` or `_DisparityFloat32`.

**HIDDEN GEM**: depth/disparity maps are written into the HEIF auxiliary track. They survive AirDrop and iCloud Photo Library — applications can re-edit Portrait mode photos days later because the depth metadata is preserved.

## Editing with Depth (508)

Core Image gains depth-aware filters:

- `CIDepthBlurEffect` — recreates Portrait mode bokeh from any image+depth pair.
- `CIPortraitEffect` (iOS 12 preview).
- `CIImage(depthData:)` — convert the depth map to a CIImage and use as a matte for any other filter.

```swift
let depthImage = CIImage(depthData: depthData)!
let blurredBg = original.applyingFilter("CIGaussianBlur", parameters: [kCIInputRadiusKey: 12])
let composited = original.applyingFilter("CIBlendWithMask", parameters: [
    kCIInputBackgroundImageKey: blurredBg,
    kCIInputMaskImageKey: depthImage
])
```

**HIDDEN GEM**: depth maps from iPhone X TrueDepth camera are dense and accurate enough to drive face-relighting filters — Vision face landmarks + AVDepthData = professional-quality portrait lighting.

## Core Image: Metal, Vision, Custom Filters (510)

- Core Image now compiles filter chains directly to **Metal Performance Shaders**. Massive perf wins on iOS 11.
- `CIFilter` chains feed directly into Vision: `VNImageRequestHandler(ciImage: filteredImage, …)`.
- Write custom CIFilters in Metal: subclass `CIKernel` with a `.metal` source. Eliminates the old Core Image Shading Language.

```metal
extern "C" float4 invertKernel(coreimage::sample_t s) {
    return float4(1.0 - s.rgb, s.a);
}
```

Compile with the new `metal` build phase set to `Core Image` flavor.

## HDR Video (504, 514, 515)

- iOS 11 / Apple TV 4K play **HDR10** and **Dolby Vision** content via AVPlayer.
- Capture HDR10 video on iPhone 12+ (later WWDCs) — for 2017, the focus is playback infrastructure.
- HLS gains HDR signaling via `VIDEO-RANGE=PQ` (HDR10) or `=HLG` and `EXT-X-VERSION=8` requirement.
- Authoring tools: `mediastreamsegmenter` and `mediafilesegmenter` updated for HEVC + HDR. `mediastreamvalidator` enforces playlist correctness.

## Audio & Music (501, 502)

- **MusicKit** (502) opens the Apple Music catalog to third-party apps for the first time. Users sign in with their Apple Music subscription; your app gets full streaming access via `MPMusicPlayerController.applicationQueuePlayer`.
- Audio (501) refresh: `AVAudioEngine` gains AirPlay 2 routing, `AUv3` plug-ins for Logic / GarageBand, and `MPRemoteCommandCenter` integration.
- **HIDDEN GEM**: MusicKit JS lets web apps stream Apple Music in Safari with the same auth model — embed an Apple Music player in your marketing site or web app.

## Photos APIs Refresh (505)

- **`PHLivePhoto`** can now be created programmatically from a still + video pair — share custom Live Photos.
- `PHContentEditingInput.adjustmentData` rounds out the cross-process editing protocol so third-party photo editors interoperate with Photos.app revert.
- **HIDDEN GEM**: `PHPhotoLibrary.performChanges(_:completionHandler:)` is now thread-safe; you can fire many requests in parallel from any queue. Earlier versions required serialization.

## Cross-references

- See `arkit-debut.md` — TrueDepth front camera also powers ARKit face tracking.
- See `metal2-graphics-pipeline.md` — Metal 2 + MPS underpin Core Image acceleration.
- See `coreml-vision-nlp.md` — Vision face landmarks + AVDepthData enable studio-grade portrait effects.
