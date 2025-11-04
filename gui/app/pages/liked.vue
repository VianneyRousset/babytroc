<script setup lang="ts">
definePageMeta({
  layout: 'liked',
})
</script>

<template>
  <AppPage
    with-header
    logged-in-only
  >
    <!-- Header bar (mobile only) -->
    <template #mobile-header-bar>
      <h1>Mon compte</h1>
    </template>

    <main>
      <h1>Favorits</h1>
    </main>
  </AppPage>
</template>

<style scoped lang="scss">
</style>
