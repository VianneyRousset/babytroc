<script setup lang="ts">
const images = ref(Array<StudioImage>())

const video = useTemplateRef<HTMLVideoElement>('video')
const studio = useTemplateRef<HTMLElement>('studio')
const { width } = useElementSize(
  studio,
  undefined,
  { box: 'border-box' },
)

function addImage(data: string) {
  const img = useStudioImage(data)
  const cropRatio = 1

  // img width and height are not set until the img is fully loaded
  img.onload = () => {
    const vw: number = img.width
    const vh: number = img.height

    if (!vw || !vh)
      throw new Error(`Invalid image dimensions: ${vw}x${vh}`)

    img.crop.w = Math.floor((vw / vh > cropRatio) ? vh * cropRatio : vw)
    img.crop.h = Math.floor((vw / vh > cropRatio) ? vh : vw / cropRatio)

    unref(images).push(img)
  }
}
</script>

<template>
  <div
    ref="studio"
    class="ItemImagesStudio"
  >
    <!-- video -->
    <video
      ref="video"
      muted
      autoplay
    >Video stream not available.</video>

    <!-- framing -->
    <div class="framing">
      <div class="images">
        <ItemStudioImages v-model="images" />
      </div>
      <div class="guides">
        <div />
      </div>
      <div class="controls">
        <ItemStudioControls
          v-if="video"
          :video="video"
          @new-image="addImage"
        />
      </div>
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
  align-items: stretch;
  background: #3A403A;
  background: radial-gradient(circle, $neutral-400 0%, black 100%);
  position: relative;

  .header {
    @include flex-row;
    gap: 16px;
    height: 64px;
    position: absolute;
    top: 0px;
    box-sizing: border-box;
    width: 100%;
    color: white;
    padding: 0 1rem;
  }

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

  video {
    min-height: v-bind('width + "px"');
    object-fit: cover;
  }

  .framing {
    @include flex-column;
    align-items: stretch;
    position: absolute;
    width: 100%;
    height: 100%;

    &>div:not(:nth-child(2)) {
      background: rgba(0, 0, 0, 0.5);
      flex: 1;
    }

    &>div:nth-child(2) {
      @include flex-column;
      align-items: stretch;
      aspect-ratio: 1;
      padding: 5%;
      &>div {
        flex: 1;
        border-radius: 4%;
        border: 2px dashed rgba(0, 0, 0, 0.2);
      }
    }

    .images {
      @include flex-column;
      justify-content: flex-end;
    }

    .controls {
      @include flex-column-center;
    }
  }
}
</style>
