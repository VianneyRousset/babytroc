export function useCreateAccount(options?: { onSuccess?: () => void }) {
  const { $api } = useNuxtApp()

  const { mutateAsync: createAccount, ...mutation } = useMutation({
    mutation: (context: UserCreate) => {
      return $api('/v1/auth/new', {
        method: 'POST',
        body: context,
      })
    },
    onSuccess: () => options?.onSuccess && options.onSuccess(),
  })

  return { createAccount, ...mutation }
}
