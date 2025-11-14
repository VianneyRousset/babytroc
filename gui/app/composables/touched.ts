import { isEqual } from 'lodash'

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
  const _compare = compare ?? isEqual

  const stop = watch(() => toValue(value), (v) => {
    if (!_compare(v, _initialValue) && unref(touched) === false)
      touched.value = true
  }, { immediate: true })

  tryOnUnmounted(stop)

  return touched
}
