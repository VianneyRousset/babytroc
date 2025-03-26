export const useRequestItemMutation = defineMutation(() => {

  const { $api, $toast } = useNuxtApp();
  const queryCache = useQueryCache();

  return useMutation({
    mutation: (itemId: number) => $api("/v1/items/{item_id}/request", {
      method: "POST",
      path: {
        item_id: itemId,
      }
    }),
    onSuccess: () => $toast.success("Demande d'emprunt envoyé"),
    onError: () => $toast.error("Échec de la demande d'emprunt."),
    onSettled: (data) => {
      queryCache.invalidateQueries({ key: ['me-borrowings-requests'] });
      if (data)
        queryCache.invalidateQueries({ key: ['chat', data.chat_id, "messages"] });
    },
  });
});

export const useUnrequestItemMutation = defineMutation(() => {

  const { $api, $toast } = useNuxtApp();
  const queryCache = useQueryCache();

  return useMutation({
    mutation: (itemId: number) => $api("/v1/items/{item_id}/request", {
      method: "DELETE",
      path: {
        item_id: itemId,
      }
    }),
    onSuccess: () => $toast.success("Demande d'emprunt envoyé"),
    onError: () => $toast.error("Échec de la demande d'emprunt."),
    onSettled: (data) => {
      queryCache.invalidateQueries({ key: ['me-borrowings-requests'] });
      if (data)
        queryCache.invalidateQueries({ key: ['chat', data.chat_id, "messages"] });
    },
  });
});
