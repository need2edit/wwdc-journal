# Grouped & Interactive Notifications — WWDC 2018 Analysis

**Sessions covered:** 710 (What's New in User Notifications), 711 (Using Grouped Notifications), 806 (Designing Notifications), 202 (What's New in Cocoa Touch §Notifications)

## Headline

iOS 12 added two systemic notification features (**grouping** and **provisional authorization**), one major content extension overhaul (**user-interactive notifications** with dynamic actions), one regulated power feature (**critical alerts** that bypass DND/silent), and Apple's first attempt at notification triage UI. The grouping work is built on top of the existing `threadIdentifier` from iOS 11, and the API surface is delightfully small.

## Grouped Notifications: One Property to Rule Them All (710, 711)

- All app notifications are grouped by default in iOS 12, regardless of code changes.
- To create _multiple_ groups within your app, set `UNMutableNotificationContent.threadIdentifier` to any unique string. Notifications with the same thread ID get grouped together.
- Three user controls (Settings → Notifications → [App] → Notification Grouping):
  - **Automatic** (default) — respects your `threadIdentifier`.
  - **By App** — ignores your thread ID, one group per app.
  - **Off** — iOS 11 behavior, every notification on its own.

**HIDDEN GEM**: `threadIdentifier` is the same property used for routing rich content extensions and for "private" notifications since iOS 11. If you set it for those features, you're already grouping correctly.

## Three App Patterns to Learn From (711)

| App | Pattern | Lesson |
|---|---|---|
| Calendar | Default app group for routine updates; separate thread for "starts in 15 min" alerts | Separate _important actionable_ from _informational updates_ |
| Messages | One thread per conversation | Create groups for **meaningful personal communications** that resolve quickly |
| Mail | One group per account; VIP senders get their own group; user-flagged threads get their own group | **Respect the user's existing organization** — accounts, VIPs, flagged threads — instead of trying to invent a new hierarchy |

**BEST PRACTICE**: think about how _the user_ already organizes related notifications, not how _your data model_ organizes them. A 200-message Slack-style channel is one group; a one-on-one DM is a separate group.

## Custom Summary Text (711)

- Default summary: "9 more messages" (system-generated count).
- Custom: set on the notification _category_ (not the notification), so all notifications in that category share one template.
```swift
let category = UNNotificationCategory(
  identifier: "messages",
  actions: [...],
  intentIdentifiers: [],
  hiddenPreviewsBodyPlaceholder: "%u messages",
  categorySummaryFormat: "%u more messages from %@"   // %u count, %@ string
)
```
- Two supported format types: `%u` only (numeric count) or `%u` + `%@` (count + arguments string).
- The `%@` argument comes from `UNMutableNotificationContent.summaryArgument` (a per-notification string). The system de-duplicates so "Alice, Alice, Bob" → "Alice and Bob."
- `summaryArgumentCount` lets you say one notification represents N items (Podcasts: one notification = "3 new episodes" so it counts for 3 in the summary).

## Localizing Summaries with Plurals (711)

- Format strings should use `NSString.localizedUserNotificationString(forKey:arguments:)` to defer translation until actual delivery (in case the user changes language between scheduling and delivery).
- Use a `.stringsdict` plurals file. Apple ships examples covering English, Hebrew (3 cases), and Russian (3 cases). Foundation handles all the rules — you don't need to know which language has which plural form.

## Dynamic Notification Actions (710)

- `UNNotificationAction` is no longer fixed at category-registration time.
- Inside a notification content extension you can read and write `extensionContext.notificationActions`:
```swift
override func didReceive(_ response: UNNotificationResponse, completionHandler: @escaping ...) {
  // toggle "Like" → "Unlike" after a tap
  let unlike = UNNotificationAction(identifier: "unlike", title: "Unlike", options: [])
  let comment = extensionContext?.notificationActions.first { $0.identifier == "comment" }!
  extensionContext?.notificationActions = [unlike, comment]
  completionHandler(.doNotDismiss)
}
```
- Lets you build flows like "Tap Like → button replaced with Unlike," "Tap Rate → secondary list of star ratings appears."

## Interactive Content (710)

- New plist key: `UNNotificationExtensionUserInteractionEnabled = true` opts your content extension into receiving touches.
- Pre-iOS-12 content extensions could not have buttons, sliders, or other interactive UI inside the extension view. Now they can — like-buttons, parking-meter timer extension, restaurant reservation update with party size — without bouncing to the app.
- Two new APIs to round it out:
  - `extensionContext.performNotificationDefaultAction()` — programmatically launch your app from a custom button (calls `UserNotificationCenter:didReceive:withResponse:` with `UNNotificationDefaultActionIdentifier`).
  - `extensionContext.dismissNotificationContentExtension()` — programmatically dismiss the extension view from your custom button (does _not_ withdraw the notification — use the regular remove API for that).

## Notification Management View (710)

- Swipe a notification → tap "Manage" → contextual settings sheet appears with:
  - Deliver Quietly / Deliver Prominently
  - Turn Off
  - **Configure in [App]** — deep link to your app's notification settings
  - Quick link to system Settings for the app
- The "Configure in App" link calls a new delegate method:
```swift
func userNotificationCenter(_ center: UNUserNotificationCenter, openSettingsFor notification: UNNotification?)
```
- The same delegate method fires when the user taps "[App] Notification Settings" at the bottom of Settings → Notifications → [App].
- **BEST PRACTICE**: implement this delegate even if you don't have granular settings. Use it as a chance to navigate to a per-category preference UI ("Notify me about new episodes / new replies / new likes").

## Provisional Authorization: Trial Period for Notifications (710)

- New `UNAuthorizationOptions.provisional` option.
- Bypasses the system permission prompt entirely. Notifications start arriving — but always **delivered quietly** (notification center only, no banner, no sound).
- Each notification has a "Keep / Turn Off" prompt at the top so the user decides _after experiencing_ a few notifications whether to keep them.
- **HIDDEN GEM**: send `[.alert, .sound, .badge, .provisional]`. The non-provisional options describe how notifications will be delivered _if_ the user keeps them. Provisional is purely a delivery-mode override during the trial.
- Strongly recommended for apps that send too many low-importance pushes — this lets you demonstrate the value before requesting permission.

## Critical Alerts: Bypass DND and Mute (710)

- New `UNAuthorizationOptions.criticalAlert` option. **Requires entitlement** from Apple via the developer portal.
- Critical alerts bypass Do Not Disturb _and_ the ringer mute switch. They play a sound regardless.
- Intended for: medical / health (continuous glucose monitor warnings), home / security (smoke alarm, intrusion), public safety, emergency response.
- Set up:
  - Apply for the critical-alert entitlement on developer.apple.com.
  - Request `[.criticalAlert]` from the user.
  - Build the notification content with `content.sound = UNNotificationSound.defaultCritical` (or `.criticalSoundNamed(_:withAudioVolume:)` for a custom sound).
- The system shows a special icon and dedicated section in Settings ("Critical Alerts") that the user can disable independently of regular notifications.
- **URGENT**: do not use this for marketing, social, or "engagement" notifications. App Review will reject. The entitlement is gated specifically because misuse degrades the privilege for legitimate apps.

## Notifications on watchOS 5 (206 — cross-reference)

- Dynamic notification content runs in Notification Center now too (previously Notification Center showed the static fallback). No code change required.
- New "interactive" interface controllers for notifications can have buttons, switches, and gesture recognizers — same model as iOS interactive content extensions.
- `WKExtensionDelegate.handleActiveWorkoutRecovery()` for workout-app crash recovery.

## Cross-references

- Designing tips: 806 (Designing Notifications) covers content best practices, frequency, and the line between useful and annoying.
- New iOS settings affordances for end-users: covered in keynote — Screen Time integration with notification quietening.
- Server-side: critical alerts and provisional notifications work with regular APNS payloads; just include `interruption-level` and `mutable-content` flags as appropriate.
