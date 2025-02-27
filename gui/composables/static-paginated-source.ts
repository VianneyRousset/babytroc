function useStaticPaginatedSource<T>(data: Array<T>): PaginatedSource<T> {
  return {
    data,
    more: async () => { },
    reset: () => { },
    end: true,
    error: null,
    status: "success",
  };
}

export { useStaticPaginatedSource };
