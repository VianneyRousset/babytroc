<script setup lang="ts">
const { height: headerHeight } = useElementSize(
  useTemplateRef('header'),
)

const itemEditStore = useItemEditStore('new-item')

if (itemEditStore.studioImages.images.length === 0) navigateTo('/newitem')

const { mutateAsync: mutate, asyncStatus: createItemAsyncStatus } = useCreateItemMutation()

const isNameTouched = ref(false)
const isDescriptionTouched = ref(false)
const isRegionsTouched = ref(false)

watch(itemEditStore.regions, () => {
  isRegionsTouched.value = true
})

async function createItem() {
  if (itemEditStore.studioImages.data == null || itemEditStore.studioImages.data.some(img => img == null))
    throw new Error('Some img are not yet uploaded')

  // create object
  await mutate({
    name: itemEditStore.name,
    description: itemEditStore.description,
    images: itemEditStore.studioImages.data as Array<string>,
    targeted_age_months: itemEditStore.targetedAge,
    regions: Array.from(itemEditStore.regions),
    blocked: itemEditStore.blocked,
  })

  // reset store
  itemEditStore.reset()

  // exit page
  navigateTo('/')
}
</script>

<template>
  <div>
    <!-- Header bar -->
    <AppHeaderBar ref="header">
      <AppBack />
      <input
        v-model="itemEditStore.name"
        :class="{ invalid: isNameTouched && !itemEditStore.isNameValid }"
        placeholder="Nom"
        @blur="isNameTouched = true"
      >
    </AppHeaderBar>

    <!-- Filters main -->
    <main class="app-content page">
      <div>
        <ImageGallery :images="itemEditStore.studioImages.images.map(img => img.cropped ?? ',')" />

        <h2>Description</h2>
        <div class="textarea-wrapper">
          <textarea
            ref="textarea"
            v-model="itemEditStore.description"
            placeholder="Description"
            :class="{ invalid: isDescriptionTouched && !itemEditStore.isDescriptionValid }"
            @blur="isDescriptionTouched = true"
          />
        </div>

        <h2>Age</h2>
        <AgeRangeInput v-model="itemEditStore.targetedAge" />

        <h2>Disponibilité</h2>
        <div class="checkbox-group">
          <Checkbox v-model="itemEditStore.blocked">
            Rendre indisponible
          </Checkbox>
        </div>

        <h2>Régions</h2>
        <RegionsMap
          v-model="itemEditStore.regions"
          :class="{ invalid: isRegionsTouched && !itemEditStore.isRegionsValid }"
        />
        <RegionsCheckboxes v-model="itemEditStore.regions" />
        <TextButton
          aspect="bezel"
          size="large"
          color="primary"
          :loading="createItemAsyncStatus === 'loading'"
          :disabled="!itemEditStore.isValid || itemEditStore.studioImages.status !== 'success'"
          @click="createItem()"
        >
          Créer l'objet
        </TextButton>
      </div>
    </main>
  </div>
</template>

<style scoped lang="scss">
.AppHeaderBar {
  input {
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
    color: $neutral-700;
    flex-grow: 1;
    margin: 0;
    font-weight: 500;
    font-size: 1.6rem;

    &.invalid {
      color: $red-700;
      &::placeholder {
        color: $red-700;
      }
    }

  }
}

main {
  @include flex-column;
  align-items: stretch;
  gap: 1rem;

  --header-height: v-bind(headerHeight + "px");

  textarea {
    -ms-overflow-style: none;
    scrollbar-width: none;

    &::-webkit-scrollbar {
      display: none;
    }

    &.invalid {
      color: $red-700;
      box-shadow: 0 0 8px $red-700;
      &::placeholder {
        color: $red-700;
      }
    }
  }

  .RegionsMap {
    &.invalid {
      filter: drop-shadow(0 0 3px $red-700);
    }
  }

  .TextButton {
    margin-top: 2rem;
  }
}
</style>
