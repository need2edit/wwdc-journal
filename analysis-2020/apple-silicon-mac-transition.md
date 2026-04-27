# WWDC 2020 — Apple Silicon Mac Transition

The headline announcement of WWDC 2020: the Mac is moving from Intel to Apple Silicon (arm64). This is the biggest hardware platform shift Apple has done in 15 years, and it touches every layer — hardware, OS, security, build tooling, app distribution, and frameworks.

## Sessions Analyzed
- 10686 — Explore the new system architecture of Apple silicon Macs (gateway)
- 10214 — Port your Mac app to Apple silicon
- 10114 — iPad and iPhone apps on Apple silicon Macs
- 10631 — Bring your Metal app to Apple silicon Macs
- 10632 — Optimize Metal Performance for Apple silicon Macs
- 10210 — Modernize PCI and SCSI drivers with DriverKit

## The Hardware Shift

Apple Silicon Macs are a **system-on-chip (SoC)** with **unified memory architecture** — CPU and GPU share the same RAM with no PCIe copy step. The chip combines:
- Performance cores ("P cores") + Efficient cores ("E cores") — asymmetric multiprocessing (AMP)
- Apple-designed GPU (TBDR family, same as iPhone/iPad)
- Neural Engine for Core ML
- ML accelerators reachable via the Accelerate framework
- Hardware video encoders/decoders

Implication: zero-copy texture sharing for graphics, Metal directly drives a tile-based deferred renderer on the desktop for the first time.

## What "Just Works" — Same Frameworks, Different Backend

Apple's pitch is deliberate: **no new APIs to learn**. The same Metal, Core ML, AVFoundation/VideoToolbox, Accelerate, Compression, SIMD calls just run faster on Apple Silicon. Specific recommendations:
- Use `computeUnits = .all` on Core ML models so the Neural Engine can be picked.
- Prefer **BiPlanar pixel formats** (YUV) for AVFoundation video — best path through HW codecs.
- Use **Grand Central Dispatch + concurrentPerform**, not hand-rolled threads, for parallel work — GCD knows how to spread tasks across P/E cores intelligently.
- Always set **Quality of Service (QoS)** on every work item; QoS is a primary input to which core a task lands on.

## Security Model (Inherited from iOS)

Apple Silicon Macs adopt iPhone-style security primitives:
- **Write XOR Execute (W^X)** on memory pages. Pages cannot be writable AND executable simultaneously. New API lets a page be flipped between W and X **per-thread** so JITs (Java, JavaScript) can be both fast and secure.
- **Kernel Integrity Protection** — kernel pages become immutable after load, blocking kernel code injection.
- **Pointer Authentication (PAC)** — unused bits in 64-bit pointers store an authentication code, hardening against ROP attacks. Currently enabled for Apple's own kernel, system apps, and system services. Third-party apps can experiment via boot-arg.
- **Per-device IOMMU isolation** — every PCIe device gets its own memory mapping. Drivers using `getPhysicalSegment` on `IOMemoryDescriptor` directly will break; use `IOMapper` + `IODMACommand` instead.

### Kernel Extensions: The Endgame

Kext development gets progressively more painful: requires reboot to load, requires PAC, surfaces friction warnings to users, and Apple states "expect to see more friction over time." **Migrate to DriverKit** — drivers in user space — now.

## Boot, Recovery, FileVault

- All start-up keys unified into a single **Press-and-hold-Touch-ID/Power → Startup Options** UI (replaces the constellation of Cmd-R / Cmd-Opt-R / etc).
- **Mac Sharing Mode** replaces Target Disk Mode — uses SMB file sharing, requires user authentication.
- **Per-volume security policy** — you can run a reduced-security dev-OS install on one volume while another volume stays full-security for daily use.
- **System Recovery** is a hidden minimal macOS partition that can reinstall macOS Recovery itself if the recovery container is corrupt. Apple Configurator 2 stays as the last-resort restore path.
- **Secure hibernation** with at-rest memory encryption (integrity + anti-replay) is new and made possible by the SoC.

## Rosetta 2: How Translation Works

Rosetta translates x86_64 code to arm64 at **install time** (triggered by Mac App Store or pkg installer). Anything the static translator misses gets JIT-translated on the fly. Translations are:
- Code-signed
- Tied to the specific machine
- Securely cached
- Refreshed across OS updates

What works: macOS apps, Catalyst apps, games, complex apps with embedded JITs (web browsers).
What doesn't: kernel extensions, AVX vector extensions, virtualization.

To detect at runtime: `sysctl.proc_translated`. Apps should already be querying for AVX support; nothing changes for that pattern.

## Porting Your App: The Concrete Steps

1. **Build for Intel under Rosetta first** — verify nothing broke. Note: `PAGE_SIZE` is no longer a compile-time constant. Use `PAGE_MAX_SIZE` (compile-time upper bound) or `vm_page_size` (runtime).
2. **Switch run destination to native (arm64)** and resolve compile errors. The classic pitfall: `#if x86_64` used as a synonym for "macOS" — replace with `TARGET_OS_OSX` / `#if os(macOS)`.
3. **Resolve linker errors** — non-universal binary frameworks. Use `lipo -info <binary>` to inspect. You must get universal builds from every vendor.

Then runtime test: build only proves cross-compile worked, not correctness.

### The mach_absolute_time Trap

The single most common bug in ported code: assuming `mach_absolute_time()` returns nanoseconds. It does not. The timebase changes per architecture. Symptom: something runs ~40× slower (or faster) than expected. Fix:
- Use `mach_timebase_info` to get the conversion factor, OR
- Use `clock_gettime(CLOCK_UPTIME_RAW, ...)` which always returns nanoseconds, OR
- Better: prefer `Foundation.Date` / GCD timers / `DispatchTime` — they handle this for you.

### Spinlocks and Busy-Waiting Are Now Worse

On AMP cores, busy-waiting can pin a P core needlessly, slowing the entire job. Replace with blocking primitives: `os_unfair_lock`, `NSLock`, pthread mutex, condition variables.

### Memory Ordering Subtlety

Intel and arm64 have different memory ordering models. Code with **latent data races** that "happened to work" on Intel may crash on Apple Silicon. Rosetta fully emulates Intel ordering, so you only see the new behavior with native builds. **Run Thread Sanitizer.**

## Plug-ins and Process Architecture

A single process must contain code of one architecture only. So:
- **In-process plug-ins**: native apps can only `dlopen` native plug-ins; Rosetta apps can only load Intel plug-ins. If your plug-in vendor hasn't shipped a universal build, the plug-in will fail to load with a clear `dlerror` message.
- **Out-of-process plug-ins (XPC)**: no restriction — each plug-in process can be a different architecture. Migrate toward XPC for plug-ins.
- Last-resort escape hatch: Finder Get-Info has an **"Open using Rosetta"** checkbox for universal apps that need to load Intel-only plug-ins. You can disallow this with an Info.plist key.

## iOS Apps on the Mac (Free Distribution Win)

This is the under-celebrated part of the transition: **every compatible iOS app is automatically available on the Mac App Store as the same binary**. No recompile, no Catalyst conversion. Developer can opt-out per app from App Store Connect's Pricing & Availability page.

Caveats to design around:
- iOS apps run in fixed-size windows unless they support iPad multitasking (then fully resizable, with **live resize** — optimize layout perf!).
- Sensors (accelerometer, gyro, magnetometer, depth cam, GPS) may be absent — use `if isAvailable` checks.
- Cameras: don't enumerate AV devices; use `AVCaptureDeviceDiscoverySession` to handle external/USB cams correctly.
- Don't hard-code device.model checks for "iPhone"/"iPad"/"iPod touch" — fall back gracefully.
- Foundation file-system APIs handle the different container locations transparently.

In Xcode the run destination is **"My Mac, Designed for iPad"**. Full debugging, profiling, tests, View debugger, Memory debugger — all work on the iOS app running on a Mac. No TestFlight on Mac yet, so use ad-hoc / development distribution for prerelease testing.

App Store features that work unchanged: in-app purchases, subscriptions, on-demand resources, app thinning. The Mac is treated as "a very capable iPad" for thinning purposes — a single Mac variant.

## Metal on Apple Silicon Mac (The Architecture Surprise)

This is more subtle than "old Metal works." Apple Silicon Macs use the **TBDR (Tile-Based Deferred Renderer)** architecture — same as iPhone, **not** like Intel/AMD/Nvidia immediate-mode renderers. Implications:
- Apple GPU exposes a **unified Metal feature set** (Mac 2 family + Apple GPU family). Programmable Blending, Tile Shaders, Local Image Blocks, on-chip MSAA resolve, memoryless render targets are now available on the Mac.
- `isLowPower` returns **false** for Apple GPUs — treat them like discrete GPUs for tier/quality decisions, not integrated GPUs.
- **Stop querying GPU name strings to gate features.** Use `supportsFamily(_:)`, individual feature queries, and `threadExecutionWidth` for SIMD-group size.

### The Silent-Bug Trio (Compatibility Workarounds Applied)

For apps built with the macOS Catalina SDK or earlier, Metal applies **automatic compatibility workarounds** for three specific bugs that only manifest as graphics corruption on TBDR. Apps built with the Big Sur SDK lose these workarounds and must be correct:
1. `loadAction = .dontCare` where `.load` was actually needed (under TBDR, the tile memory is uninitialized, producing artifacts).
2. **Position invariance** — vertex shaders that compute positions identically across passes can produce slightly different values due to compiler optimizations. If a later pass uses depth-compare `.equal`, pixels fail the test and get cleared. Fix: pass `preserveInvariance` to the compiler AND mark the position output `[[invariant]]` in MSL.
3. **Sampling the current depth/stencil attachment in the same render pass** is undefined behavior. Workaround: copy the texture before the pass; do **not** insert texture/memory barriers (very expensive on TBDR).

### Threadgroup Synchronization: SIMD Size Matters

Apple GPU's SIMD group size is **32**, not 64 like AMD. Code that "got lucky" assuming SIMD == threadgroup size on AMD will produce visual artifacts on Apple. Always:
- Query `threads_per_simdgroup` (in shader) or `threadExecutionWidth` (Metal API).
- Use `simdgroup_barrier` for single-SIMD-group threadgroups; `threadgroup_barrier` only when crossing groups (it's expensive).
- Best perf: rewrite shaders for 32-thread SIMD groups to skip the threadgroup barrier entirely.

### Load/Store Action Discipline

On TBDR these aren't optimization hints — they directly control on-chip tile memory state:
- `loadAction = .load` only if previous content needs to be preserved (partial-frame draws on top of prior content).
- `storeAction = .store` only if a later pass consumes the result; otherwise `.dontCare`.
- Memoryless render targets (`storageMode = .memoryless`) for intermediate buffers (G-buffer attachments that never leave tile memory) — **zero memory footprint** on TBDR.

### MSAA Is Now Cheap

On Apple GPU, MSAA samples live in tile memory and resolve before flush. The multisample texture can be `.memoryless` — no VRAM cost. MSAA combined with deferred rendering is finally practical.

## Cross-References
- See [big-sur-design-system.md](big-sur-design-system.md) for the macOS Big Sur visual overhaul that landed alongside.
- See [catalyst-mac-modernization.md](catalyst-mac-modernization.md) for Mac Catalyst's "Optimized for Mac" mode, which complements the iOS-on-Mac story.
- See [metal-graphics-pro.md](metal-graphics-pro.md) for the broader Metal feature additions in 2020.

## Migration Checklist
- [ ] Run app under Rosetta — verify it still works.
- [ ] Switch to native arm64 run destination — fix `#if x86_64` mis-uses, `mach_absolute_time` assumptions, busy-waiting.
- [ ] `lipo -info` every binary dependency; demand universal builds.
- [ ] Replace gesture-recognizer-on-UIButton patterns and other iOS-isms before optimizing for Mac.
- [ ] Audit Metal: stop querying GPU name; query feature families; verify load/store actions; preserve position invariance where needed.
- [ ] Plan a kext-to-DriverKit migration timeline.
- [ ] Test under Thread Sanitizer to surface memory-ordering bugs.
- [ ] Audit Info.plist for `LSRequiresNativeExecution` if you must opt out of Rosetta.
- [ ] Decide: ship iOS app on Mac App Store as-is, or build a Catalyst-optimized version for the full Mac experience.
