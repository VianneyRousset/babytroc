export const useToggleItemLikeMutation = defineMutation(() => {
	const { $api } = useNuxtApp();
	const queryCache = useQueryCache();

	return useMutation({
		mutation: (context: { itemId: number; isLikedByUser: boolean }) => {
			return $api("/v1/me/liked/{item_id}", {
				method: context.isLikedByUser ? "DELETE" : "POST",
				path: {
					item_id: context.itemId,
				},
			});
		},
		onSettled: (_data, _error, vars) => {
			queryCache.invalidateQueries({ key: ["me-liked-items"] });
			queryCache.invalidateQueries({ key: ["item", vars.itemId] });
		},
	});
});
