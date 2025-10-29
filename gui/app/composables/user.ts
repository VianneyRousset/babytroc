export function useUser({ userId }: { userId: MaybeRefOrGetter<number> }) {
  const { data: user, ...query } = useApiQuery('/v1/users/{user_id}', {
    key: () => ['user', toValue(userId)],
    path: () => ({
      user_id: toValue(userId),
    }),
    refetchOnMount: false,
  })

  return { user, ...query }
}
