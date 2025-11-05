/**
 * List of all items of me
 **/
export function useMeItems() {
  const { data, ...query } = useMeItemsListQuery()

  const items: Ref<Array<ItemPreview>> = data

  return { items, ...query }
}
