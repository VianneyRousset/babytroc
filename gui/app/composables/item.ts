import { ItemQueryAvailability } from '#build/types/open-fetch/schemas/api'
import type { AsyncDataRequestStatus as AsyncStatus } from '#app'

export const useIsItemOwnedByUser = (
  item: MaybeRefOrGetter<Item | ItemPreview>,
  user: MaybeRefOrGetter<UserPrivate | User | UserPreview | undefined>,
) => ({
  isOwnedByUser: computed(() => {
    const _user = toValue(user)
    if (_user === undefined) return undefined
    return toValue(item).owner_id === _user.id
  }),
})

export const useItemTargetedAgeMonths = (
  item: MaybeRefOrGetter<Item | ItemPreview>,
) => {
  const targetedAgeMonths = computed(() => toValue(item).targeted_age_months)
  const formatedTargetedAgeMonths = computed(() => {
    const _targetedAgeMonths = toValue(item).targeted_age_months
    return formatTargetedAge(_targetedAgeMonths[0], _targetedAgeMonths[1])
  })

  return { targetedAgeMonths, formatedTargetedAgeMonths }
}

export const useItemFirstImage = (item: MaybeRefOrGetter<ItemPreview>) => ({
  firstImageName: computed(() => toValue(item).first_image_name),
  firstImagePath: computed(() => imagePath(toValue(item).first_image_name)),
})

export const useItemImages = (item: MaybeRefOrGetter<Item>) => ({
  imagesNames: computed(() => toValue(item).images_names),
  imagesPaths: computed(() => toValue(item).images_names.map(imagePath)),
})

export const useItemRegions = (item: MaybeRefOrGetter<Item>) => ({
  regions: computed(() => toValue(item).regions),
  regionsIds: computed(
    () => new Set(toValue(item).regions.map(reg => reg.id)),
  ),
})

export const useItemLike = (
  item: MaybeRefOrGetter<Item | ItemPreview>,
  likedItems: MaybeRefOrGetter<Array<Item | ItemPreview>>,
) => ({
  isLikedByUser: computed(() => {
    const itemId = toValue(item).id
    return toValue(likedItems).some(likedItem => likedItem.id === itemId)
  }),
})

export const useItemSave = (
  item: MaybeRefOrGetter<Item | ItemPreview>,
  savedItems: MaybeRefOrGetter<Array<Item | ItemPreview>>,
) => ({
  isSavedByUser: computed(() => {
    const itemId = toValue(item).id
    return toValue(savedItems).some(savedItem => savedItem.id === itemId)
  }),
})

export const useItemFilters = () => {
  const route = useRoute()
  const router = useRouter()

  const searchInput = ref(getQueryParamAsArray(route.query, 'q').join(' '))
  const stateAvailable = ref(route.query.av !== ItemQueryAvailability.no)
  const stateUnavailable = ref(
    route.query.av === ItemQueryAvailability.no
    || route.query.av === ItemQueryAvailability.all,
  )

  const targetedAge = ref<AgeRange>(
    typeof route.query.mo === 'string'
      ? string2range(route.query.mo)
      : [0, null],
  )
  const regions = reactive(
    new Set(getQueryParamAsArray(route.query, 'reg').map(Number.parseInt)),
  )

  const isFilterActive = computed(() => {
    if (typeof route.query.mo === 'string') return true

    if (
      typeof route.query.av === 'string'
      && Object.values(ItemQueryAvailability).includes(
        route.query.av as ItemQueryAvailability,
      )
    )
      return true

    if (route.query.reg) return true

    return false
  })

  const areFilterInputsChanged = computed(() => {
    if (!stateAvailable.value) return true

    if (stateUnavailable.value) return true

    if (targetedAge.value[0] !== 0 || targetedAge.value[1] !== null)
      return true

    if (regions.size > 0) return true

    return false
  })

  function filter() {
    const q = unref(searchInput)
      .split(' ')
      .filter(word => word.length > 0)
    const mo = unref(targetedAge)
    const _available = unref(stateAvailable)
    const _unavailable = unref(stateUnavailable)

    const query: ItemQuery = {
      q: q.length > 0 ? q : undefined,
      mo: (mo[0] ?? 0) > 0 || mo[1] !== null ? range2string(mo) : undefined,
      av: _unavailable
        ? _available
          ? ItemQueryAvailability.all
          : ItemQueryAvailability.no
        : undefined,
      reg: regions.size > 0 ? Array.from(regions) : undefined,
    }

    // update page query params
    router.push({ query: query })
  }

  return {
    searchInput,
    stateAvailable,
    stateUnavailable,
    targetedAge,
    regions,
    isFilterActive,
    areFilterInputsChanged,
    filter,
  }
}

export function useItemNameValidity(
  name: MaybeRefOrGetter<string>,
  touched?: MaybeRefOrGetter<boolean>,
) {
  const _touched: MaybeRefOrGetter<boolean> = touched === undefined ? true : touched

  // validity pattern (unicode letters with ' ' and '-' not at the ends)
  const validCharactersRegex = /^\p{L}[\p{L} -]+\p{L}$/u

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
