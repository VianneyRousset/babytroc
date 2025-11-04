/**
 * `touched` becomes and stays true if `value` changed.
 **/
export function useTouched<T extends string | number | undefined | null>(
  value: MaybeRefOrGetter<T>,
  initialValue?: T,
): Ref<boolean> {
  const touched = ref(false)
  const _initialValue = initialValue ?? toValue(value)

  const stop = watch(() => toValue(value), (v) => {
    if (v != _initialValue)
      touched.value = true
  }, { immediate: true })

  tryOnUnmounted(stop)

  return touched
}
