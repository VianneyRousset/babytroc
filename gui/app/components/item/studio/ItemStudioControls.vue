<script setup lang="ts">
import { Images, Camera, ArrowRight } from 'lucide-vue-next'

const props = defineProps<{
  video: HTMLVideoElement,
}>()

const { video } = toRefs(props)

const emit = defineEmits<(e: 'new-image', value: string) => void>()

const { capture } = useVideoCamera(video)
</script>

<template>
  <div class="ItemStudioControls">
    <IconButton class="gallery">
      <Images
        :size="32"
        :stroke-width="1.5"
      />
    </IconButton>
    <IconButton
      class="shoot"
      @click="emit('new-image', capture({ cropRatio: 1 }))"
    >
      <Camera
        :size="48"
        :stroke-width="1.5"
      />
    </IconButton>
    <IconButton class="continue">
      <ArrowRight
        :size="32"
        :stroke-width="1.5"
      />
    </IconButton>
  </div>
</template>

<style lang="scss" scoped>
.ItemStudioControls {
  @include flex-row-center;
  align-self: center;
  width: 80%;
  max-width: 350px;
  min-width: 200px;
  justify-content: space-between;
  align-items: center;
  height: clamp(100px, 20%, 160px);
  color: white;

  .IconButton.gallery {
    width: 60px;
    height: 60px;
  }

  .IconButton.shoot {
    width: 100px;
    height: 100px;
    border-radius: 50%;
    background: $neutral-200;
    color: $neutral-600;
    border: 1px solid $neutral-600;
  }

  .IconButton.continue {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: $primary-400;
  }

}
</style>
