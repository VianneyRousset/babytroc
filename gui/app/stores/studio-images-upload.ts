import { defineStore } from 'pinia'

export function useStudioImagesUploadStore(name: string) {
  const definition = defineStore(`studio-images-upload-${name}`, () => {
    const { $api } = useNuxtApp()

    // cached images dataUrl -> name map
    const cache = new Map<string, string | null>()

    const images = ref(Array<StudioImage>())

    async function ensureImageUpload(
      image: StudioImage,
      signal?: AbortSignal,
    ): Promise<string> {
      const data: string | undefined = image.cropped

      if (data == null)
        throw new Error('Null image cropped data')

      const cachedData = cache.get(data)

      if (cachedData != null)
        return cachedData

      const blob = await (await fetch(data, { signal })).blob()
      const file = new File([blob], 'name', {
        type: blob.type,
      })
      const form = new FormData()
      form.append('file', file)
      const resp = await $api('/v1/images', {
        method: 'POST',

        // @ts-expect-error: cannot type FormData
        body: form,
        signal,
      })

      cache.set(data, resp.name)
      return resp.name
    }

    async function ensureAllImagesUpload(
      images: Array<StudioImage>,
      signal?: AbortSignal,
    ): Promise<Array<string>> {
      return Promise.all(images.map(img => ensureImageUpload(img, signal)))
    }

    function setImages(_images: Array<StudioImage>) {
      images.value = _images.map(img => img.copy())
    }

    return {
      images,
      setImages,
      ...useAsyncData<Array<string>>(
        () => `images-upload-${name} ${unref(images).map(img => img.cropped).join(' ')}`,
        () => ensureAllImagesUpload(unref(images)),
        {
          default: () => Array<string>(),
        },
      ),
    }
  })

  return definition()
}
