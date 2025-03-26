import { useInfiniteQuery, useQuery } from '@pinia/colada'
import { parseLinkHeader } from '@web3-storage/parse-link-header'


export function useChatQuery(chatId: string) {

  const { $api } = useNuxtApp();

  return useQuery({
    key: () => ["chat", chatId],
    query: () => $api("/v1/me/chats/{chat_id}", {
      path: {
        chat_id: chatId,
      }
    }),
  });
}

export const useChatsListQuery = defineQuery(() => {

  const { $api } = useNuxtApp();

  return useInfiniteQuery({
    key: ["chats"],

    initialPage: {
      data: Array<Chat>(),
      cursor: {} as ChatQuery,
      end: false,
    },

    query: async (pages) => {

      let newCursor: ChatQuery = {};

      const newData = await $api("/v1/me/chats", {
        query: pages.cursor,

        onResponse: async ({ response: { ok, headers } }: { response: { ok: boolean, headers: Headers } }) => {
          if (!ok) return;

          const linkHeader = parseLinkHeader(headers.get("link"));

          if (linkHeader === null)
            return console.error("Null linkHeader when fetching first items.");

          const { rel, url, ...query } = linkHeader.next;
          newCursor = query;
        },

      });

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
      };
    },
  });
});


export const useChatMessagesListQuery = (chatId: MaybeRefOrGetter<string>) => {
  const definition = defineQuery(() => {

    const { $api } = useNuxtApp();

    return useInfiniteQuery({
      key: ["chat", toValue(chatId), "messages"],

      initialPage: {
        data: Array<ChatMessage>(),
        cursor: {} as ChatMessageQuery,
        end: false,
      },

      query: async (pages) => {

        let newCursor: ChatMessageQuery = {};

        const newData = await $api("/v1/me/chats/{chat_id}/messages", {
          path: {
            chat_id: toValue(chatId),
          },
          query: pages.cursor,

          onResponse: async ({ response: { ok, headers } }: { response: { ok: boolean, headers: Headers } }) => {
            if (!ok) return;

            const linkHeader = parseLinkHeader(headers.get("link"));

            if (linkHeader === null)
              return console.error("Null linkHeader when fetching first items.");

            const { rel, url, ...query } = linkHeader.next;
            newCursor = query;
          },

        });

        return {
          data: newData,
          cursor: newCursor,
        }
      },

      merge: (pages, newPage) => {

        console.log("Merge", toValue(chatId), newPage);

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
        };
      },
    });
  });

  return definition();
};
