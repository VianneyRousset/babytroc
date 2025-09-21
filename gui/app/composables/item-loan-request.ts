export function useItemLoanRequest({ itemId }: { itemId: MaybeRefOrGetter<number> }): {
  request: () => Promise<LoanRequest>
  unrequest: () => Promise<void>
  error: Ref<boolean>
  loading: Ref<boolean>
} {
  const {
    mutateAsync: requestMutateAsync,
    status: requestMutateStatus,
    asyncStatus: requestMutateAsyncStatus,
  } = useRequestItemMutation(itemId)

  const {
    mutateAsync: unrequestMutateAsync,
    status: unrequestMutateStatus,
    asyncStatus: unrequestMutateAsyncStatus,
  } = useUnrequestItemMutation(itemId)

  const error = computed<boolean>(() => {
    return unref(requestMutateStatus) === 'error' || unref(unrequestMutateStatus) === 'error'
  })
  const loading = computed<boolean>(() => {
    return unref(requestMutateAsyncStatus) === 'loading' || unref(unrequestMutateAsyncStatus) === 'loading'
  })

  return {
    request: requestMutateAsync,
    unrequest: async () => {
      await unrequestMutateAsync()
    },
    error,
    loading,
  }
}
