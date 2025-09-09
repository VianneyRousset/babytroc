import { defineStore } from 'pinia'

export const useItemExploreStore = defineStore(`item-explore`, () => {
  const queryParams = ref<ItemQueryParams | undefined>(undefined)
  const scrollY = ref<number>(0)
  return { queryParams, scrollY }
})
