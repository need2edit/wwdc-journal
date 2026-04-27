# iMessage Apps & Stickers Debut — WWDC 2016 Analysis

**Sessions covered:** 204 (iMessage Apps and Stickers, Part 1), 224 (iMessage Apps and Stickers, Part 2)

## Headline

iOS 10 ships the **Messages App Store** — an entirely new App Store, a new business model, a new app type. iMessage apps run inside the Messages app, can ship as standalone (no containing app required), and can be sticker-only (zero code). The Messages App Drawer and inline app attribution turn shared content into a sticker discovery loop.

## Three content types an iMessage app can produce

1. **Interactive messages** — your app generates a custom bubble; tapping it on the recipient's device launches your app to interact with the data (collaborative ordering, polls, etc.).
2. **Stickers** — PNG/APNG/JPEG/GIF up to 500KB. Drag-and-drop onto bubbles. Live in the new Sticker tray.
3. **Anything Messages already supports** — photos, video, links — your iMessage app can attach them too.

## Two ways to build (BEST PRACTICE)

**Sticker Pack Application** — *no code at all*. Xcode template, drop PNGs into the Stickers asset catalog, ship to App Store. Apple handles drag-and-drop, tray rendering, attribution.

**Custom Messages Application** — code-driven. Subclass `MSMessagesAppViewController`. Use `MSStickerBrowserViewController` (default grid) or build your own UI with `MSStickerView` + `MSSticker`. Background colors, layouts, in-app purchase to unlock packs, server-driven sticker fetching, camera-generated stickers — all custom.

## Sticker file format guidance

- **Use PNG / APNG.** PNGs handle transparency cleanly. **GIFs and JPEGs do NOT** — JPEGs have no alpha at all; GIFs leave artifacted edges visible against any background. Your sticker can be dropped onto a photo — transparency matters.
- Provide stickers at **3x scale always**, regardless of target device. Messages framework downscales for 1x/2x devices.
- Cell sizes: small (100×100pt @3x), regular (136×136pt @3x), large (206×206pt @3x). Your max sticker dimension is the cell — anything larger gets shrunk.
- **Hard cap: 500KB per sticker.** Chosen so attachments transmit fast and use minimal on-disk space; Messages performs additional optimization under the hood.

## No containing app required (URGENT for marketing)

This is new. Your iMessage app can ship **standalone** — it shows in the Messages App Store and Messages App Drawer only, NOT in the regular App Store or iOS home screen. You still must provide a containing-app icon (used in Settings for storage info), but no companion app code.

If you DO have a containing app, you can ship the Messages extension inside it; users see your icon both on the home screen AND in the Messages App Drawer.

## Inline app attribution (HIDDEN GEM — drives installs)

When a user receives a sticker (or any content) from an app they don't have installed, Messages shows the app's name beneath the bubble. **Tapping the attribution opens that app's page in the Messages App Store.** This is the viral discovery loop.

This applies to ALL content types your iMessage app produces, not just stickers.

## Interactive messages (Part 2)

A custom message uses an `MSMessage` carrying a `MSMessageTemplateLayout` (or a custom `MSMessageLiveLayout` in iOS 11). The message has a `URL` that encodes your app's state. Tapping launches your iMessage extension on the recipient's device, you decode the URL, build the next state, send back. Useful for:

- DoorDash group menu building (the headline demo)
- Collaborative ride-sharing
- Polls
- Game turns

## Compact vs expanded presentation

`MSMessagesAppPresentationStyle` is `.compact` (lives below the keyboard) or `.expanded` (fills most of the screen). User toggles via the chevron. Apps must handle both modes:

- Override `willTransition(to:)` and `didTransition(to:)`.
- Call `requestPresentationStyle(.expanded)` to programmatically expand (when picking from a long list, capturing a photo, etc.).

## Cross-platform consumption

iMessage apps **only run on iOS 10**, but the content they produce travels:

- **watchOS 3 Recents Page** — recently sent stickers from the iPhone show up on the Watch's Messages app, and the watch can re-send them without the iPhone present.
- **macOS Sierra** can view stickers and interactive bubbles, but cannot author iMessage app content.

## API minimum vocabulary

- `MSMessagesAppViewController` — your principal class. Subclass `MSMessagesAppViewController`.
- `MSStickerBrowserViewController` + `MSStickerBrowserView` + `MSStickerBrowserViewDataSource` — out-of-the-box sticker grid.
- `MSStickerView` — single sticker with built-in drag/drop. Use inside any UICollectionView/UIScrollView for custom layouts.
- `MSSticker(contentsOfFileURL:localizedDescription:)` — wraps a sticker image with VoiceOver-readable description.
- `MSConversation` — the active conversation; `insert(_:)`, `send(_:)`.

## Best practices

- Subclass `MSStickerBrowserViewController` for the simplest custom-background-with-grid case (just override `numberOfStickers` and `sticker(at:)`).
- Set `MSStickerView`'s `startAnimating()` / `stopAnimating()` based on whether the cell is on screen — animated APNG/GIF stickers consume CPU you don't want when scrolled off.
- Use `CGImageSourceCreateWithURL` + `CGImageSourceGetCount` to detect animated stickers (count > 1 frame).
- Read app's containing-bundle display name with care — it's also the bundle identifier suffix the App Store users see.

## Hidden gems summary

- **Sticker-only apps ship with literally zero source code.** Just drag PNGs into the asset catalog.
- **Inline app attribution drives free user acquisition** — every sticker you send is essentially an ad.
- **iMessage extensions get camera, IAP, and Apple Pay** — full iOS app capability inside the conversation.
- **APNG sticker sequences** — Xcode lets you assemble individual frames into an APNG with no command-line tooling.
- **Recents on watchOS 3** automatically promotes recently-sent stickers — no Watch app code required from you.

## Cross-references

- Apple Pay inside iMessage extensions → analysis-2016/apple-pay-extensions.md
- Notifications around message delivery → analysis-2016/ios10-notifications.md
