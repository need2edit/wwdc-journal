# Design, Accessibility & Typography — WWDC 2015 Analysis

**Sessions covered:** 802 (Designing for Apple Watch), 805 (Apple Watch Design Tips and Tricks), 803 (Designing with Animation), 801 (Designing for Future Hardware), 804 (Introducing the New System Fonts), 201 (iOS Accessibility), 204 (Apple Watch Accessibility)

## Headline

WWDC 2015 sets the bar for designing tiny experiences. Apple Watch design is a discipline of subtraction — Mike Stern's three themes (Personal Communication, Holistic Design, Lightweight Interaction) become the canonical design language for the wrist. **San Francisco** debuts as the new system font for ALL platforms, replacing Helvetica Neue. iOS Accessibility introduces Touch Accommodations, magic taps, and accessibility focus tracking.

## Apple Watch Design (802, 805)

### Three foundational themes

**1. Personal Communication** — design as if you're talking to a friend.
- Be considerate of time and attention. Notifications buzz the wrist; over-notifying gets your app's notifications switched off (and possibly the iPhone's too — the user has only ONE switch for "notifications from this app on watch").
- Be relevant. Use location and time as contextual filters (Invoice2Go reminds to clock in when arriving on-site; American Airlines reminds to leave for the airport).
- Pay attention to user preferences — both **explicit** (settings) and **implicit** (Fitness app reorders workout types by frequency, defaults to last-chosen goal).

**2. Holistic Design** — blur the line between hardware and software.
- Black backgrounds match the bezel: your UI extends visually edge-to-edge.
- **Force Touch menus**: contextual actions, not critical-path actions. Frees the main UI for content. Use for "view mode preferences" (stopwatch face style, calendar list/time view).
- Don't put critical-path actions in menus — keep them inline. (Save/Discard at workout end MUST be visible, not hidden behind Force Touch.)
- **Digital Crown**: never cram everything on screen at once. The Stocks detail screen lets the current value breathe at the top; older history scrolls below.
- **Pickers** with three styles (list, stack, image-sequence) and optional outline/caption/scroll-indicator — see watchos-2-native.md.
- **Taptic Engine + audio**: 9 named haptic patterns (notification, directionUp, directionDown, success, failure, retry, start, stop, click). Each has a designed audio tone. Use them consistently across apps so users learn meaning.
- **HIDDEN GEM**: haptics CANNOT overlap. Fast crank of a digital crown with click haptics on every minor tick will swallow most clicks. Use click only on major ticks.

**3. Lightweight Interaction** — five seconds or less per interaction.
- **Glances**: scannable summary, not a mini-app. Built from one upper template + one lower template (12 + 24 combinations = 288 layouts). Left-aligned text reads better at speed.
- **Notifications**: as few words as possible. Use graphics where possible. One action only when there's an obvious dominant choice (Reply on a new message); offer alternatives sparingly.
- **App design**: NOT a miniature iPhone app. The New York Times watch app shows 5 curated top stories, not browsable sections. Green Kitchen shows ONLY recipe-step timers — not the full recipe.
- Use **Handoff** so reading a synopsis on the watch can be continued on the iPhone. Some apps onboard this once; others let it self-discover.

### Best practices

- Always include a "primary" haptic for the actual significant event; reserve clicks for incremental adjustments.
- Avoid spinners that span the whole 5-second budget. Show data immediately, even if stale, then refresh.
- Animate to communicate (Resound's hearing-aid setting visualization), to delight (Toby walking off the watch edge), to provide feedback (PaceMaker's pulsing effect buttons synced to the music).

## Designing for Future Hardware (801)

The iPad Pro and Pencil were imminent (and 3D Touch on iPhone 6s). Design philosophy talk on principles that endure across hardware generations.

- Design at the level of the gesture, not the device.
- Design intent is more durable than design specifics. The intent of a swipe-to-dismiss gesture survives keyboards, joysticks, and stylus inputs.

## Designing with Animation (803)

- Animations carry meaning: feedback, focus, hierarchy, continuity.
- **PERFORMANCE/DESIGN**: animations on a watch should be quick (<1s typically). They should feel like punctuation, not exposition.
- watchOS 2's `animate(withDuration:animations:)` makes UIKit-style animation possible: alpha, height, width, color, opacity, group offset all animatable.
- Animate values along the same dimension as the user gesture (digital crown rotates → values change in lockstep via coordinated images).

## San Francisco Font (804)

The new system typeface for iOS, watchOS, OS X, and tvOS. Replaces Helvetica Neue.

- **Two designs**: SF (for larger sizes; iOS, OS X) and SF Compact (narrower forms for watch where line length is precious).
- **Two weights ranges**: Display weights (for sizes >= 20pt) and Text weights (smaller sizes have higher x-height, looser tracking, slightly different shapes).
- **Dynamic type system optical sizes**: the system substitutes an appropriately optimized variant per text size; you specify weight and let iOS choose Display vs Text.
- **Punctuation features**: monospaced figures available as a feature flag — critical for tabular data (clocks, statistics).
- **Track adjustments per size**: smaller sizes get slightly looser tracking automatically. Don't override unless you have a strong reason.

**HIDDEN GEM**: SF Mono ships with Xcode (later, public). Apple's first publicly available monospace font.

## iOS Accessibility (201)

The fundamentals never change but iOS 9 adds important features.

### The six questions every accessible element answers

1. `isAccessibilityElement` — am I worth interacting with?
2. `accessibilityLabel` — what's my name? (terse: "Add", not "Button To Add A Clock")
3. `accessibilityTraits` — what kind of element am I? (button, header, selected, image, link, etc.)
4. `accessibilityValue` — what's my state right now? (changes with state)
5. `accessibilityHint` — how do I interact? (e.g., "Drag up or down to change order"; localize this!)
6. `accessibilityFrame` — where am I on screen? (in screen coordinates; convert with `convert(_:to:)`)

### NEW in iOS 9

- **Touch Accommodations**: hold duration (ignore quick brushes), swipe gestures (ignore unintended motions), tap assistance (use the final tap location, the initial tap location, or whichever is closest to the target).
- **Accessibility Custom Actions**: `UIAccessibilityCustomAction` lets a single element expose multiple verbs to assistive technology (e.g., a chess piece exposing "move" and "trade").
- **Magic Tap**: `accessibilityPerformMagicTap()` returning `true` lets you handle the two-finger double-tap gesture contextually (answer call, toggle play, add to favorites). VoiceOver users learn one gesture, every app does the right thing.
- **Accessibility Focus tracking**: `UIAccessibility.focusedElement(using: .voiceOver)` to query the currently focused element. Notification when focus moves: `accessibilityElementDidBecomeFocusedNotification`.
- **HIDDEN GEM**: combine Magic Tap + Focus Tracking to add the focused item to a list with one gesture, no UI required.

### Accessibility for custom-drawn views (201)

If a view does its own `draw(_:)` (e.g., an SVG canvas, a graph), iOS can't infer the structure. Subdivide:

- Use `UIAccessibilityElement` (subclass) instances per logical sub-region, parented to the containing view.
- Set `accessibilityElements` array on the parent view.
- Frame each sub-element so VoiceOver gestures hit them in a predictable order. **HIDDEN GEM**: use the FULL HEIGHT of the chart for each data-point's frame, narrow horizontally — VoiceOver swipe-rotor lands on each point as the user moves left/right.

## Apple Watch Accessibility (204)

- Same accessibility properties carry to `WKInterface` elements. Set in IB or programmatically.
- VoiceOver on watch reads from text properties, image accessibility labels, and traits.
- Authorization (location, contacts, etc.) is shared between iPhone and watch — see `data-cloudkit-storage.md` and `watchos-2-native.md`.

## MapKit for Design and Discovery (206)

Tangentially relevant — design improvements:

- Pin colors customizable beyond red/green/purple via `pinTintColor` (deprecates old `pinColor`).
- **`detailCalloutAccessoryView`** lets you put any UIView in the callout (image, multi-line text, custom UI). Replaces emoji-in-subtitle hacks.
- `showsTraffic`, `showsCompass`, `showsScale` toggles.
- Transit ETA via `MKDirectionsTransportType.transit`, plus launch into Maps in transit mode.
- **Flyover** map type: photo-realistic 3D city models. New `MKMapCamera(lookingAtCenter:fromDistance:pitch:heading:)` because traditional altitude doesn't work over varied terrain. Annotations sit on top of buildings; overlays are occluded by buildings but follow terrain.

## Cross-references

- Apple Watch design (802) plus Watch Connectivity (713) plus ClockKit (209) is the holistic story for non-trivial watch apps.
- Accessibility (201) intersects with the entire system; if your app is hard for VoiceOver to explore, your VoiceOver users will reject it.
- San Francisco font (804) plus Dynamic Type plus accessible labels (201) — design-time planning saves user-time pain.
