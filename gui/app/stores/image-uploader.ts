import { defineStore } from 'pinia'
import { xxHash32 } from 'js-xxhash'

type AsyncStatus = 'pending' | 'error' | 'success'

type AsyncData<T> = {
  data: Ref<T>
  status: Ref<AsyncStatus>
}

function computeHash(data: string): string {
  const seed = 0
  return xxHash32(data, seed).toString(16)
}

export const useImageUploader = defineStore('image-uploader', () => {
  const { $api } = useNuxtApp()

  // cached images data hash -> AsyncState of imageName
  const cache = new Map<string, AsyncData<string | undefined>>()

  function ensure(data: string): AsyncData<string | undefined> {
    const hash = computeHash(data)
    const entry = unref(cache).get(hash)
    if (entry) return entry
    const { state, isLoading, error } = useAsyncState<string | undefined>(_upload(data), undefined)
    const status = computed(() => {
      if (unref(isLoading)) return 'pending'
      if (unref(error)) return 'error'
      return 'success'
    })
    const newEntry = { data: state, status }
    cache.set(hash, newEntry)
    return newEntry
  }

  function upload(data: MaybeRefOrGetter<string>): AsyncData<string | undefined> {
    const ret: AsyncData<string | undefined> = {
      data: ref<string | undefined>(undefined),
      status: ref<AsyncStatus>('pending'),
    }

    onScopeDispose(watchEffect(() => {
      const { data: _data, status } = ensure(toValue(data))
      ret.data.value = unref(_data)
      ret.status.value = unref(status)
    }))

    return ret
  }

  function uploadMany(data: MaybeRefOrGetter<Array<string>>): AsyncData<Array<string | undefined>> {
    const ret: AsyncData<Array<string | undefined>> = {
      data: ref<Array<string | undefined>>([]),
      status: ref<AsyncStatus>('pending'),
    }

    onScopeDispose(watchEffect(() => {
      const entries: Array<AsyncData<string | undefined>> = toValue(data).map(ensure)
      ret.data.value = entries.map(({ data }) => unref(data))
      ret.status.value = (
        entries.every(({ status }) => unref(status) === 'success')
          ? 'success'
          : entries.some(({ status }) => unref(status) === 'error')
            ? 'error'
            : 'pending'
      )
    }))

    return ret
  }

  async function _upload(
    data: string,
    signal?: AbortSignal,
  ): Promise<string> {
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

    return resp.name
  }

  return { upload, uploadMany }
})
