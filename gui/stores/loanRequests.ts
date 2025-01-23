import { defineStore } from 'pinia'

export const useLoanRequestsStore = defineStore('loanRequests', () => {

  const { $api } = useNuxtApp()

  const { data: loanRequests, refresh } = useApi('/v1/me/borrowings/requests', {
    key: "/me/borrowings/requests", // provided to avoid missmatch with ssr (bug with openfetch?)
    watch: false,
  });

  async function requestItem(itemId: number) {
    await $api('/v1/items/{item_id}/request', {
      method: "post",
      path: {
        item_id: itemId,
      }
    });

    refresh();
  }

  const hasItem = (itemId: number | Ref<number>) => {

    if (isRef(itemId))
      return computed(() => loanRequests.value?.map(req => req.item.id).includes(itemId.value) ?? false);

    return loanRequests.value?.map(req => req.item.id).includes(itemId) ?? false;
  };


  return {
    loanRequests,
    requestItem,
    hasItem,
  }

});
