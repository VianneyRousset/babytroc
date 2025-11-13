<script setup lang="ts">
definePageMeta({
  layout: 'me',
})

// auth
useAuth({ fallbackRoute: '/me' })

// name
const name = ref('')
const nameValid = ref(false)
const nameTouched = ref(false)

// description
const description = ref('')
const descriptionValid = ref(false)
const descriptionTouched = ref(false)

// age
const targetedAgeMonths = ref<AgeRange>([null, null])

// regions
const regions = ref(new Set<number>())
const regionsValid = ref(false)
const regionsTouched = ref(false)

// images
const imageUploader = useImageUploader()

const studioImages = ref<Array<StudioImage>>([])
const { data: images, status: imagesStatus } = imageUploader.uploadMany(() => unref(studioImages).map(img => img.cropped).filter(img => img != null))
const imagesTouched = ref(false)
const imagesValid = ref(false)

const valid = computed(() => (
  [nameValid, descriptionValid, regionsValid, imagesValid].every(v => v)
  && unref(imagesStatus) === 'success'
))

const { $toast } = useNuxtApp()

const studioOverlay = ref(false)
const tmpStudioImages = ref<Array<StudioImage>>([])

function openStudioOverlay() {
  tmpStudioImages.value = unref(studioImages).map(img => img.copy())
  studioOverlay.value = true
}

function closeStudioOverlay() {
  studioOverlay.value = false
}

function saveStudioImages() {
  studioImages.value = unref(tmpStudioImages).map(img => img.copy())
}

async function onclick() {
  touchAll()

  if (!unref(valid))
    return

  const _images = unref(images)

  if (!_images.every(img => img != null))
    throw new Error('Cannot create object with null image')

  const item = await create({
    name: unref(name),
    description: unref(description),
    images: _images,
    targeted_age_months: range2string(unref(targetedAgeMonths)),
    regions: [...unref(regions)],
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
        <ItemImagesInput
          v-model:valid="imagesValid"
          v-model:touched="imagesTouched"
          :upload-status="imagesStatus"
          :images="images.filter(img => img != null)"
          msg-placement="top"
          @edit="() => openStudioOverlay()"
        />
        <section class="v">
          <h2>Nom et description</h2>
          <ItemNameInput
            v-model:name="name"
            v-model:valid="nameValid"
            v-model:touched="nameTouched"
            msg-placement="top"
          />
          <ItemDescriptionInput
            v-model:description="description"
            v-model:valid="descriptionValid"
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
          <AgeRangeInput v-model="targetedAgeMonths" />
        </section>
        <section class="v">
          <div>
            <h2>Régions</h2>
            <p class="legend">
              Dans quelles régions de Lausanne peut-on venir chercher votre objet ?
            </p>
          </div>
          <ItemRegionsInput
            v-model:regions="regions"
            v-model:valid="regionsValid"
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
      <Teleport to="body">
        <Overlay v-model="studioOverlay">
          <ItemStudio
            v-model="tmpStudioImages"
            @exit="() => closeStudioOverlay()"
            @done="() => { saveStudioImages(); closeStudioOverlay() }"
          />
        </Overlay>
      </Teleport>
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

.Overlay {
  z-index: 3;

  .ItemStudio {
    width: 100%;
    height: 100%;
  }
}
</style>
