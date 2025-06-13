export function useAuthAccountNameAvailable(name: MaybeRefOrGetter<string>) {
  const { $api } = useNuxtApp()

  return useQuery({
    key: () => ['auth', 'available-account-name', toValue(name)],
    query: () => $api('/v1/auth/available', {
      query: {
        name: toValue(name),
      },
    }),
  })
}

export function useAuthAccountEmailAvailable(email: MaybeRefOrGetter<string>) {
  const { $api } = useNuxtApp()

  return useQuery({
    key: () => ['auth', 'available-account-email', toValue(email)],
    query: () =>
      $api('/v1/auth/available', {
        query: {
          email: toValue(email),
        },
      }),
  })
}
