# Core ML, Vision & NLP — WWDC 2017 Analysis

**Sessions covered:** 703 (Introducing Core ML), 710 (Core ML in Depth), 506 (Vision Framework: Building on Core ML), 208 (Natural Language Processing and your Apps), 711 (Accelerate and Sparse Solvers)

## Headline

Apple introduced its first public, on-device **machine learning inference framework**: Core ML, plus the higher-level domain frameworks Vision (computer vision) and the rebooted NLP (text). All three are built on Accelerate and Metal Performance Shaders. The same inference engines that power Siri, Photos, and the keyboard are now in your apps — with no network calls, no per-prediction cost, and no model data leaving the device.

## The Layered ML Stack (703)

```
   Your App
   ────────────────────────────────────────
   Vision      |   NLP            ← domain frameworks
   ────────────────────────────────────────
   Core ML                         ← model-agnostic inference
   ────────────────────────────────────────
   Accelerate (BNNS, vDSP)  |  MPS (Metal Performance Shaders)
```

**Decision tree**: vision app → Vision; text app → NLP; need a custom model → Core ML directly; doing your own ML primitives → Accelerate + MPS.

## Core ML in Three Lines (703)

1. Drag a `.mlmodel` file into Xcode. Xcode shows the metadata (size, author, license, inputs/outputs) and **auto-generates a typed Swift class** named after the model.
2. Instantiate: `let model = FlowerClassifier()`
3. Predict: `let result = try model.prediction(flowerImage: pixelBuffer); print(result.flowerType)`

The build process compiles `.mlmodel` → `.mlmodelc` (a runtime-optimized format) and embeds it. The generated class is fully typed: inputs and outputs are checked at compile time, not runtime.

## Supported Model Types (703, 710)

- **Neural networks** (feedforward and recurrent), 30+ layer types
- **Tree ensembles** (random forests, boosted trees)
- **Support vector machines**
- **Generalized linear models** (logistic, linear, etc.)
- Mixed-input pipelines (image + text in, text + dictionary out)

**HIDDEN GEM**: Core ML uses a single `MLModel` API surface for every model type. Whether your `.mlmodel` is a 100MB ResNet or a 5KB linear classifier, the calling code is identical — you can A/B-test models by swapping the file. The famous demo swapped a 41 MB FlowerClassifier for a 5.4 MB FlowerSqueeze with no code change.

## Core ML Tools — Convert From Anything (703, 710)

The `coremltools` Python package, **open-sourced** at WWDC 2017, converts:

- **Caffe** (image models)
- **Keras** (TensorFlow backed)
- **scikit-learn** (classical ML)
- **XGBoost** (gradient boosting)
- **LIBSVM**

You can write your own converter — all the primitives are public. There are starter `.mlmodel` files at developer.apple.com/machine-learning (MobileNet, ResNet50, Inception v3, VGG16, SqueezeNet, Places205-GoogLeNet).

## Privacy + Performance Wins (703)

- **PERFORMANCE**: zero network round-trip. Real-time use cases like 60 fps image classification work; sending every frame to a cloud endpoint does not.
- **PRIVACY**: nothing leaves the device. Even health/keyboard text models stay local.
- **COST**: no per-prediction server bill, no rate limits, no offline failure mode. The user goes to Yosemite — your app still classifies the photo.

## The Vision Framework (506)

Vision is Apple's "one-stop computer vision API" — high-level on-device problems wrapped in a single request/observation/handler model.

### What Ships in Vision (506)

| Feature | Notes |
|---|---|
| **Face detection (deep learning)** | Higher precision and dramatically higher recall than the older `CIDetector`. Detects smaller faces, profiles, occluded faces (hats/glasses). |
| **Face landmarks** | Constellation of points: eye corners, mouth outline, chin contour. New in 2017. |
| **Image registration** | Align two images by features. Translation-only or full homography. For panoramas / image stacking. |
| **Rectangle detection** | Returns oriented quadrilateral. Used by the iOS 11 Notes document scanner. |
| **Barcode and QR detection** | Pulls payload + symbology + location. |
| **Text detection** | Returns regions, not characters — pair with your own OCR. |
| **Object tracking** | Initial seed (face, rect, or general bounding box) tracked across a video. Handles large scale changes and deformation. |
| **Custom Core ML model wrapping** | `VNCoreMLRequest(model:)` runs any image-input `.mlmodel` with automatic preprocessing. |

### The Request / Observation / Handler Pattern (506)

```swift
let request = VNDetectFaceRectanglesRequest { req, err in
    let faces = req.results as? [VNFaceObservation]
    // …
}
let handler = VNImageRequestHandler(url: imageURL, orientation: .up, options: [:])
try handler.perform([request])
```

Two handler classes:

- **`VNImageRequestHandler`** — single image, multiple sequential or chained requests; holds the image for its lifetime so it can cache intermediates between requests on the same image.
- **`VNSequenceRequestHandler`** — for tracking across frames; releases each frame after use; cannot do multi-request optimization within a frame.

### Best Practices (506)

- **PERFORMANCE**: pass a `URL` or `Data` (not a pre-decoded image) when reading from disk — Vision will read only what it needs. Critical for 64 MP panoramas.
- **PERFORMANCE**: do NOT pre-scale images. Vision has its own pipeline; pre-scaling means the work happens twice. Only pass small images if you've already shrunk them for display.
- **CRITICAL**: pass the correct `CGImagePropertyOrientation`. A portrait image fed in landscape will fail to find faces — the #1 mistake.
- Run requests off the main queue and dispatch the completion to main for UI work.

### Vision + Core ML Composition (506)

`VNCoreMLRequest` automatically: decodes the image, resizes/center-crops to the model's expected input size, normalizes pixel values, and invokes the model. **HIDDEN GEM**: set `.imageCropAndScaleOption = .scaleFill` / `.centerCrop` / `.scaleFit` to control aspect-ratio handling. Without it, you get the default crop, which can ruin classification on portraits.

### Vision vs Other Detectors (506)

| Engine | Quality | Speed | Power | Available |
|---|---|---|---|---|
| Vision (deep learning) | Best | Good | Optimized | iOS, macOS, tvOS (no watchOS) |
| Core Image `CIDetector` | OK | Faster | OK | Same |
| AVCaptureSession face metadata | Lower | Realtime hardware | Best | During capture only |

**MIGRATION**: existing CIDetector code keeps working, but all new detectors and improvements ship to Vision only. Plan to migrate.

## NLP — Now A Real API (208)

Renamed from NSLinguisticTagger-only days into a proper framework with three new flavors:

- **Language identification** (52 languages, returns confidence-ranked dominant language).
- **Tokenization** at word, sentence, paragraph levels.
- **Lemmatization** (returns base forms — "running" → "run").
- **Part-of-speech tagging** (noun, verb, adjective…).
- **Named-entity recognition (NER)** — NEW: extracts person names, place names, organizations from text. Powers many app features for free.

**HIDDEN GEM**: NLP combined with Core ML enables sentiment analysis end-to-end on device. Pipeline: `NSLinguisticTagger` for tokens/lemmas → custom `.mlmodel` (e.g. trained from scikit-learn) for sentiment classification.

## Accelerate & MPS — The Engines (711)

When the high-level APIs don't fit, drop down:

- **BNNS** (Basic Neural Network Subroutines): convolution, pooling, activation in `Accelerate`. CPU-side, vDSP-backed.
- **MPS Neural Network**: Metal-backed equivalents for GPU inference. The same kernels Core ML uses internally.
- **PERFORMANCE**: MPS now ships with **MPSCNN** (CNN primitives) and a sparse solver suite — large-scale linear algebra and physics simulations get GPU acceleration without writing Metal shaders.

## Cross-Cutting Best Practices

- **BEST PRACTICE**: Always provide a CVPixelBuffer when possible (camera, in-memory raw); use `URL` or `Data` for files; convert to `CGImage` only when needed for UI.
- **PERFORMANCE**: `MLModel` first-load can take noticeable time (model decompression). Instantiate at app launch on a background queue and cache.
- **HIDDEN GEM**: Core ML model files are signed and validated by the system. Don't ship corrupt or hand-edited `.mlmodel` files — they will fail to load with a generic error. Re-export from `coremltools`.

## Cross-references

- See `arkit-debut.md` for using Vision/Core ML on `ARFrame.capturedImage` for AR scene understanding.
- See `metal2-graphics-pipeline.md` for direct MPS usage in custom renderers.
- See `swift4-language-codable.md` for `Decodable` patterns to deserialize JSON model metadata.
