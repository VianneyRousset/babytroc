import type { FetchError } from 'ofetch'

export function useAccountNameValidity(
  name: MaybeRefOrGetter<string>,
  touched?: Ref<boolean>,
) {
  // delayed propagation of the name
  const { value: throttledName } = useThrottle(name, 1000)

  // retrieve user name avability from API
  const {
    available: nameAvailable,
    isLoading: nameAvailableIsLoading,
    error: nameAvailableError,
  } = useAccountNameAvailable(throttledName)

  return defineValidityFunction<string>(
    (_name) => {
      // validity pattern (unicode letters with ' ' and '-' not at the ends)
      const validCharactersRegex = /^\p{L}[\p{L} -]+\p{L}$/u
      const _error = unref(nameAvailableError) as FetchError | undefined
      if (_name === '') return 'Veuillez spécifier un pseudonyme'
      if (_name.length < 3) return 'Pseudonyme trop court'
      if (_name.length > 30) return 'Pseudonyme trop long'
      if (!validCharactersRegex.test(_name) || _error?.status === 400) return 'Pseudonyme invalide'
      if (_error != null) return 'Une erreur s\'est produite'
      if (unref(nameAvailable) === false) return 'Pseudonyme est déjà utilisé'
      return undefined
    }, {
      pending: nameAvailableIsLoading,
    },
  )(name, touched)
}

export function useAccountEmailValidity(
  email: MaybeRefOrGetter<string>,
  touched?: Ref<boolean>,
) {
  // delayed propagation of the email
  const { value: throttledEmail } = useThrottle(email, 1000)

  // retrieve user email avability from API
  const {
    available: emailAvailable,
    isLoading: emailAvailableIsLoading,
    error: emailAvailableError,
  } = useAccountEmailAvailable(throttledEmail)

  return defineValidityFunction<string>(
    (_email) => {
      const _error = unref(emailAvailableError) as FetchError | undefined
      if (_email === '') return 'Veuillez spécifier une adresse email'
      if (_error?.status === 400) return 'Adresse email invalide'
      if (_error != null) return 'Une erreur s\'est produite'
      if (unref(emailAvailable) === false) return 'Addresse mail est déjà utilisé'
      return undefined
    }, {
      pending: emailAvailableIsLoading,
    },
  )(email, touched)
}

export const useAccountPasswordValidity = defineValidityFunction<string>((_password) => {
  // validity pattern
  const digitPattern = /[0-9]/
  if (_password === '') return 'Veuillez spécifier un mot de passe'
  if (_password.length < 7) return 'Le mot de passe doit avoir au moins 7 caractères'
  if (_password.toLowerCase() === _password || _password.toUpperCase() === _password || !digitPattern.test(_password))
    return 'Le mot de passe doit contenir des minuscules et des majuscules ainsi qu\'au moins un chiffre'
  return undefined
})
