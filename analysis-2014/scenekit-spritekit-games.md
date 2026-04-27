# SceneKit, SpriteKit & Games — WWDC 2014 Analysis

**Sessions covered:** 606 (What's New in SpriteKit), 608 (Best Practices for Building SpriteKit Games), 609 (What's New in SceneKit), 610 (Building a Game with SceneKit), 611 (Designing for Game Controllers), 612 (Motion Tracking with the Core Motion Framework), 602 (Ingredients of Great Games)

## Headline

iOS 8 brings **SceneKit to iOS** for the first time (it was Mac-only since 10.8), and dramatically expands **SpriteKit** with shaders, lighting, per-pixel physics, inverse kinematics, physics fields, and a built-in Xcode SpriteKit editor. The two frameworks gain bidirectional integration: include 3D content (`SK3DNode`) inside 2D scenes; use SpriteKit textures and audio in 3D scenes.

## SpriteKit Major Additions (session 606)

### Custom Shaders
- New **`SKShader`** class — attach a GLSL ES 2.0 fragment shader to `SKSpriteNode`, `SKShapeNode` (both stroke and fill), `SKEmitterNode`, `SKEffectNode`, or even the entire `SKScene`.
- Built-in uniforms passed automatically: `u_texture`, `u_sprite_size`, `u_time`, `u_path_length`. Plus user-defined `SKUniform`s.
- HIDDEN GEM: `SKDefaultShading()` callable inside your shader returns "what SpriteKit would have rendered" — apply effects ON TOP of the default rendering instead of replacing it (606).
- BEST PRACTICE: load shaders from `.fsh` files (NOT strings) — file-based shaders share a backing instance per source, which lets the GPU **batch draw calls** for sprites using the same shader (606).
- WARNING: changing shader source mid-frame forces a recompile. Avoid (606).

### Lighting and Shadows
- **`SKLightNode`** — add a 2D dynamic light to your scene. Properties: `lightColor`, `ambientColor`, `shadowColor`, `falloff`. Up to 8 lights per sprite (606).
- HIDDEN GEM: **automatic normal map generation**. `sprite.normalTexture = SKTexture.texture(byGeneratingNormalMapWithSmoothness:contrast:)` analyzes the sprite's texture and synthesizes a normal map — your sprite gets fake-3D bumpiness with one line, no artist work required (606).
- BEST PRACTICE: limit light counts. Multiple lights per sprite are supported but expensive. More than 2 lights affecting one sprite hits 60fps on lower-end iOS hardware (606).

### Per-Pixel Physics Bodies
- **`SKPhysicsBody(texture:size:)`** — automatically generate a physics body that traces the texture's alpha outline. Gears that mesh, hammers that tumble correctly, jagged terrain — all with one line (606).
- Tunable via `alphaThreshold` for textures with semi-transparent pixels.
- WARNING: the cost scales with texture size. A 2K×2K texture takes proportionally longer to introspect; even if the rendered sprite is small, the source matters (606).

### Constraints, Inverse Kinematics, Physics Fields
- **`SKConstraint`** — declarative position/orientation/distance constraints. Eliminates boilerplate "in `update`, snap this node to follow that node" code (606).
- **Inverse Kinematics** — `SKReachConstraint` per joint, then `SKAction.reach(to:rootNode:duration:)` drives the chain. Build a robot arm, it reaches naturally (606).
- **Physics Fields** — `SKFieldNode` with 10+ field types (radial gravity, linear gravity, drag, vortex, noise, magnetic, electric, spring, etc.). Compose them like Legos for emergent behavior (606).

### SpriteKit Editor in Xcode
- Visual scene composer **inside Xcode 6**. Drag sprites, set physics bodies, configure lighting, set up IK chains, edit shaders with live WYSIWYG.
- HIDDEN GEM: `[scene writeToURL:atomically:]` serializes any runtime scene to an `.sks` file — load it in Xcode editor to debug what's actually on screen at any moment (606).
- BEST PRACTICE: separate game content (in `.sks` files) from game logic (in code). Your designers iterate on levels independently from your engineers (606).

## SceneKit on iOS (session 609)

- **First iOS release of SceneKit**. Same API as Mac (since OS X 10.8). High-level scene graph for 3D, on top of OpenGL ES (and Metal on A7).
- **Camera, lights, geometry, materials, animations** — the full Hollywood production stack.
- **`SCNScene`** loaded from COLLADA `.dae` files exported by tools like Blender, Maya, Cinema 4D.
- **Physics** integrated — `SCNPhysicsBody`, joints, gravity. Same conceptual model as SpriteKit's 2D physics.
- HIDDEN GEM: **3D Inverse Kinematics** with `SCNIKConstraint` — the Mac/iPad has the same per-joint reach constraints as SpriteKit's 2D IK. Drive a 3D character's arm with one line (609).

## SpriteKit + SceneKit Integration (session 606)

- **`SK3DNode`** — embed a `SCNScene` inside a `SpriteKit` scene. The 3D content renders in-line as part of the SpriteKit draw pass (606).
- Conversely, **SceneKit can use SpriteKit textures** as material sources. Use SpriteKit's automatic Texture Atlas generator for 3D assets too (606).
- Same audio API for both. Same Texture Atlas pipeline.
- HIDDEN GEM: a 2D background with 3D characters flying through, or a 3D scene with 2D HUD overlay — implementable with no manual GL/Metal interleaving (606).

## SpriteKit Texture Atlases (session 606)

- Up to **4K × 4K** texture atlases now supported. (Previously 2K.)
- **Runtime atlas generation** — `SKTextureAtlas(dictionary:)` from runtime images (downloaded content, user photos). Stitches them into an atlas for efficient batched drawing (606).

## Game Controllers (session 611)

- **`GCController`** — third-party MFi-certified gamepads (Mad Catz, SteelSeries, etc.) work with iOS 7+. iOS 8 adds **profile** support: extended (full PlayStation/Xbox layout) vs micro (Apple TV remote-style).
- HIDDEN GEM: **detect controllers via NSNotificationCenter** (`GCControllerDidConnect`/`Disconnect`) — handle hot-pluggable controllers gracefully (611).

## Core Motion + Game Sensors (session 612)

- **`CMMotionActivity`** classifications (walking, running, automotive, cycling, stationary) usable in games for context-aware behavior.
- **Pedometer API** integration — your game can react to player movement.
- **Indoor altimeter** (iPhone 6 with barometer) — detect floor changes.

## Best Practices

- **Use the SpriteKit Editor for content, code for logic** — separate the two for parallel team workflows (606).
- **Share `SKShader` instances across sprites** that need the same effect — enables draw-call batching (606).
- **Use automatic normal maps** before commissioning artist normal maps. Often good enough; saves immense art time (606).
- **Use per-pixel physics bodies** for shapes that don't fit a circle/rectangle/polygon. Worth the runtime cost for accurate collision (606).
- **Use `SKConstraint` and `SKAction` declaratively** instead of imperative `update:` code — easier to reason about, more performant (constraints batch across nodes) (606).
- **For 3D, prefer SceneKit** unless you have specific Metal needs. SceneKit handles GPU efficiency; you focus on content (609).
- **Test on the OLDEST device you support** — SpriteKit/SceneKit can render the same scene at 60fps on iPhone 5s and 30fps on iPhone 4s. Profile early.

## Hidden Gems

- HIDDEN GEM: **`SKMutableTexture`** — texture you can write to from CPU each frame. Use for procedural textures, GPU-CPU effect chains, sending custom data to a shader as a texture (606).
- HIDDEN GEM: **`SKTexture.texture(noiseWithSmoothness:size:grayscale:)`** generates coherent (Perlin-style) noise textures procedurally. Use for atmospheric effects, terrain generation, shader inputs (606).
- HIDDEN GEM: SpriteKit's automatic Texture Atlas generator (in Xcode 6) handles **per-resolution atlases** automatically. Drop @2x/@3x assets into a folder; build a single atlas per resolution; only the right one ships to each device (606).
- HIDDEN GEM: **physics weld joints** can be created with `SKPhysicsBody.pinned = true` AND `allowsRotation = false`. One-line gear locking onto a board (606).
- HIDDEN GEM: SceneKit on iOS uses **Metal automatically** on A7+ devices. You get the Metal performance benefit without rewriting any code (609).
- PERFORMANCE: SceneKit `SCNNode.runAction()` and SpriteKit `SKNode.runAction()` are designed to play well with the physics step. Don't fight them with manual `update:` math (606).

## Cross-references

- **Metal (603)** — SpriteKit and SceneKit are clients of Metal on supported devices. Adopt the high-level frameworks unless you need the bare-metal control.
- **Game Center (Game Controllers - 611)** — `GCController` integrates with Game Center for player profile awareness.
- **App Extensions (217)** — game today widgets are great for daily-challenge games; the SpriteKit scene runs inside the widget.
- **HealthKit (203)** — fitness games can read step data, write workout data, integrate with Apple Watch (announced for spring 2015).

## Migration Guidance

- **iOS games using OpenGL ES directly**: evaluate moving the rendering layer to SceneKit (3D) or SpriteKit (2D). The high-level frameworks adopt Metal on A7+ for free; OpenGL ES is the legacy path Apple is steering away from.
- **2D games using `CADisplayLink` + custom rendering**: SpriteKit's editor + automatic batching often beats custom 2D engines on programmer time AND runtime performance. Consider the rewrite for new games.
- **Mac games using SceneKit**: minimal porting effort to ship on iOS — same API, just careful about asset sizes for mobile.
- **Cross-platform (iOS + Android + Web)**: stay with cross-platform engines (Unity, Unreal, cocos2d-x). SpriteKit/SceneKit are Apple-only.
