/**
 * Mirrors the route query parameters to usable reactive values.
 **/
export function useMirrorItemQueryParamsAndRouteQueryParams(): {
  queryParams: Ref<ItemQueryParams>
} {
  const route = useRoute()
  const router = useRouter()

  return {
    queryParams: computed<ItemQueryParams>({
      get: () => {
        const _query = route.query
        return {
          cwm: typeof _query.cwm === 'string' && !isNaN(parseInt(_query.cwm)) ? parseInt(_query.cwm) : undefined,
          cid: typeof _query.cid === 'string' && !isNaN(parseInt(_query.cid)) ? parseInt(_query.cid) : undefined,
          mo: typeof _query.mo === 'string' ? _query.mo : undefined,
          av: typeof _query.av === 'string' && Object.values(ItemQueryAvailability).includes(_query.av as ItemQueryAvailabilityType)
            ? (_query.av as ItemQueryAvailabilityType)
            : undefined,
          reg: _query.reg ? getQueryParamAsArray(_query, 'reg').map(Number.parseInt) : undefined,
          n: typeof _query.n === 'string' && !isNaN(parseInt(_query.n)) ? parseInt(_query.n) : undefined,
          q: _query.q ? getQueryParamAsArray(_query, 'q') : undefined,
        }
      },
      set: (queryParams: ItemQueryParams) => router.replace({ query: queryParams }),
    }),
  }
}

export type ItemFilters = {
  words: string
  available: boolean
  unavailable: boolean
  targetedAge: AgeRange
  regions: Set<number>
}

/**
 * Expose filters for items and utils.
 *
 * filters regroups all the values of the filters
 * isDefault is only true if all filters are set to theirs default value.
 * reset sets all filters to their default value.
 * loadFiltersFromQueryParams loads filters value from item query params.
 * dumpFiltersAsQueryParams returns the item query params from the current filters.
 **/
export function useItemFilters(): {
  filters: Ref<ItemFilters>
  isDefault: Ref<boolean>
  reset: () => void
  loadFiltersFromQueryParams: (queryParams: ItemQueryParams) => void
  dumpFiltersAsQueryParams: () => ItemQueryParams
} {
  const filters = ref<ItemFilters>({
    words: '',
    available: true,
    unavailable: false,
    targetedAge: [0, null],
    regions: new Set<number>(),
  })

  const isDefault = computed<boolean>(() => {
    const { words, available, unavailable, targetedAge, regions } = unref(filters)
    return (
      words.trim().length === 0
      && available && !unavailable
      && targetedAge[0] === 0 && targetedAge[1] === null
      && regions.size === 0
    )
  })

  const reset = () => loadFiltersFromQueryParams({})

  function loadFiltersFromQueryParams(queryParams: ItemQueryParams) {
    filters.value = {
      words: queryParams.q?.join(' ') ?? '',
      available: queryParams.av !== ItemQueryAvailability.no,
      unavailable: queryParams.av !== ItemQueryAvailability.yes,
      targetedAge: string2range(queryParams.mo ?? '0-'),
      regions: new Set(queryParams.reg ?? []),
    }
  }

  function dumpFiltersAsQueryParams(): ItemQueryParams {
    const { words, available, unavailable, targetedAge, regions } = unref(filters)
    return {
      q: words.trim().length > 0 ? words.split(' ').filter((w: string) => w.length > 0) : undefined,
      av: (available
        ? (unavailable ? ItemQueryAvailability.all : undefined)
        : (unavailable ? ItemQueryAvailability.no : undefined)),
      mo: ((targetedAge[0] !== 0 && targetedAge[1] !== null)
        ? range2string(targetedAge)
        : undefined),
      reg: regions.size > 0 ? [...regions] : undefined,
    }
  }

  return {
    filters,
    isDefault,
    reset,
    loadFiltersFromQueryParams,
    dumpFiltersAsQueryParams,
  }
}
