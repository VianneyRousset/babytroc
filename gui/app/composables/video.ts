export function useVideoCamera(video: MaybeRefOrGetter<HTMLVideoElement | null | undefined>) {
  const canvas: HTMLCanvasElement = document.createElement('canvas')
  const { stream, enabled } = useUserMedia({
    constraints: {
      audio: false,
      video: {
        facingMode: {
          ideal: 'environment',
        },
      },
    },
  })
  const width = ref<number | undefined>()
  const height = ref<number | undefined>()
  const aspectRatio = computed<number | undefined>(() => {
    const _width = unref(width)
    const _height = unref(height)
    return (_width == null || _height == null) ? undefined : _width / _height
  })

  const stop = watchEffect(() => {
    const _video = toValue(video)
    const _stream = unref(stream)
    if (_video && _stream) {
      _video.addEventListener('loadedmetadata', () => {
        width.value = _video.videoWidth
        height.value = _video.videoHeight
      })

      _video.srcObject = _stream
    }
  })

  enabled.value = true

  function capture(): string {
    const _video = toValue(video)
    const context = canvas.getContext('2d')

    if (!context)
      throw new Error('Context is null')

    if (!_video)
      throw new Error('Video is null')

    canvas.width = _video.videoWidth
    canvas.height = _video.videoHeight
    context.drawImage(_video, 0, 0)
    return canvas.toDataURL('image/png')
  }

  tryOnUnmounted(stop)

  return {
    capture,
    width,
    height,
    aspectRatio,
  }
}
