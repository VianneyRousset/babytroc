import { useQuery } from "@pinia/colada";

// TODO check paginated
export function useBorrowingsListQuery() {
	const { $api } = useNuxtApp();

	return useQuery({
		key: () => ["me", "borrowings"],
		query: () => $api("/v1/me/borrowings"),
	});
}

export function useBorrowingsLoanRequestsListQuery() {
	const { $api } = useNuxtApp();

	return useQuery({
		key: () => ["me", "borrowings", "requests"],
		query: () => $api("/v1/me/borrowings/requests"),
	});
}

export function useBorrowingsLoanRequestQuery(
	loanRequestId: MaybeRefOrGetter<number>,
) {
	const { $api } = useNuxtApp();

	return useQuery({
		key: () => ["me", "borrowings", "requests", toValue(loanRequestId)],
		query: () =>
			$api("/v1/me/borrowings/requests/{loan_request_id}", {
				path: {
					loan_request_id: toValue(loanRequestId),
				},
			}),
	});
}

export function useItemLoanRequestsListQuery(itemId: MaybeRefOrGetter<number>) {
	const { $api } = useNuxtApp();

	return useQuery({
		key: () => ["me", "items", toValue(itemId), "requests"],
		query: () =>
			$api("/v1/me/items/{item_id}/requests", {
				path: {
					item_id: toValue(itemId),
				},
			}),
	});
}

export function useItemLoanRequestQuery({
	itemId,
	loanRequestId,
}: {
	itemId: MaybeRefOrGetter<number>;
	loanRequestId: MaybeRefOrGetter<number>;
}) {
	const { $api } = useNuxtApp();

	return useQuery({
		key: () => [
			"me",
			"items",
			toValue(itemId),
			"requests",
			toValue(loanRequestId),
		],
		query: () =>
			$api("/v1/me/items/{item_id}/requests/{loan_request_id}", {
				path: {
					item_id: toValue(itemId),
					loan_request_id: toValue(loanRequestId),
				},
			}),
	});
}

export function useLoanQuery({ loanId }: { loanId: MaybeRefOrGetter<number> }) {
	const { $api } = useNuxtApp();

	return useQuery({
		key: () => ["me", "loans", toValue(loanId)],
		query: () =>
			$api("/v1/me/loans/{loan_id}", {
				path: {
					loan_id: toValue(loanId),
				},
			}),
	});
}
