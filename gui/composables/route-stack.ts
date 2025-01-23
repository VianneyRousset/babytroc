export const useRouteStack = () => {

  const stack = useNuxtApp().$routeStack;

  function push(fullPath: string) {

    if (stack.length === 0)
      return stack.push(fullPath);

    if (stack[stack.length - 1] === fullPath)
      return;

    return stack.push(fullPath);
  }

  function amend(fullPath: string) {
    stack[stack.length - 1] = fullPath;
  };

  function pop() {
    const route = current.value;
    stack.pop();
    return route;
  }

  function reset() {

    if (!stack)
      return

    while (stack.length > 0) {
      stack.pop();
    }
  }

  const current = computed(() => stack[stack.length - 1]);

  const previous = computed(() => {

    if (!stack || stack.length < 2)
      return null;

    return stack[stack.length - 2];
  });

  return {
    stack,
    push,
    amend,
    pop,
    reset,
    current,
    previous,
  }
}
