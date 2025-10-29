export function useCreateAccount() {
  const { $api } = useNuxtApp()

  const { mutateAsync: createAccount, ...mutation } = useMutation({
    mutation: (context: UserCreate) => {
      return $api('/v1/auth/new', {
        method: 'POST',
        body: context,
      })
    },
  })

  return { createAccount, ...mutation }
}
