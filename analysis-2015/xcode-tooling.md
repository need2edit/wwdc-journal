# Xcode 7 Tooling — WWDC 2015 Analysis

**Sessions covered:** 104 (What's New in Xcode), 406 (UI Testing in Xcode), 410 (Continuous Integration and Code Coverage in Xcode), 412 (Profiling in Depth), 413 (Advanced Debugging and the Address Sanitizer), 405 (Authoring Rich Playgrounds), 402 (What's New in LLDB), 407 (Implementing UI Designs in Interface Builder)

## Headline

Xcode 7 brings UI Testing, code coverage, the Address Sanitizer, free provisioning (no developer account required to deploy to your own device), playgrounds with rich markup and explicit pages, and continuous integration via Xcode Server with bot triggers and a JSON+HTTPS API.

## Free Code Signing & Deployment

- For the first time, no Apple Developer Program membership is required to deploy to your own physical device. Sign in with any Apple ID; Xcode handles the certificate.
- Cannot publish to the App Store without the program; can deploy to devices you own for personal use, learning, school projects.

## UI Testing (406)

A new test target type. Tests run in a separate process from the app under test; access the app via Accessibility data.

### Three core APIs

- `XCUIApplication()` — launch (always spawns a fresh process), terminate, become a proxy for the app under test.
- `XCUIElement` — proxy for an accessible element. Backed by a query.
- `XCUIElementQuery` — a specification of which elements to find. Lazily evaluated on demand.

### UI Recording

Click the record button in the debug bar; interact with your app; Xcode synthesizes the code to reproduce the interactions. Then add `XCTAssert*` assertions for state validation.

### Element Hierarchy & Queries

- Elements form a tree: app → windows → views → controls.
- Three relationship operators: `descendants`, `children`, `containing`.
- Filter by type and identifier (or NSPredicate for partial matches).
- Convenience properties: `app.buttons` is shorthand for `app.descendantsMatchingType(.button)`.
- Chain queries: `app.tables.staticTexts["Groceries"]` finds the "Groceries" label inside any table descendant of the app.

### Element resolution rules

- Elements MUST resolve to a single match for event synthesis. If the query matches 0 or >1 elements, accessing the element raises a failure.
- Exception: the `exists` Boolean property tests presence safely.
- Queries are re-evaluated each access — a query that pointed to "apples" yesterday may point to "oranges" today after a deletion. Use `element(at: 0)` for index-based access only when the layout is stable.

### Accessibility quality determines test quality

The single most important takeaway: better accessibility data → easier tests, more reliable tests, AND a better experience for disabled users. Improving accessibility is a double win.

### Test Reports for UI Tests

- Per-step screenshots (auto-captured at significant moments).
- Hierarchical activity log: `tap` becomes (1) wait for app to idle, (2) compute query and resolve element, (3) synthesize tap, (4) wait for app to idle.
- Quick Look on any failure shows the actual screen state at that moment — solving the "multiple matches found" mystery instantly.

## Code Coverage (410)

- Built on LLVM instrumentation. Compiler counts every expression's execution.
- Enable in scheme → Test action → "Gather coverage data" checkbox.
- Coverage report: per-target, per-file, per-method coverage percentages.
- Click into source code: line-level annotations. Uncovered lines are gray; covered lines are white with execution counts.
- **HIDDEN GEM**: branch coverage shows partially covered conditionals (e.g., `func isEqual(other: Self?) -> Bool` where `return false` for the wrong-type branch was never tested).

### On Xcode Server

- Coverage trends over time as a chart alongside test count and issues.
- **HIDDEN GEM**: per-device coverage with diffs highlighted in orange. Identifies code paths that ONLY run on iPad vs ONLY run on iPhone.
- Pinpoints the exact integration that introduced new uncovered or newly-covered code.

## Continuous Integration (410)

Xcode Server (bundled with macOS Server) hosts bots:

- **Bot** = a recipe (scheme + target + schedule + actions) that integrates regularly.
- **Integration** = one execution of the bot. Each integration produces a report.
- **Triggers** can be `before integration` (after checkout, before build — modify project) or `after integration` (gated on result — notify, deploy).

### Triggers can be Swift!

- Email triggers: configurable based on environment variables.
- Script triggers: any language via the `#!` shebang. Default Bash; Swift is supported and demonstrated.
- Environment variables: `XCS_BOT_NAME`, `XCS_INTEGRATION_NUMBER`, `XCS_INTEGRATION_RESULT`, `XCS_SOURCE_DIR`, etc.

### Xcode Server REST API

- `https://server:20343/api/...`
- HTTPS + Basic Auth + JSON. REST verbs.
- `GET /api/bots`, `GET /api/bots/{id}/integrations`, `POST /api/bots/{id}/integrations` (trigger an integration).
- **HIDDEN GEM**: A button taped to your desk + a serial-port-listening Swift script + the API = "press the button, kick off an integration." Demonstrated on stage.

## Address Sanitizer (413)

- New in Xcode 7: `-fsanitize=address` runtime instrumentation.
- Detects: heap buffer overflows, stack buffer overflows, use-after-free, use-after-return, double-free, invalid free.
- Slowdown ~2-3x. Enable in Test scheme; disable in Release.
- **CRITICAL** for catching bugs that are hard to reproduce in normal debugging — randomly corrupted memory whose effect manifests far from the cause.

## Profiling in Depth (412)

- New consolidated Time Profiler enhancements: search, weight by self-time vs total time.
- New cost-attribution view: function tree per-thread.
- Specific recipes: profile launch (the new App Launch instrument), profile UI rendering (Core Animation), profile GPU work (new GPU Driver instrument).

## LLDB Improvements (402)

- Faster expression evaluation; better Swift support.
- `frame variable` (or `v`) inspects known variables without compiling an expression — much faster than `po` for everyday cases.
- Auto-completion in the LLDB prompt.
- Debugger commands accept Swift syntax.

## Playgrounds (405)

Major Xcode 7 upgrade:

- **Multi-page playgrounds**: a `.playground` is a folder; pages are sub-pages with their own code, can navigate between them.
- **Rich markup**: comments with `//:` (line) or `/*: ... */` (block) render as Markdown formatted prose.
- Resources: a Resources folder per playground; auxiliary code in Sources folder for reusable types.
- Inline `XCPlayground.XCPCaptureValue(_:value:)` for time series of computed values shown as a graph.
- Async playgrounds: `XCPlaygroundPage.currentPage.needsIndefiniteExecution = true`.

## Interface Builder (407)

- IB now does live previews of your custom views (with `IBInspectable` and `IBDesignable` from Xcode 6).
- Adaptive UI editor for size classes — choose a size class, edit constraints/properties, jump back to "any" for the universal layout.
- Stack View embed: select multiple views in the canvas, click the Embed in Stack View button (see `ipad-multitasking.md`).
- Custom segues, unwind segues, storyboard references all UI-driven.
- Auto Layout has new "Pin" and "Resolve Auto Layout Issues" menus with sensible defaults.

## On-Device Build & Run

- Plug in any iOS device; sign in with Apple ID; deploy. The certificate is provisioned automatically and rotated as needed.
- Profiles you can use for development without paying. Adoption: dramatically lower barrier to entry for new developers and students.

## Cross-references

- UI Testing (406) demands accessibility hygiene (201).
- Code coverage (410) plus Address Sanitizer (413) plus continuous integration (410) form the modern Xcode safety net.
- LLDB Swift improvements (402) plus playgrounds (405) plus Swift 2 (106) are the integrated developer experience around the language work.
