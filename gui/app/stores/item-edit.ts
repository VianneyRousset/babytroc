import { defineStore } from 'pinia'

export function useItemEditStore(storeName: string) {
  const definition = defineStore(`item-edit-${storeName}`, () => {
    const studioImages = useStudioImagesUploadStore(storeName)

    // name
    const name = ref('')
    const nameValid = ref(false)

    // description
    const description = ref('')
    const descriptionValid = ref(false)

    // age
    const targetedAge = ref<AgeRange>([null, null])

    // regions
    const regions = ref(new Set<number>())

    // options
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
      nameValid,
      description,
      descriptionValid,
      targetedAge,
      regions,
      blocked,
      studioImages,
      reset,
    }
  })

  return definition()
}
