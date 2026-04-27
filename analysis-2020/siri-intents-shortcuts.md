# WWDC 2020 — Siri, Intents, Shortcuts, Design for Intelligence

WWDC 2020's "Design for Intelligence" series — five sessions framing the philosophy — paired with the new compact Siri UI, Shortcuts on Apple Watch, in-app intent handling, and richer Shortcut automations.

## Sessions Analyzed
- 10068 — What's new in SiriKit and Shortcuts (gateway)
- 10086 — Design for intelligence: Apps, evolved
- 10087 — Design for intelligence: Make friends with "The System"
- 10088 — Design for intelligence: Discover new opportunities
- 10200 — Design for intelligence: Meet people where they are
- 10073 — Empower your intents
- 10074 — Decipher and deal with common Siri errors
- 10084 — Feature your actions in the Shortcuts app
- 10190 — Create quick interactions with Shortcuts on watchOS
- 10071 — Evaluate and optimize voice interaction for your app
- 10197 — Broaden your reach with Siri Event Suggestions
- 10060 — Design high quality Siri media interactions
- 10061 — Expand your SiriKit Media Intents to more platforms
- 10854 — Integrate SiriKit Media Intents with HomePod (Tech Talk)

## The "Intelligent System Experience" Framing

Apple's argument is that **intelligence is a design practice**, not a feature. Like the share button is a platform convention (consistent appearance signals consistent behavior), Siri Suggestions, Shortcuts, and proactive surfaces are conventions — but **alive**, adapting to each user's behavior.

The premise: as intelligent surfaces grow, users come to expect them. An app that doesn't participate feels dumber than its peers, even when its core functionality is fine.

Key technologies powering it:
- **Intents framework** (formerly SiriKit) — donated user actions
- **Universal Links** — content URLs the system can route
- **Handoff** — cross-device continuity
- **Spotlight Search** indexing
- **Shortcuts** — user-customizable workflows
- **Widgets** + **App Clips** (debuted same year) — surface app content outside the app

## Compact Siri UI in iOS 14 (10068)

Siri got a complete visual redesign — small bottom-anchored UI rather than full-screen takeover. Same design philosophy applies to Shortcuts running in foreground.

Implications for your Intents UI:
- **Less vertical space** — minimize disruption, defer to current context
- Use the new **transparent background material** for Intents UI views (system applies it; keep your view transparent to participate)
- Test against many backgrounds for readability
- For disambiguation lists: the new options-with-images-and-subtitles API helps users distinguish similar items (e.g., choosing among soup orders), but use judiciously — too much imagery overwhelms

## Shortcuts: Major Additions

### Folders for Organization

Long-requested. Users can now organize the dozens-to-hundreds of shortcuts they accumulate.

### Smart Folders
Built-in: "Watch", "Share Sheet" — automatically populated based on which shortcuts have what availability flags.

### Shortcuts on Apple Watch (10190)

Brand new in watchOS 7: a **Shortcuts app on the watch**. Run shortcuts directly from the watch face as **complications**, or from the watch's app launcher. Use the new Apple Watch toggle in Shortcut details.

The watchOS Shortcuts app supports a subset of intents — design and test your intents to work without iPhone if you want them to run on the watch. Network actions, on-device data fetches, simple back-end calls all work.

### New Personal Automation Triggers (10068)

In iOS 13 you got time, location, and app-open triggers. In iOS 14:
- **Receive an email** matching criteria
- **Receive a message** matching criteria
- **Close a certain app** (the inverse of open)
- **Battery hits a level**
- **Connect to a charger**

Many of these now run **without asking the user first** (silent automations), enabling routines like "every time I open my journaling app, log it to my habit tracker, enable Do Not Disturb, start my focus playlist."

### Wind Down Integration

Apps in supported categories (mindfulness, journaling, music, sleep) can be featured in the Wind Down setup screen. Mark your donated shortcut:

```swift
shortcut.shortcutAvailability = .sleepGoodForSleep
```

Significant App Store discoverability path.

### Automation Suggestions in the Gallery

The Shortcuts gallery now suggests catered automations based on the user's device usage patterns.

## In-App Intent Handling (Major)

iOS 14 lets your **main app process intents in-process** rather than only via the extension. This unlocks dynamic options that need access to the full app state (e.g., the user's currently-active filters) without duplicating logic in the extension. Adopt by handling the intent in your main app via the new `INIntentHandlerProviding` protocol.

## Empower Your Intents (10073)

For the Intents extension itself:
- Always **donate intents** when users perform an action your app exposes — this trains Siri Suggestions.
- Implement **intent disambiguation** for parameters that have multiple plausible interpretations.
- Use **dynamic options** for parameters whose value set changes based on context.
- Provide **rich snippets** (your Intents UI view) to confirm or disambiguate complex requests.

## Common Siri Errors (10074)

Practical session. Most-common pitfalls:
- **Failing to declare all parameter types** in your `.intentdefinition` file — Siri can't classify utterances correctly.
- **Generic vocabulary clashes** — your "Send" intent overlaps with Messages' "Send"; use distinct verbs in titles.
- **Missing localizations** — declare alternative phrasings per locale.
- **Slow intent resolution** — intents with long resolution callbacks feel broken; cache aggressively.

## Feature Your Actions in Shortcuts (10084)

Submit actions to be featured in the Shortcuts gallery — Apple's curated discovery surface. Requirements:
- Clear, concise action title and description
- Localized parameter prompts
- Functional in standalone context (no app dependency for the basic flow)
- Privacy-respecting

## Voice Interaction Quality (10071)

Practical guidance for building media/voice apps:
- **Test with real recorded utterances**, not synthesized speech
- Use **vocabulary** APIs to teach Siri about your app's specific terms (band names, app-specific jargon)
- Provide **alternative app names** Siri can recognize
- Time-box voice responses (Siri will cut you off after a few seconds)

## Siri Event Suggestions (10197)

Apps can donate event-like content (concert tickets, restaurant reservations, flights) so Siri can:
- Suggest reminders to leave on time
- Suggest related content (driving directions to the venue)
- Show on the lock screen at the right moment

Donate via `INRequestRideIntent`, `INSearchForReservationsIntent`, etc. with metadata (event time, location, cancellation policy).

## SiriKit Media Intents (10060, 10061)

Music/podcast/audio apps can integrate with Siri to:
- Play specific content ("Play [song] on [app]")
- Browse user library
- Resume playback
- Like/dislike content

Available across iPhone, iPad, Mac, **HomePod** (Tech Talk 10854), CarPlay. Implement `INPlayMediaIntent` and friends; provide rich responses with album art and metadata.

## Cross-References
- [widgets-and-widgetkit.md](widgets-and-widgetkit.md) — IntentConfiguration is how widgets are personalized via the same Intents framework.
- [watchos-7.md](watchos-7.md) — Shortcuts on watchOS, Wind Down integration.
- [media-hls-audio.md](media-hls-audio.md) — Media intents for audio streaming apps.

## Adoption Checklist
- [ ] If your app has dynamic data, implement in-app intent handling for richer parameter resolution.
- [ ] Donate user actions as intents — fuel for Siri Suggestions.
- [ ] Audit your `.intentdefinition` for all parameter types and clear localized titles.
- [ ] If you have a watch app, evaluate Shortcuts complication support.
- [ ] If your app touches sleep/wellness, mark relevant shortcuts with `.sleepGoodForSleep` for Wind Down.
- [ ] If a media app, support SiriKit Media Intents to extend reach to HomePod and CarPlay.
- [ ] For events/reservations, donate Siri Event Suggestions.
- [ ] Adopt the new compact Intents UI guidelines: minimal vertical space, transparent background, defer to context.
