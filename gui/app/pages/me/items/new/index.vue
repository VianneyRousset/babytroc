<script setup lang="ts">
import { Check } from 'lucide-vue-next'

definePageMeta({
  layout: 'me',
})

// auth
useAuth({ fallbackRoute: '/me' })

const name = ref('')
const nameValid = ref(false)
const description = ref('')
const descriptionValid = ref(false)
const age = ref<AgeRange>([null, null])
</script>

<template>
  <AppPage
    with-header
  >
    <!-- Header bar (mobile only) -->
    <template #mobile-header-bar>
      <AppBack />
      <h1>Nouvel objet</h1>
      <IconButton
        :icon="Check"
      />
    </template>

    <!-- Desktop page -->
    <template #desktop>
      <AppHeaderDesktop>
        <template #buttons-left>
          <AppBack />
        </template>
        <template #buttons-right>
          <TextButton
            aspect="bezel"
            color="primary"
          >
            Créer
          </TextButton>
        </template>
      </AppHeaderDesktop>
    </template>

    <main>
      <Panel :max-width="600">
        <ItemImagesGallery
          :item="{ images_names: [] }"
        />
        <section class="v">
          <h2>Nom et description</h2>
          <ItemNameInput
            v-model:name="name"
            v-model:valid="nameValid"
            msg-placement="top"
          />
          <ItemDescriptionInput
            v-model:description="description"
            v-model:valid="descriptionValid"
            msg-placement="top"
          />
        </section>
        <section>
          <h2>Age</h2>
          <p class="legend">
            Pour quels ages cet objet convient-il ?
          </p>
          <AgeRangeInput v-model="age" />
        </section>
        <section class="v">
          <h2>Régions</h2>
          <p class="legend">
            Dans quelles régions de Lausanne peut-on venir chercher votre objet ?
          </p>
          <RegionsMap />
          <RegionsList />
        </section>
      </Panel>
    </main>
  </AppPage>
</template>

<style scoped lang="scss">
</style>
