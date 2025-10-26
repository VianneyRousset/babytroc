<script setup lang="ts">
const { goBack } = useNavigation()

function done() {
  setTimeout(() => goBack(), 10000)
}
</script>

<template>
  <AppPage
    with-header
    :max-width="800"
  >
    <!-- Header bar -->
    <template #mobile-header-bar>
      <AppBack />
      <h1>Réinitialisation mot de passe</h1>
    </template>

    <template #desktop>
      <AppHeaderDesktop>
        <template #buttons-left>
          <AppBack />
        </template>
      </AppHeaderDesktop>
    </template>

    <!-- Main content -->
    <main>
      <AccountAskPasswordResetPanel @done="done" />
    </main>
  </AppPage>
</template>
