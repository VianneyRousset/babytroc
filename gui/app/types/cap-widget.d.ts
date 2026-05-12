export {};

/**
 * Ambient typing for the cap-widget custom element loaded from
 * https://cdn.jsdelivr.net/npm/cap-widget.
 *
 * The widget renders a Proof-of-Work captcha and emits CustomEvents:
 *   - "solve" with { detail: { token: string } }
 *   - "expire" (no detail)
 * It also exposes a reset() method on the element instance.
 */
declare global {
	type CapSolveEventDetail = { token: string };
	type CapSolveEvent = CustomEvent<CapSolveEventDetail>;
	type CapExpireEvent = CustomEvent<void>;

	interface CapWidgetElement extends HTMLElement {
		reset?: () => void;
	}

	interface HTMLElementEventMap {
		solve: CapSolveEvent;
		expire: CapExpireEvent;
	}

	interface HTMLElementTagNameMap {
		"cap-widget": CapWidgetElement;
	}
}
