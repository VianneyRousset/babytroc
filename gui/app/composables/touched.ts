/**
 * `touched` becomes and stays true if `value` changed.
 **/
export function useTouched<T>(
  value: MaybeRefOrGetter<T>,
  initialValue?: T,
  compare?: (a: NoInfer<T>, b: NoInfer<T>) => boolean,
): Ref<boolean> {
  const touched = ref(false)
  const _initialValue = initialValue ?? toValue(value)
  const _compare = compare ?? ((a, b) => a === b)

  const stop = watch(() => toValue(value), (v) => {
    if (!_compare(v, _initialValue))
      touched.value = true
  }, { immediate: true })

  tryOnUnmounted(stop)

  return touched
}
