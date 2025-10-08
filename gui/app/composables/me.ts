export function useMe(): {
  me: Ref<UserPrivate | undefined>
  error: Ref<boolean>
  loading: Ref<boolean>
} {
  const {
    data: me,
    asyncStatus,
    status,
  } = useMeQuery()

  const error = computed<boolean>(() => unref(status) === 'error')
  const loading = computed<boolean>(() => unref(asyncStatus) === 'loading')

  return {
    me,
    error,
    loading,
  }
}
