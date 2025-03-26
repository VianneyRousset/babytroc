import { useInfiniteQuery, useQuery } from '@pinia/colada'
import { parseLinkHeader } from '@web3-storage/parse-link-header'
import type { UseInfiniteQueryOptions } from '@pinia/colada';

interface TypesConfig { };
type ErrorDefault = TypesConfig extends Record<'defaultError', infer E> ? E : Error;

const sleep = (ms: number) => new Promise(resolve => setTimeout(resolve, ms));


function useIQ<TResult, TError = ErrorDefault, TPage = unknown>(
  options: UseInfiniteQueryOptions<TResult, TError, TResult | undefined, TPage>,
) {
  let pages: TPage = toValue(options.initialPage)

  const { refetch, refresh, ...query } = useQuery<TPage, TError, TPage>({
    ...options,
    initialData: () => toValue(options.initialPage),
    // since we hijack the query function and augment the data, we cannot refetch the data
    // like usual
    staleTime: Infinity,
    async query(context) {
      const data: TResult = await options.query(context.data, context)
      return (pages = options.merge(context.data, data))
    },
  })

  return {
    ...query,
    loadMore: () => refetch(),
  }
}


const useTestInfiniteQuery = defineQuery(() => {

  const arg = ref<string>("a");

  const { ...query } = useInfiniteQuery({
    key: () => ["test", unref(arg)],

    initialPage: {
      data: Array<string>(),
      cursor: 0 as number,
    },

    query: async (pages) => {

      console.log("query", pages);
      await sleep(1000);

      if (pages.cursor === 5)
        return null;

      return [`${unref(arg)}${pages.cursor}`];
    },

    merge: (pages, newData) => {

      console.log("merge", pages.data.length);

      if (newData === null) {
        console.log("end");
        return pages;
      }

      return {
        data: [...toValue(pages.data), ...toValue(newData)],
        cursor: pages.cursor + 1,
      }
    },
    enabled: typeof document !== 'undefined',
  });

  return {
    arg,
    ...query,
  };
});

export { useTestInfiniteQuery }
