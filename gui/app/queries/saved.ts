/*
 * List of saved items.
 */
export function useSavedItemsListQuery() {
  return useApiPaginatedQuery('/v1/me/saved', {
    key: ['item', 'items', 'saved'],
  })
}
