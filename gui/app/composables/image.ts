let studioImageIndex = 0

export function useStudioImage(data: string): StudioImage {
  const img = ref(new Image())
  const canvas = document.createElement('canvas')
  const context = canvas.getContext('2d')

  if (!context)
    throw new Error('Unsupported context identifier')

  const x = ref(0)
  const y = ref(0)
  const w = ref<number | undefined>(undefined)
  const h = ref<number | undefined>(undefined)

  const onload = ref<(() => void) | undefined>(undefined)

  let _original = data
  const original = computed<string>({
    get: () => _original,
    set: (v: string) => {
      _original = v
      unref(img).src = v
    },
  })

  unref(img).onload = () => {
    const _onload = unref(onload)
    triggerRef(img)
    if (_onload)
      _onload()
  }

  unref(img).src = data

  return reactive({
    id: studioImageIndex++,
    original,
    width: computed(() => unref(img).width),
    height: computed(() => unref(img).height),
    crop: { x, y, w, h },
    cropped: computed(() => {
      const _x = unref(x)
      const _y = unref(y)
      const _w = unref(w)
      const _h = unref(h)

      const _img = unref(img)

      canvas.width = _w ?? _img.width
      canvas.height = _h ?? _img.height

      context.drawImage(_img, -_x, -_y)

      return canvas.toDataURL()
    }),
    onload,
  })
}

export function useVideoCamera(video: MaybeRefOrGetter<HTMLVideoElement>) {
  const currentCamera = shallowRef<string>()
  const canvas: HTMLCanvasElement = document.createElement('canvas')
  const { stream, enabled } = useUserMedia({
    constraints: reactive({ video: { deviceId: currentCamera } }),
  })

  watchEffect(() => {
    const _video = toValue(video)
    const _stream = unref(stream)
    if (_video && _stream)
      _video.srcObject = _stream
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
  }
}
