<script setup lang="ts">

const props = defineProps<{
  type: string,
  loading?: Boolean,
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
    <div v-if="loader" class="loading">
      <Loader :small="true" />
    </div>
    <div
      :class="{ flat: props.type == 'flat', outline: props.type == 'outline', bezel: props.type == 'bezel', small: props.loading }"
      class="button">
      <slot />
    </div>
  </div>

</template>

<style scoped lang="scss">
.container {

  position: relative;

  .loading {
    @include flex-row-center;
    width: 100%;
    height: 100%;
    position: absolute;
    top: 0;
    left: 0;
    background: rgba(255, 255, 255, 0.2);
  }

  .button {
    color: white;
    padding: 0.6rem 1.5rem;
    text-align: center;
    border-radius: 0.5rem;
    cursor: pointer;
    font-size: 1.5rem;

    background: $neutral-500;

    transition: transform 200ms ease-out, opacity 200ms ease-out;

    &.small {
      transform: scale(0.8);
      opacity: 0;
    }

    &.flat {
      background: $primary-500;

      &:hover {
        background: $primary-600;
      }

      &:active {
        background: $primary-700;
      }
    }

    &.bezel {
      background: linear-gradient($primary-500 0%, $primary-600 100%);
      box-shadow: inset 0 2px 0 0 hsla(0, 0%, 100%, .2), inset 0 -1px 0 0 rgba(0, 0, 0, .25), 0 2px 6px 0 rgba(0, 0, 0, .1);

      &:hover {
        background: linear-gradient($primary-600 0%, $primary-700 100%);
      }

      &:active {
        background: linear-gradient($primary-700 0%, $primary-800 100%);
      }
    }
  }
}
</style>
