import { useImage } from '@vueuse/core'

let studioImageIndex = 0

export function useStudioImage(
  src: string,
  crop?: StudioImageCrop | 'center' | 'all',
): StudioImage {
  const canvas = document.createElement('canvas')
  const context = canvas.getContext('2d')
  const _crop = crop ?? 'all'

  const original = ref<string>(src)
  const { state: img } = useImage(() => ({ src: unref(original) }))

  if (!context)
    throw new Error('Unsupported context identifier')

  const width = ref(0)
  const height = ref(0)
  const top = ref(0)
  const left = ref(0)

  watch(img, (_img) => {
    if (_img == null)
      return

    if (_crop === 'center') {
      const s = Math.min(_img.width, _img.height)
      width.value = s
      height.value = s
      top.value = (_img.height - s) / 2
      left.value = (_img.width - s) / 2
    }
    else if (_crop === 'all') {
      width.value = _img.width
      height.value = _img.height
      top.value = 0
      left.value = 0
    }
    else {
      width.value = _crop.width
      height.value = _crop.height
      top.value = _crop.top
      left.value = _crop.left
    }
  })

  return reactive({
    id: studioImageIndex++,
    original: src,
    width: computed(() => unref(img)?.width),
    height: computed(() => unref(img)?.height),
    crop: { width, height, top, left },
    cropped: computed(() => {
      const _width = unref(width)
      const _height = unref(height)
      const _top = unref(top)
      const _left = unref(left)

      const _img = unref(img)

      if (_img == null)
        return

      canvas.width = _width
      canvas.height = _height

      context.drawImage(
        _img,
        -_left,
        -_top,
      )

      return canvas.toDataURL('image/jpeg')
    }),
  })
}

export function useVideoCamera(video: MaybeRefOrGetter<HTMLVideoElement | null | undefined>) {
  const currentCamera = shallowRef<string>()
  const canvas: HTMLCanvasElement = document.createElement('canvas')
  const { stream, enabled } = useUserMedia({
    constraints: reactive({ video: { deviceId: currentCamera } }),
  })
  const width = ref<number | undefined>()
  const height = ref<number | undefined>()
  const aspectRatio = computed<number | undefined>(() => {
    const _width = unref(width)
    const _height = unref(height)
    return (_width == null || _height == null) ? undefined : _width / _height
  })

  watchEffect(() => {
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

  const { videoInputs: cameras } = useDevicesList({
    requestPermissions: true,
    constraints: { video: true, audio: false },
    onUpdated() {
      if (!cameras.value.find(i => i.deviceId === currentCamera.value))
        currentCamera.value = cameras.value[0]?.deviceId
    },
  })

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

  return {
    capture,
    width,
    height,
    aspectRatio,
  }
}
