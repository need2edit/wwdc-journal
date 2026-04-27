# Web, Safari & Modern WebKit — WWDC 2014 Analysis

**Sessions covered:** 206 (Introducing the Modern WebKit API), 504 (Advanced Media for the Web), 506 (Ensuring Continuity Between Your App, Your Website, and Safari), 509 (Creating 3D Interactive Content with WebGL), 512 (Web Inspector and Modern JavaScript), 516 (Improving the Accessibility and Usability of Complex Web Applications), 517 (Designing Responsive Web Experiences)

## Headline

iOS 8 ships **`WKWebView`** — the modern, high-performance WebKit replacement for `UIWebView`. Same API on iOS and OS X. Out-of-process content rendering, full Nitro JavaScript JIT, native scroll/zoom gestures, and a powerful `WKUserScript` + script messages bridge for app↔web communication. The 6-year `UIWebView` era ends.

## The Mental Model — WKWebView (session 206)

- **Multi-process architecture**: each `WKWebView` runs its content in a separate "Web Content" process. Crashes in JS or rendering don't kill your app. Memory pressure manages cleanly (206).
- **Full JavaScript Nitro JIT on iOS** — `UIWebView` had only the slow interpreter for security reasons. `WKWebView` ships with **the fourth-tier compiler** (LLVM-based), making JS-heavy web apps comparable to Safari's own performance (206).
- **Native scroll/zoom gestures** — pinch-to-zoom, double-tap-to-zoom, swipe-back/forward — all match Safari's built-in behavior (206).
- HIDDEN GEM: **on iOS, the swipe-back/forward navigation gesture isn't on by default** — set `WKWebView.allowsBackForwardNavigationGestures = true`. Free Safari-style nav (206).
- HIDDEN GEM: on macOS, `WKWebView.allowsMagnification = true` enables double-tap-to-zoom and pinch-to-zoom (206).

## Sharing Configuration Across Web Views (session 206)

- **`WKWebViewConfiguration`** holds shared state: process pool, preferences, user content controller (user scripts + script message handlers), website data store.
- Multiple `WKWebView`s sharing the same configuration share processes (up to a system-imposed limit) and shared preferences (206).
- Each `WKWebView` instance gets its own delegate; observe properties like `title`, `loading`, `canGoBack`, `canGoForward` via KVO or Cocoa Bindings (206).

## Navigation Delegation (session 206)

- **`WKNavigationDelegate`** intercepts page loads. Two key callbacks:
  - **`webView(_:decidePolicyFor:decisionHandler:)` for navigation actions** — link clicks, history nav, JS navigation. Inspect `WKNavigationAction.navigationType`, `request`, `targetFrame`, even `modifierFlags` (cmd-click). Return `.allow` or `.cancel`.
  - **`webView(_:decidePolicyFor:decisionHandler:)` for navigation responses** — server responses. Inspect `WKNavigationResponse.response` (HTTP status, MIME type, etc.) before allowing the load.
- HIDDEN GEM: the WKPedia demo from session 206 routes external (non-Wikipedia) links to Safari and intercepts cmd-clicks to open new windows in the same Wikipedia browser app. Both behaviors implemented in 5 lines via the navigation delegate (206).

## User Scripts (session 206)

- **`WKUserScript`** = a JavaScript blob injected into every page load (or every frame).
- Configurable: **inject at document start** (before any page JS runs) or **document end** (after DOM parsed but before subresources finish).
- Injected scope: main frame only or all frames.
- HIDDEN GEM: combine `documentStart` + a `<style>` injection to **hide elements before the user sees them**. The WKPedia iPad demo hides Wikipedia's table of contents and sidebar this way, replacing them with a native UI (206).

## Script Messages (session 206)

- **`WKScriptMessageHandler`**: register a name; a JS global `window.webkit.messageHandlers.<name>.postMessage(...)` calls back into your app.
- Auto-converts JS data to native: JS objects → `NSDictionary`, arrays → `NSArray`, numbers → `NSNumber`, strings → `NSString`.
- HIDDEN GEM: this is the **bidirectional bridge** — your user script reads the DOM and posts data; your native code receives it (e.g., Wikipedia's table of contents extracted to a UITableView). Native code can push data back via `webView.evaluateJavaScript(...)` (206).
- WARNING: **don't blindly trust messages from arbitrary web pages**. Any site can post messages. Validate types and contents on the native side (206).

## App + Website Continuity (session 506)

- **Shared web credentials** (covered in Continuity analysis) — your app reads passwords Safari saved.
- **`autocomplete` attribute values**: `username`, `current-password`, `new-password` — help Safari understand your forms. Without these, AutoFill uses heuristics that can fail on dynamic sites (506).
- HIDDEN GEM: for AJAX-driven sites that don't full-page-reload after login or password change, call **`history.pushState(...)`** to signal the state change to Safari. Safari listens for `pushState` to know when to prompt about saving an updated password (506).

## Apple-Touch-Icon for Start Page (session 506)

- Safari 8 on Yosemite + iOS 8 use `apple-touch-icon` link for the Favorites and Frequently Visited start page tiles.
- BEST PRACTICE: serve the touch icon on EVERY page (not just mobile-targeted), at 180×180 minimum. Use the full square — Safari rounds the corners automatically (506).

## Reading List + Shared Links (session 506)

- Apps can add to the user's Reading List via `SSReadingList.default()?.addReadingListItem(with:title:previewText:)`. Lightweight, no permission prompts.
- Use **OpenGraph metadata** (`<meta property="og:title">`, `<meta property="og:description">`) so Safari extracts good titles/descriptions when the user adds your page to Reading List (506).
- **Shared Links** in Safari (sidebar showing tweets and follows) supports any RSS feed. Serve a feed; users opt in via "Subscribe in Shared Links" (506).

## Responsive Web Design (session 517)

- **The mobile-website era is over** — one responsive site beats `m.example.com` redirect chains. Apple explicitly says so in 517.
- Use CSS media queries, viewport meta tag, fluid grids, scalable images. Test on real devices.
- HIDDEN GEM: Handoff in iOS 8 means a user can open a link sent from someone's iPhone on their Mac. **A mobile site that doesn't redirect back to a desktop layout looks broken on a 27" iMac**. Make sure your `m.example.com` redirects users on desktop user agents to the desktop site — or eliminate the split entirely (506, 517).

## Standards-Based Video (session 504)

- HTML5 `<video>` plays everywhere on Apple platforms — no plugins, on iOS or Mac.
- BEST PRACTICE: **use `<video>` on Mac too** — same video everywhere, better battery, smoother playback than Flash plugins (504, 506).
- Pre-roll ads via JS instead of plugin solutions — DOM-aware, native performance.

## Web Inspector + JavaScriptCore (session 512)

- Safari Web Inspector now profiles **CPU usage** with a flame chart for JS, layout, paint, compositing.
- HIDDEN GEM: you can attach Safari Web Inspector to your app's `WKWebView` content for full inspection — including your injected user scripts. Only works on dev builds; production users can't be inspected (206).
- **JavaScriptCore framework** on iOS lets you embed JS in native apps without WebView. `JSContext`, `JSValue`, callable from Swift/Obj-C.

## WebGL on iOS (session 509)

- WebGL fully supported in `WKWebView` on iOS 8+. Same standard API as desktop browsers.
- Hardware-accelerated 3D in your web pages.

## Best Practices

- **New apps: use `WKWebView`. Existing apps: migrate from `UIWebView`** when iOS 8+ minimum-deployment is acceptable. Performance and stability gains are dramatic (206).
- **Use the navigation delegate** to control which links go where (your app, Safari, a popover) (206).
- **Use user scripts + script messages** for app↔web bridge instead of brittle JS-from-Obj-C eval chains (206).
- **Use `autocomplete` attribute values** on your forms so Safari understands them (506).
- **Use OpenGraph metadata** so Reading List entries look right (506).
- **Serve apple-touch-icon on every page** at 180×180+ (506).
- **Use HTML5 video, not Flash** — better everything (504).
- **Adopt responsive design** if you have a separate mobile site — better long-term (517).

## Hidden Gems

- HIDDEN GEM: `WKWebView` is **API-incompatible with `UIWebView`** — no drop-in replacement. Migrating apps with deep `UIWebView` integration takes work. Allow time (206).
- HIDDEN GEM: `WKWebView`'s out-of-process content means **memory leaks in JS don't leak your app** — the web content process is killed and recreated cleanly under memory pressure (206).
- HIDDEN GEM: `WKUserScript` can pre-emptively rewrite the page DOM (`documentStart`) to remove ads, restyle, add affordances. Powerful for purpose-built browser apps (206).
- HIDDEN GEM: shared web credentials' `SecAddSharedWebCredential` syncs passwords to all the user's Safari instances on all devices via iCloud Keychain — your app effectively bootstraps the user's cross-device password (506).
- WARNING: WKWebView on iOS 8.0 (the seed shown at WWDC) had cookie sharing issues with native NSURLSession — fixed in later 8.x. Test cookie-shared flows carefully on the GM (206).

## Cross-references

- **Continuity (219, 506)** — Handoff URLs, shared web credentials.
- **Touch ID (711)** — gates the credential picker for shared web credentials.
- **App Extensions (217)** — Safari custom action extensions can run JavaScript inside Safari pages and bridge to your native extension.
- **Networking (707)** — `WKWebView` uses the same `NSURLSession` machinery as your native code, including SPDY support.

## Migration Guidance

- **From `UIWebView`**: API surface is different. Plan migration carefully:
  1. `UIWebViewDelegate` → `WKNavigationDelegate` + `WKUIDelegate`.
  2. `stringByEvaluatingJavaScriptFromString:` → `evaluateJavaScript:completionHandler:` (now async).
  3. JS-to-native callbacks via window.location URL hacks → **WKScriptMessageHandler** (vastly cleaner).
  4. CSS injection via JS string → **WKUserScript at documentStart**.
- **From mobile websites**: invest in responsive design. The 2-3 week effort pays back forever in maintenance simplicity and Handoff compatibility.
- **From plugin-based video**: use HTML5 video. Done in a day usually.
