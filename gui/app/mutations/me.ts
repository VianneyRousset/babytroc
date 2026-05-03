export const useUpdateProfileMutation = defineMutation(() => {
  const { $api } = useNuxtApp()
  const queryCache = useQueryCache()

  return useMutation({
    mutation: async (data: { name?: string, avatar_seed?: string }) =>
      await $api('/v1/me', {
        method: 'POST',
        body: data,
      }),
    onSettled: () => {
      queryCache.invalidateQueries({ key: ['me'] }, 'all')
    },
  })
})
