import { defineStore } from 'pinia'

export const useLoanRequestsStore = defineStore('loanRequests', () => {

  const { $api } = useNuxtApp()

  /*
  const { data: items, status, error, refresh } = useApi('/v1/me/liked', {
    key: "/me/liked", // provided to avoid missmatch with ssr (bug with openfetch?)
    watch: false,
  });
  */

  async function requestItem(itemId: number) {
    await $api('/v1/items/{item_id}/request', {
      method: "post",
      path: {
        item_id: itemId,
      }
    });

    //refresh();
  }

  /*
  const hasItem = (itemId: number | Ref<number>) => {

    if (isRef(itemId))
      return computed(() => items.value?.map(item => item.id).includes(itemId.value) ?? false);

    return items.value?.map(item => item.id).includes(itemId) ?? false;
  };
  */


  return {
    requestItem,
  }

});
