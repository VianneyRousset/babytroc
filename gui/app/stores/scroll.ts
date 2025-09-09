import { defineStore } from 'pinia'

export function useSavedScrollStore(name: string) {
  const definition = defineStore(`saved-scroll-${name}`, () => {
    const x = ref<number>(0)
    const y = ref<number>(0)
    return { x, y }
  })
  return definition()
}
