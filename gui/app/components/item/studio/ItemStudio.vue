<script setup lang="ts">
import { X } from 'lucide-vue-next'

const images = defineModel<Array<StudioImage>>({ default: [] })

const emit = defineEmits(['exit', 'done'])
const {
  selectedImage,
  disabledNewImage,
  selectImage,
  addImage,
  deleteImage,
  cropSelectedImage,
} = useItemStudioImages(images, { maxImages: 6 })

const mode = ref<'view' | 'crop'>('view')
const camera = useTemplateRef('camera')
</script>

<template>
  <div class="ItemStudio">
    <IconButton
      class="exit"
      :icon="X"
      :size="32"
      @click="emit('exit')"
    />
    <main>
      <transition
        mode="out-in"
        name="fade"
        appear
      >
        <!-- Camera -->
        <ItemStudioCamera
          v-if="selectedImage === undefined"
          ref="camera"
          @new-image="addImage"
        />

        <!-- view -->
        <ItemStudioImageView
          v-else-if="mode === 'view'"
          v-model="selectedImage"
          @delete="selectedImage ? deleteImage(selectedImage.id) : undefined"
          @crop="mode = 'crop'"
        />

        <!-- crop -->
        <ItemStudioImageCrop
          v-else-if="selectedImage !== undefined && mode === 'crop'"
          v-model="selectedImage"
          @crop="(crop) => { cropSelectedImage(crop); mode = 'view' }"
        />
      </transition>
    </main>
    <div class="left" />
    <div class="right" />
    <div class="top">
      <ItemStudioImages
        v-if="mode != 'crop'"
        v-model="images"
        :selected="selectedImage?.id"
        @select="selectImage"
      />
    </div>
    <div class="bottom">
      <ItemStudioControls
        v-if="mode != 'crop'"
        :disable-shoot="disabledNewImage || selectedImage !== undefined"
        :disable-gallery="disabledNewImage"
        @new-image="addImage"
        @capture="camera?.capture()"
        @done="emit('done')"
      />
    </div>
  </div>
</template>

<style scoped lang="scss">
.ItemStudio {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  grid-template-rows: 1fr auto 1fr;
  grid-template-areas:
    "left top     right"
    "left main    right"
    "left bottom  right";
  background: radial-gradient(circle, $neutral-400 0%, black 100%);

  .exit {
    color: white;
    position: absolute;
    top: 1.5em;
    left: 1.5em;
    z-index: 3;
  }

  & > *:not(main) {
    background: rgba(0, 0, 0, 0.6);
    z-index: 2;
  }

  .top {
    grid-area: top;
    @include flex-column;
    justify-content: flex-end;
    padding-bottom: 1em;
  }

  .bottom {
    grid-area: bottom;
    @include flex-column;
    justify-content: flex-start;
    padding-top: 3em;
  }

  .left {
    grid-area: left;
  }

  .right {
    grid-area: right;
  }

  main {
    position: relative;
    grid-area: main;
    aspect-ratio: 1;
    width: min(100vw, 50vh);
    max-width: 800px;
    box-shadow: 0 0 12px rgba(0, 0, 0, 0.5);

    & > * {
      width: 100%;
      height: 100%;
    }
  }
}
</style>
