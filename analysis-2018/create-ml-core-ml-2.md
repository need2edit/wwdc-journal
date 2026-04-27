# Create ML & Core ML 2 — WWDC 2018 Analysis

**Sessions covered:** 703 (Introducing Create ML), 708 (What's New in Core ML, Part 1), 709 (What's New in Core ML, Part 2), 712 (A Guide to Turi Create), 713 (Introducing Natural Language Framework), 716 (Object Tracking in Vision), 717 (Vision with Core ML), 609 (Metal for Accelerating Machine Learning), 102 (Platforms State of the Union §ML)

## Headline

WWDC 2018 closed the loop: 2017 gave us **Core ML** for inference; 2018 gives us **Create ML** for training and **Core ML 2** with massive size and speed wins. Train a custom image classifier in 30 lines of Swift in a Playground, drag the resulting `.mlmodel` into your app, and ship an experience that would have been a 100 MB add-on a year ago in ~80 KB. The new **Natural Language framework** replaces `NSLinguisticTagger` and accepts custom text classifiers and word taggers trained in Create ML.

## Create ML Core Workflow (703)

Three problems, one Swift API:

| Domain | Use case | Code lines |
|---|---|---|
| Images | Custom classifier (your products, art styles, plant species) | ~5 |
| Text | Topic classification, sentiment, intent detection | ~5 |
| Tabular | Regression / classification on rows-and-columns data | ~5 |

```swift
import CreateML
let data = MLDataTable(contentsOf: csvURL)
let model = try MLImageClassifier(trainingData: .labeledDirectories(at: trainURL))
let metrics = model.evaluation(on: .labeledDirectories(at: testURL))
try model.write(to: outputURL)
```

The reason this is so short: **transfer learning**. Apple ships a pre-trained large image classifier _in the operating system_, and Create ML adds a small head on top using your data. You ship only the head — kilobytes, not megabytes.

## The 100 MB → 83 KB Result (703)

- Demo app: classify fruit. With a 2017-style state-of-the-art classifier inside the app: 100 MB.
- After Create ML retraining + transfer learning: **83 KB**.
- Three orders of magnitude smaller — same accuracy on the relevant labels.
- **HIDDEN GEM**: the head is tied to the OS-resident base model. Older OS versions don't have the base, so a Create-ML-trained image classifier requires iOS 12 / macOS Mojave minimum.

## Two Create ML UIs (703)

- **Drag-and-drop UI** (`CreateMLUI`) — open a Playground, write `MLImageClassifierBuilder().showInLiveView()`, drag your training folder into the canvas, training begins instantly with GPU acceleration. Drag a test folder for evaluation, then drag the trained model out into your Xcode project.
- **Programmatic API** (`CreateML`) — same workflow as a script, suitable for scheduled retraining or CI pipelines.

Tabular data uses `MLDataTable` (built atop Turi Create's SFrame) with subscript syntax (`table["price"]`), arithmetic between columns, splitting, filtering. Several regression and classification algorithms (Linear, Boosted Tree, Random Forest, Logistic) plus the high-level `MLRegressor` / `MLClassifier` wrappers that auto-select the best algorithm.

## Natural Language Framework (713)

- Replaces `NSLinguisticTagger` with a Swift-native API across iOS, macOS, tvOS, watchOS.
- `NLLanguageRecognizer.dominantLanguage(for:)` — single best language guess.
- `NLLanguageRecognizer.languageHypotheses(withMaximum: 3)` — top-N guesses with probabilities, perfect for multilingual messaging apps.
- `NLTokenizer(unit: .word)` — handles word boundaries even in scripts like Chinese where there are no spaces.
- `NLTagger(tagSchemes: [.nameType, .lexicalClass])` — named entity recognition, part-of-speech tagging, lemma, language, script.
- **HIDDEN GEM**: custom text classifiers and word taggers train in Create ML, drop directly into the Natural Language API:
```swift
let nlModel = try NLModel(mlModel: customMLModel)
tagger.setModels([nlModel], forTagScheme: customScheme)
```
The tagger then handles tokenization and feature extraction automatically — no need to maintain matching preprocessing code in your app.

## Quantization: 4× to 8× Smaller Models (708, 709)

- Core ML 1 stored neural network weights as 32-bit floats. Core ML 1.2 added 16-bit floats (50% reduction).
- Core ML 2 supports **arbitrary bit depths** down to 1 bit. ResNet-50 went from 102 MB → 26 MB at 8 bits → 12.8 MB at 4 bits.
- Two algorithms: **linear quantization** (uniform mapping) and **lookup-table quantization** (non-uniform clusters, k-means by default but you can plug in your own).
- Live demo with style transfer: 32-bit (6.7 MB) → 8-bit (1.7 MB) → 4-bit (~960 KB) → 3-bit (~50 KB but visible color shift) → 2-bit (artifacts).
- **BEST PRACTICE**: there's an accuracy-vs-size tradeoff. Use `coremltools.models.neural_network.quantization_utils.compare_models(...)` to measure top-1 agreement against your test set before shipping. Apple's example app went from 27 MB to 3.4 MB by quantizing four style models to 4-bit with no visible quality loss.

## Flexible Shapes (708)

- Models can now declare a _range_ of input dimensions or an _enumeration_ of accepted shapes. Previously you needed one model per resolution.
- Use case: style transfer that supports both standard-definition and high-definition versions — one model file, switch sizes at runtime via `MLModel`'s configuration.
- Enumerated shapes are faster than ranges because Core ML can pre-optimize for each known shape.
- Works with fully-convolutional networks (style transfer, super-resolution, image enhancement, segmentation). Core ML Tools can detect whether a model qualifies.

## Batch Prediction API (708)

- Old: `model.prediction(from: input)` in a `for` loop. The GPU pipeline bubbled between calls — idle time, then ramp.
- New: `model.predictions(from: [inputs])` — Core ML keeps the GPU continuously busy and runs at higher performance state. Live demo: ~3× faster than the for-loop on a batch of 200 style-transfer renders.
- Use whenever you have an array of inputs ready to process (batch image classification, batch sentence sentiment, etc.).

## Custom Layers and Custom Models (708, 709)

- The neural network field moves so fast that any new research paper might use a layer Core ML doesn't natively support. Custom layers solve this.
- Conform to `MLCustomLayer`: provide an init from layer parameters (stored in the `.mlmodel`), an output-shape callback, and an `evaluate(inputs:outputs:)` method. Optional: a Metal Shading Language implementation that runs in the same command buffer as the rest of the model — no extra round-trips to the GPU.
- **Custom Models** generalize this beyond neural networks. Conform to `MLCustomModel` for entirely new model types (k-NN, locality-sensitive hashing, hybrid systems combining audio + motion, etc.).
- Both are first-class assets in Xcode — class names show in the model description and required dependencies are listed.

## Vision Improvements (716, 717)

- New `VNDetectFaceRectanglesRequest`, `VNDetectFaceLandmarksRequest`, `VNDetectBarcodesRequest`, plus people segmentation that separates a person from the background using portrait-mode depth.
- `VNTrackObjectRequest` (object tracking across video frames) is fully Apple-vended now — previously you'd have to build your own optical flow.
- `VNCoreMLRequest` connects any Vision-amenable Core ML model to the request pipeline; image preprocessing (rotation, scaling, color matching) is handled by Vision.

## Turi Create as the Open-Source Companion (712)

- Apple open-sourced Turi Create in late 2017. It's the Python toolkit Create ML wraps for tabular work and several other tasks.
- Multi-task models (one network, multiple labels — e.g., "what type of bird is this AND is it adult or juvenile") are easier to express in Turi Create than in Create ML's Swift API.
- Useful when you need data prep (joins, filters, transforms) before training, since `SFrame` is more fully-featured than `MLDataTable`.

## Metal Performance Shaders for Training (609, 102)

- 2018 added training kernels (not just inference) to MPS. An order-of-magnitude faster training on macOS.
- Apple announced a partnership with Google to bring Metal acceleration to TensorFlow — early benchmarks 20× the previous unaccelerated implementation.
- For most apps Create ML is all you need. MPS is the path when you're rolling your own training loop or have novel topologies that don't map to either Create ML or Turi Create.

## Privacy is the Story (713, 102)

- Every Create ML / Core ML / Natural Language pipeline runs **on device**. Training in Create ML happens on your Mac; inference happens on the user's device.
- Compare to cloud-based ML: zero data egress, no per-prediction billing, latency-free inference, works offline.
- This is why Apple invested in Create ML rather than just shipping a hosted training API.

## DEPRECATION (713)

- `NSLinguisticTagger` still works but is no longer the future. Move to `NLTagger` and `NLTokenizer`.

## Cross-references

- Apple's iOS 12 face / scene effects in Camera and Photos (people segmentation) use the same Vision pipeline you have access to.
- Core Image's Python integration (719 — Core Image: Performance, Prototyping, and Python) lets you script CI filter chains for ML pre/post-processing.
- See 102 for Apple's high-level positioning: ML adoption, Create ML demo, transfer learning explanation.
