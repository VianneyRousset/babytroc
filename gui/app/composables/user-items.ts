/**
 * List of all items owned by an user
 **/
export function useUserItems({ userId }: { userId: MaybeRefOrGetter<number> }): {
  items: Ref<Array<ItemPreview>>
  error: Ref<boolean>
  loading: Ref<boolean>
  loadMore: () => void
} {
  const {
    data: pages,
    loadMore,
    asyncStatus,
    status,
  } = useUserItemsListQuery(userId)

  const items = computed<Array<ItemPreview>>(() => unref(pages).items ?? [])
  const error = computed<boolean>(() => unref(status) === 'error')
  const loading = computed<boolean>(() => unref(asyncStatus) === 'loading')

  // fixes few bugs by loading more items when `items` is empty
  watch(items, _items => _items.length === 0 && loadMore())

  return {
    items,
    error,
    loading,
    loadMore: async () => {
      if (!unref(pages).end && !unref(error) && !unref(loading))
        await loadMore()
    },
  }
}
