# Xcode 6, Tools & Testing — WWDC 2014 Analysis

**Sessions covered:** 401 (What's New in Xcode 6), 411 (What's New in Interface Builder), 412 (Localizing with Xcode 6), 413 (Debugging in Xcode 6), 414 (Testing in Xcode 6), 415 (Continuous Integration with Xcode 6), 416 (Building Modern Frameworks), 418 (Improving Your App with Instruments), 417 (What's New in LLVM)

## Headline

Xcode 6 ships alongside Swift, the new SDKs, and a stack of developer-tool improvements: **Live Rendering in Interface Builder**, **Resizable Simulators**, **Asset Catalogs with size-class variants**, **iOS Embedded Frameworks**, **Performance Tests in XCTest**, **OS X Storyboards**, **Continuous Integration in Xcode Server**, and a redesigned **Instruments**.

## Live Rendering in Interface Builder (session 411)

- **`@IBDesignable`** on a `UIView`/`NSView` subclass: Interface Builder builds the framework containing the class, runs the view's drawing live in the IB canvas. See custom views render in the storyboard while you design.
- **`@IBInspectable`** on a property: appears in the Attributes Inspector. Backed by user-defined runtime attributes — no encoding/decoding code required.
- HIDDEN GEM: `prepareForInterfaceBuilder()` is called by IB after init but only at design time. Use to inject placeholder data, sample images, fake state — your runtime stays clean (411).
- HIDDEN GEM: **debug your IB-rendered view** — set a breakpoint, choose Editor → Debug Selected Views, Xcode attaches the debugger to IB's helper process (411).
- HIDDEN GEM: `IB_PROJECT_SOURCE_DIRECTORIES` environment variable in IB's helper points to your project root — load placeholder assets from there during `prepareForInterfaceBuilder` without bundling them in your app (411).
- WARNING: live rendering requires your custom class to live in a **framework**, not your app target. Apple's reasoning: IB needs to dynamically load your code; load failures (crashes) shouldn't kill IB itself. The recommended pattern: app + UIKit/AppKit framework with your `@IBDesignable` views.

## Resizable iOS Simulator (sessions 216, 411)

- New simulator type: "Resizable iPad" / "Resizable iPhone". Drag the simulator window to any size; type custom dimensions; switch size class and idiom independently of the resolution. **Test your adaptive UI without dozens of device simulators** (216, 411).
- HIDDEN GEM: the resizable simulator can simulate iPhone size class on a virtual iPad-resolution canvas — exercise your "what if a third-party windowing scheme appeared" code paths (216).

## Asset Catalogs Get Size Classes, JPEGs, PDFs, Templates (sessions 411, 220)

- New per-image variants: **size class** (Compact/Regular Width × Compact/Regular Height). One image set, four optional variants. UIImageView automatically picks the right one for its trait collection (411).
- HIDDEN GEM: **JPEG and PDF images are now supported** in asset catalogs. Use JPEG for large photos that compress better than PNG; PDF for vector icons. PDFs are rasterized at the appropriate scales at build time on iOS, kept as vectors on OS X (411).
- HIDDEN GEM: **template images** can be marked in the asset catalog UI rather than relying on the `_Template` filename suffix. Cleaner than naming conventions (411).
- HIDDEN GEM: Asset catalogs support **alignment rect insets** — image padding for centering effects (glow halos, drop shadows) without the layout being thrown off (411).

## Localization in Xcode 6 (session 412)

- **XLIFF Export/Import** — export your project's localizable strings as standard XLIFF, hand to translators, import the result. No more manual `.strings` file management.
- **Pseudo-Languages** in IB Preview — preview your UI in **Double Length Pseudo-Language** without any actual translation. See whether your Auto Layout copes with German-length text. Also Right-to-Left pseudo-language for testing RTL layouts (411, 412).
- BEST PRACTICE: pseudo-languages catch broken layouts at design time. Run with them as a regular part of QA.
- **Storyboard localization** is now base-language + per-language string overrides — single source of truth for layout, separate translations.

## Embedded Frameworks on iOS (session 416)

- iOS 8 supports **dynamic frameworks** in the app bundle — finally. Previously only static libraries.
- Build target type: "Cocoa Touch Framework". Linked into your app, copied into the app bundle's `Frameworks/` directory at build time.
- HIDDEN GEM: Apple **encrypts embedded frameworks with the same FairPlay encryption** as the app binary. Same anti-piracy story (416).
- WARNING: embedded frameworks are NOT a code-sharing mechanism between apps. Each app bundles its own copy. They exist primarily to share code between an app and its extensions (416, 217).
- BEST PRACTICE: define a clean module-based public API in your framework. Hide implementation details. Treat your framework as you would a third-party library — strict access control (416).

## Modules System for Objective-C (sessions 416, 417)

- **`@import UIKit;`** instead of `#import <UIKit/UIKit.h>`. Faster builds (compiled module cache vs. textual `#include`), no preprocessor leakage between files.
- HIDDEN GEM: Xcode 6 turns on `Defines Module = YES` by default for new framework targets. Your framework is module-importable from Swift AND from `@import` in Obj-C (416).
- Required for Swift interop: Swift can ONLY import modules, never include headers (416).

## Testing — XCTest Performance Tests (session 414)

- New **`measure { }`** API on `XCTestCase`. Run a closure 10 times; capture stats; surface the **mean and stddev** in Xcode. Set baselines and regressions trigger test failures.
- **`measureMetrics(_:automaticallyStartMeasuring:for:)`** — measure user-defined metrics with explicit start/stop control.
- HIDDEN GEM: performance baselines are stored per machine. Different team members get different baselines automatically; CI can have its own baseline (414).
- **Asynchronous tests**: `XCTestExpectation` + `wait(for:timeout:)` — finally a clean way to test async code without spinning the run loop manually (414).

## Continuous Integration with Xcode Server (session 415)

- Xcode 6 + OS X Yosemite Server: hosted bots build/test/archive on every commit. Email notifications, integration history, downloadable artifacts.
- HIDDEN GEM: Xcode Server can deploy archives to TestFlight (Apple acquired TestFlight in early 2014; full integration in iOS 8 era) — automatic beta distribution from green builds (415).
- BEST PRACTICE: enable XCTest performance tests in the bot's test action — get email when somebody regresses launch time.

## Debugging in Xcode 6 (session 413)

- **View Debugging** in Xcode 6 — pause your app, see a 3D exploded view of the view hierarchy. Inspect any view's properties, constraints, frames. Replaces Reveal/Spark Inspector for many use cases.
- **Visual constraint debugging** — when an Auto Layout failure happens, Xcode shows the broken constraints visually with conflict markers.
- **Improved LLDB**: `e --object-description self` for full debug description; tab completion for property names; expression evaluation in Swift breakpoint condition fields.
- HIDDEN GEM: edit Auto Layout constants while paused at a breakpoint and see the result on the next layout pass. Iterating layout values without rebuild (413).

## LLVM 6 Improvements (session 417)

- **Swift integration**, obviously.
- **Compile-time speedups**: incremental indexing improvements, modules-by-default for new projects.
- **Better error messages** for templated/generic types.
- **Address Sanitizer (ASan)** ships in Xcode 6 — detect use-after-free, heap-buffer-overflow, stack-buffer-overflow at runtime in your tests. Slower than normal builds but catches bugs the static analyzer can't see (417).
- BEST PRACTICE: run your test suite under ASan in CI — catches a class of bugs that historically appeared as random crashes in production.

## Instruments — Redesigned UI + Swift Support (session 418)

- New unified UI matching Xcode 6's design language. Configurable inspector pane on the right.
- **Allocations and Leaks instruments understand Swift classes** — symbol mangling translates to your readable Swift class names (418).
- HIDDEN GEM: Instruments can profile **app extensions**. Choose your extension as the launch target; pick the host app from a dropdown. Time-profile a today widget while it's running inside Notification Center (418).
- HIDDEN GEM: **generational analysis** for memory leaks. Mark a baseline; perform an action; mark another baseline. Instruments shows what objects accumulated between marks. Drag marks around the timeline to redefine generations after the fact (418).
- **Time Profiler in iOS 8 supports waiting threads** — sample idle threads, useful for finding blocked main-thread waits (418).

## Modern Cocoa Apps (session 227)

- AppKit gets **`NSGestureRecognizer`** with five flavors: pan, click, rotate, magnification, press. Same API shape as UIKit gesture recognizers.
- **Storyboards on OS X** — designed alongside iOS storyboards.
- **`NSSplitViewController`** and **`NSTabViewController`** — first-class container view controllers (227).
- BEST PRACTICE: build new Mac apps with storyboards + view-controller-centric architecture. The XIB-per-window era is ending.

## Best Practices

- **Adopt embedded frameworks for code shared between an app and its extensions** — the alternative is duplicate compilation (416).
- **Add XCTest performance tests for critical paths** — app launch time, scrolling frame rate, table view cell loading. Catch regressions in CI (414).
- **Run tests under Address Sanitizer in CI** — catches a class of memory bugs you can't easily find any other way (417).
- **Use the resizable simulator** — way faster than booting multiple device simulators to test layouts (216, 411).
- **Use IB Live Rendering** for any custom drawing — saves the build-and-run iteration loop (411).
- **Use `@import` instead of `#import`** — Swift requires it; Obj-C builds faster with it (416).

## Hidden Gems

- HIDDEN GEM: Xcode 6 IB has **Find and Replace across storyboards AND code simultaneously**. Renaming a selector with `Cmd-Option-Shift-F` updates both the source file and the IB connection — preserving the wiring (411).
- HIDDEN GEM: **`viewForBaselineLayout`** on a custom view tells Auto Layout where the baseline of your view is. Other Auto Layout-positioned text aligns to that baseline correctly. Critical for custom-drawn text components (411).
- HIDDEN GEM: Asset Catalog "Universal" device class entries can have a "Width Compact" variant — different image for any device when shown in compact horizontal trait (411).
- HIDDEN GEM: Instruments' new track-view zoom uses click-and-drag to filter time, click-and-shift-drag to zoom — much more intuitive than the old `Cmd+`/`Cmd-` (418).

## Cross-references

- **Swift (402-407)** — Xcode 6 IS the Swift toolchain. The two ship together.
- **Embedded Frameworks (416)** + **App Extensions (217)** — extensions almost mandate frameworks for code sharing.
- **Adaptive UI (216)** + **Asset Catalogs (411)** — the per-size-class image variants are the asset-catalog side of the trait collection model.

## Migration Guidance

- **Existing projects upgrading to Xcode 6**: enable size classes in your storyboards (Xcode prompts). The upgrade is one-way; back up first if your team includes developers still on Xcode 5.
- **Add framework targets** to any project that has multiple shared files between an app and a future extension. Easier to factor out now than later.
- **Add XCTest performance baselines** for slow tests; CI catches regressions.
- **Adopt `@import`** for new code. The build-time win compounds.
