# Wide Color (Display P3) — WWDC 2016 Analysis

**Sessions covered:** 712 (Working with Wide Color), 605 (What's New in Metal, Part 2)

## Headline

iOS 10 introduces **system-wide color management** with a new working color space: **extended-range sRGB**. The iPad Pro 9.7-inch (and the late-2015 iMac) ship Display P3 panels showing 25% more colors than sRGB. iOS apps that do nothing continue to render correctly. iOS apps that opt in via 16-bit P3 assets, new color constructors, and updated drawing contexts get vivid wide-gamut output where the hardware supports it.

## Color basics, fast

- **Color space**: a coordinate system + primaries + gamma + white point. `sRGB` is the default everywhere; `Display P3` is the new wide one.
- **Display P3 vs DCI-P3**: Apple's P3 inherits the broader color primaries from DCI-P3 (cinema standard), but uses sRGB's gamma 2.2 and D65 (6500K) white point — making it a true superset of sRGB and compatible with web/desktop content.
- **Extended-range sRGB**: same primaries/gamma/white point as sRGB but allows pixel values **<0 and >1**, which can represent any color in the visible spectrum while maintaining sRGB anchor points. Apple uses this as the system **working color space** so existing sRGB content behaves identically while wide content can flow through unchanged.

## Three deployment choices for asset catalogs

The Asset Catalog gets a new **Display Gamut** option (`sRGB and Display P3`):

1. **Do nothing** — your sRGB 8-bit assets keep working. No wide color, no extra cost. Often the right answer.
2. **Universal P3 asset** — replace your asset with a 16-bit Display P3 PNG. Xcode auto-generates an sRGB 8-bit derivative at build time with high-quality color match + dither. App slicing delivers the right variant per device.
3. **Optimize per-gamut** — provide BOTH a 16-bit P3 master AND a hand-tuned 8-bit sRGB asset. Maximum control. Use when the auto-conversion doesn't satisfy.

**BEST PRACTICE:** Convert (don't assign) when migrating Photoshop docs to Display P3 — `Convert to Profile` does a color match, leaving the appearance unchanged. `Assign Profile` re-interprets the existing pixels with new primaries, often making colors look wrong.

## Pixel format Goldilocks

| Format | Bytes/px | Bits/channel | Range | Use |
|--------|----------|--------------|-------|-----|
| `RGBA8` | 4 | 8 | 0–1 | Standard sRGB |
| `RGBAh` (half-float) | 8 | 10 effective | -65k to +65k | **Wide color** — the Goldilocks choice |
| `RGBAf` (full float) | 16 | 24 | unbounded | Maximum precision (Core Image working space) |

`RGBAh` (half-float) is new in CGContext (Sierra) — same precision benefits as full float for ~2× the memory of RGBA8. iOS uses it as the default working format on wide-gamut devices.

There's also `kCVPixelFormatType_30RGBLittleEndianPackedWideGamut` — 4 bytes per pixel, 10 bits per channel, no alpha — useful for capture/display pipelines where alpha is dropped.

## App color creation in code

New convenience constructors:
```swift
UIColor(displayP3Red: 1.0, green: 0.0, blue: 0.0, alpha: 1.0)
NSColor(displayP3Red: 1.0, green: 0.0, blue: 0.0, alpha: 1.0)
```

Existing sRGB constructors (`UIColor(red:green:blue:alpha:)`) **no longer clamp** — pass values <0 or >1 to get extended-range sRGB:
```swift
let oversaturatedRed = UIColor(red: 1.2, green: -0.05, blue: -0.05, alpha: 1.0)
```

## Drawing into wide-color contexts

### iOS — UIGraphicsImageRenderer (NEW, replaces UIGraphicsBeginImageContext)

`UIGraphicsBeginImageContext` is documented to only ever return RGBA8 contexts — no wide color. Use the new renderer:

```swift
let renderer = UIGraphicsImageRenderer(size: CGSize(width: 200, height: 200))
let image = renderer.image { context in
    UIColor(displayP3Red: 1, green: 0, blue: 0, alpha: 1).setFill()
    context.fill(CGRect(x: 0, y: 0, width: 100, height: 200))
    UIColor(red: 1, green: 0, blue: 0, alpha: 1).setFill()
    context.fill(CGRect(x: 100, y: 0, width: 100, height: 200))
}
```

By default it picks RGBAh on wide-gamut devices, RGBA8 elsewhere. Auto color-managed. Auto-handles context lifetime. Compatible with `UIGraphicsGetCurrentContext()` for legacy code.

### macOS — `NSImage(size:flipped:drawingHandler:)`

Already wide-color aware on Sierra. Use it everywhere on Mac.

### CALayer.contentsFormat (NEW)

`CALayer.contentsFormat` controls pixel depth. Defaults: `RGBA8` on standard devices, **wide color (RGBAh) on iPad Pro 9.7's display**. Force a depth via:
```swift
layer.contentsFormat = .RGBA8Uint     // legacy 8-bit
layer.contentsFormat = .RGBA16Float   // wide-color
```

Use `RGBA8Uint` if you're rendering UI you know will never need wide color — saves memory.

### UITraitCollection.displayGamut (NEW)

```swift
switch traitCollection.displayGamut {
case .P3: useWideColorAsset()
case .SRGB: useStandardAsset()
}
```

Use when you need to match a UIColor with an asset-catalog asset across the gamut boundary.

## Communicating colors clearly (HIDDEN GEM)

When designers and engineers exchange RGB tuples, they implicitly assume sRGB. With wide color, this assumption fails. **Annotate the color space** when writing colors anywhere:
```
P3(255, 128, 191)
P3(1.0, 0.5, 0.75)  // floating-point preferred for precision
sRGB(64, 128, 200)
```

The macOS Color Panel got new options:
- Action menu: directly select sRGB or Display P3 for the numeric input.
- Toggle integer (0–255) ↔ floating-point.
- Hue wheel renders the full P3 gamut on capable displays.
- Pin the picker to a specific gamut.

## Storage of colors in documents (BEST PRACTICE)

If you store colors in document data and need backwards compatibility, **store BOTH the wide-gamut color AND a converted sRGB fallback**. Older versions of your app, unaware of the wider gamut, can read the sRGB fallback. Newer versions read the P3 value.

```swift
let p3Color = UIColor(displayP3Red: 1.0, green: 0.0, blue: 0.0, alpha: 1.0)
// store p3 components AND sRGB equivalent:
let srgbColor = p3Color.convert(to: CGColorSpace(name: CGColorSpace.sRGB)!)
```

Apple's TextEdit RTF document format gained an annotated color table for this exact reason.

## App slicing keeps payloads small

Wide-color assets only ship to wide-color devices. iPhone 6 doesn't download the 16-bit P3 PNGs. Mac apps select the appropriate variant when the user moves between displays (and refresh automatically via app slicing + display change notifications).

## ASTC GPU compression for asset catalogs (NEW)

`Asset Catalog Compression` options gained:
- **Lossless** (existing)
- **Basic (lossy)** — JPEG-like with alpha. Great quality, small files, all devices.
- **GPU best quality (ASTC 4bpp)** — high-quality GPU-compressed texture
- **GPU smallest size (ASTC 1bpp)** — minimum footprint

ASTC variants render directly on supporting GPUs (zero-copy texture upload — huge memory win for games). Older GPUs get an automatic software fallback texture variant. Wide-color content with ASTC: dithers down to 8-bit but stores in Display P3 colorspace at compress time, preserving the gamut even though channel depth drops.

## Web wide color (HIDDEN GEM)

- Tagged image content auto-color-matches in WebKit.
- New CSS media query: `@media (color-gamut: p3) { … }` selects between asset variants.
- A draft CSS Color Level 4 syntax for naming colors in non-sRGB spaces is in development.

## Best practices summary

- Convert (don't reassign) Photoshop docs to Display P3 when going wide.
- Provide 16-bit Universal Display P3 PNGs in asset catalogs; let Xcode auto-derive sRGB.
- Use `UIGraphicsImageRenderer` instead of `UIGraphicsBeginImageContext` for any new image generation.
- Use `UIColor(displayP3Red:…)` and label colors as `P3(…)` when communicating.
- Store wide colors with sRGB fallback for backwards-compatible document formats.
- Adopt `@media (color-gamut: p3)` on the web for served-image variants.

## Hidden gems summary

- `RGBAh` (half-float) is the "Goldilocks" pixel format — 8 bytes/pixel for 10-bit precision and ±65k range.
- `UIGraphicsImageRenderer` auto-picks wide color on capable devices — drop-in modernization.
- `CALayer.contentsFormat = .RGBA8Uint` saves memory when you know UI doesn't need wide color.
- ASTC compression auto-falls-back to RGBA8 textures for older GPUs — zero-effort GPU compression.
- `@media (color-gamut: p3)` lets web apps serve different image assets per gamut.
- Color Panel toggles between sRGB/P3 numeric input — finally explicit at the source.

## Cross-references

- Camera capture in wide color → analysis-2016/photos-camera-media.md
- Core Image RAW pipeline (extended sRGB working space) → analysis-2016/photos-camera-media.md
- Metal wide color textures → session 605 (in same area)
