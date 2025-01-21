
export default defineNuxtPlugin((nuxtApp) => {
  const router = useRouter()
  const stack = reactive(Array<string>()) as Array<string>;

  router.afterEach((to, from) => {

    const fullPath = from.fullPath;

    if (to.fullPath === from.fullPath)
      return;

    if (stack.length === 0)
      return stack.push(fullPath);

    if (stack[stack.length - 1] === fullPath)
      return;

    return stack.push(fullPath);
  })

  return {
    provide: {
      routeStack: stack,
    }
  }
})
