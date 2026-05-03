export function useSaveItemMutation(itemId: MaybeRefOrGetter<number>) {
  const { $api } = useNuxtApp()
  const queryCache = useQueryCache()

  return useMutation({
    mutation: () => {
      return $api('/v1/me/saved/{item_id}', {
        method: 'POST',
        path: {
          item_id: toValue(itemId),
        },
      })
    },
    onSettled: () => {
      queryCache.invalidateQueries({ key: ['me', 'item', 'items', 'saved'] }, 'all')
      queryCache.invalidateQueries({ predicate: entry => entry.key.includes(`item-${toValue(itemId)}`) }, 'all')
    },
  })
}

export function useUnsaveItemMutation(itemId: MaybeRefOrGetter<number>) {
  const { $api } = useNuxtApp()
  const queryCache = useQueryCache()

  return useMutation({
    mutation: () => {
      return $api('/v1/me/saved/{item_id}', {
        method: 'DELETE',
        path: {
          item_id: toValue(itemId),
        },
      })
    },
    onSettled: () => {
      queryCache.invalidateQueries({ key: ['me', 'item', 'items', 'saved'] }, 'all')
      queryCache.invalidateQueries({ predicate: entry => entry.key.includes(`item-${toValue(itemId)}`) }, 'all')
    },
  })
}
