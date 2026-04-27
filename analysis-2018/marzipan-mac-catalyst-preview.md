# Marzipan / Mac Catalyst Sneak Peek — WWDC 2018 Analysis

**Sessions covered:** 102 (Platforms State of the Union §UIKit-on-Mac), 209 (What's New in Cocoa for macOS), 202 (What's New in Cocoa Touch), 235 (UIKit: Apps for Every Size and Shape), 803 (Designing Fluid Interfaces)

## Headline

Apple revealed they were running iOS apps on the Mac at WWDC 2018 — News, Stocks, Voice Memos, and Home all built from their iOS UIKit codebases. Public release was deferred to **2019** as Mac Catalyst. The 2018 announcement is a **sneak peek**: no public API, no developer beta. But the year's UIKit and AppKit changes (semantic materials, Swift type nesting, Codable on UIKit value types, NSGridView matching UIStackView, NSTextView factory methods aligned with UIKit conventions) are deliberately positioning both frameworks for the Catalyst bridge.

## What Apple Showed (102)

- News, Stocks, Voice Memos, Home — all genuine UIKit apps running natively on Mojave.
- The apps share native macOS conveniences:
  - Mouse events mapped to UI events (taps + clicks unified).
  - Two-finger scroll mapped to scroll-view interactions.
  - Window resize, full-screen, native menu bar, native toolbar with red/yellow/green window controls.
  - Drag-and-drop into other apps (drag selected text from Stocks → drop into Notes).
  - Window-level "share" affordance in toolbar.
- These four apps are built from the same source as the iPad versions. Apple's stated approach: "this is a new way to deliver Mac apps for iOS developers who don't have a native AppKit experience to ship."

## The Stack Change (102, 209)

- AppKit and UIKit historically each had their own substrate. Apple realized that "in some cases [it has] drifted apart over time" and is _rationalizing_ both onto a common foundation.
- This means: even if you never adopt Catalyst, your AppKit-vs-UIKit code becomes more portable in 2018 — same Codable types, similar API patterns, same nested constants.
- Examples already shipping in 2018:
  - Both frameworks have `automatic` constraint adjustment behavior.
  - Both frameworks expose `NSColor` / `UIColor` semantic accessors with the same naming convention (`labelColor`, `controlAccentColor`, `systemRed`, etc.).
  - Both frameworks now have `NSGridView` and the existing `UIStackView` filling a similar role; APIs are converging.
  - `NSImage.Name` / `UIImage` use bridged typedef patterns that simplify Swift call sites identically (see 209).

## What's NOT Available in 2018

- **No public Catalyst SDK**. Apple's own apps used a private framework.
- **No developer beta**. Mojave seeds did not include Marzipan tooling.
- **No App Store distribution path** for "iPad app on Mac" yet.

Wait for 2019 (session 205 — "Introducing iPad Apps for Mac" — for the public reveal of Catalyst).

## How to Prepare in 2018

1. **Adopt Safe Area properly**. Catalyst windows have variable size and the iPhone X-style safe-area mental model carries over. (See 235.)
2. **Use Auto Layout** thoroughly. Frame-based layouts won't reflow on window resize.
3. **Use system colors and dynamic colors**. Hardcoded colors will look wrong in Mojave's Dark Mode. (See 210.)
4. **Use `UIScrollView.contentInsetAdjustmentBehavior`** and propagate safe-area insets correctly. (See 235.)
5. **Sandbox properly**. Mac sandbox is stricter than iOS in some areas. Apps that bake in network endpoints or file paths assuming "always-on, no permissions" will break.
6. **Audit your file I/O**. Many UIKit data-protection APIs (`.completeFileProtection`) silently no-op on macOS. The bridging story Apple ships in 2019 makes this explicit, but your design should not depend on file-level encryption for security on Mac.

## Historical Context

- 2017's "Marzipan" rumors became confirmed at WWDC 2018 in this session.
- 2018: four Apple apps as proof of concept, public sneak peek.
- 2019: Mac Catalyst SDK ships with Xcode 11 + macOS Catalina. Existing iPad apps gain a "Mac" checkbox in target settings.
- 2020: Big Sur brings full design parity (toolbar, sidebar, controls), Catalyst more polished.
- 2021–2022: SwiftUI gradually overtakes Catalyst as the multi-platform story.

## Cross-references

- AppKit changes that anticipate Catalyst convergence: 209.
- UIKit changes that anticipate Catalyst convergence: 202, 235.
- Dark mode (must work for Catalyst apps on Mojave): 210, 218.
- Design considerations for Mac vs. iPad: largely deferred to 2019's session 205.
