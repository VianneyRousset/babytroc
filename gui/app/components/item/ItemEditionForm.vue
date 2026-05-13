<script setup lang="ts" generic="ItemData extends Pick<Item, 'name' | 'description' | 'targeted_age_months' | 'image_names' | 'region_ids' | 'category_slugs' | 'blocked'>">
import { OctagonAlert } from "lucide-vue-next";

const emit = defineEmits<(event: "submit", data: ItemFormData) => void>();

const props = withDefaults(
	defineProps<{
		item?: ItemData;
		isLoading?: boolean;
		submitDisabled?: boolean;
	}>(),
	{
		isLoading: false,
		submitDisabled: false,
	},
);

// name
const name = ref("");
const nameValid = ref(false);
const nameTouched = ref(false);

// description
const description = ref("");
const descriptionValid = ref(false);
const descriptionTouched = ref(false);

// age
const targetedAgeMonths = ref<AgeRange>([null, null]);

// regions
const regions = ref(new Set<number>());
const regionsValid = ref(false);
const regionsTouched = ref(false);

// categories
const categories = ref(new Set<string>());

// images
const imageUploader = useImageUploader();
const studioImages = ref<Array<StudioImage>>([]);
const { data: images, status: imagesStatus } = imageUploader.uploadMany(() =>
	unref(studioImages)
		.map((img) => img.cropped)
		.filter((img) => img != null),
);
const imagesTouched = ref(false);
const imagesValid = ref(false);

// studio
const studioOverlay = ref(false);
const tmpStudioImages = ref<Array<StudioImage>>([]);

// cap
const { cap } = useRuntimeConfig().public;
const capToken = ref("");
const capResetSignal = ref(0);
const capConfigured = computed<boolean>(
	() => cap.apiUrl !== "" && cap.siteKey !== "",
);

// honeypot
const website = ref("");

// load data on props.data change
const stop = watch(
	() => props.item,
	(_item) => {
		if (_item) {
			name.value = _item.name;
			description.value = _item.description;
			targetedAgeMonths.value = string2range(_item.targeted_age_months);
			regions.value = new Set(_item.region_ids);
			categories.value = new Set(_item.category_slugs);
			studioImages.value = _item.image_names.map((name: string) =>
				useStudioImage(imagePath(name, 1024), {
					crop: "center",
					maxSize: 1024,
				}),
			);
		}
	},
	{ immediate: true },
);
tryOnUnmounted(stop);

// all field validation must pass and upload succeeded
const valid = computed(
	() =>
		[
			nameValid,
			descriptionValid,
			regionsValid,
			imagesValid,
			capConfigured,
		].every((v) => unref(v) === true) &&
		unref(imagesStatus) === "success" &&
		unref(images).every((img: string | undefined) => img != null) &&
		unref(capToken) !== "",
);

function openStudioOverlay() {
	tmpStudioImages.value = unref(studioImages).map((img) => img.copy());
	studioOverlay.value = true;
}

function closeStudioOverlay() {
	studioOverlay.value = false;
}

function saveStudioImages() {
	studioImages.value = unref(tmpStudioImages).map((img) => img.copy());
}

function touchAll() {
	nameTouched.value = true;
	descriptionTouched.value = true;
	regionsTouched.value = true;
	imagesTouched.value = true;
}

function onclick() {
	touchAll();

	if (!unref(valid)) return;

	const _images = unref(images);

	if (!_images.every((img) => img != null))
		throw new Error("Cannot create object with null image");

	emit("submit", {
		name: unref(name),
		description: unref(description),
		images: _images,
		targeted_age_months: range2string(unref(targetedAgeMonths)),
		regions: [...unref(regions)],
		categories: [...unref(categories)],
		blocked: false,
		cap_token: unref(capToken),
		website: unref(website),
	});

	capToken.value = "";
	capResetSignal.value += 1;
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
    <div>
      <h2>Catégories</h2>
      <p class="legend">
        Dans quelles catégories se trouve votre objet ?
      </p>
    </div>
    <CategoriesCheckboxes v-model="categories" />
  </section>
  <section
    v-if="!studioOverlay"
    class="v"
  >

    <Honeypot v-model="website" />

    <CapWidget
      v-if="capConfigured"
      :api-url="cap.apiUrl"
      :site-key="cap.siteKey"
      :reset-signal="capResetSignal"
      :disabled="isLoading"
      @solve="capToken = $event"
      @expire="capToken = ''"
    />
    <PanelBanner
      v-else
      color="red"
      :icon="OctagonAlert"
    >
      Captcha indisponible. Création désactivée.
    </PanelBanner>
  
    <TextButton
      aspect="flat"
      color="primary"
      :disabled="!valid || props.isLoading || props.submitDisabled"
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
section {
  display: flex;
  flex-direction: column;
  gap: $space-6;

  h2 {
    color: $text-primary;
    margin: 0 0 $space-2 0;
  }

  p.legend {
    color: $text-secondary;
    margin: 0;
  }
}

.ItemImagesInput {
  margin-bottom: $space-6;
  border-radius: $radius-lg;
  border: 1px solid $divider;
}

.TextButton {
  margin: $space-6 0;
}

.RegionsMap {
  margin: $space-6 $space-10;
}

.RegionsList {
  font-size: 1em;
  color: $text-primary;
}

.Overlay {
  z-index: 3;

  .ItemStudio {
    width: 100%;
    height: 100%;
  }
}
</style>
