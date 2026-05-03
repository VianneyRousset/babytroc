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
    // If page explicitly blocks back navigation
    if (route.meta.appBack === false)
      return

    // Resolve fallback: explicit param > meta > currentTabRoot
    const resolvedFallback = fallback
      ?? (typeof route.meta.appBack === 'string' || (typeof route.meta.appBack === 'object' && route.meta.appBack !== null)
        ? route.meta.appBack as string | RouteLocationAsRelativeGeneric | RouteLocationAsPathGeneric
        : undefined)
      ?? unref(currentTabRoot)

    const back = window.history.state.back
    const res = back && [...appSectionUrls].find(([_, v]) => back.startsWith(v))
    const previousSection = res && res[0]

    // If previous route was from a different section, use fallback
    if (previousSection !== unref(activeAppSection)) {
      return router.push(resolvedFallback)
    }

    return router.go(-1)
  }

  return {
    appSectionUrls,
    activeAppSection,
    direction,
    goBack,
  }
}
