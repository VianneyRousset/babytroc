import { defineStore } from 'pinia'

export function useStudioImagesUploadStore(name: string) {
  const definition = defineStore(`studio-images-upload-${name}`, () => {
    const { $api } = useNuxtApp()

    // cached images dataUrl -> name map
    const cache = new Map<string, string | null>()

    const images = ref(Array<StudioImage>())

    async function ensureImageUpload(img: StudioImage) {
      const data = img.cropped

      if (data == null)
        throw new Error('Null image cropped data')

      if (cache.get(data) != null)
        return cache.get(data)

      const blob = await (await fetch(data)).blob()
      const file = new File([blob], 'name', {
        type: blob.type,
      })
      const form = new FormData()
      form.append('file', file)
      const resp = await $api('/v1/images', {
        method: 'POST',

        // @ts-expect-error: cannot type FormData
        body: form,
      })

      cache.set(data, resp.name)
      return resp.name
    }

    return {
      images,
      ...useAsyncData(
        () => `images-upload-${name} ${unref(images).map(img => img.cropped).join(' ')}`,
        () => Promise.all(unref(images).map(ensureImageUpload)),
      ),
    }
  })

  return definition()
}
