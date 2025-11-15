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
      queryCache.invalidateQueries({ predicate: entry => entry.key.includes('saved') })
      queryCache.invalidateQueries({ predicate: entry => entry.key.includes(`item-${toValue(itemId)}`) })
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
      queryCache.invalidateQueries({ predicate: entry => entry.key.includes('saved') })
      queryCache.invalidateQueries({ predicate: entry => entry.key.includes(`item-${toValue(itemId)}`) })
    },
  })
}
