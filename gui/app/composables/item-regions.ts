export function useItemRegions<T extends { regions: Array<Region> }>(
  item: MaybeRefOrGetter<T>,
): {
  regions: Ref<Array<Region>>
  regionIds: Ref<Set<number>>
} {
  return {
    regions: computed(() => toValue(item).regions),
    regionIds: computed(() => new Set(toValue(item).regions.map(reg => reg.id))),
  }
}
