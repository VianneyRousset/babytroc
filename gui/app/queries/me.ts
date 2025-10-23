function useMeQuery() {
  const { $api } = useNuxtApp()

  return useQueryWithAuth({
    key: ['me'],
    query: () => $api('/v1/me'),
    refetchOnMount: false,
  })
}

export { useMeQuery }
