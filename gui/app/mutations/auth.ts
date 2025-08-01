export const useLoginMutation = defineMutation(() => {
  const { $api } = useNuxtApp()
  const queryCache = useQueryCache()

  return useMutation({
    mutation: (ctx: { username: string, password: string }) => {
      // create form data
      const formData = new FormData()
      formData.append('grant_type', 'password')
      formData.append('username', ctx.username)
      formData.append('password', ctx.password)

      return $api('/v1/auth/login', {
        method: 'POST',
        // @ts-expect-error: cannot type FormData
        body: formData,
      })
    },

    onSettled: () => {
      queryCache.invalidateQueries({ key: ['me'] })
      queryCache.invalidateQueries({ key: ['auth'] })
    },

    onSuccess: () => {
      localStorage.setItem('auth-session', 'true')
    },
  })
})

export const useLogoutMutation = defineMutation(() => {
  const { $api, $toast } = useNuxtApp()
  const queryCache = useQueryCache()

  return useMutation({
    mutation: () => {
      return $api('/v1/auth/logout', {
        method: 'POST',
      })
    },

    onSettled: () => {
      queryCache.invalidateQueries({ key: ['me'] })
      queryCache.invalidateQueries({ key: ['auth'], exact: true })
    },

    onSuccess: () => {
      localStorage.removeItem('auth-session')
    },

    onError: () => $toast('Échec de la déconnection.'),
  })
})

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
