import { useInfiniteQuery } from '@pinia/colada'
import { parseLinkHeader } from '@web3-storage/parse-link-header'
import { pickBy, clone } from 'lodash'
import type { paths } from '#build/types/open-fetch/schemas/api'
import type { UseInfiniteQueryOptions, UseInfiniteQueryReturn } from '@pinia/colada'
import type { ApiFetchOptions, PathWithGetOperationData } from './query'

// Available API paginated query paths (retuns an array and has query params)
type ApiPaginatedQueryPaths = {
  [K in keyof paths as paths[K] extends PathWithGetOperationData<Array<unknown>>
    ? paths[K] extends PathWithGetOperationQueryParams<never> ? never : K
    : never]: paths[K]
}

// Options type
type ApiPaginatedQueryOptions<TPath, TData, TError, TQueryParams> = (
  ApiFetchOptions<TPath>
  & Omit<UseInfiniteQueryOptions<TData, TError, TData | undefined, Array<ApiPage<TData, TQueryParams>>>, 'query' | 'initialPage' | 'merge'>
)

// Return type (rename 'data' to 'pages' to avoid confusion)
type ApiPaginatedQueryReturn<TData, TError, TQueryParams> = Omit<UseInfiniteQueryReturn<Array<ApiPage<TData, TQueryParams>>, TError>, 'data'>
  & {
    pages: Ref<Array<ApiPage<TData, TQueryParams>>>
    data: Ref<Array<TData>>
    end: Ref<boolean>
    loadMore: () => Promise<void>
  }

// API page
type ApiPage<TData, TQuery> = {
  data: Array<TData>
  cursor?: TQuery
  end: boolean
}

export function useApiPaginatedQuery<
  TReq extends keyof ApiPaginatedQueryPaths,
  TData = FetchResponseDataArray<ApiPaginatedQueryPaths[TReq]>,
  TQueryParams = FetchQueryParams<ApiPaginatedQueryPaths[TReq]>,
>(
  url: TReq,
  options: NoInfer<ApiPaginatedQueryOptions<ApiPaginatedQueryPaths[TReq], TData, Error, TQueryParams>>,
): NoInfer<ApiPaginatedQueryReturn<TData, Error, TQueryParams>> {
  const queryParams = computed(() => pickBy(unref(options.query), v => v != null) as TQueryParams)
  const key = computed(() => {
    const _key = toValue(options.key)
    return Array.isArray(_key) ? [..._key, unref(queryParams)] : [_key, unref(queryParams)]
  })
  const { $api } = useNuxtApp()

  let cursor: TQueryParams | undefined = undefined

  const { data: pages, error, isLoading, loadMore: _loadMore, ...query } = useInfiniteQuery<Array<TData>, Error, Array<ApiPage<TData, TQueryParams>>>({

    ...options,

    key,

    initialPage: Array<ApiPage<TData, TQueryParams>>(),

    // @ts-expect-error avoid typing error
    query: () => $api(url, {
      query: {
        ...unref(queryParams),
        ...cursor,
      },
      header: toValue(options.header),
      path: toValue(options.path),
      cookie: toValue(options.cookie),

      onResponse: async ({
        response: { ok, headers },
      }: { response: { ok: boolean, headers: Headers } }) => {
        if (!ok) return
        cursor = extractNextQueryParamsFromHeaders(headers) as TQueryParams
      },
    }),

    merge: (pages: Array<ApiPage<TData, TQueryParams>>, newData: Array<TData>) => ([
      ...pages,
      {
        data: newData,
        cursor: clone(cursor),
        end: cursor == null,
      },
    ]),
  })

  const data = computed(() => unref(pages).flatMap(page => page.data))
  const end = computed(() => unref(pages).some(page => page.end))
  async function loadMore() {
    if (unref(error) != null || unref(end) || unref(isLoading))
      return
    await _loadMore()
  }

  return { pages, data, error, isLoading, end, loadMore, ...query }
}

export function extractNextQueryParamsFromHeaders(headers: Headers) {
  const linkHeader = parseLinkHeader(headers.get('link'))

  if (!linkHeader?.next)
    return undefined

  const { rel, url, ...query } = linkHeader.next
  return query
}

// Helpers
type PathWithGetOperationQueryParams<TQueryParams = unknown> = {
  get: {
    parameters: {
      query?: TQueryParams
    }
  }
}

type FetchResponseDataArray<TPath> = TPath extends PathWithGetOperationData<Array<infer D>> ? D : never
type FetchQueryParams<TPath> = TPath extends PathWithGetOperationQueryParams<infer Q> ? Q : never
