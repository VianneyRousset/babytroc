import { useQuery } from "@pinia/colada";

export function useUserQuery(userId: MaybeRefOrGetter<number>) {
	const { $api } = useNuxtApp();

	return useQuery({
		key: () => ["users", toValue(userId)],
		query: () =>
			$api("/v1/users/{user_id}", {
				path: {
					user_id: toValue(userId),
				},
			}),
	});
}
