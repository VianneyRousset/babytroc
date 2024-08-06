// https://nuxt.com/docs/api/configuration/nuxt-config

import config from './config'

export default defineNuxtConfig({
  devtools: { enabled: false },
  css: [
    "~/assets/css/properties.css",
    "~/assets/css/main.css",
    "~/assets/css/page.css",
  ],
  app: {
    head: {
      title: "Kindbaby",
      meta: [
        {
          name: "description",
          content: "The easiest way to share baby stuff with your neighbors",
        },
      ],
      link: [
        {
          rel: "stylesheet",
          href: "https://cdnjs.cloudflare.com/ajax/libs/animate.css/4.1.1/animate.min.css",
        },
        {
          rel: "preconnect",
          href: "https://fonts.googleapis.com",
        },
        {
          rel: "preconnect",
          href: "https://fonts.gstatic.com",
          crossorigin: "",
        },
        {
          href: "https://fonts.googleapis.com/css2?family=Inter:wght@100..900&display=swap",
          rel: "stylesheet",
        },
        {
          href: "https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,200..800;1,200..800&display=swap",
          rel: "stylesheet",
        },
      ]
    },
  },
  runtimeConfig: {
    postgresPassword: process.env.POSTGRES_PASSWORD,
    jwtSecret: process.env.JWT_SECRET,
    jwtIssuer: "urn:kindbaby:issuer",
    jwtAudience: "urn:kindbaby:audience",
    hashingConfig: config.hashingConfig,
    public: {
      cookieDuration: 30 * 24 * 60 * 60,
    },
  },
  vite: {
    vue: {
      script: {
        defineModel: true,
        propsDestructure: true,
      },
    },
  },
});
