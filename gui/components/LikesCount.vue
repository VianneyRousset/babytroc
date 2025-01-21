<script setup lang="ts">

import { Heart } from 'lucide-vue-next';

const props = defineProps<{
  count: number,
  liked?: boolean,
  loading?: boolean,
}>();

const loadingTimeout = ref(null as null | ReturnType<typeof setTimeout>);
const loader = ref(false);

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
    <div v-else :class="{ small: props.loading }" class="likes">
      <Heart :class="{ filled: props.liked }" :size="32" :strokeWidth="2" :absoluteStrokeWidth="true" />
      <p>{{ props.count }}</p>
    </div>
  </div>

</template>

<style scoped lang="scss">
.container {
  min-width: 5rem;
  display: flex;
  flex-direction: row;
  justify-content: center;
  padding: 0.8rem 1.2rem;

  .loader {
    @include flex-row-center;
    width: 32px;
    height: 32px;
  }

  .likes {
    @include flex-row;
    font-family: 'Inter', sans-serif;
    cursor: pointer;

    gap: 0.6rem;
    font-size: 1.5rem;

    color: $neutral-700;

    transition: transform 200ms ease-out, opacity 200ms ease-out;

    &.small {
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
