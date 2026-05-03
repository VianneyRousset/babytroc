export function useMe(): {
  me: Ref<UserPrivate | undefined>
  error: Ref<boolean>
  loading: Ref<boolean>
} {
  const {
    data: me,
    asyncStatus,
    status,
  } = useMeQuery()

  const error = computed<boolean>(() => unref(status) === 'error')
  const loading = computed<boolean>(() => unref(asyncStatus) === 'loading')

  return {
    me,
    error,
    loading,
  }
}

/* Loans */

export function useMeLoans({ active }: { active?: boolean } = {}) {
  const { data: loans, ...query } = useApiPaginatedQuery('/v1/me/loans', {
    key: ['me', 'loans', String(active)],
    query: computed(() => ({ a: active })),
    refetchOnMount: false,
  })
  return { loans, ...query }
}

/* Borrowings */

export function useMeBorrowings({ active }: { active?: boolean } = {}) {
  const { data: loans, ...query } = useApiPaginatedQuery('/v1/me/borrowings', {
    key: ['me', 'borrowings', String(active)],
    query: computed(() => ({ a: active })),
    refetchOnMount: false,
  })
  return { loans, ...query }
}

export function useMeBorrowingRequests() {
  const { data: loans, ...query } = useApiPaginatedQuery('/v1/me/borrowings/requests', {
    key: ['me', 'borrowings', 'requests'],
    refetchOnMount: false,
  })
  return { loans, ...query }
}
