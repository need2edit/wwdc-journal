# WWDC 2020 — Media: HLS, Audio Workgroups, AirPlay, Stereo Capture, tvOS

WWDC 2020's media story has three big pillars: **Low-Latency HLS** (LL-HLS) — the new standard for sub-2-second-latency streaming, **Audio Workgroups** for realtime-thread-aware scheduling on Apple Silicon, and **stereo audio recording on iPhone**.

## Sessions Analyzed
- 10228 — What's new in Low-Latency HLS (gateway)
- 10229 — Discover HLS Blocking Preload Hints
- 10230 — Optimize live streams with HLS Playlist Delta Updates
- 10231 — Reduce latency with HLS Blocking Playlist Reload
- 10232 — Adapt ad insertion to Low-Latency HLS
- 10225 — Improve stream authoring with HLS Tools
- 10158 — Deliver a better HLS audio experience
- 10655 — Discover how to download and play HLS offline
- 10224 — Meet Audio Workgroups
- 10226 — Record stereo audio with AVAudioSession
- 10011 — Author fragmented MPEG-4 content with AVAssetWriter
- 10042 — Build SwiftUI apps for tvOS
- 10645 — Support multiple users in your tvOS app
- 10176 — Master Picture in Picture on tvOS
- 10636 — What's new in streaming audio for Apple Watch

## Low-Latency HLS (LL-HLS) — The Big Streaming Story

LL-HLS reduces live-stream latency from the traditional 6-30 seconds down to **2 seconds or less** while remaining HTTP-cacheable and CDN-friendly. The core innovations:

### Partial Segments

Instead of waiting for a full 6-second segment, the encoder publishes **partial segments** every 200ms-300ms. The player can request the latest part as soon as it's available.

### Blocking Playlist Reload (10231)

The player issues a request like "give me the playlist when it includes media sequence N+1 OR when 3 seconds elapse." The server **holds the request** until that condition is met (long-polling). Eliminates the polling loop.

### Blocking Preload Hints (10229)

The playlist includes a `#EXT-X-PRELOAD-HINT` tag pointing at the next part. The player can issue a request **before the part exists**, and the server holds it until the part is ready. Eliminates the gap between part publication and player fetch.

### Playlist Delta Updates (10230)

Big live playlists are expensive. The `#EXT-X-SKIP` tag lets the server send only the delta since a known media sequence number, reducing payload size by 90%+ for long-running streams.

### HTTP/2 Push Optimization

Player can request the playlist; server can push the next part it expects the player to need next. Cuts round-trips.

### Ad Insertion in LL-HLS (10232)

Server-side ad insertion (SSAI) APIs adapted for LL-HLS. `EXT-X-DATERANGE` with SCTE-35 markers; player handles ad-segment rendering, includes companion-ad signaling.

### LL-HLS Authoring (10225)

The HLS toolset (`mediastreamsegmenter`, `mediafilesegmenter`, `variantplaylistcreator`) updated to author LL-HLS-compliant streams. Practical recommendations: target part duration 200-300ms, partial segment count 2-4, strict `EXT-X-PART-INF` declaration.

### Offline HLS Download (10655)

`AVAssetDownloadURLSession` improvements: download specific tracks (audio-only, specific languages, lower-bitrate variants) for offline playback. New `AVMediaSelectionGroup` controls which tracks come along.

## Audio Workgroups (10224) — Critical for Realtime Audio on Apple Silicon

**The single most important addition for audio app developers in 2020.**

### The Problem

Apple Silicon Macs have asymmetric P/E cores. Without explicit signaling, the kernel scheduler doesn't know your audio thread has a deadline — it might schedule it on an E core, causing glitches. The performance controller traditionally observed thread behavior; now audio gets a direct input.

### The Fix

Audio frameworks (CoreAudio, AVFoundation) automatically join their realtime threads to the device's `os_workgroup`. **Your job**: if you create your own realtime audio threads, join them too:

```swift
// Get the device's workgroup
let workgroup = audioUnit.osWorkgroup  // From AURemoteIO/AUHAL property

// In your realtime thread (do this once):
var joinToken = os_workgroup_join_token_s()
os_workgroup_join(workgroup, &joinToken)

// At thread end:
os_workgroup_leave(workgroup, &joinToken)
```

### For Audio Units That Create Their Own Threads

Implement the new `AURenderContextObserver` block. It receives the workgroup from the host before each render call (the workgroup may change between renders!). Join your auxiliary realtime threads to the **current** workgroup at render time.

```swift
audioUnit.renderContextObserver = { context in
  let workgroup = context.workgroup
  // Join auxiliary threads if workgroup changed
}
```

### Asynchronous Worker Threads with Different Deadlines

Create your own workgroup with `AudioWorkIntervalCreate`. Master thread calls `os_workgroup_interval_start` at cycle start (with start time and deadline) and `os_workgroup_interval_finish` at cycle end. Other threads `os_workgroup_join`.

### Deadline Time Units

`mach_absolute_time` units. Use `mach_timebase_info` for the conversion factor. **Don't assume nanoseconds.**

### Recommended Thread Count

`os_workgroup_max_parallel_threads(workgroup, attr)` returns the recommended parallel-thread count for the current device. For Audio Units that don't know the workgroup until render, allocate threads pessimistically (CPU core count) but only **use** the recommended subset at render time.

### Bottom Line

Every audio app or plug-in that creates realtime threads **must adopt this**. Without it, Apple Silicon Macs may glitch even when older hardware was fine.

## Stereo Audio Recording on iPhone (10226)

iPhone XS and later support **stereo audio capture**. Configure via `AVAudioSession`:

```swift
let session = AVAudioSession.sharedInstance()
try session.setCategory(.playAndRecord, options: [.allowBluetooth])
try session.setSupportedPolarPatterns([...])
let dataSource = session.preferredInputDataSource
try dataSource?.setPreferredPolarPattern(.stereo)
try session.setActive(true)
```

Polar patterns:
- `.cardioid` — front-pointing
- `.subcardioid`
- `.omnidirectional`
- `.stereo` (the new one)

The system automatically selects the appropriate microphones and applies beamforming.

## HLS Audio Improvements (10158)

LL-HLS audio improvements: lower-latency music streaming, support for **Dolby Atmos** in HLS playlists, gapless playback for music apps.

## tvOS Updates

### SwiftUI for tvOS (10042)

Build entire tvOS apps in SwiftUI. The session covers the focus engine integration, customizing focus appearance via `.focusable(_:onFocusChange:)`, and tvOS-specific patterns (carousel rows, fullscreen video).

### Multi-User on tvOS (10645)

Apple TV now supports multiple users with personalized state. Apps can adopt:
- Per-user app data (saved in user-specific containers)
- Per-user preferences and state
- Sign-in flows that enroll Apple TV users

### Picture-in-Picture on tvOS (10176)

Native PiP support on Apple TV. Adopt via `AVPictureInPictureController`, similar to iOS.

## Cross-References
- [apple-silicon-mac-transition.md](apple-silicon-mac-transition.md) — Audio Workgroups are critical for the Apple Silicon transition.
- [metal-graphics-pro.md](metal-graphics-pro.md) — HDR video pipeline pairs with HLS HDR streaming.
- [siri-intents-shortcuts.md](siri-intents-shortcuts.md) — Media Intents for audio streaming apps.
- [watchos-7.md](watchos-7.md) — Streaming audio for Apple Watch (10636).

## Adoption Checklist
- [ ] If you stream live video, evaluate LL-HLS adoption — sub-2-second latency without giving up CDN caching.
- [ ] Use HLS Playlist Delta Updates to slash playlist sizes for long-running streams.
- [ ] If you're a player, implement `EXT-X-PRELOAD-HINT` handling for low-latency.
- [ ] **Critical**: if you do any custom realtime audio, adopt `os_workgroup` joins.
- [ ] If a music recording app, expose stereo capture with selectable polar patterns.
- [ ] If a tvOS app, evaluate multi-user adoption.
- [ ] If a media app, evaluate SwiftUI for tvOS for shared codebase with iOS.
