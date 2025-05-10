export const useRequestItemMutation = defineMutation(() => {
  const { $api, $toast } = useNuxtApp()
  const queryCache = useQueryCache()

  return useMutation({
    mutation: (itemId: number) =>
      $api('/v1/items/{item_id}/request', {
        method: 'POST',
        path: {
          item_id: itemId,
        },
      }),
    onSuccess: () => $toast.success('Demande d\'emprunt envoyé'),
    onError: () => $toast.error('Échec de la demande d\'emprunt.'),
    onSettled: (data) => {
      queryCache.invalidateQueries({ key: ['me', 'borrowings', 'requests'] })
      if (data)
        queryCache.invalidateQueries({
          key: ['chats', data.chat_id, 'messages'],
        })
    },
  })
})

export const useUnrequestItemMutation = defineMutation(() => {
  const { $api, $toast } = useNuxtApp()
  const queryCache = useQueryCache()

  return useMutation({
    mutation: (itemId: number) =>
      $api('/v1/items/{item_id}/request', {
        method: 'DELETE',
        path: {
          item_id: itemId,
        },
      }),
    onSuccess: () => $toast.success('Demande d\'emprunt envoyé'),
    onError: () => $toast.error('Échec de la demande d\'emprunt.'),
    onSettled: (data) => {
      queryCache.invalidateQueries({ key: ['me', 'borrowings', 'requests'] })
      if (data)
        queryCache.invalidateQueries({
          key: ['chats', data.chat_id, 'messages'],
        })
    },
  })
})

export const useAcceptLoanRequestMutation = defineMutation(() => {
  const { $api, $toast } = useNuxtApp()
  const queryCache = useQueryCache()

  return useMutation({
    mutation: ({
      itemId,
      loanRequestId,
    }: { itemId: number, loanRequestId: number }) =>
      $api('/v1/me/items/{item_id}/requests/{loan_request_id}/accept', {
        method: 'POST',
        path: {
          item_id: itemId,
          loan_request_id: loanRequestId,
        },
      }),
    onSuccess: () => $toast.success('Demande d\'emprunt acceptée.'),
    onError: () =>
      $toast.error('Échec de l\'acceptation de la demande d\'emprunt.'),
    onSettled: (_data, _error, { itemId }) => {
      queryCache.invalidateQueries({
        key: ['me', 'items', itemId, 'requests'],
      })
    },
  })
})

export const useRejectLoanRequestMutation = defineMutation(() => {
  const { $api, $toast } = useNuxtApp()
  const queryCache = useQueryCache()

  return useMutation({
    mutation: ({
      itemId,
      loanRequestId,
    }: { itemId: number, loanRequestId: number }) =>
      $api('/v1/me/items/{item_id}/requests/{loan_request_id}/reject', {
        method: 'POST',
        path: {
          item_id: itemId,
          loan_request_id: loanRequestId,
        },
      }),
    onSuccess: () => $toast.success('Demande d\'emprunt rejetée.'),
    onError: () => $toast.error('Échec du rejet de la demande d\'emprunt.'),
    onSettled: (_data, _error, { itemId }) => {
      queryCache.invalidateQueries({
        key: ['me', 'items', itemId, 'requests'],
      })
    },
  })
})

export const useExecuteLoanRequestMutation = defineMutation(() => {
  const { $api, $toast } = useNuxtApp()

  return useMutation({
    mutation: ({ loanRequestId }: { loanRequestId: number }) =>
      $api('/v1/me/borrowings/requests/{loan_request_id}/execute', {
        method: 'POST',
        path: {
          loan_request_id: loanRequestId,
        },
      }),
    onSuccess: () => $toast.success('Emprunt commencé.'),
    onError: () => $toast.error('Échec de l\'emprunt.'),
  })
})

export const useEndLoanMutation = defineMutation(() => {
  const { $api, $toast } = useNuxtApp()
  const queryCache = useQueryCache()

  return useMutation({
    mutation: ({ loanId }: { loanId: number }) =>
      $api('/v1/me/loans/{loan_id}/end', {
        method: 'POST',
        path: {
          loan_id: loanId,
        },
      }),
    onSuccess: () => $toast.success('Emprunt commencé.'),
    onError: () => $toast.error('Échec de l\'emprunt.'),
    onSettled: (_data, _error, { loanId }) => {
      queryCache.invalidateQueries({ key: ['me', 'loans', loanId] })
    },
  })
})
