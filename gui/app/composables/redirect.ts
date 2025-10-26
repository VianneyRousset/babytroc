/**
 * Provide redirect() that navigate to redirect url if present in route.
 **/
export function useRedirect() {
  const route = useRoute()

  function redirect() {
    if (route.query.redirect)
      navigateTo(route.query.redirect as string)
  }

  return { redirect }
}
