import type { Ref } from 'vue'
import type { RouteLocationAsRelativeGeneric, RouteLocationAsPathGeneric } from 'vue-router'

export type AppSection = 'explore' | 'liked' | 'newitem' | 'chats' | 'me'

export function useNavigation() {
  const route = useRoute()
  const router = useRouter()
  const stack = useNuxtApp().$routeStack
  const backwardFlag = useNuxtApp().$routeStackBackwardFlag
  const direction = useNuxtApp().$routeStackDirection
  const { currentTabRoot } = useTab()

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

  function push(fullPath: string) {
    if (stack.length === 0) return stack.push(fullPath)

    if (stack[stack.length - 1] === fullPath) return

    return stack.push(fullPath)
  }

  function amend(fullPath: string) {
    stack[stack.length - 1] = fullPath
  }

  function pop() {
    const route = current.value
    stack.pop()
    return route
  }

  function reset() {
    while (stack.length > 0)
      stack.pop()
  }

  function markBackward() {
    backwardFlag.value = true
    direction.value = 'backward'
  }

  const current = computed(() => stack[stack.length - 1])

  const previous = computed(() => {
    if (!stack || stack.length < 2) return null

    return stack[stack.length - 2]
  })

  function goTo(
    location: string | RouteLocationAsRelativeGeneric | RouteLocationAsPathGeneric,
    options: { saveHash?: string },
  ) {
    if (options.saveHash)
      amend(router.resolve({ ...route, hash: options.saveHash }).fullPath)
    return navigateTo(location)
  }

  function goBack(fallback?: string | RouteLocationAsRelativeGeneric | RouteLocationAsPathGeneric | null) {
    markBackward()
    pop()
    pop()
    return navigateTo(unref(current) ?? fallback ?? currentTabRoot)
  }

  function resetDirection() {
    direction.value = 'forward'
  }

  return {
    appSectionUrls,
    activeAppSection,
    stack,
    direction,
    push,
    amend,
    pop,
    goTo,
    goBack,
    reset,
    current,
    previous,
    markBackward,
    resetDirection,
  }
}
