export default defineNuxtPlugin(() => {
  const router = useRouter()
  const stack = reactive(Array<string>()) as Array<string>
  const backwardFlag = ref(false)
  const direction = ref('forward')

  router.afterEach((to) => {
    const fullPath = to.fullPath
    stack.push(fullPath)

    if (backwardFlag.value) {
      backwardFlag.value = false
      direction.value = 'backward'
    }
    else {
      direction.value = 'forward'
    }
  })

  return {
    provide: {
      routeStack: stack,
      routeStackBackwardFlag: backwardFlag,
      routeStackDirection: direction,
    },
  }
})
