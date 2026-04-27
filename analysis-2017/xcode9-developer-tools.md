# Xcode 9, Testing, Source Control & Developer Tools — WWDC 2017 Analysis

**Sessions covered:** 405 (GitHub and the New Source Control Workflows in Xcode 9), 404 (Debugging with Xcode 9), 406 (Finding Bugs Using Xcode Runtime Tools), 407 (Understanding Undefined Behavior), 408 (What's New in Swift Playgrounds), 409 (What's New in Testing), 411 (What's New in LLVM), 412 (Auto Layout Techniques in Interface Builder), 413 (App Startup Time: Past, Present, and Future), 414 (Engineering for Testability), 403 (What's New in Signing for Xcode and Xcode Server), 416 (Teaching with Swift Playgrounds), 410 (Localizing Content for Swift Playgrounds), 401 (Localizing with Xcode 9)

## Headline

Xcode 9 is the most ambitious developer tools release of the decade: **wireless install/debug**, **GitHub-aware source control with PR review and clone**, **simultaneous device debug** (run on iPhone and Apple Watch in one click), **refactoring for Swift**, **a Swift-native build system**, **the Address/Thread/Undefined-Behavior sanitizers integrated into the test runner**, **Main Thread Checker**, and **Index-While-Building** that eliminates the standalone indexing pass.

## Wireless Install & Debug (404)

Pair your device once over USB, then unplug. From then on, Xcode discovers it over the local Wi-Fi network for build/install/debug.

- Settings: Window → Devices and Simulators → click device → "Connect via network".
- Build to device, attach LLDB, breakpoint, edit-and-continue — all wireless.
- Debug Apple Watch directly without going through the iPhone.
- **HIDDEN GEM**: Xcode shows wireless devices with a Wi-Fi icon next to the device dropdown. If you see the icon, no cable; if you don't, you're plugged in.

## Simultaneous Device Debugging (404)

Pick "iPhone X + Apple Watch Series 3" as a paired destination — Xcode launches both apps and runs **two simultaneous debug sessions**. Set breakpoints in both schemes; LLDB switches contexts on hit.

- Critical for Watch app development — finally debug iPhone↔Watch communication without two Xcodes.

## GitHub Integration & Source Control (405)

- **Account-aware GitHub**: Xcode → Preferences → Accounts → Add GitHub. Browse your repos, clone with one click, see issues and pull requests inline.
- **In-IDE PR review**: open a PR, see the diff annotated in the editor, comment inline, approve.
- **Branching UI**: a new Source Control Navigator (left pane) shows local branches, remote branches, tags, stashed changes — with a graph view of recent commits.
- **Tags**: create, push, see them in the navigator.

**HIDDEN GEM**: rebases, force-pushes, and stashes are still command-line territory — the UI handles routine branch/commit/push, but power workflows still want the terminal.

## Refactoring for Swift (411)

Xcode 9 adds:

- **Rename** (file-aware: renames the symbol everywhere including in Storyboards/XIBs that reference it via `@IBOutlet`/`@IBAction`).
- **Extract Method**, **Extract Local**.
- **Generate Memberwise Initializer** for structs.
- **Fill Switch Cases** for enums.

The infrastructure ships in the open-source Swift project; third-party refactorings can be loaded via toolchains.

**HIDDEN GEM**: rename works **across Swift, Objective-C, and Interface Builder** simultaneously. Rename `myMethod` and the `IBAction` connection in the storyboard updates automatically. This was previously a constant source of runtime crashes after rename.

## Index-While-Building (411)

Xcode previously had a separate, slow indexing pass that would lock up the IDE on large projects. Xcode 9 indexes as a side effect of compilation:

- First build = first usable index. No "Indexing… Please wait" wall.
- Search, jump-to-definition, autocomplete, and refactoring all work immediately.
- **PERFORMANCE**: large Swift projects (~100k LOC) cut their cold-open time from minutes to seconds.

## New Swift Build System (411)

- Written in Swift, runs on top of LLBuild (open source).
- Opt-in via Workspace Settings → Build System: `New Build System (Preview)`.
- **PERFORMANCE**: incremental builds 2-10x faster on large projects. Parallel target compilation when independent.
- Default in Xcode 10. Most projects work without modification, but watch for shell scripts that depend on Xcode's working directory or environment variables.

## Sanitizers (406)

Xcode 9 ships three runtime checkers as scheme options:

- **Address Sanitizer** (ASan) — detects use-after-free, heap/stack buffer overflows, double-free, leaks. Build with `-fsanitize=address`. ~2x runtime overhead.
- **Thread Sanitizer** (TSan) — data races on shared variables. Catches concurrent reads-with-writes that "happen to work" today.
- **Undefined Behavior Sanitizer** (UBSan) — integer overflow, null pointer dereference, misaligned access, divide-by-zero in C/Objective-C/C++.

Enable per-scheme in Edit Scheme → Diagnostics. **WARNING**: only ASan and TSan are mutually exclusive (can't run both at once).

**HIDDEN GEM**: enabling Main Thread Checker in the same diagnostics tab catches `setNeedsLayout` from background queues and similar UIKit-on-wrong-thread bugs that historically only crashed in the field.

## Main Thread Checker (406)

Free with Xcode 9. Catches UIKit calls from background threads at runtime:

```
Main Thread Checker: UI API called on a background thread:
  -[UILabel setText:]
  PID: 12345, TID: 67890, Thread name: (none),
  Queue name: com.example.NetworkQueue
  Backtrace: …
```

Always on by default in debug builds. **PERFORMANCE**: minimal overhead. No reason to disable.

## Understanding Undefined Behavior (407)

The session walks through the most common UB patterns in C/C++/Objective-C and how UBSan reports them. Highlights:

- Signed integer overflow is UB in C (wraps in unsigned). UBSan catches both intentional and accidental cases.
- Strict aliasing violations: casting `int*` to `float*` and reading is UB.
- Format strings without matching argument types: `%d` with a `long` is UB on 64-bit systems where `int != long`.

Migrate to Swift where possible; otherwise enable UBSan in CI.

## Auto Layout in Interface Builder (412)

- **Stack View Refactoring**: Editor → Embed In → Stack View transforms a constraint-heavy layout into a clean stack hierarchy.
- **Vary for Traits**: design for compact and regular size classes in the same XIB without duplicating views.
- **Live rendering of `IBDesignable` views** at multiple device sizes simultaneously.

**HIDDEN GEM**: the new "Resolve Auto Layout Issues" → "Update Frames" command updates frames to match constraints (or vice-versa with "Update Constraints") — kills entire categories of "the storyboard is yellow but it works" warnings.

## Testing (409, 414)

- **Parallel testing destinations**: split a test plan across simulators (3 iPhone, 1 iPad) and run all in parallel. Test suite times divided by destination count.
- **Test Plans** are not yet here in Xcode 9 (Apple ships them in Xcode 11). For 2017, use schemes with different test action configurations.
- **`XCTContext.runActivity(named:)`**: group assertions in the test report. Critical for end-to-end tests with many checkpoints.
- **`XCTAttachment`**: attach screenshots, JSON dumps, custom data to the test report. Ideal for failure forensics.
- **`measure { }`**: performance metric APIs gain custom metrics support — measure not just wall time but also memory peak and disk I/O.

## App Startup Time (413)

- **First-frame target on iOS: 400 ms**. Anything beyond and the user notices.
- **dyld 3** (iOS 11) caches mach-o linkage results across launches. Warm starts skip most of the symbol resolution work.
- **PERFORMANCE**: avoid linking unused frameworks. Each `OTHER_LDFLAGS = -framework Foo` adds milliseconds even if Foo is never called.
- **WARNING**: `+initialize` and `+load` in Objective-C run on first message and at load time respectively. `+load` runs even if the class is never used — never put work there.
- Swift static initializers (`let global = …` at file scope) run lazily on first access. Move expensive setup off the launch path.

## Code Signing & Xcode Server (403)

- **Automatic code signing** is now the default for new projects. Xcode manages provisioning profiles transparently.
- Xcode Server can run inside Xcode now (no separate macOS Server install required).
- **HIDDEN GEM**: signed XCFrameworks (later in 2019) — for 2017, framework code signing checks happen at runtime; mismatched signatures crash on launch with a System Integrity Protection error.

## Swift Playgrounds (408, 410, 416)

- Playground books support **localization** — see session 410 for the full structure (Resources/{lang}.lproj).
- Author your own books with the Subscription model, distribute through the Playgrounds app.
- iPad-only authoring tools — but books open on Mac in Xcode for review.
- **HIDDEN GEM**: Playground books can include **multiple localized voiceover scripts** — turn on VoiceOver and the lesson narrates differently per language.

## Cross-references

- See `swift4-language-codable.md` — Codable + KVO blocks integrate cleanly with the new test architectures.
- See `apfs-storage-system.md` — APFS clones make `xcodebuild clean` and CI sandbox setup faster.
