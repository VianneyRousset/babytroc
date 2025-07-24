import Components from 'unplugin-vue-components/vite'
import RadixVueResolver from 'radix-vue/resolver'

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({

  /* Extends */
  modules: [
    'nuxt-open-fetch',
    '@pinia/nuxt',
    '@vueuse/nuxt',
    'nuxt-swiper',
    'radix-vue/nuxt',
    '@pinia/colada-nuxt',
    '@nuxt/eslint',
    'floating-vue/nuxt',
  ],

  // disable server-side rendering
  ssr: false,

  /* Nuxt Core Features */
  // do not name components based on path
  components: [
    {
      path: '~/components',
      pathPrefix: false,
    },
  ],

  // import pinia-colada queries and mutations
  imports: {
    dirs: ['queries', 'queries/**', 'mutations', 'mutations/**'],
  },

  devtools: { enabled: true },

  /* Client-side Integrations */
  app: {
    pageTransition: { name: 'fade', mode: 'out-in' },
    head: {
      title: 'Babytroc', // default fallback title
      htmlAttrs: {
        lang: 'fr',
      },
      meta: [
        // set mobile status bar color
        { name: 'theme-color', content: '#f6f7f6' },
        { name: 'msapplication-navbutton-color', content: '#f6f7f6' },
        { name: 'apple-mobile-web-app-status-bar-style', content: '#f6f7f6' },
      ],
    },
  },

  // inject SCSS code (colors definition)
  css: ['assets/styles/main.scss', 'assets/styles/animations.scss', 'assets/styles/floating-vue.scss'],

  runtimeConfig: {
    public: {
      openFetch: {
        api: {
          baseURL: '/api',
        },
      },
    },
  },

  /* Build Pipeline Configs */
  routeRules: {
    '/': { redirect: '/home' },
    '/newitem': { redirect: '/newitem/studio' },
  },

  /* Feature flags */
  future: {
    compatibilityVersion: 4,
  },
  compatibilityDate: '2024-11-01',

  /* Tooling Integrations */
  vite: {
    css: {
      preprocessorOptions: {
        scss: {
          additionalData: '@use "~/assets/styles/_colors.scss" as *; @use "~/assets/styles/_mixings.scss" as *; @use "~/assets/styles/_fonts.scss" as *;',
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
        baseURL: '/api',
      },
    },
    openAPITS: {
      enum: true,
    },
  },

  pinia: {
    // accept nested store directories
    storesDirs: ['app/stores/**'],
  },
})
