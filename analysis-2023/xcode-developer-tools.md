# WWDC 2023 — Xcode 15, Developer Tools, & Build System

Xcode 15 is the most polished release in years. String catalogs replace .strings files, asset catalogs back into Swift symbols, previews become macro-based, mergeable libraries change link-time behavior, and structured logging becomes a first-class console feature.

## Sessions Analyzed
- 10165 — What's new in Xcode 15 (gateway)
- 10252 — Build programmatic UI with Xcode Previews
- 10155 — Discover String Catalogs
- 10153 — Unlock the power of grammatical agreement
- 10244 — Create rich documentation with Swift-DocC
- 10268 — Meet mergeable libraries
- 10248 — Analyze hangs with Instruments
- 10226 — Debug with structured logging
- 10175 — Fix failures faster with Xcode test reports
- 10250 — Prototype with Xcode Playgrounds
- 10224 — Simplify distribution in Xcode and Xcode Cloud
- 10278 — Create practical workflows in Xcode Cloud

## Xcode 15: Smaller, Faster

- **Modular simulators**: All simulators (including iOS) are now optional downloads. Initial Xcode is a few GB instead of 10+ GB.
- **45% faster test reporting**: Test navigator rewritten in Swift.
- **Code completion** is dramatically smarter: file-name-based type suggestions, context-aware modifier suggestions (font for Text, padding for VStack), commonly-paired property suggestions (latitude → longitude).
- **Bookmarks navigator**: persistent bookmarks with descriptions, groupable, also supports BOOKMARKED FIND QUERIES (so a search becomes a refreshable list).
- **Source control**: redesigned changes navigator + commit editor with hunk-level staging directly inline.

## Asset Catalogs ↔ Swift Symbols

Color and image assets in `.xcassets` now generate Swift symbols. `Color.brandPrimary` and `Image(.heroLogo)` are TYPE-CHECKED. Renaming an asset causes a build error at every use site, with a fix-it.

The old `Color("brandPrimary")` string-keyed style still works but is no longer recommended.

## String Catalogs (.xcstrings)

A NEW localization format that replaces `.strings`, `.stringsdict`, AND localized storyboards in a SINGLE .xcstrings file per localizable bundle.

Conversion: Edit → Convert to String Catalog. Xcode migrates all your existing files.

Key features:
- Source strings extracted from `LocalizedStringResource` automatically every build.
- Per-language progress bar in the sidebar.
- Pluralization (replaces .stringsdict) handled inline with variations UI.
- Stale entries are auto-marked when source strings disappear.
- One file in source control, easy to diff.

This is the SINGLE biggest improvement to localization workflow in Apple's history.

### Grammatical Agreement (10153)

`Morphology` API in Foundation supports automatic gender/number/case agreement in localized strings (initially Spanish, more languages added over time). Lets you write `^[the apple](inflect: true)` and have it become "la manzana" in feminine context.

## #Preview Macro (Replaces PreviewProvider)

```swift
#Preview { ContentView() }
#Preview("Empty State") { ContentView(items: []) }
#Preview("Dark mode", traits: .sizeThatFitsLayout) {
  ContentView().preferredColorScheme(.dark)
}

// Widget previews:
#Preview(as: .systemMedium) { MyWidget() } timeline: { dateOne, dateTwo, dateThree }
```

`#Preview` works for SwiftUI, UIKit (`UIViewController`), AND AppKit. Widgets get a proper TIMELINE preview that animates between entries.

## Macro Quick Actions

Press Cmd-Shift-A → "New Swift Macro Package" to scaffold a macro package with the canonical `#stringify` example, a unit test, and a working compiler plugin target. This is the fastest path to your first macro.

You can right-click any macro use site → Expand Macro to see generated source. Errors in expanded code show the expansion in the diagnostic.

## Mergeable Libraries (10268)

A new build setting (`MERGEABLE_LIBRARY = YES`) lets dynamic frameworks be merged at link time into a single binary. Why this matters:
- DEBUG: keep dynamic linking for fast incremental builds.
- RELEASE: merge for fast launch (avoids dyld load cost) — like static libraries.
- BEST OF BOTH: same target topology in both configs, just toggle.

Major win for apps with 30+ frameworks. Launch speedups of 1.5x–3x have been reported. To adopt:
1. Set `MERGEABLE_LIBRARY = YES` on libraries.
2. Set `MERGED_BINARY_TYPE = automatic` on the app target.
3. Profile launch time before/after.

This was previously an iOS dyld feature; now it's a developer-facing toggle.

## Structured Logging in the Console (10226)

`OSLog` integration in Xcode 15's console:
- Each log line shows subsystem, category, severity (with color background).
- Filter on metadata fields (`subsystem == "com.app"`, `severity >= info`).
- Click a log line to JUMP TO THE LINE OF SOURCE that emitted it.
- Privacy redaction respected (`<private>` for unmarked dynamic strings).

Best practice:
```swift
let logger = Logger(subsystem: "com.app.network", category: "request")
logger.info("Loaded \(items.count, privacy: .public) items for \(url, privacy: .private)")
```

Use `Logger`, NOT `print`. `os_signpost` integrates with Instruments for performance regions.

## Test Reports (10175)

Major redesign:
- Insights tab: pattern-based correlation across failures (e.g., "all failures involve French locale + iPad").
- Per-test detail view with breakdown across destinations and configurations.
- UI test failures get a video timeline with scrubbable playback and OVERLAID touch points.
- At point of failure: full UI hierarchy of the app under test.

Hangs are reported with stack traces of the main thread captured by the test runner.

## Hangs Instrument (10248)

A new Instruments template specifically for hang analysis. Captures:
- Microhangs (visible jank, 250ms–1s)
- Hangs (≥1s)
- Backtrace at hang time
- Disk + CPU + memory contention overlays

Recommended workflow: profile a real device under realistic conditions, look for "expected" hangs (synchronous work on main), then use the call tree to push work off main.

## Xcode Cloud (10278, 10224)

- Notarization is now a built-in post-action.
- TestFlight test notes can ship with the source code.
- Internal-only TestFlight distribution (won't accidentally release to external testers).
- New common workflow templates for "Test a PR", "Nightly build", "Release candidate".
- Desktop notifications when builds complete.

Test plans now support per-configuration code coverage targets in Cloud.

## Xcode Playgrounds (10250)

- Playgrounds in projects (not just standalone) are properly supported again.
- Quick prototype views without launching the full app.
- Live Views work with SwiftUI.
- Limitations: no debugger, single-target context only.

## Swift-DocC (10244)

- Real-time documentation preview in an editor split (Editor → Assistant → Documentation Preview).
- Custom themes via JSON config.
- Improved support for tutorials and structured documentation.
- Better handling of cross-module symbol references.

## Pathways

- **New Xcode features tour**: 10165 → 10155 → 10252
- **Performance debugging**: 10248 → 10226 → 10175
- **CI/CD setup**: 10224 → 10278
- **Documentation author**: 10244

## Hidden Gems

- Code completion now uses the FILE NAME to suggest the type name when you start `struct` — a small thing that saves keystrokes thousands of times a year.
- Bookmarked Find queries can be REFRESHED with one click, giving you a live "list of all TODOs" or "all sites of a deprecated API" without rerunning search.
- The new commit editor lets you stage individual hunks WITHOUT leaving the editor; no need for `git add -p` muscle memory.
- `MERGEABLE_LIBRARY = YES` requires the framework to NOT be linked from outside the merging target — it becomes effectively private.
- `os.Logger` automatically captures the file/line/function — you don't need to include them in the message.
- String catalogs let you mark strings as "Don't translate" — useful for brand names that should stay in English.
- The simulator runtime download is now ON-DEMAND: Xcode prompts you when you target a platform you haven't downloaded yet.
- Test report's "Insights" can save HOURS in flaky-test investigations by surfacing pattern correlations you'd miss reading individual failure messages.
- `#Preview` macro inside an extension on a type produces a preview scoped to that file's symbol scope — clean separation from production code.
