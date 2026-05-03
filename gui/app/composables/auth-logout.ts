export function useLogout() {
  const { $api } = useNuxtApp()
  const queryCache = useQueryCache()
  const liveChatStore = useLiveChatStore()

  const { mutateAsync: logout, ...mutation } = useMutation({
    mutation: () => {
      return $api('/v1/auth/logout', {
        method: 'POST',
      })
    },

    onSettled: () => {
      queryCache.invalidateQueries({ key: ['auth'], exact: true })

      queryCache.getEntries({
        predicate: entry => entry.key.includes('me'),
      }).map(queryCache.remove)

      liveChatStore.reset()
    },

    onSuccess: () => {
      localStorage.removeItem('auth-session')
    },
  })

  return { logout, ...mutation }
}
