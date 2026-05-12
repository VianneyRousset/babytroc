import * as LucideIcons from "lucide-vue-next";
import RadixVueResolver from "radix-vue/resolver";
import Components from "unplugin-vue-components/vite";

const lucideIconNames = new Set(Object.keys(LucideIcons));

function LucideIconsResolver() {
	return {
		type: "component" as const,
		resolve: (name: string) => {
			if (lucideIconNames.has(name)) {
				return { name, from: "lucide-vue-next" };
			}
		},
	};
}

const vue3CarouselComponents = new Set([
	"Carousel",
	"Slide",
	"Navigation",
	"Pagination",
]);

function Vue3CarouselResolver() {
	return {
		type: "component" as const,
		resolve: (name: string) => {
			if (vue3CarouselComponents.has(name)) {
				return { name, from: "vue3-carousel" };
			}
		},
	};
}

function VSwitchResolver() {
	return {
		type: "component" as const,
		resolve: (name: string) => {
			if (name === "VSwitch") {
				return { as: "VSwitch", from: "@lmiller1990/v-switch" };
			}
		},
	};
}

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
	/* Extends */
	modules: [
		"nuxt-open-fetch",
		"@pinia/nuxt",
		"@vueuse/nuxt",
		"radix-vue/nuxt",
		"@pinia/colada-nuxt",
		"floating-vue/nuxt",
		"@nuxtjs/device",
	],

	// disable server-side rendering
	ssr: false,

	/* Nuxt Core Features */
	// do not name components based on path
	components: [
		{
			path: "~/components",
			pathPrefix: false,
		},
	],

	// import pinia-colada queries and mutations
	imports: {
		dirs: [
			"types",
			"queries",
			"queries/**",
			"mutations",
			"mutations/**",
			"stores",
			"stores/**",
		],
	},

	devtools: { enabled: false },

	/* Client-side Integrations */
	app: {
		head: {
			title: "Babytroc", // default fallback title
			htmlAttrs: {
				lang: "fr",
			},
			meta: [
				// set mobile status bar color
				{ name: "theme-color", content: "#ffffff" },
				{ name: "msapplication-navbutton-color", content: "#ffffff" },
				{ name: "apple-mobile-web-app-status-bar-style", content: "#ffffff" },
			],
		},
		layoutTransition: {
			name: "fade",
			mode: "out-in",
		},
	},

	// inject SCSS code (colors definition)
	css: [
		"assets/styles/main.scss",
		"assets/styles/animations.scss",
		"assets/styles/floating-vue.scss",
	],

	runtimeConfig: {
		public: {
			openFetch: {
				api: {
					baseURL: "/api",
				},
			},
			cap: {
				apiUrl: "",
				siteKey: "",
			},
		},
	},

	/* Build Pipeline Configs */
	routeRules: {
		"/": { redirect: "/explore" },
		"/newitem": { redirect: "/newitem/studio" },
	},

	/* Feature flags */
	future: {
		compatibilityVersion: 4,
	},
	compatibilityDate: "2024-11-01",

	experimental: {
		viteEnvironmentApi: true,
	},

	/* Tooling Integrations */
	vite: {
		css: {
			preprocessorOptions: {
				scss: {
					additionalData: `
          @use "~/assets/styles/_constants.scss" as *;
          @use "~/assets/styles/_colors.scss" as *;
          @use "~/assets/styles/_mixings.scss" as *;
          @use "~/assets/styles/_fonts.scss" as *;
        `,
				},
			},
		},

		plugins: [
			Components({
				dts: true,
				resolvers: [
					RadixVueResolver(),
					Vue3CarouselResolver(),
					VSwitchResolver(),
					LucideIconsResolver(),
				],
			}),
		],
	},

	vue: {
		compilerOptions: {
			isCustomElement: (tag) => tag === "cap-widget",
		},
	},

	// use typescript type checking
	typescript: {
		strict: true,
		typeCheck: true,
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
