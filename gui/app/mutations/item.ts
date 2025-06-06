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
      queryCache.invalidateQueries({ key: ['items'] })
    },
  })
})
