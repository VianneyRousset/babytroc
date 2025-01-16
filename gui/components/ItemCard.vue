<script setup lang="ts">

// TODO query reduced image size
// TODO "missing image" if item.image is missing

import type { ApiResponse } from '#open-fetch';

type Item = ApiResponse<'list_items_v1_items_get'>[number];

const props = defineProps<{
  item: Item
}>();

const emit = defineEmits(["select"]);

const backgroundImage = computed(() => {

  const backgrounds = []
  const params = "";

  backgrounds.push("linear-gradient(transparent 0 50%, #202020 100%)");
  backgrounds.push(`url('/api/v1/images/${props.item.first_image_name}${params}')`);

  return backgrounds.join(", ");

});

const formatedTargetedAge = computed(() => {

  const ageMin = props.item.targeted_age_months[0];
  const ageMax = props.item.targeted_age_months[1];


  if (ageMin !== null && ageMin > 0) {

    if (ageMax === null)
      return `À partie de ${ageMin} mois`;

    return `De ${ageMin} à ${ageMax} mois`
  }

  if (ageMax !== null)
    return `Jusqu'à ${ageMax} mois`

  return "Pour tous âges"
});


</script>

<template>
  <div :class="{ box: true }" @click="emit('select');" :style="{ backgroundImage: backgroundImage }">

    <div class="status">
    </div>

    <div class="info">
      <div class="age">{{ formatedTargetedAge }}</div>
      <div class="name">{{ props.item.name }}</div>
    </div>
  </div>

</template>

<style scoped lang="scss">
.box {
  display: flex;
  box-sizing: border-box;
  aspect-ratio: 1;
  flex-direction: column;
  justify-content: space-between;
  border-radius: 1rem;
  background-repeat: no-repeat;
  background-size: cover;
  background-position: center;
  cursor: pointer;
  color: $neutral-50;

}

.box:target {
  /* ensure the target element (anchor) is not flushed to the top */
  scroll-margin-top: 20vh;
  animation: flash;
  animation-duration: 0.8s;
}

.box>div {
  padding: 1rem;
}

.status {
  display: flex;
  justify-content: right;
}

.age {
  color: $primary-400;
  margin-bottom: 0.2em;
}

.name {
  font-family: "Plus Jakarta Sans", sans-serif;
  color: var(--brand-50);
  font-size: 1.6rem;
  font-weight: bold;
}

.name-status>img {
  width: clamp(2em, 10vw, 2.5em);
  margin-left: 1em;
}
</style>
