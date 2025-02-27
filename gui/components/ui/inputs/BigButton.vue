<script setup lang="ts">

const props = defineProps<{
  type: "flat" | "outline" | "bezel",
  loading?: boolean,
  disabled?: boolean,
}>();
const { type, loading, disabled } = toRefs(props);

const loadingTimeout = ref(null as null | ReturnType<typeof setTimeout>);
const loader = ref(false);

watch(loading, (v) => {

  if (v) {

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
      :class="{ flat: type == 'flat', outline: type == 'outline', bezel: type == 'bezel', small: loading, disabled: disabled === true }"
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
  }

  .button {
    color: white;
    padding: 0.6rem 1.5rem;
    text-align: center;
    border-radius: 0.5rem;
    cursor: pointer;
    font-size: 1.5rem;

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

      &.disabled {
        background: $primary-100;
        color: $primary-400;
        cursor: default;
      }
    }

    &.outline {
      color: $primary-500;
      border: $primary-500 1px solid;

      &:hover {
        color: $primary-600;
        border-color: $primary-600;
      }

      &:active {
        color: $primary-700;
        border-color: $primary-700;
      }

      &.disabled {
        color: $primary-200;
        border-color: $primary-200;
        cursor: default;
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

      &.disabled {
        background: $primary-100;
        color: $primary-300;
        box-shadow: none;
        cursor: default;
      }
    }
  }
}
</style>
