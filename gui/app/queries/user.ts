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

export function useUserItemsListQuery(userId: MaybeRefOrGetter<number>) {
  return useApiPaginatedQuery('/v1/users/{user_id}/items', {
    key: () => ['item', 'user', `user${toValue(userId)}`],
    path: {
      user_id: toValue(userId),
    },
  })
}
