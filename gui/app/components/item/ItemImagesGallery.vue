<script setup lang="ts">
const props = defineProps<{
  item: Item
}>()

const { item } = toRefs(props)

const { imagesPaths } = useItemImages(item)
</script>

<template>
  <ImageGallery
    class="ItemImagesGallery"
    :images="imagesPaths"
  />
</template>

<style lang="scss" scoped></style>
