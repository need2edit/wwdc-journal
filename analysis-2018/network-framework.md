# Network.framework — WWDC 2018 Analysis

**Sessions covered:** 715 (Introducing Network.framework), 713 (Optimizing Your App for Today's Internet — note: 714 in the metadata), 714 (Optimizing Your App for Today's Internet)

## Headline

WWDC 2018 introduced **Network.framework** — Apple's modern alternative to BSD sockets. It's the same library URLSession has been built on for years, now exposed directly to your apps. It does smart connection establishment (PAC, proxies, dual-stack racing, Wi-Fi Assist fallback), built-in TLS/DTLS, asynchronous read/write with built-in back-pressure, mobility-aware migration between networks, and runs on user-space networking on iOS/tvOS for ~30% less CPU on packet-heavy workloads. Apple wants you to **stop using sockets** and stop using `SCNetworkReachability`.

## Why Sockets Don't Cut It Anymore (715)

Three areas where sockets fail today's mobile internet:

1. **Connection establishment** — DNS resolution, IPv4/IPv6 dual-stack racing, PAC scripts, SOCKS / HTTP CONNECT proxies, captive portals. You re-implement all of this badly.
2. **Data transfer** — read/write semantics force you to build a state machine for partial reads, you have to manually integrate a TLS library, you can't easily back-pressure.
3. **Mobility** — sockets predate mobile. They have no concept of "this Wi-Fi just died, fall back to cellular" or "this connection moved networks but should resume."

Network.framework solves all three.

## NWConnection: The Core Object (715)

```swift
import Network
let connection = NWConnection(
  host: "mail.example.com",
  port: .imaps,
  using: .tls           // also .udp, .quic, .tcp, .dtls, custom protocols
)
connection.stateUpdateHandler = { state in /* ready, waiting, failed, cancelled */ }
connection.start(queue: queue)
```

That's it for a TLS-over-TCP connection. Compare to sockets: getaddrinfo, choose address, socket, set options, fcntl nonblocking, connect, then a TLS library on top.

## Connection States (715)

`setup → preparing → ready → cancelled` is the happy path. Two key alternates:

- **`waiting(reason)`** — no network available. The connection is queued. When the network changes, `preparing` automatically retries. **HIDDEN GEM**: this is the same waits-for-connectivity behavior URLSession got in 2017, and it's _on by default_. You get auto-retry across network changes for free. Use the waiting state to update UI ("offline — will send when connected") rather than failing.
- **`failed(error)`** — TLS handshake failure, server reset, protocol error. Surface to the user.

## Smart Connection Establishment (715)

When you call `start()`, Network.framework:
1. Evaluates available interfaces (Wi-Fi, cellular, ethernet, VPN), preferring less expensive paths.
2. Checks for a configured proxy (PAC scripts run automatically — your app doesn't need a JavaScript runtime).
3. Resolves DNS in parallel and races multiple addresses (Happy Eyeballs RFC 8305).
4. Falls back to cellular via Wi-Fi Assist if Wi-Fi quality degrades during connection.

To restrict: `NWParameters.prohibitedInterfaceTypes = [.cellular]`, `prohibitExpensivePaths = true`, or via `NWParameters.IP.version = .v6`, `NWParameters.allowFastOpen = true`, etc.

## Asynchronous Send and Receive (715)

```swift
connection.send(content: data, completion: .contentProcessed { error in
  if error == nil { fetchMoreFrom(stream) }   // backpressure-driven loop
})

connection.receive(minimumIncompleteLength: 10, maximumLength: 10) { data, _, _, error in
  // exactly 10 bytes (or error). No state machine needed.
}
```

Key features:
- `.contentProcessed` fires when the network stack consumes data — your hook to enqueue more. Forms a natural back-pressure loop without buffering everything in memory.
- `receive(minimumIncompleteLength:maximumLength:)` waits until exactly N bytes are available. No more "I asked for 100, got 17, manage state, ask again." Specify equal min/max to read fixed-size headers.

## Batching for UDP (715)

```swift
connection.batch {
  for packet in packets { connection.send(content: packet, completion: .idempotent) }
}
```

A traditional UDP socket sends one datagram per syscall. `connection.batch { ... }` coalesces all sends into a single descent into the kernel — the difference between 100 context switches and 1.

## NWListener for Incoming (715)

```swift
let listener = try NWListener(using: .udp)
listener.service = NWListener.Service(name: nil, type: "_camera._udp")
listener.newConnectionHandler = { connection in
  connection.start(queue: queue)
}
listener.start(queue: queue)
```

- Bonjour service registration is built in — no separate `NetService` plumbing.
- `listen()` _doesn't even work_ on UDP sockets, but `NWListener` does.
- The `service` is registered automatically; `serviceRegistrationUpdateHandler` tells you the actual advertised name (system can append a number if there's a conflict).

## User-Space Networking: 30% Less CPU (715)

- iOS 12 / tvOS 12 introduced **user-space networking** for Network.framework and URLSession (not for raw sockets).
- The TCP/UDP stack lives in your app's address space, sharing memory-mapped buffers directly with the driver. No copy from kernel buffer to user buffer, no context switch per packet.
- Live demo: identical UDP video stream, sockets vs Network.framework, on the same hardware. The Network.framework receiver kept up with the sender; the sockets receiver fell behind. ~30% less CPU on the receiver side.
- **PERFORMANCE**: if you're sending or receiving lots of UDP packets (gaming, live streaming, real-time data), this is the single biggest win available to you. Run instruments before/after to confirm.

## Mobility: Three Connection Events (715)

After your connection is `ready`, three handlers tell you about network changes:

1. `viabilityUpdateHandler` — fires `false` when connectivity is lost (no route), `true` when restored. Don't tear the connection down — the same network may come back (e.g., user walks out of an elevator). Update UI to indicate offline.
2. `betterPathUpdateHandler` — fires when a better path becomes available (e.g., started on cellular, walked into Wi-Fi range). Recommendation: start a parallel new connection on the better path; only close the old one once the new is `ready`. Saves user data charges.
3. `pathUpdateHandler` (less common) — generic network change notifications.

## Multipath TCP for Seamless Migration (715)

```swift
let parameters = NWParameters.tcp
parameters.multipathServiceType = .handover
```

- Same as URLSession's `multipathServiceType`. The connection migrates seamlessly between networks if your server supports MPTCP. iOS doesn't expose MPTCP for arbitrary servers — Siri uses it.
- Apple's own services (iCloud, Maps, Siri) use MPTCP; this lets you opt your own endpoints in if you control the server.

## Stop Using Reachability (715)

- **URGENT**: `SCNetworkReachability` introduces race conditions ("network is up... oh wait, it just went down between your check and your call"). The `waiting` state in NWConnection is the modern replacement.
- For genuine UI questions ("can I send anything at all right now?"), use the new `NWPathMonitor` instead. It tells you the current state of interfaces, fires on changes, and lets you iterate available interfaces.

## DEPRECATIONS in 715

- **CFStreamCreatePairWithSocket** family, **CFSocket**, **NSStream**, **NSNetService**, **NSSocketPort** — all should move to Network.framework or URLSession.
- For URLSession specifically: **FTP and file URLs in PAC scripts** are no longer supported. PAC scripts can only reason about HTTP/HTTPS URLs going forward.
- macOS Network Kernel Extensions are not compatible with user-space networking. If you have one, contact Apple — there should be a higher-level alternative.

## Cross-references

- URLSession new features: 714 (Optimizing Your App for Today's Internet) — Low Data Mode is 2019 but most of its prerequisites land here.
- Background networking: see 707 (Advances in Background Tasks — though more substantively in 2019's session 707).
- TLS pinning, custom protocols, and DTLS specifics: 715 hands-on lab session covered in detail.
