<script setup lang="ts">
const { loggedIn } = useAuth()

// redirect once logged in
const { redirect } = useRedirect()
const stop = watch(loggedIn, (newState, oldState) => (oldState === false && newState === true) && redirect())
tryOnUnmounted(stop)
</script>

<template>
  <AppPage
    with-header
    :max-width="800"
  >
    <!-- Header bar (mobile only) -->
    <template #mobile-header-bar>
      <AppBack />
      <h1>Mon compte</h1>
    </template>

    <!-- Header (desktop only) -->
    <template #desktop>
      <AppHeaderDesktop>
        <template #buttons-left>
          <AppBack />
        </template>
      </AppHeaderDesktop>
    </template>

    <!-- Main content -->
    <main>
      <WithLoading :loading="loggedIn == null">
        <transition
          name="fade"
          mode="out-in"
        >
          <AccountLoginPanel v-if="loggedIn === false" />
          <AccountLogoutPanel v-else />
        </transition>
      </WithLoading>
    </main>
  </AppPage>
</template>
