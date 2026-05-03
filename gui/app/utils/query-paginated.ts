import { useInfiniteQuery } from '@pinia/colada'
import { parseLinkHeader } from '@web3-storage/parse-link-header'
import { pickBy } from 'lodash'
import type { paths } from '#build/types/open-fetch/schemas/api'
import type { UseInfiniteQueryOptions, UseInfiniteQueryReturn, UseInfiniteQueryData } from '@pinia/colada'
import type { ApiFetchOptions, PathWithGetOperationData } from './query'

// Available API paginated query paths (returns an array and has query params)
type ApiPaginatedQueryPaths = {
  [K in keyof paths as paths[K] extends PathWithGetOperationData<Array<unknown>>
    ? paths[K] extends PathWithGetOperationQueryParams<never> ? never : K
    : never]: paths[K]
}

// Cursor is the parsed query params from the Link header, or null when no more pages
type Cursor = Record<string, string> | null

// Options type
type ApiPaginatedQueryOptions<TPath, TData, TError> = (
  ApiFetchOptions<TPath>
  & Omit<UseInfiniteQueryOptions<Array<TData>, TError, Cursor, undefined>, 'query' | 'initialPageParam' | 'getNextPageParam'>
)

// Return type
export type ApiPaginatedQueryReturn<TData, TError> = {
    data: Ref<Array<TData>>
    pages: Ref<UseInfiniteQueryData<Array<TData>, Cursor> | undefined>
    error: Ref<TError | null>
    isLoading: Ref<boolean>
    end: Ref<boolean>
    loadMore: () => Promise<void>
  }

export function useApiPaginatedQuery<
  TReq extends keyof ApiPaginatedQueryPaths,
  TData = FetchResponseDataArray<ApiPaginatedQueryPaths[TReq]>,
  TQueryParams = FetchQueryParams<ApiPaginatedQueryPaths[TReq]>,
>(
  url: TReq,
  options: NoInfer<ApiPaginatedQueryOptions<ApiPaginatedQueryPaths[TReq], TData, Error>>,
): NoInfer<ApiPaginatedQueryReturn<TData, Error>> {
  const queryParams = computed(() => pickBy(unref(options.query), v => v != null) as TQueryParams)
  const key = computed(() => {
    const _key = toValue(options.key)
    return Array.isArray(_key) ? [..._key, toRaw(unref(queryParams))] : [_key, toRaw(unref(queryParams))]
  })
  const { $api } = useNuxtApp()

  // Track the next cursor per request (set in onResponse, read in getNextPageParam)
  let lastCursor: Cursor = null

  const { data: pages, loadNextPage, error, isLoading, ...query } = useInfiniteQuery<Array<TData>, Error, Cursor>({

    ...options,

    key,

    initialPageParam: null as Cursor,

    query: async ({ pageParam, signal }) => {
      const cursorParams = pageParam ?? {}
      lastCursor = null

      // @ts-expect-error complex open-fetch generic inference
      return await $api(url, {
        signal,
        query: {
          ...unref(queryParams),
          ...cursorParams,
        },
        header: toValue(options.header),
        path: toValue(options.path),
        cookie: toValue(options.cookie),

        onResponse: async ({
          response: { ok, headers },
        }: { response: { ok: boolean, headers: Headers } }) => {
          if (!ok) return
          lastCursor = extractNextCursorFromHeaders(headers)
        },
      })
    },

    getNextPageParam: () => lastCursor,
  })

  const data = computed(() => unref(pages)?.pages.flat() ?? [])
  const end = computed(() => {
    const p = unref(pages)
    if (!p || p.pages.length === 0) return false
    // If getNextPageParam returned null for the last page, we're done
    const lastPageParam = p.pageParams[p.pageParams.length - 1]
    return p.pages.length > 1 && lastPageParam == null
  })

  async function loadMore() {
    if (unref(error) != null || unref(end) || unref(isLoading))
      return
    await loadNextPage()
  }

  return { pages, data, error, isLoading, end, loadMore }
}

function extractNextCursorFromHeaders(headers: Headers): Cursor {
  const linkHeader = parseLinkHeader(headers.get('link'))

  if (!linkHeader?.next)
    return null

  const { rel, url, ...query } = linkHeader.next
  return Object.keys(query).length > 0 ? query : null
}

// Helpers
type PathWithGetOperationQueryParams<TQueryParams = unknown> = {
  get: {
    parameters: {
      query?: TQueryParams
    }
  }
}

export type FetchResponseDataArray<TPath> = TPath extends PathWithGetOperationData<Array<infer D>> ? D : never
export type FetchQueryParams<TPath> = TPath extends PathWithGetOperationQueryParams<infer Q> ? Q : never
