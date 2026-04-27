# Machine Learning, Vision, Create ML & Speech — WWDC 2019 Analysis

**Sessions covered:** 209 (What's New in Machine Learning), 704 (Core ML 3 Framework), 222 (Understanding Images in Vision Framework), 234 (Text Recognition in Vision Framework), 232 (Advances in Natural Language Framework), 256 (Advances in Speech Recognition), 228 (Creating Great Apps Using Core ML and ARKit), 425/426/427/428 (Create ML model trainers), 430 (Introducing the Create ML App), 614 (Metal for Machine Learning)

## Headline

Core ML 3 ships **on-device personalization (training)** for the first time. Create ML becomes a standalone Mac app for training image, sound, activity, text, and recommender models on-device with zero ML expertise required. Vision adds high-quality on-device text recognition. Speech recognition runs on-device for privacy.

## Core ML 3 (209, 704)

- **On-device updatable models** — the headline feature. Train models with user-specific data without sending it to a server. Privacy-friendly.
  - Mark layers as updatable in the model `.mlmodel`.
  - Provide a `MLUpdateTask` with training data.
  - Updated model lives only on the user's device.
  - Use cases: photo album face clustering, handwriting recognition tuned to one user, recommendations.
- **Personalization workflow**: ship a base model, fine-tune the last layers on-device with a small dataset.
- **New layer types**: dynamic shapes, control flow (if/while), nested models, embeddings.
- **Model encryption** — encrypted CoreML models that decrypt only with the app's entitlement.
- **Linked models** (compose multiple `.mlmodel`s into a pipeline at runtime).
- **PERFORMANCE**: Core ML 3 uses Apple Neural Engine (A12+) automatically for supported ops. Up to 10x speedup for inference vs CPU.

## Create ML App (430)

A standalone Mac app — no Xcode playground required.

- Drag-and-drop training: drop labeled folders of images, audio, text, or activity sensor data.
- Live preview during training (loss curves, accuracy graphs).
- Test set evaluation with confusion matrices.
- Multi-version comparison (train two models with different params, compare).
- Output: `.mlmodel` you drop into Xcode.

### Five Trainers Shipped (424-428, 430)

- **Image Classifier** (424) — folders of images per category.
- **Object Detector** (424) — JSON annotations with bounding boxes.
- **Sound Classifier** (425) — audio clips per category.
- **Activity Classifier** (426) — accelerometer/gyro time-series.
- **Recommender** (427) — user-item interaction lists.
- **Text Classifier** (428) — labeled text snippets.
- **Image Similarity** — embeddings for image retrieval.
- **Tabular Regressor / Classifier** — CSV in, predictions out.

**HIDDEN GEM**: model training uses Apple Silicon GPU and Neural Engine — significantly faster than equivalent TensorFlow on the same Mac.

## Vision Framework (222, 234)

- **Saliency** — `VNGenerateAttentionBasedSaliencyImageRequest` and `VNGenerateObjectnessBasedSaliencyImageRequest`. Find what's interesting in an image. Useful for smart cropping.
- **Image Similarity** — `VNGenerateImageFeaturePrintRequest` returns a 2048-dim vector you can compare via cosine distance. Build search-by-image.
- **Animal recognition** — pet detection with bounding boxes.
- **Document detection** — extract a quad-bounded document and dewarp.
- **Text recognition (234)** — fast on-device OCR! Two paths:
  - **Fast** — character-shape based, recognizes ~30 lines/sec.
  - **Accurate** — neural-network based, slower but handles handwriting and stylized text.
  - Region-of-interest support, language hints, custom word lists.
- **Face detection improvements** — better with occlusions, profiles, side angles.

## Natural Language Framework (232)

- **Sentiment analysis** — `tagger.tag(at:unit:scheme:)` with `.sentimentScore` returns -1 to +1.
- **Custom embeddings** — train word embeddings with Create ML.
- **Word/Sentence embeddings** — built-in Apple-trained `NLEmbedding.wordEmbedding(for:)` for many languages.

## Speech Recognition (256)

- **On-device recognition** — `recognizer.requiresOnDeviceRecognition = true`. Privacy-preserving.
- **No request limits** when on-device (server-based has a quota).
- Supported on A9+ devices (iPhone 6S+).
- macOS speech recognition for AppKit and Catalyst apps.
- **Voice Analytics** — new `SFTranscription` properties:
  - `speakingRate` (words/min)
  - `averagePauseDuration`
  - per-segment `voiceAnalytics` with `jitter`, `shimmer`, `pitch`, `voicing`.
  - **HIDDEN GEM**: insight into vocal characteristics — useful for accessibility, fatigue detection, and health apps.

## Photo Segmentation Mattes (260)

New iOS 13 photo metadata: per-pixel mattes for hair, skin, teeth (in addition to the iOS 12 person matte). Composited into Portrait mode photos. Use them for advanced compositing in your camera/photo apps.

## Metal for Machine Learning (614)

- MPSCNN gets new layers (recurrent, attention, batch norm variants).
- MPSGraph (foreshadowed; more in 2020).
- Use `MLComputeUnits.cpuAndGPU` or `.all` (default) on `MLModelConfiguration` to control whether the Neural Engine is used.

## Cross-references

- Vision feeds into RealityKit and ARKit for AR composition: 603, 604.
- Create ML for activity classification + HealthKit: 218 (Exploring New Data Representations in HealthKit).
- ML model encryption + privacy: 708 (Designing for Privacy).
