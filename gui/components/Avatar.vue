<script setup lang="ts">

import { onMounted, ref } from 'vue';
import { createAvatar } from '@dicebear/core';
import { thumbs } from '@dicebear/collection';

const props = defineProps<{
  seed?: string,
  size?: number,
}>();

const avatar = createAvatar(thumbs, {
  seed: "weloifjwoiegfjew",
  size: props.size ?? 64,
  scale: 80,
  radius: 50,
  backgroundColor: ["c4d6c5"],
  shapeColor: ["729577"],
}).toDataUri();

</script>

<template>
  <img :src="avatar">
</template>

<style lang="scss" scoped>
img {
  vertical-align: middle;
}
</style>
