// Base on Nuxt open fetch custom client documentation
// https://nuxt-open-fetch.vercel.app/advanced/custom-client

import type { FetchContext, FetchHook } from "ofetch";
import { StatusCodes } from "http-status-codes";

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
								if (localOptions)
									return await callHooks(ctx, localOptions.onRequest);
							},

							onResponse: async (ctx) => {
								console.log("RESPONSE", ctx.response);

								// if unauthorized, try to log in and reexecute query
								if (ctx.response.status === StatusCodes.UNAUTHORIZED) {
									console.log("UNAUTHORIZAED");

									const formData = new FormData();

									formData.append("grant_type", "password");
									formData.append("username", "alice@kindbaby.ch");
									formData.append("password", "alice_password");

									globalThis.$fetch("/api/v1/auth/login", {
										method: "POST",
										body: formData,
										onResponse: async ({ response }) => {
											console.log("AUTH", response.ok ? "OK" : "NOK");
										},
									});

									//Object.assign(ctx, )
								}
							},
						}),
						globalThis.$fetch,
					),
				]),
			),
		};
	},
});
