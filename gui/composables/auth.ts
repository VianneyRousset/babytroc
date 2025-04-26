export function useAuth() {
	const { state: me } = useMeQuery();

	return {
		loggedIn: computed(() => me != null),
	};
}
