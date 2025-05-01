<script setup lang="ts">
import { Heart } from "lucide-vue-next";

import type { AsyncStatus } from "@pinia/colada";

const props = defineProps<{
	item: Item;
}>();

const {item} = toRefs(props);

const { imagesPaths } = useItemImages(item);

</script>

<template>
  <Gallery :images="imagesPaths" />
</template>

<style lang="scss" scoped></style>
