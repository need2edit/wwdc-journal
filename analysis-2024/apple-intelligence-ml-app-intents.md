# Apple Intelligence, Machine Learning & App Intents -- WWDC24 Deep Analysis

Comprehensive analysis of the WWDC 2024 sessions covering Apple Intelligence, Writing Tools, Genmoji, the Translation framework, Vision framework Swift API, Core ML, Create ML, and the major App Intents revolution that connects apps to Siri's new LLM-powered intelligence.

Sessions analyzed: 10117 (Translation), 10168 (Writing Tools), 10220 (Genmoji), 10133 (Bring your app to Siri), 10134 (What's new in App Intents), 10210 (Bring core features with App Intents), 10176 (Design App Intents), 10223 (Explore ML overview), 10161 (Core ML deploy), 10183 (Create ML), 10159 (ML to Apple silicon), 10160 (Train on Apple GPUs), 10211 (BNNS Graph CPU), 10218 (Metal ML), 10163 (Vision framework Swift).

---

## 1. The Apple Intelligence Strategy -- Three Adoption Tiers

WWDC24 presents Apple Intelligence as a layered system with **three distinct integration points** depending on how much control you need (WWDC24-10223):

1. **Built-in OS features** -- adopt Writing Tools / Image Playground / Genmoji with zero or minimal code; users get them for free in any text view that uses TextKit 2.
2. **App Intents + Assistant Schemas** -- expose your app's verbs and nouns so Siri (and Spotlight, Shortcuts, Action Button, Apple Pencil squeeze, Control Center) can invoke them with natural-language understanding from the new LLM-powered Siri.
3. **Bring your own model** -- use Core ML, MPS Graph (GPU-bound), or BNNS Graph (CPU/real-time) to deploy your own ML/AI models on device.

This layered approach is the central organizing principle of WWDC 2024's ML story.

---

## 2. Writing Tools -- The Free Win (WWDC24-10168)

### 2.1 The "It Just Works" Path

If your app uses `UITextView`, `NSTextView`, or `WKWebView` with **TextKit 2**, Writing Tools appears automatically -- in the callout bar, context menu, Edit menu, and on hover (macOS).

**Critical caveat:** TextKit 1 only gets the *limited* panel experience (rewritten text in a popover). Full inline experience requires TextKit 2.

### 2.2 The New Delegate Methods You Must Implement

```swift
func textViewWritingToolsWillBegin(_ textView: UITextView) {
    // Pause syncing, prevent direct text manipulation
}
func textViewWritingToolsDidEnd(_ textView: UITextView) {
    // Resume syncing
}
```

**Hidden gem:** Writing Tools modifies your text storage **directly** -- including pushing changes to the undo stack. **Do NOT persist text storage while `isWritingToolsActive` is true** (data corruption risk during long async streams).

### 2.3 Behavior Control

```swift
textView.writingToolsBehavior = .complete    // default for native views
textView.writingToolsBehavior = .limited     // panel only
textView.writingToolsBehavior = .none        // opt out

textView.writingToolsAllowedInputOptions = [.plainText, .richText, .table]
```

**Hidden gem:** `WKWebView`'s default is `.limited`, NOT `.complete`. Set it explicitly if you want the full inline experience.

### 2.4 Protecting Code Blocks and Quotes

A new `UITextViewDelegate` method lets you return ranges Writing Tools should ignore -- code blocks in a notes app, `<blockquote>` in a mail composer:

```swift
func textView(_:writingToolsIgnoredRangesIn:) -> [NSRange] { ... }
```

For `WKWebView`, `<blockquote>` and `<pre>` are auto-ignored. (WWDC24-10168)

### 2.5 Custom Text Views Path (WWDC24-10168)

- iOS: Adopt `UITextInteraction` (or `UITextSelectionDisplayInteraction` + `UIEditMenuInteraction`)
- macOS: Adopt `NSServicesMenuRequestor` + override `validRequestor(forSendType:returnType:)`

Even if you can't fully integrate, you get the *panel* experience for free.

---

## 3. Genmoji & NSAdaptiveImageGlyph (WWDC24-10220)

### 3.1 The Core Concept

`NSAdaptiveImageGlyph` is the new API behind Genmoji, Memoji, and stickers used inline as text. Each glyph carries:
- A square-aspect-ratio image with multiple resolutions
- A globally **unique and stable identifier** (deduplicate before storing!)
- A content description (used as alt-text + accessibility)
- Alignment metrics that adapt to the surrounding font

### 3.2 Adoption -- One Line

```swift
textView.supportsAdaptiveImageGlyph = true     // iOS
textView.importsGraphics = true                // macOS
```

If you already support image paste (`pasteConfiguration` includes images), this is enabled by default. (WWDC24-10220)

### 3.3 The Plain-Text Storage Pattern

If your storage is plain text (server-bound, etc.), the recommended pattern is the same as for inline images:
1. Store the Unicode attachment character (`U+FFFC`) in plain text at the position
2. Store the image identifier alongside
3. Maintain an image store keyed by identifier (deduplicate -- the IDs are stable)

### 3.4 Cross-Compatible HTML Export

```swift
let html = attributedString.data(from: range, documentAttributes: [.documentType: NSAttributedString.DocumentType.html])
```

Emits `apple-adaptive-glyph` typed HTML. WebKit displays inline; other browsers fall back to a static image. The fallback alt-text comes from the glyph's `contentDescription`. (WWDC24-10220)

### 3.5 Notification Support

`UNNotificationAttributedMessageContext` lets push notifications carry rich text with image glyphs. Use a Notification Service Extension to download assets and assemble the attributed string.

### 3.6 Critical Compatibility Warning

> "Image glyphs may not be appropriate for use with text-only items such as email addresses and phone numbers." (WWDC24-10220)

User-generated content (titles, posts, messages) is the right home for glyphs. Don't allow them in a phone-number or email field.

---

## 4. The Translation Framework (WWDC24-10117)

### 4.1 Two Tiers of Adoption

1. **`.translationPresentation()`** -- one SwiftUI modifier, system overlay, zero customization. Already shipping.
2. **`TranslationSession` + `.translationTask`** -- full control, batch translation, custom UI placement.

### 4.2 The On-Device Model Sharing

> "TranslationSession performs translation using on-device ML models. These models are shared with all apps on the system, including the Translate app." (WWDC24-10117)

If the user already downloaded Spanish for the Translate app, your app uses it for free. The framework handles permission prompts, progress UI, and *background* downloads (continues even if the user closes the sheet or your app).

### 4.3 The Streaming vs. Batched API Choice

```swift
// Batched -- all results at once, original order
let results = try await session.translations(from: requests)

// Streaming -- AsyncSequence, results as ready
for try await response in session.translate(batch: requests) { ... }
```

**Performance tip:** ALWAYS prefer batch APIs over single-string in a loop. The model spins up once per batch.

**Critical:** When using the streaming version, set `clientIdentifier` per request -- responses are NOT in input order.

### 4.4 Mixed-Language Batches Produce Garbage

> "Mixing different languages in the same batch will produce poor results." (WWDC24-10117)

Group your requests by source language, call `.translate(batch:)` per group on the same session.

### 4.5 Lifecycle Trap

`TranslationSession` is anchored to its view. If the view disappears, the session breaks. **Do NOT store the session in a model object or singleton.**

### 4.6 Simulator Doesn't Work

> "These translation APIs don't function in the simulator. Be sure to do development on an iPhone, iPad, or Mac." (WWDC24-10117)

### 4.7 New Hindi Support + 19 Languages Total

Use `LanguageAvailability.supportedLanguages` -- the list grows OS-by-OS. New: Hindi.

---

## 5. App Intents -- The Foundation for Everything (WWDC24-10210, 10133, 10134)

### 5.1 The Core Insight

> "App Intents is not a feature in itself. It's a common foundation for building features." (WWDC24-10210)

A single `AppIntent` definition powers Spotlight, Shortcuts, Siri, Widgets, Controls, Action Button, Apple Pencil squeeze, **and** the new Apple Intelligence experiences. **You write code once, get N+ entry points.**

### 5.2 The Trinity: Intents, Entities, App Shortcuts (WWDC24-10210)

| Concept | Role | Example |
|---|---|---|
| **AppIntent** | Verb / action | `OpenTrailIntent`, `FavoritePhotoIntent` |
| **AppEntity** | Noun / content | `TrailEntity`, `AssetEntity` |
| **AppShortcut** | Sentence (zero-config) | "Open my pinned trail" |

### 5.3 Critical: Parameters Should Be ENTITIES, Not IDs

> "A parameter that refers to an entity should be an entity, not data describing one. So this isn't a trail name, or UUID, it's a TrailEntity." (WWDC24-10210)

This is non-obvious and frequently broken in shipping App Intents.

### 5.4 The `EntityQuery` Subprotocols

Queries answer two questions:
- "What entities exist?" → `EnumerableEntityQuery.allEntities()`
- "What entity has this ID?" → `EntityQuery.entities(for:)`

**Hidden gem:** With iOS 18 SDK, App Intents can DERIVE the more complex queries (search-by-string, search-by-predicate) from `EnumerableEntityQuery`. You only need the more advanced protocols if your data set doesn't fit in memory or you want a custom search algorithm. (WWDC24-10210)

### 5.5 The `ParameterSummary` -- Don't Skip It

Without it, your intent shows up in Shortcuts with the parameter "below the fold." A `parameterSummary` is a natural-language sentence (`"Open \(\.$trail)"`) that makes the intent's purpose readable. **Required for a polished Shortcuts experience.**

### 5.6 Intent Reuse Across Surfaces (WWDC24-10210)

The OpenTrailIntent can simultaneously be:
- A Shortcuts action (default)
- A widget configuration intent (add `WidgetConfigurationIntent` conformance)
- A Control Center button action (add `ControlConfigurationIntent`)
- An App Shortcut (wrap it in `AppShortcut`)

**Each conformance is empty** -- it's just declaring "this intent fits this role."

### 5.7 Returning Dialog + Snippet for Siri (WWDC24-10210)

```swift
return .result(dialog: "It's 72° at \(trail.name)") {
    TrailConditionsView(trail: trail)
}
```

If Siri is on a HomePod or AirPods, dialog is spoken. On screen, the snippet view shows. View is archived like a widget -- subset of SwiftUI. **Strongly preferred over `openAppWhenRun` for ambient queries.**

### 5.8 Code-Free App Shortcut Registration

> "Notice one thing that's not here: any sort of registration code. The App Intents framework automatically detects the provider and handles registration." (WWDC24-10210)

Just declare `AppShortcutsProvider` -- Siri picks it up at install.

---

## 6. App Intents 2024 Improvements (WWDC24-10134)

### 6.1 IndexedEntity -- Entities in Spotlight + Semantic Search

```swift
extension TrailEntity: IndexedEntity { }
// In your app init:
try await CSSearchableIndex.default().indexAppEntities(trails)
```

**Hidden gem:** This wires your entities into Siri's new **semantic search**. Searching "pets" finds entities tagged with cats, dogs, snakes -- not just literal string matches.

The default uses `DisplayRepresentation`. For better results, override `attributeSet` to add city/state/keywords/etc.

### 6.2 Transferable for Entities

App Entities can now conform to `Transferable`. This is huge -- it means Shortcuts can convert your `ActivitySummaryEntity` to PDF, image, RTF, plain text on the fly:

```swift
static var transferRepresentation: some TransferRepresentation {
    DataRepresentation(exportedContentType: .rtf) { entity in
        entity.asRichText()
    }
    FileRepresentation(exportedContentType: .png) { entity in
        SentTransferredFile(entity.exportPNG())
    }
}
```

**Critical ordering rule:** Highest-fidelity representation FIRST. (WWDC24-10134)

### 6.3 FileEntity -- When the File IS the Entity

If your entity *is* a document on disk (PhotoEntity, NoteFile), conform to `FileEntity`. Other apps can then operate on it via `IntentFile` -- e.g., a "Rotate Image" intent in another app can rotate your photos in place. The `FileEntityIdentifier` uses bookmark data, surviving moves and renames.

### 6.4 URLRepresentable Types

Let Siri/Shortcuts treat your entity as a deep link:

```swift
extension TrailEntity: URLRepresentableEntity {
    static var urlRepresentation: URLRepresentation {
        "https://trails.example.com/trails/\(.$id)"
    }
}
```

If your intent conforms to `URLRepresentableIntent` AND opens its parameter, **you don't even need to write a `perform()` method** -- App Intents calls your existing universal-link handler.

### 6.5 UnionValue -- Sum Types as Parameters

```swift
@UnionValue enum DayPassType {
    case trail(TrailEntity)
    case park(ParkEntity)
}
```

Each case must have **exactly one** associated value, and each value type must be **distinct**. (WWDC24-10134)

### 6.6 Two Quality-of-Life Improvements

1. `@Parameter` no longer requires a `title:` argument in Xcode 16 -- inferred from property name.
2. App Intents and Entities can now live in **frameworks** (not libraries) and be referenced by app/extension targets.

---

## 7. Assistant Schemas -- The Apple Intelligence Bridge (WWDC24-10133)

### 7.1 What They Are

> "Apple Intelligence is powered by foundation models that give Siri new capabilities... These models are trained to expect an intent with a particular shape. This shape is what we call a schema." (WWDC24-10133)

Twelve App Intent **domains** (Mail, Photos, Books, Camera, Spreadsheets, etc.) with 100+ pre-trained schema shapes. Conforming your intent to a schema gives the LLM the ability to call it from natural language with no per-developer training.

### 7.2 The Macro-Based API

```swift
@AssistantIntent(schema: .photos.openAsset)
struct OpenAssetIntent: AppIntent {
    @Parameter var target: AssetEntity
    func perform() async throws -> some IntentResult { ... }
}

@AssistantEntity(schema: .photos.asset)
struct AssetEntity: AppEntity { ... }

@AssistantEnum(schema: .photos.assetType)
enum AssetType: AppEnum { ... }
```

The compiler validates that your intent matches the trained schema's shape -- if your entity is missing `hasSuggestedEdits`, build fails. **You can extend schemas with optional parameters** for app-specific behavior.

### 7.3 Testing Today, Siri Tomorrow

> "In the future, the same intents will automatically work with Siri. Shortcuts App is a great way for you to test Assistant Schemas today." (WWDC24-10133)

Schema-conforming intents appear in Shortcuts immediately. The full Siri/Apple Intelligence path will activate in subsequent OS updates.

### 7.4 In-App Search via `ShowInAppSearchResultsIntent`

Conform to the `system.search` schema and Siri can route "Find bicycles in Trails" directly to your search results UI.

---

## 8. Core ML 2024 -- MLTensor, States, Multi-Function (WWDC24-10161)

### 8.1 MLTensor -- The "Glue Code" Replacement

A new type for the math/transformation operations between models in a pipeline. Resembles NumPy/PyTorch APIs:

```swift
let mask = (logits > logits.mean())
let filtered = logits * mask
let topK = filtered.topK(k: 5).indices
```

**Performance note:** All MLTensor operations are dispatched **asynchronously**. You must explicitly `materialize()` to `MLShapedArray` to read scalar data. This avoids accidental synchronous waits in pipeline code.

### 8.2 Hidden Speed Boost in iOS 18

> "When comparing the relative prediction time between iOS 17 and 18, you'll observe that iOS 18 is faster across many of your models. This speed-up comes with the OS and doesn't require recompiling your models or changing any of your code." (WWDC24-10161)

### 8.3 Stateful Models + KV-Cache (WWDC24-10161)

Core ML now natively supports model state. For LLMs, this means the **KV cache** can live as model state instead of being passed input→output every step:

```swift
let state = model.makeState()  // Core ML pre-allocates buffers
let result = try await model.prediction(from: input, using: state)
```

**Result:** A 1.6x speedup on Mistral 7B on M3 Max for token generation. Support must be added during the model preparation phase.

### 8.4 Multi-Function Models

A single Core ML model file can now expose multiple functions. The use case: a base diffusion model with multiple style adapters merged together, exposing "sticker" and "storybook" functions:

```swift
let config = MLModelConfiguration()
config.functionName = "sticker"
let model = try await MLModel.load(from: url, configuration: config)
```

Replaces the prior pattern of shipping N specialized model files OR passing adapter weights as inputs.

### 8.5 New Performance Tools

- Performance Report now shows **per-operation estimated time** + per-operation compute device support
- Hover over an unsupported op to see *why* (e.g., "data type not supported")
- Reports can be **exported and compared** between runs (no code needed for A/B model changes)
- New `MLComputePlan` API for the same info programmatically

---

## 9. Create ML 2024 (WWDC24-10183)

### 9.1 Object Tracking for visionOS -- The Headline

A new **Spatial Category** template builds object trackers for visionOS from just a 3D asset of your object. The Create ML app generates training data automatically. (Companion video: WWDC24-10101 "Explore object tracking for visionOS".)

### 9.2 Time Series -- Two New Components

- **Time series classification** (general purpose, replaces specialized activity classifier for many cases)
- **Time series forecasting** (NEW) -- predict future values from historical data

The forecaster is generic over data type -- works for sales, accelerometer, audio, weather.

### 9.3 The DateFeatureExtractor

```swift
let extractor = DateFeatureExtractor(featureComponents: [.month, .weekday])
```

Crucial for forecasting: extracts cyclical date features (day-of-week, month-of-year) so the model learns weekly/annual patterns. The donut-truck-vs-ice-cream-truck example illustrates why -- weekday vs. weekend matters differently per business.

### 9.4 Annotation Explorer

Click a class label in your data source to **visualize all bounding boxes/labels for that class**. Catches the "coffee cup vs. coffee surface" duplicate-prediction class of bug before training.

---

## 10. Vision Framework Swift API (WWDC24-10163)

### 10.1 The Modern API

The Vision framework is rewritten with a Swift-first API for iOS 18:

```swift
let request = DetectFaceRectanglesRequest()
let observations = try await request.perform(on: image)
```

Async/await, Swift 6 concurrency-safe, `Result`-style returns. Old `VNRequest` + `VNRequestHandler` API is still available but the Swift API is preferred.

### 10.2 New Capabilities

- **Hand pose** (added to body pose requests)
- **Aesthetic score** (new request type -- rate image quality / interestingness)
- Improved text recognition for documents (also covered in WWDC24-10103-related sessions)

---

## 11. ML Beyond Core ML

### 11.1 BNNS Graph -- CPU Real-Time (WWDC24-10211)

Replaces the older kernel-based BNNS API. Designed for:
- Audio processing where you need strict latency bounds
- Real-time signal processing with controlled memory allocation
- Use cases where Neural Engine wakeups would add latency you can't afford

Works with Core ML model files but executes purely on CPU.

### 11.2 Metal MPS Graph (WWDC24-10218)

For sequencing ML with custom Metal graphics workloads (game engines, custom renderers). New strided ND-array API for Fourier transforms; new MPS Graph viewer for understanding execution.

### 11.3 Train on Apple GPUs (WWDC24-10160)

PyTorch, TensorFlow, JAX, and MLX all use Metal under the hood for training. New mixed-precision support in JAX; improved scaled dot-product attention for transformers; custom Metal operation support in PyTorch.

---

## 12. Cross-References & Watch Order

For App Intents adoption (mandatory reading):
1. **WWDC24-10210** (Bring core features) -- the foundational session
2. **WWDC24-10134** (What's new in App Intents) -- 2024 improvements
3. **WWDC24-10133** (Bring app to Siri) -- the Apple Intelligence connection
4. **WWDC24-10176** (Design App Intents) -- design principles

For Apple Intelligence integration:
1. **WWDC24-10168** (Writing Tools) -- free win, do it first
2. **WWDC24-10220** (Genmoji) -- if your app does rich text
3. **WWDC24-10133** (App Intents → Siri) -- the strategic investment

For ML/Core ML:
1. **WWDC24-10223** (Explore ML overview) -- the map
2. **WWDC24-10161** (Core ML deploy) -- on-device deployment
3. **WWDC24-10159** (Bring models to Apple silicon) -- conversion + optimization
4. **WWDC24-10183** (Create ML) -- if you don't have a model yet
