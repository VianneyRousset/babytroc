import type { FetchError } from 'ofetch'

export function useAskPasswordReset(
  email: MaybeRefOrGetter<string>,
) {
  const { $api } = useNuxtApp()
  const { value: touched } = useThrottle(useTouched(email), 1000)

  // email trimmed and without consecutive whitespaces
  const cleanedEmail = computed(() => avoidConsecutiveWhitespaces(toValue(email).trim()))

  // ask password reset mutation
  const { mutateAsync: askPasswordReset, ...mutation } = useMutation({
    mutation: () => {
      return $api('/v1/auth/reset-password', {
        method: 'POST',
        body: {
          email: unref(cleanedEmail),
        },
      })
    },
  })

  // delayed propagation of the cleaned email
  const { value: throttledEmail, synced: throttledEmailSynced } = useThrottle(cleanedEmail, 500)

  // retrieve user email availability from API
  const {
    available: emailAvailable,
    isLoading: emailAvailableIsLoading,
    error: emailAvailableError,
  } = useAccountEmailAvailable(throttledEmail)

  // validation error message
  const validationError = computed<string | undefined>(() => {
    const _email = unref(cleanedEmail)
    const _error = unref(emailAvailableError) as FetchError | undefined

    if (_email === '') return 'Veuillez spécifier une adresse email'
    if (_error?.status === 400) return 'Adresse email invalide'
    if (_error != null) return 'Une erreur s\'est produite'
    if (unref(emailAvailable) === true) return 'Cette adresse n\'existe pas'
    return undefined
  })

  const validationStatus = computed<'idle' | 'pending' | 'error' | 'success'>(() => {
    if (unref(touched) === false) return 'idle'
    if (unref(throttledEmailSynced) === false || unref(emailAvailableIsLoading)) return 'pending'
    if (unref(validationError) != null) return 'error'
    return 'success'
  })

  return {
    askPasswordReset,
    ...mutation,
    validationStatus,
    validationError,
  }
}
