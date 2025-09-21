import type { RouteLocationGeneric } from 'vue-router'

export function useItemLoanRequest({ itemId }: { itemId: MaybeRefOrGetter<number> }): {
  request: () => Promise<{ loanRequest: LoanRequest, chatLocation: RouteLocationGeneric }>
  unrequest: () => Promise<void>
  error: Ref<boolean>
  loading: Ref<boolean>
} {
  const {
    mutateAsync: requestMutateAsync,
    status: requestMutateStatus,
    asyncStatus: requestMutateAsyncStatus,
  } = useRequestItemMutation(itemId)

  const {
    mutateAsync: unrequestMutateAsync,
    status: unrequestMutateStatus,
    asyncStatus: unrequestMutateAsyncStatus,
  } = useUnrequestItemMutation(itemId)

  const router = useRouter()

  async function request() {
    const loanRequest = await requestMutateAsync()
    const chatLocation = router.resolve({
      name: 'chats-chat_id',
      params: {
        chat_id: loanRequest.chat_id,
      },
    })
    return { loanRequest, chatLocation }
  }

  const error = computed<boolean>(() => {
    return unref(requestMutateStatus) === 'error' || unref(unrequestMutateStatus) === 'error'
  })
  const loading = computed<boolean>(() => {
    return unref(requestMutateAsyncStatus) === 'loading' || unref(unrequestMutateAsyncStatus) === 'loading'
  })

  return {
    request,
    unrequest: async () => {
      await unrequestMutateAsync()
    },
    error,
    loading,
  }
}
