<script setup lang="ts">
const { height: mainHeaderHeight } = useElementSize(
  useTemplateRef('main-header'),
)

const {
  loggedIn,
} = useAuth()

const route = useRoute()

watch(loggedIn, (newState, oldState) => {
  if (oldState === false && newState === true && route.query.redirect)
    navigateTo(route.query.redirect as string)
})
</script>

<template>
  <div>
    <!-- Header bar -->
    <AppHeaderBar ref="main-header">
      <AppBack />
      <h1>A propos de Babytroc</h1>
    </AppHeaderBar>

    <!-- Main content -->
    <main class="app-content page">
      <h1>In construction</h1>
      <p>Will some context on babytroc</p>
    </main>
  </div>
</template>

<style scoped lang="scss">
main {
  --header-height: v-bind(mainHeaderHeight + "px");
}
</style>
