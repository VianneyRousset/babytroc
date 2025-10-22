export function useObjectFit(
  obj: MaybeRefOrGetter<HTMLElement | undefined | null>,
  aspectRatio: MaybeRefOrGetter<number | undefined | null>,
  fit: MaybeRefOrGetter<'fill' | 'cover' | 'contain'>,
): { width: Ref<number | undefined>, height: Ref<number | undefined> } {
  const { width: containerWidth, height: containerHeight } = useElementSize(obj)

  const width = ref<number | undefined>(0)
  const height = ref<number | undefined>(0)

  const stop = watchEffect(() => {
    const _containerWidth = unref(containerWidth)
    const _containerHeight = unref(containerHeight)
    const _aspectRatio = toValue(aspectRatio)

    if (_containerWidth == null || _containerHeight == null || _aspectRatio == null) {
      width.value = undefined
      height.value = undefined
      return
    }

    // is the video flatter than its container ?
    const _flatter = _aspectRatio > _containerWidth / _containerHeight

    switch (toValue(fit)) {
      case 'fill':
        width.value = _containerWidth
        height.value = _containerHeight
        break

      case 'cover':
        width.value = _flatter ? undefined : _containerWidth
        height.value = _flatter ? _containerHeight : undefined
        break

      case 'contain':
        width.value = _flatter ? _containerWidth : undefined
        height.value = _flatter ? undefined : _containerHeight
        break
    }
  })

  tryOnUnmounted(stop)

  return { width, height }
}
