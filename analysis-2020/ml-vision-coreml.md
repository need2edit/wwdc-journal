# WWDC 2020 — ML, Vision, Core ML, Create ML

WWDC 2020's ML story focused on **bringing more powerful models on-device** — Core ML model deployment & encryption, an MPS Graph API for custom model training on the GPU, Vision's new hand and body pose detectors, Create ML's action classification, and PyTorch → Core ML conversion.

## Sessions Analyzed
- 10043 — Build an Action Classifier with Create ML
- 10099 — Explore the Action & Vision app
- 10153 — Get models on device using Core ML Converters
- 10154 — Convert PyTorch models to Core ML
- 10155 — Improve Object Detection models in Create ML
- 10156 — Control training in Create ML with Swift
- 10653 — Detect Body and Hand Pose with Vision (gateway)
- 10673 — Explore Computer Vision APIs
- 10657 — Make apps smarter with Natural Language
- 10677 — Build customized ML models with the Metal Performance Shaders Graph
- 10152 — Use model deployment and security with Core ML
- 10042 — Build SwiftUI apps for tvOS (covered in tvOS analysis; mentions ML use cases)
- 10044 — (placeholder — analytics in Create ML)

## Vision: Hand and Body Pose Detection

The headline 2020 Vision additions: **`VNDetectHumanHandPoseRequest`** and **`VNDetectHumanBodyPoseRequest`**.

### Hand Pose

21 landmarks per hand: 4 per finger + thumb + 1 wrist. Returns `VNRecognizedPointsObservation`s with grouped point keys.

```swift
let request = VNDetectHumanHandPoseRequest()
let handler = VNImageRequestHandler(cvPixelBuffer: buffer, options: [:])
try handler.perform([request])
guard let observation = request.results?.first else { return }
let thumbPoints = try observation.recognizedPoints(forGroupKey: .handLandmarkRegionKeyThumb)
let indexPoints = try observation.recognizedPoints(forGroupKey: .handLandmarkRegionKeyIndexFinger)
guard let thumbTip = thumbPoints[.handLandmarkKeyThumbTIP],
      let indexTip = indexPoints[.handLandmarkKeyIndexTIP] else { return }
```

Default `maximumHandCount` is **2**. Increase if you need more, but each additional hand has a latency cost — pose computation is per-hand.

Apple's sample app: pinch detection between thumb tip and index tip with a 40-point distance threshold and 3-frame state-change debouncing. Use this pattern (collect evidence frames before transitioning state) to avoid jitter.

### Caveats
- Hands near screen edges may be partially occluded — pose accuracy degrades.
- Hands parallel to the camera (a karate-chop pose) — algorithm struggles.
- Gloves can confuse it.
- The algorithm sometimes detects feet as hands. Be defensive.

### Body Pose

19 landmarks (5 face: nose, eyes, ears; 6 arms; 3 torso/hip; 6 legs). Same request pattern as hand pose. Each landmark belongs to a group key (left arm, right arm, torso, left leg, right leg, face); groups can overlap (shoulders are in both arm and torso groups).

### Caveats
- Bent-over or upside-down subjects: degraded accuracy.
- Flowing clothing can obstruct.
- One person partially occluding another can confuse identity.

### Vision Body Pose vs. ARKit Body Pose
- Vision: still images, recorded videos, any platform except watchOS, **per-point confidence** values.
- ARKit: live ARSession only, supported devices only, rear-facing camera only, designed for live motion capture, no per-point confidence.
- **For training Create ML action classifiers, use Vision** — Vision is what's used at inference time.

## Action Classification with Create ML (10043, 10099)

A new Create ML template: train a model to recognize body actions (jumping jacks, squats, dance moves) from videos.

### Training Data

- Videos of the action, ideally with **only one subject in frame** (Vision will pick the largest one by default).
- Crop your training videos so only the subject of interest is present.
- Or: pre-extract poses with `VNRecognizedPointsObservation.keypointsMultiArray()` and feed `MLMultiArray` directly for full control.

### Inference

Action classification needs a **time window** of body poses (the model is trained on a fixed sample count, typically 60). Maintain a ring buffer of `VNRecognizedPointsObservation`s. When you want to classify:

```swift
// Concatenate keypointsMultiArrays into a single MLMultiArray
// Provide as input to your classifier
let input = PlayerActionClassifierInput(poses: bigArray)
let output = try classifier.prediction(input: input)
let label = output.label  // Most-probable action
```

### Performance Tip

On older devices, doing inference every frame will starve the camera buffer pipeline. Body pose generation is fine every frame (the classifier expects that sampling rate), but **only run classification a few times per second**. Recognizing an action within a fraction of a second is plenty for most use cases.

The Action & Vision sample (10099) demonstrates the full pipeline: pose detection → trajectory analysis (for projectiles like cornhole bean bags) → action classifier. Beautiful end-to-end demo.

## Computer Vision APIs Refresher (10673)

VNContoursRequest got upgraded to detect contours within an image (good for shape extraction). VNGenerateOpticalFlowRequest for dense optical flow. New `VNTrackTranslationalImageRegistrationRequest` for registering frames against each other. The session is primarily a tour of the Vision toolset.

## Create ML Improvements (10155, 10156)

### Object Detection (10155)

A new training algorithm based on **transfer learning** with smaller models. Faster training, smaller model size, accuracy improvements for object detection.

### Control Training in Swift (10156)

Create ML had an app UI; now there's a **Swift framework** for full programmatic control. Run training in a script, schedule retraining, integrate with CI. Train models from the same JSON/folder layouts the app uses.

```swift
import CreateML
let trainer = try MLObjectDetector.train(trainingData: ..., parameters: ...)
let model = try trainer.makeModel()
try model.write(to: url)
```

## PyTorch → Core ML (10154)

`coremltools 4` natively converts PyTorch models (via TorchScript). Previously you went PyTorch → ONNX → Core ML; now direct. Critical for shipping models from research/HuggingFace into iOS apps.

## Get Models On Device (10153)

The same `coremltools 4` covers TensorFlow → Core ML conversion improvements, plus model size optimizations (palettization for weight compression). Critical for shipping ML in App Store binary limits.

## Core ML Model Deployment & Security (10152)

Two big additions:

### Model Encryption

Encrypt your `.mlmodel` files at build time. Apple manages the key via your developer ID; the model is decrypted into memory only when loaded. Critical for ML models that represent expensive IP.

### Model Deployment (Cloud-hosted)

Apple-hosted Core ML model deployment. Push new model versions through a console; apps download updates via background refresh. Use cases:
- A/B test models without app updates
- Hot-fix bad models without going through App Review
- Roll out improved models for trained-on-user-data scenarios

API:
```swift
MLModelCollection.beginAccessing(identifier: "MyModelCollection")
let modelEntry = collection.entries["MyModel"]!
let url = modelEntry.modelURL  // Decrypted, downloaded, cached
let model = try MyModelClass(contentsOf: url)
```

## Natural Language (10657)

NLP is "ML for text." Improvements in 2020:
- **Native sentence embedding** support — semantic similarity without rolling your own.
- Improved tokenization for more languages.
- Built-in personal-data scrubbing helpers (find emails, phone numbers, locations to redact).
- The Sentiment Analysis API (`NLTagger`) gets refinements.

## MPS Graph: Train on Metal (10677)

Metal Performance Shaders (MPS) Graph is an API for **building and running computational graphs on the GPU directly**. Without leaving Metal, you can:
- Train custom neural networks on Apple GPUs.
- Run inference for non-Core-ML model architectures.
- Compose differentiable ops for custom losses.

This is for advanced ML developers / framework authors — most app developers stick with Core ML.

## Cross-References
- [arkit-realitykit-usd.md](arkit-realitykit-usd.md) — ARKit body pose vs. Vision body pose.
- [privacy-security-network.md](privacy-security-network.md) — on-device ML is the privacy-friendly alternative to cloud inference.
- [media-hls-audio.md](media-hls-audio.md) — `VNDetectAnimalRectanglesRequest` and similar are useful in media apps.

## Adoption Checklist
- [ ] If your app uses gesture interaction, evaluate `VNDetectHumanHandPoseRequest` for new interaction modes.
- [ ] If your app analyzes movement (fitness, dance, sports), explore body pose + action classification.
- [ ] Pre-process Create ML training videos (single subject, cropped) for best results.
- [ ] If your model is sensitive IP, encrypt with `coremltools` at build time.
- [ ] If you ship multiple model versions, evaluate Apple-hosted model deployment.
- [ ] Convert PyTorch models directly via the new `coremltools` 4 path.
- [ ] If you wrote model-loading boilerplate, simplify with `MLModelCollection`.
- [ ] Limit body-pose action classification to a few inferences per second on older devices.
