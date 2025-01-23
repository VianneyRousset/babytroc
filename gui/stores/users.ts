import { defineStore } from 'pinia'
import type { ApiResponse } from '#open-fetch';

type User = ApiResponse<"get_user_v1_users__user_id__get">;

export const useUsersStore = defineStore('users', () => {

  const { $api } = useNuxtApp()

  const users = reactive({} as { [key: number]: User });

  const has = (userId: number | Ref<number>) => {

    if (isRef(userId))
      return computed(() => users[userId.value] !== undefined);

    return users[userId] !== undefined;
  };

  async function get(userId: number | Ref<number>) {

    // fetch user if not in cache
    if (!has(userId))
      await add(isRef(userId) ? userId.value : userId);

    // get from cache
    return isRef(userId) ? users[userId.value] : users[userId];
  };

  async function add(userId: number) {
    users[userId] = await $api('/v1/users/{user_id}', {
      path: {
        user_id: userId,
      }
    });
  }

  return {
    has,
    get,
    add,
  }

});
