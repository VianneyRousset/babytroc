import { defineStore } from 'pinia'

type AllItemsStore = () => PaginatedSource<ItemPreview> & {
  add: (itemId: number) => Promise<void>,
  remove: (itemId: number) => Promise<void>,
  has: (itemId: number) => Ref<boolean>,
};

export const useSavedItemsStore: AllItemsStore = defineStore('savedItems', () => {

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

  function has(itemId: number): Ref<boolean> {
    return computed(() => items.value?.map(item => item.id).includes(itemId) ?? false) as any;
  }

  return {
    items,
    data: computed(() => items.value ?? []),
    more: async () => { },
    reset: () => { },
    end: true,
    add,
    remove,
    has,
    status,
    error,
  }

});
