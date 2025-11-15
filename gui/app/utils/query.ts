import type { paths } from '#build/types/open-fetch/schemas/api'
import type { FetchOptions } from 'ofetch'
import type { PathsWithMethod } from 'openapi-typescript-helpers'
import type { UseQueryOptions, UseQueryReturn } from '@pinia/colada'

// Available API query paths
type ApiQueryPaths = Pick<paths, PathsWithMethod<paths, 'get'>>

// API query options
type ApiQueryOptions<TPath, TData, Error> = (
  ApiFetchOptions<TPath>
  & Omit<UseQueryOptions<TData, Error, TData | undefined>, 'query'>
)

export function useApiQuery<
  TReq extends keyof ApiQueryPaths,
  TRes = FetchResponseData<ApiQueryPaths[TReq]>,
>(
  url: TReq,
  options: NoInfer<ApiQueryOptions<ApiQueryPaths[TReq], TRes, Error>>,
): NoInfer<UseQueryReturn<TRes, Error>> {
  const { $api } = useNuxtApp()

  // @ts-expect-error avoid typing errors
  return useQuery({
    ...options,
    // @ts-expect-error avoid typing errors
    query: () => $api(url, {
      ...options,
      query: toValue(options.query),
      header: toValue(options.header),
      path: toValue(options.path),
      cookie: toValue(options.cookie),
    }),
  })
}

// Query parameters options
type ParamsOptions<TOperation>
  = TOperation extends { parameters: infer TParams }
    ? {
        [K in keyof TParams as TParams[K] extends never ? never : K]: MaybeRefOrGetter<TParams[K]>
      } : never

// Fetching options
export type ApiFetchOptions<TPath> = 'get' extends keyof TPath
  ? (
    ParamsOptions<TPath['get']>
    & Omit<FetchOptions, 'query' | 'body' | 'method'>
    ) : never

// Helpers
type FetchResponseData<TPath> = TPath extends PathWithGetOperationData<infer D> ? D : never

export type PathWithGetOperationData<TRes = unknown> = {
  get: {
    responses: {
      200: {
        content: {
          'application/json': TRes
        }
      }
    }
  }
}
