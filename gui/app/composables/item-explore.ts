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
  const stop = watchEffect(() => {
    if (!isEqual(unref(storeQueryParams), unref(routeQueryParams)))
      queryParams.value = unref(storeQueryParams) ?? unref(routeQueryParams)
  })

  tryOnUnmounted(stop)

  return { queryParams }
}

/**
 * List of all items for item explore
 **/
export function useItemExplore({ queryParams }: { queryParams: Ref<ItemQueryParams> }) {
  const { data: items, ...query } = useApiPaginatedQuery(
    '/v1/items',
    {
      key: ['item', 'explore'],
      query: queryParams,
    },
  )

  return { items, ...query }
}
