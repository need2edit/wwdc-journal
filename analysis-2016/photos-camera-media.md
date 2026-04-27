# Photos, Camera & Media — WWDC 2016 Analysis

**Sessions covered:** 501 (Advances in iOS Photography), 505 (Live Photo Editing and RAW Processing with Core Image), 511 (AVCapturePhotoOutput - Beyond the Basics), 503 (Advances in AVFoundation Playback), 504 (What's New in HTTP Live Streaming), 506 (AVKit on tvOS), 507 (Delivering an Exceptional Audio Experience), 510 (Validating HTTP Live Streams)

## Headline

A massive year for photo/media on iOS:
- **`AVCapturePhotoOutput`** replaces `AVCaptureStillImageOutput` — atomic settings, RAW (DNG) capture, Live Photo capture, embedded preview thumbnails, wide color.
- **Live Photo editing API** — third-party apps can now edit Live Photos with full motion + photo round-tripping.
- **RAW image processing on iOS** via Core Image — 4,500+ lines of CI Kernel code, support for 400+ camera models including iPhone 6s/SE/iPad Pro 9.7 RAW DNG capture.
- **Wide color (Display P3) capture** on iPad Pro 9.7-inch.
- **Apple News format** for publishers (sessions 502, 508).

## AVCapturePhotoOutput — the new world

### Why the new API

The old `AVCaptureStillImageOutput` mixed atomic and non-atomic state across `AVCaptureDevice` (flash) and the output itself (still-image-stabilization, format). Users hit race conditions modifying settings during a capture. The new API:

1. Settings are encapsulated in **`AVCapturePhotoSettings`** (immutable per-capture).
2. Each settings instance has a **unique ID** — you get exactly one set of results per request.
3. **Functional flow**: settings → callbacks (delegate) → results, each callback carrying the resolved settings so you know exactly what you got.

### The five-callback delegate flow

```
willBegin → willCapture → didCapture → didFinishProcessingPhoto → didFinishCapture
```

`willBegin(captureFor: resolvedSettings)` resolves auto-flash / auto-still-image-stabilization to concrete `on/off` immediately — so your UI can react before the capture completes (animate the shutter, show "Flash: On" indicator). The `resolvedSettings` carries a unique ID matching your original request.

`willCapture` fires when the virtual shutter closes — perfect for shutter animation/sound.

`didFinishProcessingPhoto(_:photoSampleBuffer:previewPhotoSampleBuffer:resolvedSettings:bracketSettings:error:)` delivers the JPEG. **HIDDEN GEM:** the second parameter (`previewPhotoSampleBuffer`) is a small uncompressed thumbnail — included if you opted in. Use it to populate your "image well" instantly without decompressing the full JPEG.

```swift
let settings = AVCapturePhotoSettings(format: [
    AVVideoCodecKey: AVVideoCodecJPEG
])
settings.flashMode = .auto
settings.isAutoStillImageStabilizationEnabled = true
settings.isHighResolutionPhotoEnabled = true

// Embedded preview
if let previewFormat = settings.availablePreviewPhotoPixelFormatTypes.first {
    settings.previewPhotoFormat = [
        kCVPixelBufferPixelFormatTypeKey as String: previewFormat,
        kCVPixelBufferWidthKey as String: 160,
        kCVPixelBufferHeightKey as String: 160
    ]
}
photoOutput.capturePhoto(with: settings, delegate: self)
```

## Live Photo capture from your app

```swift
photoOutput.isLivePhotoCaptureSupported          // hardware check
photoOutput.isLivePhotoCaptureEnabled = true     // opt in BEFORE startRunning

settings.livePhotoMovieFileURL = sandboxURL      // where to write the .mov
settings.livePhotoMovieMetadata = [
    AVMetadataItem(...).author = "Brad"
]
```

Required: an audio input (`AVCaptureDeviceInput` for the microphone). Without it, Live Photos record without audio.

Two extra delegate callbacks:
- `didFinishRecordingLivePhotoMovieFor(eventualFileAt:resolvedSettings:)` — fired ~1.5 seconds after capture, when sample collection ends. **Dismiss your "Live" badge here** — the user no longer needs to hold still.
- `didFinishProcessingLivePhotoToMovieFileAt(_:duration:photoDisplayTime:resolvedSettings:error:)` — fired when the .mov is fully written and ready to attach to the photo library entry.

The pair (JPEG + MOV) shares a unique UUID stored in QuickTime metadata (`kQTMetadataIdentifierContentIdentifier`) and the JPEG's Apple Maker Note. Use Photos framework to ingest both as a single Live Photo asset.

**HIDDEN GEM:** `isLivePhotoCaptureSuspended = true/false` lets you bracket-out a noisy interruption (you play a sound effect; you don't want the foghorn ending up in two Live Photo movies). Setting `true` immediately trims any in-flight movie; setting `false` resumes new movies cleanly.

## RAW capture (iPhone 6s / SE / iPad Pro 9.7 — A8 and later)

```swift
let availableRAWFormat = photoOutput.availableRawPhotoPixelFormatTypes.first!
let settings = AVCapturePhotoSettings(rawPixelFormatType: availableRAWFormat)
settings.isAutoStillImageStabilizationEnabled = false  // SIS is multi-image fusion — incompatible with RAW
settings.isHighResolutionPhotoEnabled = false

// RAW + JPEG (the pro mode)
let settings = AVCapturePhotoSettings(
    rawPixelFormatType: availableRAWFormat,
    processedFormat: [AVVideoCodecKey: AVVideoCodecJPEG]
)
```

A separate delegate callback `didFinishProcessingRawPhoto(_:rawSampleBuffer:previewPhotoSampleBuffer:resolvedSettings:bracketSettings:error:)` delivers RAW. The processed (JPEG) format goes to the regular `didFinishProcessingPhoto` callback. RAW + processed brackets work — you get N RAWs and N JPEGs.

Save RAW to **DNG** (Adobe's standard) via:
```swift
let dngData = AVCapturePhotoOutput.dngPhotoDataRepresentation(
    forRawSampleBuffer: rawBuffer,
    previewPhotoSampleBuffer: previewBuffer  // ALWAYS embed a preview thumbnail
)
try dngData.write(to: dngURL)
```

**BEST PRACTICE:** Always pass the preview buffer to `dngPhotoDataRepresentation`. Apps that don't understand DNG can still display the embedded thumbnail; the Photos library pre-renders thumbnails from it instantly.

## RAW editing in Core Image (`CIRAWFilter`)

The same powerful pipeline that ships in macOS Aperture lineage now runs on iOS A8+ devices, supporting up to 120-megapixel files on devices with 2GB+ RAM, 60-megapixel on 1GB devices.

```swift
let filter = CIFilter(imageURL: dngURL)!
let originalImage = filter.outputImage  // CIImage in extended-range Display P3
filter.setValue(0.5, forKey: kCIInputEVKey)            // exposure
filter.setValue(5500, forKey: kCIInputNeutralTemperatureKey) // white balance
filter.setValue(0.7, forKey: kCIInputNoiseReductionAmountKey)
let edited = filter.outputImage
```

Properties exposed: exposure (EV), temperature, tint, scaleFactor, neutralLocation, decoderVersion, draftMode, noise-reduction sub-controls (luma/sharpness/contrast/detail), shadow/highlight controls, and many more.

**HIDDEN GEM:** Set `kCIInputDisableGamutMapKey` to `true` if you want the raw extended-range pixels (for further processing) without gamut clamp.

**HIDDEN GEM:** Insert your own filter into the middle of the RAW pipeline (after demosaic, before tone mapping) via `kCIInputAllowDraftModeKey` and the `kCIInputBaselineExposureKey` adjustment hooks.

## Live Photo editing — third-party API

The Photos framework gains `PHLivePhotoEditingContext`. Use it inside a Photo Editing Extension or a PhotoKit app:

```swift
// Get a Live Photo for editing
let input: PHContentEditingInput = ...  // from PhotoEditingExtension.startContentEditing or PHAsset.requestContentEditingInput

guard input.mediaType == .image,
      input.mediaSubtypes.contains(.photoLive) else { return }

let context = PHLivePhotoEditingContext(livePhotoEditingInput: input)!

// Frame processor — applied to each frame (photo + every video frame)
context.frameProcessor = { (frame, errorPointer) -> CIImage? in
    let img = frame.image
    let cropped = img.cropped(to: CGRect(...))
    return cropped
}

// Preview
context.prepareLivePhotoForPlayback(withTargetSize: livePhotoView.bounds.size,
                                    options: nil) { livePhoto, error in
    DispatchQueue.main.async { livePhotoView.livePhoto = livePhoto }
}

// Save (in finishContentEditing or PHAssetChangeRequest)
let output = PHContentEditingOutput(contentEditingInput: input)
context.saveLivePhoto(to: output, options: nil) { success, error in
    // …
}
```

The `frameProcessor` block receives each frame: photo (`frame.type == .photo`) or video (`frame.type == .video`). You return a modified CIImage. Use `frame.time` for time-driven effects, `frame.renderScale` for resolution-aware effects (parameter pixel sizes scale with this), and `frame.type` to apply photo-only effects (like a watermark) that you don't want on the video.

**URGENT (DOCS MISS THIS):** Add `PHSupportedMediaTypes = ["livePhoto"]` to your Photo Editing Extension's `Info.plist`. Without it you receive only a still image, not a Live Photo.

**BEST PRACTICE:** Always save adjustment data in your `PHContentEditingOutput.adjustmentData` so users can re-edit non-destructively.

## Wide color capture (iPad Pro 9.7)

`AVCaptureSession.automaticallyConfiguresCaptureDeviceForWideColor = true` (default) auto-selects Display P3 when a `AVCapturePhotoOutput` is in the session and the hardware supports it.

Wide color flows through capture → photo output → JPEG (tagged Display P3) → Photos library. Backwards-compatible JPEGs use **Apple Wide Color Sharing Profile** — a content-specific table-based ICC profile so non-color-managed viewers see the sRGB subset rendered correctly while color-managed viewers see full P3.

**URGENT:** Wide color is for **photos only** in iOS 10. Don't force-enable it for video — the playback ecosystem isn't widely color-managed yet, and Display P3 movies render with wrong colors on most platforms. The session warns repeatedly: "Wide color is for photos."

RAW capture is inherently wide color — render with whatever profile you want at edit time.

## Audio sessions and interruptions (BEST PRACTICE)

Modernize audio session category usage:
- `AVAudioSessionCategoryPlayback` for media playback (mixes with non-mixable system audio properly).
- `AVAudioSessionCategoryPlayAndRecord` with `.allowBluetooth` for VoIP/recording with Bluetooth headsets.
- New: **`AVAudioSessionInterruptionOptionShouldResume`** in iOS 10 interruption end notifications — true means user expects you to resume (e.g. after a phone call ends). Honor it. False means user explicitly stopped you (e.g. they answered then declined to resume).
- Use `AVAudioSession.notifyOthersOnDeactivation` to notify other apps when you finish so they can resume.

## HLS improvements (sessions 504, 510)

- **HEVC** support for video tracks (later iOS releases add it; iOS 10 lays the groundwork).
- **`mediastreamvalidator`** at developer.apple.com lints your HLS streams for Apple's specs.
- **AirPlay 2 prep** — multi-room audio coming next year.

## Best practices summary

- Migrate from `AVCaptureStillImageOutput` to `AVCapturePhotoOutput` immediately — the old API is deprecated.
- Always pass `previewPhotoSampleBuffer` when writing DNG — instant thumbnails everywhere.
- For live audio in Live Photo capture, attach the microphone input — it's not on by default.
- Set `PHSupportedMediaTypes = ["livePhoto"]` in any Photo Editing Extension that handles Live Photos.
- Use the new `AVAudioSessionInterruptionOptionShouldResume` to honor user intent on interruption end.
- For wide color rendering of JPEGs, leverage Apple Wide Color Sharing Profile via Core Image's `CGImageDestinationOptimizeForSharing` option.

## Hidden gems summary

- The DNG embedded thumbnail makes your RAW files render thumbnails everywhere instantly.
- `isLivePhotoCaptureSuspended` lets you bracket-out app sounds from the Live Photo movie.
- `previewPhotoSampleBuffer` is uncompressed — use directly in image well, no JPEG decompression needed.
- Live Photo `frameProcessor` distinguishes photo vs video frames — apply photo-only watermarks freely.
- Core Image renders RAW with extended Range Display P3 by default — set the working colorSpace.
- DNGs up to 120 megapixels work on 2GB+ devices.
- `AVAudioSessionInterruptionOptionShouldResume` distinguishes phone-call interruption from user-initiated stop.

## Cross-references

- Wide color end-to-end → analysis-2016/wide-color-display.md
- Photos asset catalog wide-color images → analysis-2016/wide-color-display.md
- Camera privacy + permissions → analysis-2016/privacy-differential.md
