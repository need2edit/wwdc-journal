# Accessibility — WWDC 2018 Analysis

**Sessions covered:** 226 (VoiceOver: App Testing Beyond The Visuals), 230 (Deliver an Exceptional Accessibility Experience), 241 (Accessible Drag and Drop), 803 (§ Accessibility in Fluid Interfaces), 603 (§ AR Quick Look + VoiceOver)

## Headline

WWDC 2018 doesn't introduce a new headline accessibility framework, but it makes important usability commitments: AR Quick Look ships with full VoiceOver and Switch Control support out of the box, drag-and-drop on iOS got accessibility hooks for VoiceOver users, and Apple gave a long, methodology-focused VoiceOver session walking through "test beyond the visuals" — auditing apps with the screen off.

## Test With the Screen Off (226)

The single most actionable best practice from session 226:
- Run your app with VoiceOver on _and_ the screen turned off (Triple-click → "Screen Curtain"). If you can't navigate, neither can a blind user.
- Listen for the order of focus traversal: does it match the visual reading order? Does it skip decorative elements?
- Listen for hints: are interactive elements clearly described? "Button" alone is meaningless; "Send Message Button" is useful.

## Accessibility Inspector Workflow (230)

- Run the Accessibility Inspector (Xcode → Open Developer Tool → Accessibility Inspector) connected to your app on simulator or device.
- Audit pane: highlights elements with missing labels, contrast issues, dynamic type compliance, and tap-target size violations.
- Audit catches issues that VoiceOver alone won't surface — like a button with sufficient label but tap target only 24×24.

## VoiceOver Custom Actions (230)

- `accessibilityCustomActions` on any UIView lets you provide actions triggered by VoiceOver's rotor without the user navigating to discrete buttons.
- Powerful for compound cells: a list cell with "Reply", "Like", "Delete" as custom actions reads as one element ("Message from Alice, 3 unread, double-tap to read") and exposes those actions via the rotor.
- Reduces traversal friction for blind users.

## Accessible Drag and Drop (241)

- Drag-and-drop on iPad introduced in iOS 11 was visually-driven and inaccessible without sight.
- iOS 12 adds a parallel VoiceOver flow: long-press initiates a drop-mode where the user navigates to a drop target and double-taps to drop.
- Implement `accessibilityDragSourceDescriptors` on your drag sources and `accessibilityDropPointDescriptors` on your drop targets — VoiceOver reads these as it traverses.
- **HIDDEN GEM**: this isn't optional. App Review can reject apps that ship drag/drop without VoiceOver support.

## AR Quick Look + VoiceOver (603)

- AR Quick Look reads model name and description; announces "object now placed in world," "object now off-screen," "object now on-screen" via positional audio.
- Switch Control: tap targets adjusted so single-switch users can navigate the AR scene.
- Sets a precedent: AR experiences are not exempt from accessibility.

## Sub-Topic: Dynamic Type and Reading (230)

- Dynamic type sizes go up to AX5 (huge) and down to xSmall. Always test with both extremes.
- The new readable-content guide (introduced 2017, now widely adopted by table views) keeps line lengths comfortable at any text size.
- Use `UIFontMetrics.scaledFont(for:)` to scale custom-named fonts (e.g., "Helvetica-Bold") with dynamic type. Without this, custom fonts stay one size while system fonts grow.

## Increased Contrast / Reduced Transparency (210, 218)

- macOS Mojave's high-contrast appearances are first-class members of NSAppearance. Define asset catalog variants for high-contrast light + high-contrast dark.
- Reduce Transparency removes vibrancy materials (background becomes opaque). Test that your text remains legible.

## Accessibility-Driven Design (230, 802)

- Apple's framing: "accessibility is a feature, not a checklist."
- Voice Control, Switch Control, AssistiveTouch — design custom controls so they work with these alternative input methods.
- Custom controls should be subclasses of `UIControl` (not raw `UIView` with gesture recognizers), so default accessibility plumbing works.

## Cross-references

- AR Quick Look accessibility: 603.
- iOS dark mode + accessibility (high contrast) is one year out (2019).
- VoiceOver gestures for navigating documents and tables: 226 (full demonstration).
