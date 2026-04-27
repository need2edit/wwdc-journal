# System Services, Networking & Privacy (WWDC 2021)

HTTP/3 + QUIC, iCloud Private Relay, App Attest, and the foundations of the modern privacy story.

## Sessions covered
- WWDC21-10094 — Accelerate networking with HTTP/3 and QUIC
- WWDC21-10103 — Optimize for 5G networks
- WWDC21-10239 — Reduce network delays for your app
- WWDC21-10096 — Get ready for iCloud Private Relay
- WWDC21-10085 — Apple's privacy pillars in focus
- WWDC21-10102 — Meet the Location Button
- WWDC21-10105 — Secure login with iCloud Keychain verification codes
- WWDC21-10106 — Move beyond passwords (Passkeys preview)
- WWDC21-10110 — Safeguard your accounts, promotions, and content
- WWDC21-10244 — Mitigate fraud with App Attest and DeviceCheck
- WWDC21-10298 — Add support for Matter in your smart home app
- WWDC21-10117 — Meet CloudKit Console
- WWDC21-10298 — Matter framework
- WWDC21-10165 — Explore Nearby Interaction with third-party accessories

## Best practices

- **Don't check network type to drive behavior.** The system already picks the best network (Smart Data Mode, Auto-Switch-to-5G). Check `URLSessionTask.delegate` `allowsExpensiveNetworkAccess`, `allowsConstrainedNetworkAccess` instead (WWDC21-10103).
- **Use modern HTTP APIs** (`URLSession`, `Network.framework`) — HTTP/3 is on by default in iOS 15 once your server advertises it. No code change for opt-in clients (WWDC21-10094).
- **Advertise HTTP/3 from your server** via the HTTPS DNS resource record (`alpn=h3`). Falls back to `Alt-Svc` HTTP header if DNS isn't configured. DNS is preferred — first-connection HTTP/3 instead of after-discovery HTTP/3 (WWDC21-10094).
- **Set `prefersIncrementalDelivery=true`** on URLSessionTasks streaming JSON-Lines or chunked content — avoid waiting for the full body when you can process incrementally (WWDC21-10094).

## Hidden gems

- **Location Button** (`CLLocationButton`, SwiftUI `LocationButton`) — Apple-vended button that grants one-shot location access without a Settings prompt or even a system dialog. Lower-friction equivalent of the OAuth "Sign in with Apple" button for Maps (WWDC21-10102).
- **iCloud Private Relay** rewrites Safari and unencrypted-app traffic via two-hop proxies. Your server-side IP geolocation will see relay IPs in known IP ranges; explicit signed JSON list at mask-api.icloud.com publishes them (WWDC21-10096).
- **App Attest** (already shipped iOS 14, expanded 2021): server-attested device-key proofs. Use to gate API endpoints against scrapers/cheaters. Free to use but rate-limited (WWDC21-10244).
- **DeviceCheck**'s 2-bit per-device storage is per-developer-account, not per-app — track abusers across multiple apps you publish (WWDC21-10244).
- **Passkeys** previewed under "Move beyond passwords" — the WebAuthn-based replacement for passwords, syncing via iCloud Keychain. Full ship comes in 2022 (WWDC21-10106).
- **HTTP/3 / QUIC** is now in `Network.framework` directly: `NWParameters.quic(alpn: ["h3"])` for DIY non-HTTP QUIC protocols. Multiplexed streams via `NWMultiplexGroup`/`NWConnectionGroup` (WWDC21-10094).
- L4S (Low-Latency, Low-Loss) — set `URLSessionConfiguration.requiresDNSSECValidation`-adjacent options for L4S support. (Note: L4S formalized 2023, foundations laid here.)
- **Matter** support: HomeKit's accessory protocol now interoperates with the Matter standard. Apps that use HomeKit get Matter for free (WWDC21-10298).
- **Nearby Interaction** + third-party UWB accessories: `NINearbyAccessoryConfiguration` makes any U1-equipped accessory rangeable. Used for AirTag-like products (WWDC21-10165).

## Performance

- HTTP/3 vs HTTP/2: connection setup drops from 2 round-trips (TCP+TLS) to 1 (QUIC+TLS combined). Per-stream packet loss doesn't head-of-line block other streams. Connection migration across Wi-Fi → cellular happens without a new handshake (WWDC21-10094).
- 5G ideal max ~4 Gbps theoretical; Apple's testing got 3 Gbps real-world in Apple Park. Latency drops to ~7ms ping (WWDC21-10103).

## Migration guidance

- Audit hardcoded port 80 / `http://` URLs for Private Relay compatibility. Plain HTTP traffic from non-Safari apps is rewritten by the relay; if you depend on IP-based logging, results will be wrong post-relay (WWDC21-10096).
- For the new Location Button, you can show it in your UI INSTEAD of "Allow Once" Settings — users tap the button and get one-time location without leaving your screen (WWDC21-10102).

## Cross-references

- iCloud Keychain verification codes (WWDC21-10105) — TOTP support without a third-party authenticator. Apple builds the secret-sharing handshake into Settings.
- L4S details and HTTP/3 ECN are also covered in 2023's "Reduce network delays with L4S" (WWDC23-10004).
