import { defineStore } from "pinia";
import { isEqual } from "lodash";

type ItemsListStore = () => PaginatedSource<ItemPreview> & {
	setQuery: (query: ItemQuery) => void;
};

const useItemsListStore: ItemsListStore = defineStore("itemsList", () => {
	var query: ItemQuery = reactive({
		n: 16,
	});

	const { data, more, error, end, reset, status } = usePaginatedFetch(
		"/v1/items",
		{
			query: query,
			timeout: 10_000, // 10s
		},
	);

	function setQuery(newQuery: ItemQuery) {
		// skip if no changes
		if (isEqual(query, newQuery)) return;

		assign(query, { ...newQuery, n: 16 }, { remove: true });
	}

	return {
		data,
		more,
		reset,
		end,
		error,
		status,
		setQuery,
	};
});

export { useItemsListStore };
