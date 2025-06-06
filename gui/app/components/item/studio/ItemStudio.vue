<script setup lang="ts">
const props = defineProps<{
  initImages: Array<StudioImage>
}>()

const { initImages } = toRefs(props)

const camera = useTemplateRef('camera')

const images = ref(Array<StudioImage>())

watch(initImages, (_initImages) => {
  images.value = [..._initImages]
}, { immediate: true })

const emit = defineEmits<(event: 'done', images: Array<StudioImage>) => void>()

const selectedImage = ref<StudioImage | undefined>(undefined)
const mode = ref<'view' | 'crop'>('view')

function addImage(img: StudioImage) {
  const _images = unref(images)

  if (_images.length >= 6)
    return

  _images.push(img)
}

function selectImage(id: number | undefined) {
  mode.value = 'view'
  selectedImage.value = unref(images).find(img => img.id === id)
}

function deleteImage(id: number) {
  const _images = unref(images)

  // get selected image index
  const index: number | undefined = images.value.findIndex(img => img.id === id)
  const nextIndex = Math.min(Math.max(0, index - 1), _images.length - 1)

  // remove image from array
  images.value = unref(images).filter(img => img.id !== id)

  selectedImage.value = unref(images)[nextIndex]
}

function cropSelectedImage(crop: StudioImageCrop) {
  const _selectedImage = unref(selectedImage)

  if (_selectedImage == null)
    return

  _selectedImage.crop.width = crop.width
  _selectedImage.crop.height = crop.height
  _selectedImage.crop.top = crop.top
  _selectedImage.crop.left = crop.left
}

async function done() {
  emit('done', toRaw(unref(images)))
}
</script>

<template>
  <div
    ref="studio"
    class="ItemImagesStudio"
  >
    <!-- top -->
    <div class="top">
      <ItemStudioImages
        v-if="mode != 'crop'"
        v-model="images"
        :selected="selectedImage?.id"
        @select="selectImage"
      />
    </div>

    <!-- center -->
    <AspectRatio
      :ratio="1"
      class="center"
    >
      <!-- video -->
      <ItemStudioCamera
        v-if="selectedImage === undefined"
        ref="camera"
        @new-image="addImage"
      />

      <!-- view -->
      <ItemStudioImageView
        v-if="selectedImage !== undefined && mode === 'view'"
        v-model="selectedImage"
        @delete="selectedImage ? deleteImage(selectedImage.id) : undefined"
        @crop="mode = 'crop'"
      />

      <!-- crop -->
      <ItemStudioImageCrop
        v-if="selectedImage !== undefined && mode === 'crop'"
        v-model="selectedImage"
        @crop="(crop) => { cropSelectedImage(crop); mode = 'view' }"
      />
    </AspectRatio>

    <!-- bottom -->
    <div class="bottom">
      <transition
        name="pop"
        mode="in-out"
        appear
      >
        <ItemStudioControls
          v-if="mode != 'crop'"
          :disable-shoot="images.length >= 6 || selectedImage !== undefined"
          :disable-gallery="images.length >= 6"
          :disable-done="images.length == 0"
          @new-image="addImage"
          @capture="camera?.capture()"
          @done="done()"
        />
      </transition>
    </div>

    <!-- header -->
    <div class="header">
      <slot name="header" />
    </div>
  </div>
</template>

<style lang="scss" scoped>
.ItemImagesStudio {
  @include flex-column-center;
  position: relative;
  align-items: stretch;
  background: radial-gradient(circle, $neutral-400 0%, black 100%);

  .header {
    @include flex-row;
    z-index: 2;
    gap: 16px;
    height: 64px;
    position: absolute;
    top: 0px;
    box-sizing: border-box;
    width: 100%;
    color: white;
    padding: 0 1rem;

    :deep(a) {
      @include reset-link;
    }

    :deep(h1) {
      @include ellipsis-overflow;
      position: relative;
      top: -0.1rem;
      flex-grow: 1;
      margin: 0;
      font-weight: 500;
      font-size: 1.6rem;
    }

  }

  .top, .bottom {
    background: rgba(0, 0, 0, 0.75);
    flex: 1;
    z-index: 1;
  }

  :deep(.center) {
    &>* {
      width: 100%;
      height: 100%;
    }
  }

  .top {
    @include flex-column;
    justify-content: flex-end;
  }

  .bottom {
    @include flex-column-center;
  }
}
</style>
