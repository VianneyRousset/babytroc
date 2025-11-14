<script setup lang="ts">
definePageMeta({
  layout: 'me',
})

// auth
useAuth({ fallbackRoute: '/me' })

const { $toast } = useNuxtApp()
const { mutateAsync: create, isLoading } = useCreateItemMutation()

async function submit(data: ItemCreate) {
  const item = await create(data).catch((err) => {
    $toast.error('Échec de la création de l\'objet')
    throw err
  })

  return navigateTo(`/explore/item/${item.id}`)
}
</script>

<template>
  <AppPage with-header>
    <!-- Header bar (mobile only) -->
    <template #mobile-header-bar>
      <AppBack />
      <h1>Nouvel objet</h1>
    </template>

    <!-- Desktop page -->
    <template #desktop>
      <AppHeaderDesktop>
        <template #buttons-left>
          <AppBack />
        </template>
      </AppHeaderDesktop>
    </template>

    <main>
      <Panel :max-width="600">
        <ItemEditionForm
          :is-loading="isLoading"
          @submit="submit"
        />
      </Panel>
    </main>
  </AppPage>
</template>

<style scoped lang="scss">
</style>
