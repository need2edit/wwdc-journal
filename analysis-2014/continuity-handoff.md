# Continuity & Handoff — WWDC 2014 Analysis

**Sessions covered:** 219 (Adopting Handoff on iOS and OS X), 506 (Ensuring Continuity Between Your App, Your Website, and Safari), 711 (Keychain and Authentication with Touch ID — for shared web credentials)

## Headline

iOS 8 + OS X Yosemite introduce **Continuity** — a suite of features that make Apple devices feel like one continuous experience. The flagship: **Handoff**, where any activity in progress on one device (composing email, browsing a webpage, editing a document) appears on nearby Apple devices for instant resumption. Plus **shared web credentials**, **Instant Hotspot**, **SMS Relay**, **iPhone calls on Mac**.

## The Mental Model — NSUserActivity (session 219)

- **`NSUserActivity`** is the universal currency. ONE class, identical API on iOS and OS X. Represents a discrete user activity (composing message, viewing document, editing image).
- **Activity types** are reverse-DNS strings you make up: `com.example.MyApp.composing`. Listed in your Info.plist `NSUserActivityTypes` array (regular apps) or `NSUbiquitousDocumentUserActivityType` per-document-type entry (document apps) (219).
- HIDDEN GEM: **document-based apps get Handoff almost for free** — declare `NSUbiquitousDocumentUserActivityType` per `CFBundleDocumentTypes` entry, and `NSDocument`/`UIDocument` automatically creates and manages the user activity for documents in iCloud (219).
- **Three callbacks** matter:
  1. `becomeCurrent()` — start broadcasting this activity to nearby devices via BTLE.
  2. `updateUserInfo(...)` — populate the `userInfo` dictionary with state needed to resume the activity.
  3. `invalidate()` — stop broadcasting. The activity is done.
- AppKit/UIKit do all this for you when you set `userActivity` on a `UIResponder`/`NSResponder` (any view, view controller, window, document) (219).

## Activity State Transfer (session 219)

- **`userInfo`** is a `[String: Plist]` dictionary that travels from device to device. Plist types only: NSString, NSNumber, NSData, NSDate, NSArray, NSDictionary. Plus `NSURL` — but only `file://` URLs in iCloud or document providers (URLs to content addressable across devices) (219).
- **Keep it small.** Bytes count. Don't ship the whole document — ship the URL of the document in iCloud + a position offset. Resume target loads from iCloud (219).
- BEST PRACTICE: include a **version number** in your `userInfo` so future versions of your app can handle older payloads gracefully (219).
- BEST PRACTICE: avoid platform-specifics like a UIScrollView's visible rect. Use a content-relative anchor ("scroll to the message with this ID") that resolves on either platform (219).
- **`needsSave`** flag: set when state has changed; the framework calls back later via `userActivityWillSave(_:)` to populate the dict. **Don't update `userInfo` after every keystroke** — set the flag and let the framework batch (219).

## Continuation on the Receiving Device (session 219)

- `application(_:willContinueUserActivityWithType:)` — fires when user TAPS the Handoff icon. You don't have the user info yet (still being fetched). Show "loading the email" UI immediately for perceived speed.
- `application(_:continue:restorationHandler:)` — fires when the activity has been fetched. You get the full `NSUserActivity`. Restore the state, optionally hand `restorationHandler` an array of responders that need their `restoreUserActivityState(_:)` called.
- `application(_:didFailToContinueUserActivityWithType:withError:)` — fires if the transfer fails. Apple guarantees: for every `willContinue`, you get exactly ONE of `continue` or `didFail` (219).
- HIDDEN GEM: if the error is `NSUserCancelledError`, **don't surface anything** — the system already cancelled silently because the user picked a different activity (219).

## Continuation Streams (session 219)

- HIDDEN GEM: an activity can opt into **bi-directional `NSStream` pairs between continuing devices**. Set `supportsContinuationStreams = true` on the source activity; on the receiver, call `getContinuationStreams(completionHandler:)` to get NSInputStream + NSOutputStream connected to the source.
- Use case: a real-time multiplayer game starts on iPhone; user opens iPad to "join the same game"; the app uses the continuation stream as a side-channel for game-state sync (219).
- The source-side activity's delegate gets `userActivity(_:didReceive:outputStream:)` with the matching streams (219).

## Native ↔ Web Handoff (session 219)

- HIDDEN GEM: an activity can carry a `webpageURL` — a HTTPS URL. If a continuing device doesn't have an app that claims your activity type, it offers Safari instead. The user lands on your URL (219).
- Reverse direction: a user on your website can hand off TO your iOS app. Configure the **`com.apple.developer.associated-domains`** entitlement listing `applinks:yourdomain.com`. Your domain serves an `apple-app-site-association` JSON file mapping iOS app IDs to allowed paths. iOS validates and routes the Handoff to your app (219).
- This is the same association-domains plumbing later used for Universal Links (iOS 9) and Shared Web Credentials (described below).

## Shared Web Credentials (session 506)

- The login problem: user creates account in Safari (with iCloud Keychain saving the password); user installs your app; **the app shows a login screen**, defeating the iCloud Keychain win.
- iOS 8 fix: **`SecRequestSharedWebCredential`** lets your app read passwords Safari has saved for your domain — *if your app and your domain are associated*.
- Setup mirrors Native↔Web Handoff: `com.apple.developer.associated-domains` entitlement listing `webcredentials:yourdomain.com`; serve `apple-app-site-association` with appropriate JSON (506).
- Three new APIs:
  - **`SecRequestSharedWebCredential(domain, account, completion)`** — shows a system picker of credentials for the domain; returns the user's selected user/password to your app (506).
  - **`SecAddSharedWebCredential(domain, account, password, completion)`** — adds/updates/deletes a credential (pass nil password to delete). Syncs across devices via iCloud Keychain.
  - **`SecCreateSharedWebCredentialPassword()`** — returns a strong random password in the same format as Safari's password generator.
- BEST PRACTICE: in your login flow, check shared web credentials BEFORE showing your login UI. If the user has one, populate your fields automatically and attempt the sign-in (506).

## Web AutoFill — Help Safari Help You (session 506)

- Safari's password manager uses heuristics to identify forms. New `autocomplete` attribute values in iOS 8/Safari 8: **`username`**, **`current-password`**, **`new-password`**.
- Mark login forms: `<input autocomplete="username">` + `<input type="password" autocomplete="current-password">`.
- Mark account creation: `<input autocomplete="username">` + `<input type="password" autocomplete="new-password">` (so Safari offers password generation).
- Mark password change: include `<input type="hidden" autocomplete="username" value="user@example.com">` (so Safari knows WHICH user is updating) + `<input autocomplete="current-password">` + `<input autocomplete="new-password">` (506).
- HIDDEN GEM: for AJAX-driven sites that don't do full page reloads, call **`history.pushState(...)` or `replaceState(...)`** after a successful password change. Safari listens for these to know when to prompt about saving the new password (506).

## Apple-Touch-Icon for Safari Start Page (session 506)

- iOS 7+ Safari shows a "Favorites" + "Frequently Visited" start page. The icon used is your **`apple-touch-icon`** (the same one used when adding to home screen).
- BEST PRACTICE: add `<link rel="apple-touch-icon" sizes="180x180" href="...">` to ALL pages of your site, not just mobile-targeted ones. Safari 8 on Mac uses these too (506).
- Use the entire square canvas — iOS handles rounding the corners automatically. Don't pre-mask, you'll get mismatched corner radii (506).

## Best Practices

- **Identify discrete user activities first** before writing code. "Reading email" and "composing email" are SEPARATE activities — different icons, different resume targets (219).
- **Set `userActivity` on the responder hierarchy**; AppKit/UIKit will call `becomeCurrent` for you when the responder is on screen and the window is key (219).
- **Set `needsSave = true` when state changes** instead of repeatedly updating `userInfo` — let the framework batch (219).
- **Test all four cases**: brand-new credential creation, sign-in with existing credential, password change, no credential available (506).
- **Use `webpageURL` as a fallback** so users on devices without your app still get something useful (219).
- **Test with Safari AutoFill on a clean iCloud account** — your daily-use accounts will mask bugs in your form heuristics (506).

## Hidden Gems

- HIDDEN GEM: **the activity type string is the binding key** between source and destination. Different vendors can claim the same activity type if Apple agrees ("com.example.markdownreading" — many markdown editors could continue each other). In practice, use your reverse-DNS prefix (219).
- HIDDEN GEM: `userActivityWasContinued(_:)` delegate callback fires on the SOURCE device when continuation succeeds elsewhere. Mail uses this to delete a draft on the source iPhone when the user continues the draft on Mac (219).
- HIDDEN GEM: `application(_:didUpdate:)` is a great debug breakpoint to inspect exactly what's in your `userInfo` before broadcast (219).
- HIDDEN GEM: shared web credentials' `SecAddSharedWebCredential` updates iCloud Keychain on ALL the user's devices simultaneously. Change a password in your iOS app, see it on Safari Mac immediately (506).
- WARNING: if you don't host `apple-app-site-association` correctly (must be served as `application/json`, served from `/.well-known/apple-app-site-association` OR `/apple-app-site-association`, signed with a valid TLS-CA-issued certificate), iOS silently refuses the association. Test thoroughly (219).

## Cross-references

- **App Extensions (205, 217)** — extensions can also be Handoff sources/destinations. The today widget can hand off to the main app.
- **iCloud Drive** — the canonical content store for documents you reference in `userInfo` via file URLs.
- **CloudKit (208)** — useful for activity payloads larger than the recommended NSUserActivity size budget; store the bulk in CloudKit, ship the record ID in the activity.
- **Touch ID (711)** — Shared Web Credentials integrates with Touch ID for the credential picker UI (touch to authorize the credential transfer).

## Migration Guidance

- **Apps with iCloud documents already**: enabling Handoff is a few lines + Info.plist key. Almost-free win.
- **Apps with custom server-side accounts**: invest in shared web credentials + autocomplete attribute values on your forms. The cross-platform single-sign-on UX is a significant differentiator.
- **Apps with custom URL schemes for app↔website routing**: migrate to `apple-app-site-association` + universal links pattern (the precursor in 2014, full Universal Links arrives in iOS 9).
- **Don't over-implement Continuation Streams** unless you have a real-time interactive use case — it's a heavy hammer (NSStream over Wi-Fi/BTLE peer-to-peer); most Handoff use cases are stateless transfers.
