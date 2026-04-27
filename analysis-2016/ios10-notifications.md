# iOS 10 Notifications Overhaul — WWDC 2016 Analysis

**Sessions covered:** 707 (Introduction to Notifications), 708 (Advanced Notifications)

## Headline

Apple shipped a **brand-new `UserNotifications` framework** that replaces the eight-year-old `UIApplication`/`UILocalNotification` API. The new API is cross-platform (iOS, watchOS 3, tvOS 10), unifies local + remote handling into a single delegate method, and adds two new extension points: **service extensions** (intercept-and-mutate remote notifications before display) and **content extensions** (custom UI for expanded notifications).

The visual redesign is equally significant: rich title + subtitle + body, media attachments (image/audio/video including GIF), 3D-Touch-expandable rich content, in-app foreground presentation.

## The new framework

```swift
import UserNotifications

UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge])
UNUserNotificationCenter.current().delegate = self
```

Key types:
- `UNUserNotificationCenter` — singleton, replaces `UIApplication`'s notification methods.
- `UNMutableNotificationContent` — title, subtitle, body, sound, badge, attachments, categoryIdentifier, threadIdentifier, userInfo.
- `UNNotificationTrigger` — abstract base. Concrete: `UNTimeIntervalNotificationTrigger`, `UNCalendarNotificationTrigger`, `UNLocationNotificationTrigger`, `UNPushNotificationTrigger`.
- `UNNotificationRequest(identifier:content:trigger:)` — the unit you schedule.
- `UNNotificationCategory` + `UNNotificationAction` + `UNTextInputNotificationAction` — actionable notifications.

## Two delegate methods replace eight

```swift
// Foreground presentation (in-app notifications — NEW)
func userNotificationCenter(_ center: UNUserNotificationCenter,
    willPresent notification: UNNotification,
    withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void)

// Response handling (default tap, custom action, dismiss)
func userNotificationCenter(_ center: UNUserNotificationCenter,
    didReceive response: UNNotificationResponse,
    withCompletionHandler completionHandler: @escaping () -> Void)
```

`response.actionIdentifier` is one of:
- `UNNotificationDefaultActionIdentifier` — user tapped the notification body
- `UNNotificationDismissActionIdentifier` — **NEW** — user explicitly dismissed (only delivered if your category opted into `.customDismissAction`)
- One of your custom action identifiers

For text-input actions, `(response as? UNTextInputNotificationResponse)?.userText` gives the typed text.

## Notification management (HIDDEN GEM — new in iOS 10)

Apps can now query and manipulate **pending** AND **delivered** notifications:

```swift
center.getPendingNotificationRequests { … }
center.getDeliveredNotifications { … }
center.removePendingNotificationRequests(withIdentifiers: ["game-update-42"])
center.removeDeliveredNotifications(withIdentifiers: ["score-update"])
center.removeAllDeliveredNotifications()
```

**Updating a delivered notification** — schedule a new request with the **same identifier**, and it replaces the previous one in Notification Center (no clutter). Critical for live sports scores, game state, message threads.

For remote notifications, set the new HTTP/2 push header `apns-collapse-id` to achieve the same effect server-side — the latest payload with a given collapse-id replaces previous ones on-device.

## Settings introspection (HIDDEN GEM)

Apps can finally **read** the user's notification preferences:

```swift
center.getNotificationSettings { settings in
    // settings.authorizationStatus, alertSetting, soundSetting, badgeSetting,
    // notificationCenterSetting, lockScreenSetting, carPlaySetting
}
```

Use this to gracefully degrade UI ("badges are disabled — you won't see unread counts") instead of guessing.

## Triggers — four kinds

| Trigger | Use case |
|---------|----------|
| `UNTimeIntervalNotificationTrigger(timeInterval: 60, repeats: false)` | "in N seconds" / "every N seconds" |
| `UNCalendarNotificationTrigger(dateMatching: components, repeats: true)` | "every weekday at 9am" |
| `UNLocationNotificationTrigger(region: region, repeats: false)` | enter/exit geofence or iBeacon |
| `UNPushNotificationTrigger` | not constructed by you — added by APNs to incoming remote notifications |

## Service Extensions (URGENT new pattern for E2E encryption)

A `UNNotificationServiceExtension` is a non-UI extension that runs **between APNs delivery and notification display**. It receives the original payload, has up to ~30s to mutate it, then calls `contentHandler(modifiedContent)` to display.

Use cases:
- **End-to-end encryption** of remote notifications: server sends ciphertext, your extension decrypts client-side, displays plaintext. APNs never sees readable content.
- **Rich attachments** that exceed the 4KB push limit: server sends a thumbnail URL, extension downloads the image, attaches via `UNNotificationAttachment(identifier:url:options:)`.
- **Localization** of payload sent in a single language.

Required server flag: include `"mutable-content": 1` in the `aps` payload. Without it, the service extension is **never** invoked.

```json
{
  "aps": {
    "alert": {"title": "New message", "body": "Tap to decrypt"},
    "mutable-content": 1
  },
  "encryptedBody": "AES-GCM-base64..."
}
```

```swift
class NotificationService: UNNotificationServiceExtension {
    var contentHandler: ((UNNotificationContent) -> Void)?
    var bestAttempt: UNMutableNotificationContent?

    override func didReceive(_ request: UNNotificationRequest,
                             withContentHandler handler: @escaping (UNNotificationContent) -> Void) {
        contentHandler = handler
        bestAttempt = request.content.mutableCopy() as? UNMutableNotificationContent
        // decrypt …
        bestAttempt?.body = decryptedBody
        handler(bestAttempt!)
    }

    override func serviceExtensionTimeWillExpire() {
        contentHandler?(bestAttempt ?? UNMutableNotificationContent())
    }
}
```

**HIDDEN GEM:** If you fail to call `contentHandler` in time, the system displays the **original** (encrypted) payload — which is unreadable. Always implement `serviceExtensionTimeWillExpire` and call the handler with at least *something*.

## Content Extensions (rich expanded UI)

A `UNNotificationContentExtension` is a `UIViewController` subclass that conforms to `UNNotificationContentExtension`. It renders a **non-interactive** custom view above the standard notification when the user 3D-touches or long-presses to expand.

Match it to a category by identifier in the extension's Info.plist (`UNNotificationExtensionCategory` array). One extension can serve multiple categories.

Critical knobs in Info.plist:
- `UNNotificationExtensionInitialContentSizeRatio` — height/width ratio so the system can size correctly on first present without animation glitch. **Set this** even approximately, otherwise the system animates a resize after your code runs.
- `UNNotificationExtensionDefaultContentHidden` — hide the default title/body row beneath your custom view (since you're already showing the same data).

```swift
class NotificationViewController: UIViewController, UNNotificationContentExtension {
    func didReceive(_ notification: UNNotification) {
        // populate your custom views from notification.request.content
    }

    // OPTIONAL: handle actions inside the extension
    func didReceive(_ response: UNNotificationResponse,
                    completionHandler completion: @escaping (UNNotificationContentExtensionResponseOption) -> Void) {
        // .doNotDismiss — keep open, update UI ("✓ Accepted")
        // .dismiss — close the notification
        // .dismissAndForwardAction — close + deliver to app's UNUserNotificationCenterDelegate
        completion(.doNotDismiss)
    }
}
```

**HIDDEN GEM:** Want a custom keyboard accessory in a text-input action? Make your `UNNotificationContentExtension` return `true` from `canBecomeFirstResponder`, build any `UIView` as `inputAccessoryView`, and the system uses **your** view (with custom buttons!) instead of the plain Send button. The Calendar/Mail apps use this for accept/decline alongside the typed reply.

## Media attachments

Add via `UNMutableNotificationContent.attachments = [UNNotificationAttachment(...)]`. Supported: image (JPEG/PNG/GIF — yes, animated), audio, video (MP4). Max sizes are device-dependent (~10MB image, ~50MB video).

Once attached, the system **moves the file out of your sandbox** and takes ownership. Use `attachment.url.startAccessingSecurityScopedResource()` to read it from inside extensions.

## watchOS 3 brings local scheduling on the watch (HIDDEN GEM)

In watchOS 2, only forwarded notifications worked. In watchOS 3, the watch app can schedule its OWN local notifications via the same `UNUserNotificationCenter` API. The watch is now standalone — workout milestones, reminders during a hike with no phone in range, etc.

If you schedule the same notification (same identifier) from both the iPhone (via Watch Connectivity) AND the watch app, watchOS de-duplicates so the user sees it once. Belt-and-suspenders coverage.

## tvOS 10 — badges only

tvOS 10 supports badging the app icon for both local and remote notifications. Useful for "unwatched episodes" counts, turn-based-game user-action-required indicators. No alerts/sounds — only the count badge.

## Best practices

- **Request authorization at a contextual moment**, not at first launch — the user is more likely to accept when they understand why.
- **Set `categoryIdentifier`** on every notification you might want actions on. Categories are cheap; register them all at app launch.
- **Use `threadIdentifier`** to group conversations / recurring updates so they collapse in Notification Center.
- **Service extensions are mandatory** for any rich-attachment use case where payload exceeds 4KB.
- **Always handle `serviceExtensionTimeWillExpire`** — fail open with whatever you've got.

## Hidden gems summary

- Update a delivered notification by re-using the identifier — no Notification Center clutter.
- `apns-collapse-id` HTTP/2 header replaces silent re-deliveries with mutating updates.
- Settings introspection (`getNotificationSettings`) means apps can gracefully adapt to disabled badges/sounds.
- Service extensions enable end-to-end encrypted notifications.
- Custom `inputAccessoryView` works inside text-input actions — combine quick-reply with custom buttons.
- watchOS 3 schedules notifications independently — works without iPhone in range.
- The `UNNotificationDismissActionIdentifier` only fires if your category opts in via `.customDismissAction`.

## Cross-references

- watchOS 3 notifications integration → analysis-2016/watchos3-redesign.md
- VoIP push behaviour and CallKit — analysis-2016/callkit-voip.md (the reportNewIncomingCall sync rule)
