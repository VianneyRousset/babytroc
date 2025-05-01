export const useSaveItemMutation = defineMutation(() => {
	const { $api, $toast } = useNuxtApp();
	const queryCache = useQueryCache();

	return useMutation({
		mutation: (itemId: number) => {
			return $api("/v1/me/saved/{item_id}", {
				method: "POST",
				path: {
					item_id: itemId,
				},
			});
		},
		onSuccess: () => $toast.success("Objet sauvegardé."),
		onError: () => $toast.error("Échec de la sauvegarde de l'objet."),
		onSettled: () =>
			queryCache.invalidateQueries({ key: ["me", "saved-items"] }),
	});
});

export const useUnsaveItemMutation = defineMutation(() => {
	const { $api, $toast } = useNuxtApp();
	const queryCache = useQueryCache();

	return useMutation({
		mutation: (itemId: number) => {
			return $api("/v1/me/saved/{item_id}", {
				method: "DELETE",
				path: {
					item_id: itemId,
				},
			});
		},
		onSettled: () =>
			queryCache.invalidateQueries({ key: ["me", "saved-items"] }),
		onError: () => $toast.error("Échec de l'oublie de l'objet."),
	});
});
