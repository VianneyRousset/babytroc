<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    aspect?: 'flat' | 'outline' | 'bezel'
    size?: 'large' | 'normal'
    color?: 'neutral' | 'primary' | 'red'
    loading?: boolean
    timeout?: number
    disabled?: boolean
  }>(),
  {
    aspect: 'flat',
    size: 'normal',
    color: 'neutral',
    loading: false,
    timeout: 1000,
    disabled: false,
  },
)
const { aspect, size, color, loading, timeout, disabled } = toRefs(props)

const loadingTimeout = ref(null as null | ReturnType<typeof setTimeout>)
const showLoader = ref(false)

const classes = computed(() => ({
  large: unref(size) === 'large',

  flat: unref(aspect) === 'flat',
  outline: unref(aspect) === 'outline',
  bezel: unref(aspect) === 'bezel',

  disabled: unref(disabled),

  primary: unref(color) === 'primary',
  red: unref(color) === 'red',

  loading: unref(showLoader),
}))

watch(
  loading,
  (v) => {
    if (v) {
      clearTimeout(loadingTimeout.value ?? undefined)

      loadingTimeout.value = setTimeout(() => {
        showLoader.value = true
      }, unref(timeout))
    }
    else {
      clearTimeout(unref(loadingTimeout.value) ?? undefined)
      loadingTimeout.value = null

      showLoader.value = false
    }
  },
  { immediate: true },
)
</script>

<template>
  <div
    class="TextButton"
    :class="classes"
  >
    <div
      v-if="showLoader"
      class="loader"
    >
      <LoadingAnimation :small="true" />
    </div>
    <span>
      <slot />
    </span>
  </div>
</template>

<style scoped lang="scss">
.TextButton {
  position: relative;
  color: white;
  text-align: center;
  cursor: pointer;
  border-radius: 0.4rem;
  padding: 0.3rem 0.8rem;

  transition: transform 200ms ease-out, opacity 200ms ease-out;

  --color-50: #{$neutral-50};
  --color-100: #{$neutral-100};
  --color-200: #{$neutral-200};
  --color-300: #{$neutral-300};
  --color-400: #{$neutral-400};
  --color-500: #{$neutral-500};
  --color-600: #{$neutral-600};
  --color-700: #{$neutral-700};
  --color-800: #{$neutral-800};
  --color-900: #{$neutral-900};

  .loader {
    @include flex-row-center;
    width: 100%;
    height: 100%;
    position: absolute;
    top: 0;
    left: 0;
  }

  &.loading>span {
    opacity: 0.1;
  }

  &.primary {
    --color-50: #{$primary-50};
    --color-100: #{$primary-100};
    --color-200: #{$primary-200};
    --color-300: #{$primary-300};
    --color-400: #{$primary-400};
    --color-500: #{$primary-500};
    --color-600: #{$primary-600};
    --color-700: #{$primary-700};
    --color-800: #{$primary-800};
    --color-900: #{$primary-900};
  }

  &.red {
    --color-50: #{$red-50};
    --color-100: #{$red-100};
    --color-200: #{$red-200};
    --color-300: #{$red-300};
    --color-400: #{$red-400};
    --color-500: #{$red-500};
    --color-600: #{$red-600};
    --color-700: #{$red-700};
    --color-800: #{$red-800};
    --color-900: #{$red-900};
  }

  &.large {
    border-radius: 0.5rem;
    padding: 0.6rem 1.5rem;
    font-size: 1.5rem;
  }

  &.active {
    transform: scale(0.8);
    opacity: 0;
  }

  &.flat {
    background: var(--color-500);

    &:hover {
      background: var(--color-600);
    }

    &:active {
      background: var(--color-700);
    }

    &.disabled {
      background: var(--color-100);
      color: var(--color-400);
      cursor: default;
    }
  }

  &.outline {
    color: var(--color-500);
    border: var(--color-500) 1px solid;

    /* compensate for the border width */
    padding: calc(0.3rem - 1px) 0.8rem;

    &.large {
      padding: calc(0.6rem - 1px) 1.5rem;
    }

    &:hover {
      color: var(--color-600);
      border-color: var(--color-600);
    }

    &:active {
      color: var(--color-700);
      border-color: var(--color-700);
    }

    &.disabled {
      color: var(--color-200);
      border-color: var(--color-200);
      cursor: default;
    }
  }

  &.bezel {
    background: linear-gradient(var(--color-500) 0%, var(--color-600) 100%);
    box-shadow: inset 0 2px 0 0 hsla(0, 0%, 100%, .2), inset 0 -1px 0 0 rgba(0, 0, 0, .25), 0 2px 6px 0 rgba(0, 0, 0, .1);

    &:hover {
      background: linear-gradient(var(--color-600) 0%, var(--color-700) 100%);
    }

    &:active {
      background: linear-gradient(var(--color-700) 0%, var(--color-800) 100%);
    }

    &.disabled {
      background: var(--color-100);
      color: var(--color-300);
      box-shadow: none;
      cursor: default;
    }
  }
}
</style>
