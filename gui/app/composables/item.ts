import type { AsyncDataRequestStatus as AsyncStatus } from '#app'

/* NEW */
export function useItem({ itemId }: { itemId: MaybeRefOrGetter<number> }) {
  const { data: item, ...query } = useApiQuery('/v1/items/{item_id}', {
    key: () => ['item', toValue(itemId)],
    path: () => ({
      item_id: toValue(itemId),
    }),
  })
  return { item, ...query }
}

/* OLD */

export const useItemFirstImage = (item: MaybeRefOrGetter<ItemPreview>) => ({
  firstImageName: computed(() => toValue(item).first_image_name),
  firstImagePath: computed(() => imagePath(toValue(item).first_image_name)),
})

export const useItemImages = (item: MaybeRefOrGetter<Item>) => ({
  imagesNames: computed(() => toValue(item).images_names),
  imagesPaths: computed(() => toValue(item).images_names.map(imagePath)),
})

export function useItemNameValidity(
  name: MaybeRefOrGetter<string>,
  touched?: MaybeRefOrGetter<boolean>,
) {
  const _touched: MaybeRefOrGetter<boolean> = touched === undefined ? true : touched

  // validity pattern (unicode letters with ' ' and '-' not at the ends)
  const validCharactersRegex = /^\p{L}[\p{L} \-']+\p{L}$/u

  // name trimmed and without consecutive whitespaces
  const cleanedName = computed(() => avoidConsecutiveWhitespaces(toValue(name).trim()))

  // delayed propagation of the cleaned name
  const { synced: throttledNameSynced } = useThrottle(cleanedName, 500)

  // compute error message
  const error = computed<string | undefined>(() => {
    const _name = unref(cleanedName)

    if (_name === '')
      return 'Veuillez spécifier un nom'

    if (_name.length < 5)
      return 'Nom trop court'

    if (_name.length > 30)
      return 'Nom trop long'

    if (!validCharactersRegex.test(_name))
      return 'Nom invalide'

    return undefined
  })

  const status = computed<AsyncStatus>(() => {
    if (toValue(_touched) === false)
      return 'idle'

    if (unref(throttledNameSynced) === false)
      return 'pending'

    if (unref(error) != null)
      return 'error'

    return 'success'
  })

  return {
    name: cleanedName,
    status,
    error,
  }
}

export function useItemDescriptionValidity(
  description: MaybeRefOrGetter<string>,
  touched?: MaybeRefOrGetter<boolean>,
) {
  const _touched: MaybeRefOrGetter<boolean> = touched === undefined ? true : touched

  // description trimmed and without consecutive whitespaces
  const cleanedDescription = computed(() => avoidConsecutiveWhitespaces(toValue(description).trim()))

  // delayed propagation of the cleaned description
  const { synced: throttledDescriptionSynced } = useThrottle(cleanedDescription, 500)

  // compute error message
  const error = computed<string | undefined>(() => {
    const _description = unref(cleanedDescription)

    if (_description === '')
      return 'Veuillez spécifier une description'

    if (_description.length < 20)
      return 'Description trop court'

    if (_description.length > 600)
      return 'Description trop long'

    return undefined
  })

  const status = computed<AsyncStatus>(() => {
    if (toValue(_touched) === false)
      return 'idle'

    if (unref(throttledDescriptionSynced) === false)
      return 'pending'

    if (unref(error) != null)
      return 'error'

    return 'success'
  })

  return {
    description: cleanedDescription,
    status,
    error,
  }
}

export function useItemRegionsValidity(
  regions: MaybeRefOrGetter<Set<number>>,
  touched?: MaybeRefOrGetter<boolean>,
) {
  const _touched: MaybeRefOrGetter<boolean> = touched === undefined ? true : touched

  // delayed propagation of the cleaned description
  const { synced: throttledRegionsSynced } = useThrottle(computed(() => toValue(regions)), 500)

  // compute error message
  const error = computed<string | undefined>(() => {
    const _regions = toValue(regions)

    if (_regions.size < 1)
      return 'Veuillez spécifier une région'

    return undefined
  })

  const status = computed<AsyncStatus>(() => {
    if (toValue(_touched) === false)
      return 'idle'

    if (unref(throttledRegionsSynced) === false)
      return 'pending'

    if (unref(error) != null)
      return 'error'

    return 'success'
  })

  return {
    status,
    error,
  }
}
