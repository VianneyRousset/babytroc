import { defineStore } from 'pinia'
import { parseLinkHeader } from '@web3-storage/parse-link-header'
import type { Links } from '@web3-storage/parse-link-header'
import type { ApiResponse, ApiRequestQuery } from '#open-fetch'
import type { AsyncDataRequestStatus } from '#app';
import type { FetchError } from 'ofetch';

type Item = ApiResponse<'list_items_v1_items_get'>[number];
type ItemQuery = ApiRequestQuery<'list_items_v1_items_get'>;

export const useAllItemsStore = defineStore('allItems', () => {

  const filters = reactive({
    ageMin: 0 as number,
    ageMax: null as number | null,
    regions: [] as number[],
    searchText: "",
  });

  const { $api } = useNuxtApp()
  const controller = new AbortController();
  const signal = controller.signal;

  const extraItems = ref(Array<Item>());
  const extraFetchLink = ref(null) as Ref<null | Links[string]>;
  const extraFetchStatus = ref("idle") as Ref<AsyncDataRequestStatus>;
  const extraFetchError = ref(null) as Ref<FetchError | null>;
  const canFetchMore = ref(false);

  const queryParams = reactive({ n: 16 }) as ItemQuery

  function refresh() {

    // words
    const words = filters.searchText.split(" ").filter((word => word.length > 0));
    if (words.length === 0) {
      delete queryParams.q;
    } else {
      queryParams.q = words;
    }

    // targeted age month
    if (filters.ageMin === 0 && filters.ageMax === null) {
      delete queryParams.mo;
    } else {
      queryParams.mo = `${filters.ageMin === null ? "" : filters.ageMin}-${filters.ageMax === null ? "" : filters.ageMax}`;
    }

    // reset items
    firstFetchStatus.value = "idle";
    firstItems.value = [];
    extraFetchStatus.value = "idle";
    extraItems.value = [];

    // refetch first items
    reFetch();
  };

  const { data: firstItems, status: firstFetchStatus, error: firstFetchError, refresh: reFetch } = useApi('/v1/items', {
    query: queryParams,
    key: "/items", // provided to avoid missmatch with ssr (bug with openfetch?)
    async onResponse({ response }) {

      const linkHeader = parseLinkHeader(response.headers.get("link"));

      if (linkHeader === null)
        return console.error("Null linkHeader when fetching first items.");

      extraFetchLink.value = linkHeader.next;
      canFetchMore.value = response._data.length > 0;
    },
    watch: false,
  });

  const items = computed(() => {

    if (firstItems.value === null)
      return Array<Item>();

    return firstItems.value.concat(extraItems.value);
  });

  const error = computed(() => firstFetchError.value || extraFetchError.value);

  function fetchMore() {

    console.log("fetch more");

    if (extraFetchLink.value === null)
      return console.error("Null extraFetchLink");

    const { rel, url, ...query } = extraFetchLink.value;

    extraFetchStatus.value = "pending";
    $api('/v1/items', {
      query,
      signal,
      onResponse({ response }) {

        const linkHeader = parseLinkHeader(response.headers.get("link"));

        if (linkHeader === null)
          return console.error("Null linkHeader when fetching extra items.");

        extraFetchLink.value = parseLinkHeader(response.headers.get("link"))?.next ?? null;
      }
    }).then((data) => {

      canFetchMore.value = data.length > 0;

      extraItems.value = extraItems.value.concat(data)
      extraFetchStatus.value = "success";
    }).catch((error) => {
      console.error(error);
      extraFetchError.value = error;
      extraFetchStatus.value = "error";
    })
  }

  return {
    refresh,
    firstFetchStatus,
    firstFetchError,
    extraFetchStatus,
    extraFetchError,
    filters,
    items,
    extraFetchLink,
    fetchMore,
    canFetchMore,
    error,
  }

});
