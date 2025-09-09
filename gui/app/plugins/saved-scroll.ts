export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.directive('saved-scroll', {
    mounted(el, { arg: name }) {
      if (name != null)
        useSavedScroll(name, el)
    },
  })
})
