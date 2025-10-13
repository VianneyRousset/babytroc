/**
 * List of all items owned by an user
 **/
export function useUserItems({ userId }: { userId: MaybeRefOrGetter<number> }) {
  const { data, ...query } = useUserItemsListQuery(userId)

  const items: Ref<Array<ItemPreview>> = data

  return { items, ...query }
}
