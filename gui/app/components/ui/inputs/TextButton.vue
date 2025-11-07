<script setup lang="ts">
import type { LucideIcon } from 'lucide-vue-next'
import type { RouteLocationGeneric } from 'vue-router'

const props = withDefaults(
  defineProps<{
    aspect?: 'flat' | 'outline' | 'bezel'
    size?: 'large' | 'normal' | 'small'
    color?: 'neutral' | 'primary' | 'red'
    loading?: boolean
    timeout?: number
    disabled?: boolean
    icon?: LucideIcon
    target?: string | RouteLocationGeneric
  }>(),
  {
    aspect: 'flat',
    size: 'normal',
    color: 'neutral',
    loading: false,
    timeout: 500,
    disabled: false,
  },
)
const { aspect, size, color, loading, timeout, disabled, icon, target } = toRefs(props)

const { value: longLoading } = useThrottle(loading, timeout)

const slots = useSlots()

const iconSize = computed(() => ({ small: 16, normal: 24, large: 32 }[unref(size)]))

const classes = computed(() => ({
  large: unref(size) === 'large',
  small: unref(size) === 'small',

  flat: unref(aspect) === 'flat',
  outline: unref(aspect) === 'outline',
  bezel: unref(aspect) === 'bezel',

  disabled: unref(disabled),

  primary: unref(color) === 'primary',
  red: unref(color) === 'red',

  loading: unref(loading),
}))
</script>

<template>
  <NuxtLink
    class="TextButton"
    :class="classes"
    :to="target"
  >
    <div
      v-if="loading && longLoading"
      class="loader"
    >
      <LoadingAnimation :small="true" />
    </div>
    <div class="content">
      <div
        v-if="slots.icon || icon"
        class="icon"
      >
        <component
          :is="icon"
          v-if="icon"
          :size="iconSize"
          :stroke-width="1"
        />
        <slot name="icon" />
      </div>
      <slot />
    </div>
  </NuxtLink>
</template>

<style scoped lang="scss">
a.TextButton {
  @include reset-link;

  display: block;
  position: relative;
  color: white;
  text-align: center;
  cursor: pointer;
  user-select: none;
  font-size: 1.2em;
  border-radius: 0.4em;

  padding: 0.5em 1em;
  font-size: 1.3em;

  transition: all 200ms ease-out;

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

  .content {
    @include flex-row;
    align-content: center;
    justify-content: center;
    gap: 0.5em;

    .icon {
      position: relative;
      top: 3px;
    }
  }

  &.loading>.content {
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

  &.small {
    border-radius: 0.4em;
    padding: 0.3em 0.8em;
    font-size: 1em;
  }

  &.large {
    border-radius: 0.5em;
    padding: 0.6em 1.5em;
    font-size: 1.5em;
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

    &.disabled, &.loading {
      background: var(--color-100);
      color: var(--color-400);
      cursor: default;
    }
  }

  &.outline {
    color: var(--color-500);
    border: var(--color-500) 1px solid;

    /* compensate for the border width */
    padding: calc(0.3em - 1px) 0.8em;

    &.large {
      padding: calc(0.6em - 1px) 1.5em;
    }

    &:hover {
      color: var(--color-600);
      border-color: var(--color-600);
    }

    &:active {
      color: var(--color-700);
      border-color: var(--color-700);
    }

    &.disabled, &.loading {
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

    &.disabled, &.loading {
      background: var(--color-100);
      color: var(--color-300);
      box-shadow: none;
      cursor: default;
    }
  }
}
</style>
