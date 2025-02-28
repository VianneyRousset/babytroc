<script setup lang="ts">

// TODO query reduced image size
// TODO "missing image" if item.image is missing

const props = defineProps<{
  item: ItemPreview,
}>();
const { item } = toRefs(props);

const { name, formatedTargetedAgeMonths } = useItemPreview(item);

const backgroundImage = computed(() => {

  const backgrounds = []
  const params = "";

  backgrounds.push("linear-gradient(transparent 0 40%, #202020 100%)");
  backgrounds.push(`url('/api/v1/images/${props.item.first_image_name}${params}')`);

  return backgrounds.join(", ");

});


</script>

<template>
  <div class="box" :style="{ backgroundImage: backgroundImage }">

    <div class="status">
    </div>

    <div class="info">
      <div class="age">{{ formatedTargetedAgeMonths }}
      </div>
      <div class="name">{{ name }}</div>
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
  color: $primary-300;
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
