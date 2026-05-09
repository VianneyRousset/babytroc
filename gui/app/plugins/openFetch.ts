// Base on Nuxt open fetch custom client documentation
// https://nuxt-open-fetch.vercel.app/advanced/custom-client

import { StatusCodes } from "http-status-codes";
import type { NitroFetchOptions } from "nitropack/types";
import type { FetchContext, FetchHook, ResponseType } from "ofetch";

// Call fetch hooks
async function callHooks<C extends FetchContext = FetchContext>(
	context: C,
	hooks: FetchHook<C> | FetchHook<C>[] | undefined,
): Promise<void> {
	if (hooks) {
		if (Array.isArray(hooks)) {
			for (const hook of hooks) {
				await hook(context);
			}
		} else {
			await hooks(context);
		}
	}
}

let refreshPromise: Promise<boolean> | null = null;

// provide open fetch clients (e.g. $api) with authentification features
export default defineNuxtPlugin({
	enforce: "pre", // clients will be ready to use by other plugins, Pinia stores etc.
	setup() {
		const clientsConfig = useRuntimeConfig().public.openFetch;
		const $fetch = globalThis.$fetch;

		return {
			provide: Object.fromEntries(
				Object.entries(clientsConfig).map(([name, options]) => [
					name,
					createOpenFetch(
						(localOptions) => ({
							...options,
							...localOptions,

							onResponse: async (ctx) => {
								const activeSession =
									localStorage.getItem("auth-session") === "true";

								// if active session and received unauthorized,
								// try to refresh token and reexecute query
								if (
									activeSession &&
									ctx.response.status === StatusCodes.UNAUTHORIZED
								) {
									// deduplicate concurrent refresh attempts
									if (!refreshPromise) {
										refreshPromise = $fetch("/api/v1/auth/refresh", {
											method: "POST",
										})
											.then(() => true)
											.catch(() => false)
											.finally(() => {
												refreshPromise = null;
											});
									}

									const refreshed = await refreshPromise;

									if (refreshed) {
										await $fetch(ctx.request, {
											...options,
											...(localOptions as NitroFetchOptions<ResponseType>),
											onResponse: async (newCtx) => {
												if (newCtx.response.ok) Object.assign(ctx, newCtx);
											},
										});
									}
								}

								// call other hooks
								if (localOptions) await callHooks(ctx, localOptions.onResponse);
							},
						}),
						$fetch,
					),
				]),
			),
		};
	},
});
