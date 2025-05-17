<script setup lang="ts">
import { Images, Camera, ArrowRight } from 'lucide-vue-next'

const currentCamera = shallowRef<string>()
const { videoInputs: cameras } = useDevicesList({
  requestPermissions: true,
  onUpdated() {
    if (!cameras.value.find(i => i.deviceId === currentCamera.value))
      currentCamera.value = cameras.value[0]?.deviceId
  },
})

const video = useTemplateRef<HTMLVideoElement>('video')
const { stream, enabled } = useUserMedia({
  constraints: reactive({ video: { deviceId: currentCamera } }),
})

watchEffect(() => {
  if (video.value)
    video.value.srcObject = stream.value!
})

enabled.value = true

const studio = useTemplateRef<HTMLElement>('studio')

const { width } = useElementSize(
  studio,
  undefined,
  { box: 'border-box' },
)
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
      <div />
      <div>
        <div />
      </div>
      <div>
        <div class="controls">
          <IconButton class="gallery">
            <Images
              :size="32"
              :stroke-width="1.5"
            />
          </IconButton>

          <IconButton class="shoot">
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
  background: #111;
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

    &>div:first-child, &>div:last-child {
      background: rgba(0, 0, 0, 0.5);
      flex: 1;
      @include flex-column-center;
    }

    &>div:nth-child(2) {
      @include flex-column;
      align-items: stretch;
      aspect-ratio: 1;
      padding: 5%;
      &>div {
        flex: 1;
        border-radius: 2%;
        border: 2px dashed rgba(0, 0, 0, 0.2);
      }
    }

    .controls {
      align-self: center;
      width: 80%;
      max-width: 350px;
      min-width: 200px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      height: clamp(100px, 20%, 160px);
      color: white;

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
  }
}
</style>
