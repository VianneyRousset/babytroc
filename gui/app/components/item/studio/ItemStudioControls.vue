<script setup lang="ts">
import { Images, Camera, ArrowRight } from 'lucide-vue-next'

const props = withDefaults(defineProps<{
  disableShoot?: boolean
  disableGallery?: boolean
}>(),
{
  disableShoot: false,
  disableGallery: false,
},
)

const { disableShoot, disableGallery } = toRefs(props)

const emit = defineEmits<{
  (e: 'capture'): void
  (e: 'new-image', img: StudioImage): void
}>()
</script>

<template>
  <div class="ItemStudioControls">
    <IconButton
      class="gallery"
      :disabled="disableGallery"
    >
      <Images
        :size="32"
        :stroke-width="1.5"
      />
    </IconButton>
    <IconButton
      class="shoot"
      :disabled="disableShoot"
      @click="!disableShoot && emit('capture')"
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
