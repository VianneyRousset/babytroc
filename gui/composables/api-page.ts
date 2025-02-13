import type { paths as ApiPaths } from '#open-fetch-schemas/api'
import type { OpenFetchOptions, UseOpenFetchClient } from '#imports'
import type { Awaited } from '@vueuse/core';

type PaginatedAsyncApiData = Awaited<ReturnType<typeof useApi>> & {
  more: () => Promise<void>,
};



export const usePaginatedApi = <Path extends keyof ApiPaths>(url: Path, options: OpenFetchOptions = {}): PaginatedAsyncApiData => {

  const { $api } = useNuxtApp()

  const pending = ref(false);
  //const data = ref([]) as Ref<EnsureArray<ExtractResponseType<Path>>>;

  const { data, status, error, ...asyncData } = useApi(url, options);

  async function more() {
    try {
      status.value = "pending";
      const newData = await $api(url, options);
      data.value = data.value?.concat(newData);
      status.value = "success";
    } catch (err) {
      //error.value = err as ErrorT;
      status.value = "error";
    }
  }

  return {
    data,
    status,
    error,
    more,
    ...asyncData,
  }
}
