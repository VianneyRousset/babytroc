/**
 * `touched` becomes and stays true if `value` changed.
 **/
export function useTouched<T extends string | number | undefined | null>(value: MaybeRefOrGetter<T>): Ref<boolean> {
  const touched = ref(false)
  const initialValue = toValue(value)

  const stop = watch(() => toValue(value), (v) => {
    if (v != initialValue)
      touched.value = true
  })

  tryOnUnmounted(stop)

  return touched
}
