import { defineStore } from 'pinia'
import type { ApiResponse } from '#open-fetch';

type User = ApiResponse<"get_user_v1_users__user_id__get">;

export const useUsersStore = defineStore('users', () => {

  const { $api } = useNuxtApp()

  const users = reactive({} as { [key: number]: User });

  function has(userId: number): Ref<boolean> {
    return computed(() => users[userId] !== undefined);
  };

  async function get(userId: number): Promise<Ref<User>> {


    // fetch user if not in cache
    if (!has(userId).value)
      await fetch(userId);

    // get from cache
    return toRef(users, userId);
  };

  async function fetch(userId: number): Promise<void> {
    users[userId] = await $api('/v1/users/{user_id}', {
      path: {
        user_id: userId,
      }
    });
  }

  return {
    has,
    get,
    fetch,
  }

});
