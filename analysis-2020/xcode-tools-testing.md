# WWDC 2020 — Xcode 12, Tooling, Testing, Performance

WWDC 2020's developer tools story: Xcode 12 with redesigned UI, **multi-platform app templates**, dramatically improved Swift code completion, **animation hitch detection** in XCTest, **MetricKit improvements**, **Swift Package Manager additions**, and a refined Instruments toolset.

## Sessions Analyzed
- 10076 — Diagnose performance issues with the Xcode Organizer
- 10077 — Eliminate animation hitches with XCTest
- 10081 — What's new in MetricKit
- 10091 — Write tests to fail
- 10164 — XCTSkip your tests
- 10185 — Visually edit SwiftUI views (covered in swiftui-2-foundation.md)
- 10219 — Build localization-friendly layouts using Xcode
- 10220 — Handle interruptions and alerts in UI tests
- 10221 — Get your test results faster
- 10647 — Become a Simulator expert
- 10649 — Add custom views and modifiers to the Xcode Library
- 10654 — Create Swift Playgrounds content for iPad and Mac
- 10078 — Why is my app getting killed?
- 10057 — Identify trends with the Power and Performance API
- 10687 — Triage test failures with XCTIssue
- 10643 — Build a SwiftUI view in Swift Playgrounds

## Xcode 12 Visual Refresh & Multi-Platform Templates

Xcode 12 ships with the macOS Big Sur design language: rounded sidebars, integrated toolbar with the new title style, refreshed iconography. Functionally:
- **Multi-platform App template** auto-creates groups for shared code, iOS-specific, and macOS-specific code/assets
- **Document App** template for `DocumentGroup`-based apps
- **App Clip** template for the new App Clip target type

## Code Completion: 15× Faster

The headline tooling improvement. Common SwiftUI completions that took ~0.5s in Xcode 11.5 now take under 0.1s. The compiler's diagnostic engine also improved dramatically — SwiftUI errors that were inscrutable now point to the exact problem with actionable fix-its.

## Animation Hitch Detection (10077)

XCTest can now measure **animation hitches** — frames where animation didn't render in time. Use the `XCTOSSignpostMetric.animationHitchTimeRatio` metric in performance tests:

```swift
func testScrolling() {
  measure(metrics: [XCTOSSignpostMetric.scrollingDecelerationHitchTimeRatio]) {
    // Trigger scroll
  }
}
```

The Xcode test report includes hitch counts, hitch durations, and the percentage of frames affected. Backed by **OS signposts** that the system emits during animation; no instrumentation needed in your code.

## MetricKit Improvements (10081)

MetricKit (the framework that delivers daily app performance reports from real users) gained:
- **Diagnostic payloads** for crashes and hangs — get crash logs and hang reports from production users
- **Custom signposts** appear in MetricKit reports
- **CPU exception reporting** — when your app gets killed for CPU usage, MetricKit tells you why
- **Disk write reporting** — surface unexpected I/O hot paths

Adopt by conforming to `MXMetricManagerSubscriber` and registering with `MXMetricManager.shared`. Implement `didReceive(_:)` to handle `MXMetricPayload`s and the new `MXDiagnosticPayload`s.

## Why Is My App Getting Killed? (10078)

Detailed coverage of jetsam (memory-pressure kills), CPU exceptions, watchdog timeouts, and other process-termination scenarios. Tools to diagnose:
- **MetricKit diagnostic payloads** for production
- **Xcode debug navigator** Memory gauge with detailed breakdowns
- **Instruments Allocations** + Generations to track per-cycle leaks
- **VM Tracker** for virtual memory issues
- **Energy Log** for unexpected wakeups

## Diagnose Performance with Xcode Organizer (10076)

The Xcode Organizer collects metrics from real users (opt-in) and surfaces:
- Launch time histograms
- Hang rate
- Disk write rate
- Battery usage by app
- Scroll hitch rate

You can compare versions to see if a regression landed. **Filter by device type, OS version, and country** to spot localized issues. Recommended workflow: every release, check Organizer for regressions before it hits a wide audience.

## Power and Performance API (10057)

Programmatic access to the same metrics the Organizer shows. Useful for:
- Automated performance regression testing
- Internal dashboards
- Anomaly detection on production deployments

## Testing Improvements

### XCTSkip (10164)

`XCTSkip` is the explicit way to skip tests with a reason — better than commenting them out:

```swift
func testNetworkFeature() throws {
  try XCTSkipUnless(NetworkAvailable(), "Requires network")
  // test
}
```

Skipped tests appear distinctly in test reports — neither pass nor fail.

### XCTIssue / Triage (10687)

The new `XCTIssue` API replaces the older `recordFailure(...)` boilerplate. Provide a richer issue with type (assertion, performance, crash, error), severity, source location, and attached files. Test reports show structured issues with screenshots, logs, and reproduce steps.

### Faster Test Results (10221)

Test result archives stream now — Xcode shows results as they happen rather than after the whole run. Particularly helpful for long UI test runs. Build settings let you parallelize tests across simulators.

### Handle Interruptions in UI Tests (10220)

The notorious "interruption monitor" pattern got better APIs:
```swift
let monitor = addUIInterruptionMonitor(withDescription: "Permission") { alert in
  alert.buttons["Allow"].tap()
  return true
}
// ... test continues; monitor fires when alert appears
removeUIInterruptionMonitor(monitor)
```

Plus better expected-failure handling (`XCTExpectFailure(_:enabled:strict:)`) for known-flaky tests.

### Write Tests to Fail (10091)

Conceptual session on test design: tests should aim to **find bugs**, not confirm correctness. Mutation testing, boundary-condition focus, fail-loud assertions over silent skips. The session's mantra: a passing test that doesn't catch the bug-you-care-about is worthless.

## Simulator Improvements (10647)

Xcode 12's Simulator:
- **Recordings** save as videos directly
- **Pointer simulation** for testing iPadOS pointer code
- **Faster boot** for new simulator types
- **Always-on `simctl`** command-line for scripting
- **Push notifications** can be triggered from a `.apns` file dragged onto the simulator

## Localization-Friendly Layouts (10219)

Tooling support for catching localization issues at design time:
- **Pseudo-language** previews — Double-Length, Right-to-Left modes in Interface Builder previews and at runtime via scheme options
- **Auto Layout fix-its** in Interface Builder — "Add missing constraints", "Set Constraint ≥ Minimum Width"
- **Embed in Stack View / Grid View** — modern container that handles localization-driven size changes
- **Localizer hint** field in the identity inspector for context comments to translators

Practical patterns:
- Avoid fixed widths/frames on text-bearing controls
- Avoid fixed spacing between distant elements (use stacks or `≥` constraints)
- Allow text to wrap to multiple lines
- Always test in Pseudo-language mode

## Custom Xcode Library Items (10649)

Add your own SwiftUI views and modifiers to the Xcode Library so they appear in the canvas's drag-drop palette:

```swift
struct MyLibraryContent: LibraryContentProvider {
  var views: [LibraryItem] {
    [LibraryItem(MyButton(title: "Tap"), title: "My Button", category: .control)]
  }
  func modifiers(base: MyView) -> [LibraryItem] {
    [LibraryItem(base.myModifier())]
  }
}
```

Critical for design-system / component-library teams.

## Swift Playgrounds 4 (10643, 10654)

Build Swift Playgrounds **content** (interactive lessons) for iPad and Mac. The content authoring uses the new content authoring extensions; Playgrounds themselves can include cuts, hints, fix-its, and run-only-this-section affordances. Useful for educational apps, internal training, sample-code distribution.

## Cross-References
- [swift-5.3-language.md](swift-5.3-language.md) — Logger replacements, Standard Library wins.
- [swiftui-2-foundation.md](swiftui-2-foundation.md) — Visually editing SwiftUI views and previews.
- [media-hls-audio.md](media-hls-audio.md) — Demystify hitches in render phase tech talks (10855, 10856, 10857) complement these.

## Adoption Checklist
- [ ] Adopt MetricKit's diagnostic payloads — get production crash and hang reports.
- [ ] Use `XCTSkip` to clean up skipped tests with reasons.
- [ ] Integrate `XCTOSSignpostMetric.scrollingDecelerationHitchTimeRatio` into perf tests.
- [ ] Run Pseudo-language mode previews on every screen.
- [ ] Use the modern `XCTIssue` API in custom test helpers.
- [ ] Watch the Xcode Organizer per release for regressions.
- [ ] Parallelize UI tests across simulators if you have a CI bottleneck.
- [ ] Investigate why-is-my-app-being-killed reports for any production crashes.
- [ ] Migrate hand-rolled stack code to `UIStackView` / `UIGridView` for layout robustness.
