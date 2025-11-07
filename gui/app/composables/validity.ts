import type { AsyncDataRequestStatus as AsyncStatus } from '#app'

export type ValidityFunction<T> = (value: MaybeRefOrGetter<T>, touched?: Ref<boolean>) => ({
  status: Ref<AsyncStatus>
  error: Ref<string | undefined>
  touched: Ref<boolean>
})

export function defineValidityFunction<T>(
  errorFn: (value: NoInfer<T>) => string | undefined,
  options?: {
    throttle?: number
    initialValue?: T
    compare?: (a: NoInfer<T>, b: NoInfer<T>) => boolean
    pending?: MaybeRefOrGetter<boolean>
  },
): ValidityFunction<T> {
  return (
    value: MaybeRefOrGetter<T>,
    _touched?: Ref<boolean>,
  ) => {
    // throttled touched
    const { value: touched } = useThrottle(
      useTouched<T>(
        value,
        options?.initialValue,
        options?.compare,
      ),
      options?.throttle ?? 1000,
    )

    // throttled value
    const { value: throttledValue, synced } = useThrottle(value, options?.throttle ?? 1000)

    // sync with the given touched value if given
    if (_touched)
      syncRef(touched, _touched)

    // computed error message
    const error = computed(() => errorFn(toValue(throttledValue)))

    // status
    const status = computed<AsyncStatus>(() => {
      if (unref(touched) === false) return 'idle'
      if (unref(synced) === false || toValue(options?.pending) === true) return 'pending'
      if (unref(error) != null) return 'error'
      return 'success'
    })

    return { status, error, touched }
  }
}
