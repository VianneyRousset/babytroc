import type { AsyncDataRequestStatus as AsyncStatus } from '#app'

/* NEW */
export function useUser({ userId }: { userId: MaybeRefOrGetter<number> }) {
  const { data: user, ...query } = useApiQuery('/v1/users/{user_id}', {
    key: () => ['user', toValue(userId)],
    path: () => ({
      user_id: toValue(userId),
    }),
    refetchOnMount: false,
  })

  return { user, ...query }
}

/* OLD */
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

  // retrieve user name avability from API
  const {
    data: nameAvailability,
    asyncStatus: nameAvailabilityAsyncStatus,
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

    if (!validCharactersRegex.test(_name))
      return 'Pseudonyme non valide'

    if (unref(nameAvailability)?.available === false)
      return 'Pseudonyme est déjà utilisé'

    return undefined
  })

  const status = computed<AsyncStatus>(() => {
    if (toValue(_touched) === false)
      return 'idle'

    if (unref(throttledNameSynced) === false || unref(nameAvailabilityAsyncStatus) === 'loading')
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

export function useUserEmailValidity(
  email: MaybeRefOrGetter<string>,
  touched?: MaybeRefOrGetter<boolean>,
) {
  const _touched: MaybeRefOrGetter<boolean> = touched === undefined ? true : touched

  // email trimmed and without consecutive whitespaces
  const cleanedEmail = computed(() => avoidConsecutiveWhitespaces(toValue(email).trim()))

  // delayed propagation of the cleaned email
  const { value: throttledEmail, synced: throttledEmailSynced } = useThrottle(cleanedEmail, 500)

  // retrieve user email avAsyncDataRequestStatusailability from API
  const {
    data: emailAvailability,
    status: emailAvailabilityStatus,
    asyncStatus: emailAvailabilityAsyncStatus,
  } = useAuthAccountEmailAvailableQuery(throttledEmail)

  // compute error message
  const error = computed<string | undefined>(() => {
    const _email = unref(cleanedEmail)

    if (_email === '')
      return 'Veuillez spécifier une adresse email'

    if (unref(emailAvailabilityStatus) === 'error')
      return 'Adresse email invalide'

    if (unref(emailAvailability)?.available === false)
      return 'Addresse mail est déjà utilisé'

    return undefined
  })

  const status = computed<AsyncStatus>(() => {
    if (toValue(_touched) === false)
      return 'idle'

    if (unref(throttledEmailSynced) === false || unref(emailAvailabilityAsyncStatus) === 'loading')
      return 'pending'

    if (unref(error) != null)
      return 'error'

    return 'success'
  })

  return {
    email: cleanedEmail,
    status,
    error,
  }
}

export function useUserPasswordValidity(
  password: MaybeRefOrGetter<string>,
  touched?: MaybeRefOrGetter<boolean>,
) {
  const _touched: MaybeRefOrGetter<boolean> = touched === undefined ? true : touched

  // validity pattern
  const digitPattern = /[0-9]/

  // delayed propagation of the cleaned email
  const { synced: throttledPasswordSynced } = useThrottle(computed(() => toValue(password)), 500)

  // compute error message
  const error = computed<string | undefined>(() => {
    const _password = toValue(password)

    if (_password === '')
      return 'Veuillez spécifier un mot de passe'

    if (_password.length < 7)
      return 'Le mot de passe doit avoir au moins 7 caractères'

    if (_password.toLowerCase() === _password || _password.toUpperCase() === _password || !digitPattern.test(_password))
      return 'Le mot de passe doit contenir des minuscules et des majuscules ainsi qu\'au moins un chiffre'

    return undefined
  })

  const status = computed<AsyncStatus>(() => {
    if (toValue(_touched) === false)
      return 'idle'

    if (unref(throttledPasswordSynced) === false)
      return 'pending'

    if (unref(error) != null)
      return 'error'

    return 'success'
  })

  return {
    password,
    status,
    error,
  }
}
