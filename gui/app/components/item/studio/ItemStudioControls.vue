<script setup lang="ts">
import { Images, Camera, ArrowRight } from 'lucide-vue-next'

const props = withDefaults(defineProps<{
  disableShoot?: boolean
  disableGallery?: boolean
  disableDone?: boolean
}>(),
{
  disableShoot: false,
  disableGallery: false,
  disableDone: false,
},
)

const emit = defineEmits<{
  (event: 'capture' | 'done'): void
  (event: 'new-image', img: StudioImage): void
}>()

const { disableShoot, disableGallery } = toRefs(props)

const { open, onChange } = useFileDialog({
  accept: 'image/*',
  reset: true,
})

onChange((files) => {
  for (const file of files ?? [])
    emitImageFromFile(file)
})

function emitImageFromFile(file: File) {
  const fileReader = new FileReader()
  fileReader.onload = () => {
    if (typeof fileReader.result !== 'string')
      throw new Error('File reader result is not a string')

    const img: StudioImage = useStudioImage(fileReader.result, 'center')
    emit('new-image', img)
  }
  fileReader.readAsDataURL(file)
}
</script>

<template>
  <div class="ItemStudioControls">
    <IconButton
      class="gallery"
      :disabled="disableGallery"
      @click="!disableGallery && open()"
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
    <IconButton
      class="done"
      :disabled="disableDone"
    >
      <ArrowRight
        :size="32"
        :stroke-width="1.5"
        @click="!disableDone && emit('done')"
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

  .IconButton.done {
    width: 60px;
    height: 60px;
    border-radius: 50%;
    background: $primary-400;
  }

}
</style>
