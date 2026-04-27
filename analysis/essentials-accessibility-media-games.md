# WWDC25 Deep Analysis: Essentials, Accessibility, Health, Photos/Camera, Graphics/Games, App Store, Business/Education, Maps

*Analysis of 32 WWDC25 session transcripts with engineering insights, hidden gems, and API details.*

---

## Table of Contents

1. [Platform Essentials & Design](#platform-essentials--design)
2. [Accessibility](#accessibility)
3. [Health & Fitness](#health--fitness)
4. [Photos, Camera & Audio](#photos-camera--audio)
5. [Video & Media](#video--media)
6. [Metal 4 & Graphics](#metal-4--graphics)
7. [Games & Game Center](#games--game-center)
8. [Maps](#maps)
9. [App Store & Monetization](#app-store--monetization)
10. [Business, Education & Device Management](#business-education--device-management)

---

## Platform Essentials & Design

### Platforms State of the Union (WWDC25-102)

**Key Themes:**
- Metal 4 is the headline graphics advancement, supported on M1+ and A14 Bionic+
- Foundation Models framework brings on-device AI with structured generation via `@Generable` macro
- Swift 6.2 with `defaultIsolation(MainActor)` build setting eliminates boilerplate for UI code
- Liquid Glass is the new design material across all platforms

**Hidden Gems:**
- The `@Generable` macro for Foundation Models framework automatically enables structured JSON output from on-device LLMs -- no manual parsing needed
- Swift Testing can now run tests in parallel on physical devices, not just simulators
- New `InlineData` macro in Swift Testing lets you run the same test with multiple inputs
- Xcode 26 now has a "Strict Concurrency" migration tool that automatically fixes data race issues
- SwiftUI's `customContainerContent` API lets you build custom container views that work like `List` or `TabView`

**Performance Tips:**
- Foundation Models framework uses speculative decoding for faster inference
- Metal 4's unified compute encoder reduces encoder count and memory overhead
- MetalFX frame interpolation generates intermediate frames cheaper than full renders

**Cross-references:** Discover Metal 4 (205), Meet the Foundation Models framework (286), Deep dive into Foundation Models (301)

---

### Design Foundations: From Idea to Interface (WWDC25-359)

**Best Practices:**
- Start every screen with three questions: "Where am I?", "What can I do?", "Where can I go?"
- Tab bars are for navigation, never for actions -- move primary actions like "Add" into the screen content
- Use SF Symbols for tab bar icons for platform consistency and recognition
- Apply progressive disclosure: show only a few groups upfront, hide rest behind a disclosure control

**Hidden Gems:**
- When choosing between grid and list layouts: lists take less vertical space, handle longer text better, and facilitate quick scanning
- "Information architecture" exercise: write down everything the app does, imagine usage context, remove non-essentials, rename unclear items, group related items
- Grouping content by time, seasonality, progress, or patterns reduces choice overload
- Use system text styles for hierarchy instead of custom sizes -- they automatically support Dynamic Type
- Semantic colors (like `label`, `secondarySystemBackground`) should be your primary palette; accent colors sparingly on buttons/controls

**Content Organization Strategies:**
- By time: recent files, continue watching
- By seasonality: current events
- By progress: drafts, ongoing classes
- By patterns: related products, styles, genres

**Cross-references:** Get to know the new design system (356)

---

### Make a Big Impact with Small Writing Changes (WWDC25-404)

**Four Key UX Writing Changes:**
1. **Remove fillers**: Cut unnecessary adverbs ("simply", "quickly", "easily"), adjectives, interjections ("uh oh", "oops"), and pleasantries ("we're sorry")
2. **Avoid repetition**: Don't say the same thing in different ways. Combine redundant sentences
3. **Lead with the why**: Move the benefit to the front of the sentence. "To get reservation updates, enter your phone number" beats "Enter your phone number to get reservation updates"
4. **Make a word list**: Create a table of preferred terms vs. avoided terms with definitions for consistency

**Hidden Gems:**
- "Read your writing out loud" -- makes filler words and repetition easier to hear
- Never use exclamation points to soften bad news (e.g., "10 short minutes!")
- Button labels are great candidates for your word list -- consistent labels build trust
- The Apple Style Guide is publicly available as a starting reference

**Cross-references:** Human Interface Guidelines: Writing

---

### Elevate the Design of Your iPad App (WWDC25-208)

**Best Practices:**
- Start with a tab bar if unsure about navigation -- it can morph into a sidebar later
- Tab bar morphing to sidebar is now seamless and user-controlled
- Layout changes from resizing should be **non-destructive** -- never permanently alter layout on resize
- Extend content below toolbar using the new "scroll edge effect"
- Wrap toolbar around window controls (inline placement) -- the compatibility placement above the toolbar wastes space

**API Details:**
- New `windowAssistiveAccessApplication` scene role for UIKit apps
- New pointer shape is more precise, tracks input 1:1 (no more rubber banding/magnetizing)
- New liquid glass highlight effect replaces the old pointer morphing hover effect
- Each document should open in its own window (additive windowing)
- Provide descriptive window names using document titles

**iPad Menu Bar Guidelines:**
- Order menu items by frequency, not alphabetically
- Group related actions into sections
- Never hide menu items based on context -- dim them instead (spatial memory matters)
- Populate the View menu with tab shortcuts and sidebar toggle
- Assign keyboard shortcuts to common actions

**Cross-references:** Get to know the new design system (356), Build a UIKit app with the new design (284)

---

### Design Interactive Snippets (WWDC25-281)

**Best Practices:**
- Snippets are compact App Intent views for Siri, Spotlight, and Shortcuts
- Keep content under 340 points in height -- no scrolling
- Use larger text than system defaults for glanceability
- Use `ContainerRelativeShape` API for responsive margins across platforms
- Check contrast from a distance -- vibrant backgrounds can reduce readability

**API Details:**
- Two types: **Result** snippets (outcome/info, only "Done" button) and **Confirmation** snippets (requires action before showing result)
- Snippets now support buttons and updated state information
- Data updates animate with scale and blur for visual feedback
- Confirmation button verbs can be customized or chosen from pre-written options

**Hidden Gems:**
- Challenge yourself to make snippets understandable without dialog -- removes redundancy for visual-first users
- Snippets remain until confirming, canceling, or swiping away -- great for routine tasks

**Cross-references:** Develop for Shortcuts and Spotlight with App Intents (260), Explore advances in App Intents (275)

---

### Create Icons with Icon Composer (WWDC25-361)

**Best Practices:**
- One `.icon` file now produces all platform variants (iPhone, iPad, Mac, Watch)
- Keep source art flat, opaque, and graphic -- dynamic properties (blur, shadow, specular) are added in Icon Composer
- Export layers as SVGs for scalability; use PNG for custom gradients, raster images, or non-SVG-expressible elements
- Never include the rounded rectangle or circle mask in exports
- Convert text to outlines before SVG export (SVG doesn't preserve fonts)

**Hidden Gems:**
- Separating colors into separate layers gives maximum control for dark/mono mode variants
- Icon Composer supports up to 4 groups (Z-depth layers) -- found to be the right bound for visual complexity
- System background presets are optimized for liquid glass materials
- Number layers in Z-order and they auto-sort in Icon Composer
- Simple background colors/gradients are added directly in Icon Composer, no need to export
- Watch canvas is now 1088px (vs 1024px for others), uses same grid for easy cross-platform design

**Appearance Modes:**
- Three annotation modes: Default, Dark, Mono
- Mono artwork automatically produces tinted light/dark appearances
- For mono: set at least one prominent element to white for legibility
- Chromatic shadows (color spills from artwork) look great against white backgrounds; use neutral shadows for dark mode

**Cross-references:** Say hello to the new look of app icons (220), Meet Liquid Glass (219), Get to know the new design system (356)

---

## Accessibility

### Evaluate Your App for Accessibility Nutrition Labels (WWDC25-224)

**Best Practices:**
- Define your app's "common tasks" first -- primary functionalities plus login, purchase, settings
- Test each accessibility feature against each common task on every supported device
- Only indicate support for features your app genuinely handles throughout all common tasks
- If a feature isn't relevant (e.g., Captions for an app with no audio/video), don't indicate support

**Feature Evaluation Checklist:**
1. **Sufficient Contrast**: High enough foreground/background contrast; check with Increase Contrast setting on
2. **Dark Interface**: Must work with dark mode AND Smart Invert (ensure media colors don't get inverted)
3. **Larger Text**: Text must scale to at least 200% (ideally 310%+); layout must accommodate without overlap/severe truncation
4. **Differentiate Without Color Alone**: Use shapes, icons, or text alongside color for information
5. **Reduced Motion**: Remove or adapt known triggers (zooming/sliding transitions, flashing, auto-playing animations, parallax)
6. **Voice Control**: All touch-responsive items must have accurate accessibility labels
7. **VoiceOver**: Full navigation and interaction possible with VoiceOver gestures/keyboard
8. **Captions/Audio Descriptions**: Only if app has audio/video content

**Hidden Gems:**
- Lisa's real-world perspective: "If an app is designed to support my experience as a blind person, I feel included as a valued customer"
- "Nothing about us without us" -- test with people who actually use accessibility features
- Text fields must grow to accommodate larger text sizes -- truncation or inability to scroll is a failing point
- You can always come back and add features to Nutrition Labels later after fixing issues

**API Details:**
- `.accessibilityLabel("Share")` on buttons with icon-only labels
- Use Dynamic Type for Larger Text support (see "Get Started with Dynamic Type" from WWDC24)

**Cross-references:** Get started with Dynamic Type (WWDC24), Principles of inclusive app design (316)

---

### Make Your Mac App More Accessible to Everyone (WWDC25-229)

**Best Practices:**
- Mac accessibility has unique considerations: denser UIs, keyboard/mouse interactions, nested containers
- Group related elements into containers to speed VoiceOver navigation, but avoid too many nesting levels
- If ordering doesn't feel right, use `.accessibilitySortPriority()` to reorder elements
- Any interaction requiring hover/trackpad gesture may not be accessible -- provide alternative accessibility actions
- Adding keyboard shortcuts for common tasks has a huge impact on accessibility

**API Details:**
- `.accessibilityElement(children: .contain)` -- creates a container
- `.accessibilityElement(children: .combine)` -- merges subviews into one element
- `.accessibilityElement(children: .ignore)` -- hides subviews
- `.accessibilitySortPriority(1)` -- higher priority = sorted first (default is 0)
- `.accessibilityRotor("Bookmarks")` -- custom rotor for quick navigation
- `.accessibilityDefaultFocus($focusedForVoiceOver, true)` -- new in macOS/iOS 26, suggests initial VoiceOver focus
- `.accessibilityAction(named:)` -- adds actions for hover-only interactions

**Hidden Gems:**
- VoiceOver on Mac navigates by container by default (unlike iOS which navigates linearly)
- The tree-like structure of nested containers is a key Mac accessibility concept
- Accessibility rotors are "essential" for accelerating VoiceOver navigation
- `@AccessibilityFocusState(for: .voiceOver)` is the state wrapper for programmatic VoiceOver focus

**Cross-references:** Catch up on accessibility in SwiftUI (WWDC24), SwiftUI Accessibility: Beyond the basics (WWDC21), Evaluate your app for Accessibility Nutrition Labels (224)

---

### Customize Your App for Assistive Access (WWDC25-238)

**Best Practices:**
- Assistive Access is for people with cognitive disabilities -- aims to reduce cognitive load
- Two paths: full screen (for apps already designed for cognitive disabilities like AAC apps) or the new Assistive Access scene type (for all other apps)
- Distill your app to 1-2 essential features only
- Reduce options at any given time; avoid hidden gestures or nested UI
- Avoid timed interactions -- let people complete tasks at their own pace
- Build incremental step-by-step flows rather than presenting multiple options at once
- Remove or double-confirm destructive actions (like deletion)
- Use both icons and labels for all controls and navigation links

**API Details:**
- `UISupportsFullScreenInAssistiveAccess` Info.plist key for full screen mode
- `UISupportsAssistiveAccess` Info.plist key + `AssistiveAccess` scene type for tailored experience
- `AssistiveAccess { }` scene in SwiftUI app body
- `#Preview(traits: .assistiveAccess)` for previewing in Xcode
- `.assistiveAccessNavigationIcon(systemImage:)` modifier for navigation bar icons
- For UIKit: `UIHostingSceneDelegate` with `static var rootScene` containing `AssistiveAccess` scene
- Scene role: `.windowAssistiveAccessApplication`

**Hidden Gems:**
- Native SwiftUI controls automatically get the larger, clearer Assistive Access styling when the scene is active
- Controls automatically adhere to grid or row layout (configured in Assistive Access settings)
- The Assistive Access back button handles navigation stack traversal automatically
- Consider reordering decisions to isolate each one into its own view (e.g., color selection before canvas)
- "The best source of feedback is from your audience: find opportunities to test within the Assistive Access community"

**Cross-references:** What's new in SwiftUI (256), Meet Assistive Access (WWDC23)

---

### Principles of Inclusive App Design (WWDC25-316)

**Core Framework:**
- About 1 in 7 people has a disability -- design for the spectrum
- Five categories: Vision, Hearing, Motor, Speech, Cognitive -- all are spectrums
- The "inclusion gap" = difference between what a person can do and what society (or your app) expects
- Disability is as much about the environment as the body

**Four Practical Steps:**
1. **Support multiple senses**: Provide visual, audible, and haptic alternatives for all information
2. **Provide customization**: Let people personalize UI and interactions (text size, colors, layout density)
3. **Adopt Accessibility APIs**: VoiceOver, Switch Control, Voice Control, Larger Text
4. **Track inclusion debt**: Know what gaps exist, plan to close them, treat it as ongoing work

**Hidden Gems:**
- "Nothing about us without us" -- coined by disability rights activists, applies directly to app design
- Accessibility Reader: new feature supporting visual text, audio reading, and highlighted follow-along
- Crouton app example: import from image/camera (for those who can't type), hands-free mode (for motor disabilities)
- Carrot Weather example: customizable density from data-rich to minimal layout
- Blackbox game: VoiceOver labels provide puzzle hints for blind players with audio clue "360 dashes in a circle"
- "Inclusion debt" is the accessibility version of tech debt -- normal and expected, but must be tracked

**Cross-references:** Evaluate your app for Accessibility Nutrition Labels (224), Catch up on accessibility in SwiftUI (WWDC24)

---

## Health & Fitness

### Meet the HealthKit Medications API (WWDC25-321)

**API Details:**
- New `HKMedication` and `HKMedicationDoseEvent` types
- Medications use **per-object authorization** -- unique model where user selects which specific medications to share (not blanket type access)
- `requiresPerObjectAuthorization()` returns true for medication types
- Authorization flow: user picks individual medications to share via system UI
- `HKSampleQuery` for basic medication retrieval
- `HKAnchoredObjectQuery` for ongoing monitoring of changes (new meds, dose events, deletions)

**Best Practices:**
- Request read-only access to `HKMedication` and `HKMedicationDoseEvent`
- Use anchored object queries to detect when users add new medications -- prompt re-authorization
- Medication data includes: display name, type (prescription/OTC/supplement), active ingredients with dosage strengths
- Dose events include: date, dose status (taken/skipped), medication reference
- Always handle the case where user hasn't shared any medications yet

**Hidden Gems:**
- Per-object authorization means your app gets a fresh authorization prompt when the user adds a new medication -- use `HKAnchoredObjectQuery` to detect this and call `requestPerObjectReadAuthorization`
- The medications API surfaces data from the Health app's Medications feature (added in iOS 16)
- Active ingredients include RxNorm codes for interoperability
- Sample app is available as a complete reference implementation

**Cross-references:** Track workouts with HealthKit on iOS and iPadOS (322)

---

### Track Workouts with HealthKit on iOS and iPadOS (WWDC25-322)

**Best Practices:**
- Same workout API code works on iPhone, iPad, and Apple Watch with minimal changes
- Always call `prepare()` before `startActivity()` -- show a 3-second countdown to let sensors connect
- Use the workout builder delegate for UI updates (not anchored object queries)
- Always use the workout builder API to create/save workouts -- ensures activity rings update correctly
- Only request authorization for data types you actually need

**API Details:**
- `HKWorkoutSession` + `HKLiveWorkoutBuilder` + `HKLiveWorkoutDataSource`
- iPhone/iPad: external heart rate monitors via Bluetooth GATT profile (including Powerbeats Pro 2)
- `typesToCollect` on data source includes all possible types (e.g., heart rate even without sensor)
- `enableCollection(for:)` / `disableCollection(for:)` to modify collected types
- For post-workout: `statistics(for:)` for summary, `HKStatisticsCollectionQuery` for charting
- `HKQuantitySeriesSampleQuery` for fine-grained data (samples may have count > 1)

**Lock Screen & Siri Integration:**
- First workout session triggers system prompt for lock-screen data access
- Live Activities for workout metrics on lock screen
- Siri intents for start/pause/resume/cancel from lock screen (no unlock needed)
- Implement `INStartWorkoutIntentHandling`, `INPauseWorkoutIntentHandling`, etc. inside main app (not extension)

**Crash Recovery (new for iOS/iPadOS):**
- System auto-relaunches app after crash
- Session and builder restored; you only need to recreate the data source
- New scene delegate: check `options.shouldHandleActiveWorkoutRecovery`
- Call `store.recoverActiveWorkoutSession(completion:)`

**Hidden Gems:**
- If no heart rate sensor is available, gracefully omit the metric from UI rather than showing zero
- If Watch app exists, start workout there for all metrics, then mirror to iPhone
- Demo app with complete code is attached to the session

**Cross-references:** Meet the HealthKit Medications API (321), Bring your app's core features to users with App Intents (WWDC24), Meet ActivityKit (WWDC23), Build a multi-device workout app (WWDC23)

---

## Photos, Camera & Audio

### Enhancing Your Camera Experience with Capture Controls (WWDC25-253)

**API Details -- Physical Capture Events:**
- `AVCaptureEventInteraction` overrides volume buttons and Action button for capture
- Three event phases: `.began`, `.cancelled`, `.ended`
- Primary action: volume down, Action button, Camera Control
- Secondary action: volume up (optional -- defaults to primary if not set)
- SwiftUI: `.onCameraCaptureEvent { event in }` view modifier

**AirPods Remote Capture (new in iOS 26):**
- AirPods with H2 chip can trigger primary capture actions via stem clicks
- Free for apps already using `AVCaptureEventInteraction`
- Default capture sound plays on AirPods; customizable via `playSound` method
- `event.shouldPlaySound` is true only for AirPod-triggered events
- `defaultSoundDisabled` parameter to suppress default sound

**Camera Control (iPhone 16):**
- `AVCaptureControl` base class with subclasses:
  - `AVCaptureSystemZoomSlider` / `AVCaptureSystemExposureBiasSlider` (system-defined)
  - `AVCaptureSlider` (continuous/discrete, app-defined)
  - `AVCapturePicker` (indexed items, app-defined)
- Controls added to `AVCaptureSession` (check `canAddControl` and `maxControlsCount`)
- System controls drive device properties automatically; use KVO or action handler for UI sync
- Disable controls when unsupported rather than removing them (avoids user confusion)

**Hidden Gems:**
- Only 6 lines of code to enable physical button capture in SwiftUI
- Camera events only fire for apps with active `AVCaptureSession` -- backgrounded apps get default system behavior
- Camera Control picker can iterate through custom effects (e.g., reaction effects from iOS 17)

**Cross-references:** Build a great Lock Screen camera capture experience (WWDC24)

---

### Capture Cinematic Video in Your App (WWDC25-319)

**API Details:**
- `AVCaptureDeviceInput.isCinematicVideoCaptureEnabled = true` enables cinematic mode
- Supported on Dual Wide (back) and TrueDepth (front) cameras
- `isCinematicVideoCaptureSupported` on format to verify compatibility
- `simulatedAperture` property controls bokeh strength (min/max/default on format)
- Spatial audio: `audioInput.multichannelAudioMode = .firstOrderAmbisonics`
- Video stabilization: `connection.preferredVideoStabilizationMode = .cinematicExtendedEnhanced`

**Focus Control:**
- `AVCaptureMetadataOutput` with `requiredMetadataObjectTypesForCinematicVideoCapture` detects focus candidates
- Three focus methods:
  1. `setCinematicVideoTrackingFocus(detectedObjectID:focusMode:)` -- lock onto detected object
  2. `setCinematicVideoTrackingFocus(at:focusMode:)` -- find object at point
  3. `setCinematicVideoFixedFocus(at:focusMode:)` -- lock focus on a plane
- `CinematicVideoFocusMode`: `.none`, `.strong` (locked), `.weak` (auto rack focus)

**Hidden Gems:**
- `cinematicVideoCaptureSceneMonitoringStatuses` KVO property reports `.notEnoughLight` -- show user warning
- Still photos captured during cinematic recording automatically get the bokeh treatment
- Long press gesture for fixed focus lock vs. tap for tracking focus is a great UX pattern
- Output includes original video + disparity data + metadata for non-destructive post-editing via Cinematic framework

**Cross-references:** Enhancing your camera experience with capture controls (253)

---

### Enhance Your App's Audio Recording Capabilities (WWDC25-251)

**API Details:**
- New `AVInputPickerInteraction` in AVKit for in-app microphone selection with live metering
- AirPods high-quality recording mode via API
- Spatial audio capture with first-order ambisonics
- Audio Mix feature for separating speech and ambient audio in spatial recordings

**Hidden Gems:**
- Input picker remembers selected device across app sessions
- Audio stack manages the selected device across app activations
- Spatial audio editing can isolate speech from ambient sounds -- great for podcast/content creation apps

**Cross-references:** Capture cinematic video in your app (319), Enhancing your camera experience with capture controls (253)

---

## Video & Media

### Create a Seamless Multiview Playback Experience (WWDC25-302)

**API Details:**
- `AVPlaybackCoordinationMedium` -- synchronizes playback across multiple `AVPlayer` instances
- `player.playbackCoordinator.coordinate(using: coordinationMedium)` -- connect player to medium
- Handles rate changes, seeks, stalling, interruptions, startup synchronization
- `AVRoutingPlaybackArbiter.shared()` -- manages AirPlay routing for multiview
  - `.preferredParticipantForExternalPlayback` -- which player routes to TV
  - `.preferredParticipantForNonMixableAudioRoutes` -- which player routes to HomePod
- `AVPlayer.networkResourcePriority` -- `.high`, `.default`, `.low` for bandwidth allocation

**Best Practices:**
- Use coordination medium for same-event multiview (sports cameras, sign language streams)
- Non-coordinated multiview also works for different events
- Set preferred participants before routing -- avoids wrong stream on big screen
- High priority streams maintain quality when bandwidth is constrained; low priority degrades first

**Hidden Gems:**
- Coordination works across system interfaces: Picture-in-Picture, Now Playing controls
- Coordination medium just takes a few lines of code -- handles all the complex sync logic
- Can switch preferred AirPlay stream dynamically by updating the arbiter property

**Cross-references:** Coordinate media experiences with Group Activities (WWDC21)

---

### Learn About the Apple Projected Media Profile (WWDC25-297)

**Key Concepts:**
- APMP enables 180/360 degree and wide FoV projections in QuickTime/MP4 files
- Uses Video Extended Usage (VEU) signaling
- Apple Positional Audio Codec (APAC) for spatial audio content

**API Details:**
- Conversion tools for equirectangular, cubemap, and other projection formats to APMP
- AVFoundation APIs for reading/writing/editing APMP video
- Support for both mono and stereo VR content

**Cross-references:** Explore video experiences for visionOS (304)

---

### Enhance Your App with ML-Based Video Effects (WWDC25-300)

**API Details:**
- `VTFrameProcessor` API in VideoToolbox (macOS 15.4+, now iOS 26)
- Six effects:
  1. **Frame rate conversion** -- slow-mo, FPS matching
  2. **Super resolution** -- upscale with detail restoration (image and video models)
  3. **Motion blur** -- simulated slow shutter, adjustable strength (1-100)
  4. **Temporal noise filter** -- uses past/future reference frames
  5. **Low latency frame interpolation** -- real-time FPS upsampling
  6. **Low latency super resolution** -- lightweight upscaler for video conferencing

**Best Practices:**
- Configuration class describes the session; Parameters class describes per-frame I/O
- Pre-compute optical flow for editing (expensive); let processor compute on-the-fly for real-time
- Use `sourcePixelBufferAttributes` / `destinationPixelBufferAttributes` for creating CVPixelBuffer pools
- Frame rate conversion: source, next frame, interpolation phases array, destination frames array
- Motion blur: needs previous and next reference frames (set nil for first/last frames)

**Hidden Gems:**
- Combined frame rate doubling + resolution upscaling in a single filter for video conferencing
- Optical flow pre-computation vs. on-the-fly is a key architecture decision
- Sample code with test clips is attached to the session

**Cross-references:** None listed but relates to VideoToolbox documentation

---

## Metal 4 & Graphics

### Discover Metal 4 (WWDC25-205)

**Architecture Changes:**
- `MTL4CommandQueue`, `MTL4CommandBuffer`, `MTL4CommandAllocator` -- new command model
- Command buffers decoupled from queues; independent for parallel encoding
- Unified compute encoder handles blit and acceleration structure commands too
- `MTL4RenderCommandEncoder` with attachment map for swapping color attachments on the fly

**Resource Management:**
- `MTL4ArgumentTable` replaces per-draw bind points -- specify only what you need
- Residency sets: declare all resources at startup, add to queue; rarely need runtime updates
- Placement sparse resources: buffers/textures allocated without pages, mapped from placement heaps
- Barrier API for stage-to-stage synchronization (e.g., dispatch-to-fragment)

**Shader Compilation:**
- `MTL4Compiler` is separate from device; inherits QoS from requesting thread
- Flexible render pipeline states: build common Metal IR once, specialize with different color states
- Pipeline harvesting improvements for ahead-of-time compilation

**Machine Learning Integration:**
- Metal tensors: multi-dimensional data containers, supported across all contexts
- New ML command encoder for large networks (CoreML package format, converted to Metal package)
- Metal Performance Primitives (tensor ops) for small networks inline in shaders
- Tensor ops are shader primitives optimized for Apple silicon

**MetalFX:**
- Frame interpolation: generate intermediate frames for higher refresh rates
- Denoising during upscale: removes noise from low ray-count renders

**Adoption Strategy (phased):**
1. Start with compiler adoption (easiest win, QoS improvements)
2. Add flexible render pipelines and harvesting
3. Adopt Metal 4 command encoding (parallel encoding, ML capabilities)
4. Integrate residency sets, barriers, placement sparse resources
- Can mix Metal and MTL4 command queues using Metal events for synchronization

**Cross-references:** Explore Metal 4 games (254), Go further with Metal 4 games (211), Combine Metal 4 ML and graphics (262), Level up your games (209)

---

### Explore Metal 4 Games (WWDC25-254)

**Command Encoding Efficiency:**
- Unified compute encoder reduces encoder count; no need for separate blit encoders
- Attachment map on render encoder eliminates redundant encoder allocation for multi-pass rendering
- Command allocator gives explicit control over command buffer memory
- Parallel command buffer encoding is first-class (command buffers are independent)

**Resource Management at Scale:**
- Argument tables sized to actual bind point needs (vs. fixed bind point counts)
- Residency sets populated at startup; updates pushed to background thread
- Placement sparse for streaming: allocate/deallocate pages from heaps on demand
- Barriers replace resource hazard tracking: dispatch-to-fragment, vertex-to-dispatch, etc.

**Pipeline Loading:**
- Flexible render pipeline states: compile shared Metal IR once, specialize per color state
- Binary archives for ahead-of-time compilation
- Pipeline harvesting with `MTL4CompilerPipelineDescriptorCallback`
- New compilation API inherits QoS from requesting thread -- prioritize critical shaders

**Performance Tips:**
- Reduce residency management overhead by using residency sets (Remedy's Control saw "significant reductions")
- Use placement sparse for LOD streaming to fit content across device memory budgets
- Move residency set updates to a background thread separate from encoding
- Binary archives eliminate on-device compilation entirely (most performant path)

**Cross-references:** Discover Metal 4 (205), Go further with Metal 4 games (211)

---

### Go Further with Metal 4 Games (WWDC25-211)

**MetalFX Temporal Upscaling:**
- Render at lower resolution, upscale to output resolution
- Requires: color, depth, motion vectors, reactive mask, exposure
- `MTLFXTemporalScaler2` -- new this year
- Reactive mask: marks pixels that change abruptly (particles, transparencies) to prevent ghosting
- Reset history flag for scene cuts

**MetalFX Frame Interpolation:**
- `MTLFXFrameInterpolator` generates intermediate frames
- Inputs: two rendered frames + depth + motion vectors
- Optical flow generated by MetalFX (don't need to compute yourself)
- "Present interpolation first, then real frame" ordering gives lowest perceived latency
- Interpolation bypasses the full render pipeline -- much cheaper than rendering

**Ray Tracing with Metal 4:**
- Acceleration structures built with new Metal 4 API
- `MTL4AccelerationStructureSizes` for memory planning
- Scratch buffer needed during build
- Instance acceleration structures reference primitive acceleration structures
- Ray tracing integrated with Metal 4 barriers and residency

**MetalFX Denoising:**
- Removes noise from low-ray-count renders during upscaling
- Inputs: noisy render, depth, motion, normals, albedo, specular albedo, roughness
- Separate denoising for diffuse and specular channels
- `MTLFXTemporalDenoisedScaler` combines denoising + upscaling

**Performance Tips:**
- Frame interpolation: present interpolated frame FIRST for lowest latency
- Reactive mask is critical for preventing ghosting artifacts on particles/UI
- Denoising allows fewer rays per pixel while maintaining quality

**Cross-references:** Discover Metal 4 (205), Explore Metal 4 games (254), Your guide to Metal ray tracing (WWDC23)

---

## Games & Game Center

### Get Started with Game Center (WWDC25-214)

**Best Practices:**
- Game Center config is now fully in Xcode via `.gamekit` bundle (version-controlled, code-reviewable)
- Single line to initialize: `GKLocalPlayer.local.authenticateHandler = { _, error in }`
- Use Game Progress Manager in Xcode for local testing (debug mode only)
- Lifecycle: Xcode development -> TestFlight beta -> App Store Connect review -> Live

**New Features:**
- **Challenges**: Linked to leaderboards; auto-submit scores when leaderboard scores are submitted
- Challenges can be non-repeatable (great for daily puzzles)
- Duration options configurable per challenge
- **Activities**: Deep links into specific game destinations
- Activities linked to leaderboards, achievements, or multiplayer
- `GKGameActivity` with properties for routing to the right game location
- `activity.start()` / `activity.setScore()` / `activity.end()` -- buffers scores, submits only latest

**Multiplayer Activities:**
- Party codes auto-generated by Game Center
- Shareable via iMessage with web fallback (OpenGraph tags)
- `activity.findMatch()` integrates with Game Center matchmaking
- Display party code in-game; provide manual entry option

**Score Submission Best Practices:**
- Submit score at end of each level attempt (not accumulated lifetime scores)
- Don't submit more times than intended -- challenges are skill contests
- Use `activity.setScore()` to prevent accidental multiple submissions

**Cross-references:** Engage players with the Apple Games app (215)

---

### Level Up Your Games (WWDC25-209)

**System Features:**
- **Game Mode**: `LSSupportsGameMode` in Info.plist; reduces background activity, improves Bluetooth latency
- **Sustained Execution Mode**: Limits performance to steady state from launch for consistent frame rates; requires entitlement
- **Low Power Mode for Gaming** (macOS 26): Players notified about energy usage; can switch in Game Overlay
- Listen for `NSProcessInfoPowerStateDidChange` to detect Low Power Mode

**New Frameworks:**
- **GameSave**: Cloud saves via iCloud, default UI for sync progress/conflicts, offline support
  - `GSSyncedDirectory.openDirectoryForContainerIdentifier()`
  - `directory.finishSyncing(statusDisplay:completionHandler:)`
- **Touch Controls**: Built-in touch control framework for games, integrates with Metal
- **Background Assets**: 200GB Apple hosting, auto out-of-band updates, TestFlight integration

**Game Porting Toolkit 3:**
- Full Metal 4 support in Metal-cpp
- MetalFX denoising and frame interpolation in Metal-cpp
- Metal Shader Converter: HLSL to Metal with intersection function buffers for ray tracing
- Function constants and framebuffer fetch available directly in HLSL

**Metal Performance HUD Updates:**
- Performance insights with recommendations
- Shader compilation count metric (identify hitch sources)
- Performance reports for offline review
- Customizable HUD appearance and position
- Works for both native games and Windows game evaluation environment

**Cross-references:** Discover Metal 4 (205), Explore Metal 4 games (254), Go further with Metal 4 games (211), Get started with Game Center (214), Engage players with the Apple Games app (215), Discover Apple-Hosted Background Assets (325)

---

### Bring Your SceneKit Project to RealityKit (WWDC25-288)

**Key Message: SceneKit is deprecated; migrate to RealityKit**

**Core Differences:**
- SceneKit: `SCNNode` tree hierarchy; RealityKit: Entity-Component System (ECS)
- SceneKit: `SCNView`; RealityKit: `RealityView` (SwiftUI) or `ARView` (UIKit)
- RealityKit uses USD (USDZ) as native format; use Reality Converter for asset conversion
- RealityKit works across iOS, macOS, visionOS; SceneKit did not support visionOS

**Migration Guide:**
- Assets: Convert `.scn`/`.dae` to `.usdz` via Reality Converter or Reality Composer Pro
- Scene composition: Replace `SCNNode` trees with Entity hierarchies; use `ModelComponent` for geometry
- Animations: Use `AnimationResource` and `playAnimation()`; RealityKit supports skeletal and transform animations
- Lights: `DirectionalLightComponent`, `PointLightComponent`, `SpotLightComponent`; image-based lighting via `ImageBasedLightComponent`
- Audio: `AudioFileResource` + `SpatialAudioComponent` for 3D sound
- Visual effects: Particle systems via `ParticleEmitterComponent`; custom materials via `ShaderGraphMaterial`

**Hidden Gems:**
- SceneKit will continue to work on existing platforms -- no urgent forced migration
- Reality Composer Pro is the recommended tool for complex scene setup
- RealityKit's ECS architecture performs better for large scenes due to data-oriented design
- Custom shaders in RealityKit use Shader Graph (visual editor) or `CustomMaterial`

**Cross-references:** What's new in RealityKit (287), Compose interactive 3D content in Reality Composer Pro (WWDC24)

---

## Maps

### Go Further with MapKit (WWDC25-204)

**New APIs:**

**PlaceDescriptor (GeoToolbox framework):**
- Represents places using structured info: name, address, coordinate, service identifier
- Ordered `representations` array (most accurate first)
- `PlaceDescriptor(mapItem:)` and `MKMapItemRequest(placeDescriptor:)` for bidirectional conversion
- Service identifiers: dictionary mapping bundle ID to place ID for cross-service interoperability
- Works with App Intents for natural language place references

**Geocoding (now in MapKit, replacing deprecated CLGeocoder):**
- `MKReverseGeocodingRequest(location:)` -- coordinates to address
- `MKGeocodingRequest(addressString:)` -- address to coordinates
- `MKAddress` for simple full/short address strings
- `MKAddressRepresentations` for locale-aware, customizable address display

**Cycling Directions:**
- `request.transportType = .cycling` on `MKDirections.Request`
- Available on iOS, watchOS, and MapKit JS
- Returns routes with time/distance estimates, step-by-step instructions, geometry

**Look Around in MapKit JS:**
- `new mapkit.LookAround(container, place, options)` -- full interactive experience
- `new mapkit.LookAroundPreview(container, place)` -- compact preview
- Options: `openDialog`, `showsDialogControl`, `showsCloseControl`
- Events: `close`, `load`, `error`, `readystatechange`

**Hidden Gems:**
- Place cards automatically show rich info when using `.mapItemDetailSelectionAccessory(.callout)`
- PlaceDescriptor enables universal links to Apple Maps via `maps.apple.com`
- Unified Maps URLs replace platform-specific URL schemes

**Cross-references:** Unlock the power of places with MapKit (WWDC24), Meet MapKit for SwiftUI (WWDC23)

---

## App Store & Monetization

### Dive into App Store Server APIs for In-App Purchase (WWDC25-249)

**API Updates:**
- New `offerPeriod` field in JWSTransaction (ISO 8601 duration format)
- `offerPeriod` also in JWSRenewalInfo for next renewal
- `appAccountToken` improvements for linking transactions to customer accounts
- Simplified signature generation for promotional offers

**Hidden Gems:**
- Per-object transaction linking makes it easier to reconcile purchases with customer accounts
- Consumption Information endpoint helps the App Store make informed refund decisions

**Cross-references:** What's new in StoreKit and In-App Purchase (241)

---

### Optimize Your Monetization with App Analytics (WWDC25-252)

**New Analytics Features:**
- App Analytics moved to Apps tab in App Store Connect (closer to app management)
- Up to 7 filters on any metric (more than double previous limit), with multiple values per filter
- New Monetization section with Sales view, cohort metrics, benchmarks

**New Metrics:**
- **Download-to-Paid Conversion**: How quickly new users buy (cohort analysis)
- **Average Proceeds per Download**: Revenue growth per user over time
- **Subscription analytics**: 50+ new subscription metrics (states and events)
- **Subscription Retention**: % of users keeping subscriptions over months
- **Offer metrics**: Active offers, conversion rate to paid plans
- **Net Paid Plans**: Visualizes starts, voluntary/involuntary churn

**Cohort Analysis:**
- Table shows conversion/retention by download month and days/months elapsed
- Filterable by custom product page, territory, device, OS
- Color-coded heatmap for visual pattern recognition

**New Analytics Reports API:**
- Subscription state report and subscription event report (replacing older Sales and Trends)
- Links download information to subscription performance in privacy-friendly way

**Best Practices:**
- Compare results to peer group benchmarks to identify gaps
- Use custom product pages to attract different user segments and compare funnel performance
- Use offers to acquire, retain, or win back paying users

**Cross-references:** What's new in App Store Connect (328), What's new in StoreKit and In-App Purchase (241)

---

### Automate Your Development Process with the App Store Connect API (WWDC25-324)

**Webhook Notifications (new):**
- Push-based: App Store Connect sends HTTP POST to your registered URL
- Events: TestFlight feedback, app version state, build upload state, build beta state, Apple-Hosted Background Asset state
- Register via App Store Connect UI or API
- Secret key for HMAC-SHA256 signature verification
- No more polling -- event-driven workflows

**Build Upload API (new):**
- `POST` to create BuildUpload with bundle version and platform
- `POST` to create BuildUploadFile with name, size, asset type
- Response includes upload instructions (URL, method, headers)
- Large builds uploaded in chunks
- `PATCH` with `uploaded: true` to trigger processing

**Feedback API (new):**
- Webhook notification on new screenshot/crash feedback
- API to retrieve device info, screenshot URLs, crash logs
- Programmatic download of crash logs and screenshots

**Hidden Gems:**
- Build upload API works with any language/platform (not just Xcode/altool)
- Webhook signature verification: calculate HMAC-SHA256 with secret + payload body, compare to `X-Apple-SIGNATURE` header
- Build beta state webhook tells you instantly when TestFlight review completes

**Cross-references:** Discover Apple-Hosted Background Assets (325), What's new in App Store Connect (328)

---

### What's New in App Store Connect (WWDC25-328)

**Build Delivery:**
- New web UI for build delivery directly in App Store Connect
- Enhanced TestFlight notifications

**App Discovery:**
- Keywords for custom product pages
- Accessibility Nutrition Labels integration
- Age ratings updates

**New Features:**
- In-App Purchase offer codes
- Review summarization tools
- Build upload via web interface

**Cross-references:** Automate your development process with the App Store Connect API (324), Optimize your monetization with App Analytics (252)

---

## Business, Education & Device Management

### Get to Know the ManagedApp Framework (WWDC25-203)

**API Details:**
- New `ManagedApp` framework (iOS 18.4+, iPadOS 18.4+, visionOS 2.4+)
- Enables organizations to push configuration, secrets, certificates, and identities to apps
- Apps can detect if they're in a managed environment and adapt behavior
- Secure secret distribution via MDM without user interaction

**Best Practices:**
- Use for customizing app experiences per organization
- Retrieve API access tokens securely
- Add custom trust certificates
- Hardware-bound keys for device posture verification
- Design app to work both managed and unmanaged -- graceful degradation

**Hidden Gems:**
- Managed configurations can include passwords, certificates, and PKCS12 identities
- The framework handles secure storage -- developers don't manage keychain directly
- Works with Declarative Device Management for push-based configuration

**Cross-references:** What's new in Apple device management and identity (258)

---

### What's New in Apple Device Management and Identity (WWDC25-258)

**Headline Features:**
- **Device Management Migration**: Reassign devices between MDM servers without wipe; user notification with deadline
- **Apple Business/School Manager APIs**: Device inventory, MDM server assignment, batch operations
- **Return to Service**: iPhone/iPad now preserve managed apps during reset (new key in cloud config)
- **Vision Pro Return to Service**: "Reset for Next User" in Control Center, Digital Crown reset

**Platform SSO Updates:**
- Registration now in Setup Assistant during Automated Device Enrollment
- **Authenticated Guest Mode**: Cloud identity login at login window, data wiped on logout
- **Tap to Login**: NFC reader + corporate badge/school ID in Apple Wallet; Access Keys in Secure Enclave
- Express Mode for login without wake/unlock

**App Management:**
- Per-app update control (enforce, disable, pin to version)
- Real-time installation progress via status channel
- Cellular download restrictions per app
- macOS Tahoe: App Store apps, custom apps, and packages via Declarative Device Management

**Hidden Gems:**
- Device management migration preserves apps and data -- use `await device configured` to ensure apps reinstalled before completing
- Admins can now download lists of personal Apple Accounts on their domain
- Access Management can prevent personal Apple Accounts on org-owned devices (no MDM required)
- AppleCare coverage information now in device inventory
- Older MDM software update management is deprecated in favor of Declarative Device Management

**Cross-references:** Get to know the ManagedApp Framework (203), Filter and tunnel network traffic with NetworkExtension (234)

---

### Explore Enhancements to Your Spatial Business App (WWDC25-223)

**Enterprise visionOS APIs:**
- Streamlined model training workflows for object tracking
- Enhanced video feeds for enterprise applications
- Coordinate system alignment over local network for collaborative experiences
- Enterprise APIs require entitlements (in-house distribution only)

**Key Capabilities:**
- Object tracking with custom-trained models
- Network-based coordinate system sharing for multi-device collaboration
- Enhanced camera feed access for enterprise workflows
- Spatial computing for manufacturing, healthcare, training scenarios

**Hidden Gems:**
- Local network coordinate alignment enables shared AR experiences without cloud infrastructure
- These APIs are only available for in-house enterprise distribution, not App Store apps

**Cross-references:** Share visionOS experiences with nearby people (318), Building spatial experiences for business apps with enterprise APIs (documentation)

---

## Cross-Cutting Themes

### Recurring Patterns Across Sessions

1. **Per-object authorization** is a new pattern (HealthKit Medications) -- expect it to expand to other sensitive data types
2. **Webhook/push-based APIs** replacing polling (App Store Connect) -- a platform-wide trend
3. **Declarative configuration** replacing imperative commands (Device Management)
4. **ML integration at every level**: Metal 4 tensors/ML encoder, VideoToolbox VTFrameProcessor, MetalFX denoising
5. **SceneKit deprecation** signals full commitment to RealityKit/Entity-Component architecture
6. **Assistive Access scene type** is a new paradigm for cognitive accessibility -- expect first-party apps to adopt widely
7. **Liquid Glass** is everywhere: icons, controls, pointer effects, toolbar -- the unifying design material
8. **GameSave framework** + Background Assets = complete cross-device game infrastructure
9. **PlaceDescriptor** in GeoToolbox enables cross-service place interoperability

### Most Impactful Quick Wins

| Session | Quick Win | Effort |
|---------|-----------|--------|
| WWDC25-209 | Add `LSSupportsGameMode` to Info.plist | 1 minute |
| WWDC25-253 | 6 lines for physical button camera capture | 5 minutes |
| WWDC25-229 | `.accessibilityElement(children: .contain)` for VoiceOver containers | Minutes per view |
| WWDC25-238 | `UISupportsFullScreenInAssistiveAccess` in Info.plist | 1 minute |
| WWDC25-214 | Single line Game Center initialization | 1 minute |
| WWDC25-302 | `AVPlaybackCoordinationMedium` for multiview sync | ~10 lines |
| WWDC25-361 | One `.icon` file for all platform variants | Saves hours |
| WWDC25-324 | Webhook listener for App Store Connect events | Hours (one-time) |
