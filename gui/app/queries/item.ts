import { useInfiniteQuery, useQuery } from '@pinia/colada'
import { pickBy } from 'lodash'

export function useItemQuery(itemId: MaybeRefOrGetter<number>) {
  const { $api } = useNuxtApp()

  return useQuery({
    key: () => ['item', toValue(itemId)],
    query: () =>
      $api('/v1/items/{item_id}', {
        path: {
          item_id: toValue(itemId),
        },
      }),
  })
}

export function useItemsListQuery(queryParams?: Ref<ItemQueryParams>) {
  const definition = defineQuery(() => {
    const { $api } = useNuxtApp()

    queryParams = queryParams ?? ref<ItemQueryParams>({})

    const query = useInfiniteQuery({
      key: () => ['item', 'explore', pickBy(unref(queryParams) ?? {}, v => v != null)],

      initialPage: {
        items: Array<ItemPreview>(),
        cursor: undefined as ItemQueryParams | undefined,
        end: false,
      },

      query: async (pages) => {
        let cursor: ItemQueryParams | undefined = undefined
        const items = await $api('/v1/items', {
          query: {
            ...pickBy(unref(queryParams), v => v != null),
            ...pages.cursor,
          },

          onResponse: async ({
            response: { ok, headers },
          }: { response: { ok: boolean, headers: Headers } }) => {
            if (!ok) return
            cursor = extractNextQueryParamsFromHeaders(headers)
          },
        })
        return { items, cursor }
      },

      merge: (result, current) => {
        return {
          items: [...result.items, ...current.items],
          cursor: current.cursor ?? result.cursor,
          end: current.cursor == null,
        }
      },
    })

    return {
      ...query,
      queryParams,
    }
  })
  return definition()
}
