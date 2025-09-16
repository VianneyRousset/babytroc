export function useNarrowWindow() {
  const device = useDevice()
  const { width: windowWidth } = useWindowSize()
  const narrowWindow = computed(() => device.isMobile || unref(windowWidth) < 1000)
  return { narrowWindow }
}
