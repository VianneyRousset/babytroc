export const useLoginMutation = defineMutation(() => {
	const { $api } = useNuxtApp();
	const queryCache = useQueryCache();

	return useMutation({
		mutation: (ctx: { username: string; password: string }) => {
			// create form data
			const formData = new FormData();
			formData.append("grant_type", "password");
			formData.append("username", ctx.username);
			formData.append("password", ctx.password);

			return $api("/v1/auth/login", {
				method: "POST",
				// @ts-expect-error: cannot type FormData
				body: formData,
			});
		},

		onSettled: () => {
			queryCache.invalidateQueries({ key: ["me"] });
			queryCache.invalidateQueries({ key: ["auth"] });
		},

		onSuccess: () => {
			localStorage.setItem("auth-session", "true");
		},
	});
});

export const useLogoutMutation = defineMutation(() => {
	const { $api, $toast } = useNuxtApp();
	const queryCache = useQueryCache();

	return useMutation({
		mutation: () => {
			return $api("/v1/auth/logout", {
				method: "POST",
			});
		},

		onSettled: () => {
			queryCache.invalidateQueries({ key: ["me"] });
			queryCache.invalidateQueries({ key: ["auth"], exact: true });
		},

		onSuccess: () => {
			localStorage.removeItem("auth-session");
		},

		onError: () => $toast("Échec de la déconnection."),
	});
});
