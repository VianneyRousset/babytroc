export function useRequestItemMutation(itemId: MaybeRefOrGetter<number>) {
  const { $api, $toast } = useNuxtApp()
  const queryCache = useQueryCache()

  return useMutation({
    key: () => ['item', 'request', toValue(itemId)],
    mutation: () => $api('/v1/items/{item_id}/request', {
      method: 'POST',
      path: {
        item_id: toValue(itemId),
      },
    }),
    onSuccess: () => $toast.success('Demande d\'emprunt envoyé'),
    onError: () => $toast.error('Échec de la demande d\'emprunt.'),
    onSettled: (data) => {
      queryCache.invalidateQueries({ key: ['item', toValue(itemId)] })
      queryCache.invalidateQueries({ key: ['me', 'borrowings', 'requests'] })
      if (data)
        queryCache.invalidateQueries({ key: ['chats', data.chat_id, 'messages'] })
    },
  })
}

export function useUnrequestItemMutation(itemId: MaybeRefOrGetter<number>) {
  const { $api, $toast } = useNuxtApp()
  const queryCache = useQueryCache()

  return useMutation({
    key: () => ['item', 'unrequest', toValue(itemId)],
    mutation: () => $api('/v1/items/{item_id}/request', {
      method: 'DELETE',
      path: {
        item_id: toValue(itemId),
      },
    }),
    onSuccess: () => $toast.success('Demande d\'emprunt supprimée'),
    onError: () => $toast.error('Échec de la demande d\'emprunt.'),
    onSettled: (data) => {
      queryCache.invalidateQueries({ key: ['item', toValue(itemId)] })
      queryCache.invalidateQueries({ key: ['me', 'borrowings', 'requests'] })
      if (data)
        queryCache.invalidateQueries({ key: ['chats', data.chat_id, 'messages'] })
    },
  })
}
