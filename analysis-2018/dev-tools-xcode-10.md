# Xcode 10 Developer Tools — WWDC 2018 Analysis

**Sessions covered:** 408 (Building Faster in Xcode), 415 (Behind the Scenes of the Xcode Build Process), 410 (Creating Custom Instruments), 405 (Measuring Performance Using Logging), 412 (Advanced Debugging with Xcode and LLDB), 414 (Understanding Crashes and Crash Logs), 417 (Testing Tips & Tricks), 403 (What's New in Testing), 418 (Source Control Workflows in Xcode), 411 (Getting to Know Swift Package Manager), 402 (Getting the Most out of Playgrounds in Xcode), 404 (New Localization Workflows in Xcode 10), 413 (Create Your Own Swift Playgrounds Subscription), 102 (Platforms State of the Union §Tools)

## Headline

Xcode 10 is the **performance and productivity** release. Build times often 2× faster (3× for pure Swift), tests can fan out across simulator clones for ~4× faster runs, the new modern build system is on by default with better task parallelization, multi-cursor editing arrived (option-click for column, control-shift-click for arbitrary additional cursors), Xcode finally supports dark mode (when running on Mojave), source control change-bar and rebase support landed, and the brand-new `os_signpost` API + Custom Instruments package format unlock a whole new class of measurement and analysis you can ship.

## Build Speed (408, 415, 102)

- 2× faster Debug builds on representative apps; 3× on pure-Swift targets.
- The win came from Apple realizing Swift's whole-module visibility was causing _redundant_ work across files. The pipeline now shares more work and parallelizes per-file better.
- New build system (introduced as preview in 2017) is now **on by default** for all projects. Better task parallelization, smaller memory footprint, richer diagnostics.
- **DEPRECATION**: the "whole-module + no optimization" Debug-build hack is no longer beneficial — it actively hurts incremental builds. Set Compilation Mode = `incremental` for Debug.

## Multi-Cursor Editing (102)

- Option-drag to make a column selection.
- Control-shift-click to add cursors at arbitrary positions.
- Type once → all cursors get the change. Game-changer for repetitive edits like converting `let` to `var` across 8 stored properties.

## Source Control Change Bar (102, 418)

- Left of the line numbers, a new gutter shows: blue stripe = changed since last checkout, red = conflicts with upstream.
- Click a stripe → contextual menu with description + actions (discard, pull upstream, etc.).
- Cleaner than the older "tool-tip on hover" pattern.
- New: pull with rebase (no more spurious merge commits when your branch is one commit behind), Bitbucket Cloud + Server, GitLab.com + self-hosted integrations.
- Xcode generates SSH keys and uploads to your service automatically.

## Test Parallelism (102, 403, 417)

- Xcode 10 clones simulators (or Mac app processes) and fans test suites out across them. **~4× faster** XC tests on a multi-core Mac.
- Behind a checkbox in the scheme: Test → Options → Execute in Parallel.
- Test plans (.xctestplan) finally landed: one set of tests run under multiple configurations (locales, sanitizers, screenshots) without duplicating schemes. (More mature in 2019.)

## Code Coverage Improvements (403)

- Coverage reports now scopable to specific targets (no more 50% coverage that's mostly framework noise).
- `xccov` command-line tool exposes coverage data for CI dashboards.
- Random test execution order option to catch accidental order dependencies between tests.

## Memory Debugging (102, 416)

- Xcode catches `EXC_RESOURCE` exceptions and pauses your app — start the Memory Debugger from the crash point.
- Memgraph file format now usable from command-line tools: `vmmap`, `heap`, `leaks`, `malloc_history`. (See `ios-12-performance.md`.)
- Compact layout in the Memory Debugger handles much larger graphs than 2017's UI.

## LLDB Improvements (412)

- Faster startup. Variables view + console "po" both faster on access.
- More precise variable inspection — fewer "<unavailable>" results in optimized builds.
- Debug-symbol downloads from Apple's symbol server are 5× faster (seconds, not minutes).

## Energy Diagnostic Reports (102, 228)

- Like crash logs, but for **energy usage**. Auto-collected on iOS for TestFlight + App Store apps. Surfaces foreground vs. background drain, with stack frames pointing at the offending code.
- Show up in the Xcode Organizer alongside crash reports.
- Open in your project to navigate directly to the offending lines.

## os_signpost + Custom Instruments (405, 410, 102)

The biggest single tools investment of the year:

- New `os_signpost` API: emit named begin/end intervals or points-of-interest events from your code. Format strings can capture variables (`%lu`, `%{public}s`) for richer instrumentation than `printf`.
- Special category `OSLog.Category.pointsOfInterest` is auto-shown by Instruments in a dedicated lane.
- New "Instruments Package" Xcode project: define schemas, modelers, graph templates, table aggregations in XML. Modelers can be production-rule expert systems written in Clips that detect application-specific anti-patterns automatically.
- The `<os-signpost-interval-schema>` element auto-generates a modeler from signpost names — for simple cases you write zero Clips code.
- Apple's own instruments (Time Profiler, System Trace, Game Performance, Network Connections) are now built on the same Standard UI + Analysis Core that you have access to.

## Build Reports & Diagnostics (415)

- Build timing reports: per-task duration, dependency graph (so you can see why your slow Swift target was waiting on a slow Obj-C target).
- "Show in Build Log" reveals the exact Swift / clang command line invoked.
- Useful for hunting down "why does this one file take 30 seconds to compile" — usually deeply-nested generics or chained higher-order functions Swift's type-checker chokes on.

## Crash Logs Demystified (414)

- Symbolication: dSYMs uploaded with TestFlight builds make crash logs human-readable in Xcode Organizer.
- New `MetricKit`-style energy reports complement crash logs.
- Watchdog termination logs (`0x8badf00d`, `0xdeadfa11`) explained in detail. Most are launch-time too-slow violations or main-thread blocking.

## Localization Workflows (404)

- Stringsdict for plurals (already covered in `notifications-grouped.md`).
- Xcode 10 export/import format for localizations is XLIFF — broadly supported by translation services.
- Pseudo-localization for QA: append accented characters and brackets to surface untranslated strings and clipped layouts.

## Xcode Playgrounds (102, 402)

- Continuous run mode (REPL-like): Shift-Enter on a new line evaluates without restarting the Playground session. Massive speedup for exploratory work.
- `import CreateMLUI; let builder = MLImageClassifierBuilder(); builder.showInLiveView()` — drag-and-drop ML training inside the Playground (see `create-ml-core-ml-2.md`).

## Swift Playground Subscriptions (413)

- Apps in the App Store can now ship Swift Playgrounds modules to the iPad Swift Playgrounds app via Subscriptions.
- Authoring tooling for assessment, exercises, code completion hints.
- Curated educational use case but the API is general.

## Swift Package Manager (411)

- Xcode 10 doesn't yet integrate SPM into project workflows (that arrives in Xcode 11). For 2018: SPM is CLI-driven for command-line tools and packages.
- `swift package generate-xcodeproj` produces a one-off .xcodeproj for SPM-managed projects.
- Schema 4.2 brings per-target Swift language version and system-library dependencies.

## Cross-references

- Performance methodology with these tools: 407 (covered in `ios-12-performance.md`).
- Custom Instruments deep dive: 410 (full session).
- Signpost API examples: 405 walks through the Trailblazer demo app start-to-finish.
