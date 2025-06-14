import type { AsyncDataRequestStatus as AsyncStatus } from '#app'

export function useUserNameValidity(
  name: MaybeRefOrGetter<string>,
  touched?: MaybeRefOrGetter<boolean>,
) {
  const _touched: MaybeRefOrGetter<boolean> = touched === undefined ? true : touched

  // validity pattern (unicode letters with ' ' and '-' not at the ends)
  const validCharactersRegex = /^\p{L}[\p{L} -]+\p{L}$/u

  // name trimmed and without consecutive whitespaces
  const cleanedName = computed(() => avoidConsecutiveWhitespaces(toValue(name).trim()))

  // delayed propagation of the cleaned name
  const { value: throttledName, synced: throttledNameSynced } = useThrottle(cleanedName, 500)

  // retrieve user name avAsyncDataRequestStatusailability from API
  const {
    data: nameAvailability,
    asyncStatus: nameAvailabilityStatus,
  } = useAuthAccountNameAvailableQuery(throttledName)

  // compute error message
  const error = computed<string | undefined>(() => {
    const _name = unref(cleanedName)

    if (_name === '')
      return 'Veuillez spécifier un pseudonyme'

    if (_name.length < 3)
      return 'Pseudonyme trop court'

    if (_name.length > 30)
      return 'Pseudonyme trop long'

    if (unref(nameAvailability)?.available === false)
      return 'Pseudonyme est déjà utilisé'

    if (!validCharactersRegex.test(_name))
      return 'Pseudonyme non valide'

    return undefined
  })

  const status = computed<AsyncStatus>(() => {
    if (toValue(_touched) === false)
      return 'idle'

    if (unref(throttledNameSynced) === false || unref(nameAvailabilityStatus) === 'loading')
      return 'pending'

    if (unref(error) != null)
      return 'error'

    return 'success'
  })

  return {
    name: cleanedName,
    status,
    error,
  }
}
