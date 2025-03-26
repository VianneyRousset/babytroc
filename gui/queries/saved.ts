import { useQuery } from '@pinia/colada'


function useSavedItemsQuery() {

  const { $api } = useNuxtApp()

  return useQuery({
    key: () => ["me-saved-items"],
    query: () => $api("/v1/me/saved"),
  });
}


export { useSavedItemsQuery }
