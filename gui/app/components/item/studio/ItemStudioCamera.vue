<script setup lang="ts">
const capture = defineModel<boolean>()
const emit = defineEmits<(event: 'new-image', img: StudioImage) => void>()

const video = useTemplateRef<HTMLVideoElement>('video')
const {
  capture: recordImage,
  width: videoWidth,
  height: videoHeight,
  aspectRatio: videoAspectRatio,
} = useVideoCamera(video)

const {
  width,
  height,
} = useObjectFit(
  useTemplateRef<HTMLElement>('container'),
  videoAspectRatio,
  'cover',
)

watch(capture, (_capture) => {
  if (_capture === true) {
    const _w = unref(videoWidth)
    const _h = unref(videoHeight)

    if (_w == null || _h == null)
      throw new Error(`Invalid video dimensions ${_w}x${_h}`)

    const _s: number = Math.min(_w, _h)
    const img: StudioImage = useStudioImage(recordImage(), 'center')

    emit('new-image', img)
    capture.value = false
  }
}, { immediate: true })
</script>

<template>
  <div
    ref="container"
    class="ItemStudioCamera"
  >
    <video
      ref="video"
      muted
      autoplay
    >Video stream not available.</video>
    <div class="guide">
      <div />
    </div>
  </div>
</template>

<style lang="scss" scoped>
.ItemStudioCamera {
  @include flex-column-center;
  position: relative;

  video {
    width: v-bind("width != null ? `${width}px` : 'auto'");
    height: v-bind("height != null ? `${height}px` : 'auto'");
  }

  .guide {
    @include flex-column;
    align-items: stretch;
    padding: 5%;
    border-radius: 4%;
    pointer-events: none;
    position: absolute;
    top: 0;
    left: 0;
    bottom: 0;
    right: 0;
    &>div {
    flex: 1;
      border: 2px dashed rgba(0, 0, 0, 0.2);
    }
  }
}
</style>
