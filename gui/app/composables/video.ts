type UseVideoCameraCaptureContext = {
  cropRatio?: number
}

export function useVideoCamera(video: MaybeRefOrGetter<HTMLVideoElement>) {
  const currentCamera = shallowRef<string>()
  const canvas: HTMLCanvasElement = document.createElement('canvas')
  const { stream, enabled } = useUserMedia({
    constraints: reactive({ video: { deviceId: currentCamera } }),
  })

  watchEffect(() => {
    const _video = toValue(video)
    if (_video)
      _video.srcObject = stream.value!
  })

  enabled.value = true

  const { videoInputs: cameras } = useDevicesList({
    requestPermissions: true,
    constraints: {video: true, audio: false},
    onUpdated() {
      if (!cameras.value.find(i => i.deviceId === currentCamera.value))
        currentCamera.value = cameras.value[0]?.deviceId
    },
  })

  function capture({ cropRatio }: UseVideoCameraCaptureContext = {}): string {
    const _video = toValue(video)
    const context = canvas.getContext('2d')

    if (!context)
      throw new Error('Context is null')

    if (!_video)
      throw new Error('Video is null')

    // video dimensions
    const vw = _video.videoWidth
    const vh = _video.videoHeight

    if (!vw || !vh)
      throw new Error(`Invalid video dimensions: ${vw}x${vh}`)

    if (cropRatio === undefined) {
      canvas.width = vw
      canvas.height = vh
    }
    else {
      canvas.width = Math.floor((vw / vh > cropRatio) ? vh * cropRatio : vw)
      canvas.height = Math.floor((vw / vh > cropRatio) ? vh : vw / cropRatio)
    }

    context.drawImage(_video, -Math.floor((vw - canvas.width) / 2), -Math.floor((vh - canvas.height) / 2))
    return canvas.toDataURL('image/png')
  }

  return {
    capture,
  }
}
