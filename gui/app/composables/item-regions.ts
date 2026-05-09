export function useItemRegions<T extends { region_ids: number[] }>(
	item: MaybeRefOrGetter<T>,
): {
	regionIds: Ref<Set<number>>;
} {
	return {
		regionIds: computed(() => new Set(toValue(item).region_ids)),
	};
}
