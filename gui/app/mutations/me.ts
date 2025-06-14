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
