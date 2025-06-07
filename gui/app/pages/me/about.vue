<script setup lang="ts">
const { height: mainHeaderHeight } = useElementSize(
  useTemplateRef('main-header'),
)
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
