<script setup lang="ts">
definePageMeta({
  layout: 'me',
})

// auth
useAuth({ fallbackRoute: '/me' })

const store = useItemEditStore('create')
</script>

<template>
  <AppPage
    with-header
  >
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
        <ItemImagesGallery
          :item="{ images_names: ['dsWHU', 'pcUv7', 'mDOp0'] }"
        />
        <section class="v">
          <h2>Nom et description</h2>
          <ItemNameInput
            v-model:name="store.name"
            v-model:valid="store.nameValid"
            msg-placement="top"
          />
          <ItemDescriptionInput
            v-model:description="store.description"
            v-model:valid="store.descriptionValid"
            msg-placement="bottom"
          />
        </section>
        <section class="v">
          <div>
            <h2>Age</h2>
            <p class="legend">
              Pour quels ages cet objet convient-il ?
            </p>
          </div>
          <AgeRangeInput v-model="store.targetedAge" />
        </section>
        <section class="v">
          <div>
            <h2>Régions</h2>
            <p class="legend">
              Dans quelles régions de Lausanne peut-on venir chercher votre objet ?
            </p>
          </div>
          <RegionsMap
            v-model="store.regions"
            editable
          />
          <RegionsList
            v-model="store.regions"
            :columns="3"
            editable
          />
        </section>
        <section>
          <TextButton
            aspect="bezel"
            color="primary"
          >
            Créer l'objet
          </TextButton>
        </section>
      </Panel>
    </main>
  </AppPage>
</template>

<style scoped lang="scss">
.TextButton {
  margin: 2em 0;
}

.RegionsMap {
  margin: 2em 4em;
}

.RegionsList {
  font-size: 1em;
}
</style>
