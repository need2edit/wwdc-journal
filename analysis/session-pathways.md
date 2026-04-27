# WWDC 2025 Session Pathways & Prerequisite Map

Comprehensive guide to watching WWDC 2025 sessions in the most effective order, with curated learning pathways, prerequisite dependencies, and session clusters.

---

## 1. Session Prerequisites Map

The following sessions have explicit or topic-based prerequisites. Watch the listed sessions first for maximum comprehension.

### Swift & Concurrency Chain
| Session | Title | Watch First |
|---------|-------|-------------|
| 268 | Embracing Swift concurrency | 245 (What's new in Swift) |
| 270 | Code-along: Elevate an app with Swift concurrency | 245, 268 |
| 266 | Explore concurrency in SwiftUI | 268, 270 |
| 312 | Improve memory usage and performance with Swift | 245 |
| 311 | Safely mix C, C++, and Swift | 312 |
| 307 | Explore Swift and Java interoperability | 245 |
| 291 | SwiftData: Inheritance and schema migration | 256 (What's new in SwiftUI) |

### Foundation Models Chain
| Session | Title | Watch First |
|---------|-------|-------------|
| 301 | Deep dive into Foundation Models | 286 (Meet Foundation Models) |
| 259 | Code-along: Foundation Models | 286 |
| 248 | Prompt design & safety | 286 |

### Liquid Glass Chain
| Session | Title | Watch First |
|---------|-------|-------------|
| 356 | Get to know the new design system | 219 (Meet Liquid Glass) |
| 323 | Build a SwiftUI app with the new design | 219, 356 |
| 284 | Build a UIKit app with the new design | 219, 356 |
| 310 | Build an AppKit app with the new design | 219, 356 |
| 361 | Create icons with Icon Composer | 220 (New look of app icons) |

### visionOS / Spatial Computing Chain
| Session | Title | Watch First |
|---------|-------|-------------|
| 273 | Meet SwiftUI spatial layout | 317 (What's new in visionOS) |
| 274 | Better together: SwiftUI and RealityKit | 273, 317 |
| 290 | Set the scene with SwiftUI in visionOS | 317 |
| 287 | What's new in RealityKit | 317 |
| 318 | Share visionOS experiences | 317 |
| 289 | Explore spatial accessory input | 287 |
| 288 | Bring SceneKit project to RealityKit | 287 |
| 305 | Optimize custom environments | 317 |

### Immersive Video Chain
| Session | Title | Watch First |
|---------|-------|-------------|
| 296 | Support immersive video playback | 304 (Explore video experiences) |
| 403 | Apple Immersive Video technologies | 304 |
| 297 | Apple Projected Media Profile | 304 |

### Metal 4 Chain
| Session | Title | Watch First |
|---------|-------|-------------|
| 254 | Explore Metal 4 games | 205 (Discover Metal 4) |
| 211 | Go further with Metal 4 games | 205, 254 |
| 262 | Combine Metal 4 ML and graphics | 205 |

### Performance & Instruments Chain
| Session | Title | Watch First |
|---------|-------|-------------|
| 306 | Optimize SwiftUI performance with Instruments | 256 (What's new in SwiftUI) |
| 308 | Optimize CPU performance with Instruments | 312 (Memory & performance) |
| 226 | Profile and optimize power usage | 308 |

### App Intents Chain
| Session | Title | Watch First |
|---------|-------|-------------|
| 275 | Explore advances in App Intents | 244 (Get to know App Intents) |
| 260 | Develop for Shortcuts and Spotlight | 244 |
| 281 | Design interactive snippets | 244, 275 |

### UIKit Chain
| Session | Title | Watch First |
|---------|-------|-------------|
| 282 | Make your UIKit app more flexible | 243 (What's new in UIKit) |
| 284 | Build a UIKit app with the new design | 243, 356 |

### Child Safety Chain
| Session | Title | Watch First |
|---------|-------|-------------|
| 293 | Enhance child safety with PermissionKit | 299 (Deliver age-appropriate experiences) |

---

## 2. Learning Pathways

### Path 1: Swift Modernization (5.0 hours)

**For:** iOS/macOS developers adopting Swift 6.2

| Order | ID | Session | Why This Order |
|-------|-----|---------|----------------|
| 1 | 245 | What's new in Swift | **Gateway.** Overview of all Swift 6.2 changes: main actor by default, @concurrent, InlineArray, Span, Observations |
| 2 | 268 | Embracing Swift concurrency | Teaches the concurrency model introduced in 245 -- when and how to add concurrency |
| 3 | 270 | Code-along: Elevate an app with Swift concurrency | Hands-on practice applying concepts from 245 and 268 to a real app |
| 4 | 266 | Explore concurrency in SwiftUI | How SwiftUI leverages the concurrency model you just learned |
| 5 | 312 | Improve memory usage and performance with Swift | Deep dive into InlineArray, Span, and algorithmic fixes previewed in 245 |
| 6 | 291 | SwiftData: Inheritance and schema migration | New data persistence patterns using Swift's type system |

**Optional enrichment:** 311 (C/C++ interop), 307 (Java interop)

---

### Path 2: AI/ML Developer (5.5 hours)

**For:** Developers adding on-device AI features

| Order | ID | Session | Why This Order |
|-------|-----|---------|----------------|
| 1 | 360 | Discover ML & AI frameworks | **Gateway.** Decision framework for choosing the right ML tool |
| 2 | 286 | Meet the Foundation Models framework | Core API: @Generable, sessions, streaming, tool calling |
| 3 | 301 | Deep dive into Foundation Models | Advanced: regex guides, dynamic schemas, stateful tools, session management |
| 4 | 259 | Code-along: Foundation Models | Hands-on implementation with optimization techniques |
| 5 | 248 | Prompt design & safety | Critical safety layer -- Swiss cheese model, guardrail handling |

**Optional enrichment:** 265 (Writing Tools), 272 (Vision document reading), 277 (SpeechAnalyzer)

---

### Path 3: Liquid Glass Adoption (5.5 hours)

**For:** All Apple platform developers updating for the new design system

| Order | ID | Session | Why This Order |
|-------|-----|---------|----------------|
| 1 | 219 | Meet Liquid Glass | **Gateway.** Design principles: lensing, tinting, concentricity, two variants |
| 2 | 356 | Get to know the new design system | Deeper design system: scroll edge effects, component changes, best practices |
| 3 | 323 | Build a SwiftUI app with the new design | SwiftUI-specific: .glassEffect(), toolbar APIs, tab bar, search |
| 4 | 284 | Build a UIKit app with the new design | UIKit-specific: UIGlassEffect, navigation transitions, slider enhancements |
| 5 | 310 | Build an AppKit app with the new design | AppKit-specific: NSGlassEffectView, toolbar items, split view accessories |
| 6 | 220 | Say hello to the new look of app icons | New icon appearances and design |
| 7 | 361 | Create icons with Icon Composer | Practical tool for creating new icons |

**Optional enrichment:** 208 (iPad design), 337 (SF Symbols 7), 404 (UX writing)

**Note:** Watch sessions 3-5 selectively based on which frameworks you use. Most developers only need one or two of the platform-specific sessions.

---

### Path 4: Spatial Computing (6.0 hours)

**For:** visionOS developers from window-based to fully immersive apps

| Order | ID | Session | Why This Order |
|-------|-----|---------|----------------|
| 1 | 317 | What's new in visionOS 26 | **Gateway.** Platform overview: new APIs, depth alignments, scene persistence, enterprise features |
| 2 | 273 | Meet SwiftUI spatial layout | 3D layout fundamentals: depth alignments, rotation3DLayout, SpatialContainer |
| 3 | 274 | Better together: SwiftUI and RealityKit | Bridge between SwiftUI and RealityKit: Model3D, ViewAttachmentComponent, GestureComponent |
| 4 | 290 | Set the scene with SwiftUI in visionOS | Scene management: windows, volumes, immersive spaces, surface snapping |
| 5 | 287 | What's new in RealityKit | New components: ManipulationComponent, MeshInstances, ImagePresentation, environment occlusion |
| 6 | 318 | Share visionOS experiences | Nearby sharing, SharePlay, shared world anchors |
| 7 | 303 | Design hover interactions | Hover effects, Look to Scroll, media control persistence |

**Optional enrichment:** 289 (spatial accessories), 255 (widget design for visionOS), 305 (environment optimization), 288 (SceneKit migration)

---

### Path 5: Performance Mastery (4.0 hours)

**For:** Developers optimizing existing apps

| Order | ID | Session | Why This Order |
|-------|-----|---------|----------------|
| 1 | 312 | Improve memory usage and performance with Swift | **Gateway.** Algorithmic fixes first -- Data.dropFirst() pitfalls, Span, InlineArray, eliminating exclusivity checks. "Fix algorithmic issues first" |
| 2 | 306 | Optimize SwiftUI performance with Instruments | New SwiftUI Instrument: Cause & Effect graph, view body analysis, @Observable array pitfalls |
| 3 | 308 | Optimize CPU performance with Instruments | CPU Profiler, Processor Trace, CPU Counters bottleneck analysis. "This order was important" |
| 4 | 226 | Profile and optimize power usage | Power Profiler, on-device power profiling, lazy loading patterns |

**Optional enrichment:** 266 (SwiftUI concurrency), 268 (when to add concurrency)

**Key insight:** The optimization order matters -- fix algorithms before software overheads before CPU micro-optimizations.

---

### Path 6: UIKit Modernization (3.5 hours)

**For:** UIKit developers with urgent migration needs

| Order | ID | Session | Why This Order |
|-------|-----|---------|----------------|
| 1 | 243 | What's new in UIKit | **Gateway.** URGENT: UIScene lifecycle will be required in the release following iOS 26. Also covers Observable tracking, updateProperties(), scene bridging |
| 2 | 284 | Build a UIKit app with the new design | Liquid Glass adoption, navigation transitions, scroll edge effects, search changes |
| 3 | 282 | Make your UIKit app more flexible | Scene lifecycle migration, split view column resizing, inspector columns |
| 4 | 208 | Elevate the design of your iPad app | iPad-specific: tab bar morphing, menu bar, pointer shape |

**Optional enrichment:** 356 (design system overview), 219 (Liquid Glass principles)

---

### Path 7: App Intents & Intelligence (3.5 hours)

**For:** Developers integrating with Siri, Spotlight, Shortcuts, and Apple Intelligence

| Order | ID | Session | Why This Order |
|-------|-----|---------|----------------|
| 1 | 244 | Get to know App Intents | **Gateway.** Core concepts: intents, entities, queries, app shortcuts, AppIntentsPackage |
| 2 | 275 | Explore advances in App Intents | New: interactive snippets, Visual Intelligence, undoable intents, deferred properties |
| 3 | 260 | Develop for Shortcuts and Spotlight | "Use Model" action integration, Spotlight on Mac, automations |
| 4 | 281 | Design interactive snippets | Design guidelines for the new snippet UI |

**Optional enrichment:** 286 (Foundation Models for AI context), 265 (Writing Tools integration)

---

### Path 8: Immersive Video (3.5 hours)

**For:** Video app developers targeting visionOS

| Order | ID | Session | Why This Order |
|-------|-----|---------|----------------|
| 1 | 304 | Explore video experiences for visionOS | **Gateway.** Complete overview of all video profiles: 2D, 3D, spatial, APMP, Apple Immersive Video |
| 2 | 296 | Support immersive video playback | Implementation: VideoPlayerComponent, viewing modes, comfort mitigation, spatial video |
| 3 | 297 | Learn about Apple Projected Media Profile | APMP details: 180/360/wide FOV, APAC spatial audio, conversion tools |
| 4 | 403 | Learn about Apple Immersive Video technologies | AIVU format, ImmersiveMediaSupport framework, production specs |

**Optional enrichment:** 317 (visionOS overview for context)

---

### Path 9: Security & Privacy (4.0 hours)

**For:** All developers, especially those handling sensitive data

| Order | ID | Session | Why This Order |
|-------|-----|---------|----------------|
| 1 | 246 | Integrate privacy into your development process | **Gateway.** Privacy-by-design framework, data minimization, CloudKit E2E encryption, testing |
| 2 | 314 | Get ahead with quantum-secure cryptography | URGENT: TLS quantum-secure enabled by default in iOS 26. CryptoKit APIs, migration priority |
| 3 | 279 | What's new in passkeys | Account creation API, automatic upgrades, Signal APIs, import/export |
| 4 | 299 | Deliver age-appropriate experiences | Declared Age Range API, parental controls detection, caching behavior |
| 5 | 293 | Enhance child safety with PermissionKit | PermissionKit for communication limits, Family Sharing integration |

**Optional enrichment:** 232 (identity document verification), 234 (URL filtering with NetworkExtension)

---

### Path 10: Metal 4 & Games (5.5 hours)

**For:** Game developers and graphics engineers

| Order | ID | Session | Why This Order |
|-------|-----|---------|----------------|
| 1 | 205 | Discover Metal 4 | **Gateway.** Architecture overview: MTL4 command model, unified compute, residency sets, tensors |
| 2 | 254 | Explore Metal 4 games | Command encoding efficiency, resource management, pipeline loading |
| 3 | 211 | Go further with Metal 4 games | MetalFX upscaling, frame interpolation, ray tracing, denoising |
| 4 | 262 | Combine Metal 4 ML and graphics | ML command encoder, shader ML, Metal Performance Primitives, debugging |
| 5 | 209 | Level up your games | Game Mode, GameSave, Touch Controls, Background Assets, Game Porting Toolkit 3 |

**Optional enrichment:** 214 (Game Center), 215 (Apple Games app), 288 (SceneKit to RealityKit)

---

### Path 11: MLX Research & Fine-Tuning (2.0 hours)

**For:** ML engineers and researchers running models locally

| Order | ID | Session | Why This Order |
|-------|-----|---------|----------------|
| 1 | 315 | Get started with MLX | **Gateway.** Array framework fundamentals: unified memory, lazy computation, function transforms, custom kernels |
| 2 | 298 | Explore LLMs on Apple silicon with MLX | MLX LM: inference, fine-tuning with LoRA, quantization, KV cache, Swift integration |

**Optional enrichment:** 360 (ML framework landscape), 262 (Metal 4 ML)

---

### Path 12: New Developer Essentials (5.5 hours)

**For:** Developers new to Apple platforms

| Order | ID | Session | Why This Order |
|-------|-----|---------|----------------|
| 1 | 359 | Design foundations: From idea to interface | **Gateway.** Universal design principles: information architecture, tab bars, progressive disclosure |
| 2 | 256 | What's new in SwiftUI | SwiftUI overview: performance gains, new APIs, @Animatable, drag and drop, WebView |
| 3 | 247 | What's new in Xcode | Xcode 26: Playgrounds, AI integration, testing, build improvements |
| 4 | 316 | Principles of inclusive app design | Accessibility fundamentals: inclusion gap, four practical steps |
| 5 | 286 | Meet the Foundation Models framework | On-device AI: @Generable, streaming, tool calling |
| 6 | 244 | Get to know App Intents | System integration: Siri, Spotlight, Shortcuts, Action Button |

**Optional enrichment:** 225 (localization), 344 (UI automation), 224 (accessibility nutrition labels)

---

### Path 13: Accessibility Champion (3.0 hours)

**For:** Developers committed to inclusive design

| Order | ID | Session | Why This Order |
|-------|-----|---------|----------------|
| 1 | 316 | Principles of inclusive app design | **Gateway.** Framework for understanding disability spectrum, four practical steps |
| 2 | 224 | Evaluate your app for Accessibility Nutrition Labels | Feature-by-feature evaluation checklist, testing methodology |
| 3 | 229 | Make your Mac app more accessible | Mac-specific: VoiceOver containers, sort priority, rotors, keyboard shortcuts |
| 4 | 238 | Customize your app for Assistive Access | Cognitive accessibility: AssistiveAccess scene type, design principles |

**Optional enrichment:** 299 (age-appropriate experiences), 293 (child safety)

---

## 3. Session Clusters

Sessions that cover the same feature from different angles. Watch together for complete coverage.

### Liquid Glass Design System
Sessions: 219, 356, 323, 284, 310
- 219: Design principles and optical properties
- 356: Design system details (concentricity, scroll edges, components)
- 323: SwiftUI implementation
- 284: UIKit implementation
- 310: AppKit implementation

### Swift Concurrency
Sessions: 245, 268, 270, 266
- 245: Language-level changes (main actor by default, @concurrent)
- 268: Conceptual guide (when and how to add concurrency)
- 270: Hands-on code-along applying concurrency
- 266: SwiftUI-specific concurrency patterns

### Foundation Models Framework
Sessions: 286, 301, 259, 248
- 286: High-level overview (no prerequisites)
- 301: Deep dive (guided generation internals, dynamic schemas, tool calling)
- 259: Code-along with optimization techniques
- 248: Prompt design and safety architecture

### Performance & Instruments
Sessions: 306, 308, 312, 226
- 312: Swift-level memory and algorithmic optimization
- 306: SwiftUI Instrument for view body analysis
- 308: CPU Profiler, Processor Trace, CPU Counters
- 226: Power Profiler for energy impact

### Metal 4
Sessions: 205, 254, 211, 262
- 205: Architecture overview and adoption strategy
- 254: Game engine command encoding and resource management
- 211: MetalFX, ray tracing, denoising
- 262: ML command encoder and shader ML

### App Intents Ecosystem
Sessions: 244, 275, 260, 281
- 244: Core concepts ground-up
- 275: New features (snippets, Visual Intelligence, undoable)
- 260: Shortcuts, Spotlight, "Use Model" action
- 281: Design guidelines for snippets

### visionOS Scene Management
Sessions: 317, 273, 274, 290
- 317: Platform overview with all new APIs
- 273: 3D SwiftUI layout system
- 274: SwiftUI + RealityKit integration
- 290: Window, volume, and immersive space APIs

### Immersive Video
Sessions: 304, 296, 297, 403
- 304: Video profile landscape overview
- 296: Playback implementation (VideoPlayerComponent)
- 297: APMP format details
- 403: Apple Immersive Video production

### UIKit Modernization
Sessions: 243, 284, 282
- 243: What's new (Observable tracking, updateProperties, scene bridging, menu bar)
- 284: New design adoption (glass, navigation, controls)
- 282: Flexibility (scene lifecycle, split view, layout)

### App Icon Refresh
Sessions: 220, 361
- 220: Design principles for new icon appearances
- 361: Icon Composer tool walkthrough

### Child Safety & Age
Sessions: 299, 293
- 299: Declared Age Range API (privacy-preserving age detection)
- 293: PermissionKit for parental communication controls

### MLX on Apple Silicon
Sessions: 315, 298
- 315: MLX framework fundamentals
- 298: LLM-specific workflows (inference, fine-tuning, Swift API)

### Widgets & Live Activities
Sessions: 278, 334, 255
- 278: What's new across platforms (push updates, relevance, CarPlay)
- 334: watchOS 26 specifics (arm64, controls, configurable widgets)
- 255: visionOS widget design (paper/glass, mounting, proximity)

### Game Center & Games App
Sessions: 214, 215
- 214: Implementation (achievements, challenges, activities, multiplayer)
- 215: Apple Games app integration and discovery optimization

### Accessibility
Sessions: 316, 224, 229, 238
- 316: Inclusive design principles
- 224: Nutrition label evaluation
- 229: Mac-specific accessibility
- 238: Assistive Access customization

### App Store & Commerce
Sessions: 241, 249, 252, 324, 328
- 241: StoreKit client-side updates
- 249: Server API updates
- 252: Analytics and monetization optimization
- 324: App Store Connect API (webhooks, build upload)
- 328: App Store Connect UI updates

### Camera & Capture
Sessions: 253, 319, 251
- 253: Physical capture controls (AirPods, Camera Control)
- 319: Cinematic video capture API
- 251: Audio recording (input picker, spatial audio, AirPods)

### RealityKit
Sessions: 287, 288
- 287: New APIs (ManipulationComponent, MeshInstances, ImagePresentation)
- 288: SceneKit to RealityKit migration guide

---

## 4. Standalone Sessions

These sessions work well independently and do not require watching other WWDC25 sessions first.

| ID | Title | Why It Works Alone |
|----|-------|--------------------|
| 227 | Finish tasks in the background | Self-contained overview of all background APIs with decision framework |
| 346 | Meet Containerization | Independent topic -- Linux containers on Mac using Swift |
| 228 | Supercharge device connectivity with Wi-Fi Aware | New framework, no dependencies on other sessions |
| 257 | Optimize home electricity usage with EnergyKit | New standalone framework for energy-aware apps |
| 285 | Meet PaperKit | New standalone markup framework integrating PencilKit |
| 230 | Wake up to the AlarmKit API | New standalone alarms/timers framework |
| 321 | Meet the HealthKit Medications API | Self-contained API introduction |
| 322 | Track workouts with HealthKit on iOS and iPadOS | Complete workout API guide |
| 302 | Create a seamless multiview playback experience | Independent AVFoundation synchronized playback feature |
| 300 | Enhance your app with ML-based video effects | Standalone VideoToolbox processing API |
| 222 | Enhance your app's multilingual experience | Independent localization improvements |
| 204 | Go further with MapKit | Standalone MapKit updates (cycling, geocoding, PlaceDescriptor) |
| 231 | Meet WebKit for SwiftUI | New self-contained WebView API |
| 325 | Discover Apple-Hosted Background Assets | Independent asset delivery system |
| 216 | Turbocharge your app for CarPlay | CarPlay-specific updates |
| 404 | Make a big impact with small writing changes | Universal UX writing guidance |
| 359 | Design foundations from idea to interface | Universal design principles, no prerequisites |
| 280 | Code-along: Rich text with AttributedString | Self-contained TextEditor feature |
| 337 | SF Symbols 7 | New draw animations, gradients, custom annotation |
| 203 | Get to know the ManagedApp Framework | Enterprise app configuration, independent topic |
| 258 | What's new in Apple device management | MDM and identity updates, standalone for IT/enterprise |

---

## 5. Quick Reference: Estimated Watch Times by Pathway

| Pathway | Sessions | Est. Hours | Priority Level |
|---------|----------|------------|----------------|
| Swift Modernization | 6 core + 2 optional | 5.0 | High (Swift 6.2 migration) |
| AI/ML Developer | 5 core + 3 optional | 5.5 | High (new framework) |
| Liquid Glass Adoption | 7 core + 3 optional | 5.5 | High (design refresh) |
| UIKit Modernization | 4 core + 2 optional | 3.5 | URGENT (scene lifecycle deadline) |
| Performance Mastery | 4 core + 2 optional | 4.0 | High |
| Spatial Computing | 7 core + 4 optional | 6.0 | Medium-High |
| App Intents & Intelligence | 4 core + 2 optional | 3.5 | Medium-High |
| Security & Privacy | 5 core + 2 optional | 4.0 | High (quantum TLS default) |
| Metal 4 & Games | 5 core + 3 optional | 5.5 | Medium (game devs) |
| Immersive Video | 4 core + 1 optional | 3.5 | Medium (video app devs) |
| MLX Research | 2 core + 2 optional | 2.0 | Medium (ML engineers) |
| New Developer Essentials | 6 core + 3 optional | 5.5 | For newcomers |
| Accessibility Champion | 4 core + 2 optional | 3.0 | Medium-High |

**Total unique sessions across all pathways:** ~85 (of ~90 analyzed sessions)

**Recommended starting point for most iOS developers:** UIKit Modernization Path (urgent deadline) or Swift Modernization Path (foundational changes), followed by Liquid Glass Adoption Path.
