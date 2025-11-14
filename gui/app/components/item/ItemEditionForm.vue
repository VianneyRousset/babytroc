<script setup lang="ts" generic="ItemData extends Pick<Item, 'name' | 'description' | 'targeted_age_months' | 'images_names' | 'regions' | 'blocked'>">
const emit = defineEmits<(event: 'submit', data: ItemCreate) => void>()

const props = withDefaults(defineProps<{
  item?: ItemData
  isLoading?: boolean
}>(), {
  isLoading: false,
})

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
const { data: images, status: imagesStatus } = (
  imageUploader
    .uploadMany(() => unref(studioImages)
      .map(img => img.cropped)
      .filter(img => img != null))
)
const imagesTouched = ref(false)
const imagesValid = ref(false)

// studio
const studioOverlay = ref(false)
const tmpStudioImages = ref<Array<StudioImage>>([])

// load data on props.data change
const stop = watch(() => props.item, (_item) => {
  if (_item) {
    name.value = _item.name
    description.value = _item.description
    targetedAgeMonths.value = string2range(_item.targeted_age_months)
    regions.value = new Set(_item.regions.map(reg => reg.id))
    studioImages.value = _item.images_names.map((name: string) => useStudioImage(imagePath(name), { crop: 'center', maxSize: 1024 }))
  }
}, { immediate: true })
tryOnUnmounted(stop)

// all field validation must pass and upload succeeded
const valid = computed(() => (
  [nameValid, descriptionValid, regionsValid, imagesValid].every(v => unref(v) === true)
  && unref(imagesStatus) === 'success'
  && unref(images).every((img: string | undefined) => img != null)
))

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

function touchAll() {
  nameTouched.value = true
  descriptionTouched.value = true
  regionsTouched.value = true
  imagesTouched.value = true
}

function onclick() {
  touchAll()

  if (unref(valid)) {
    const _images = unref(images)

    if (!_images.every(img => img != null))
      throw new Error('Cannot create object with null image')

    emit('submit', {
      name: unref(name),
      description: unref(description),
      images: _images,
      targeted_age_months: range2string(unref(targetedAgeMonths)),
      regions: [...unref(regions)],
      blocked: false,
    })
  }
}
</script>

<template>
  <section v-if="!studioOverlay">
    <ItemImagesInput
      v-model:valid="imagesValid"
      v-model:touched="imagesTouched"
      :upload-status="imagesStatus"
      :images="images.filter(img => img != null)"
      msg-placement="top"
      @edit="() => openStudioOverlay()"
    />
  </section>
  <section
    v-if="!studioOverlay"
    class="v"
  >
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
  <section
    v-if="!studioOverlay"
    class="v"
  >
    <div>
      <h2>Age</h2>
      <p class="legend">
        Pour quels ages cet objet convient-il ?
      </p>
    </div>
    <AgeRangeInput v-model="targetedAgeMonths" />
  </section>
  <section
    v-if="!studioOverlay"
    class="v"
  >
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
  <section
    v-if="!studioOverlay"
    class="v"
  >
    <TextButton
      aspect="bezel"
      color="primary"
      :disabled="!valid"
      :loading="props.isLoading"
      @click="onclick"
    >
      Enregistrer
    </TextButton>
  </section>
  <Teleport to="body">
    <Overlay v-model="studioOverlay">
      <ItemStudio
        v-model="tmpStudioImages"
        @exit="() => closeStudioOverlay()"
        @done="() => { saveStudioImages(); closeStudioOverlay() }"
      />
    </Overlay>
  </Teleport>
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
