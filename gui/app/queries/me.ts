export function useMeQuery() {
  const { $api } = useNuxtApp()

  return useQueryWithAuth({
    key: ['me'],
    query: () => $api('/v1/me'),
    refetchOnMount: false,
  })
}

export function useMeItemsListQuery() {
  return useApiPaginatedQuery('/v1/me/items', {
    key: ['item', 'items', 'me'],
  })
}
