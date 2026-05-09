const WEBSOCKET_PATH = "/api/v1/me/websocket";
const MAX_RECONNECT_DELAY_MS = 30_000;
const BASE_RECONNECT_DELAY_MS = 1_000;

export type WebSocketMessageTypes = {
	new_chat_message: {
		type: "new_chat_message";
		message: ChatMessage;
	};
	updated_chat_message: {
		type: "updated_chat_message";
		message: ChatMessage;
	};
	updated_account_validation: {
		type: "updated_account_validation";
		validated: boolean;
	};
};

type ConnectionState = "connected" | "disconnected" | "reconnecting";

const connectionState = ref<ConnectionState>("disconnected");
// incremented on each reconnect so listeners can re-attach
const reconnectGeneration = ref(0);
let reconnectTimer: ReturnType<typeof setTimeout> | undefined;
let reconnectAttempt = 0;

function createWebSocket(): WebSocket {
	const loc = window.location;
	const proto = loc.protocol === "https:" ? "wss:" : "ws:";
	const url = `${proto}//${loc.host}${WEBSOCKET_PATH}`;
	const ws = new WebSocket(url);

	ws.addEventListener("open", () => {
		connectionState.value = "connected";
		reconnectAttempt = 0;
	});

	ws.addEventListener("close", () => {
		connectionState.value = "disconnected";
		scheduleReconnect();
	});

	ws.addEventListener("error", () => {
		connectionState.value = "disconnected";
	});

	return ws;
}

function scheduleReconnect() {
	if (websocketRefCounter.counter === 0) return;
	if (reconnectTimer) return;

	connectionState.value = "reconnecting";
	const delay = Math.min(
		BASE_RECONNECT_DELAY_MS * 2 ** reconnectAttempt,
		MAX_RECONNECT_DELAY_MS,
	);
	reconnectAttempt++;

	reconnectTimer = setTimeout(() => {
		reconnectTimer = undefined;
		if (websocketRefCounter.counter > 0) {
			if (websocketRefCounter.value) {
				websocketRefCounter.value.close();
				websocketRefCounter.value = undefined;
			}
			websocketRefCounter.value = createWebSocket();
			reconnectGeneration.value++;
		}
	}, delay);
}

const websocketRefCounter = new RefCounter<WebSocket>(
	() => createWebSocket(),
	(ws: WebSocket) => {
		clearTimeout(reconnectTimer);
		reconnectTimer = undefined;
		reconnectAttempt = 0;
		ws.close();
		connectionState.value = "disconnected";
	},
);

export function useWebSocketState(): Readonly<Ref<ConnectionState>> {
	return connectionState;
}

export function useSharedWebSocket(): WebSocket {
	const ws: WebSocket = websocketRefCounter.start();

	onScopeDispose(() => websocketRefCounter?.stop());

	return ws;
}

export function useLiveMessage<T extends keyof WebSocketMessageTypes>(
	type: T,
	handler: (msg: WebSocketMessageTypes[T]) => void,
	options?: {
		enabled?: MaybeRefOrGetter<boolean>;
	},
) {
	let abortController: AbortController | undefined;
	let active = false;

	function attachListener() {
		const ws = websocketRefCounter.value;
		if (!ws) return;

		abortController?.abort();
		abortController = new AbortController();

		ws.addEventListener(
			"message",
			(event: MessageEvent) => {
				const wsMessage = JSON.parse(event.data);

				if (wsMessage.type === type) handler(wsMessage);
			},
			{
				signal: abortController.signal,
			},
		);
	}

	function start() {
		active = true;
		websocketRefCounter.start();
		attachListener();
	}

	function stop() {
		if (!active) return;
		active = false;
		abortController?.abort();
		abortController = undefined;
		websocketRefCounter.stop();
	}

	// re-attach listener when websocket reconnects
	const stopWatchReconnect = watch(reconnectGeneration, () => {
		if (active) attachListener();
	});

	const unwatch = watch(
		() => toValue(options?.enabled) ?? true,
		(state) => (state === true ? start() : stop()),
		{ immediate: true },
	);

	tryOnUnmounted(() => {
		stopWatchReconnect();
		unwatch();
		stop();
	});
}
