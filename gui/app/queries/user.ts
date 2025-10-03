import { useQuery } from '@pinia/colada'

export function useUserQuery(userId: MaybeRefOrGetter<number>) {
  const { $api } = useNuxtApp()

  return useQuery({
    key: () => ['user', toValue(userId)],
    query: () =>
      $api('/v1/users/{user_id}', {
        path: {
          user_id: toValue(userId),
        },
      }),
  })
}
