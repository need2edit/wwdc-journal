# Maps Transit + Extensions — WWDC 2016 Analysis

**Sessions covered:** 241 (Public Transit in Apple Maps), 240 (Increase Usage of Your App With Proactive Suggestions — Maps integration parts), 716 (Core Location Best Practices)

## Headline

Apple Maps in iOS 10 opens up to **third-party extensions** — ride sharing booked from inside Maps (using the same SiriKit intents extension), restaurant reservations, food ordering — and ships **fully-curated transit support** in 21 cities + 300+ in China. The ride-booking extension API is one of the year's quietest but most impactful integrations.

## Transit data quality (session 241)

Apple's transit philosophy: don't just import GTFS feeds. Curate.

- **16,000+ station entrances** mapped individually, with specific exit codes (E3 not "exit") to match real-world signage.
- **Real path geometry** for every transit line — buses follow streets, trains follow tracks. Schematic maps (London Tube style) lose your dot-on-the-line context.
- **Per-city terminology**: "BART" (no line names), "the A train" (lines as nouns), "the 510 Spadina streetcar" (specific), "uptown/downtown" vs "northbound/southbound" — every system gets local-correct vocabulary.
- **Multi-agency transfers** with appropriate signage and exit codes.

For developers, the API impact is minimal — `MKDirectionsRequest` with `.transit` mode just works in supported cities — but the user-experience bar is now very high. If your routing app competes in transit, this is the standard.

## Maps third-party extensions

Maps gains a **ride-booking extension** that piggybacks on the SiriKit `INRequestRideIntent` infrastructure. **Adopting SiriKit for ride-booking automatically gives you Maps integration** (and CarPlay) — same intent extension, three surfaces.

The user picks "Get a Ride" in Maps, picks your service from a list, taps Confirm → Apple Pay sheet appears (if your service uses Apple Pay). Optional UI extension lets you brand the Maps card.

Other supported third-party extensions in iOS 10 Maps:
- **Restaurant reservations** (`INBookRestaurantReservationIntent`)
- **Food ordering** (`INPayBillIntent` family)

## Promote your routing app via `MKDirectionsRequest`

Even outside Maps' first-class extensions, you can register your routing app to handle directions URLs for users when iOS infers a routing intent.

1. Enable the **routing apps capability** in Xcode → Capabilities.
2. **Declare supported routing modes** in Info.plist (`MKDirectionsModeCar`, `Bus`, `Train`, `Bike`, `Walking`, `Streetcar`, `Subway`, `Taxi`, `Ferry`, `Pedestrian`, **`RideShare`** new in iOS 10, etc.).
3. **Declare supported regions** — ship a `MKMapRegion` GeoJSON for the territories your app covers (city-bound apps don't get suggested in cities they don't serve).
4. Implement `application(_:open:options:)` — the URL is launched by the system; convert with `MKDirectionsRequest(contentsOf: url)`.

**HIDDEN GEM (NEW in iOS 10):** Your app may be launched with map items that have **no geo-coordinates** — only an address dictionary. You're responsible for geocoding via `CLGeocoder.geocodeAddressDictionary(_:completionHandler:)` to get lat/lng before routing. Old code that assumed lat/lng was always populated will fail silently.

## Location-based proactive surfaces (session 240)

iOS 10 promotes locations the user recently viewed in YOUR app across the system: Multitasking UI ("Get directions to The Mill"), Messages QuickType ("Let's meet at —"), Maps app, Today widget, CarPlay, even inside *other* apps that opt in (Uber's destination text field shows Yelp results).

Adoption: capture an `NSUserActivity` with location info via:

```swift
let activity = NSUserActivity(activityType: "com.example.viewing-location")
activity.title = restaurant.name
activity.isEligibleForHandoff = true
activity.isEligibleForSearch = true
activity.isEligibleForPublicIndexing = true  // discovers via differential privacy

// Either…
activity.mapItem = mapItem  // MapKit shortcut

// …or build the attribute set directly
let attrs = CSSearchableItemAttributeSet(itemContentType: kUTTypeJSON as String)
attrs.namedLocation = restaurant.name
attrs.thoroughfare = restaurant.streetAddress
attrs.city = restaurant.city
attrs.latitude = NSNumber(value: restaurant.lat)
attrs.longitude = NSNumber(value: restaurant.lng)
attrs.phoneNumbers = [restaurant.phone]
attrs.supportsNavigation = NSNumber(value: true)
attrs.supportsPhoneCall = NSNumber(value: true)
activity.contentAttributeSet = attrs

self.userActivity = activity  // UIResponder property — UIKit manages currentness
```

`mapItem` is a one-line shortcut that auto-populates the searchable item attribute set. Use it when you have an `MKMapItem` already.

**BEST PRACTICE:** Set `userActivity.needsSave = true` and implement `userActivityWillSave(_:)` to lazily update the userInfo only when the activity is about to be persisted/handed off — don't rebuild on every keystroke.

## Consume location suggestions in your app

If your app accepts addresses (an Uber-like destination field), opt your text fields in to receive system location suggestions:

```swift
addressField.textContentType = .fullStreetAddress
// or .addressCityAndState, .addressCity, .addressState, .countryName, .postalCode, .sublocality, .streetAddressLine1, .streetAddressLine2
```

When the system has a recently-viewed location matching that intent, it surfaces in the QuickType bar above the keyboard. Even without explicit suggestions, declaring `textContentType` improves autocorrect (it knows you're typing an address).

`UITextContentType` also covers names, phone numbers, emails, organization, location subcomponents — declare them on every relevant text field.

## Schema.org for the web (HIDDEN GEM)

If your business has a website mirroring the in-app content (Yelp, Open Table), annotate it with **Schema.org** metadata (JSON-LD or microdata):

```html
<script type="application/ld+json">
{
  "@context": "http://schema.org",
  "@type": "Restaurant",
  "name": "The Mill",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "736 Divisadero St",
    "addressLocality": "San Francisco",
    "addressRegion": "CA"
  },
  "telephone": "+14156535104",
  "geo": { "@type": "GeoCoordinates", "latitude": 37.7766, "longitude": -122.4378 }
}
</script>
```

Safari extracts these annotations and **promotes the location across the same system surfaces NSUserActivity does** — Multitasking suggestions, Messages QuickType, Maps. Your website becomes a first-class iOS data source.

Apple's tool at `search.developer.apple.com` validates your markup.

## Best practices

- **Adopt SiriKit ride-booking** — you get Siri + Maps + CarPlay for one extension's effort.
- **Always declare `textContentType`** for fields accepting addresses, phone numbers, emails.
- **Use `mapItem` shortcut on NSUserActivity** when you have an MKMapItem.
- **For ride-share apps, declare `MKDirectionsModeRideShare`** in supported routing modes.
- **Mark your activity dirty (`needsSave = true`) instead of rebuilding userInfo eagerly.**
- **Annotate websites with Schema.org** — Safari relays the data into the same proactive surfaces.

## Hidden gems summary

- Adopting SiriKit ride-booking gets you Apple Maps and CarPlay for free — same extension.
- The `mapItem` setter on NSUserActivity auto-populates `contentAttributeSet`.
- iOS 10 may launch routing apps with map items missing lat/lng — you must geocode the address dictionary first.
- Schema.org markup on your website surfaces the same proactive UI as a native NSUserActivity.
- `UITextContentType` improves autocorrect quality even when no suggestions are present.

## Cross-references

- SiriKit intents that drive Maps extensions → analysis-2016/sirikit-debut.md
- NSUserActivity + Search → analysis-2016/search-spotlight.md
- Apple Pay inside ride-booking → analysis-2016/apple-pay-web-extensions.md
