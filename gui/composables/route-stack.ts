export const useRouteStack = () => {

  const stack = useNuxtApp().$routeStack;

  function push(fullPath: string) {

    if (stack.length === 0)
      return stack.push(fullPath);

    if (stack[stack.length - 1] === fullPath)
      return;

    return stack.push(fullPath);
  }

  function pop() {
    stack.pop();
  }

  function reset() {

    if (!stack)
      return

    while (stack.length > 0) {
      stack.pop();
    }
  }

  const last = computed(() => {

    if (!stack || stack.length === 0)
      return null;

    return stack[stack.length - 1];
  });

  return {
    stack,
    push,
    pop,
    reset,
    last
  }
}
