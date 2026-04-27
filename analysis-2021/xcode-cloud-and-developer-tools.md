# Xcode Cloud & Developer Tools (WWDC 2021)

Xcode Cloud's debut: an Apple-hosted CI/CD product integrated into Xcode and App Store Connect. Plus a wide set of Xcode 13 productivity wins.

## Sessions covered
- WWDC21-10267 — Meet Xcode Cloud
- WWDC21-10268 — Explore Xcode Cloud workflows
- WWDC21-10269 — Customize your advanced Xcode Cloud workflows
- WWDC21-10204 — Distribute apps in Xcode with cloud signing
- WWDC21-10205 — Review code and collaborate in Xcode
- WWDC21-10209 — Discover breakpoint improvements
- WWDC21-10202 — Detect bugs early with the static analyzer
- WWDC21-10203 — Triage TestFlight crashes in Xcode Organizer
- WWDC21-10207 — Embrace Expected Failures in XCTest
- WWDC21-10212 — Analyze HTTP traffic in Instruments
- WWDC21-10210 — Explore advanced project configuration in Xcode
- WWDC21-10211 — Symbolication: Beyond the basics
- WWDC21-10180 — Detect and diagnose memory issues
- WWDC21-10181 — Ultimate application performance survival guide
- WWDC21-10258 — Understand and eliminate hangs from your app
- WWDC21-10296 — Diagnose unreliable code with test repetitions
- WWDC21-10208 — Explore Digital Crown, Trackpad, and iPad pointer automation
- WWDC21-10261 — Faster and simpler notarization for Mac apps
- WWDC21-10170 — Meet TestFlight on Mac

## Best practices

- **Cloud signing**: stop managing provisioning profiles by hand. Xcode Cloud handles signing automatically based on the action (TestFlight Internal, External, App Store) (WWDC21-10204, WWDC21-10267).
- **Deploy to internal testers from pull-request workflows**, not just `main`. PR builds without Clean=YES are deployable to internal-team TestFlight groups (WWDC21-10268).
- **Use a separate "Releases" workflow** with `Clean=YES`, pinned Xcode/macOS versions, and TestFlight External + App Store deployment. Builds intended for App Review must be from a clean build (WWDC21-10268).
- **Auto-cancel previous PR builds** in start conditions — saves machine minutes when force-pushing (WWDC21-10268).
- **Set environment variables, mark secrets** — never hardcode API keys or tokens in your scripts (WWDC21-10269).

## Hidden gems

- Xcode Cloud's source code is **never persisted** — fetched into a temporary build environment per build, torn down after. Build artifacts go to a dedicated CloudKit DB encrypted at rest (WWDC21-10267).
- `ci_post_clone.sh`, `ci_pre_xcodebuild.sh`, `ci_post_xcodebuild.sh` are the three custom-script extension points — drop them in your repo's `ci_scripts/` directory (WWDC21-10269).
- **TestFlight on Mac** is now a thing — same product as iOS, but your Mac app needs to be a Mac Catalyst, native macOS, or Designed-for-iPad build (WWDC21-10170).
- Notarization for Mac: `xcrun notarytool` replaces `altool` — submission and waiting in a single command, much faster (WWDC21-10261).
- `XCTExpectedFailure` — finally a way to say "this test is broken, but I want to track regressions on the OPPOSITE" without disabling it. Tests that pass while marked expected-fail surface as "unexpected pass" warnings (WWDC21-10207).
- `XCUITest` test repetitions: rerun a flaky test up to N times, with strategies (until-success, retry-on-failure, every-time) (WWDC21-10296).
- DocC: documentation is now a first-class build product. `xcodebuild docbuild` produces a `.doccarchive` you can host on the web (WWDC21-10166, WWDC21-10236).
- Static analyzer: now catches **out-of-bounds-style memory access** and **API misuse** patterns the compiler can't (WWDC21-10202).
- Breakpoint columns: column-based breakpoints for one-line conditional expressions (WWDC21-10209).

## Performance

- The new HTTP Traffic instrument taps into URLSession with no setup — drag onto a process and you immediately see HTTP/3 vs HTTP/2 vs HTTP/1.1 transactions, request/response sizes, headers (WWDC21-10212, WWDC21-10094).
- Hangs: the new MetricKit hang reports collect **call trees aggregated across all hits in the field**. Triage in the Xcode Organizer Performance tab. Hang rate is now a tracked metric per app version (WWDC21-10258).
- For hang root causes: the most common are **synchronous I/O on main**, **dispatch_sync to a contended queue**, and **CGContext.draw with rounded corners** (use CALayer.cornerRadius instead, GPU-accelerated) (WWDC21-10258).

## Migration guidance

- The `LIBDISPATCH_COOPERATIVE_POOL_STRICT=1` env var asserts on Swift Concurrency forward-progress violations — use it during testing to catch semaphore-on-async bugs early (WWDC21-10254, WWDC21-10258).
- Symbolication: ship dSYMs to the Xcode Organizer (or App Store Connect for upload-symbols) so TestFlight crash logs symbolicate automatically (WWDC21-10211, WWDC21-10203).

## Cross-references

- Xcode Cloud workflows can be created and managed entirely from App Store Connect (web) for users without Xcode access (e.g., QA team members) (WWDC21-10267).
- The "Customize your advanced Xcode Cloud workflows" session (WWDC21-10269) covers REST API access, scripts, and integration with Slack/Jira/email.
