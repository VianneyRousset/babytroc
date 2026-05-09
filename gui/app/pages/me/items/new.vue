<script setup lang="ts">
definePageMeta({
	layout: "empty",
	appBack: true,
});

const { $toast } = useNuxtApp();
const { mutateAsync: create, isLoading } = useCreateItemMutation();

async function _submit(data: ItemCreate) {
	const _item = await create(data).catch((err) => {
		$toast.error("Échec de la création de l'objet");
		throw err;
	});

	return navigateTo("/me/items");
}
</script>

<template>
  <AppPage
    logged-in-only
    with-header
  >
    <!-- Header bar (mobile only) -->
    <template #mobile-header-bar>
      <AppBack
        :icon="X"
      />
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
