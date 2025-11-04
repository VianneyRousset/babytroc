const WEBSOCKET_PATH = '/api/v1/me/websocket'

export type WebSocketMessageTypes = {
  new_chat_message: {
    type: 'new_chat_message'
    message: ChatMessage
  }
  updated_chat_message: {
    type: 'updated_chat_message'
    message: ChatMessage
  }
  updated_account_validation: {
    type: 'updated_account_validation'
    validated: boolean
  }
}

const websocketRefCounter = new RefCounter<WebSocket>(
  () => {
    const loc = window.location
    const proto = loc.protocol === 'https:' ? 'wss:' : 'ws:'
    const url = `${proto}//${loc.host}${WEBSOCKET_PATH}`
    return new WebSocket(url)
  },
  (ws: WebSocket) => ws.close(),
)

export function useSharedWebSocket(): WebSocket {
  const ws: WebSocket = websocketRefCounter.start()

  // cleanup on scope dispose
  onScopeDispose(() => websocketRefCounter?.stop())

  return ws
}

export function useLiveMessage<T extends keyof WebSocketMessageTypes>(
  type: T,
  handler: (msg: WebSocketMessageTypes[T]) => void,
  options?: {
    enabled?: MaybeRefOrGetter<boolean>
  },
) {
  let websocket: WebSocket | undefined = undefined
  let abortController: AbortController | undefined = undefined

  function start() {
    // get websocket
    websocket = websocketRefCounter.start()

    // create abort controller
    abortController = new AbortController()

    // add event listener
    websocket.addEventListener(
      'message',
      (event: MessageEvent) => {
        const wsMessage = JSON.parse(event.data)

        if (wsMessage.type === type)
          handler(wsMessage)
      }, {
        signal: abortController.signal,
      },
    )
  }

  function stop() {
    abortController?.abort()
    websocketRefCounter.stop()
    websocket = undefined
    abortController = undefined
  }

  const unwatch = watch(() => toValue(options?.enabled) ?? true, state => state === true ? start() : (websocket && stop()), { immediate: true })

  tryOnUnmounted(() => {
    unwatch()
    stop()
  })
}
