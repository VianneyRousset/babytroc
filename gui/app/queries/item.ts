export const useItemExploreQuery = defineQuery(() => {
  const queryParams = ref<ItemQueryParams>({})

  const query = useApiPaginatedQuery(
    '/v1/items',
    {
      key: ['item', 'explore'],
      query: queryParams,
    },
  )

  return { ...query, queryParams }
})
