# Image URL Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate image fetching from `/api/v1/images/{name}?s={size}` to `https://babytroc.ch/images/{name}_{size}.webp`

**Architecture:** Update `imagePath` utility to accept a size parameter and build the new URL. Simplify composables to return names only. Update all consuming components to call `imagePath(name, size)` directly with appropriate sizes.

**Tech Stack:** Vue 3, Nuxt, TypeScript

---

## File Map

| File | Action | Responsibility |
|---|---|---|
| `app/utils/image.ts` | Modify | `imagePath(name, size)` utility |
| `app/composables/item.ts` | Modify | Drop path-returning computed props, keep name-only |
| `app/components/ui/ProgressiveImage.vue` | Modify | Accept `name` prop, build URLs internally |
| `app/components/ui/ImageGallery.vue` | Modify | Pass names to ProgressiveImage |
| `app/components/item/ItemImagesGallery.vue` | Modify | Pass names instead of paths |
| `app/components/item/card/ItemCard.vue` | Modify | Use `firstImageName` + `imagePath` |
| `app/components/ImageAndAvatar.vue` | Modify | Accept `imageName`, build URL internally |
| `app/components/chat/ChatSlab.vue` | Modify | Use `firstImageName` |
| `app/components/loan/LoanSlab.vue` | Modify | Use `firstImageName` |
| `app/components/loan/LoanRequestSlab.vue` | Modify | Remove unused `firstImagePath` |
| `app/components/item/ItemEditionForm.vue` | Modify | Use `imagePath(name, 1024)` for studio |

---

### Task 1: Update `imagePath` utility

**Files:**
- Modify: `app/utils/image.ts:1`

- [ ] **Step 1: Update imagePath to accept size parameter**

Replace the contents of `app/utils/image.ts` with:

```ts
export type ImageSize = 128 | 256 | 512 | 1024

export const imagePath = (name: string, size: ImageSize = 1024) =>
  `https://babytroc.ch/images/${name}_${size}.webp`
```

- [ ] **Step 2: Commit**

```bash
git add app/utils/image.ts
git commit -m "feat: update imagePath to use new URL format with size parameter"
```

---

### Task 2: Simplify composables to return names only

**Files:**
- Modify: `app/composables/item.ts:1-25`

- [ ] **Step 1: Remove path-returning computed props**

Replace the full contents of `app/composables/item.ts` with:

```ts
/* NEW */
export function useItem({ itemId }: { itemId: MaybeRefOrGetter<number> }) {
  const { data: item, ...query } = useApiQuery('/v1/items/{item_id}', {
    key: () => ['item', `item-${toValue(itemId)}`],
    path: () => ({
      item_id: toValue(itemId),
    }),
    refetchOnMount: false,
  })
  return { item, ...query }
}

export function useItemImages<T extends { image_names: Array<string> }>(item: MaybeRefOrGetter<T>) {
  return {
    imagesNames: computed(() => toValue(item).image_names),
  }
}

/* OLD */

export const useItemFirstImage = (item: MaybeRefOrGetter<ItemPreview>) => ({
  firstImageName: computed(() => toValue(item).first_image_name),
})
```

- [ ] **Step 2: Commit**

```bash
git add app/composables/item.ts
git commit -m "refactor: composables return image names only, drop path computed props"
```

---

### Task 3: Update ProgressiveImage to accept image name

**Files:**
- Modify: `app/components/ui/ProgressiveImage.vue:1-19`

- [ ] **Step 1: Replace props and computed logic**

Replace the `<script setup>` block in `ProgressiveImage.vue` with:

```vue
<script setup lang="ts">
const props = defineProps<{
  name: string
}>()

const { name } = toRefs(props)

const src = computed(() => imagePath(unref(name), 1024))
const placeholderSrc = computed(() => imagePath(unref(name), 128))

const { data: imageData, status } = useQuery({
  key: () => ['image', unref(src)],
  query: async () => {
    const request = new Request(unref(src))
    const resp: Response = await fetch(request)
    return URL.createObjectURL(await resp.blob())
  },
})

const placeholder = computed(() => unref(status) !== 'success')
const _src = computed(() => unref(placeholder) ? unref(placeholderSrc) : unref(imageData))
</script>
```

- [ ] **Step 2: Commit**

```bash
git add app/components/ui/ProgressiveImage.vue
git commit -m "refactor: ProgressiveImage accepts name prop, builds URLs internally"
```

---

### Task 4: Update ImageGallery to pass names

**Files:**
- Modify: `app/components/ui/ImageGallery.vue:65-68`

- [ ] **Step 1: Update ProgressiveImage usage**

In `ImageGallery.vue`, replace:

```vue
        <ProgressiveImage
          class="carousel__item"
          :src="`${image}`"
          :placeholder-src="`${image}?s=16`"
        />
```

with:

```vue
        <ProgressiveImage
          class="carousel__item"
          :name="image"
        />
```

No other changes needed — `images: string[]` prop stays the same, it just now represents names instead of paths. The prop name `images` still makes sense.

- [ ] **Step 2: Commit**

```bash
git add app/components/ui/ImageGallery.vue
git commit -m "refactor: ImageGallery passes image names to ProgressiveImage"
```

---

### Task 5: Update ItemImagesGallery to pass names

**Files:**
- Modify: `app/components/item/ItemImagesGallery.vue:11`

- [ ] **Step 1: Pass names instead of paths**

In `ItemImagesGallery.vue`, replace:

```ts
const { imagesPaths } = useItemImages(item)
```

with:

```ts
const { imagesNames } = useItemImages(item)
```

And in the template, replace:

```vue
    :images="imagesPaths"
```

with:

```vue
    :images="imagesNames"
```

- [ ] **Step 2: Commit**

```bash
git add app/components/item/ItemImagesGallery.vue
git commit -m "refactor: ItemImagesGallery passes image names to ImageGallery"
```

---

### Task 6: Update ItemCard to use imagePath with sizes

**Files:**
- Modify: `app/components/item/card/ItemCard.vue:15-24`

- [ ] **Step 1: Replace firstImagePath with firstImageName + imagePath**

In `ItemCard.vue`, replace:

```ts
const { firstImagePath } = useItemFirstImage(item)

const backgroundImage = computed(() => {
  const backgrounds = []

  backgrounds.push('linear-gradient(transparent 0 40%, #202020 100%)')
  backgrounds.push(`url('${unref(firstImagePath)}?s=512')`)
  backgrounds.push(`url('${unref(firstImagePath)}?s=32')`)

  return backgrounds.join(', ')
})
```

with:

```ts
const { firstImageName } = useItemFirstImage(item)

const backgroundImage = computed(() => {
  const backgrounds = []

  backgrounds.push('linear-gradient(transparent 0 40%, #202020 100%)')
  backgrounds.push(`url('${imagePath(unref(firstImageName), 512)}')`)
  backgrounds.push(`url('${imagePath(unref(firstImageName), 128)}')`)

  return backgrounds.join(', ')
})
```

- [ ] **Step 2: Commit**

```bash
git add app/components/item/card/ItemCard.vue
git commit -m "refactor: ItemCard uses imagePath with explicit sizes"
```

---

### Task 7: Update ImageAndAvatar to accept imageName

**Files:**
- Modify: `app/components/ImageAndAvatar.vue:1-19`

- [ ] **Step 1: Replace props to accept imageName**

In `ImageAndAvatar.vue`, replace the `<script setup>` block:

```vue
<script setup lang="ts">
// TODO query reduced image size

const props = defineProps<{
  image: string | null
  avatar: string | null
}>()

const { image, avatar } = toRefs(props)
</script>
```

with:

```vue
<script setup lang="ts">
const props = defineProps<{
  imageName: string | null
  avatar: string | null
}>()

const { imageName, avatar } = toRefs(props)

const image = computed(() => {
  const name = unref(imageName)
  return name ? imagePath(name, 256) : null
})
</script>
```

The template stays unchanged — it already uses `:src="image"` which now resolves from the computed.

- [ ] **Step 2: Commit**

```bash
git add app/components/ImageAndAvatar.vue
git commit -m "refactor: ImageAndAvatar accepts imageName prop, builds URL internally"
```

---

### Task 8: Update consumers of ImageAndAvatar and useItemFirstImage

**Files:**
- Modify: `app/components/chat/ChatSlab.vue:14-16, 28`
- Modify: `app/components/loan/LoanSlab.vue:16, 42`
- Modify: `app/components/loan/LoanRequestSlab.vue:15`

- [ ] **Step 1: Update ChatSlab**

In `ChatSlab.vue`, replace:

```ts
const { firstImagePath: itemImage } = useItemFirstImage(
  computed(() => unref(chat).item),
)
```

with:

```ts
const { firstImageName: itemImageName } = useItemFirstImage(
  computed(() => unref(chat).item),
)
```

And in the template, replace:

```vue
        :image="itemImage"
```

with:

```vue
        :image-name="itemImageName"
```

- [ ] **Step 2: Update LoanSlab**

In `LoanSlab.vue`, replace:

```ts
const { firstImagePath: itemImage } = useItemFirstImage(() => unref(loan).item)
```

with:

```ts
const { firstImageName: itemImageName } = useItemFirstImage(() => unref(loan).item)
```

And in the template, replace:

```vue
        :image="itemImage"
```

with:

```vue
        :image-name="itemImageName"
```

- [ ] **Step 3: Update LoanRequestSlab**

In `LoanRequestSlab.vue`, remove this unused line entirely:

```ts
const { firstImagePath: itemImage } = useItemFirstImage(() => unref(loanRequest).item)
```

It's never referenced in the template (the component uses `stateIcon` instead).

- [ ] **Step 4: Commit**

```bash
git add app/components/chat/ChatSlab.vue app/components/loan/LoanSlab.vue app/components/loan/LoanRequestSlab.vue
git commit -m "refactor: update ImageAndAvatar consumers to pass imageName"
```

---

### Task 9: Update ItemEditionForm

**Files:**
- Modify: `app/components/item/ItemEditionForm.vue:56`

- [ ] **Step 1: Use explicit size for studio image loading**

In `ItemEditionForm.vue`, replace:

```ts
    studioImages.value = _item.image_names.map((name: string) => useStudioImage(imagePath(name), { crop: 'center', maxSize: 1024 }))
```

with:

```ts
    studioImages.value = _item.image_names.map((name: string) => useStudioImage(imagePath(name, 1024), { crop: 'center', maxSize: 1024 }))
```

- [ ] **Step 2: Commit**

```bash
git add app/components/item/ItemEditionForm.vue
git commit -m "refactor: ItemEditionForm uses explicit image size"
```

---

### Task 10: Verify build

- [ ] **Step 1: Run type check**

```bash
npx nuxi typecheck
```

Expected: no type errors

- [ ] **Step 2: Run dev server and smoke test**

```bash
npx nuxi dev
```

Verify: item cards display images, image gallery works, chat/loan slabs show thumbnails.
