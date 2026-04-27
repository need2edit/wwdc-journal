# ARKit 2, USDZ, and AR Quick Look — WWDC 2018 Analysis

**Sessions covered:** 602 (What's New in ARKit 2), 603 (Integrating Apps and Content with AR Quick Look), 605 (Inside SwiftShot: Creating an AR Game), 610 (Understanding ARKit Tracking and Detection), 805 (Creating Great AR Experiences), 808 (Prototyping for AR), 102 (Platforms State of the Union §AR)

## Headline

WWDC 2018 turned AR from a tech demo into a system feature. Three big shifts: **persistent and shared world maps** (multi-user AR experiences via peer-to-peer with no cloud), the new **USDZ file format** (developed with Pixar, supported across iOS in Messages/Mail/Safari/News/Notes/Files/Quick Look), and **AR Quick Look** itself — a system-wide 3D viewer you embed with three lines of HTML or one Quick Look API call. ARKit 2 also adds image _tracking_ (not just detection), 3D object detection from a scan, environment texturing for realistic reflections, and gaze + tongue tracking on iPhone X.

## ARWorldMap: Persistence and Multi-User (602, 605)

- The mapping the world tracker builds is now exposed as `ARWorldMap`, a serializable object with anchors (plane, custom, image, environment probe), raw feature points, and the extent.
- `session.getCurrentWorldMap { map, error in ... }` retrieves it. Set `configuration.initialWorldMap` and `session.run(configuration)` to start a session in a previously-mapped space.
- **HIDDEN GEM**: World maps share via _whatever transport you choose_ — AirDrop, MultipeerConnectivity (Bluetooth/local Wi-Fi), iCloud, your own server. No cloud required. Multi-user games like SwiftShot share the map peer-to-peer with no internet.
- All players share one coordinate system, which means custom anchors placed by player A appear in the same physical position to player B.
- **BEST PRACTICE**: read `ARFrame.worldMappingStatus` (`.notAvailable` → `.limited` → `.extending` → `.mapped`) to gate your "Share World Map" button. Don't let the user share until the status is `.mapped`. Show an activity indicator when `.extending` to encourage them to keep moving.

## SwiftShot Architecture (605)

- Apple's reference multi-user AR game, full source code released under a permissive license.
- Uses MultipeerConnectivity for the world map handoff, then peer-to-peer streaming of game state.
- Demonstrates the GameplayKit ECS pattern atop ARKit anchors, deterministic physics for replays, and CRDT-like resolution of conflicting input across peers.
- Worth reading even if you're not making AR games — its networking layer is a solid model for multi-device synchronized state.

## Environment Texturing (602)

- New `ARWorldTrackingConfiguration.environmentTexturing = .automatic` (or `.manual`).
- ARKit builds a reflection cube map from camera frames as the user looks around. For unscanned regions, ML-trained models hallucinate plausible texture (lighting from above, ambient color tinting).
- Provided as `AREnvironmentProbeAnchor` with a Metal cube map texture and physical extent (for parallax correction).
- Fully integrated with `ARSCNView` — just enable in config, SceneKit picks up the probes automatically.
- **HIDDEN GEM**: dramatic visual upgrade for shiny/metallic objects. The kettle in the demos went from fake-looking to convincingly there because it now reflects the wooden table, the green leaves on the side, the orange of the fruit on the counter — all generated on-device in real time.

## Image Tracking (vs. Detection) (602, 610)

- iOS 11.3 introduced image _detection_ — known 2D images get a six-degrees-of-freedom anchor, but the image must stay still.
- iOS 12 adds image _tracking_ — the anchor updates at 60 fps as the image moves. Use cases: trading cards, magazine pages that flip, board games being moved.
- Two configurations: world tracking with `detectionImages` set (legacy, also gets the upgrade), or the new `ARImageTrackingConfiguration` for stand-alone tracking with no world tracking required.
- **HIDDEN GEM**: `ARImageTrackingConfiguration` doesn't use the motion sensor and therefore works in scenarios where world tracking fails — moving platforms (elevators, trains, cars). If you only need image tracking, use this lighter config.
- `ARWorldTrackingConfiguration.maximumNumberOfTrackedImages` defaults to 1; set higher for double-page magazines etc.

## Object Detection (602, 610)

- New `ARObjectAnchor` for known 3D objects (toys, museum exhibits, household items).
- Objects must first be scanned via the `ARObjectScanningConfiguration`. Apple ships full source for a scanner app.
- Scanned objects export as `.arobject` files that drop directly into Xcode asset catalogs.
- **BEST PRACTICE**: scan from multiple viewpoints, but you don't have to scan sides that will face a wall. Use the scanner's "test detection" flow against different lighting conditions before shipping.
- Limitations: must be rigid, well-textured, non-reflective, roughly tabletop-sized.

## Face Tracking Adds Gaze + Tongue (602)

- `ARFaceAnchor.leftEyeTransform` / `.rightEyeTransform` — six degrees of freedom for each eye.
- `ARFaceAnchor.lookAtPoint` — intersection of the two gaze rays. Useful as an input mechanism (eye-controlled UI).
- New blend shape: `.tongueOut` — value 0–1 like the existing 50+ blend shapes. The first thing kids do with Animoji is stick out their tongue, hence its inclusion.
- **HIDDEN GEM**: nothing about Animoji is private. ARKit gives you all 50+ blend shape coefficients plus head pose; you can ship your own Memoji-style avatar in your app.

## ARKit 2 Other Improvements (602)

- Faster initialization, much faster plane detection (especially in difficult environments — dim, partially-textured rooms).
- Continuous autofocus for AR (introduced 11.3) is more aggressively tuned for AR-specific scenes in iOS 12.
- New default video format: **4:3** instead of 16:9 (matches iPad aspect ratio). Existing apps need to rebuild against the iOS 12 SDK to get this.
- Vertical plane detection (added in 11.3) has more accurate boundaries.

## USDZ — The File Format (603)

- Built with Pixar atop Universal Scene Description (USD), the same format Pixar uses for Toy Story 4.
- USDZ is an _uncompressed_ zip archive containing one `.usdc` (binary USD with mesh, animation, materials) followed by texture image files. Spec is open and published at graphics.pixar.com.
- Supported in iOS 12 / macOS Mojave natively in: Files, Mail, Messages, News, Notes, Safari, Quick Look, SceneKit, Model I/O.
- Adobe announced native USDZ support in Creative Cloud (Project Aero, Dimension, Photoshop). USDZ is positioned as the "JPEG of 3D."
- **TOOL**: `xcrun usdz_converter input.obj output.usdz -g <groupName> <albedo.png> <metallic.png> <roughness.png> <normal.png> <ao.png> <emissive.png>` — ships in Xcode 10. Converts OBJ, Alembic, and existing USDA/USDC files.

## AR Quick Look Integration (603)

**Three lines of HTML** to put a 3D model in any web page:
```html
<a rel="ar" href="model.usdz">
  <img src="thumbnail.jpg">
</a>
```
- Safari renders a thumbnail with the AR badge in the top-right corner. Tap loads the model directly into AR Quick Look — no link navigation, no URL change, optimized flow.
- MIME type matters: USDZ files must be served as `model/vnd.usdz+zip` (still pending official IANA registration; Apache configs can use `model/vnd.pixar.usd` as a fallback).
- In iOS apps: standard `QLPreviewController` with the USDZ file URL — same API used for PDFs and images. The transition view (returned from `previewController(_:transitionViewFor:)`) gives you the seamless zoom-out animation. Use a `UIButton` with the thumbnail image so taps highlight properly.

## Authoring Models for AR Quick Look (603, 805)

Six things matter when modeling for AR Quick Look:

1. **Placement** — face +Z (toward the user), base on the `y=0` plane, natural pivot at the origin. Test by asking yourself "if I asked a child to draw this object, which profile would they draw?" That's your starting orientation.
2. **Physical size** — set in real-world units. Models that don't have a natural size (cartoon characters) should default to desktop size — easy to place anywhere, easy to scale up for photo ops.
3. **Animation** — loop, stay near origin (no walk cycles that move 1m to the side; users can't grab the moving object), keep bounding box consistent. For inherently-moving things (a swimming fish), build a small base scene (an aquarium) so the user manipulates the scene, not the moving object.
4. **Contact shadow** — never bake one into the model. AR Quick Look adds and removes the shadow as you transition between object mode and AR mode. The shadow is generated from the **first frame** of any animation, so choose a neutral first frame.
5. **PBR materials** — albedo, metallic, roughness, normal map, AO, emissive. Use system PBR + reflection probes for realism.
6. **Transparency** — separate materials for transparent and opaque parts, encode transparency in alpha channel. Don't use it for cutouts (leaf edges, butterfly wings) — use a proper mesh instead.

## PBR Quick Reference (805)

- **Albedo** (RGB or RGBA) — base color. Avoid extreme bright or dark values that won't blend in real environments.
- **Metallic** (grayscale, mostly black/white) — which surfaces are conductors vs. insulators. The light interaction physics differ fundamentally.
- **Roughness** (grayscale) — micro-surface variation. The single biggest visual quality lever you have. Vary it within materials; perfectly uniform roughness looks fake.
- **Normal map** (RGB) — fakes geometric detail without polygons. Bake from a high-poly source mesh in your DCC tool.
- **Ambient occlusion** (grayscale) — baked self-shadowing in crevices. Subtle but adds depth. Always bake; never use SSAO at runtime in AR.
- **Emissive** (RGB) — surfaces that glow (TV screens, LED indicators).

## Memory and Polygon Budgets (805)

- Target 60 fps and minimal battery drain. Test from every angle, near and far.
- Recommended for high-memory devices (iPhone 7 Plus, 8 Plus, X, iPad Pro 12.9"): ~100k polygons, one set of 2k×2k PBR textures, ~10 seconds animation.
- AR Quick Look automatically downsamples textures on lower-memory devices. Meshes and animations are NOT downsampled — model for the high end.
- **BEST PRACTICE**: in `prepare()` for any custom rendering, freeze transforms and merge adjacent vertices in your DCC tool before export. Single material per model when possible — lets you optimize texture packing.

## Light Estimation and Shadow Don'ts (805)

- ARKit's `lightEstimate` exposes intensity and color temperature. Apply to your virtual lights so objects react to room lighting changes.
- **URGENT** for shadows: don't cast a sharp directional shadow at an angle — it'll fight whatever the real environment is doing. Place the directional light directly overhead and reduce intensity for a subtle shadow that looks plausible in any environment. Better still: bake a soft drop shadow into the model's base.

## Cross-references

- Quick Look fundamentals: 237 (Quick Look Previews from the Ground Up).
- AR Quick Look in product catalogs at Apple: the new web showcase at `developer.apple.com/arkit/gallery` demonstrates Safari integration and PBR best practices.
- For 3D rendering performance details: 612 (Metal Game Performance Optimization), 606 (Metal for Ray Tracing Acceleration).
