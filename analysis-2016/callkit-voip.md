# CallKit & VoIP — WWDC 2016 Analysis

**Sessions covered:** 230 (Enhancing VoIP Apps with CallKit)

## Headline

CallKit elevates third-party VoIP apps to **first-party citizens**. Apps using CallKit appear in:
- The full-screen native incoming call UI (lock screen + unlocked banner)
- Recents
- Favorites
- Contacts (assignable as the default call method for a person)
- Siri ("Call Mom on Speakerbox")
- CarPlay
- Bluetooth headset controls
- Do-not-disturb / blocked list integration

Before CallKit, an incoming WhatsApp/Skype/etc. call was just a notification banner — users could miss it, couldn't slide-to-answer, couldn't see it on the lock screen. CallKit replaces that with the same UI as a regular phone call.

## Architecture: two classes (CXProvider + CXCallController)

- **`CXProvider`** — out-of-band events your app pushes to the system. "Incoming call arrived." "Outgoing call connected." "Remote party hung up."
- **`CXCallController`** — local user actions your app pushes through the system. "User tapped Call from inside our UI." "User tapped End from inside our UI." Wraps actions in `CXTransaction` for the system to mediate.

The asymmetry exists because user-initiated actions need system mediation: an outgoing call you start has to interplay with an existing FaceTime call (system holds it for you), an active phone call (system rejects yours), etc. The system tells your app what's allowed via callbacks.

## CallKit objects

| Class | Role |
|-------|------|
| `CXCallUpdate` | Metadata about an incoming call (handle, hasVideo, supportsHolding, etc.) — sent via provider |
| `CXAction` | Concrete things to do (`CXAnswerCallAction`, `CXEndCallAction`, `CXSetHeldCallAction`, `CXStartCallAction`, `CXSetMutedCallAction`, `CXSetGroupCallAction`, `CXPlayDTMFCallAction`) |
| `CXTransaction` | Bundle of one-or-more actions, sent through controller |
| `CXProviderConfiguration` | App-level config: localized name, ringtone, supports video, ringtone sound, masked icon, max calls per group |

## The incoming call flow (canonical)

1. Your app receives a PushKit voip push (PKPushRegistry / `didReceiveIncomingPushWith`).
2. **Synchronously, in that same callback, you MUST call `provider.reportNewIncomingCall(with: uuid, update: update, completion:)`.** No await. No background work first.
3. System shows the full-screen UI. Plays your ringtone.
4. User taps green button. Your `CXProviderDelegate` receives `provider(_:perform:)` with a `CXAnswerCallAction`. You configure your audio session (don't activate it!), call your app's "answer" code, then `action.fulfill()` (or `action.fail()` on error).
5. System activates your audio session at boosted priority. You get `provider(_:didActivate audioSession:)`. NOW start media processing.

## URGENT: Synchronous reporting or your app gets killed

The **single most important rule**: `reportNewIncomingCall(with:update:completion:)` must be invoked **synchronously inside `didReceiveIncomingPushWith`**. If you fail to do so (e.g. you await a network round-trip first), the system penalizes you progressively — eventually it stops launching your app for VoIP pushes entirely. The user's perception is "Skype calls just stopped working" with no error to debug.

This is barely mentioned in PushKit docs. The CallKit session emphasizes it.

## URGENT: Audio session — do NOT activate it yourself

With CallKit, your app **only configures** the audio session category, mode, and options. The system activates it at a boosted priority on par with phone/FaceTime. After activation you're notified via `provider(_:didActivate:)`.

If you call `setActive(true)` yourself, you get a non-boosted session that other apps can interrupt.

## Outgoing call flow

1. App launched (from Siri, contact card, recents, your own UI) with a `INStartAudioCallIntent` or `INStartVideoCallIntent` wrapped in `NSUserActivity`.
2. Build a `CXStartCallAction` from the intent's handle/contactIdentifier.
3. Wrap in `CXTransaction`, send via `controller.request(_:completion:)`.
4. System mediates (puts existing calls on hold if needed) and calls back into your `CXProviderDelegate` via `provider(_:perform: CXStartCallAction)`. You then talk to your network, configure audio session, and `action.fulfill()`.
5. Use `provider.reportOutgoingCall(with: uuid, startedConnectingAt: Date())` and `provider.reportOutgoingCall(with: uuid, connectedAt: Date())` to update system UI as the call progresses.

## Multiple-call transactions

When the user has an active call and accepts an incoming waiting call from the native UI, the system may bundle (`endActive + answerNew`) into a single `CXTransaction` containing two actions. **You must `fulfill` each action individually.** Don't bulk-fulfill.

## Provider configuration tips

- `localizedName` — appears as the call source ("Speakerbox audio").
- `ringtoneSound` — your custom sound. Set per-call via `CXCallUpdate.ringtoneSound` if dynamic.
- `iconTemplateImageData` — masked black-and-white image (template style) appearing as the in-call button that returns to your app. Future-seeded — not in seed 1.
- `supportsVideo` — show/hide video buttons.
- `maximumCallGroups` / `maximumCallsPerCallGroup` — limit conferencing.

## Restrictions and errors

`reportNewIncomingCall` may fail (passes error in completion):
- App not authorized (user disabled in Settings)
- Caller in user's blocked list
- Do-Not-Disturb is on (silent reject)
- App has been throttled for synchronous-reporting violations

Match on `CXErrorCodeIncomingCallError` cases — handle each gracefully. The system will not display UI for these failures; your app should silently dismiss the underlying push.

Action timeouts: each action has a deadline. If you don't fulfill in time, you get `provider(_:timedOutPerforming:)`. Treat it as a failure to maintain UI consistency.

## SiriKit integration (free benefit)

If you adopt CallKit + the `INStartAudioCallIntent` / `INStartVideoCallIntent` SiriKit intents, "Call my brother on Speakerbox" works automatically, and your app appears under the Call button on contact cards. Donate `INInteraction` after every call to populate the Contacts UI personalization.

## Best practices summary

- Prepare a CallKit setup at app launch (`CXProvider` + `CXProviderConfiguration` + delegate). Cheap.
- Maintain authorization status — observe changes in `provider(_:didDeactivate:)` cycle and refresh UI accordingly.
- Always stop processing audio in `provider(_:perform: CXEndCallAction)` and `provider(_:didDeactivate:)`.
- Build a tiny test app first — Speakerbox sample is at developer.apple.com.

## Hidden gems

- The **green double-height status bar** (previously reserved for native phone/FaceTime calls) now appears for CallKit apps when the user backgrounds during an active call. Tapping returns to your app.
- Apple Pay can be used inside the in-call UI of a CallKit app — tap to pay for a service from inside the call screen.
- The system masked-icon API gives a button right next to the End Call button to jump back into your app — better than relying on the green status bar.
- All CallKit work is supported in iOS Simulator (no PushKit), so you can build the Speakerbox demo on a Mac.

## Cross-references

- SiriKit VoIP intents → analysis-2016/sirikit-debut.md
- Notifications integration → analysis-2016/ios10-notifications.md
- Audio session priorities → analysis-2016/audio-media.md
