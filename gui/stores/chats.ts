import { defineStore } from 'pinia'
import { parseLinkHeader } from '@web3-storage/parse-link-header'
import type { Links } from '@web3-storage/parse-link-header'
import type { ApiResponse, ApiRequestQuery } from '#open-fetch'
import type { AsyncDataRequestStatus } from '#app';
import type { FetchError } from 'ofetch';

type Chat = ApiResponse<'list_client_chats_v1_me_chats_get'>[number];
type ChatQuery = ApiRequestQuery<'list_client_chats_v1_me_chats_get'>;

export const useChatsStore = defineStore('chats', () => {

  const { $api } = useNuxtApp()

  const data = ref(Array<Chat>());
  const error = ref<FetchError | null>(null);
  const status = ref<AsyncDataRequestStatus>("idle");
  const done = ref<boolean>(false);

  var defaultQuery: ChatQuery = {
    n: 2,
  }

  var nextQuery: ChatQuery = {}

  async function more() {

    try {
      const newData = await $api('/v1/me/chats', {

        query: {
          ...defaultQuery,
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

      done.value = (newData.length == 0);
      data.value = data.value.concat(newData);
      status.value = "success";

    } catch (err) {
      console.error(err);
      error.value = err as FetchError;
      status.value = "error";
    }

  }

  const chats = computed(() => {
    return data.value.toSorted((a: Chat, b: Chat) => b.last_message_id - a.last_message_id);
  })

  return {
    chats,
    more,
  }

});
