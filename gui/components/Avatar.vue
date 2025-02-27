<script setup lang="ts">

import { onMounted, ref } from 'vue';
import { createAvatar } from '@dicebear/core';
import { thumbs } from '@dicebear/collection';

const props = withDefaults(defineProps<{
  seed: string | null,
  size?: number,
}>(), {
  size: 64,
});

const { seed, size } = toRefs(props);

const avatar = computed(() => createAvatar(thumbs, {
  seed: unref(seed) ?? "",
  size: unref(size),
  scale: 80,
  radius: 50,
  backgroundColor: ["c4d6c5"],
  shapeColor: ["729577"],
}).toDataUri());

const sizePx = computed(() => `${unref(size)}px`);

</script>

<template>
  <div class="Avatar">
    <img v-if="seed !== undefined" :src="avatar">
  </div>
</template>

<style lang="scss" scoped>
.Avatar {
  @include flex-row-center;

  width: v-bind(sizePx);
  height: v-bind(sizePx);

  background: $neutral-100;
  border-radius: 50%;

  img {
    vertical-align: middle;
  }


}
</style>
