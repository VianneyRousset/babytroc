import type { RouteLocationAsRelativeGeneric, RouteLocationAsPathGeneric } from 'vue-router'

export const useRouteStack = () => {
  const stack = useNuxtApp().$routeStack
  const backwardFlag = useNuxtApp().$routeStackBackwardFlag
  const direction = useNuxtApp().$routeStackDirection
  const { currentTabRoot } = useTab()

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

  function goBack(fallback?: string | RouteLocationAsRelativeGeneric | RouteLocationAsPathGeneric | null) {
    markBackward()
    pop()
    pop()
    navigateTo(unref(current) ?? fallback ?? currentTabRoot)
  }

  return {
    stack,
    direction,
    push,
    amend,
    pop,
    goBack,
    reset,
    current,
    previous,
    markBackward,
  }
}
