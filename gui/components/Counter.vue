<script setup lang="ts">

import { Heart, Star } from 'lucide-vue-next';

const props = defineProps<{
  symbol: "heart" | "star",
  size?: "normal" | "small" | "tiny",
  count?: number | null,
  active?: boolean,
  loading?: boolean,
}>();

const loadingTimeout = ref(null as null | ReturnType<typeof setTimeout>);
const loader = ref(false);

const symbolSize = computed(() => {
  switch (props.size ?? "normal") {
    case "normal":
      return 32;
    case "small":
      return 24;
    case "tiny":
      return 16;
    default:
      throw new Error(`Unhandled case: ${props.size}`);
  }
});

const symbolStrokeWidth = computed(() => {
  switch (props.size ?? "normal") {
    case "normal":
      return 2;
    case "small":
      return 2;
    case "tiny":
      return 1.2;
    default:
      throw new Error(`Unhandled case: ${props.size}`);
  }
});


watch(toRef(props, "loading"), (loading) => {

  if (loading) {

    if (loadingTimeout.value)
      clearTimeout(loadingTimeout.value);

    loadingTimeout.value = setTimeout(() => {
      loader.value = true
    }, 1000);

  } else {

    if (loadingTimeout.value)
      clearTimeout(loadingTimeout.value);

    loader.value = false;
  }

});


</script>

<template>

  <div class="container">
    <div v-if="loader" class="loader">
      <Loader :small="true" />
    </div>
    <div v-else :class="{ pressed: props.loading, small: props.size === 'small', tiny: props.size === 'tiny' }"
      class="likes">
      <Heart v-if="props.symbol === 'heart'" :class="{ filled: props.active }" :size="symbolSize"
        :strokeWidth="symbolStrokeWidth" :absoluteStrokeWidth="true" />
      <Star v-else-if="props.symbol === 'star'" :class="{ filled: props.active }" :size="symbolSize"
        :strokeWidth="symbolStrokeWidth" :absoluteStrokeWidth="true" />
      <p>{{ props.count ?? "..." }}</p>
    </div>
  </div>

</template>

<style scoped lang="scss">
.container {
  display: flex;
  flex-direction: row;
  justify-content: center;

  .loader {
    @include flex-row-center;
    width: 32px;
    height: 32px;
  }

  .likes {
    @include flex-row;
    font-family: "Inter", sans-serif;
    cursor: pointer;
    margin: 0.8rem 1.2rem;

    gap: 0.6rem;
    font-size: 1.5rem;

    color: $neutral-700;

    transition: transform 200ms ease-out, opacity 200ms ease-out;

    &.small {
      gap: 0.4rem;
      font-size: 1rem;
      margin: 0.4rem 0.6rem;
    }

    &.tiny {
      gap: 0.2rem;
      font-size: 12px;
      margin: 0.2rem 0.4rem;
    }

    &.pressed {
      transform: scale(0.8);
      opacity: 0;
    }


    svg.filled {
      fill: $neutral-700;
    }

    p {
      min-width: 1.2rem;
      margin: 0px
    }

  }
}
</style>
