# Designing Fluid Interfaces — WWDC 2018 Analysis

**Sessions covered:** 803 (Designing Fluid Interfaces), 802 (Intentional Design), 801 (The Qualities of Great Design), 804 (The Life of a Button), 805 (Creating Great AR Experiences), 808 (Prototyping for AR), 809 (Apple Pencil Design Essentials), 810 (Tips for Great Maps), 811 (Presenting Design Work), 233 (Adding Delight to your iOS App)

## Headline

This may be the design talk most-cited by designers across the apple-platforms ecosystem for the rest of the decade. Apple's HI team distills the iPhone X's home-indicator gestural language into eight design principles — response, redirection, spatial consistency, hinting, lightweight interactions with amplification, soft boundaries, smooth frames, dynamic behavior — and demonstrates them with the iPhone X interface itself. Plus a 35-minute deep dive on "the life of a button" demonstrating how much consideration goes into something everyone takes for granted.

## The Eight Principles (803)

### 1. Response

- Latency kills the feeling of direct manipulation. Users sense even tens of milliseconds.
- The iPhone X hardware was tuned to detect touches faster, so the entire interface gets that benefit.
- **BEST PRACTICE**: kill timers and delays everywhere. Even the smallest response delay during an animation makes it feel disconnected from you.

### 2. Allow Redirection and Interruption

- Our minds change direction constantly; interfaces must reflect that.
- iPhone X's gestural model is _fully redirectable_: swipe up to go home, then peek over to multitasking partway through, then continue home — all one continuous gesture.
- This is more than UX polish — it's _faster_ than the linear "decide → act → release" pattern. Thought and gesture proceed in parallel.
- Multi-axis gestural spaces let users discover new gestures along the path of an existing one.
- **HIDDEN GEM**: detect changes in motion via finger _acceleration_, not timers. iPhone X's pause-for-multitasking gesture works because pausing produces a huge acceleration spike. Detection is instant rather than waiting for a fixed time of low velocity.

### 3. Maintain Spatial Consistency

- Things smoothly leave and enter the same way. UIKit navigation: details push from the right, return to the right.
- A back gesture works because the user knows where the previous screen "lives."
- **GOTCHA**: an unmotivated transition direction (up vs. left) implies "send to elsewhere." Use only when you mean it.

### 4. Hint in the Direction of the Gesture

- Press a Control Center module: it grows up and out toward your finger as it transitions to the expanded state.
- Tells the user what's coming next; reduces surprise; aligns the upcoming animation with the muscle memory of the gesture.

### 5. Lightweight Interactions, Amplified Output

- Touch is light. Scrolling is a quick flick that translates into a long animated coast.
- The system preserves all the energy and momentum from the brief gesture and gracefully transfers it.
- Scrolling is the most familiar example. The iPhone X home gesture is another: a short swipe maps to a much larger animated transition.

### 6. Rubberband / Soft Boundaries

- When you scroll past the top of a list, the content stretches and snaps back. This tells you (a) the system is alive, (b) you've hit an edge.
- **HIDDEN GEM**: hard boundaries (no rubberband) feel indistinguishable from a frozen interface. Always provide soft boundary feedback.
- This applies to gesture _hand-offs_ too. When your finger slides up the dock to lift the app, both objects should track in smooth curves rather than one suddenly stopping and another suddenly starting.

### 7. Design Smooth Frames of Motion

- Frame rate matters less than the visual delta between consecutive frames. Fast motion at 30 fps strobes; slow motion at 30 fps looks smooth.
- Tools to overcome this: motion blur (encode movement information per frame), motion stretching (visually elongate moving objects, used on iPhone X app launch animation).
- **PERFORMANCE**: 60 fps lets you move things faster. 120 fps (iPad Pro 11"/12.9" 2018 Pro Motion) lets you move them faster still.

### 8. Work with Behavior, Rather than Animation

- The world isn't keyframed. Things have mass, momentum, friction, elasticity.
- Don't write `UIView.animate(withDuration: 0.3) { ... }`. Use `UIViewPropertyAnimator` or, better, a spring-based behavior model.
- Conceptually: don't end animations. Behaviors are always "ready to move next." A scrolling page in mid-coast should accept a new touch and continue smoothly.

## Spring Behaviors with Designer-Friendly Properties (803)

- Old: mass, stiffness, damping (physics class).
- New, designer-friendly: **damping** (0–100%, controls overshoot) and **response** (how quickly to converge).
- "Avoid the word _duration_" — it implies an end, but spring behaviors don't end; they're ready to move again.
- iPhone X uses ~80% damping for momentum-driven gestures (with a satisfying squish), 100% damping for tap-driven transitions (no overshoot needed).

## Bounciness as Discovery (803)

- The iPhone X cover-sheet flashlight button responds with a small bounce on tap. This _teaches_ that the button works _and_ hints that a more intentional press will activate it.
- Bounce as a hint that "something more is here."

## Project Momentum to Find Endpoints (803)

```swift
func project(initialVelocity: CGFloat, decelerationRate: CGFloat = UIScrollView.DecelerationRate.normal.rawValue) -> CGFloat {
  return (initialVelocity / 1000) * decelerationRate / (1 - decelerationRate)
}
```

- The PIP video in FaceTime: dragging the small camera-self view to a corner. With "find nearest endpoint at release time" you have to drag it 80% of the way. With **projection of momentum** at scrolling deceleration rate, a quick flick from one corner to the other works.
- Use the same projection for scales and rotations.

## The Life of a Button (804)

A 35-minute deep dive into the consideration behind a single button:

### Three phases of every interaction

1. **Before** — affordance: how does the user know this is interactive? Glass doesn't tell you to tap. We rely on prior experience + visual cues (button shape, label, color).
2. **During** — feedforward: highlight on touchdown, instant. Hit area larger than the visual button (especially small ones). Hit area cancellable: drag finger out → button unhighlights → release → no action.
3. **After** — feedback: confirmation (text + animation), result of the action. Maybe a stop button replaces the start button.

### Sound design (Hugo's section in 804)

- Four sound properties: timbre (tone color), frequency (low = big object), duration (short for repeated, longer for rare), loudness (UI sounds are subtle; ringtones are loud).
- Three sound options offered for the toast app's "Make Toast" button:
  - Option A: minimal click — felt slight.
  - Option B: realistic mechanical click — felt harsh and metallic.
  - Option C: friendly with built-in tonal "checkmark" confirmation — chosen.

## AR-Specific Design (805, 808)

- See `arkit-2-usdz.md` for the modeling and PBR side. The interaction side highlights:
  - **Get into AR fast** — give a fixed reference (the room) so users know to move the device. ARKit is faster in iOS 12 — most cases need no instruction.
  - Show feedback that the device is _detecting_ motion (the cube spinning under-glass icon in built-in AR onboarding).
  - **2D AR** is valid — see "Rainbrow" eyebrow-control game. Not all AR needs 3D.
  - **VR via ARKit** is valid — "Enter the Room" by ICRC. No headset needed.
  - **Screen-space text** stays readable from any angle/distance. Use it for measurements, labels.
  - **Movement of the device** is the primary interaction in AR; touch is secondary. Quick Look uses both: drag-to-pick-up + device-rotation-to-place is more precise than touch-only would be.

## Apple Pencil Design (809)

- 2nd-gen Pencil features: tap-to-switch-tools (configure in Notes / your app via `UIPencilInteraction`).
- Latency is the biggest user complaint; iOS 12 / iPad Pro 2018 latency is ~9 ms.
- Predict touches with `UITouchPrediction` — the system extrapolates the next stroke and renders it before the touch arrives, hiding the rest of the latency.

## Maps as a Design Pattern (810)

- Custom map content should respect zoom levels — show _less_ at low zoom, _more_ at high zoom.
- Annotations should cluster at low zoom; a hundred pins is unreadable.
- Color and shape carry meaning fastest. Text annotations are slow.

## Cross-references

- Designers should also study 802 ("Intentional Design") for Apple's broader design culture and 801 (a slot session whose recording is more abstract).
- Adding Delight (233) covers tactical UIKit techniques — haptics, sound, micro-interactions.
- iPhone X gestures explained at the OS level: 803 is the canonical reference. Re-watch every couple of years.
