export function useItemLike({ itemId }: { itemId: MaybeRefOrGetter<number> }): {
  like: () => Promise<void>
  unlike: () => Promise<void>
  error: Ref<boolean>
  loading: Ref<boolean>
} {
  const {
    mutateAsync: likeMutateAsync,
    status: likeMutateStatus,
    asyncStatus: likeMutateAsyncStatus,
  } = useLikeItemMutation(itemId)

  const {
    mutateAsync: unlikeMutateAsync,
    status: unlikeMutateStatus,
    asyncStatus: unlikeMutateAsyncStatus,
  } = useUnlikeItemMutation(itemId)

  const error = computed<boolean>(() => {
    return unref(likeMutateStatus) === 'error' || unref(unlikeMutateStatus) === 'error'
  })
  const loading = computed<boolean>(() => {
    return unref(likeMutateAsyncStatus) === 'loading' || unref(unlikeMutateAsyncStatus) === 'loading'
  })

  return {
    like: async () => {
      await likeMutateAsync()
    },
    unlike: async () => {
      await unlikeMutateAsync()
    },
    error,
    loading,
  }
}
