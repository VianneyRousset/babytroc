export const useCreateItemMutation = defineMutation(() => {
  const { $api } = useNuxtApp()
  const queryCache = useQueryCache()

  return useMutation({
    mutation: (context: ItemCreate) => {
      return $api('/v1/me/items', {
        method: 'POST',
        body: context,
      })
    },
    onSettled: (_data, _error, _vars) => {
      // TODO do not invalidate to much
      queryCache.invalidateQueries()
    },
  })
})

export function useUpdateItemMutation(itemId: MaybeRefOrGetter<number>) {
  const { $api } = useNuxtApp()
  const queryCache = useQueryCache()

  return useMutation({
    key: () => ['item', 'updaet', toValue(itemId)],
    mutation: (context: ItemUpdate) => $api('/v1/me/items/{item_id}', {
      method: 'POST',
      path: {
        item_id: toValue(itemId),
      },
      body: context,
    }),
    onSettled: (_data, _error) => {
      queryCache.invalidateQueries({ key: ['item', toValue(itemId)] })
      queryCache.invalidateQueries({ key: ['item', 'explore'] })
      queryCache.invalidateQueries({ key: ['item', 'me'] })
    },
  })
}
