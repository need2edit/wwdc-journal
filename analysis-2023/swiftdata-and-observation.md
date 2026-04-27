# WWDC 2023 — SwiftData & Observation

Two of WWDC 2023's most consequential frameworks for app developers. SwiftData replaces Core Data for new code, and Observation replaces ObservableObject + @Published as the SwiftUI data-flow model.

## Sessions Analyzed
- 10187 — Meet SwiftData (gateway)
- 10195 — Model your schema with SwiftData
- 10154 — Build an app with SwiftData
- 10196 — Dive deeper into SwiftData
- 10189 — Migrate to SwiftData
- 10149 — Discover Observation in SwiftUI

## SwiftData: Code-Only Persistence

SwiftData is built on top of Core Data but exposes a code-only Swift API powered by macros. **No xcdatamodeld file**. The schema IS your Swift code.

### The @Model Macro

```swift
@Model
class Trip {
  @Attribute(.unique) var name: String
  var destination: String
  var startDate: Date
  @Relationship(deleteRule: .cascade) var bucketList: [BucketListItem] = []
  @Transient var localOnlyCache: String?
}
```

`@Model` transforms stored properties to be tracked & persisted. Supports:
- Value types (String, Int, Float, Bool, Date, Data, URL, Decimal, UUID)
- Structs and enums (auto-encoded)
- Codable types
- Collections of any supported type
- Other `@Model` reference types (these become **relationships**)

Property-level macros:
- `@Attribute(.unique)` — uniqueness constraints, transformable, allowsCloudEncryption
- `@Relationship(deleteRule:inverse:)` — cascade, nullify, deny rules
- `@Transient` — exclude from persistence

### ModelContainer & ModelContext

- `ModelContainer` — the persistent store. Lives for the app's lifetime. Configured with the schema and storage URL/iCloud container.
- `ModelContext` — your read/write session. Tracks changes, performs save, supports undo/redo.

```swift
.modelContainer(for: Trip.self) // SwiftUI scene modifier
@Environment(\.modelContext) private var context
```

### @Query — The SwiftUI Bridge

```swift
@Query(sort: \.startDate, order: .reverse) var trips: [Trip]
@Query(filter: #Predicate<Trip> { $0.destination == "New York" }) var nyTrips: [Trip]
```

`@Query` is reactive: the view re-evaluates body when matching data changes. Predicate is a Swift macro — fully type-checked at compile time, replaces NSPredicate.

### Migration Strategies (10189)

- Lightweight: add property, add unique constraint → automatic.
- Custom: define `VersionedSchema` types and a `SchemaMigrationPlan` with explicit `MigrationStage`s.
- For Core Data → SwiftData: SwiftData uses Core Data's persistent store under the hood, so you can OPEN A CORE DATA STORE WITH SWIFTDATA without copy/migrate. The two can coexist on the same store.

This is huge for incremental migration: Add SwiftData @Model classes that mirror your NSManagedObject subclasses, point them at the same store URL, and migrate one screen at a time.

### Predicate Macro

`#Predicate<Trip> { $0.destination.contains(search) }` is a Swift macro that produces a Predicate value usable across SwiftData, Core Data, Foundation, and SwiftUI. Compile-time type-checked, supports closures, captures local variables.

## Observation: The New SwiftUI Data Model

`@Observable` macro replaces `ObservableObject` + `@Published`.

```swift
@Observable
final class FoodTruckModel {
  var donuts: [Donut] = []
  var orders: [Order] = []
}
```

### Three Property Wrappers

The decision tree for using `@Observable` types in SwiftUI is now THREE questions:

1. Is this state OWNED by this view? → `@State`
2. Is this state in the GLOBAL environment? → `@Environment`
3. Do you need a BINDING from this object? → `@Bindable`
4. Otherwise? → just declare it as a plain property.

```swift
struct ContentView: View {
  @State private var model = FoodTruckModel()  // owned
  @Environment(Account.self) private var account  // global
  @Bindable var donut: Donut  // binding-only
}
```

Note: `@Bindable` doesn't store. It just lets you write `$donut.name` for property bindings.

### Granular Tracking

The MAGIC: SwiftUI tracks property access PER INSTANCE. If a view's body reads `model.donuts.count` but not `model.orders`, only `donuts` mutations invalidate that view. This is dramatically more efficient than `ObservableObject`, which invalidates ALL observers when ANY @Published property changes.

### Migration from ObservableObject

Apple says it's "mostly just deleting annotations":
- `class X: ObservableObject` → `@Observable class X`
- `@Published var foo` → `var foo`
- `@ObservedObject var x` → `var x` (delete the wrapper) OR `@Bindable var x` (if you need bindings)
- `@EnvironmentObject var x` → `@Environment(X.self) var x`
- `@StateObject var x` → `@State var x`

### Computed Properties

Computed properties from stored ones JUST WORK. SwiftUI sees the access on the underlying stored properties.

For computed properties NOT backed by stored state (e.g., reading from a closure or external source), you can manually call `withMutation(keyPath:)` and `access(keyPath:)` from the `Observation` module to flag access.

## Observation + SwiftData

`@Model` IMPLIES `@Observable`. A SwiftData model class is automatically observable — you get persistence + observation in one annotation.

```swift
@Model class Dog {
  var name: String
  var isFavorite: Bool
  init(name: String) { self.name = name; self.isFavorite = false }
}
```

This single class works with `@Query`, with `@State` (transient instances), with `@Bindable`, and persists. Apple consolidated four older patterns (Core Data + ObservableObject + @Published + @ObservedObject) into one.

## Pathways

- **New developer**: 10149 → 10187 → 10154
- **Existing Core Data app**: 10189 → 10187 → 10195 → 10196
- **Schema deep-dive**: 10187 → 10195 → 10196

## Hidden Gems

- SwiftData supports CloudKit sync with a SINGLE configuration line — if your model has all-optional properties or sensible defaults.
- `@Attribute(.unique)` on a property creates a true unique constraint at the store level; insert-with-duplicate now uses upsert semantics.
- `@Query` accepts a `FetchDescriptor` for prefetching, limit, sort, predicate — you don't need to use the convenience initializer for everything.
- `ModelContext.autosaveEnabled` defaults to true on the main-actor context. Saves happen periodically and on scene phase transitions.
- `withAnimation { context.delete(item) }` works correctly with `@Query` — SwiftUI animates the row removal.
- For Observation, computed property access only works automatically if the computation reads tracked stored properties. Manual hooks exist for the edge cases.
- Observation tracking is BODY-scoped per call. Properties accessed in a child view are tracked separately, so passing a model down doesn't invalidate the parent.
