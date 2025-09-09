import { isEqual } from 'lodash'

/**
 * Item query params for item explore that ensures sync between store and route
 **/
export function useItemExploreQueryParams(): { queryParams: Ref<ItemQueryParams> } {
  // query params in store
  const { queryParams: storeQueryParams } = storeToRefs(useItemExploreStore())

  // query params in route
  const { queryParams: routeQueryParams } = useRouteItemQueryParams()

  const queryParams = computed<ItemQueryParams>({
    get: () => unref(storeQueryParams) ?? unref(routeQueryParams),
    set: (qp) => {
      storeQueryParams.value = qp
      routeQueryParams.value = qp
    },
  })

  // ensure store and route query params are always synced
  watchEffect(() => {
    if (!isEqual(unref(storeQueryParams), unref(routeQueryParams)))
      queryParams.value = unref(storeQueryParams) ?? unref(routeQueryParams)
  })

  return { queryParams }
}

/**
 * List of all items for item explore
 **/
export function useItemExplore({ queryParams }: { queryParams: Ref<ItemQueryParams> }): {
  items: Ref<Array<ItemPreview>>
  queryParams: Ref<ItemQueryParams>
  error: Ref<boolean>
  loading: Ref<boolean>
  loadMore: () => void
  scrollY: Ref<number>
} {
  const {
    data: pages,
    loadMore,
    asyncStatus,
    status,
  } = useItemsListQuery(queryParams)

  const items = computed<Array<ItemPreview>>(() => unref(pages).items ?? [])
  const error = computed<boolean>(() => unref(status) === 'error')
  const loading = computed<boolean>(() => unref(asyncStatus) === 'loading')

  // fixes few bugs by loading more items when `items` is empty
  watch(items, _items => _items.length === 0 && loadMore())

  // query params in store
  const { scrollY } = storeToRefs(useItemExploreStore())
  const { y } = useScroll(window)

  watch(y, newY => (scrollY.value = newY))

  return {
    items,
    error,
    loading,
    queryParams,
    loadMore: async () => {
      if (!unref(pages).end && !unref(error) && !unref(loading))
        await loadMore()
    },
    scrollY,
  }
}
