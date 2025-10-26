export function useLogin() {
  const { $api } = useNuxtApp()
  const queryCache = useQueryCache()

  const { mutateAsync: login, ...mutation } = useMutation({
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

  return { login, ...mutation }
}
