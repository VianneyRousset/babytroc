import { useQuery } from "@pinia/colada";

function useLikedItemsQuery() {
	const { $api } = useNuxtApp();

	return useQuery({
		key: () => ["me-liked-items"],
		query: () => $api("/v1/me/liked"),
	});
}

export { useLikedItemsQuery };
