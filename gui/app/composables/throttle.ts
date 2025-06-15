export function useThrottle<T>(
  value: Ref<T>,
  time: MaybeRefOrGetter<number>,
): { value: Ref<T>, synced: Ref<boolean> } {
  const synced = ref(true)
  const result = ref<T>(unref(value)) as Ref<T>

  let timeout = null as null | ReturnType<typeof setTimeout>

  watch(value, (v) => {
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

  return {
    synced,
    value: result,
  }
}
