<script setup lang="ts">
definePageMeta({
  layout: 'me',
})

// auth
useAuth({ fallbackRoute: '/me' })

const store = useItemEditStore('create')

const nameTouched = ref(false)
const descriptionTouched = ref(false)
const regionsTouched = ref(false)
const imagesTouched = ref(false)

const valid = computed(() => [store.nameValid, store.descriptionValid, store.regionsValid, store.imagesValid].every(v => v) && store.images.status === 'success')

const { $toast } = useNuxtApp()

async function onclick() {
  touchAll()

  if (!unref(valid))
    return

  const item = await create({
    name: store.name,
    description: store.description,
    images: store.images.data,
    targeted_age_months: range2string(store.targetedAge),
    regions: [...store.regions],
    blocked: false,
  }).catch((err) => {
    $toast.error('Échec de la création de l\'objet')
    throw err
  })

  return navigateTo(`/explore/item/${item.id}`)
}

function touchAll() {
  nameTouched.value = true
  descriptionTouched.value = true
  regionsTouched.value = true
  imagesTouched.value = true
}

const { mutateAsync: create, isLoading } = useCreateItemMutation()
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
        <ItemImagesInput
          v-model:valid="store.imagesValid"
          v-model:touched="imagesTouched"
          :upload-status="store.images.status"
          :images="store.images.data"
          msg-placement="top"
          @edit="navigateTo('new/studio')"
        />
        <section class="v">
          <h2>Nom et description</h2>
          <ItemNameInput
            v-model:name="store.name"
            v-model:valid="store.nameValid"
            v-model:touched="nameTouched"
            msg-placement="top"
          />
          <ItemDescriptionInput
            v-model:description="store.description"
            v-model:valid="store.descriptionValid"
            v-model:touched="descriptionTouched"
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
          <ItemRegionsInput
            v-model:regions="store.regions"
            v-model:valid="store.regionsValid"
            v-model:touched="regionsTouched"
            msg-placement="top"
          />
        </section>
        <section>
          <TextButton
            aspect="bezel"
            color="primary"
            :disabled="!valid"
            :loading="isLoading"
            @click="onclick"
          >
            Créer l'objet
          </TextButton>
        </section>
      </Panel>
    </main>
  </AppPage>
</template>

<style scoped lang="scss">
.ItemImagesInput {
  margin-bottom: 2em;
}

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
