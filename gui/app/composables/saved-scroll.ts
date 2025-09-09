export function useSavedScroll(
  name: string,
  element: MaybeRefOrGetter<ComponentPublicInstance | HTMLElement | SVGElement | Window | Document | null | undefined>,
) {
  // get $el from ComponentPublicInstance
  const _element = computed(() => {
    const _el = toValue(element)

    if (_el == null || _el instanceof HTMLElement || _el instanceof SVGElement || _el instanceof Window || _el instanceof Document) return _el

    return _el.$el
  })

  const { x: savedX, y: savedY } = storeToRefs(useSavedScrollStore(name))
  const { x, y } = useScroll(_element)

  // update saved scroll position
  watch(x, _x => (savedX.value = _x))
  watch(y, _y => (savedY.value = _y))

  // restore scroll position of element update
  watch(_element, () => {
    x.value = unref(savedX)
    y.value = unref(savedY)
  }, { immediate: true })

  return { x: savedX, y: savedY }
}
