export function useMeBorrowings() {
  const {
    data: loans,
    ...query
  } = useApiPaginatedQuery('/v1/me/borrowings', {
    key: ['me', 'borrowings'],
  })

  return { loans, ...query }
}
