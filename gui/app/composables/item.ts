/* NEW */
export function useItem({ itemId }: { itemId: MaybeRefOrGetter<number> }) {
  const { data: item, ...query } = useApiQuery('/v1/items/{item_id}', {
    key: () => ['item', `item-${toValue(itemId)}`],
    path: () => ({
      item_id: toValue(itemId),
    }),
    refetchOnMount: false,
  })
  return { item, ...query }
}

export function useItemImages<T extends { images_names: Array<string> }>(item: MaybeRefOrGetter<T>) {
  return {
    imagesNames: computed(() => toValue(item).images_names),
    imagesPaths: computed(() => toValue(item).images_names.map(imagePath)),
  }
}

/* OLD */

export const useItemFirstImage = (item: MaybeRefOrGetter<ItemPreview>) => ({
  firstImageName: computed(() => toValue(item).first_image_name),
  firstImagePath: computed(() => imagePath(toValue(item).first_image_name)),
})
