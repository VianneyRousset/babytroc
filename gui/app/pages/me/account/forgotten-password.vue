<script setup lang="ts">
const { goBack } = useNavigation();

definePageMeta({
	layout: "me",
	appBack: true,
	appTitle: "Mot de passe oublié",
});

function done() {
	setTimeout(() => goBack(), 10000);
}
</script>

<template>
  <AppPage
    with-header
    :max-width="600"
  >
    <!-- Main content -->
    <main>
      <AccountAskPasswordResetPanel @done="done" />
    </main>
  </AppPage>
</template>
