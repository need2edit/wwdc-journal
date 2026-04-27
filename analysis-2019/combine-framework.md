# Combine Framework — WWDC 2019 Analysis

**Sessions covered:** 722 (Introducing Combine), 721 (Combine in Practice), 712 (Advances in Networking, Part 1 — DataTaskPublisher), 226 (Data Flow Through SwiftUI — `onReceive` and `BindableObject`)

## Headline

Apple's first-party answer to RxSwift / ReactiveSwift. A unified, generics-based, type-safe, request-driven (back-pressure) declarative API for processing values over time. Three concepts only: **Publisher**, **Subscriber**, **Operator**.

## The Three Concepts (722)

### Publisher (struct, value type)
```swift
protocol Publisher {
    associatedtype Output
    associatedtype Failure: Error
    func subscribe<S: Subscriber>(_ subscriber: S)
        where S.Input == Output, S.Failure == Failure
}
```
If a publisher cannot fail, set `Failure = Never`.

### Subscriber (class, reference type — receives & mutates state)
Three callbacks: `receive(subscription:)`, `receive(_:)`, `receive(completion:)`. Completion is optional and at most one.

### Operator (struct — both Publisher & internally a Subscriber)
Subscribes upstream, transforms values, sends downstream. Examples: `map`, `filter`, `removeDuplicates`, `debounce`, `throttle`, `delay`, `prefix`, `tryMap`, `flatMap`, `compactMap`, `decode`, `catch`, `retry`, `assertNoFailure`, `mapError`, `replaceError(with:)`, `Zip`, `CombineLatest`, `merge`, `share`, `multicast`, `assign(to:on:)`, `sink`, `receive(on:)`, `subscribe(on:)`.

## The Naming Mental Model (722)

| | Synchronous | Asynchronous |
|---|---|---|
| **Single value** | `Int` | `Future` |
| **Many values** | `[Int]` | `Publisher` |

If you know how to do something with an Array, try the same name on a Publisher. `compactMap`, `prefix`, `filter`, `dropFirst` all work the same way. **HIDDEN GEM**: this is the single most useful intuition for navigating Combine's huge operator surface.

## Subjects: Imperative Bridges (721)

When you need to inject values into a Combine pipeline imperatively (especially from existing callback code):

- `PassthroughSubject<Output, Failure>` — no stored value; subscribers only see values sent **after** they subscribe.
- `CurrentValueSubject<Output, Failure>` — stores last value; new subscribers immediately get it.

`subject.send(value)` is how you push values into the chain.

## Cancellation (721)

- `Cancellable` protocol with one method: `cancel()`.
- `AnyCancellable` is a class wrapper that **automatically cancels on `deinit`**. Store it in an ivar and ARC handles teardown — no manual cancellation required.

```swift
private var cancellables = Set<AnyCancellable>()
publisher.sink { ... }.store(in: &cancellables)
```

## Property Wrapper: @Published (721)

- `@Published var name: String = ""` adds a Publisher to any property using Swift 5.1's brand-new `propertyWrapper` feature.
- Access value normally: `name`. Access publisher: `$name`.
- This is THE pattern for connecting model state to Combine pipelines.

## Form Validation Example (721)

A complete real-world pattern from the talk for sign-up validation:

```swift
@Published var username = ""
@Published var password = ""
@Published var passwordAgain = ""

var validatedPassword: AnyPublisher<String?, Never> {
    Publishers.CombineLatest($password, $passwordAgain)
        .map { (pw, pwAgain) in
            guard pw == pwAgain, pw.count >= 8 else { return nil }
            return pw
        }
        .eraseToAnyPublisher()
}

var validatedUsername: AnyPublisher<String?, Never> {
    $username
        .debounce(for: 0.5, scheduler: RunLoop.main)
        .removeDuplicates()
        .flatMap { username in
            Future { promise in
                self.usernameAvailable(username) { available in
                    promise(.success(available ? username : nil))
                }
            }
        }
        .eraseToAnyPublisher()
}

var validatedCredentials: AnyPublisher<(String, String)?, Never> {
    Publishers.CombineLatest(validatedUsername, validatedPassword)
        .receive(on: RunLoop.main)
        .map { u, p in (u != nil && p != nil) ? (u!, p!) : nil }
        .eraseToAnyPublisher()
}
```

**BEST PRACTICE**: At every API boundary, call `.eraseToAnyPublisher()` to hide implementation details. Otherwise the type signature exposes every internal operator.

## Combine + Networking (712)

- `URLSession.shared.dataTaskPublisher(for: request)` returns a single-value Publisher of `(Data, URLResponse)`.
- Chain `.tryCatch { error -> AnyPublisher<...> in if error.networkUnavailableReason == .constrained { return lowDataPublisher } else { throw error } }` for Low Data Mode adaptive loading.
- `.retry(1)` operator for transient failures — but **PERFORMANCE WARNING**: only retry idempotent requests. Blindly retrying a payment is dangerous.

## Combine + SwiftUI: BindableObject (721, 226)

The bridge into SwiftUI:

```swift
final class Model: BindableObject {  // later renamed ObservableObject
    let didChange = PassthroughSubject<Void, Never>()
    var name = "" { didSet { didChange.send() } }
}
```

In a view: `@ObjectBinding var model: Model` (renamed `@ObservedObject` in 2020). SwiftUI subscribes to `didChange` and re-evaluates body whenever it fires.

**BEST PRACTICE**: Always use `.receive(on: RunLoop.main)` before assigning publisher values to UI properties. UI must be on the main thread.

## CombineLatest vs Zip (722)

| | When emits | Use case |
|---|---|---|
| **`Zip`** | When ALL upstreams have produced a NEW value (parallel pairing) | Wait for N parallel async tasks (e.g., wand-creation completion) — like `when/and` |
| **`CombineLatest`** | When ANY upstream produces a value (always uses last seen from each) | Live form validation across many fields — like `when/or` |

## Schedulers and Operators

- `receive(on:)` — switch downstream delivery to a queue/RunLoop.
- `subscribe(on:)` — control upstream subscription work location.
- `debounce(for:scheduler:)` — only emit after N seconds of silence.
- `throttle(for:scheduler:latest:)` — limit rate.
- `delay(for:scheduler:)` — defer.
- Native support for `RunLoop`, `DispatchQueue`, and timers.

## Migration Notes

- Combine works only on iOS 13+ / macOS 10.15+ / watchOS 6+ / tvOS 13+.
- API renames happened immediately: `BindableObject` → `ObservableObject` (2020), `didChange` → `objectWillChange` (and changed to fire BEFORE the change, not after).
- For pre-iOS-13 deployment, OpenCombine and CombineX exist as community ports.

## Cross-references

- SwiftUI Data Flow: 226 (BindableObject is the bridge).
- Networking adoption: 712 (DataTaskPublisher, tryCatch + Low Data Mode).
- Property wrappers underpinning @Published: 402 (What's New in Swift), 415 (Modern Swift API Design).
