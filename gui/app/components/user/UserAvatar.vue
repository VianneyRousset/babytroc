<script setup lang="ts">
import { createAvatar } from '@dicebear/core'
import { thumbs } from '@dicebear/collection'

const props = withDefaults(
  defineProps<{
    seed: string | null
    size?: number
  }>(),
  {
    size: 64,
  },
)

const { seed, size } = toRefs(props)

const avatar = computed(() =>
  createAvatar(thumbs, {
    seed: unref(seed) ?? '',
    size: unref(size),
    scale: 80,
    radius: 50,
    backgroundColor: ['c4d6c5'],
    shapeColor: ['729577'],
  }).toDataUri(),
)
</script>

<template>
  <img
    v-if="seed"
    class="UserAvatar"
    :src="avatar"
  >
</template>

<style lang="scss" scoped>
.UserAvatar {
  @include flex-row-center;

  aspect-ratio: 1;

  background: $neutral-100;
  border-radius: 50%;

  img {
    vertical-align: middle;
  }
}
</style>
