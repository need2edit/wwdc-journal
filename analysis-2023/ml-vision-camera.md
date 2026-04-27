# WWDC 2023 — Machine Learning, Vision, & Camera

WWDC 2023 brings on-device ML maturity: Core ML async prediction, model compression, multilingual NLP, animal/3D body pose, subject lifting, and substantially upgraded camera/HDR/Cinematic APIs.

## Sessions Analyzed
- 10044 — Discover machine learning enhancements in Create ML
- 10042 — Explore Natural Language multilingual models
- 10045 — Detect animal poses in Vision
- 111241 — Explore 3D body pose and person segmentation in Vision
- 10049 — Improve Core ML integration with async prediction
- 10047 — Use Core ML Tools for machine learning model compression
- 10050 — Optimize machine learning for Metal apps
- 10101 — Customize on-device speech recognition
- 10176 — Lift subjects from images in your app
- 10105 — Create a more responsive camera experience
- 10106 — Support external cameras in your iPadOS app
- 10107 — Embed the Photos Picker in your app
- 10137 — Support Cinematic mode videos in your app
- 10181 — Support HDR images in your app
- 10256 — Discover Continuity Camera for tvOS
- 10304 — Integrate with motorized iPhone stands using DockKit
- 10319 — Create animated symbols (cross-listed)

## Subject Lifting in Your App (10176)

The "tap-and-hold to lift the dog out of the photo" feature in iOS 16 Photos is now an API.

```swift
let analyzer = ImageAnalyzer()
let analysis = try await analyzer.analyze(image, configuration: .init([.visualLookUp]))
let interaction = ImageAnalysisInteraction()
view.addInteraction(interaction)
interaction.analysis = analysis
interaction.preferredInteractionTypes = .imageSubject
```

Programmatic API for extracting subjects:
```swift
let subjects = try await analysis.subjects
let subject = subjects.first
let cutOutImage = try await subject?.image  // PNG with transparent background
```

Use cases: stickers, drag-and-drop product photos, document scanning enhancements.

## Core ML Async Prediction (10049)

`MLModel.prediction(from:)` is now an `async throws` function. Replace dispatch queues with structured concurrency.

```swift
let result = try await model.prediction(from: input)
```

Batch prediction:
```swift
let results = try await model.predictions(from: inputs, options: options)
```

`MLPredictionOptions.usesCPUOnly` lets you force CPU for repeatable benchmarks. Async prediction works inside `TaskGroup` for parallel inference (one task per frame in video pipelines).

## Core ML Tools Compression (10047)

`coremltools` 7 brings major model size reductions:

| Technique | Size Reduction | Quality Impact |
|-----------|---------------|----------------|
| Linear quantization (8-bit) | ~4x | Very low |
| Palettization (4-bit, 6-bit) | ~6-8x | Low–medium |
| Pruning (sparsity) | ~2x | Depends on density |
| Combined (quant + palett) | ~10-15x | Tunable |

These are POST-TRAINING — apply to an existing `.mlmodel` without retraining. Critical for shipping LLMs and large vision models within the App Store binary limits.

## Vision Animal Pose & 3D Body Pose

- `VNDetectAnimalBodyPoseRequest` — keypoints for cats and dogs (eyes, ears, nose, paws, joints, tail).
- `VNDetectHuman3DBodyPoseRequest` (visionOS / iOS 17) — 3D joint positions in camera space, NOT just 2D screen positions. Replaces the older 2D-only API for fitness apps.
- `VNGeneratePersonSegmentationRequest` upgraded for higher quality and better edge handling around hair and fingers.

The 3D pose API is what powers the visionOS body-tracking demos. Available on iPhone 12+ for camera-based pose.

## Multilingual NLP (10042)

`NLContextualEmbedding` now supports multilingual transformer models in 27 languages. Replaces the old language-specific word embeddings.

```swift
let embedding = try NLContextualEmbedding(language: .english)
let embeddings = try embedding.embeddingResult(for: "The quick brown fox", language: .english)
```

Use cases: semantic search, document clustering, cross-language similarity. The embeddings are 512-dim vectors suitable for cosine similarity.

## Speech Recognition Customization (10101)

`SFSpeechRecognizer` now supports CUSTOM VOCABULARY:

```swift
let request = SFSpeechURLRecognitionRequest(url: audio)
request.customizedLanguageModel = SFCustomLanguageModelData(...)
```

You can boost specific phrases ("BarkBoss MAX-9000" — your product name) so the recognizer picks them up reliably. Offline recognition improved across the board.

## Camera: More Responsive Capture (10105)

Two new APIs reduce shutter lag dramatically:

1. **Deferred photo processing** — `AVCapturePhotoOutput.isAutoDeferredPhotoDeliveryEnabled = true`. Camera returns a "proxy" photo immediately; full-quality processing happens in the background. User sees their captured photo instantly.

2. **Zero shutter lag** — capture starts BEFORE the user taps. The system buffers frames; on capture, it picks the best frame from the buffer at the moment of tap. Already used by the system Camera app; now available to your app.

3. **Responsive capture queue** — burst photo capture without dropping frames between shots.

## Cinematic API (10137)

Cinematic mode videos (with the rack-focus depth-blur effect) can now be:
- READ: extract focus tracks, depth data, and disparity from `.mov` files.
- EDITED: change focus subject post-capture.
- PLAYED: with the cinematic rendering applied at playback time.

`AVAsset.loadTracks(withMediaType: .cinematic)` returns the depth track. `CNFocusDecision` represents focus selections over time.

## HDR Images (10181)

iOS 17 supports HDR JPG, HEIC, AVIF for both reading and writing. `Image(systemName: ...)` and `Image(uiImage:)` paint with extended dynamic range when:
- Display supports HDR
- `.allowedDynamicRange(.high)` modifier is applied.

WARNING: HDR images draw attention. Don't use them as thumbnails — use `.standard` dynamic range there. Use HDR for hero/full-screen content.

## Embedded Photos Picker (10107)

`PhotosPicker` view (introduced 2022) gets:
- Inline embedded mode (no sheet).
- Filter UI for asset type/album.
- Better selection UI for multi-select.

```swift
PhotosPicker(selection: $selectedItems, matching: .images, photoLibrary: .shared()) { ... }
```

Privacy: the picker runs OUT-OF-PROCESS, so your app never gets full photo library access — only the selected assets are vended.

## DockKit (10304)

Motorized iPhone stands (Belkin Auto-Track and others) accept DockKit commands.

```swift
DockAccessoryManager.shared.accessoryStateChanges  // AsyncStream
let accessory = DockAccessoryManager.shared.accessories.first
try await accessory?.setOrientation(...)
```

Apps can override the auto-tracking with custom subjects (track the speaker, track a soccer ball).

## Continuity Camera for tvOS (10256)

iPhone can now act as a webcam for tvOS apps via Continuity Camera. Same API as macOS:

```swift
let session = AVCaptureSession()
let device = AVCaptureDevice.default(.builtInWideAngleCamera, for: .video, position: .front)
// On Apple TV, this resolves to the paired iPhone.
```

## Pathways

- **Vision/Photos developer**: 10176 → 10044 → 10045
- **ML model deployment**: 10049 → 10047 → 10050
- **Camera advanced**: 10105 → 10137 → 10181
- **Multilingual / Speech**: 10042 → 10101

## Hidden Gems

- The Photos Picker runs in a SEPARATE PROCESS — your privacy posture improves WITHOUT changing your code, because you never get full library access.
- Subject lifting works on a single image OFFLINE — no network needed.
- Core ML async prediction respects task cancellation; killing the parent task aborts inference.
- 4-bit palettization can shrink an LLM by ~8x with minimal quality loss for many language tasks. Critical for on-device gen-AI in 2023.
- Cinematic mode focus DECISIONS are stored as edit-list metadata, so you can change focus targets post-capture without re-rendering.
- HDR rendering only kicks in if your view tree opted in (`.allowedDynamicRange(.high)`) AND the display supports it. Defaults are conservative.
- Animal pose works in real time on A14+ and is fast enough for live preview.
- DockKit accessories can broadcast SUBJECT POSITION events to the app even when the user isn't actively in your viewfinder.
- Speech recognition's offline model now matches cloud quality for many languages — important for privacy-first apps.
- Zero shutter lag works by using a circular buffer of frames — the buffer eats memory, so disable it on low-RAM devices.
