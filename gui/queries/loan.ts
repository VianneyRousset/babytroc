import { useQuery } from '@pinia/colada'


export function useLoanRequestsQuery() {

  const { $api } = useNuxtApp();

  return useQuery({
    key: () => ["me-borrowings-requests"],
    query: () => $api("/v1/me/borrowings/requests"),
  });
}

export function useItemLoanRequestsQuery(itemId: MaybeRefOrGetter<number>) {

  const { $api } = useNuxtApp();

  return useQuery({
    key: () => ["me", "item", toValue(itemId), "requests"],
    query: () => $api("/v1/me/items/{item_id}/requests", {
      path: {
        item_id: toValue(itemId),
      }
    }),
  });
}
