# Speech Recognition Framework — WWDC 2016 Analysis

**Sessions covered:** 509 (Speech Recognition API)

## Headline

iOS 10 introduces the **`Speech` framework** — the same recognizer that powers Siri and keyboard dictation, exposed to third-party apps for the first time. Supports 50+ languages. Recognizes pre-recorded audio files OR live microphone audio. Returns alternate interpretations, per-word confidence levels, and timing — far richer than the keyboard-dictation button apps used to wedge into UI.

## What it replaces

Apps previously had two options:
1. **The keyboard dictation button** (since iOS 5). Trivial to use but no UI control, no language control, only works for `UITextInput`-conforming text fields.
2. **Roll your own.** Push audio to a third-party service, store/transmit user audio outside Apple's privacy boundary.

Speech replaces both with a first-party API.

## API surface

```swift
import Speech

// 1. Authorization
SFSpeechRecognizer.requestAuthorization { status in
    DispatchQueue.main.async { /* enable/disable UI */ }
}

// 2. Recognizer (one per language; default = device locale)
let recognizer = SFSpeechRecognizer(locale: Locale(identifier: "en-US"))!
guard recognizer.isAvailable else { return }  // check before each request

// 3a. File-based
let request = SFSpeechURLRecognitionRequest(url: fileURL)
recognizer.recognitionTask(with: request) { result, error in
    guard let result = result else { print(error!); return }
    print(result.bestTranscription.formattedString)
    if result.isFinal { /* done */ }
}

// 3b. Live audio (microphone)
let request = SFSpeechAudioBufferRecognitionRequest()
let task = recognizer.recognitionTask(with: request) { result, error in
    if let result = result, result.isFinal { … }
}

let inputNode = audioEngine.inputNode
inputNode.installTap(onBus: 0, bufferSize: 1024, format: nil) { buffer, _ in
    request.append(buffer)
}
try audioEngine.start()

// when done:
request.endAudio()      // signal: no more input
task.cancel()           // if user cancels
```

## Required Info.plist key (URGENT — app crashes without it)

`NSSpeechRecognitionUsageDescription` — explains why your app uses speech recognition. Without this key, the request-authorization call **terminates your app** with a clear console message. Same hard-fail policy as Camera, Microphone, Photos.

## Authorization status — four cases

```swift
switch SFSpeechRecognizer.authorizationStatus() {
case .notDetermined: // ask
case .authorized:    // proceed
case .denied:        // user said no — gracefully degrade or send to Settings
case .restricted:    // parental control or supervised — don't push the user
}
```

## Privacy posture

Speech recognition runs on **Apple servers** by default. The user's audio crosses the network. This is exactly why authorization is required. Best practices Apple emphasizes:

- **Show a recording indicator** (red mic icon, recording dot) while audio is being captured.
- **Don't recognize sensitive speech** — passwords, credit-card details, health data, confidential conversations. Display a warning to the user if your app is in a context where they might say something private.
- **Stream the partial transcripts back to UI** so the user can see what's being captured, à la Siri.
- **Cancel recognition aggressively** — when the user navigates away, when audio recording is interrupted, when the user explicitly stops. Never leave a recognition task running with audio you no longer need.

## On-device recognition (iPhone 6s and later)

Some newer A9+ devices support **on-device** recognition for some languages. Check `recognizer.supportsOnDeviceRecognition` (this property is iOS 13+; in iOS 10 you can only check `recognizer.isAvailable` for live online status). When unavailable due to no internet, the recognizer reports unavailable.

In the iOS 10 release, on-device support is limited; most recognition goes server-side. Treat `isAvailable == false` as the equivalent of "no internet, fall back to typing."

## Throttling and limits (BEST PRACTICE)

Apple imposes:
- **Per-device limits per day** (number of recognitions).
- **Per-app daily quota globally** across all your installs.
- **Per-recognition duration cap of about 1 minute** (similar to keyboard dictation).

If you hit either limit, the API returns an error. Handle these like network errors — back off, surface a "recognition unavailable" UI, retry later. Don't busy-loop.

## SFSpeechRecognitionResult — the rich result

`bestTranscription` is `SFTranscription`. From it:
- `formattedString` — the text.
- `segments: [SFTranscriptionSegment]` — each segment has `substring`, `substringRange`, `timestamp`, `duration`, `confidence` (0–1), and `alternativeSubstrings` (other interpretations the recognizer considered).

`transcriptions: [SFTranscription]` gives you alternate full transcriptions ranked by confidence. Use these to show "Did you mean…?" suggestions.

The `isFinal` flag distinguishes streaming partials from the final commit. Final results are stable; partial results may change as more context arrives.

## Use cases that win

- **Voice-driven search** — restaurants, music, contacts.
- **Voice-controlled photo capture** — say "cheese" to take a photo (Apple's headline example: the Phromage cheese-detection app).
- **Hands-free messaging while driving** (CarPlay).
- **Accessibility** — replace typing for users with motor disabilities.
- **Transcription apps** — meeting notes, voice memos.

Avoid:
- **Long-form audio** — chunk it; the per-recognition duration cap will cut you off.
- **Noisy environments without a noise-suppressed audio chain** — recognition quality degrades.

## Hidden gems

- **`SFSpeechRecognizer.supportedLocales()`** returns the full set of supported languages — over 50. Use it to populate language pickers dynamically rather than hard-coding.
- **`SFSpeechRecognitionTask.state`** lets you observe whether a task is running, paused, or completed without retaining the closure-only flow.
- **The `.task` form returning a task lets you cancel from anywhere** — store it on your view controller.
- **Audio buffers can be appended both before AND after starting recognition** — perfect for prefilling a buffered recording captured before authorization completes.

## Cross-references

- SiriKit also handles audio→intent conversion at a higher level — see analysis-2016/sirikit-debut.md
- AVAudioSession + AVAudioEngine for capture — session 507 (Delivering an Exceptional Audio Experience)
- Privacy-by-design pattern → analysis-2016/privacy-differential.md
