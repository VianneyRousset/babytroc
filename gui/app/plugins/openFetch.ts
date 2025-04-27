// Base on Nuxt open fetch custom client documentation
// https://nuxt-open-fetch.vercel.app/advanced/custom-client

import type { FetchContext, FetchHook } from "ofetch";

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

// provide open fetch clients (e.g. $api) with authentification features
export default defineNuxtPlugin({
	enforce: "pre", // clients will be ready to use by other plugins, Pinia stores etc.
	setup() {
		const clientsConfig = useRuntimeConfig().public.openFetch;

		return {
			provide: Object.fromEntries(
				Object.entries(clientsConfig).map(([name, options]) => [
					name,
					createOpenFetch(
						(localOptions) => ({
							...options,
							...localOptions,

							onRequest: async (ctx) => {
								console.log("FETCHING >>> ", ctx.request);
								return await callHooks(ctx, localOptions.onRequest);
							},
						}),
						globalThis.$fetch,
					),
				]),
			),
		};
	},
});
