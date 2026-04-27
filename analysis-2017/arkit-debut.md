# ARKit Debut — WWDC 2017 Analysis

**Sessions covered:** 602 (Introducing ARKit: Augmented Reality for iOS), 604 (SceneKit: What's New — ARKit integration), 609 (Going Beyond 2D with SpriteKit — ARSKView), 610 (From Art to Engine with Model I/O), 704 (Creating Immersive Apps with Core Motion)

## Headline

WWDC 2017 introduced **ARKit**, instantly making iOS the largest AR platform on Earth. The framework is a high-level API that wraps **visual-inertial odometry (VIO)**, plane detection, hit testing, light estimation, and rendering integration into a single session-based API. It runs on every A9-and-up device on iOS 11 — no external sensors, no external setup, no pre-existing knowledge of the environment required.

## The Three Layers (602)

1. **Tracking** — `ARWorldTrackingSessionConfiguration` provides 6DOF pose using camera images + Core Motion data fused at high frequency. The base `ARSessionConfiguration` only provides 3DOF (orientation only) for older devices.
2. **Scene Understanding** — plane detection (horizontal only in v1), hit testing against detected planes / estimated planes / feature points, and light estimation.
3. **Rendering** — `ARSCNView` (SceneKit), `ARSKView` (SpriteKit billboards), or a Metal template if you bring your own renderer.

## Session-Based API (602)

- Create `ARSession`, configure with an `ARSessionConfiguration` subclass, call `run(_:)`.
- Receive `ARFrame` snapshots either by polling `session.currentFrame` or by becoming `ARSessionDelegate` and implementing `session(_:didUpdate:)`.
- Each `ARFrame` carries: a `capturedImage` (CVPixelBuffer), an `ARCamera` (transform + tracking state + intrinsics + projection matrix), an array of `ARAnchor`s, and a light estimate.

## ARAnchors Are The Universal Spatial Currency (602)

- An `ARAnchor` is a real-world position+orientation. Add custom ones to pin virtual content; the system adds `ARPlaneAnchor`s automatically when plane detection is on.
- `ARSCNView` automatically creates an `SCNNode` for each anchor and updates its transform every frame — implement the `nodeFor anchor:` delegate to provide your own node geometry.
- **HIDDEN GEM**: anchors persist across `run(_:)` calls — you can reconfigure (e.g. enable plane detection) without losing your custom anchors or dropping camera frames. Use the `.resetTracking` run option to reinitialize from a new origin point.

## Visual-Inertial Odometry (602)

- Camera frames find features (high-contrast points). The motion sensor integrates pose between frames at much higher frequency than the camera.
- **PERFORMANCE**: tracking quality is gated by visual complexity. A blank wall, low light, or a rapidly-moving scene all degrade to `ARTrackingState.limited` with `.insufficientFeatures`, `.excessiveMotion`, or `.initializing` reasons. Always implement `cameraDidChangeTrackingState:` to message the user — only the user can fix lighting or move the device.
- **HIDDEN GEM**: ARKit reads camera intrinsics (focal length, principal point) **every frame** and provides a convenient `projectionMatrix` on `ARCamera`. Use this directly; do not compute your own — it accounts for autofocus changes.

## Plane Detection (602)

- Set `configuration.planeDetection = .horizontal` and re-run. Set back to `[]` to stop. Previously detected planes remain in the scene as anchors.
- Planes have a `center` in plane coordinates and an `extent` (a fitted oriented bounding rectangle). They grow and merge over time — `session(_:didUpdate:anchors:)` fires on growth, `didRemove` fires when ARKit merges a smaller plane into a larger one. Update your visualization accordingly.
- **HIDDEN GEM**: vertical planes are NOT detected in 2017's ARKit (added in 2018's ARKit 1.5). Only horizontal planes parallel to gravity.

## Hit Testing (602)

Four hit-test types — choose by use case:

| Type | Use when |
|---|---|
| `.existingPlaneUsingExtent` | Snap to a known plane within its bounds (placing furniture on a detected table) |
| `.existingPlane` | Treat a detected plane as infinite (sliding a chair along the floor even where you haven't scanned) |
| `.estimatedHorizontalPlane` | No detected plane yet — fit a plane to coplanar feature points (great fallback for fast first placement) |
| `.featurePoint` | Project to the closest feature point along the ray (irregular surfaces, very small targets) |

Combine types in a single `hitTest(_:types:)` call. Results come back sorted by distance; `[0]` is the nearest.

## Light Estimation (602)

- `ARFrame.lightEstimate.ambientIntensity` defaults to 1000 lumens for a "neutral" exposure; brighter rooms produce higher values, darker rooms lower.
- **BEST PRACTICE**: assign directly to `SCNLight.intensity` — SceneKit's PBR lighting will pick it up automatically. Without this, virtual objects "glow" in dim environments because they're rendered as if perfectly lit.

## Rendering Integration (602)

- **SceneKit (`ARSCNView`)**: drop-in. Camera background, `SCNCamera` updates, `SCNLightProbe` for light estimation, automatic node↔anchor mapping.
- **SpriteKit (`ARSKView`)**: 2D sprites are rendered as billboards at projected anchor locations. See session 609 for the SpriteKit deep-dive.
- **Metal**: use the Xcode template. Four steps each frame: (1) draw the captured image as a textured quad with `displayTransform(for:viewportSize:)`, (2) set view matrix = `inverse(camera.transform)`, projection matrix = `camera.projectionMatrix(for:viewportSize:zNear:zFar:)`, (3) update lights from `lightEstimate`, (4) iterate `frame.anchors` to position geometry.

## CVPixelBuffer Lifetime Trap (602)

`ARFrame.capturedImage` is vended by AVFoundation. **WARNING**: holding too many ARFrames or their pixel buffers throttles AV capture — your session will stop receiving updates. Drop references promptly; if you need the image later, copy it.

## Face Tracking on TrueDepth (mentioned in 602; full API ships in iOS 11.x)

- `ARFaceTrackingConfiguration` runs on the front-facing TrueDepth camera (iPhone X exclusive at launch).
- Vends `ARFaceAnchor` per detected face with: a 3D mesh (`ARFaceGeometry` ~1200 vertices), `blendShapes` dictionary (~50 expressions like `.eyeBlinkLeft`, `.jawOpen`, `.mouthSmileRight`), and a fixed-coordinate "leftEye" / "rightEye" / "lookAtPoint".
- **HIDDEN GEM**: the blend-shape values are 0.0–1.0 and sample at 60 Hz — perfect drivers for animated puppets. Animoji literally uses these.
- The mesh is occlusion-ready: render virtual hats / glasses behind the face mesh material with `.colorBufferWriteMask = []` to write only depth, so the face properly occludes virtual content behind it.

## Common Pitfalls and Tips

- **PERFORMANCE**: `ARSession` ramps up `AVCaptureSession` and `CMMotionManager` under the hood — call `session.pause()` when your view leaves screen to free CPU/GPU and let other capture clients use the camera.
- **BEST PRACTICE**: declare `arkit` as a required device capability in Info.plist if your app cannot fall back to 3DOF — otherwise non-A9 devices will install the app and crash on world tracking.
- **BEST PRACTICE**: model assets in real-world meters. Reality Composer doesn't exist yet; design objects to physical scale or your virtual chair will be the size of a building.
- **DEPRECATION TRAP**: the camera, motion, and AVAudio session permissions all need entries in Info.plist (`NSCameraUsageDescription`). Without these the session silently fails on launch.

## Cross-references

- See `vision-coreml-on-device-ml.md` for combining ARKit camera frames with Vision/Core ML for real-time scene classification.
- See `metal2-graphics-pipeline.md` for the Metal-backed renderer template details.
