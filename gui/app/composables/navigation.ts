import type { Ref } from 'vue'
import type { RouteLocationAsRelativeGeneric, RouteLocationAsPathGeneric } from 'vue-router'

export type AppSection = 'explore' | 'saved' | 'newitem' | 'chats' | 'me'

export function useNavigation() {
  const route = useRoute()
  const router = useRouter()
  const direction = useNuxtApp().$routeChangeDirection
  const { currentTabRoot } = useTab()

  const appSectionUrls = new Map<AppSection, string>([
    ['explore', '/explore'],
    ['saved', '/saved'],
    ['chats', '/chats'],
    ['newitem', '/me/items/new'],
    ['me', '/me'],
  ])

  const activeAppSection: Ref<AppSection> = computed(() => {
    const res = [...appSectionUrls].find(([_, v]) => route.path.startsWith(v))

    if (res == null)
      throw new Error(`Invalid app section for url '${route.path}'.`)

    return res[0] as AppSection
  })

  function goBack(fallback?: string | RouteLocationAsRelativeGeneric | RouteLocationAsPathGeneric | null) {
    if (window.history.state.back == null)
      return router.push(fallback ?? unref(currentTabRoot))
    return router.go(-1)
  }

  return {
    appSectionUrls,
    activeAppSection,
    direction,
    goBack,
  }
}
