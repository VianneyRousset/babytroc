<script setup lang="ts">
import { Check } from 'lucide-vue-next'
import { Cropper } from 'vue-advanced-cropper'
import 'vue-advanced-cropper/dist/style.css'

const img = defineModel<StudioImage>()
const emit = defineEmits<(event: 'crop', crop: StudioImageCrop) => void>()
const cropperElement = useTemplateRef('cropper')

function emitCrop() {
  const _img = unref(img)
  const _cropper = unref(cropperElement)

  if (_img == null)
    throw new Error('img not defined')

  if (_cropper == null)
    throw new Error('cropper not defined')

  const { visibleArea } = _cropper.getResult()
  emit('crop', visibleArea)
}
</script>

<template>
  <div
    class="ItemStudioImageCrop"
  >
    <cropper
      v-if="img"
      ref="cropper"
      :src="img?.original"
      :stencil-size="{
        width: 400,
        height: 400,
      }"
      :stencil-props="{
        aspectRatio: 1,
        movable: false,
        resizable: false,
        handlers: {},
        lines: {},
      }"
      :default-visible-area="img.crop"
      :resize-image="{
        adjustStencil: false,
      }"
      image-restriction="stencil"
    />
    <transition
      name="pop"
      mode="in-out"
      appear
    >
      <IconButton
        class="done"
        @click="emitCrop"
      >
        <Check
          :size="24"
          :stroke-width="1.33"
        />
        <div>Enregister</div>
      </IconButton>
    </transition>
  </div>
</template>

<style lang="scss" scoped>
.ItemStudioImageCrop {

  :deep(.vue-advanced-cropper) {
    width: 100%;
    height: 100%;

    * {
      overflow: visible;
    }

  }

  .IconButton {
    position: absolute;
    color: white;
    background: rgba(0, 0, 0, 0.5);
    border-radius: 20px;
    height: 40px;
    width: 40px;
    cursor: pointer;

    &.done {
      gap: 0.5rem;
      padding: 0 10px;
      left: 0;
      right: 0;
      bottom: 1rem;
      margin-inline: auto;
      width: fit-content;
    }
  }
}
</style>
