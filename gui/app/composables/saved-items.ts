/**
 * List of all saved items.
 **/
export function useSavedItems() {
  const { data, ...query } = useSavedItemsListQuery()

  const items: Ref<Array<ItemPreview>> = data

  return { items, ...query }
}

/**
 * Add/remove item of the list of saved items.
 */
export function useItemSave(
  { itemId }: { itemId: MaybeRefOrGetter<number> },
) {
  const {
    mutateAsync: saveMutateAsync,
    // status: saveMutateStatus,
    // asyncStatus: saveMutateAsyncStatus,
  } = useSaveItemMutation(itemId)

  const {
    mutateAsync: unsaveMutateAsync,
    // status: unsaveMutateStatus,
    // asyncStatus: unsaveMutateAsyncStatus,
  } = useUnsaveItemMutation(itemId)

  return {
    save: saveMutateAsync,
    unsave: unsaveMutateAsync,
  }
}
