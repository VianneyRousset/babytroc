import type { Ref } from 'vue'

export type AppSection = 'explore' | 'liked' | 'newitem' | 'chats' | 'me'

export function useAppNavigation() {
  const route = useRoute()

  const appSectionUrls = new Map<AppSection, string>([
    ['explore', '/explore'],
    ['liked', '/liked'],
    ['newitem', '/newitem'],
    ['chats', '/chats'],
    ['me', '/me'],
  ])

  const activeAppSection: Ref<AppSection> = computed(() => {
    const res = [...appSectionUrls].find(([_, v]) => route.path.startsWith(v))

    if (res == null)
      throw new Error(`Invalid app section for url '${route.path}'.`)

    return res[1] as AppSection
  })

  return { appSectionUrls, activeAppSection }
}
