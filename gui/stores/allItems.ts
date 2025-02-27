import { defineStore } from 'pinia'
import { parseLinkHeader } from '@web3-storage/parse-link-header'
import { isEqual } from 'lodash'

import type { ApiResponse, ApiRequestQuery } from '#open-fetch'

import type { AsyncDataRequestStatus } from '#app';
import type { FetchError } from 'ofetch';

type ItemPreview = ApiResponse<'list_items_v1_items_get'>[number];
type ItemQuery = ApiRequestQuery<'list_items_v1_items_get'>;

type AllItemsStore = PaginatedSource<ItemPreview> & {
  items: Array<ItemPreview>,
  setQuery: (query: ItemQuery) => void,
};

export const useAllItemsStore: () => AllItemsStore = defineStore('allItems', () => {

  const { $api } = useNuxtApp()

  var query: ItemQuery = {
    n: 16,
  };

  function setQuery(newQuery: ItemQuery) {

    if (isEqual(query, newQuery))
      return;

    query = newQuery;
    reset();
  }

  const data = ref(Array<ItemPreview>());
  const items = computed(() => data.value);

  const end = ref<boolean>(false);
  const error = ref<FetchError | null>(null);
  const status = ref<AsyncDataRequestStatus>("idle");

  var nextQuery: ItemQuery = {};

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
      const newData = await $api('/v1/items', {

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
    items,
    more,
    reset,
    end,
    error,
    status,
    setQuery,
  };

});
