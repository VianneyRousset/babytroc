import type { AsyncDataRequestStatus as AsyncStatus } from '#app'

export function useItemNameValidity(
  name: MaybeRefOrGetter<string>,
) {
  const { value: touched } = useThrottle(useTouched(name, ''), 1000)

  // validity pattern (unicode letters with ' ' and '-' not at the ends)
  const validCharactersRegex = /^\p{L}[\p{L} \-']+\p{L}$/u

  // delayed propagation of the name
  const { value: throttledName, synced: throttledNameSynced } = useThrottle(name, 500)

  // compute error message
  const error = computed<string | undefined>(() => {
    const _name = unref(throttledName)

    if (_name === '') return 'Veuillez spécifier un nom'
    if (_name.length < 5) return 'Nom trop court'
    if (_name.length > 30) return 'Nom trop long'
    if (!validCharactersRegex.test(_name)) return 'Nom invalide'
    return undefined
  })

  const status = computed<AsyncStatus>(() => {
    if (toValue(touched) === false) return 'idle'
    if (unref(throttledNameSynced) === false) return 'pending'
    if (unref(error) != null) return 'error'
    return 'success'
  })

  return { status, error, touched }
}

export function useItemDescriptionValidity(
  description: MaybeRefOrGetter<string>,
) {
  const { value: touched } = useThrottle(useTouched(description, ''), 1000)

  // delayed propagation of the description
  const { value: throttledDescription, synced: throttledDescriptionSynced } = useThrottle(description, 500)

  // compute error message
  const error = computed<string | undefined>(() => {
    const _description = unref(throttledDescription)

    if (_description === '') return 'Veuillez spécifier une description'
    if (_description.length < 20) return 'Description trop courte'
    if (_description.length > 600) return 'Description trop longue'
    return undefined
  })

  const status = computed<AsyncStatus>(() => {
    if (toValue(touched) === false) return 'idle'
    if (unref(throttledDescriptionSynced) === false) return 'pending'
    if (unref(error) != null) return 'error'
    return 'success'
  })

  return { status, error, touched }
}

export function useItemRegionsValidity(
  regions: MaybeRefOrGetter<Set<number>>,
) {
  const { value: touched } = useThrottle(useTouched(
    regions,
    new Set(),
    (a: Set<number>, b: Set<number>) => a.size === b.size && [...a].every(x => b.has(x)),
  ), 1000)

  // delayed propagation of the regions
  const { value: throttledRegions, synced: throttledRegionsSynced } = useThrottle(regions, 500)

  // compute error message
  const error = computed<string | undefined>(() => {
    const _regions = toValue(throttledRegions)

    if (_regions.size < 1) return 'Veuillez spécifier une région'
    return undefined
  })

  const status = computed<AsyncStatus>(() => {
    if (toValue(touched) === false) return 'idle'
    if (unref(throttledRegionsSynced) === false) return 'pending'
    if (unref(error) != null) return 'error'
    return 'success'
  })

  return { status, error, touched }
}
