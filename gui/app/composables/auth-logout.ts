export function useLogout() {
	const { $api } = useNuxtApp();
	const queryCache = useQueryCache();
	const liveChatStore = useLiveChatStore();

	const { mutateAsync: logout, ...mutation } = useMutation({
		mutation: () => {
			return $api("/v1/auth/logout", {
				method: "POST",
			});
		},

		onSettled: () => {
			queryCache.invalidateQueries({ key: ["auth"] });
			queryCache.invalidateQueries({ key: ["me"] });
			liveChatStore.reset();
		},

		onSuccess: () => {
			localStorage.removeItem("auth-session");
		},
	});

	return { logout, ...mutation };
}
