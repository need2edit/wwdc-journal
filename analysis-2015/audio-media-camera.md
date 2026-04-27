# Audio, Media & Camera — WWDC 2015 Analysis

**Sessions covered:** 508 (Audio Unit Extensions), 502 (Content Protection for HTTP Live Streaming), 506 (Editing Movies in AV Foundation), 503 (Monetize and Promote Your App with iAd), 507 (What's New in Core Audio), 510 (What's New in Core Image), 211 (Multitasking Essentials for Media-Based Apps on iPad in iOS 9), 230 (Performance on iOS and watchOS — touches video performance)

## Headline

**Audio Unit Extensions** for iOS — third-party audio plugins for the first time on iOS, hostable in any AU host like GarageBand. **AVMovie / AVMutableMovie** for non-destructive editing of QuickTime files (range edits, track add/remove, sample reference movies). HLS gains FairPlay content protection. Picture-in-Picture for video. Core Audio improvements for low-latency.

## Audio Unit Extensions (508)

- New extension type: `AudioUnit`. Hostable by any AU-aware app (GarageBand, Logic, Cubase iOS, etc.).
- Three subtypes: instruments, effects, generators.
- The audio rendering callback runs in the host's audio thread context. **PERFORMANCE**: real-time audio constraints — no allocations, no locks, no blocking I/O on the render callback. Use lock-free ring buffers if you need to communicate with non-realtime threads.
- UI is a separate `AUViewController`. Can be hosted inline in the AU host or full-screen.
- Bridge to user defaults via App Groups for preset persistence shared between extension and containing app.
- Same plugin works on macOS via Audio Component (the existing AU3 API).

**HIDDEN GEM**: this collapses the gap between desktop and mobile audio production — your Mac AU plugin and your iOS AU extension can share most of their DSP code via a shared C++ framework.

## AVFoundation Movie Editing (506)

The new `AVMovie` / `AVMutableMovie` classes. Five new classes total: AVMovie, AVMutableMovie, AVMovieTrack, AVMutableMovieTrack, AVMediaDataStorage.

### Sample reference movie files

QuickTime files separate sample data (image/audio bytes) from sample organization (movie box). A "sample reference movie file" has only the movie box, with all sample data referenced from external files via URL.

- Insanely powerful: you can edit a 1.5TB collection of skating videos by manipulating a tiny movie box, never touching the underlying media files.
- **HIDDEN GEM**: relative URLs via `setSampleReferenceBaseURL(_:)` — the base for resolving sample references. Move the movie box and all sample files together to a new location, references still resolve.
- Fragility tradeoff: if referenced media moves/deletes, playback breaks. For distribution, run through `AVAssetExportSession` to produce a self-contained file.

### Editing API

- Range editing on movies and tracks: `insertTimeRange(_:of:at:copySampleData:)`. The Boolean controls whether to copy bytes or just sample references.
- Add/remove tracks: `addMutableTrack(withMediaType:copySettingsFrom:)`, `removeTrack(_:)`.
- Track associations: `addTrackAssociation(to:type:)` for chapter tracks, captioning, alternate audio.
- Movie and track metadata: `setMetadata(_:forFormat:)` — write custom keys into the movie box.

### Real-world use case (506)

Tim Monroe's "Tim's Radical Inline Skate Tour" — 500GB+ of GoPro footage indexed using:
1. Combine consecutive camera files into one sample reference movie file.
2. Add custom metadata (weather, holiday, day-of-week, location) to the movie box.
3. Add a timed metadata track containing per-second GPS coordinates from a GPX file.
4. Reverse-geocode coordinates server-side, embed street names as searchable metadata.

Total bytes copied: tiny. Total bytes processed: >500GB virtually.

## HLS Content Protection (502)

- HLS now supports FairPlay Streaming for DRM-protected content.
- Key delivery via HTTPS to a content provider's key server.
- Personalized keys per device.
- Compatible with offline downloads (iOS 10+).

## Picture in Picture for Video (211, 107)

- Background-audio apps can opt video into PiP: `AVPictureInPictureController` (or auto-enabled when using `AVPlayerViewController`).
- Only ONE PiP at a time. The system manages.
- Your video continues across app switches. The user can drag PiP to any corner; system pins.

## Multitasking & Camera (211)

- Camera access in multitasking: only the **primary** app can access. Secondary apps get a "camera not available" error.
- For media editing apps in Slide Over, gracefully degrade — show a "tap to bring to full screen for camera access" UI.

## Core Audio (507)

- New audio session options for low-latency recording (down to ~5ms round-trip).
- Hardware sample rate negotiation more reliable.
- Better integration with Inter-App Audio for routing audio between apps.

## Core Image (510)

- 200+ built-in CIFilters.
- Custom CIKernels in Metal Shading Language (CIKernel renamed; Metal kernels are now first-class).
- Core Image autocorrect and feature detection (faces, rectangles, QR, text in Vision API which lands in 2017 — this year is the foundation).
- Adopt CIImage everywhere; chains are lazily evaluated and the GPU executes them as a fused operation.

## iAd (503)

- iAd is being phased toward a developer-facing self-serve model. (Note: iAd was deprecated entirely in 2016.)
- Best-practice patterns for in-app advertising design: don't crowd content, respect Auto Layout for ad insertion.

## Cross-references

- AU Extensions (508) plus the App Extension model (224) reuse the entire app extension story.
- AVMovie (506) plus iCloud Drive plus Document-Based Apps (234) is the new pro-app pipeline.
- HLS (502) plus PiP (211) define video playback for the next decade of iOS.
- Core Image (510) plus Metal (603) plus GameplayKit (608) are the GPU-driven trinity.
