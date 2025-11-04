export default defineNuxtPlugin(() => {
  const router = useRouter()
  const direction = ref<'forward' | 'backward'>('forward')
  let previousPosition = 0

  router.beforeEach(() => {
    const delta = window.history.state.position - previousPosition
    direction.value = delta < 0 ? 'backward' : 'forward'
  })

  router.afterEach(() => {
    previousPosition = window.history.state.position
  })

  return {
    provide: {
      routeChangeDirection: direction,
    },
  }
})
