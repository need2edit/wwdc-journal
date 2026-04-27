# Media, Camera, AR/USD & ScreenCaptureKit (2022)

WWDC22's media story includes the introduction of ScreenCaptureKit (high-performance screen recording), Continuity Camera (use iPhone as Mac webcam), VisionKit's DataScannerViewController (live text/barcode UI), ShazamKit catalogs, EDR on iOS, and ARKit 6 with 4K capture and the new RoomPlan API.

## Sessions covered
- WWDC22-10025 — Capture machine-readable codes and text with VisionKit
- WWDC22-10026 — Add Live Text interaction to your app
- WWDC22-10018 — Bring Continuity Camera to your macOS app
- WWDC22-10022 — Create camera extensions with Core Media IO
- WWDC22-110429 — Discover advancements in iOS camera capture
- WWDC22-10023 — What's new in the Photos picker
- WWDC22-10089 — What's new in PDFKit
- WWDC22-110338 — Explore media metadata publishing and playback interactions
- WWDC22-110373 — Bring your driver to iPad with DriverKit
- WWDC22-110379 — Create a more responsive media app
- WWDC22-110565 — Display HDR video in EDR with AVFoundation and Metal
- WWDC22-10147 — Create a great video playback experience
- WWDC22-10144 — Deliver reliable streams with HLS Content Steering
- WWDC22-10145 — What's new in HLS Interstitials
- WWDC22-10148 — Meet Apple Music API and MusicKit
- WWDC22-10149 — What's new in AVQT
- WWDC22-10155 — Take ScreenCaptureKit to the next level
- WWDC22-10156 — Meet ScreenCaptureKit
- WWDC22-10028 — Create custom catalogs at scale with ShazamKit
- WWDC22-10126 — Discover ARKit 6
- WWDC22-10127 — Create parametric 3D room scans with RoomPlan
- WWDC22-10128 — Bring your world into augmented reality
- WWDC22-10129 — Understand USD fundamentals
- WWDC22-10131 — Qualities of great AR experiences
- WWDC22-10141 — Explore USD tools and rendering

## VisionKit DataScannerViewController (10025)

A drop-in `UIViewController` subclass that handles the entire camera+detection pipeline for text and barcodes. Replaces hand-rolled AVFoundation+Vision setups.

### Built-in features
- Live camera preview.
- Item highlighting (default or custom views).
- Tap-to-focus / tap-to-select.
- Pinch-to-zoom.
- Guidance labels.
- Coordinates returned in **view coordinates** (no AVCapture-to-Vision conversion math needed).

### Setup
```swift
let scanner = DataScannerViewController(
    recognizedDataTypes: [.barcode(symbologies: [.qr]), .text(textContentType: .url)],
    qualityLevel: .balanced,
    recognizesMultipleItems: true,
    isHighFrameRateTrackingEnabled: true,
    isPinchToZoomEnabled: true,
    isGuidanceEnabled: true,
    isHighlightingEnabled: true
)
```

### Privacy + availability
- Add a privacy-camera-usage-description to Info.plist.
- Use `DataScannerViewController.isSupported` to hide entry points on unsupported devices (anything pre-2018 iPhone/iPad without Apple Neural Engine).
- Use `DataScannerViewController.isAvailable` to handle camera-restricted devices (Screen Time content & privacy restrictions).

### Text content types
Limit recognition to specific semantic types:
- URL, email, phone number, address, currency, flight number, shipment tracking number.

### Languages
iOS 16 adds **Korean and Japanese**. Use `DataScannerViewController.supportedTextRecognitionLanguages` for the current list.

### Recognition lifecycle
Three delegate methods:
- `didAdd(_:allItems:)` — newly recognized items. Add custom highlight views here.
- `didUpdate(_:allItems:)` — items moved or transcription improved. Update view positions.
- `didRemove(_:allItems:)` — items left the scene. Remove custom highlights.

`recognizedItems` is also an `AsyncStream` if you don't want to draw custom highlights.

### Custom highlights
Add to `dataScanner.overlayContainerView` so they appear above camera preview but below system chrome.

## Add Live Text interaction (10026)

For static images (not live camera), use `ImageAnalysisInteraction` (UIKit) or `ImageAnalysisOverlayView` (AppKit). Wraps an image view to add Live Text — selectable text, data detectors, QuickActions like "Translate" or "Look up."

```swift
let analyzer = ImageAnalyzer()
let interaction = ImageAnalysisInteraction()
imageView.addInteraction(interaction)

let analysis = try await analyzer.analyze(image, configuration: .init([.text, .machineReadableCode]))
interaction.analysis = analysis
interaction.preferredInteractionTypes = .automatic
```

## Continuity Camera on macOS (10018)
- Use iPhone as the Mac's webcam.
- Center Stage and Studio Light effects work automatically.
- Desk View — overhead view of the desk surface using ultrawide camera.
- Three new AVFoundation device types for picking these inputs in your Mac app.

## Camera capture advancements (110429)
- **Multi-cam recording** improvements on iPad.
- **Depth in HEIF still capture.**
- **PhotoKit `.depth` data type.**
- Better focus and multitasking handling.

## Photos picker (10023)
The privacy-respecting picker. New in iOS 16:
- **Multi-platform** — iOS, macOS, watchOS.
- **Better filtering** by media type, asset type.
- Built into SwiftUI as `PhotosPicker` view.
- Uses `Transferable` for data delivery.

## ScreenCaptureKit (10155, 10156)

A high-performance screen-recording API for macOS that replaces older mechanisms like CGWindowList capture.

### What it does
- Per-window or per-display capture.
- Audio capture, including system audio.
- Hardware-accelerated frame delivery via `IOSurface`.
- Filtering by application or window.
- Cursor capture, microphone audio, system audio.

### Why it matters
- **Lower CPU and energy** than legacy APIs.
- **Privacy-respecting** — system prompt before capture starts.
- Used by Final Cut, OBS Studio, etc.

## ARKit 6 (10126)
- **4K video capture** at 30 fps during ARKit sessions.
- High-resolution background images on demand.
- HDR video for AR scenes.
- Plane classification improvements.
- Motion capture body skeleton at 60 fps.

## RoomPlan (10127)
A new framework that uses LiDAR and camera to scan rooms and generate parametric USD models with walls, doors, windows, and furniture as labeled, semantic objects (not just geometry). Output works directly in CAD/design tools that support USD.

## USD (10129, 10141)
USD is now Apple's first-class 3D file format. Sessions cover:
- Layer-based composition for collaborative editing.
- USDZ for delivery (zip-archived USD with textures).
- Apple's `usdpython` tools for converting from FBX, OBJ, glTF.

## Best practices
- **BEST PRACTICE**: Always check `DataScannerViewController.isSupported` AND `isAvailable` before showing entry points — `isSupported` is hardware, `isAvailable` is restrictions/permissions.
- **BEST PRACTICE**: For live text/barcode scanning, prefer `DataScannerViewController` over rolling AVFoundation+Vision — much less code and better UX.
- **BEST PRACTICE**: Use Vision revision 3 for text recognition and barcode detection — significantly more accurate than revision 1/2.
- **HIDDEN GEM**: `DataScannerViewController.recognizedItems` is an `AsyncStream` — perfect for SwiftUI `task(id:)` patterns.
- **HIDDEN GEM**: ScreenCaptureKit's hardware-accelerated `IOSurface` delivery makes real-time screen capture practical at 4K 60fps.
- **HIDDEN GEM**: RoomPlan outputs parametric USD with semantic labels (walls, doors, etc.) — not just polygon meshes. Ready for CAD apps.
- **HIDDEN GEM**: Continuity Camera works as a generic AVFoundation device — your existing webcam code "just works" with iPhone-as-camera.
- **PERFORMANCE**: Live Text barcode revision 3 is multi-code in a single ML pass — much faster than scanning each barcode individually.

## Cross-references
- VisionKit (10025, 10026) extends Vision (10024) with UI components.
- ScreenCaptureKit pairs with media playback (10147) and AVQT (10149) for full pipeline analysis.
- ARKit/RoomPlan/USD form the foundation for spatial computing later (visionOS in WWDC23).
