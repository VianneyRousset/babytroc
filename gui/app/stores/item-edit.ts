import { defineStore } from 'pinia'

export function useItemEditStore(storeName: string) {
  const definition = defineStore(`item-edit-${storeName}`, () => {
    const studioImages = useStudioImagesUploadStore(storeName)

    // name
    const name = ref('')
    const description = ref('')
    const targetedAge = ref<AgeRange>([null, null])
    const regions = ref(new Set<number>())
    const blocked = ref(false)

    function reset() {
      name.value = ''
      description.value = ''
      targetedAge.value = [null, null]
      unref(regions).clear()
      blocked.value = false
    }

    return {
      name,
      description,
      targetedAge,
      regions,
      blocked,
      studioImages,
      reset,
    }
  })

  return definition()
}
