import { defineStore } from 'pinia'

export const useMeStore = defineStore('me', () => {

  const { data: me, refresh } = useApi('/v1/me', {
    key: "/me", // provided to avoid missmatch with ssr (bug with openfetch?)
    watch: false,
  });

  return {
    me,
    refresh,
  }

});
