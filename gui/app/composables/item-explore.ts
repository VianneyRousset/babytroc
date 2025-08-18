export function useItemExplore({ queryParams }: { queryParams?: Ref<ItemQueryParams> }): {
  items: Ref<Array<ItemPreview>>
  queryParams: Ref<ItemQueryParams>
  error: Ref<boolean>
  loading: Ref<boolean>
  loadMore: () => void
  canLoadMore: Ref<boolean>
} {
  const {
    queryParams: _queryParams,
    data: pages,
    asyncStatus,
    status,
    loadMore,
  } = useItemsListQuery(queryParams)

  return {
    items: computed(() => unref(pages).data),
    queryParams: _queryParams,
    error: computed(() => unref(status) === 'error'),
    loading: computed(() => unref(asyncStatus) === 'loading'),
    loadMore,
    canLoadMore: computed(() => !unref(pages).end),
  }
}
