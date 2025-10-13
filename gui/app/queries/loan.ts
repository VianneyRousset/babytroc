/*
export const useBorrowingsListQuery = defineQuery(() => {
  const { $api } = useNuxtApp()

  const defaultQueryParams: LoanQuery = {
    n: 32,
  }
  const queryParams = ref<ItemQuery>({})

  const { ...query } = useInfiniteQuery({
    key: () => ['items', unref(queryParams)],

    initialPage: {
      data: Array<ItemPreview>(),
      cursor: {} as ItemQuery,
      end: false,
    },

    query: async (pages) => {
      let newCursor: ItemQuery = {}

      const newData = await $api('/v1/items', {
        query: {
          ...defaultQueryParams,
          ...unref(queryParams),
          ...pages.cursor,
        },

        onResponse: async ({
          response: { ok, headers },
        }: { response: { ok: boolean, headers: Headers } }) => {
          if (!ok) return

          const linkHeader = parseLinkHeader(headers.get('link'))

          if (!linkHeader?.next)
            return console.error('Null linkHeader when fetching first items.')

          const { rel, url, ...query } = linkHeader.next
          newCursor = query
        },
      })

      return {
        data: newData,
        cursor: newCursor,
      }
    },

    merge: (pages, newPage) => {
      if (newPage.data.length === 0) {
        return {
          ...pages,
          end: true,
        }
      }

      return {
        data: [...pages.data, ...newPage.data],
        cursor: newPage.cursor,
        end: false,
      }
    },
  })

  return {
    ...query,
    query: queryParams,
  }
}
*/

export function useBorrowingsLoanRequestQuery(
  loanRequestId: MaybeRefOrGetter<number>,
) {
  const { $api } = useNuxtApp()

  return useQueryWithAuth({
    key: () => ['me', 'borrowings', 'requests', toValue(loanRequestId)],
    query: () =>
      $api('/v1/me/borrowings/requests/{loan_request_id}', {
        path: {
          loan_request_id: toValue(loanRequestId),
        },
      }),
  })
}

export function useItemLoanRequestsListQuery(itemId: MaybeRefOrGetter<number>) {
  const { $api } = useNuxtApp()

  return useQueryWithAuth({
    key: () => ['me', 'items', toValue(itemId), 'requests'],
    query: () =>
      $api('/v1/me/items/{item_id}/requests', {
        path: {
          item_id: toValue(itemId),
        },
      }),
  })
}

export function useItemLoanRequestQuery({
  itemId,
  loanRequestId,
}: {
  itemId: MaybeRefOrGetter<number>
  loanRequestId: MaybeRefOrGetter<number>
}) {
  const { $api } = useNuxtApp()

  return useQueryWithAuth({
    key: () => [
      'me',
      'items',
      toValue(itemId),
      'requests',
      toValue(loanRequestId),
    ],
    query: () =>
      $api('/v1/me/items/{item_id}/requests/{loan_request_id}', {
        path: {
          item_id: toValue(itemId),
          loan_request_id: toValue(loanRequestId),
        },
      }),
  })
}

export function useLoanQuery({ loanId }: { loanId: MaybeRefOrGetter<number> }) {
  const { $api } = useNuxtApp()

  return useQueryWithAuth({
    key: () => ['me', 'loans', toValue(loanId)],
    query: () =>
      $api('/v1/me/loans/{loan_id}', {
        path: {
          loan_id: toValue(loanId),
        },
      }),
  })
}
