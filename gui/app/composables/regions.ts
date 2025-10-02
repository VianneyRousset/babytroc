export function useRegionsList(): {
  regions: Ref<Array<Region> | undefined>
  error: Ref<boolean>
  loading: Ref<boolean>
} {
  const {
    data: regions,
    asyncStatus,
    status,
  } = useRegionsListQuery()

  const error = computed<boolean>(() => unref(status) === 'error')
  const loading = computed<boolean>(() => unref(asyncStatus) === 'loading')

  return {
    regions,
    error,
    loading,
  }
}
