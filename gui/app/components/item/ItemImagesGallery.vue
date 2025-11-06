<script setup lang="ts" generic="T extends { images_names: Array<string> }">
const props = withDefaults(defineProps<{
  item: T
  wide?: boolean
}>(), {
  wide: false,
})

const { item, wide } = toRefs(props)

const { imagesPaths } = useItemImages(item)
</script>

<template>
  <ImageGallery
    class="ItemImagesGallery"
    :images="imagesPaths"
    :config="{ itemsToShow: wide ? 2.5 : 1 }"
  />
</template>

<style lang="scss" scoped></style>
