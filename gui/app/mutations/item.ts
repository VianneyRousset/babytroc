/*
 * Create item
 */
export const useCreateItemMutation = defineMutation(() => {
  const { $api } = useNuxtApp()
  const queryCache = useQueryCache()

  return useMutation({
    mutation: async (context: ItemCreate) => await $api('/v1/me/items', {
      method: 'POST',
      body: context,
    }),
    onSettled: () => {
      queryCache.invalidateQueries({ predicate: queryWithSubkey('items') })
    },
  })
})

/*
 * Update item
 */
export function useUpdateItemMutation(itemId: MaybeRefOrGetter<number>) {
  const { $api } = useNuxtApp()
  const queryCache = useQueryCache()

  return useMutation({
    key: () => ['item', 'update', toValue(itemId)],
    mutation: async (context: ItemUpdate) => await $api('/v1/me/items/{item_id}', {
      method: 'POST',
      path: {
        item_id: toValue(itemId),
      },
      body: context,
    }),
    onSettled: () => {
      queryCache.invalidateQueries({ predicate: queryWithSubkey('items') })
      queryCache.invalidateQueries({ predicate: queryWithSubkey(`item-${toValue(itemId)}`) })
    },
  })
}

/*
 * Delete item
 */
export function useDeleteItemMutation(itemId: MaybeRefOrGetter<number>) {
  const { $api } = useNuxtApp()
  const queryCache = useQueryCache()

  return useMutation({
    key: () => ['item', 'update', toValue(itemId)],
    mutation: async () => await $api('/v1/me/items/{item_id}', {
      method: 'DELETE',
      path: {
        item_id: toValue(itemId),
      },
    }),
    onSettled: () => {
      queryCache.invalidateQueries({ predicate: queryWithSubkey('items') })
      queryCache.invalidateQueries({ predicate: queryWithSubkey(`item-${toValue(itemId)}`) })
    },
  })
}
