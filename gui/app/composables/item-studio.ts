import { useImage } from '@vueuse/core'
import { cloneDeep } from 'lodash'

let studioImageIndex = 0

type UseStudioImageOptions = {
  crop?: StudioImageCrop | 'center' | 'all'
  maxSize?: number
}

function readCrop(
  crop: StudioImageCrop | 'center' | 'all',
  { width, height }: {
    width: number
    height: number
  },
): StudioImageCrop {
  const s = Math.min(width, height)
  return crop === 'center'
    ? {
        width: s,
        height: s,
        top: (height - s) / 2,
        left: (width - s) / 2,
      }
    : crop === 'all'
      ? {
          width,
          height,
          top: 0,
          left: 0,
        }
      : crop
}

export function useStudioImage(
  src: string,
  options?: UseStudioImageOptions,
): StudioImage {
  const canvas = document.createElement('canvas')
  const context = canvas.getContext('2d')
  const maxSize = ref(options?.maxSize)
  const original = ref(src)
  const { state: img } = useImage(() => ({ src: unref(original) }))
  const _crop = ref(options?.crop ?? 'all')
  const crop = computed<StudioImageCrop | undefined>(() => {
    const _img = unref(img)
    return _img && readCrop(unref(_crop), { width: _img.width, height: _img.height })
  })

  if (!context)
    throw new Error('Unsupported context identifier')

  const cropped = computed<string | undefined>(() => {
    const _img = unref(img)

    if (_img == null)
      return

    const _maxSize = unref(maxSize)
    const __crop = unref(crop)

    if (__crop == null)
      return

    const { width, height, top, left } = __crop

    const scaleDown: number = (_maxSize == null)
      ? 1
      : Math.max(width / _maxSize, height / _maxSize, 1)

    canvas.width = width / scaleDown
    canvas.height = height / scaleDown

    context.drawImage(
      _img,
      -left / scaleDown,
      -top / scaleDown,
      _img.width / scaleDown,
      _img.height / scaleDown,
    )

    return canvas.toDataURL('image/jpeg')
  })

  const copy = (): StudioImage => useStudioImage(unref(original), { crop: unref(_crop), maxSize: unref(maxSize) })

  function setCrop(newCrop: StudioImageCrop) {
    _crop.value = cloneDeep(newCrop)
  }

  return reactive({
    id: studioImageIndex++,
    original: src,
    width: computed(() => unref(img)?.width),
    height: computed(() => unref(img)?.height),
    maxSize,
    copy,
    crop,
    setCrop,
    cropped,
  })
}

export function useItemStudioImages(
  images: Ref<Array<StudioImage>>,
  options?: {
    maxImages?: number
  },
) {
  const selectedImage = ref<StudioImage | undefined>(unref(images)[0])
  const disabledNewImage = computed(() => options?.maxImages != null && unref(images).length >= options.maxImages)

  function selectImage(id: number | undefined) {
    selectedImage.value = unref(images).find(img => img.id === id)
  }

  function addImage(img: StudioImage) {
    if (unref(disabledNewImage))
      return

    unref(images).push(img)
  }

  function deleteImage(id: number) {
    let _images = unref(images)

    // get selected image index
    const index: number | undefined = images.value.findIndex(img => img.id === id)
    const nextIndex = Math.min(Math.max(0, index - 1), _images.length - 1)

    // remove image from array
    _images = _images.filter(img => img.id !== id)

    selectedImage.value = _images[nextIndex]
    images.value = _images
  }

  function cropSelectedImage(crop: StudioImageCrop) {
    const _selectedImage = unref(selectedImage)

    if (_selectedImage == null)
      return

    _selectedImage.setCrop(crop)
  }

  return { selectedImage, disabledNewImage, selectImage, addImage, deleteImage, cropSelectedImage }
}
