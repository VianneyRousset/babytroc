import type { RouteLocationAsRelativeGeneric, RouteLocationAsPathGeneric } from 'vue-router'

declare module '#app' {
  interface PageMeta {
    appBack?: boolean | string | RouteLocationAsRelativeGeneric | RouteLocationAsPathGeneric
    appTitle?: string
  }
}

export {}
