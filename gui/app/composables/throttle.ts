import { isEqual } from 'lodash'

export function useThrottle<T>(
  value: MaybeRefOrGetter<T>,
  time: MaybeRefOrGetter<number>,
): { value: Ref<T>, synced: Ref<boolean> } {
  const synced = ref(true)
  const result = ref<T>(toValue(value)) as Ref<T>

  let timeout = null as null | ReturnType<typeof setTimeout>

  const stop = watch(() => toValue(value), (v) => {
    if (isEqual(v, unref(result)))
      return

    synced.value = false

    if (timeout) clearTimeout(timeout)

    timeout = setTimeout(
      () => {
        result.value = v
        synced.value = true
      },
      toValue(time),
    )
  })

  onScopeDispose(stop)

  return {
    synced,
    value: result,
  }
}
