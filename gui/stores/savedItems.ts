import { defineStore } from 'pinia'

export const useSavedItemsStore = defineStore('savedItems', () => {

  const { $api } = useNuxtApp()

  const { data: items, status, error, refresh } = useApi('/v1/me/saved', {
    key: "/me/saved", // provided to avoid missmatch with ssr (bug with openfetch?)
    watch: false,
  });

  async function add(itemId: number) {
    await $api('/v1/me/saved/{item_id}', {
      method: "post",
      path: {
        item_id: itemId,
      }
    });
    refresh();
  }

  async function remove(itemId: number) {
    await $api('/v1/me/saved/{item_id}', {
      method: "delete",
      path: {
        item_id: itemId,
      }
    });
    refresh();
  }

  const has = (itemId: number | Ref<number>) => {

    if (isRef(itemId))
      return computed(() => items.value?.map(item => item.id).includes(itemId.value) ?? false);

    return items.value?.map(item => item.id).includes(itemId) ?? false;
  };


  return {
    items,
    add,
    remove,
    has,
    status,
    error,
  }

});
