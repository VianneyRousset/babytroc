import type { ApiRequestQuery } from '#open-fetch'

/* NEW */

export function useChatQuery(chatId: MaybeRefOrGetter<string>) {
  const { $api } = useNuxtApp()

  return useQueryWithAuth({
    key: () => ['me', 'chats', toValue(chatId)],
    query: () =>
      $api('/v1/me/chats/{chat_id}', {
        path: {
          chat_id: toValue(chatId),
        },
      }),
  })
}

type ChatsQueryParams = ApiRequestQuery<'list_client_chats_v1_me_chats_get'>

export const useChatsListQuery = defineQuery(() => {
  const { $api } = useNuxtApp()

  const query = useInfiniteQueryWithAuth({
    key: ['me', 'chats'],

    initialPage: {
      chats: Array<Chat>(),
      cursor: {} as ChatsQueryParams,
      end: false,
    },

    query: async (pages) => {
      let cursor: ChatsQueryParams | undefined = undefined

      const chats = await $api('/v1/me/chats', {
        query: pages.cursor,
        onResponse: async ({
          response: { ok, headers },
        }: { response: { ok: boolean, headers: Headers } }) => {
          if (!ok) return
          cursor = extractNextQueryParamsFromHeaders(headers)
        },
      })
      return { chats, cursor }
    },

    merge: (result, current) => {
      return {
        chats: [...result.chats, ...current.chats],
        cursor: current.cursor ?? result.cursor,
        end: current.cursor == null,
      }
    },
  })

  return query
})
