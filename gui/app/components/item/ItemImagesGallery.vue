<script setup lang="ts" generic="T extends { image_names: Array<string> }">
const props = withDefaults(
	defineProps<{
		item: T;
		wide?: boolean;
	}>(),
	{
		wide: false,
	},
);

const { item, wide } = toRefs(props);

const { imagesNames } = useItemImages(item);
</script>

<template>
  <ImageGallery
    class="ItemImagesGallery"
    :images="imagesNames"
    :config="{ itemsToShow: wide ? 2.5 : 1 }"
  />
</template>
