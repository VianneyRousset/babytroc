export function useRegionsList() {
  const { data: regions, ...query } = useApiQuery('/v1/utils/regions', {
    key: ['regions'],
    refetchOnMount: false,
  })

  return { regions, ...query }
}
