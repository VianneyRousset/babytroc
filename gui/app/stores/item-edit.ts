import { defineStore } from 'pinia'
import type { AsyncDataRequestStatus as AsyncStatus } from '#app'

export function useItemEditStore(storeName: string) {
  const definition = defineStore(`item-edit-${storeName}`, () => {
    const studioImages = useStudioImagesUploadStore(storeName)

    // name
    const name = ref('')
    const description = ref('')
    const targetedAge = ref<AgeRange>([null, null])
    const regions = ref(new Set<number>())
    const blocked = ref(false)

    const isNameValid = computed(() => unref(name).trim().length >= 5 && unref(name).trim().length <= 30)
    const isDescriptionValid = computed(() => unref(description).trim().length >= 20 && unref(description).trim().length <= 600)
    const isRegionsValid = computed(() => unref(regions).size > 0)
    const isValid = computed(() => [unref(isNameValid), unref(isDescriptionValid), unref(isRegionsValid)].every(cond => cond === true))

    function reset() {
      name.value = ''
      description.value = ''
      targetedAge.value = [null, null]
      unref(regions).clear()
      blocked.value = false
    }

    return {
      name,
      isNameValid,
      description,
      isDescriptionValid,
      targetedAge,
      regions,
      isRegionsValid,
      blocked,
      isValid,
      studioImages,
      reset,
    }
  })

  return definition()
}
