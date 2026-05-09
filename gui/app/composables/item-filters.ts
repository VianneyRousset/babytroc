import { cloneDeep, isEqual, pickBy } from "lodash";

/**
 * Parsed route query params
 **/
export function useRouteItemQueryParams(): {
	queryParams: Ref<ItemQueryParams>;
} {
	const route = useRoute();
	const router = useRouter();

	return {
		queryParams: computed<ItemQueryParams>({
			get: () => {
				const _query = route.query;
				return pickBy(
					{
						cwm:
							typeof _query.cwm === "string" &&
							!Number.isNaN(parseInt(_query.cwm, 10))
								? parseInt(_query.cwm, 10)
								: undefined,
						cid:
							typeof _query.cid === "string" &&
							!Number.isNaN(parseInt(_query.cid, 10))
								? parseInt(_query.cid, 10)
								: undefined,
						mo: typeof _query.mo === "string" ? _query.mo : undefined,
						av:
							typeof _query.av === "string" &&
							Object.values(ItemQueryAvailability).includes(
								_query.av as ItemQueryAvailabilityType,
							)
								? (_query.av as ItemQueryAvailabilityType)
								: undefined,
						reg: _query.reg
							? getQueryParamAsArray(_query, "reg")
									.map((v) => Number.parseInt(v, 10))
									.filter((v) => v != null && !Number.isNaN(v))
							: undefined,
						cat: _query.cat ? getQueryParamAsArray(_query, "cat") : undefined,
						n:
							typeof _query.n === "string" &&
							!Number.isNaN(parseInt(_query.n, 10))
								? parseInt(_query.n, 10)
								: undefined,
						q: _query.q ? getQueryParamAsArray(_query, "q") : undefined,
					},
					(v) => v != null,
				);
			},
			set: (queryParams: ItemQueryParams) =>
				router.replace({ query: queryParams }),
		}),
	};
}

export type ItemFilters = {
	words: string;
	available: boolean;
	unavailable: boolean;
	targetedAge: AgeRange;
	regions: Set<number>;
	categories: Set<string>;
};

/**
 * Expose filters for items and utils.
 *
 * filters regroups all the values of the filters
 * isDefault is only true if all filters are set to theirs default value (`words` is ignored).
 * reset sets all filters except `words` to their default value.
 * loadFiltersFromQueryParams loads filters value from item query params.
 * dumpFiltersAsQueryParams returns the item query params from the current filters.
 **/
export function useItemFilters(): {
	filters: Ref<ItemFilters>;
	isDefault: Ref<boolean>;
	reset: () => void;
	loadFiltersFromQueryParams: (queryParams: ItemQueryParams) => void;
	dumpFiltersAsQueryParams: () => ItemQueryParams;
} {
	const defaultFilters = {
		words: "",
		available: true,
		unavailable: false,
		targetedAge: [0, null] as AgeRange,
		regions: new Set<number>(),
		categories: new Set<string>(),
	};

	const filters = ref<ItemFilters>(cloneDeep(defaultFilters));

	const isDefault = computed<boolean>(() =>
		isEqual(unref(filters), defaultFilters),
	);

	function reset() {
		Object.assign(unref(filters), {
			...cloneDeep(defaultFilters),
			words: unref(filters).words,
		});
	}

	function loadFiltersFromQueryParams(queryParams: ItemQueryParams) {
		filters.value = {
			words: queryParams.q?.join(" ") ?? "",
			available: queryParams.av !== ItemQueryAvailability.no,
			unavailable: [
				ItemQueryAvailability.no,
				ItemQueryAvailability.all,
			].includes(queryParams.av ?? ItemQueryAvailability.yes),
			targetedAge: string2range(queryParams.mo ?? "0-"),
			regions: new Set(queryParams.reg ?? []),
			categories: new Set(queryParams.cat ?? []),
		};
	}

	function dumpFiltersAsQueryParams(): ItemQueryParams {
		const { words, available, unavailable, targetedAge, regions, categories } =
			unref(filters);
		const queryParams: ItemQueryParams = {};
		if (words.trim().length > 0)
			queryParams.q = words.split(" ").filter((w: string) => w.length > 0);
		if (!available) {
			queryParams.av = unavailable
				? ItemQueryAvailability.no
				: ItemQueryAvailability.all;
		} else if (unavailable) {
			queryParams.av = ItemQueryAvailability.all;
		}
		if (targetedAge[0] !== 0 || targetedAge[1] !== null)
			queryParams.mo = range2string(targetedAge);
		if (regions.size > 0) queryParams.reg = [...regions];
		if (categories.size > 0) queryParams.cat = [...categories];
		return queryParams;
	}

	return {
		filters,
		isDefault,
		reset,
		loadFiltersFromQueryParams,
		dumpFiltersAsQueryParams,
	};
}
