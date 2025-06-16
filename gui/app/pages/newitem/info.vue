<script setup lang="ts">
import VSwitch from '@lmiller1990/v-switch'
import { Check, OctagonAlert } from 'lucide-vue-next'

const { height: headerHeight } = useElementSize(
  useTemplateRef('header'),
)

// exit if not logged-in
const { loggedIn, loginRoute } = useAuth()
watch(loggedIn, (_loggedIn) => {
  if (_loggedIn === false)
    navigateTo(unref(loginRoute))
}, { immediate: true })

// item data store
const itemEditStore = useItemEditStore('new-item')

// back to studio if no images
if (itemEditStore.studioImages.images.length === 0) navigateTo('/newitem')

// item name validity
const isNameTouched = ref(false)
const {
  name: cleanedName,
  status: nameValidityStatus,
  error: nameValidityError,
} = useItemNameValidity(() => itemEditStore.name, useThrottle(isNameTouched, 1000).value)
watchEffect(() => {
  if (itemEditStore.name.length > 0)
    isNameTouched.value = true
})

// item description validity
const isDescriptionTouched = ref(false)
const {
  description: cleanedDescription,
  status: descriptionValidityStatus,
  error: descriptionValidityError,
} = useItemDescriptionValidity(() => itemEditStore.description, useThrottle(isDescriptionTouched, 1000).value)
watchEffect(() => {
  if (itemEditStore.description.length > 0)
    isDescriptionTouched.value = true
})

// item regions validity
const isRegionsTouched = ref(false)
const {
  status: regionsValidityStatus,
  error: regionsValidityError,
} = useItemRegionsValidity(() => itemEditStore.regions, useThrottle(isRegionsTouched, 1000).value)
watchEffect(() => {
  if (itemEditStore.regions.size > 0)
    isRegionsTouched.value = true
})

// overall validity
const isValid = computed(() => unref(nameValidityStatus) === 'success' && unref(descriptionValidityStatus) === 'success' && unref(regionsValidityStatus) === 'success')

const { mutateAsync: mutate, asyncStatus: createItemAsyncStatus } = useCreateItemMutation()
async function createItem() {
  const router = useRouter()
  const routeStack = useRouteStack()

  if (itemEditStore.studioImages.data == null || itemEditStore.studioImages.data.some(img => img == null))
    throw new Error('Some img are not yet uploaded')

  // create item
  const item = await mutate({
    name: unref(cleanedName),
    description: unref(cleanedDescription),
    images: itemEditStore.studioImages.data as Array<string>,
    targeted_age_months: itemEditStore.targetedAge,
    regions: Array.from(itemEditStore.regions),
    blocked: itemEditStore.blocked,
  })

  // reset store
  itemEditStore.reset()

  // exit page
  routeStack.reset()
  navigateTo(
    router.resolve({
      name: 'home-item-item_id',
      params: {
        item_id: item.id,
      },
    }))
}
</script>

<template>
  <div>
    <!-- Header bar -->
    <AppHeaderBar ref="header">
      <AppBack />
      <DropdownMessage
        :status="nameValidityStatus"
        :msg-error="nameValidityError"
        msg-placement="bottom"
        :distance="20"
      >
        <TextInput
          v-model="itemEditStore.name"
          :status="nameValidityStatus"
          placeholder="Nom"
          @blur="isNameTouched = true"
        />
      </DropdownMessage>
    </AppHeaderBar>

    <!-- Filters main -->
    <main class="app-content page">
      <div>
        <ImageGallery :images="itemEditStore.studioImages.images.map(img => img.cropped ?? ',')" />

        <div
          class="image-upload-status"
          :status="itemEditStore.studioImages.status"
        >
          <v-switch :case="itemEditStore.studioImages.status">
            <template #pending>
              <LoadingAnimation :small="true" />
              <div>Téléversement des images</div>
            </template>
            <template #success>
              <Check
                :size="24"
                :stroke-width="2"
              />
              <div>Images téléversées</div>
            </template>
            <template #error>
              <OctagonAlert
                :size="24"
                :stroke-width="2"
              />
              <div>Échec du téléversément</div>
            </template>
          </v-switch>
        </div>

        <h2>Description</h2>
        <DropdownMessage
          :status="descriptionValidityStatus"
          :msg-error="descriptionValidityError"
          msg-placement="top"
          :distance="20"
        >
          <div class="textarea-wrapper">
            <textarea
              ref="textarea"
              v-model="itemEditStore.description"
              placeholder="Description"
              @blur="isDescriptionTouched = true"
            />
          </div>
        </DropdownMessage>

        <h2>Age</h2>
        <AgeRangeInput v-model="itemEditStore.targetedAge" />

        <h2>Disponibilité</h2>
        <div class="checkbox-group">
          <Checkbox v-model="itemEditStore.blocked">
            Rendre indisponible
          </Checkbox>
        </div>

        <h2>Régions</h2>
        <DropdownMessage
          :status="regionsValidityStatus"
          :msg-error="regionsValidityError"
          msg-placement="top"
          :distance="20"
        >
          <RegionsMap
            v-model="itemEditStore.regions"
            @blur="isRegionsTouched = true"
          />
        </DropdownMessage>
        <RegionsCheckboxes v-model="itemEditStore.regions" />
        <TextButton
          aspect="bezel"
          size="large"
          color="primary"
          :loading="createItemAsyncStatus === 'loading'"
          :disabled="!isValid"
          @click="isValid && createItem()"
        >
          Créer l'objet
        </TextButton>
      </div>
    </main>
  </div>
</template>

<style scoped lang="scss">
.AppHeaderBar {

  @include flex-row;

  &>:not(.AppBack) {
    flex: 1;
  }

  :deep(input) {
    all: inherit;
    border:none;
    padding: 0;
    background-image:none;
    background-color:transparent;
    box-shadow: none;

    font-family: "Plus Jakarta Sans", sans-serif;

    @include ellipsis-overflow;
    position: relative;
    top: -0.1rem;
    flex-grow: 1;
    margin: 0;
    font-weight: 500;
    font-size: 1.6rem;

  }
}

main {
  @include flex-column;
  align-items: stretch;
  gap: 1rem;

  --header-height: v-bind(headerHeight + "px");

  .image-upload-status {
    @include flex-row;
    gap: 0.6rem;
    padding: 1rem;

    font-family: "Inter", sans-serif;
    color: $neutral-400;

    &[status="success"] {
      color: $primary-400;
    }

    &[status="error"] {
      color: $red-800;
    }

    div {
      @include ellipsis-overflow;
    }
  }

  textarea {
    -ms-overflow-style: none;
    scrollbar-width: none;

    &::-webkit-scrollbar {
      display: none;
    }
  }

  .TextButton {
    margin-top: 2rem;
  }
}
</style>
