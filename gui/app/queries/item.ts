import { useInfiniteQuery, useQuery } from '@pinia/colada'
import { parseLinkHeader } from '@web3-storage/parse-link-header'

export function useItemQuery(itemId: MaybeRefOrGetter<number>) {
  const { $api } = useNuxtApp()

  return useQuery({
    key: () => ['items', toValue(itemId)],
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

    const defaultQueryParams: ItemQueryParams = {
      n: 32,
    }
    queryParams = queryParams ?? ref<ItemQueryParams>({})

    const { ...query } = useInfiniteQuery({
      key: () => ['items'],

      initialPage: {
        data: Array<ItemPreview>(),
        cursor: {} as ItemQueryParams,
        end: false,
      },

      query: async (pages) => {
        let newCursor: ItemQueryParams = {}

        const newData = await $api('/v1/items', {
          query: {
            ...defaultQueryParams,
            ...unref(queryParams),
            ...pages.cursor,
          },

          onResponse: async ({
            response: { ok, headers },
          }: { response: { ok: boolean, headers: Headers } }) => {
            if (!ok) return

            const linkHeader = parseLinkHeader(headers.get('link'))

            if (!linkHeader?.next)
              return console.error('Null linkHeader when fetching first items.')

            const { rel, url, ...query } = linkHeader.next
            newCursor = query
          },
        })

        return {
          data: newData,
          cursor: newCursor,
        }
      },

      merge: (pages, newPage) => {
        if (newPage.data.length === 0) {
          return {
            ...pages,
            end: true,
          }
        }

        return {
          data: [...pages.data, ...newPage.data],
          cursor: newPage.cursor,
          end: false,
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
