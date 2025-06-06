import { defineStore } from 'pinia'

export function useItemEditStore(name: string) {
  const definition = defineStore(`item-edit-${name}`, () => {
    const studioImages = useStudioImagesUploadStore(name)

    const itemName = ref('')
    const description = ref('')
    const targetedAge = ref<AgeRange>([null, null])
    const regions = ref(new Set<number>())
    const blocked = ref(false)

    const isNameValid = computed(() => unref(itemName).trim().length >= 5 && unref(itemName).trim().length <= 30)
    const isDescriptionValid = computed(() => unref(description).trim().length >= 20 && unref(description).trim().length <= 600)
    const isRegionsValid = computed(() => unref(regions).size > 0)
    const isValid = computed(() => [unref(isNameValid), unref(isDescriptionValid), unref(isRegionsValid)].every(cond => cond === true))

    function reset() {
      itemName.value = ''
      description.value = ''
      targetedAge.value = [null, null]
      unref(regions).clear()
      blocked.value = false
    }

    return {
      name: itemName,
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
