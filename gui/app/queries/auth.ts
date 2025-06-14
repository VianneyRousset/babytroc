export function useAuthAccountNameAvailableQuery(name: MaybeRefOrGetter<string>) {
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

export function useAuthAccountEmailAvailableQuery(email: MaybeRefOrGetter<string>) {
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
