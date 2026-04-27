# DocC: Documentation Compiler Debut (WWDC 2021)

A brand-new documentation compiler from Apple, integrated into Xcode 13. Built around triple-slash Markdown comments, with separate authoring formats for articles and step-by-step tutorials. Open-sourced later in 2021.

## Sessions covered
- WWDC21-10166 — Meet DocC documentation in Xcode
- WWDC21-10167 — Elevate your DocC documentation in Xcode
- WWDC21-10235 — Build interactive tutorials using DocC
- WWDC21-10236 — Host and automate your DocC documentation
- WWDC21-10244 (Note: 2023 session — included as historical cross-ref)

## Best practices

- **Document `public` and `open` symbols**; DocC only generates pages for those. Internal/private symbols are correctly excluded (WWDC21-10166).
- **Triple-slash `///`** for line-style, **`/** ... */`** for block-style. The compiler treats them identically (WWDC21-10166).
- **First line is the summary**, blank line, then **Discussion** section. Markdown fenced code blocks render as syntax-highlighted Swift (WWDC21-10166).
- **Symbol links: double-backticks**. ``` ``Habitat/comfortLevel`` ``` produces a clickable cross-reference that survives symbol renames (WWDC21-10166).
- **Use `Add Documentation` in the Action menu** (Cmd-click → Add Documentation) — Xcode generates the parameter/returns scaffolding for you (WWDC21-10166).

## Hidden gems

- DocC was open-sourced in late 2021. The CLI plus a static-site web app (`Swift-DocC-Render`) is on github.com/apple/swift-docc — you can render archives outside Xcode (WWDC21-10166, WWDC21-10236).
- A `.doccarchive` is BOTH a self-contained web app AND viewable directly inside Xcode — double-click to open (WWDC21-10166).
- Tutorials are an entirely separate authoring format with their own `.tutorial` extension. Step-by-step interactive walkthroughs with code-and-screenshot pairs (WWDC21-10235).
- `xcodebuild docbuild` runs the same DocC compile as the menu item — drop into Xcode Cloud or any CI to publish docs (WWDC21-10166, WWDC21-10236).
- DocC builds documentation **for every imported Swift framework** in your build graph — open the docs window in your app project and you see your dependencies' docs (WWDC21-10166).
- Quick Help in source editor now has an "Open in Developer Documentation" button that jumps to the full page (WWDC21-10166).
- A documentation catalog (`.docc` directory) holds:
  - `*.md` articles (long-form prose)
  - `*.tutorial` files (interactive lessons)
  - `Resources/` for images
  - A landing page article matching your module name (WWDC21-10167).

## Performance

- Build setting `DOCC_RENDER_DURING_BUILD=YES` rebuilds docs on every compile — useful if you're authoring; default is off so day-to-day builds aren't slowed (WWDC21-10166).

## Migration guidance

- If you've been using Jazzy or another doc generator: DocC consumes your existing triple-slash `Parameters:`/`Returns:`/`Throws:` directly. Switching is mostly free; the rendered output looks like Apple's official documentation (WWDC21-10166).
- DocC is bundled with Swift starting with Swift 5.5; you get it whether or not you build with Xcode (WWDC21-10166).

## Cross-references

- DocC's article format reuses Markdown extensions specific to Apple's docs (e.g., `## Topics`, `### Essentials`).
- Subsequent years' DocC sessions refine: 2022 adds custom theming, 2023 adds Swift-DocC plugin support for SwiftPM, 2024 adds redirects.
