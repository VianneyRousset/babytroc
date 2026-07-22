export const useChatsQuery = defineQuery(() => {
	const { loggedIn } = useAuth();
	return useApiPaginatedQuery("/v1/me/chats", {
		key: ["me", "chats"],
		enabled: () => {
			return unref(loggedIn) === true;
		},
	});
});
