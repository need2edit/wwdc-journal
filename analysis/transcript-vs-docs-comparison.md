# WWDC 2025 Transcripts vs. Official Apple Documentation

A systematic comparison of what Apple engineers said in sessions versus what the official DocC documentation contains. Discrepancies, hidden context, and transcript-only insights are highlighted.

---

## 1. Swift 6.2 Concurrency: MainActor Default & @concurrent

### What the Transcripts Say (WWDC25-245, 268, 270, 266)
- **Async functions no longer eagerly offload** — "Instead of eagerly offloading async functions that aren't tied to a specific actor, the function will continue to run on the actor it was called from" (WWDC25-245)
- `@concurrent` is the explicit opt-in to background execution
- Two build settings recommended: "Approachable Concurrency" + "Default Actor Isolation = MainActor"
- For **libraries**: prefer `nonisolated` over `@concurrent` — let the caller decide (WWDC25-268)
- Observable models don't need `@MainActor` annotation when main actor mode is on (WWDC25-266)

### What the Docs Say
- Build settings `SWIFT_APPROACHABLE_CONCURRENCY` and `SWIFT_DEFAULT_ACTOR_ISOLATION` are documented
- `SWIFT_UPCOMING_FEATURE_NONISOLATED_NONSENDING_BY_DEFAULT` exists: "Runs nonisolated async functions on the caller's actor by default unless the function is explicitly marked `@concurrent`"
- The "Improving app responsiveness" guide still discusses the OLD behavior where nonisolated async functions hop off the main actor

### Delta: Transcript-Only Insights
- **The docs don't clearly explain the behavioral shift** — the responsiveness guide still describes Swift 5.7+ behavior where nonisolated async functions run on the concurrent pool. The transcript explicitly calls this a breaking conceptual change.
- **Library vs. app guidance** is transcript-only — the docs don't distinguish when to use `@concurrent` vs `nonisolated`
- **Observable model inference** under main actor mode is not documented
- **Migration decision tree** (3 strategies for moving code off main actor) is transcript-only

---

## 2. Liquid Glass

### What the Transcripts Say (WWDC25-219, 323, 284, 310, 356)
- Two variants: **Regular** (for interactive controls) and **Clear** (for non-interactive/decorative)
- **Concentricity** design principle: glass elements should be concentric/nested, not overlapping
- Scroll edge effects: glass elements change appearance at scroll edges
- Migration urgency: apps will look outdated without adoption
- `GlassEffectContainer` for managing groups of glass elements

### What the Docs Say
- `Glass` struct, `glassEffect(_:in:)` modifier, `GlassEffectContainer` all fully documented
- "Adopting Liquid Glass" guide covers the visual refresh comprehensively
- Materials HIG section discusses Liquid Glass as a "distinct functional layer"
- Full code examples for applying and configuring effects

### Delta: Docs Are Strong Here
- The docs are **comprehensive** — most transcript content is also in the docs
- **Transcript-only**: The urgency/motivation ("your app will look outdated") and the design philosophy behind concentricity are richer in the sessions
- **Transcript-only**: Specific migration tips for existing apps (e.g., handling custom toolbar appearances that conflict with glass)
- The docs DON'T mention specific **performance implications** of overusing glass effects that the transcripts hint at

---

## 3. Foundation Models Framework

### What the Transcripts Say (WWDC25-286, 301, 259, 248)
- ~3B parameter on-device LLM, zero cost, no API keys, offline
- `@Generable` macro with constrained decoding is the central pattern
- **Property declaration order matters** for streaming UX AND output quality — summaries should be last (WWDC25-301)
- `includeSchemaInPrompt = false` saves hundreds of tokens when examples provided (WWDC25-301)
- `session.prewarm()` can eliminate asset loading latency (WWDC25-301)
- Tool calling with `@Tool` protocol for runtime data fetching
- Guardrails system for content safety

### What the Docs Say
- `LanguageModelSession`, `SystemLanguageModel`, `@Generable`, `Tool` protocol all documented
- `prewarm(promptPrefix:)` IS documented with optimization guidance and code examples
- `includeSchemaInPrompt` IS documented in the "Analyzing runtime performance" guide with before/after token count comparisons
- "Evaluating prompts" guide covers systematic testing (NOT in transcripts)
- TN3193 covers context window management (referenced but not detailed in transcripts)
- "Improving the safety of generative model output" guide exists

### Delta: Key Differences
- **Property declaration order affecting quality**: The transcript says summaries should be the LAST property in a `@Generable` struct. The docs don't mention this — they discuss property order only in terms of the schema structure, not as a quality optimization.
- **Model size (~3B parameters)**: Mentioned in transcripts, NOT in official docs
- **Streaming behavior details**: Transcripts explain HOW streaming interleaves with constrained decoding; docs just show the streaming API
- **Docs have MORE on prompt evaluation**: The docs include a comprehensive evaluation framework for systematically testing prompts that isn't covered in the sessions
- **Docs have MORE on context window management**: TN3193 provides detailed guidance on splitting tasks across sessions

---

## 4. UIScene Lifecycle — Mandatory Migration

### What the Transcripts Say (WWDC25-243)
- UIScene lifecycle adoption is **MANDATORY** in the release following iOS 26
- Apps that don't adopt it will not launch
- `updateProperties()` is the new recommended lifecycle method
- Automatic observation tracking for UIKit views

### What the Docs Say
- TN3187 "Migrating to the UIKit scene-based life cycle" exists as a detailed migration guide
- The docs say "In iOS 13 and later, use UISceneDelegate" but describe it as **opt-in** ("Scene support is an opt-in feature")
- No mention of it becoming mandatory or apps failing to launch
- The UIApplicationDelegate lifecycle section header says "Life-cycle management in iOS 12 and earlier"

### Delta: Critical Discrepancy
- **The transcript makes a much stronger claim than the docs.** The docs still describe scene support as opt-in. The transcript says it will be mandatory. This is the single most urgent finding in the entire analysis — developers relying solely on docs would miss this deadline.
- `updateProperties()` and automatic observation tracking are not yet in the main DocC documentation for UIKit

---

## 5. New Frameworks

### AlarmKit
- **Transcript** (WWDC25-230): Live Activity integration, snooze, repeating schedules
- **Docs**: Fully documented with sample code, `AlarmManager`, `AlarmAttributes`, widget extension guidance
- **Delta**: Docs are comprehensive — transcript adds motivational context but no missing API details

### EnergyKit
- **Transcript** (WWDC25-257): Home electricity optimization, rate plans, device scheduling
- **Docs**: Framework documented, entitlement requirement, error types
- **Delta**: Docs cover the entitlement setup; transcript provides richer use-case scenarios

### PaperKit
- **Transcript** (WWDC25-285): Markup framework built on PencilKit
- **Docs**: Fully documented with "Getting started with PaperKit" guide, `PaperMarkupViewController`, integration alongside PencilKit
- **Delta**: Docs are strong — include integration patterns not detailed in the transcript

### PermissionKit
- **Transcript** (WWDC25-293): Parent-child communication approval for child safety
- **Docs**: Needs further verification — may be under ChildSafety or FamilyControls umbrella
- **Delta**: Transcript provides the design philosophy (permission as a feature, not a gate)

### SpeechAnalyzer
- **Transcript** (WWDC25-277): Advanced speech-to-text with real-time analysis
- **Docs**: Framework likely documented under the Speech framework updates
- **Delta**: Transcript provides architecture guidance (when to use SpeechAnalyzer vs. SFSpeechRecognizer)

---

## 6. SwiftData Class Inheritance

### What the Transcripts Say (WWDC25-291)
- Class inheritance now supported via `@Model` macro
- Deep queries (base + subclass) vs. shallow queries (specific subclass only)
- When to use inheritance vs. enums vs. separate models
- Query performance: avoid deep queries when you only need subclass data

### What the Docs Say
- "Adopting inheritance in SwiftData" is a comprehensive guide
- Includes the SAME deep/shallow query guidance with identical terminology
- Code examples for Trip/BusinessTrip/PersonalTrip hierarchy
- `@available(iOS 26, *)` on subclass models

### Delta: Well-Aligned
- This is one of the **best-aligned** areas — docs and transcripts tell the same story
- **Transcript-only**: The specific performance benchmarks and "when inheritance is overkill" heuristics are richer in the session
- **Docs-only**: The docs include the `Schema.Entity` inheritance chain configuration that isn't in the transcript

---

## 7. SwiftUI Performance Claims

### What the Transcripts Say (WWDC25-306, 256)
- SwiftUI Lists are **6x faster** for large data sets
- ForEach initialization is **16x faster**
- New SwiftUI Instrument with cause-and-effect graphs
- `@Animatable` macro replaces `AnimatableModifier`

### What the Docs Say
- No specific performance multiplier claims in the docs
- The Instruments documentation covers profiling but not the specific SwiftUI Instrument improvements
- `@Animatable` macro is not prominently documented yet

### Delta: Numbers Are Transcript-Only
- **Performance claims (6x, 16x)** are exclusively in the transcripts — docs never make these specific claims
- This matters because developers evaluating whether to adopt new APIs often need performance justification
- The new SwiftUI Instrument's cause-and-effect visualization is transcript-only

---

## Summary: Where to Look for What

| Information Type | Best Source |
|---|---|
| API reference, signatures, conformances | Official Docs |
| Migration urgency, deadlines, breaking changes | Transcripts |
| Performance numbers and benchmarks | Transcripts |
| Design philosophy and "why" decisions | Transcripts |
| Code examples and integration patterns | Both (docs often better) |
| Evaluation/testing frameworks | Docs |
| Hidden optimization tips | Transcripts |
| Deprecation timelines | Transcripts |
| Context window management | Docs (TN3193) |

---

## Top 10 Transcript-Only Insights Not in Docs

1. **UIScene lifecycle is mandatory post-iOS 26** — apps will not launch without it
2. **Property declaration order in @Generable** affects Foundation Models output quality
3. **Data.dropFirst() is O(n)** — use Slice or Span instead (WWDC25-312)
4. **SwiftUI List 6x / ForEach 16x performance gains** — specific numbers
5. **Library vs. app guidance for @concurrent** — libraries should prefer nonisolated
6. **Observable model isolation inference** under main actor mode
7. **SwiftUI's `visualEffect` runs on background threads** — avoid main-actor state access
8. **Eytzinger layout** for cache-friendly binary search (WWDC25-312)
9. **SceneKit is officially soft-deprecated** — RealityKit is the path forward
10. **Background Assets replaces On-Demand Resources** with 200GB Apple hosting
