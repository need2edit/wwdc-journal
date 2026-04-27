# Games & Graphics (GameplayKit, Metal, Model I/O, ReplayKit, SpriteKit, SceneKit) — WWDC 2015 Analysis

**Sessions covered:** 608 (Introducing GameplayKit), 609 (Deeper into GameplayKit with DemoBots), 605 (Going Social with ReplayKit and Game Center), 602 (Managing 3D Assets with Model I/O), 603 (What's New in Metal, Part 1), 607 (What's New in Metal, Part 2), 610 (Metal Performance Optimization Techniques), 604 (What's New in SpriteKit), 606 (Enhancements to SceneKit)

## Headline

A massive year for game development on Apple platforms. **GameplayKit** debuts as Apple's first dedicated gameplay framework — a unified library of common game algorithms (entity-component-system, state machines, agents/steering, pathfinding, MinMax AI, random distributions, rule systems). **Model I/O** debuts as a 3D asset pipeline framework. **ReplayKit** debuts to record and share game gameplay. Metal expands with new compute and tessellation, SpriteKit and SceneKit get rich editors and integrate with Metal under the hood.

## GameplayKit (608, 609)

Seven major systems, each addressing a perennial game-dev problem:

### 1. Entity-Component System (ECS)

- `GKEntity` — a container of components.
- `GKComponent` — a single piece of behavior (Move, Shoot, Health, Render). Subclass with custom properties and `update(deltaTime:)`.
- `GKComponentSystem` — collects components of a single class across all entities for ordered updates.
- **HIDDEN GEM**: removing a component dynamically (e.g., remove `MoveComponent` to "root" an entity to the ground) is the cleanest way to express temporary status effects. The rest of the game doesn't need to know about magic spells — it just sees an entity that no longer can move.
- **BEST PRACTICE**: don't update components via their entity if order matters. Add them to a `GKComponentSystem`, update systems in a deliberate order each frame.

### 2. State Machines

- `GKStateMachine` — a finite state machine, in exactly one state at a time.
- `GKState` — `didEnter`, `willExit`, `update(deltaTime:)`, override `isValidNextState(_:)` to constrain edges.
- Replaces ad-hoc `switch` statements scattered through your code. Animation states, AI states, level UI states.

### 3. Agents, Goals & Behaviors (steering)

- `GKAgent` — autonomous point mass with mass, max speed, max acceleration, bounding radius, position, rotation. **It is also a `GKComponent`** — drop it on an entity.
- `GKBehavior` — weighted dictionary of `GKGoal`s.
- Goals: seek, flee, intercept, wander, separate, align, cohere (the flocking trio), avoidObstacles, avoidAgents, followPath, stayOn, targetSpeed.
- Compose flocking from separate + cohere + align. Compose racing from followPath + avoid + targetSpeed.
- `GKAgentDelegate` with `agentWillUpdate(_:)` and `agentDidUpdate(_:)` to sync your `SKNode` / `SCNNode` to/from the agent simulation.
- **HIDDEN GEM**: agent units are dimensionless and game-world specific — pick numbers that match the scale of your world (a kilometer-scale game vs. a foot-scale game need very different agent constants).

### 4. Pathfinding

- `GKGraph` (abstract), `GKGridGraph` (2D grid), `GKObstacleGraph` (around polygonal obstacles).
- For obstacle graphs, the **buffer radius** is your character's bounding radius — used to inflate obstacles so paths don't cut corners.
- `findPath(from:to:)` returns an array of `GKGraphNode`. Subclass nodes for non-spatial costs (e.g., forest terrain doubles move cost).
- **HIDDEN GEM**: `SKNode.obstacles(fromNodeBounds:)`, `obstacles(fromNodePhysicsBodies:)`, and `obstacles(fromSpriteTextures:)` — generate `GKObstacleGraph` directly from a SpriteKit scene's nodes. Live-update as you add/remove towers in a tower-defense game.

### 5. MinMax AI

- `GKMinmaxStrategist` — classic decision-tree AI for turn-based games.
- You implement three protocols: `GKGameModel` (state snapshot), `GKGameModelUpdate` (a move), `GKGameModelPlayer` (a player).
- `bestMove(for:)` returns the move that minimizes the opponent's best response.
- **Difficulty knob**: `maxLookAheadDepth` — higher = stronger play, exponentially more expensive.
- `randomMove(for:)` to pick from the top-N moves with controlled randomness — gives the AI human-like imperfection.

### 6. Random Sources & Distributions

- Reasons to NOT use `rand()`: not deterministic across platforms (bad for networked games), single shared sequence (one new call somewhere alters all consumers), no distribution control.
- Sources: `GKARC4RandomSource` (Goldilocks), `GKLinearCongruentialRandomSource` (low overhead), `GKMersenneTwisterRandomSource` (high quality, memory-heavy). All deterministic with same seed.
- `GKRandomDistribution` (uniform), `GKGaussianDistribution` (bell curve, biased to mean), `GKShuffledDistribution` ("fair random" — guarantees you'll see every value before any repeats).
- Convenience: `GKRandomDistribution.d6()`, `.d20()`, custom-sided dice.
- `GKARC4RandomSource.sharedRandom().arrayByShufflingObjects(in: deck)` — Fisher-Yates for free.
- **HIDDEN GEM**: `NSSecureCoding` on the random source means you can serialize the RNG state with your save file — same sequence on reload (anti-cheat or replay).

### 7. Rule Systems

- `GKRuleSystem` — collection of `GKRule`s and asserted facts.
- Rules: `NSPredicate` + an action (assert facts, custom block).
- "Fuzzy logic": facts have a grade (0–1). A driver who is "kinda close, kinda far" can blend braking and accelerating proportionally.
- `evaluate()` runs all rules; whenever a rule asserts a new fact, evaluation restarts from the top until stable.
- Use case: simulation rules ("when traffic light is yellow AND I'm fast → keep going"), AI decision-making.

## Metal (603, 607, 610)

- **Compute shaders** integrated end-to-end into Metal — no need to round-trip through OpenCL.
- Indirect drawing — submit draw calls whose parameters are computed by a previous compute pass entirely on the GPU.
- New per-frame and per-draw uniform buffer techniques in 610 — triple-buffer your dynamic uniforms with a semaphore so you never block the CPU on the GPU.
- **PERFORMANCE**: every uniform update should be a single `memcpy` into the right slot of a `MTLBuffer` shared between CPU and GPU; never use a separate buffer per draw — buffer creation has nontrivial cost.
- Metal Performance Shaders (MPS) — Apple-tuned image filters (Gaussian blur, Sobel, histogram, image integral, transpose) and matrix operations on Metal. Fastest path on each GPU generation without you tuning per-device.
- SpriteKit, SceneKit, and Core Image all sit on Metal automatically when available; fallback to OpenGL ES on devices without Metal.

## Model I/O (602)

A 3D asset pipeline framework. Read/write USDZ predecessors and many other formats; introspect mesh/material/texture data; bake lighting; convert between coordinate systems.

- `MDLAsset(url:)` to load OBJ, PLY, ABC, USD; serialize with `MDLAsset.export(to:)`.
- Bridges to MTKMesh/MTKSubmesh for direct Metal rendering.
- Bridges to SCNScene for SceneKit.
- Lighting bake: light maps and ambient occlusion baked into vertex colors or new UV channels.
- Sphere harmonics / spherical harmonic lights for realistic indirect lighting at real-time cost.

## SpriteKit (604)

- New scene editor in Xcode supports particles, physics, actions, and references via SKReferenceNode.
- `SKAudioNode` — spatial audio attached to a sprite, panned/dampened by position.
- `SKConstraint` — constrain nodes to follow others (orientation, distance) — the editor has a UI for this.
- Custom Metal shaders via `SKShader` with first-class uniform support.
- Tile maps and SKTransition between scenes.
- Field nodes (gravity, electric, magnetic, vortex, noise, turbulence) carried over from UIKit Dynamics.
- Integration with on-demand resources for level downloads.

## SceneKit (606)

- New SceneKit editor in Xcode (the same editor that hosts SpriteKit).
- Scene transitions, audio nodes, model I/O bridges, ambient occlusion baking, light maps.
- Physically-based rendering (PBR) with metalness/roughness materials.
- Cascaded shadow maps for directional lights with high-quality shadows over large areas.
- IK constraints, morph targets, vertex animations.

## ReplayKit (605, 107)

- New framework for in-app screen + audio recording and broadcasting.
- `RPScreenRecorder.shared().startRecording { error in ... }` to start; `stopRecording { previewVC, error in ... }` returns a preview view controller with trim/share/discard UI.
- Built-in Game Center integration to pin the clip to your game's leaderboard.
- HIDDEN GEM: works for any app that's full-screen — not strictly games. Tutorials and demos can record their own UI for sharing.

## Game Center (605)

- Guest player accounts so multiplayer doesn't require iCloud sign-in for everyone.
- Unified server environment (development & sandbox merged with production) — eliminates the QA-time discrepancy.
- Player IDs continue to be unique per-game per-player (no cross-app tracking).

## Cross-references

- GameplayKit pathfinding (608) integrates directly with SpriteKit scenes (604).
- Metal performance work (610) underpins SpriteKit/SceneKit performance (604, 606).
- Model I/O (602) is the asset pipeline that feeds SceneKit 3D content (606).
- ReplayKit (605) plus Game Center plus on-demand resources (214) is the holistic story for a content-rich game.
