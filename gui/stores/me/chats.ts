import { defineStore } from 'pinia'
import { parseLinkHeader } from '@web3-storage/parse-link-header'
import { isEqual } from 'lodash'

import type { AsyncDataRequestStatus } from '#app';
import type { FetchError } from 'ofetch';

type ChatsStore = () => PaginatedSource<Chat> & {
  setQuery: (query: ChatQuery) => void,
};

type ChatMessagesStore = () => PaginatedSource<ChatMessage> & {
  send: (msg: string) => Promise<void>,
};

const useChatsStore: ChatsStore = defineStore('chats', () => {

  const { $api } = useNuxtApp()

  var query: ChatQuery = {
    n: 16,
  };

  function setQuery(newQuery: ChatQuery) {

    if (isEqual(query, newQuery))
      return;

    query = newQuery;
    reset();
  }

  const data = ref(Array<Chat>());

  const end = ref<boolean>(false);
  const error = ref<FetchError | null>(null);
  const status = ref<AsyncDataRequestStatus>("idle");

  var nextQuery: ChatQuery = {};

  function reset() {
    data.value = [];
    nextQuery = {};
    end.value = false;
  }

  async function more() {

    if (status.value === "pending")
      return;

    status.value = "pending";

    try {
      const newData = await $api('/v1/me/chats', {

        query: {
          ...query,
          ...nextQuery,
        },

        async onResponse({ response }) {
          const linkHeader = parseLinkHeader(response.headers.get("link"));

          if (linkHeader === null)
            return console.error("Null linkHeader when fetching first items.");

          const { rel, url, ...query } = linkHeader.next;
          nextQuery = query;
        },
      });

      end.value = (newData.length == 0);
      data.value = data.value.concat(newData);
      status.value = "success";

    } catch (err) {
      console.error(err);
      error.value = err as FetchError;
      end.value = true;
      status.value = "error";
    }

  }

  return {
    data,
    more,
    reset,
    end,
    error,
    status,
    setQuery,
  };

});

function createChatMessagesStore(chatId: string): ChatMessagesStore {
  return defineStore(`chatMessages${chatId}`, () => {

    const { $api } = useNuxtApp()

    var query: ChatMessageQuery = {
      n: 16,
    };

    const data = ref(Array<ChatMessage>());

    const end = ref<boolean>(false);
    const error = ref<FetchError | null>(null);
    const status = ref<AsyncDataRequestStatus>("idle");

    var nextQuery: ChatMessageQuery = {};

    function reset() {
      data.value = [];
      nextQuery = {};
      end.value = false;
    }

    async function more() {

      if (status.value === "pending")
        return;

      status.value = "pending";

      try {
        const newData = await $api('/v1/me/chats/{chat_id}/messages', {

          path: {
            chat_id: chatId,
          },

          query: {
            ...query,
            ...nextQuery,
          },

          async onResponse({ response }) {
            const linkHeader = parseLinkHeader(response.headers.get("link"));

            if (linkHeader === null)
              return console.error("Null linkHeader when fetching first items.");

            const { rel, url, ...query } = linkHeader.next;
            nextQuery = query;
          },
        });

        end.value = (newData.length == 0);
        data.value = data.value.concat(newData);
        status.value = "success";

      } catch (err) {
        console.error(err);
        error.value = err as FetchError;
        end.value = true;
        status.value = "error";
      }

    }

    async function send(msg: string) {

      await $api('/v1/me/chats/{chat_id}/messages', {
        method: "post",
        path: {
          chat_id: chatId,
        },
        body: {
          payload: msg,
        }
      });

      reset();
    }


    return {
      data,
      more,
      reset,
      end,
      error,
      status,
      send,
    };
  });
};

export { useChatsStore, createChatMessagesStore }
