# Xcode 11, Testing & Developer Tooling — WWDC 2019 Analysis

**Sessions covered:** 401 (What's New in Xcode 11), 405 (Swift Playgrounds 3), 412 (Debugging in Xcode 11), 413 (Testing in Xcode), 418 (Getting the Most Out of Simulator), 233 (Mastering Xcode Previews), 408 (Adopting Swift Packages in Xcode), 410 (Creating Swift Packages), 416 (Binary Frameworks in Swift), 403 (Creating Great Localized Experiences with Xcode 11), 411 (Getting Started with Instruments), 421 (Modeling in Custom Instruments), 429 (LLDB: Beyond "po"), 414 (Developing a Great Profiling Experience)

## Headline

Xcode 11 is one of the largest releases ever: **SwiftUI Previews**, **Swift Package Manager integration**, **multi-window editor**, **minimap**, **Test Plans**, **on-device builds without a tethered Mac**, **iPad Simulator on Mac**, **simulator multi-touch on Mac trackpad**, and **dramatically improved code completion**.

## SwiftUI Previews (233, 401)

Covered in detail in `swiftui-debut.md`. Key Xcode features:
- Live preview compiles your file separately and dynamically replaces in the running app.
- Literal-only changes inject instantly without recompile.
- "Pin" a preview to keep it visible while editing other files.
- Development Assets group (target settings) — preview-only assets stripped from production.

## Multi-Window Editor (401)

- Tabs, split editors (horizontal and vertical), and detached windows.
- Each editor has its own jump bar, history, and inspector.
- Right-click the editor jump bar → "Open in Assistant" / "Open in Tab" / "Open in New Window".
- **HIDDEN GEM**: Cmd-click the jump bar arrows to add a new editor; Option-click to open in assistant.

## Minimap (401)

- View → Show Minimap. Right-side gutter showing the file at-a-glance.
- Highlights for: errors, warnings, breakpoints, search results, the current selection, marks (`// MARK: -`).
- Cmd-click in the minimap to navigate.

## Test Plans (413)

- **Test Plans** (`.xctestplan`) — one shared definition of how to run tests across many configurations.
- Config dimensions: localization, language, regions, environment variables, arguments, sanitizers, code coverage, threading checker, screen captures.
- Run a test plan in CI with one config, in dev with another. No more juggling schemes per environment.
- **HIDDEN GEM**: a single test plan can run the same tests under multiple localizations / device sizes / sanitizer settings in one CI job.

## Better Code Completion (401)

- **Improved ranking** — most-relevant suggestions first based on context.
- **Image autocompletion** — `UIImage(named: "asset_name")` autocompletes from your Asset Catalog. Same for `Color(named:)`, `Localizable.strings` keys, segue identifiers.
- **Documentation popovers** — Quick Help inline.

## Source Control (401)

- **Multi-repo workspaces** — manage several Git repos in one project.
- **Visualize branches** in the source control navigator.
- **Stash** support inline.
- **Cherry-pick** in the UI.
- **GitHub integration** — Xcode pushes new repositories to GitHub directly from the Source Control menu.

## On-Device Builds for iPad (401, 405)

- Connect any iPad over Wi-Fi (no USB cable required after pairing).
- Pair via Window → Devices and Simulators → "Connect via network" checkbox.
- iPad apps can be debugged wirelessly.

## iPad Simulator on macOS Catalina (418)

- Simulator runs natively at full resolution including Apple Pencil and trackpad input simulation.
- Launch with multiple simulators side-by-side.
- New Simulator features:
  - **Drag external files into the simulator** — they appear in Files app.
  - **Pasteboard sync** between Mac and Simulator.
  - **Send Push Notifications** — drag an APNs payload `.json` onto the simulator window.
  - **`xcrun simctl push <udid> <bundle_id> <payload.json>`** — programmatic push from Terminal.
  - **`xcrun simctl status_bar`** — set the status bar to a fixed time/battery for screenshots.
  - **`xcrun simctl io <udid> recordVideo`** — record sim screen.
- **HIDDEN GEM**: drag a `.geojson` file onto the simulator → Maps app uses it as a simulated route.

## Debugging in Xcode 11 (412)

- **View Debugger** for SwiftUI shows your declarative tree.
- **Memory graph debugger** improvements: detect stub-leaks earlier, graph cycles visually.
- **Network debugging** — Network Link Conditioner integrated into Devices window.
- **Background queue summary** — see what's running on every dispatch queue.

## Localization with Export/Import for Localizers (403)

- Export localizations as XLIFF (industry standard).
- New "Export for Localization" includes asset catalog strings and storyboards.
- Pseudo-localization (Settings → Developer → Pseudolanguage) tests right-to-left and string expansion without real translations.
- **HIDDEN GEM**: SwiftUI auto-localizes string literals in `Text` (see SwiftUI analysis).

## Swift Playgrounds 3 (405)

- iPad Playgrounds 3 supports custom modules, full XCTest, source control via GitHub.
- Build full apps in iPad Playgrounds (no Mac required) — foreshadows Swift Playgrounds 4 (2021) which adds App Store deployment from iPad.

## Testing Improvements (413)

- **Random test order** — `XCTestRunOrder` setting for shuffled order, surfacing test interdependencies.
- **Parallel testing** — run tests in parallel across multiple simulators.
- **Result Bundles** — `.xcresult` bundle format with rich data (logs, screenshots, attachments).
- **`XCTAttachment`** — attach images, files, or arbitrary data to test results.
- **`XCTSkip`** — skip tests with a reason instead of failing or commenting out.

## Developing a Great Profiling Experience (414)

For framework authors:
- Mark hot functions with `@inlinable` and `@inline(__always)` carefully.
- Use `OSLog` and `os_signpost` for first-class profiler integration.
- Build custom Instruments (.instrument package) for your domain.
- Document your performance characteristics with measurable claims (X% faster, Y MB allocated).

## Cross-references

- Property wrappers and opaque return types underpin SwiftUI Previews: 402, 415.
- Performance tools deep dive: 411, 421, 423, 417.
- Simulator features: 418, 707 (background tasks via simctl push).
