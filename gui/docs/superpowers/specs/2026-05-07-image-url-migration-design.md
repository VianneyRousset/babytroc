# Image URL Migration Design

## Summary

Migrate item image fetching from `/api/v1/images/{name}?s={size}` to `https://babytroc.ch/images/{name}_{size}.webp`.

## Available Sizes

128, 256, 512, 1024 (no original/unresized variant).

## Changes

### `app/utils/image.ts`

Replace single-arg `imagePath` with a sized version:

```ts
type ImageSize = 128 | 256 | 512 | 1024
export const imagePath = (name: string, size: ImageSize = 1024) =>
  `https://babytroc.ch/images/${name}_${size}.webp`
```

### `app/composables/item.ts`

- `useItemImages`: drop `imagesPaths`, keep only `imagesNames`
- `useItemFirstImage`: drop `firstImagePath`, keep only `firstImageName`
- Consumers call `imagePath(name, size)` directly

### Component updates

| Component | Change |
|---|---|
| `ItemCard.vue` | Use `firstImageName` + `imagePath(name, 512)` / `imagePath(name, 128)` |
| `ItemImagesGallery.vue` | Pass image names to `ImageGallery` instead of paths |
| `ImageGallery.vue` | Accept `images: string[]` as names, call `imagePath` internally (1024 main, 128 placeholder) |
| `ProgressiveImage.vue` | Accept `name: string` instead of `src`/`placeholderSrc`, call `imagePath` internally |
| `ImageAndAvatar.vue` | Accept `imageName` prop, call `imagePath(name, 256)` internally |
| `ChatSlab.vue` | Pass `firstImageName` instead of `firstImagePath` |
| `LoanSlab.vue` | Pass `firstImageName` instead of `firstImagePath` |
| `LoanRequestSlab.vue` | Pass `firstImageName` instead of `firstImagePath` |
| `ItemEditionForm.vue` | Use `imagePath(name, 1024)` for studio image loading |

### Upload path unchanged

`image-uploader.ts` POSTs to `/v1/images` and returns a name. No change needed.
