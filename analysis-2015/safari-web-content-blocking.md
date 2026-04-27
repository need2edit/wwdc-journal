# Safari, WebKit & Content Blocking — WWDC 2015 Analysis

**Sessions covered:** 501 (What's New in Web Development in WebKit and Safari), 504 (Introducing Safari View Controller), 505 (Using Safari to Deliver and Debug a Responsive Web Design), 511 (Safari Extensibility: Content Blocking and Shared Links)

## Headline

Safari View Controller replaces in-app web views with a Safari-quality experience that runs out-of-process for security AND inherits the user's Safari cookies, passwords, and content blockers. Content Blocking is introduced as a privacy-respecting JSON-rule extension that compiles to bytecode. WebKit gains backdrop filters, scroll snap points, JavaScript ES6 (classes, template literals, default parameters), CSS @supports, Force Touch events.

## Safari View Controller (504)

See `search-and-deep-linking.md` for the full coverage. The TLDR:

- `SFSafariViewController(url:)` replaces in-app `UIWebView`/`WKWebView` for general browsing.
- Out-of-process; your app cannot see the user's typing or stored credentials.
- Inherits Safari's cookies, iCloud Keychain passwords, content blockers, AutoFill.
- Customize tint color to feel like part of YOUR app.
- For OAuth: present, let the redirect URL hit your app via Universal Links, dismiss. Replaces web view login flows entirely.

**BEST PRACTICE**: Stop building in-app browsers.

## WKWebView Improvements (501, 504)

When you DO need a web view (custom UI, non-browser usage):

- **`loadFileURL(_:allowingReadAccessTo:)`** — securely load local files. **HIDDEN GEM**: this was missing in iOS 8 and is the most-requested addition.
- **`loadHTMLString(_:baseURL:)` and `load(_:)` with literal data** — no spin-up server needed.
- **`customUserAgent`** — set arbitrary UA string.
- **`WKWebsiteDataStore`** — manage cookies and caches as a property of the configuration. Read/write so you can swap a non-persistent store for private browsing.
- `WKWebsiteDataStore.removeData(ofTypes:modifiedSince:completionHandler:)` — clear data by type and recency.

## Content Blockers (511, 504, 107)

iOS gets ad/content blocking — privacy-by-design.

- New extension type: **Content Blocker Extension**. Returns a JSON list of rules ONCE; Safari compiles to bytecode for fast evaluation.
- Extension never sees what URL the user visits. Safari evaluates locally.
- Same JSON works in iOS Safari, macOS Safari (replacing the deprecated `canLoad` callback model), AND every app using `SFSafariViewController`.

### Rule format
```json
{
  "trigger": {
    "url-filter": "tracking_script\\.js",
    "load-type": ["third-party"],
    "resource-type": ["script"],
    "if-domain": ["bigbearsgolfblog.com"]
  },
  "action": {
    "type": "block"
  }
}
```

Action types:
- `block` — don't load
- `block-cookies` — strip cookies
- `css-display-none` — hide via CSS selector
- `make-https` — upgrade
- `ignore-previous-rules` — exception (let earlier-blocked content through)

Trigger filters:
- `url-filter` (regex) — required
- `resource-type` — script, image, style-sheet, raw, svg-document, media, popup, font
- `load-type` — first-party, third-party
- `if-domain` / `unless-domain` — scope to specific sites

### Activation
- `SFContentBlockerManager.reloadContentBlocker(withIdentifier:)` — recompile after your app updates the rule set (e.g., user changed settings in your app).

**HIDDEN GEM**: Combine with cosmetic CSS rules to clean up sites without blocking their loads — preserves analytics if you want to be polite to publishers while removing visual clutter.

## Shared Links Extension (511)

Inject content into Safari's Shared Links sidebar (next to bookmarks/reading list).

- Implement `NSExtensionRequestHandling`. Return an array of `NSExtensionItem` objects.
- Each item: stable unique identifier (don't re-randomize), URL, attributed title, attributed content text, attached image.
- **HIDDEN GEM**: extensions are sandboxed by default — you must check **Outgoing Network Connections** in capabilities to fetch from the web.

## WebKit Layout: Backdrop Filters (501)

CSS `backdrop-filter` proposed standard. Apply CSS filters (blur, saturate, grayscale, invert) to the content BEHIND an element.

```css
nav.fixed-header {
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(10px);
}
```

- Hardware-accelerated.
- Composes with any CSS filter.
- **PERFORMANCE**: each backdrop-filter element triggers an off-screen rendering pass. Profile if used heavily.
- **HIDDEN GEM**: works on top of dynamic content (videos). Live blur over a playing video — formerly required hand-rolled GPU shaders.

## WebKit Layout: Scroll Snap (501)

CSS scroll-snap proposed standard. Native browser-driven snapping for tile-based content.

```css
.gallery {
  scroll-snap-type: mandatory;
  scroll-snap-points-x: repeat(100vw);
}
```

For non-uniform content, use scroll-snap-destination + scroll-snap-coordinate to align arbitrary points on items to arbitrary points in the container.

**Replaces** complex JavaScript scroll handlers that throw away the browser's smooth scrolling — a major performance win.

**WARNING**: don't combine with programmatic JavaScript scrolling — they'll fight.

## JavaScript ES6 (501)

Major additions in WebKit:

- **Classes**: `class Polygon { constructor(...) {} method() {} }` plus `extends`, `super`, static methods. Compatible with existing prototype-based code.
- **Template literals**: `` `Hello, ${name}` `` — backtick strings with `${...}` interpolation.
- **Object literal shorthand**: `{name, category}` instead of `{name: name, category: category}`.
- **Symbol objects, weak sets, weak maps, Object.assign, Map, Set, Proxy, generators**, and more.

## CSS Improvements (501)

- **`@supports(prop: value)`** — feature detection in CSS. Apply styles only when a property is supported.
- **`:matches()` pseudo-class** — collapse repeated selectors into a single rule. Massive code-savings in component libraries.
- **`:any-link`**, **`:placeholder-shown`**, **`:lang()`** — additional state pseudo-classes.
- Many vendor-prefixed properties unprefixed (transitions, animations, transforms, etc.). The prefixed versions still work.
- `-webkit-initial-letter` — drop-cap typography.

## Force Touch Events on Web (501)

Mac trackpad force events:

- New events: `webkitmouseforcewillbegin`, `webkitmouseforcedown` (force-click crossing), `webkitmouseforceup`, `webkitmouseforcechanged`.
- All mouse events have `webkitForce` property (current pressure 0–3).
- Constants: `MouseEvent.WEBKIT_FORCE_AT_MOUSE_DOWN`, `MouseEvent.WEBKIT_FORCE_AT_FORCE_MOUSE_DOWN` — use these, not numeric values.
- `webkitmouseforcewillbegin` is your chance to call `preventDefault()` to suppress the default OS Look Up / preview behavior.

**BEST PRACTICE**: Force Touch is a flourish. Always provide a fallback for users without the hardware.

## AirPlay on macOS Safari (501)

- Safari can AirPlay video to Apple TV from macOS. Same API as iOS — if you adopted in 2013, you're done.

## Picture in Picture for Web Video (501)

- WebKit defines `presentationMode` on video: `inline`, `fullscreen`, `picture-in-picture`.
- Default media controls support PiP automatically. Custom controls need to call the API.
- **HIDDEN GEM**: HLS strongly recommended for PiP — the video may render at 200x200 in the corner, and the system can pick the appropriate bitrate dynamically.

## Responsive Design Tools (505)

- Safari's Web Inspector (now in iOS Safari too via remote inspection) gets a Responsive Design Mode.
- Live preview of multiple viewport sizes simultaneously.
- iPad multitasking widths preset (1/3, 1/2, 2/3, full).
- CPU usage profiling for web content.
- Auditing for DOM accessibility and resource issues.

## Cross-references

- Safari View Controller (504) is the right answer for OAuth flows — works with shared web credentials (509).
- Content blockers (511) cascade automatically into apps using SFSafariViewController.
- WKWebView improvements (501) plus App Transport Security (711) require HTTPS for in-app content.
