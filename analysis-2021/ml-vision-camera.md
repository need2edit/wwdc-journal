# ML, Vision, Camera, and Live Text (WWDC 2021)

Live Text (visual intelligence on-device), VisionKit document detection, Core ML 5's ML Programs, and a modernized AVFoundation camera stack with Center Stage and Portrait video.

## Sessions covered
- WWDC21-10038 — Tune your Core ML models
- WWDC21-10037 — Build dynamic iOS apps with the Create ML framework
- WWDC21-10039 — Classify hand poses and actions with Create ML
- WWDC21-10040 — Detect people, faces, and poses using Vision
- WWDC21-10041 — Extract document data using Vision
- WWDC21-10044 — Explore ShazamKit
- WWDC21-10045 — Create custom audio experiences with ShazamKit
- WWDC21-10046 — Improve access to Photos in your app
- WWDC21-10047 — What's new in camera capture
- WWDC21-10160 — Capture and process ProRAW images
- WWDC21-10247 — Capture high-quality photos using video formats
- WWDC21-10276 — Use the camera for keyboard input in your app

## Best practices

- **Use `MLShapedArray<T>` over `MLMultiArray`** in new Swift code. Strongly typed, value semantics, copy-on-write, slicing via Swift `Range`. Xcode auto-generates the shaped-array property next to the legacy MLMultiArray (WWDC21-10038).
- **Convert to ML Programs (`.mlpackage`) for new models** targeting iOS 15+. Strongly typed intermediate tensors, ANE-friendly layout decisions made at compile time (WWDC21-10038).
- **Don't run barcode detection with empty `symbologies`** unless you really need to scan everything. Each enabled symbology adds CPU cost (WWDC21-10041).
- **VNDocumentSegmentationRequest** beats `VNDetectRectanglesRequest` on devices with a Neural Engine — ML-based, robust to folded paper, occluded corners. Falls back to CPU-based rectangle detection on older devices (WWDC21-10041).
- **VNDocumentCameraViewController** in VisionKit transparently uses the new ML segmentation request on Neural-Engine devices — adopt VisionKit and you get it for free (WWDC21-10041).
- **Pass languages in priority order** for `VNRecognizeTextRequest`. The first language picks the recognition model (Latin vs Chinese); subsequent languages affect ambiguity resolution (WWDC21-10041).

## Hidden gems

- ML Packages separate weights from architecture from metadata — so a 1-byte metadata edit no longer creates a 60MB binary diff in git (WWDC21-10038).
- The Photos framework now has a **PHPicker that returns no permission prompt** — the picker runs in a separate process and only the chosen items reach your app (WWDC21-10046). Almost no app needs full Photos library access anymore.
- `PHPickerConfiguration.selectionLimit = 0` means unlimited selection; previously this needed a non-default value (WWDC21-10046).
- **Live Text** lands as `VNRecognizeTextRequest` improvements + `UIKit/AppKit text input client integration` — any standard text view automatically supports Live Text image-paste in iOS 15.1+ on supported hardware. (WWDC21-10041, related WWDC21-10276 for camera-as-keyboard).
- Vision's `VNDetectHumanBodyPoseRequest` extends to **hand poses** (`VNDetectHumanHandPoseRequest`) — combine with Create ML's hand action classifier to recognize gestures (WWDC21-10040, WWDC21-10039).
- **Center Stage** API: `AVCaptureDevice.centerStageEnabled` (read/write), `centerStageControlMode` (`.user`/`.app`/`.cooperative`). Available on M1 iPad Pro front cameras (WWDC21-10047).
- **Portrait Video** (depth-of-field background blur) needs `NSCameraPortraitEffectEnabled=true` in Info.plist for non-VoIP apps. VoIP apps are auto-opted-in (WWDC21-10047).
- 10-bit HDR video formats use the pixel format `420YpCbCr10BiPlanarVideoRange` (a.k.a. `x420`). EDR is always-on for these. Auto-Dolby-Vision metadata is inserted per-frame (WWDC21-10047).
- Minimum focus distance is now exposed: `AVCaptureDevice.minimumFocusDistance` (mm). Use it in scanning UIs to auto-zoom when a small target is requested (WWDC21-10047).
- `AVAsset` properties are now loaded via async `load(_:)` — `let dur = try await asset.load(.duration)`. The old `loadValuesAsynchronously(forKeys:)` callback API is being deprecated for Swift (WWDC21-10146).

## Performance

- ShazamKit recognizes audio in **<1 second** on-device against the full Shazam catalog (300M+ tracks). Custom catalogs let you match against your own audio (sound effects, lectures) without the network (WWDC21-10044, WWDC21-10045).
- ProRAW capture: `AVCapturePhotoOutput` returns a 12-bit DNG with full HDR pipeline — Photos app and apps that load DNG can display the smart-HDR-fused result while preserving raw editability (WWDC21-10160).

## Migration guidance

- If your camera app reaches into private headers for video format selection, the `AVCaptureDevice.formats` array now exposes everything needed — search for the pixel format type to find HDR variants programmatically (WWDC21-10047).
- Move from `loadValuesAsynchronously(forKeys:)` to `try await asset.load(.duration, .tracks)` — multi-property loading is batched (WWDC21-10146).

## Cross-references

- Sound Analysis adds `SNClassifySoundRequest` for real-time built-in sound classification (300+ classes) (WWDC21-10036).
- ReplayKit now supports rolling 15-second clips that are saved retroactively (WWDC21-10101) — combined with game controller share button media-capture (WWDC21-10081).
