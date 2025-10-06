import { useInfiniteQuery, useQuery } from '@pinia/colada'
import type { ApiRequestQuery } from '#open-fetch'

export function useUserQuery(userId: MaybeRefOrGetter<number>) {
  const { $api } = useNuxtApp()

  return useQuery({
    key: () => ['user', toValue(userId)],
    query: () =>
      $api('/v1/users/{user_id}', {
        path: {
          user_id: toValue(userId),
        },
      }),
  })
}

type UserItemsQueryParams = ApiRequestQuery<'list_items_owned_by_user_v1_users__user_id__items_get'>

export function useUserItemsListQuery(userId: MaybeRefOrGetter<number>) {
  const definition = defineQuery(() => {
    const { $api } = useNuxtApp()

    const query = useInfiniteQuery({
      key: () => ['item', 'user', `user${toValue(userId)}`],

      initialPage: {
        items: Array<ItemPreview>(),
        cursor: undefined as UserItemsQueryParams | undefined,
        end: false,
      },

      query: async (pages) => {
        let cursor: UserItemsQueryParams | undefined = undefined
        const items = await $api('/v1/users/{user_id}/items', {
          path: {
            user_id: toValue(userId),
          },
          query: pages.cursor,
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

    return query
  })
  return definition()
}
