
export default defineNuxtPlugin((nuxtApp) => {
  const router = useRouter()
  const stack = reactive(Array<string>()) as Array<string>;

  router.afterEach((to, from) => {
    const fullPath = to.fullPath;
    stack.push(fullPath);
  })

  return {
    provide: {
      routeStack: stack,
    }
  }
})
