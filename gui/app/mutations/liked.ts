export function useLikeItemMutation(itemId: MaybeRefOrGetter<number>) {
  const { $api } = useNuxtApp()
  const queryCache = useQueryCache()

  return useMutation({
    key: () => ['item', 'like', toValue(itemId)],
    mutation: () => $api('/v1/me/liked/{item_id}', {
      method: 'POST',
      path: {
        item_id: toValue(itemId),
      },
    }),
    onSettled: (_data, _error) => {
      queryCache.invalidateQueries({ key: ['item', toValue(itemId)] })
    },
  })
}

export function useUnlikeItemMutation(itemId: MaybeRefOrGetter<number>) {
  const { $api } = useNuxtApp()
  const queryCache = useQueryCache()

  return useMutation({
    key: () => ['item', 'like', toValue(itemId)],
    mutation: () => $api('/v1/me/liked/{item_id}', {
      method: 'DELETE',
      path: {
        item_id: toValue(itemId),
      },
    }),
    onSettled: (_data, _error) => {
      queryCache.invalidateQueries({ key: ['item', toValue(itemId)] })
    },
  })
}
