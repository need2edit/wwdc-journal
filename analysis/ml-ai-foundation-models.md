# WWDC25 Deep Analysis: Machine Learning, AI, Foundation Models, and App Intents

> Comprehensive engineering analysis of 16 WWDC25 sessions covering on-device AI, the Foundation Models framework, App Intents integration, MLX, and supporting ML frameworks.

---

## Table of Contents

1. [Foundation Models Framework](#foundation-models-framework)
2. [Prompt Design and Safety](#prompt-design-and-safety)
3. [App Intents Integration](#app-intents-integration)
4. [Writing Tools](#writing-tools)
5. [On-Device ML Frameworks](#on-device-ml-frameworks)
6. [MLX for Apple Silicon](#mlx-for-apple-silicon)
7. [Metal 4 Machine Learning](#metal-4-machine-learning)
8. [Cross-Session Themes](#cross-session-themes)

---

## Foundation Models Framework

*Sources: WWDC25-286, WWDC25-301, WWDC25-259, WWDC25-248, WWDC25-360*

### Core Architecture

The Foundation Models framework provides programmatic access to an on-device ~3 billion parameter LLM, the same model powering Apple Intelligence features like Writing Tools. It runs on macOS, iOS, iPadOS, and visionOS.

**Key characteristics (WWDC25-286, WWDC25-248):**
- Entirely on-device: no API keys, no accounts, no cost per request, works offline
- Model is embedded in the OS -- does not increase app size
- Optimized for: summarization, extraction, classification, text composition, text revision, tag generation
- NOT optimized for: complex math, code generation, or tasks requiring extensive world knowledge
- The model's training data is fixed in time and does not contain recent events

### Best Practices

#### Guided Generation is Foundational

The `@Generable` macro and `@Guide` annotation are the most important APIs in the framework. They use **constrained decoding** to guarantee structural correctness of output (WWDC25-286).

```swift
@Generable
struct NPC {
    @Guide(description: "A full name")
    let name: String
    @Guide(.range(1...10))
    let level: Int
    @Guide(.count(3))
    let attributes: [Attribute]
}
```

**Why it matters (WWDC25-286):** "Guided generation fundamentally guarantees structural correctness using a technique called constrained decoding. Your prompts can be simpler and focused on desired behavior instead of the format. Additionally, Guided Generation tends to improve model accuracy. And, it allows us to perform optimizations that speed up inference at the same time."

#### Property Declaration Order Affects Quality (WWDC25-286)

**Hidden gem:** Properties are generated in the order they are declared on your Swift struct. This matters both for animations (what appears first during streaming) and for output quality. Place summary or conclusion fields last -- "the model produces the best summaries when they're the last property in the struct."

```swift
@Generable struct Itinerary {
    @Guide(description: "Plans for each day")
    var days: [DayPlan]
    @Guide(description: "A brief summary of plans")
    var summary: String  // Last = better quality summaries
}
```

#### Snapshot Streaming, Not Delta Streaming (WWDC25-286)

The framework streams **snapshots** (partially generated `PartiallyGenerated` types with optional properties), not raw token deltas. This is a deliberate design choice for structured output.

```swift
let stream = session.streamResponse(to: prompt, generating: Itinerary.self)
for try await partial in stream {
    self.itinerary = partial  // Each partial is a full snapshot
}
```

**Best practices for streaming (WWDC25-286):**
- Get creative with SwiftUI animations and transitions to hide latency
- Think carefully about view identity, especially when generating arrays
- `PartiallyGenerable` types are automatically `Identifiable` -- no manual ID management needed

#### Session Management (WWDC25-301)

Sessions are stateful and record all prompts/responses in a **transcript**:
- The `transcript` property allows inspecting previous interactions
- While the model is responding, `isResponding` becomes true -- do not submit another prompt until done
- Sessions have a **context limit**; when nearing it, create a new session and carry over condensed transcript entries

**Carrying over context to a new session (WWDC25-301):**
```swift
func continueSession(_ session: LanguageModelSession) -> LanguageModelSession {
    var condensedEntries = [Transcript.Entry]()
    if let firstEntry = session.transcript.entries.first {
        condensedEntries.append(firstEntry) // Always include instructions
    }
    if let lastEntry = session.transcript.entries.last {
        condensedEntries.append(lastEntry)
    }
    return LanguageModelSession(transcript: Transcript(entries: condensedEntries))
}
```

**Hidden gem (WWDC25-301):** You can summarize parts of the transcript with Foundation Models itself to condense context more intelligently.

#### Sampling Control (WWDC25-301)

Generation is non-deterministic by default. You can control this:

```swift
// Deterministic output
let response = try await session.respond(to: prompt, options: GenerationOptions(sampling: .greedy))

// Low-variance
let response = try await session.respond(to: prompt, options: GenerationOptions(temperature: 0.5))

// High-variance
let response = try await session.respond(to: prompt, options: GenerationOptions(temperature: 2.0))
```

#### Instructions vs. Prompts (WWDC25-286, WWDC25-248)

Critical distinction:
- **Instructions** come from the developer, set at session creation
- **Prompts** can come from the user
- The model is trained to **obey instructions over prompts** -- this helps protect against prompt injection but is not bulletproof
- Never interpolate untrusted user input into instructions
- Reasonable default instructions are used if you don't specify any

#### Regex Guides for Constrained String Output (WWDC25-301)

**Hidden gem:** You can use Swift's `Regex` builder to constrain string generation:

```swift
@Generable
struct NPC {
    @Guide(Regex {
        Capture { ChoiceOf { "Mr"; "Mrs" } }
        ". "
        OneOrMore(.word)
    })
    let name: String
}
// Generates: {name: "Mrs. Brewster"}
```

#### Dynamic Schemas at Runtime (WWDC25-301)

For use cases like level editors or user-configurable content, you can define generation schemas dynamically using `DynamicGenerationSchema`:

```swift
let riddleDynamicSchema = riddleBuilder.root
let schema = try GenerationSchema(root: riddleDynamicSchema, dependencies: [answerDynamicSchema])
let response = try await session.respond(to: "Generate a riddle", schema: schema)
let question = try response.content.value(String.self, forProperty: "question")
```

#### Generable Enum Support (WWDC25-301)

Enums with associated values can be `@Generable`, enabling the model to choose between different encounter types or data shapes:

```swift
@Generable
enum Encounter {
    case orderCoffee(String)
    case wantToTalkToManager(complaint: String)
}
```

### Tool Calling

Tools let the model execute code you define, enabling access to external data, actions, and source-of-truth citing (WWDC25-286, WWDC25-301, WWDC25-259).

**Key architecture points:**
- Tool arguments must be `@Generable` because tool calling is built on guided generation -- the model cannot produce invalid tool names or arguments
- Tools must be attached at session initialization and are available for the session's lifetime
- The framework automatically calls tools and inserts results back into the transcript
- Tools can be stateful (use `class` instead of `struct`) to track state across calls (WWDC25-301)

**Tool calling suppresses hallucinations (WWDC25-286):** "This gives the model the ability to cite sources of truth, which can suppress hallucinations and allow fact-checking the model output."

**Hidden gem (WWDC25-301):** Tools can also be fully dynamic -- you can define arguments and behaviors at runtime using dynamic generation schemas.

### Content Tagging Adapter (WWDC25-286)

A specialized adapter providing first-class support for:
- Tag generation
- Entity extraction
- Topic detection

By default outputs topic tags. With custom instructions and Generable output types, it can also detect actions and emotions.

### Performance Optimization

#### Prewarming (WWDC25-259)

The on-device model is managed by the OS and may not be in memory. Prewarming loads the model before the user makes a request:
- Best done when user gives a strong hint they'll use the session (e.g., tapping on a landmark before hitting "Generate")
- Call prewarm while the app is relatively idle

#### IncludeSchemaInPrompt Optimization (WWDC25-259)

Setting `IncludeSchemaInPrompt` to `false` avoids inserting generation schemas into prompts, reducing token count and latency.

**When to use:**
1. Subsequent same-type requests on a multi-turn session (first request already provided schema)
2. When instructions include a full example of the schema with **all optional properties both populated and nil**

**Trade-off:** You lose `@Guide` descriptions, but a thorough example compensates.

#### Foundation Models Instrument (WWDC25-259)

New Instruments template for profiling:
- Asset Loading track: time to load models
- Inference track: generation time
- Tool Calling track: time in tool calls
- Input token count: proportionate to instruction + prompt sizes

**Important (WWDC25-259):** Profile on a physical device. Simulators on powerful Macs may produce misleadingly fast results.

### Availability Handling (WWDC25-259, WWDC25-286)

Always check model availability before creating features:

```swift
let model = SystemLanguageModel.default
switch model.availability {
case .available: // proceed
case .unavailable(let reason): // handle reason
}
```

Three unavailability reasons:
1. Device not eligible for Apple Intelligence -- hide the feature entirely
2. Apple Intelligence not enabled -- inform user they can opt in
3. Model not ready (downloading) -- tell user to try again later

**Testing trick (WWDC25-259):** Use Xcode scheme settings to override Foundation Models availability without disabling Apple Intelligence on your device.

### Error Handling (WWDC25-286, WWDC25-301)

Handle these errors appropriately:
- `GuardrailViolation`: safety guardrail triggered
- `UnsupportedLanguageOrLocale`: language not supported
- `ContextWindowExceeded`: too much context

### Language Support (WWDC25-301)

```swift
let supportedLanguages = SystemLanguageModel.default.supportedLanguages
guard supportedLanguages.contains(Locale.current.language) else {
    // Show message
    return
}
```

You can write prompts in any language supported by Apple Intelligence.

### Xcode Playgrounds for Prompt Iteration (WWDC25-259, WWDC25-286, WWDC25-248)

Use `#Playground` in any Swift file to iterate on prompts with live feedback:

```swift
import FoundationModels
import Playgrounds

#Playground {
    let session = LanguageModelSession()
    let response = try await session.respond(to: "What's a good name for a trip to Japan?")
}
```

Playgrounds can access all types in your project, including `@Generable` types. This avoids the rebuild-rerun cycle.

### Custom Adapter Training (WWDC25-286)

For ML practitioners with specialized use cases, Apple provides an adapter training toolkit. **Important caveat:** You need to retrain adapters as Apple improves the base model over time.

### Feedback Mechanism (WWDC25-286)

An encodable `FeedbackAttachment` data structure can be attached to Feedback Assistant reports to help Apple improve models and APIs.

---

## Prompt Design and Safety

*Source: WWDC25-248*

### Design for the On-Device Model

The on-device model is ~3 billion parameters. Key limitations:
- Tasks that work with large server-side LLMs may not work as-is -- break complex reasoning into simpler steps
- Avoid using it as a calculator -- use non-AI code for math
- Not optimized for code generation
- Limited world knowledge with a fixed training date
- May hallucinate on facts it doesn't know

**Hidden gem (WWDC25-248):** "For knowledge the model doesn't know, it may hallucinate. In places like instructions where facts are critical, don't risk hallucinations misleading people." However, for creative/game contexts, hallucinations can be acceptable -- "a weird bagel flavor might be funny in a game rather than misleading."

### Prompting Best Practices

1. **Control output length** with phrases like "in three sentences," "in a few words," or "in detail"
2. **Specify a role** to control style and voice (e.g., "You are a fox who speaks Shakespearean English")
3. **Phrase prompts as clear commands** -- single specific task in detail
4. **Provide fewer than 5 examples** of desired outputs directly in the prompt
5. **Use ALL CAPS "DO NOT"** to suppress unwanted behavior -- "kind of like talking to it in a stern voice"

### Safety Architecture: Swiss Cheese Model (WWDC25-248)

Safety is layered like Swiss cheese slices -- problems only occur when holes in all layers align:

1. **Built-in guardrails** (Apple-provided): Block harmful inputs and outputs automatically
2. **Safety instructions**: Write instructions that handle edge cases empathetically
3. **Prompt design**: Control how user input enters prompts
4. **Use-case mitigations**: App-specific safeguards (e.g., allergen warnings, deny lists, classifiers)

### Handling Guardrail Errors (WWDC25-248)

```swift
do {
    let response = try await session.respond(to: prompt)
} catch {
    // Handle guardrail violation
}
```

**For proactive features:** Simply ignore the error and don't interrupt the UI.
**For user-initiated features:** Provide appropriate UI feedback. Image Playground provides a good pattern -- offering an "undo" for the prompt that caused the error.

### User Input Patterns (Safest to Riskiest) (WWDC25-248)

1. **Built-in prompts** -- developer provides curated prompt list (most control, least flexibility)
2. **Combined prompts** -- developer prompt + user input
3. **Direct user input** -- user input goes directly as prompt (most flexible, most risky)

**Critical rule (WWDC25-248):** "Make sure the instructions only come from you and never include untrusted content or user input. Instead, include user input in your prompts."

### Evaluation and Testing (WWDC25-248)

1. Curate datasets for both **quality** and **safety** (include prompts that may trigger safety issues)
2. Create a dedicated command-line tool or UI tester app for automation
3. For small datasets: manual inspection
4. For large datasets: use another LLM to automatically grade responses
5. Test the unhappy path (safety errors) to ensure proper UI behavior
6. Track improvements/regressions over time as prompts and models are updated
7. Report safety issues through Feedback Assistant

### Safety Checklist (WWDC25-248)

- Handle guardrail errors when prompting the model
- Include safety considerations in instructions
- Balance flexibility and safety when including user input in prompts
- Anticipate impact when people use intelligence features; apply use-case-specific mitigations
- Invest in evaluation and testing
- Report safety issues via Feedback Assistant

---

## App Intents Integration

*Sources: WWDC25-244, WWDC25-275, WWDC25-260*

### Core Concepts (WWDC25-244)

App Intents is the framework for extending app functionality across the system -- Spotlight, Siri, Shortcuts, Action Button, Widgets, Control Center, Apple Pencil Pro.

**Building blocks:**
- **Intents** = actions/verbs (require title + perform method)
- **Entities** = nouns (dynamic types like landmarks, events)
- **Queries** = how the system reasons about entities
- **App Shortcuts** = curated entry points surfaced in Spotlight, Siri, etc.

### Key New Features for 2025

#### Interactive Snippets (WWDC25-275)

New `SnippetIntent` protocol renders interactive views with buttons/toggles that trigger other App Intents:

```swift
struct LandmarkSnippetIntent: SnippetIntent {
    @Parameter var landmark: LandmarkEntity
    
    func perform() async throws -> some IntentResult & ShowsSnippetView {
        return .result(view: LandmarkView(landmark: landmark, isFavorite: isFavorite))
    }
}
```

Snippets can be refreshed with `SnippetIntent.reload()` and used for both result display and confirmation dialogs.

#### Visual Intelligence Integration (WWDC25-275)

Apps can respond to camera-based image searches via `IntentValueQuery`:

```swift
struct LandmarkIntentValueQuery: IntentValueQuery {
    func values(for input: SemanticContentDescriptor) async throws -> [LandmarkEntity] {
        guard let pixelBuffer = input.pixelBuffer else { return [] }
        return try await modelData.searchLandmarks(matching: pixelBuffer)
    }
}
```

Use `@UnionValue` enum to return multiple entity types from visual search.

#### Use Model Action in Shortcuts (WWDC25-260)

New "Use Model" action in Shortcuts lets users run Apple Intelligence models in their shortcuts. Key integration points:

1. **AttributedString support**: Make your intents accept `AttributedString` for rich text from model output -- the Bear app demo shows lossless rich text transfer
2. **Entity JSON representation**: All entity properties exposed to Shortcuts are converted to JSON for the model to reason over
3. **Entity display names matter**: The name from `typeDisplayRepresentation` and `displayRepresentation` are included in the JSON sent to the model

**Hidden gem (WWDC25-260):** The Use Model action can automatically generate Boolean, Text, Dictionary, or App Entity output types. When connected to an If action expecting Boolean, the model automatically returns yes/no instead of verbose text.

#### Undoable Intents (WWDC25-275)

```swift
struct DeleteCollectionIntent: UndoableIntent {
    func perform() async throws -> some IntentResult {
        await undoManager?.registerUndo(withTarget: modelData) { modelData in
            // Restore collection...
        }
    }
}
```

#### Multiple Choice Dialogs (WWDC25-275)

```swift
let resultChoice = try await requestChoice(
    between: [.cancel, archive, delete],
    dialog: "Archive or delete?",
    view: collectionSnippetView(collection)
)
```

#### Foreground/Background Mode Control (WWDC25-275)

```swift
struct GetCrowdStatusIntent: AppIntent {
    static let supportedModes: IntentModes = [.background, .foreground(.dynamic)]
    
    func perform() async throws -> some ReturnsValue<Int> & ProvidesDialog {
        if systemContext.currentMode.canContinueInForeground {
            try await continueInForeground(alwaysConfirm: false)
        }
    }
}
```

#### Deferred Properties (WWDC25-275)

Use `@ComputedProperty` on entity properties and `@DeferredProperty` for expensive-to-compute values that are only fetched when needed.

### Spotlight on Mac (WWDC25-260)

Intents can now run directly from Spotlight on Mac. Requirements:
- Parameter summary must contain **all required parameters** without default values
- Intent must not be hidden (`isDiscoverable` must be true, `assistantOnly` must be false)
- Widget-only intents without `perform` methods won't appear

**Best practices for Spotlight:**
- Implement `suggestedEntities()` for quick parameter fill
- Support `EntityStringQuery` for type-to-search
- Separate background and foreground intents; pair them with `OpensIntent`
- Use `PredictableIntent` for suggestion-based surfacing

### Automations on Mac (WWDC25-260)

Personal automations now come to Mac with triggers like folder changes, external drives, time of day, and Bluetooth. Any intent available on macOS works in automations, including iOS apps installable on macOS.

### IndexedEntity and Spotlight Integration (WWDC25-244, WWDC25-275)

Associate entity properties with Spotlight attribute keys for automatic Find action generation:

```swift
struct LandmarkEntity: IndexedEntity {
    @Property(indexingKey: \.displayName)
    var name: String
    
    @Property(customIndexingKey: /* ... */)
    var continent: String
}
```

### On-Screen Entity Context (WWDC25-275)

Tag on-screen content using `NSUserActivity` with `appEntityIdentifier`:

```swift
.userActivity("com.landmarks.ViewingLandmark") { activity in
    activity.appEntityIdentifier = EntityIdentifier(for: landmark)
}
```

This provides context-aware suggestions in Spotlight and Visual Intelligence.

### AppIntentsPackage for Cross-Target Sharing (WWDC25-244)

Share App Intent types between app and extensions using `AppIntentsPackage`:

```swift
struct TravelTrackingPackage: AppIntentsPackage {
    static var includedPackages: [any AppIntentsPackage.Type] {
        [TravelTrackingKitPackage.self]
    }
}
```

### View Integration with .onAppIntentExecution (WWDC25-244, WWDC25-275)

```swift
NavigationStack(path: $path) { /* ... */ }
    .onAppIntentExecution(OpenLandmarkIntent.self) { intent in
        path.append(intent.target.landmark)
    }
```

---

## Writing Tools

*Source: WWDC25-265*

### New in 2025

- ChatGPT integration for content generation
- Available on visionOS
- Follow-up requests after rewriting (refine tone, style)
- Available as Shortcuts actions (proofread, rewrite, summarize)
- New coordinator API for custom text engines

### Rich Text Formatting with Presentation Intents (WWDC25-265)

**Hidden gem:** Apps supporting semantic styles (headings, tables, lists) should use the new `.presentationIntent` result option:

```swift
coordinator.preferredResultOptions = [.richText, .presentationIntent]
```

Key distinction:
- **Display attributes** (bold, italic): carry stylistic info like font sizes
- **Presentation intents** (headers, lists, code blocks): carry semantic info without concrete styles

"Even if .presentationIntent is specified, Writing Tools may still add display attributes for things like underlines, subscript, and superscript."

Your app is responsible for converting presentation intents into display attributes or internal styles.

### WritingToolsCoordinator for Custom Text Engines (WWDC25-265)

Full Writing Tools experience (in-place rewriting, animation, proofreading marks) is now possible for custom text engines:

```swift
func configureWritingTools() {
    guard NSWritingToolsCoordinator.isWritingToolsAvailable else { return }
    let coordinator = NSWritingToolsCoordinator(delegate: self)
    coordinator.preferredBehavior = .complete
    writingToolsCoordinator = coordinator
}
```

Delegate methods handle: context preparation, text replacement, preview generation for animation, proofreading marks, and state changes.

**Hidden gem (WWDC25-265):** `automaticallyInsertsWritingToolsItems` can be set to false for custom menu implementations, then use `writingToolsItems` API to get standard items with all updates for free.

### Renamed API (WWDC25-265)

"Allowed Input Options" from WWDC24 has been renamed to "Writing Tools Result Options" for clarity.

---

## On-Device ML Frameworks

### Vision Framework: RecognizeDocumentsRequest (WWDC25-272)

New structured document understanding API that goes beyond text extraction:
- Detects tables, lists, paragraphs, barcodes
- Groups text into semantic structures
- Supports 26 languages
- Integrates with new **DataDetection framework** for emails, phone numbers, URLs, dates, measurements, tracking numbers, flight numbers

```swift
let request = RecognizeDocumentsRequest()
let observations = try await request.perform(on: imageData)
let table = observations.first?.document.tables.first
for row in table.rows {
    let name = row.first?.content.text.transcript
    for data in cell.content.text.detectedData {
        switch data.match.details {
        case .emailAddress(let email): // ...
        case .phoneNumber(let phone): // ...
        }
    }
}
```

### Vision: Camera Lens Smudge Detection (WWDC25-272)

```swift
let request = DetectLensSmudgeRequest()
let observation = try await request.perform(on: image)
if observation.confidence > 0.9 { /* image likely smudged */ }
```

**Caveats:** Camera motion blur, long exposure, clouds/fog can produce false positives. Use in combination with `DetectFaceCaptureQualityRequest` or `CalculateImageAestheticScoresRequest`.

### Vision: Updated Hand Pose Model (WWDC25-272)

New model is smaller, faster, more accurate -- but joint locations differ from previous model. **Retrain existing hand pose classifiers** with the new model.

### SpeechAnalyzer (WWDC25-277)

Replaces `SFSpeechRecognizer` with a modern Swift-native API:

```swift
let transcriber = SpeechTranscriber(locale: locale, preset: .offlineTranscription)
let analyzer = SpeechAnalyzer(modules: [transcriber])
```

**Key features:**
- Entirely on-device, does not increase app size, auto-updates
- Optimized for long-form and distant audio (lectures, meetings, conversations)
- Returns `AttributedString` with `audioTimeRange` attributes for word-level timing
- Supports **volatile results** (immediate but less accurate) and **finalized results**
- Uses `AssetInventory` API for model download management

**Hidden gem (WWDC25-277):** Results text is returned as `AttributedString` with `audioTimeRange` as `CMTimeRange` on each run -- perfect for karaoke-style word highlighting during playback.

**Pattern for live transcription (WWDC25-277):**
```swift
for try await result in transcriber.results {
    if result.isFinal {
        finalizedTranscript += result.text
        volatileTranscript = ""  // Clear to prevent duplicates
    } else {
        volatileTranscript = result.text
    }
}
```

**Important:** Call `finalizeAndFinishThroughEndOfInput()` when stopping to ensure volatile results get finalized. Use `bestAvailableAudioFormat` and convert audio buffers to match.

### BNNS Graph (WWDC25-276, WWDC25-360)

New **Graph Builder** API lets developers create graphs of operations for real-time CPU-based ML tasks. Write pre/post-processing routines or small ML models that run in real time on CPU with strict latency and memory management control.

### ML Framework Landscape (WWDC25-360)

Decision framework for choosing the right tool:

| Need | Tool |
|------|------|
| Apple Intelligence UI components | ImagePlayground, Writing Tools, Genmoji |
| Programmatic on-device LLM | Foundation Models framework |
| Image/video analysis | Vision |
| Text processing | Natural Language |
| Translation | Translation framework |
| Sound recognition | Sound Analysis |
| Speech-to-text | SpeechAnalyzer |
| Deploy custom models | Core ML |
| Fine-grained ML + graphics | MPS Graph, Metal 4 |
| Real-time CPU ML | BNNS Graph |
| Research / frontier models | MLX |
| Train custom models | Create ML |

**Hidden gem (WWDC25-360):** New in Xcode -- you can now visualize the full model architecture of Core ML models and dive into details of any operation. "This brand new view helps you build a deeper understanding of the model you are working with, making debugging and performance opportunities incredibly visible."

---

## MLX for Apple Silicon

*Sources: WWDC25-315, WWDC25-298*

### What is MLX (WWDC25-315)

Open-source array framework (MIT license) purpose-built for Apple Silicon. Available in Python, Swift, C++, and C. Runs on Mac, iPhone, iPad, and Vision Pro.

### Key Differentiators

#### Unified Memory Programming Model (WWDC25-315)

Apple Silicon's unified memory means CPU and GPU share physical memory. In MLX:
- Arrays are allocated in unified memory, never need copying
- You specify the device to the **operation**, not the data
- CPU and GPU operations can run in parallel on the same buffer

```python
c = mx.add(a, b, stream=mx.gpu)
d = mx.multiply(a, b, stream=mx.cpu)  # Runs in parallel
```

#### Lazy Computation (WWDC25-315)

Operations build a computation graph; actual computation only happens when results are needed (print, convert, or explicit `mx.eval`). Benefits: graph transformations/optimizations before execution, pay only for what you use.

#### Function Transformations (WWDC25-315)

Composable transformations on functions:
```python
dfdx = mx.grad(sin)           # First derivative
d2fdx2 = mx.grad(mx.grad(sin))  # Second derivative
```

### Performance Optimization

#### mx.compile (WWDC25-315)

Fuse multiple GPU kernels into one for less memory bandwidth and overhead:
```python
@mx.compile
def compiled_gelu(x):
    return x * (1 + mx.erf(x / math.sqrt(2))) / 2
```

#### mx.fast (WWDC25-315)

Pre-optimized implementations of common ML operations:
- `mx.fast.rms_norm` -- dramatically faster than manual implementation
- `mx.fast.scaled_dot_product_attention` -- with additive, Boolean, or string masks
- Positional encodings, normalization layers

**Hidden gem (WWDC25-315):** "Replace the entire implementation with a single call to mx.fast.rms_norm. The code is simpler, the computation graph only has a single node, and the computation itself will be much faster."

#### Custom Metal Kernels (WWDC25-315)

Write custom Metal kernels with JIT compilation when `mx.fast` doesn't cover your case:
```python
kernel = mx.fast.metal_kernel(name="myexp", input_names=["inp"], output_names=["out"], source=source)
```

#### Quantization (WWDC25-315, WWDC25-298)

Built-in quantization with flexible options:
```python
quantized_weight, scales, biases = mx.quantize(weight, bits=4, group_size=32)
nn.quantize(model, bits=4, group_size=32)  # Quantize whole model
```

**Hidden gem (WWDC25-298):** Mixed-precision quantization -- keep sensitive layers (embedding, final projection) at higher precision:
```python
def mixed_quantization(layer_path, layer, model_config):
    if "lm_head" in layer_path or "embed_tokens" in layer_path:
        return {"bits": 6, "group_size": 64}
    elif hasattr(layer, "to_quantized"):
        return {"bits": 4, "group_size": 64}
    return False
```

#### Distributed Computing (WWDC25-315)

Run across multiple machines via ethernet or Thunderbolt:
```bash
mlx.launch --hosts ip1, ip2, ip3, ip4 my_script.py
```

### MLX LM for Language Models (WWDC25-298)

One-line commands for common tasks:

```bash
# Run DeepSeek
mlx_lm.chat --model mlx-community/DeepSeek-V3-0324-4bit

# Generate text
mlx_lm.generate --model "mlx-community/Mistral-7B-Instruct-v0.3-4bit" --prompt "..."

# Fine-tune with LoRA (even on quantized models!)
mlx_lm.lora --model "mlx-community/Mistral-7B-Instruct-v0.3-4bit" --train --data /path --iters 300

# Fuse adapters back into model
mlx_lm.fuse --model "..." --adapter-path "adapters" --save-path "fused-model"

# Quantize and upload
mlx_lm.convert --hf-path "mistralai/Mistral-7B-Instruct-v0.3" --quantize --q-bits 4
```

**Hidden gem (WWDC25-298):** The loaded model is a fully structured MLX neural network -- you can inspect layers, examine parameters, and do "model surgery" (layer swapping, custom routines).

### KV Cache for Multi-Turn Conversations (WWDC25-298)

```python
cache = make_prompt_cache(model)
text = generate(model, tokenizer, prompt=prompt, prompt_cache=cache)
# Each subsequent call continues from where the last left off
```

### Fine-Tuning on Device (WWDC25-298)

**Key insight:** Fine-tune locally on Mac, no cloud required, no data leaves the device. Supports both full fine-tuning and LoRA adapter training. LoRA can train on top of quantized models -- "cutting memory usage for model weights by about 3.5x."

### MLX Swift (WWDC25-298, WWDC25-315)

Full-featured Swift API with the same capabilities:

```swift
import MLX, MLXLMCommon, MLXLLM

let model = try await LLMModelFactory.shared.loadContainer(configuration: configuration)
try await model.perform { context in
    let input = try await context.processor.prepare(input: UserInput(prompt: "..."))
    let tokenStream = try generate(input: input, parameters: GenerateParameters(), context: context)
    for await part in tokenStream {
        print(part.chunk ?? "", terminator: "")
    }
}
```

Add as SPM dependency via the MLX Swift GitHub repo.

---

## Metal 4 Machine Learning

*Source: WWDC25-262*

### MTLTensor (WWDC25-262)

New multi-dimensional resource for ML data with baked-in stride and dimension information.

### MTL4MachineLearningCommandEncoder (WWDC25-262)

Run entire neural networks on the GPU timeline alongside rendering and compute:

**Workflow:**
1. Convert PyTorch model to CoreML package (`coremltools`)
2. Convert to MTLPackage (`metal-package-builder` CLI)
3. Open as `MTLLibrary`, create pipeline state
4. Encode and dispatch with `MTL4MachineLearningCommandEncoder`

**Key insight (WWDC25-262):** Uses placement heaps for intermediate storage instead of creating/releasing buffers. Query `pipeline.intermediatesHeapSize` for minimum heap size.

**Synchronization (WWDC25-262):** Use standard Metal 4 primitives (barriers, fences) with new `MTLStageMachineLearning`:
```objc
[encoder barrierAfterStages:MTLStageMachineLearning
          beforeQueueStages:MTLStageVertex
          visibilityOptions:MTL4VisibilityOptionDevice];
```

### Shader ML (WWDC25-262)

Embed neural networks directly within shaders for techniques like neural material compression (up to 50% compression vs. block-compressed formats):

```metal
#include <metal_tensor>
#include <MetalPerformancePrimitives/MetalPerformancePrimitives.h>

// Create inline tensors from sampled textures
auto inputTensor = tensor(inputs, extents<int, INPUT_WIDTH, 1>());

// Run matrix multiplication
tensor_ops::matmul2d<desc, execution_thread> op;
op.run(inputTensor, layerN, intermediateN);
```

**Metal Performance Primitives** library provides high-performance `matmul2d` and convolution operations for shaders.

**Execution groups (WWDC25-262):** If operations are divergent or have non-uniform control flow, use `execution_thread`. For uniform operations across a simdgroup/threadgroup, use larger execution groups.

### ML Network Debugger (WWDC25-262)

New Xcode tool for debugging Metal 4 ML workloads:
- Visualize network graph structure
- Inspect intermediate tensor data at any operation
- Dependency viewer for synchronization validation

**Debugging workflow demonstrated:** Captured GPU trace -> Dependency Viewer to verify synchronization -> MTLTensor viewer for input/output inspection -> ML Network Debugger to bisect operations and find the bug.

---

## Cross-Session Themes

### Privacy by Design

Every framework discussed emphasizes on-device processing:
- Foundation Models: entirely on-device, offline capable
- SpeechAnalyzer: on-device transcription
- Vision: all APIs run on-device
- MLX: fine-tune locally, data never leaves device

### The "No Extra Cost" Model

Foundation Models framework requires no API keys, accounts, or per-request costs. The model ships with the OS. This fundamentally changes the economics of adding AI features.

### Structured Output is Central

Apple's approach to LLM output is deeply integrated with Swift's type system through `@Generable`. This is philosophically different from JSON-schema approaches -- it uses constrained decoding at the token level for guaranteed structural correctness.

### Tool Calling as the Bridge

Tool calling appears across Foundation Models, App Intents, and Shortcuts as the mechanism for connecting AI capabilities to real-world data and actions. The pattern is consistent: define a tool with a name, description, and typed arguments; let the model decide when to call it.

### Cross-Session References

| Session | Recommends |
|---------|------------|
| WWDC25-286 (Meet Foundation Models) | WWDC25-301, WWDC25-259, WWDC25-248 |
| WWDC25-301 (Deep Dive Foundation Models) | WWDC25-286, WWDC25-259, WWDC25-248 |
| WWDC25-259 (Code-Along Foundation Models) | WWDC25-286, WWDC25-301, WWDC25-248, WWDC25-360 |
| WWDC25-248 (Prompt Design & Safety) | WWDC25-286 |
| WWDC25-244 (Get to Know App Intents) | WWDC25-275, WWDC25-260 |
| WWDC25-275 (Advances in App Intents) | WWDC25-244, WWDC25-260 |
| WWDC25-260 (Shortcuts and Spotlight) | Foundation session, Rich Text Code-Along |
| WWDC25-265 (Writing Tools) | WWDC24 Writing Tools session |
| WWDC25-272 (Vision Documents) | WWDC24 Vision enhancements, WWDC25-360 |
| WWDC25-277 (SpeechAnalyzer) | WWDC25-286 (Foundation Models) |
| WWDC25-262 (Metal 4 ML) | WWDC25-205 (Discover Metal 4) |
| WWDC25-315 (Get Started MLX) | WWDC25-298 |
| WWDC25-298 (MLX LLMs) | WWDC25-315 |
| WWDC25-360 (Discover ML Frameworks) | WWDC25-286, WWDC25-259, WWDC25-248, WWDC25-272, WWDC25-277, WWDC25-298, WWDC25-315 |
