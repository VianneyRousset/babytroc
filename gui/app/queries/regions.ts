import { useQuery } from '@pinia/colada'

export function useRegionsListQuery() {
  const { $api } = useNuxtApp()

  return useQuery({
    key: () => ['regions'],
    query: async () => $api('/v1/utils/regions'),
  })
}
