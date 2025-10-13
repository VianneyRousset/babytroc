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

export function useMeLoans() {
  const { data: loans, ...query } = useApiPaginatedQuery('/v1/me/loans', {
    key: ['me', 'loans'],
  })
  return { loans, ...query }
}

/* Borrowings */

export function useMeBorrowings() {
  const { data: loans, ...query } = useApiPaginatedQuery('/v1/me/borrowings', {
    key: ['me', 'borrowings'],
  })
  return { loans, ...query }
}

export function useMeBorrowingRequests() {
  const { data: loans, ...query } = useApiPaginatedQuery('/v1/me/borrowings/requests', {
    key: ['me', 'borrowings', 'requests'],
  })
  return { loans, ...query }
}
