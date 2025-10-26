export const useCreateAccountMutation = defineMutation(() => {
  const { $api } = useNuxtApp()

  return useMutation({
    mutation: (context: UserCreate) => {
      return $api('/v1/auth/new', {
        method: 'POST',
        body: context,
      })
    },
  })
})

export const useResendValidationEmailMutation = defineMutation(() => {
  const { $api } = useNuxtApp()

  return useMutation({
    mutation: () => {
      return $api('/v1/auth/resend-validation-email', {
        method: 'POST',
      })
    },
  })
})

export const useAskPasswordResetMutation = defineMutation(() => {
  const { $api } = useNuxtApp()
  return useMutation({
    mutation: (context: { email: string }) => {
      return $api('/v1/auth/reset-password', {
        method: 'POST',
        body: context,
      })
    },
  })
})

export const useValidateAccountMutation = defineMutation(() => {
  const { $api } = useNuxtApp()
  return useMutation({
    mutation: (context: { validation_code: string }) => {
      return $api('/v1/auth/validate/{validation_code}', {
        method: 'POST',
        path: context,
      })
    },
  })
})

export const useResetPasswordMutation = defineMutation(() => {
  const { $api } = useNuxtApp()
  return useMutation({
    mutation: (context: { authorizationCode: string, newPassword: string }) => {
      return $api('/v1/auth/reset-password/{authorization_code}', {
        method: 'POST',
        path: { authorization_code: context.authorizationCode },
        body: { password: context.newPassword },
      })
    },
  })
})
