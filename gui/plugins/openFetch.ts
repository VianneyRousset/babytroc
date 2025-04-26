export default defineNuxtPlugin({
	enforce: "pre", // clients will be ready to use by other plugins, Pinia stores etc.
	setup() {
		const clients = useRuntimeConfig().public.openFetch;
		const localFetch = useRequestFetch();

		return {
			provide: Object.entries(clients).reduce(
				(acc, [name, options]) => ({
					...acc,
					[name]: createOpenFetch(options, localFetch),

					// or add the logging:

					// [name]: createOpenFetch(localOptions => ({
					//   ...options,
					//   ...localOptions,
					//   onRequest(ctx) {
					//     console.log('My logging', ctx.request)
					//     return localOptions?.onRequest?.(ctx)
					//   }
					// }), localFetch)
				}),
				{},
			),
		};
	},
});
