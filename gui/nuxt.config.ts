import Components from "unplugin-vue-components/vite";
import RadixVueResolver from "radix-vue/resolver";

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
	compatibilityDate: "2024-11-01",
	devtools: { enabled: true },

	future: {
		compatibilityVersion: 4,
	},

	// disable server-side rendering
	ssr: false,

	// route rules
	// TODO add cache control
	routeRules: {
		"/": { redirect: "/home" },
	},

	// use typescript type checking
	typescript: {
		strict: true,
		typeCheck: true,
	},

	// inject SCSS code (colors definition)
	css: ["assets/styles/main.scss", "assets/styles/animations.scss"],

	// import pinia-colada queries and mutations
	imports: {
		dirs: ["queries", "queries/**", "mutations", "mutations/**"],
	},

	// do not name components based on path
	components: [
		{
			path: "~/components",
			pathPrefix: false,
		},
	],

	vite: {
		css: {
			preprocessorOptions: {
				scss: {
					additionalData:
						'@use "~/assets/styles/_colors.scss" as *; @use "~/assets/styles/_mixings.scss" as *; @use "~/assets/styles/_fonts.scss" as *;',
				},
			},
		},

		plugins: [
			Components({
				dts: true,
				resolvers: [RadixVueResolver()],
			}),
		],
	},

	modules: [
		"nuxt-open-fetch",
		"@pinia/nuxt",
		"@vueuse/nuxt",
		"nuxt-swiper",
		"radix-vue/nuxt",
		"@pinia/colada-nuxt",
	],

	runtimeConfig: {
		public: {
			openFetch: {
				api: {
					baseURL: "/api",
				},
			},
		},
	},

	openFetch: {
		// use custom plugin to integrated auth considerations
		// https://nuxt-open-fetch.vercel.app/advanced/custom-client
		disableNuxtPlugin: true,
		clients: {
			api: {
				baseURL: "/api",
			},
		},
		openAPITS: {
			enum: true,
		},
	},

	pinia: {
		// accept nested store directories
		storesDirs: ["app/stores/**"],
	},
});
