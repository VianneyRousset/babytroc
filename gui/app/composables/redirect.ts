/**
 * Provide redirect() that navigate to redirect url if present in route.
 **/
export function useRedirect() {
  const route = useRoute()

  function redirect() {
    const target = route.query.redirect
    if (typeof target === 'string' && target.startsWith('/') && !target.startsWith('//'))
      navigateTo(target)
  }

  return { redirect }
}
