# Networking: Low Data Mode, WebSocket & Combine — WWDC 2019 Analysis

**Sessions covered:** 712 (Advances in Networking, Part 1), 713 (Advances in Networking, Part 2), 707 (Advances in App Background Execution), 714 (Network Extensions for the Modern Mac), 715 (Core NFC Enhancements), 716 (Streaming Audio on watchOS 6)

## Headline

iOS 13 introduces **Low Data Mode** as a per-network user preference. Apps can opt into respecting it. Native **WebSocket** support arrives in URLSession and Network framework. URLSession adds a Combine `DataTaskPublisher`. Background execution gets a brand-new **BackgroundTasks framework** for deferrable maintenance.

## Low Data Mode (712)

- User toggles Low Data Mode per Wi-Fi SSID and per cellular SIM in Settings.
- System effects: defers all `.background.discretionary` URL session work; disables Background App Refresh.
- App effects: you opt into respecting it via API.

### URLSession adoption

```swift
var request = URLRequest(url: url)
request.allowsConstrainedNetworkAccess = false
URLSession.shared.dataTask(with: request) { data, response, error in
    if let error = error as? URLError, error.networkUnavailableReason == .constrained {
        // Fetch lower-quality fallback resource
    }
}.resume()
```

### Network framework adoption

```swift
let params = NWParameters.tls
params.prohibitConstrainedPaths = true   // never use Low Data networks
let conn = NWConnection(to: endpoint, using: params)

// OR allow but check
conn.pathUpdateHandler = { path in
    if path.isConstrained { /* use less data */ }
}
```

### Best practices

- **Reduce image quality** — fall back to a smaller variant.
- **Reduce prefetching** — don't speculatively fetch.
- **Synchronize less frequently**.
- **Disable autoplay video**.
- **Mark background tasks as discretionary**.
- **Don't block user-initiated work** — they asked for it; fulfill it.
- **`expensive` is system-set** (cellular / personal hotspot); `constrained` is user-set. Use both.

**HIDDEN GEM**: even if you do nothing, your app will be deferred from background activity on Low Data networks for free. The big wins come from app-level adoption.

## Combine in URLSession (712)

```swift
URLSession.shared.dataTaskPublisher(for: request)
    .tryMap { data, response in
        guard (response as? HTTPURLResponse)?.statusCode == 200 else {
            throw URLError(.badServerResponse)
        }
        return data
    }
    .decode(type: MyModel.self, decoder: JSONDecoder())
    .receive(on: DispatchQueue.main)
    .sink(receiveCompletion: { ... }, receiveValue: { ... })
```

### Adaptive Loading Pattern (712)

```swift
func adaptiveLoad(regular: URL, lowData: URL) -> AnyPublisher<Data, Error> {
    var request = URLRequest(url: regular)
    request.allowsConstrainedNetworkAccess = false
    return URLSession.shared.dataTaskPublisher(for: request)
        .tryCatch { error -> URLSession.DataTaskPublisher in
            guard (error as URLError).networkUnavailableReason == .constrained
                else { throw error }
            return URLSession.shared.dataTaskPublisher(for: lowData)
        }
        .tryMap { data, response in /* validate */ data }
        .eraseToAnyPublisher()
}
```

**BEST PRACTICE**: cancel subscriptions in `prepareForReuse()` on table cells via `AnyCancellable`. Eliminates the classic "wrong image in reused cell" bug.

## Native WebSocket Support (712)

The most-requested networking feature of 2018.

### URLSession API

```swift
let task = session.webSocketTask(with: url)
task.resume()
task.send(.string("hello"), completionHandler: { _ in })
task.receive { result in /* handle */ }
```

### Network framework API

```swift
let parameters = NWParameters.tls
let wsOptions = NWProtocolWebSocket.Options()
wsOptions.autoReplyPing = true
parameters.defaultProtocolStack.applicationProtocols.insert(wsOptions, at: 0)

let conn = NWConnection(to: .url(URL(string: "wss://...")!), using: parameters)
```

- Built-in ping/pong handling.
- Server-supplied compression (`permessage-deflate`) handled automatically.
- Connection-level back-pressure.

## Mobility Improvements (712)

- Multipath TCP for cellular fallback when Wi-Fi degrades.
- Improved roaming: connections survive Wi-Fi → cellular transitions when possible.
- New `pathUpdateHandler` callbacks tell you when constrained / expensive / interface type changes mid-connection.

## Background Tasks Framework (707)

A brand-new framework specifically for deferrable maintenance work — separate from older background modes.

### BGAppRefreshTask
- Periodic short refreshes (~30s budget). Replaces the old Background Fetch API.
- Schedule: `BGTaskScheduler.shared.submit(BGAppRefreshTaskRequest(identifier:))`.

### BGProcessingTask
- Longer maintenance work — DB cleanup, ML training, large file processing.
- Runs only when device is on charger and idle (configurable: `requiresExternalPower`, `requiresNetworkConnectivity`).
- No fixed time limit, but system can interrupt.

### Setup

1. Add to `Info.plist`: `BGTaskSchedulerPermittedIdentifiers` array of your task IDs.
2. Add `Background Modes` capability with `Background processing` and `Background fetch` checked.
3. Register handlers in `application(_:didFinishLaunchingWithOptions:)` BEFORE `applicationDidFinishLaunching` returns: `BGTaskScheduler.shared.register(forTaskWithIdentifier:using:launchHandler:)`.
4. Schedule the next run from within your task's launch handler.
5. Always set `task.expirationHandler` to clean up if the system needs you to stop.

**URGENT** — these are NOT a replacement for VoIP, location, audio, or HealthKit background modes. They're a deferred task scheduler.

**HIDDEN GEM**: from the simulator, trigger a background task immediately with a private LLDB command:
```
e -l objc -- (void)[[BGTaskScheduler sharedScheduler] _simulateLaunchForTaskWithIdentifier:@"com.your.id"]
```

## Other Background Modes (707)

- **Background URL session (discretionary)** — system schedules at optimal time, can wake your app on completion.
- **VoIP push** — must use CallKit's `reportNewIncomingCall` synchronously, or the system kills your app and may stop launching it for VoIP pushes.
- **Background pushes** — `apns-priority: 5`, `apns-push-type: background`, `content-available: 1`, no alert/sound/badge. iOS may not deliver if power/network unfavorable.

## Streaming Audio on watchOS 6 (716)

- AVPlayer/AVQueuePlayer comes to watchOS for HLS streaming.
- New `URLSessionConfiguration.networkServiceType = .avStreaming` for audio streams.
- WebSocket and StreamingTask available on watchOS.
- **BEST PRACTICE**: start at 64 kbps, monitor throughput, upgrade only when conditions allow. Plan for Bluetooth → Wi-Fi → cellular transitions taking several seconds.
- watchOS no longer requires the iPhone tether for audio playback (Series 3+).

## Cross-references

- Combine in URLSession: 712 + 721/722.
- Background tasks vs old Background Fetch: 707.
- Sign In with Apple over network: 706.
