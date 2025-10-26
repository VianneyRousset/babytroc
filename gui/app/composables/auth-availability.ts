export function useAccountNameAvailable(name: MaybeRefOrGetter<string>) {
  const { data: availability, ...query } = useApiQuery('/v1/auth/available', {
    key: () => ['auth', 'available-account-name', toValue(name)],
    query: () => ({
      name: toValue(name),
    }),
  })

  return {
    available: computed<boolean | undefined>(() => unref(availability)?.available),
    ...query,
  }
}

export function useAccountEmailAvailable(email: MaybeRefOrGetter<string>) {
  const { data: availability, ...query } = useApiQuery('/v1/auth/available', {
    key: () => ['auth', 'available-account-email', toValue(email)],
    query: () => ({
      email: toValue(email),
    }),
  })

  return {
    available: computed<boolean | undefined>(() => unref(availability)?.available),
    ...query,
  }
}
