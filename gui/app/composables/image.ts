import { useImage } from '@vueuse/core'

let studioImageIndex = 0

type UseStudioImageOptions = {
  crop?: StudioImageCrop | 'center' | 'all'
  maxSize?: number
}

export function useStudioImage(
  src: string,
  options?: UseStudioImageOptions,
): StudioImage {
  const canvas = document.createElement('canvas')
  const context = canvas.getContext('2d')
  const _crop = options?.crop ?? 'all'
  const _maxSize = options?.maxSize
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

      const scaleDown: number = _maxSize == null
        ? 1
        : Math.max(_width / _maxSize, _height / _maxSize, 1)

      canvas.width = _width / scaleDown
      canvas.height = _height / scaleDown

      context.drawImage(
        _img,
        -_left / scaleDown,
        -_top / scaleDown,
        _img.width / scaleDown,
        _img.height / scaleDown,
      )

      return canvas.toDataURL('image/jpeg')
    }),
  })
}

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
