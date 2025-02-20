import Components from 'unplugin-vue-components/vite'
import RadixVueResolver from 'radix-vue/resolver'

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2024-11-01',
  devtools: { enabled: true },

  // route rules
  routeRules: {
    "/": { redirect: "/home" },
    // TODO use env variable
    // use CORS ?
    "/api/**": { proxy: "http://localhost:8080/**" }
  },

  // use typescript type checking
  typescript: {
    typeCheck: true
  },

  // inject SCSS code (colors definition)
  css: [`assets/styles/main.scss`],

  // do not name components based on path
  components: [
    {
      path: '~/components',
      pathPrefix: false,
    },
  ],

  vite: {
    css: {
      preprocessorOptions: {
        scss: {
          additionalData: '@use "~/assets/styles/_colors.scss" as *; @use "~/assets/styles/_mixings.scss" as *; @use "~/assets/styles/_fonts.scss" as *;'
        }
      }
    },

    plugins: [
      Components({
        dts: true,
        resolvers: [
          RadixVueResolver()
        ],
      }),
    ],

  },

  modules: ['nuxt-open-fetch', '@pinia/nuxt', '@vueuse/nuxt', 'nuxt-swiper', 'radix-vue/nuxt'],
  openFetch: {
    clients: {
      api: {
        baseURL: '/api'
      }
    }
  },
  runtimeConfig: {
    public: {
      openFetch: {
        api: {
          baseURL: '/api'
        }
      },
    }
  },

});
