export function useRegionsList() {
  const { data: regions, ...query } = useApiQuery('/v1/utils/regions', {
    key: ['region', 'regions'],
    refetchOnMount: false,
  })

  return { regions, ...query }
}
