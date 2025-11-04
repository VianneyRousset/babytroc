import type { AsyncDataRequestStatus as AsyncStatus } from '#app'
import type { FetchError } from 'ofetch'

export function useAccountNameValidity(
  name: MaybeRefOrGetter<string>,
) {
  const { value: touched } = useThrottle(useTouched(name, ''), 1000)

  // validity pattern (unicode letters with ' ' and '-' not at the ends)
  const validCharactersRegex = /^\p{L}[\p{L} -]+\p{L}$/u

  // delayed propagation of the cleaned name
  const { value: throttledName, synced: throttledNameSynced } = useThrottle(name, 500)

  // retrieve user name avability from API
  const {
    available: nameAvailable,
    isLoading: nameAvailableIsLoading,
    error: nameAvailableError,
  } = useAccountNameAvailable(throttledName)

  // compute error message
  const error = computed<string | undefined>(() => {
    const _name = unref(throttledName)
    const _error = unref(nameAvailableError) as FetchError | undefined

    if (_name === '') return 'Veuillez spécifier un pseudonyme'
    if (_name.length < 3) return 'Pseudonyme trop court'
    if (_name.length > 30) return 'Pseudonyme trop long'
    if (!validCharactersRegex.test(_name) || _error?.status === 400) return 'Pseudonyme invalide'
    if (_error != null) return 'Une erreur s\'est produite'
    if (unref(nameAvailable) === false) return 'Pseudonyme est déjà utilisé'
    return undefined
  })

  const status = computed<AsyncStatus>(() => {
    if (unref(touched) === false) return 'idle'
    if (unref(throttledNameSynced) === false || unref(nameAvailableIsLoading)) return 'pending'
    if (unref(error) != null) return 'error'
    return 'success'
  })

  return { status, error, touched }
}

export function useAccountEmailValidity(
  email: MaybeRefOrGetter<string>,
) {
  const { value: touched } = useThrottle(useTouched(email, ''), 1000)

  // delayed propagation of the cleaned email
  const { value: throttledEmail, synced: throttledEmailSynced } = useThrottle(email, 500)

  // retrieve user email avAsyncDataRequestStatusailability from API
  const {
    available: emailAvailable,
    isLoading: emailAvailableIsLoading,
    error: emailAvailableError,
  } = useAccountEmailAvailable(throttledEmail)

  // compute error message
  const error = computed<string | undefined>(() => {
    const _email = unref(throttledEmail)
    const _error = unref(emailAvailableError) as FetchError | undefined

    if (_email === '') return 'Veuillez spécifier une adresse email'
    if (_error?.status === 400) return 'Adresse email invalide'
    if (_error != null) return 'Une erreur s\'est produite'
    if (unref(emailAvailable) === false) return 'Addresse mail est déjà utilisé'
    return undefined
  })

  const status = computed<AsyncStatus>(() => {
    if (unref(touched) === false) return 'idle'
    if (unref(throttledEmailSynced) === false || unref(emailAvailableIsLoading)) return 'pending'
    if (unref(error) != null) return 'error'
    return 'success'
  })

  return { status, error, touched }
}

export function useAccountPasswordValidity(
  password: MaybeRefOrGetter<string>,
) {
  const { value: touched } = useThrottle(useTouched(password, ''), 1000)

  // validity pattern
  const digitPattern = /[0-9]/

  // delayed propagation of the cleaned email
  const { synced: throttledPasswordSynced } = useThrottle(computed(() => toValue(password)), 500)

  // compute error message
  const error = computed<string | undefined>(() => {
    const _password = toValue(password)

    if (_password === '') return 'Veuillez spécifier un mot de passe'
    if (_password.length < 7) return 'Le mot de passe doit avoir au moins 7 caractères'
    if (_password.toLowerCase() === _password || _password.toUpperCase() === _password || !digitPattern.test(_password))
      return 'Le mot de passe doit contenir des minuscules et des majuscules ainsi qu\'au moins un chiffre'
    return undefined
  })

  const status = computed<AsyncStatus>(() => {
    if (unref(touched) === false) return 'idle'
    if (unref(throttledPasswordSynced) === false) return 'pending'
    if (unref(error) != null) return 'error'
    return 'success'
  })

  return { status, error, touched }
}
