function useLikedItemsQuery() {
  const { $api } = useNuxtApp()

  return useQueryWithAuth({
    key: () => ['me', 'liked-items'],
    query: () => $api('/v1/me/liked'),
  })
}

export { useLikedItemsQuery }
