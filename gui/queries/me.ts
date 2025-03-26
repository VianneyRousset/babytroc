import { useQuery } from '@pinia/colada'


function useMeQuery() {

  const { $api } = useNuxtApp()

  return useQuery({
    key: () => ["me"],
    query: () => $api("/v1/me"),
  });
}

export { useMeQuery }
